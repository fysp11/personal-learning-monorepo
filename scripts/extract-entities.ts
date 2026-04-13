import { mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, extname, join, relative, resolve } from "node:path";

type EntityType =
  | "products"
  | "systems"
  | "concepts"
  | "vendors"
  | "patterns"
  | "tools"
  | "frameworks"
  | "protocols"
  | "methodologies"
  | "libraries"
  | "architectures";

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

const DEFAULT_MAX_EVIDENCE = 12;
const DEFAULT_DISCOVER_LIMIT = 30;
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
  } = {
    maxEvidence: DEFAULT_MAX_EVIDENCE,
    dryRun: false,
    syncQmd: false,
    discover: false,
    discoverLimit: DEFAULT_DISCOVER_LIMIT,
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

function collectDiscoverCandidates(
  files: string[],
  repoRoot: string,
  knownPatterns: RegExp[],
  maxEvidence: number,
) {
  const candidates = new Map<string, DiscoverCandidate>();

  for (const file of files) {
    const lines = readFileSync(file, "utf8").split(/\r?\n/);
    for (let index = 0; index < lines.length; index += 1) {
      const line = lines[index]?.trim() ?? "";
      if (!line || line.length < 4) {
        continue;
      }

      if (knownPatterns.some((pattern) => pattern.test(line))) {
        continue;
      }

      for (const candidateText of extractCandidatesFromLine(line)) {
        if (knownPatterns.some((pattern) => pattern.test(candidateText))) {
          continue;
        }

        const existing = candidates.get(candidateText) ?? {
          text: candidateText,
          score: 0,
          count: 0,
          files: new Set<string>(),
          evidence: [],
        };

        existing.count += 1;
        existing.files.add(relative(repoRoot, file));
        existing.score = Math.max(existing.score, scoreCandidate(candidateText));

        if (existing.evidence.length < maxEvidence) {
          existing.evidence.push({
            file: relative(repoRoot, file),
            line: index + 1,
            text: line,
            alias: candidateText,
          });
        }

        candidates.set(candidateText, existing);
      }
    }
  }

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

  console.log(`Config: ${config.name}`);
  console.log(`Files scanned: ${files.length}`);

  if (args.discover) {
    const candidates = collectDiscoverCandidates(files, repoRoot, knownPatterns, args.maxEvidence);
    const outputPath = resolve(config.outputRoot, "_discover", `${config.name}.md`);
    const content = renderDiscoverReport(config, candidates, args.discoverLimit);

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

  if (!args.dryRun && args.syncQmd) {
    await syncQmd();
  }
}

await main();
