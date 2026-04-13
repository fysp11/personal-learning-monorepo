import { mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, extname, join, relative, resolve } from "node:path";

type EntityType = string;

type EntityConfig = {
  slug: string;
  name: string;
  type: EntityType;
  aliases?: string[];
  tags?: string[];
  relationships?: string[];
  confidence?: "low" | "medium" | "high";
  includeGlobs?: string[];
};

type ExtractionConfig = {
  name: string;
  sourceRoots: string[];
  includeExtensions: string[];
  excludePathSubstrings?: string[];
  outputRoot: string;
  entities: EntityConfig[];
};

type Evidence = {
  file: string;
  line: number;
  text: string;
  alias: string;
};

type DiscoverCandidate = {
  text: string;
  score: number;
  count: number;
  files: Set<string>;
  evidence: Evidence[];
};

type DiscoverEngineKind = "lexical" | "qmd";

type QmdSearchResult = {
  docid?: string;
  score?: number;
  file?: string;
  title?: string;
  snippet?: string;
};

type DiscoverInput = {
  config: ExtractionConfig;
  files: string[];
  repoRoot: string;
  knownPatterns: RegExp[];
  maxEvidence: number;
};

const DEFAULT_MAX_EVIDENCE = 12;
const DEFAULT_DISCOVER_LIMIT = 30;
const DEFAULT_DISCOVER_ENGINE: DiscoverEngineKind = "qmd";
const DEFAULT_QMD_TOP_K = 5;
const DEFAULT_QMD_SEED_LIMIT = 40;
const DEFAULT_EXPAND_FROM_DISCOVER = true;
const DEFAULT_EXPAND_LIMIT = 12;
const DEFAULT_EXPAND_MIN_COUNT = 2;
const EXCLUDED_TYPES = new Set(["people", "companies"]);
const DISCOVER_MIN_COUNT = 2;
const DISCOVER_MIN_SCORE = 6;
const DISCOVER_MAX_WORDS = 5;
const DISCOVER_STOPWORDS = new Set([
  "the",
  "and",
  "for",
  "with",
  "this",
  "that",
  "from",
  "your",
  "you",
  "are",
  "not",
  "can",
  "will",
  "would",
  "should",
  "into",
  "about",
  "what",
  "how",
  "when",
  "where",
  "why",
  "who",
  "does",
  "do",
  "did",
  "have",
  "has",
  "had",
  "use",
  "used",
  "using",
  "make",
  "made",
  "add",
  "build",
  "refactor",
  "design",
  "implement",
  "workflow",
  "system",
  "workflow",
  "question",
  "answer",
]);

function parseArgs(argv: string[]) {
  const result: {
    config?: string;
    maxEvidence: number;
    dryRun: boolean;
    syncQmd: boolean;
    discover: boolean;
    discoverLimit: number;
    discoverEngine: DiscoverEngineKind;
    qmdCollection?: string;
    qmdTopK: number;
    qmdSeedLimit: number;
    expandFromDiscover: boolean;
    expandLimit: number;
    expandMinCount: number;
  } = {
    maxEvidence: DEFAULT_MAX_EVIDENCE,
    dryRun: false,
    syncQmd: false,
    discover: false,
    discoverLimit: DEFAULT_DISCOVER_LIMIT,
    discoverEngine: DEFAULT_DISCOVER_ENGINE,
    qmdTopK: DEFAULT_QMD_TOP_K,
    qmdSeedLimit: DEFAULT_QMD_SEED_LIMIT,
    expandFromDiscover: DEFAULT_EXPAND_FROM_DISCOVER,
    expandLimit: DEFAULT_EXPAND_LIMIT,
    expandMinCount: DEFAULT_EXPAND_MIN_COUNT,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--config") {
      result.config = argv[i + 1];
      i += 1;
    } else if (arg === "--max-evidence") {
      result.maxEvidence = Number(argv[i + 1] ?? DEFAULT_MAX_EVIDENCE);
      i += 1;
    } else if (arg === "--dry-run") {
      result.dryRun = true;
    } else if (arg === "--sync-qmd") {
      result.syncQmd = true;
    } else if (arg === "--discover") {
      result.discover = true;
    } else if (arg === "--discover-limit") {
      result.discoverLimit = Number(argv[i + 1] ?? DEFAULT_DISCOVER_LIMIT);
      i += 1;
    } else if (arg === "--discover-engine") {
      const engine = (argv[i + 1] ?? DEFAULT_DISCOVER_ENGINE) as DiscoverEngineKind;
      if (engine !== "lexical" && engine !== "qmd") {
        throw new Error(`Invalid --discover-engine value: ${engine}`);
      }
      result.discoverEngine = engine;
      i += 1;
    } else if (arg === "--qmd-collection") {
      result.qmdCollection = argv[i + 1];
      i += 1;
    } else if (arg === "--qmd-top-k") {
      result.qmdTopK = Number(argv[i + 1] ?? DEFAULT_QMD_TOP_K);
      i += 1;
    } else if (arg === "--qmd-seed-limit") {
      result.qmdSeedLimit = Number(argv[i + 1] ?? DEFAULT_QMD_SEED_LIMIT);
      i += 1;
    } else if (arg === "--expand-from-discover") {
      result.expandFromDiscover = true;
    } else if (arg === "--no-expand-from-discover") {
      result.expandFromDiscover = false;
    } else if (arg === "--expand-limit") {
      result.expandLimit = Number(argv[i + 1] ?? DEFAULT_EXPAND_LIMIT);
      i += 1;
    } else if (arg === "--expand-min-count") {
      result.expandMinCount = Number(argv[i + 1] ?? DEFAULT_EXPAND_MIN_COUNT);
      i += 1;
    }
  }

  if (!result.config) {
    throw new Error("Missing required --config <path>");
  }

  return result;
}

function loadConfig(configPath: string): ExtractionConfig {
  const absolute = resolve(configPath);
  return JSON.parse(readFileSync(absolute, "utf8")) as ExtractionConfig;
}

function walkFiles(root: string, exts: Set<string>, excludes: string[]): string[] {
  const files: string[] = [];

  function visit(current: string) {
    const stats = statSync(current);
    if (stats.isDirectory()) {
      for (const entry of readdirSync(current).sort((a, b) => a.localeCompare(b))) {
        visit(join(current, entry));
      }
      return;
    }

    const normalized = current.replace(/\\/g, "/");
    if (excludes.some((part) => normalized.includes(part))) {
      return;
    }

    if (exts.has(extname(current).toLowerCase())) {
      files.push(current);
    }
  }

  visit(root);
  return files.sort((a, b) => a.localeCompare(b));
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function buildAliasPatterns(entity: EntityConfig) {
  const rawAliases = [entity.name, ...(entity.aliases ?? [])];
  const aliases = Array.from(
    new Set(rawAliases.map((value) => value.trim()).filter(Boolean)),
  );

  return aliases.map((alias) => ({
    alias,
    regex: new RegExp(`(^|[^A-Za-z0-9])(${escapeRegExp(alias)})(?=[^A-Za-z0-9]|$)`, "i"),
  }));
}

function buildKnownPatterns(entities: EntityConfig[]) {
  return entities.flatMap((entity) => buildAliasPatterns(entity).map((pattern) => pattern.regex));
}

function normalizeCandidate(value: string) {
  return value
    .replace(/\s+/g, " ")
    .replace(/[“”]/g, '"')
    .replace(/[‘’]/g, "'")
    .trim()
    .replace(/^["'`([{<]+/, "")
    .replace(/["'`)}\]>.,:;!?]+$/, "")
    .trim();
}

function extractCandidatesFromLine(line: string): string[] {
  const candidates = new Set<string>();
  const add = (value: string) => {
    const normalized = normalizeCandidate(value);
    if (normalized.length < 3) {
      return;
    }
    const words = normalized.split(/\s+/).filter(Boolean);
    if (words.length > DISCOVER_MAX_WORDS) {
      return;
    }
    if (words.every((word) => DISCOVER_STOPWORDS.has(word.toLowerCase()))) {
      return;
    }
    candidates.add(normalized);
  };

  for (const match of line.matchAll(/`([^`]{3,80})`/g)) {
    add(match[1] ?? "");
  }

  for (const match of line.matchAll(/\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4}\b/g)) {
    add(match[0] ?? "");
  }

  for (const match of line.matchAll(/\b[A-Z]{2,}(?:[-/][A-Z0-9]{2,})*\b/g)) {
    add(match[0] ?? "");
  }

  for (const match of line.matchAll(/\b(?:[a-z]+[A-Z][A-Za-z0-9]+|[A-Z][a-z]+(?:[A-Z][A-Za-z0-9]+)+)\b/g)) {
    add(match[0] ?? "");
  }

  return Array.from(candidates);
}

function scoreCandidate(text: string) {
  const words = text.split(/\s+/).filter(Boolean);
  const lengthScore = Math.min(text.length / 10, 6);
  const wordScore = Math.min(words.length * 0.75, 3);
  const shapeScore = /[A-Z]/.test(text) ? 2 : 1;
  return Number((lengthScore + wordScore + shapeScore).toFixed(2));
}

function finalizeCandidates(candidates: Map<string, DiscoverCandidate>) {
  return Array.from(candidates.values())
    .filter(
      (candidate) =>
        (candidate.count >= DISCOVER_MIN_COUNT && candidate.score >= DISCOVER_MIN_SCORE) ||
        (/^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}$/.test(candidate.text) &&
          candidate.count >= 2 &&
          candidate.score >= DISCOVER_MIN_SCORE),
    )
    .sort((a, b) => b.score - a.score || b.count - a.count || a.text.localeCompare(b.text));
}

function upsertCandidate(
  candidates: Map<string, DiscoverCandidate>,
  candidateText: string,
  file: string,
  line: number,
  rawText: string,
  maxEvidence: number,
  extraScore = 0,
) {
  const existing = candidates.get(candidateText) ?? {
    text: candidateText,
    score: 0,
    count: 0,
    files: new Set<string>(),
    evidence: [],
  };

  existing.count += 1;
  existing.files.add(file);
  existing.score = Math.max(existing.score, scoreCandidate(candidateText), extraScore);

  if (existing.evidence.length < maxEvidence) {
    existing.evidence.push({
      file,
      line,
      text: rawText,
      alias: candidateText,
    });
  }

  candidates.set(candidateText, existing);
}

abstract class DiscoverEngine {
  abstract readonly id: DiscoverEngineKind;

  abstract collectCandidates(input: DiscoverInput): Promise<DiscoverCandidate[]>;
}

class LexicalDiscoverEngine extends DiscoverEngine {
  readonly id = "lexical" as const;

  async collectCandidates(input: DiscoverInput): Promise<DiscoverCandidate[]> {
    const candidates = new Map<string, DiscoverCandidate>();

    for (const file of input.files) {
      const lines = readFileSync(file, "utf8").split(/\r?\n/);
      for (let index = 0; index < lines.length; index += 1) {
        const line = lines[index]?.trim() ?? "";
        if (!line || line.length < 4) {
          continue;
        }

        if (input.knownPatterns.some((pattern) => pattern.test(line))) {
          continue;
        }

        for (const candidateText of extractCandidatesFromLine(line)) {
          if (input.knownPatterns.some((pattern) => pattern.test(candidateText))) {
            continue;
          }
          upsertCandidate(
            candidates,
            candidateText,
            relative(input.repoRoot, file),
            index + 1,
            line,
            input.maxEvidence,
          );
        }
      }
    }

    return finalizeCandidates(candidates);
  }
}

class QmdDiscoverEngine extends DiscoverEngine {
  readonly id = "qmd" as const;

  constructor(
    private readonly qmdCollection: string | undefined,
    private readonly topK: number,
    private readonly seedLimit: number,
  ) {
    super();
  }

  async collectCandidates(input: DiscoverInput): Promise<DiscoverCandidate[]> {
    const candidates = new Map<string, DiscoverCandidate>();
    const seedQueries = this.buildSeedQueries(input.config);
    const allowedFiles = new Set(
      input.files.map((file) => relative(input.repoRoot, file).replace(/\\/g, "/")),
    );

    for (const query of seedQueries) {
      const results = await this.fetchResults(query);
      for (const result of results) {
        const file = this.normalizeFilePath(result.file, input.repoRoot) ?? "unknown";
        if (!allowedFiles.has(file)) {
          continue;
        }
        const retrievalScore = Math.max(0, Number(result.score ?? 0) * 10);
        const lines = [result.title ?? "", ...(result.snippet ?? "").split(/\r?\n/)];

        for (const rawLine of lines) {
          const line = rawLine.trim();
          if (!line || line.startsWith("@@")) {
            continue;
          }
          if (input.knownPatterns.some((pattern) => pattern.test(line))) {
            continue;
          }
          for (const candidateText of extractCandidatesFromLine(line)) {
            if (input.knownPatterns.some((pattern) => pattern.test(candidateText))) {
              continue;
            }
            upsertCandidate(candidates, candidateText, file, 1, line, input.maxEvidence, retrievalScore);
          }
        }
      }
    }

    return finalizeCandidates(candidates);
  }

  private buildSeedQueries(config: ExtractionConfig) {
    const seeds = new Set<string>();
    for (const entity of config.entities) {
      seeds.add(entity.name);
      for (const alias of entity.aliases ?? []) {
        seeds.add(alias);
      }
      for (const tag of entity.tags ?? []) {
        if (tag.trim().length >= 4) {
          seeds.add(tag);
        }
      }
    }
    return Array.from(seeds).filter(Boolean).slice(0, this.seedLimit);
  }

  private normalizeFilePath(value: string | undefined, repoRoot: string) {
    if (!value) {
      return undefined;
    }
    const qmdMatch = value.match(/^qmd:\/\/[^/]+\/(.+)$/);
    if (qmdMatch?.[1]) {
      return qmdMatch[1];
    }
    if (value.startsWith(repoRoot)) {
      return relative(repoRoot, value);
    }
    if (!value.startsWith("/")) {
      return value;
    }
    return undefined;
  }

  private parseQmdResults(output: string): QmdSearchResult[] {
    const start = output.indexOf("[");
    const end = output.lastIndexOf("]");
    if (start < 0 || end <= start) {
      return [];
    }

    const jsonSlice = output.slice(start, end + 1);
    try {
      const parsed = JSON.parse(jsonSlice) as unknown;
      return Array.isArray(parsed) ? (parsed as QmdSearchResult[]) : [];
    } catch {
      return [];
    }
  }

  private async runQmd(args: string[]) {
    const process = Bun.spawn(["qmd", ...args], {
      stdout: "pipe",
      stderr: "pipe",
    });
    const [stdout, stderr, code] = await Promise.all([
      new Response(process.stdout).text(),
      new Response(process.stderr).text(),
      process.exited,
    ]);
    return { stdout, stderr, code };
  }

  private async fetchResults(query: string) {
    const queryArgs = ["query", `lex: ${query}`, "--json", "--no-rerank", "-n", String(this.topK)];
    if (this.qmdCollection) {
      queryArgs.push("-c", this.qmdCollection);
    }

    const queryRun = await this.runQmd(queryArgs);
    const queryResults = this.parseQmdResults(`${queryRun.stdout}\n${queryRun.stderr}`);
    if (queryResults.length > 0) {
      return queryResults;
    }

    const searchArgs = ["search", query, "--json", "-n", String(this.topK)];
    if (this.qmdCollection) {
      searchArgs.push("-c", this.qmdCollection);
    }
    const searchRun = await this.runQmd(searchArgs);
    return this.parseQmdResults(`${searchRun.stdout}\n${searchRun.stderr}`);
  }
}

function createDiscoverEngine(
  kind: DiscoverEngineKind,
  qmdCollection: string | undefined,
  qmdTopK: number,
  qmdSeedLimit: number,
) {
  if (kind === "qmd") {
    return new QmdDiscoverEngine(qmdCollection, qmdTopK, qmdSeedLimit);
  }
  return new LexicalDiscoverEngine();
}

function collectEvidence(
  entity: EntityConfig,
  files: string[],
  repoRoot: string,
  maxEvidence: number,
): Evidence[] {
  const patterns = buildAliasPatterns(entity);
  const evidence: Evidence[] = [];

  for (const file of files) {
    const lines = readFileSync(file, "utf8").split(/\r?\n/);
    for (let index = 0; index < lines.length; index += 1) {
      const line = lines[index]?.trim() ?? "";
      if (!line || line.length < 4) {
        continue;
      }

      for (const pattern of patterns) {
        if (!pattern.regex.test(line)) {
          continue;
        }

        evidence.push({
          file: relative(repoRoot, file),
          line: index + 1,
          text: line,
          alias: pattern.alias,
        });
        break;
      }

      if (evidence.length >= maxEvidence) {
        return evidence;
      }
    }
  }

  return evidence;
}

function formatList(items: string[] | undefined) {
  if (!items || items.length === 0) {
    return "[]";
  }

  return items.map((item) => `  - ${item}`).join("\n");
}

function renderEntity(entity: EntityConfig, evidence: Evidence[]) {
  const aliases = entity.aliases ?? [];
  const tags = entity.tags ?? [];
  const relationships = entity.relationships ?? [];
  const confidence = entity.confidence ?? "medium";
  const generatedAt = new Date().toISOString();

  const evidenceLines =
    evidence.length === 0
      ? "- No matching evidence found in the configured source set."
      : evidence
          .map(
            (item) =>
              `- [${item.file}](/Users/fysp/personal/learning/${item.file}:${item.line}) — matched \`${item.alias}\`: ${item.text}`,
          )
          .join("\n");

  return `# Entity: ${entity.name}

type: ${entity.type}
aliases:
${formatList(aliases)}
tags:
${formatList(tags)}
relationships:
${formatList(relationships)}
confidence: ${confidence}
generated_by: scripts/extract-entities.ts
generated_at: ${generatedAt}

## Evidence
${evidenceLines}
`;
}

function slugify(value: string) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80);
}

function inferTypeFromCandidate(candidate: DiscoverCandidate): EntityType | undefined {
  const text = candidate.text.toLowerCase();
  const evidenceText = candidate.evidence.map((item) => item.text.toLowerCase()).join(" ");
  const corpus = `${text} ${evidenceText}`;

  if (/pattern|mode|playbook|ladder|loop/.test(corpus)) {
    return "patterns";
  }
  if (/protocol|mcp|interface/.test(corpus)) {
    return "protocols";
  }
  if (/architecture|topology|workflow|orchestrator|orchestration/.test(corpus)) {
    return "architectures";
  }
  if (/method|methodology|calibration|error|evaluation|benchmark|metric/.test(corpus)) {
    return "methodologies";
  }
  if (/tool|notebooklm|codex|claude code|cli|sdk/.test(corpus)) {
    return "tools";
  }
  if (/framework|langchain|dspy/.test(corpus)) {
    return "frameworks";
  }
  if (/library|numpy|pandas|zod/.test(corpus)) {
    return "libraries";
  }
  if (/product|agent|assistant/.test(corpus)) {
    return "products";
  }
  if (/system|platform|service/.test(corpus)) {
    return "systems";
  }
  if (/concept|trust|confidence|autonomy|config|routing/.test(corpus)) {
    return "concepts";
  }
  return undefined;
}

function renderDiscoveredEntity(type: EntityType, candidate: DiscoverCandidate) {
  const generatedAt = new Date().toISOString();
  const evidenceLines =
    candidate.evidence.length === 0
      ? "- No retrieval evidence found."
      : candidate.evidence
          .map(
            (item) =>
              `- [${item.file}](/Users/fysp/personal/learning/${item.file}:${item.line}) — ${item.text}`,
          )
          .join("\n");

  return `# Entity: ${candidate.text}

type: ${type}
aliases:
[]
tags:
  - discovered
relationships:
[]
confidence: medium
generated_by: scripts/extract-entities.ts
generated_at: ${generatedAt}

## Evidence
${evidenceLines}
`;
}

function ensureDir(path: string) {
  mkdirSync(path, { recursive: true });
}

function renderDiscoverReport(
  config: ExtractionConfig,
  candidates: DiscoverCandidate[],
  limit: number,
) {
  const selected = candidates.slice(0, limit);
  const generatedAt = new Date().toISOString();

  const blocks = selected.length
    ? selected
        .map((candidate, index) => {
          const files = Array.from(candidate.files).sort((a, b) => a.localeCompare(b));
          const evidence = candidate.evidence
            .map(
              (item) =>
                `- [${item.file}](/Users/fysp/personal/learning/${item.file}:${item.line}) — ${item.text}`,
            )
            .join("\n");

          return `## ${index + 1}. ${candidate.text}

- score: ${candidate.score}
- count: ${candidate.count}
- files: ${files.join(", ")}

${evidence}
`;
        })
        .join("\n")
    : "No candidate entities met the threshold.";

  return `# Discover Report: ${config.name}

generated_at: ${generatedAt}

## Summary

- candidates_found: ${candidates.length}
- candidates_reported: ${selected.length}

## Candidates

${blocks}
`;
}

async function syncQmd() {
  const update = Bun.spawn(["qmd", "update"], {
    stdout: "inherit",
    stderr: "inherit",
  });
  const updateCode = await update.exited;
  if (updateCode !== 0) {
    console.warn(
      `[warn] qmd update failed with exit code ${updateCode}. The entity files were still generated.`,
    );
    console.warn("[warn] Re-run `qmd update && qmd embed` from a shell with qmd write access.");
    return;
  }

  const embed = Bun.spawn(["qmd", "embed"], {
    stdout: "inherit",
    stderr: "inherit",
  });
  const embedCode = await embed.exited;
  if (embedCode !== 0) {
    console.warn(
      `[warn] qmd embed failed with exit code ${embedCode}. The entity files were still generated.`,
    );
    console.warn("[warn] Re-run `qmd embed` from a shell with qmd write access.");
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const config = loadConfig(args.config as string);
  const repoRoot = resolve("/Users/fysp/personal/learning");
  const exts = new Set(config.includeExtensions.map((ext) => ext.toLowerCase()));
  const excludes = config.excludePathSubstrings ?? [];

  const files = config.sourceRoots.flatMap((root) => walkFiles(resolve(root), exts, excludes));
  const knownPatterns = buildKnownPatterns(config.entities);
  const configuredTypes = Array.from(new Set(config.entities.map((entity) => entity.type))).sort();

  console.log(`Config: ${config.name}`);
  console.log(`Files scanned: ${files.length}`);
  console.log(`Configured entity types: ${configuredTypes.join(", ") || "(none)"}`);

  if (args.discover) {
    const engine = createDiscoverEngine(
      args.discoverEngine,
      args.qmdCollection,
      args.qmdTopK,
      args.qmdSeedLimit,
    );
    const candidates = await engine.collectCandidates({
      config,
      files,
      repoRoot,
      knownPatterns,
      maxEvidence: args.maxEvidence,
    });
    const outputPath = resolve(config.outputRoot, "_discover", `${config.name}.md`);
    const content = renderDiscoverReport(config, candidates, args.discoverLimit);

    console.log(`discover engine: ${engine.id}`);
    console.log(`discover candidates: ${candidates.length}`);

    if (!args.dryRun) {
      ensureDir(dirname(outputPath));
      writeFileSync(outputPath, content, "utf8");
    }
    if (args.syncQmd) {
      await syncQmd();
    }
    return;
  }

  for (const entity of config.entities) {
    const evidence = collectEvidence(entity, files, repoRoot, args.maxEvidence);
    const outputPath = resolve(config.outputRoot, entity.type, `${entity.slug}.md`);
    const content = renderEntity(entity, evidence);

    console.log(`${entity.type}/${entity.slug}: ${evidence.length} evidence line(s)`);

    if (args.dryRun) {
      continue;
    }

    ensureDir(dirname(outputPath));
    writeFileSync(outputPath, content, "utf8");
  }

  if (args.expandFromDiscover) {
    const engine = createDiscoverEngine(
      args.discoverEngine,
      args.qmdCollection,
      args.qmdTopK,
      args.qmdSeedLimit,
    );
    const discovered = await engine.collectCandidates({
      config,
      files,
      repoRoot,
      knownPatterns,
      maxEvidence: args.maxEvidence,
    });

    const existingSlugs = new Set(config.entities.map((entity) => entity.slug));
    const existingEntityFiles = walkFiles(
      resolve(config.outputRoot),
      new Set([".md"]),
      [...excludes, "/_discover/"],
    );
    for (const file of existingEntityFiles) {
      const name = file.split("/").pop() ?? "";
      if (!name.endsWith(".md")) {
        continue;
      }
      const slug = name.slice(0, -3);
      if (slug) {
        existingSlugs.add(slug);
      }
    }
    const promoted: Array<{ type: string; slug: string }> = [];
    let considered = 0;

    for (const candidate of discovered) {
      if (candidate.count < args.expandMinCount) {
        continue;
      }
      const type = inferTypeFromCandidate(candidate);
      if (!type || EXCLUDED_TYPES.has(type)) {
        continue;
      }
      const slug = slugify(candidate.text);
      if (!slug || existingSlugs.has(slug)) {
        continue;
      }
      considered += 1;
      if (considered > args.expandLimit) {
        break;
      }

      const outputPath = resolve(config.outputRoot, type, `${slug}.md`);
      if (!args.dryRun) {
        ensureDir(dirname(outputPath));
        writeFileSync(outputPath, renderDiscoveredEntity(type, candidate), "utf8");
      }
      promoted.push({ type, slug });
      existingSlugs.add(slug);
    }

    console.log(`expand engine: ${engine.id}`);
    console.log(`expanded entities: ${promoted.length}`);
    for (const item of promoted) {
      console.log(`${item.type}/${item.slug}: discovered`);
    }
  }

  if (!args.dryRun && args.syncQmd) {
    await syncQmd();
  }
}

await main();
