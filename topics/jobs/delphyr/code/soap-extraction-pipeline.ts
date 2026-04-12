/**
 * SOAP Note Extraction Pipeline — Delphyr Context
 *
 * Demonstrates the ambient listening → structured clinical note pipeline.
 * Takes a mock consultation transcript and extracts structured SOAP notes
 * with citation links back to source transcript lines.
 *
 * No LLM calls — uses deterministic pattern matching to show the pipeline
 * architecture. In production, structured LLM output would replace the
 * keyword extraction.
 *
 * Run with: bun run soap-extraction-pipeline.ts
 */

// ─── Types ──────────────────────────────────────────────────────

type Speaker = "doctor" | "patient" | "unknown";

interface TranscriptUtterance {
  lineNumber: number;
  speaker: Speaker;
  text: string;
  timestamp: string; // simulated audio timestamp
}

interface SOAPCitation {
  sourceLineNumbers: number[];
  sourceText: string;
  confidence: number;
}

interface SOAPEntry {
  text: string;
  citations: SOAPCitation[];
}

interface SOAPNote {
  subjective: SOAPEntry[];
  objective: SOAPEntry[];
  assessment: SOAPEntry[];
  plan: SOAPEntry[];
}

interface ExtractionMetrics {
  totalEntries: number;
  totalCitations: number;
  averageCitationConfidence: number;
  uncitedEntries: number;
  sectionCoverage: Record<string, number>;
}

interface NegationCheck {
  term: string;
  isNegated: boolean;
  context: string;
  lineNumber: number;
}

// ─── Mock Transcript ────────────────────────────────────────────

const MOCK_TRANSCRIPT: TranscriptUtterance[] = [
  { lineNumber: 1, speaker: "doctor", text: "Good morning, Mrs. de Vries. How have you been feeling since our last visit?", timestamp: "00:00:05" },
  { lineNumber: 2, speaker: "patient", text: "Not great, doctor. I've been having this chest pain for about three days now. It comes and goes.", timestamp: "00:00:12" },
  { lineNumber: 3, speaker: "doctor", text: "Can you describe the pain? Is it sharp or more of a pressure?", timestamp: "00:00:22" },
  { lineNumber: 4, speaker: "patient", text: "More like pressure. Especially when I climb the stairs. It goes away when I rest.", timestamp: "00:00:28" },
  { lineNumber: 5, speaker: "doctor", text: "Any shortness of breath?", timestamp: "00:00:38" },
  { lineNumber: 6, speaker: "patient", text: "Yes, a bit, also with the stairs. No cough though.", timestamp: "00:00:42" },
  { lineNumber: 7, speaker: "doctor", text: "And dizziness or fainting?", timestamp: "00:00:48" },
  { lineNumber: 8, speaker: "patient", text: "No dizziness. No fainting. I do feel more tired than usual.", timestamp: "00:00:52" },
  { lineNumber: 9, speaker: "doctor", text: "Are you still taking the Metoprolol 50mg and the Lisinopril?", timestamp: "00:01:00" },
  { lineNumber: 10, speaker: "patient", text: "Yes, every morning. And the aspirin as well.", timestamp: "00:01:08" },
  { lineNumber: 11, speaker: "doctor", text: "Good. Let me check your blood pressure... It's 148 over 92. Heart rate is 78, regular rhythm.", timestamp: "00:01:15" },
  { lineNumber: 12, speaker: "doctor", text: "Lungs are clear bilaterally. No peripheral edema.", timestamp: "00:01:35" },
  { lineNumber: 13, speaker: "doctor", text: "I'm looking at your recent lab results. Your troponin was negative, which is reassuring. Cholesterol is elevated at 6.2 mmol/L.", timestamp: "00:01:45" },
  { lineNumber: 14, speaker: "doctor", text: "The ECG from last week showed no acute changes, just the known left ventricular hypertrophy.", timestamp: "00:02:00" },
  { lineNumber: 15, speaker: "doctor", text: "Based on what I'm seeing, this looks like stable angina — exertional chest pain that resolves with rest.", timestamp: "00:02:15" },
  { lineNumber: 16, speaker: "doctor", text: "It's not an acute event, but we should take it seriously given your history.", timestamp: "00:02:25" },
  { lineNumber: 17, speaker: "doctor", text: "I'd like to add Isosorbide Mononitrate 30mg once daily for the angina symptoms.", timestamp: "00:02:32" },
  { lineNumber: 18, speaker: "doctor", text: "We should also increase the statin — let's go to Atorvastatin 40mg given the cholesterol level.", timestamp: "00:02:40" },
  { lineNumber: 19, speaker: "doctor", text: "I'm referring you for a stress test within the next two weeks to assess the severity.", timestamp: "00:02:50" },
  { lineNumber: 20, speaker: "doctor", text: "Come back in four weeks, or sooner if the pain worsens or occurs at rest.", timestamp: "00:03:00" },
  { lineNumber: 21, speaker: "patient", text: "Should I be worried?", timestamp: "00:03:08" },
  { lineNumber: 22, speaker: "doctor", text: "We're catching this early. The negative troponin means no heart damage. We'll manage it with medication and the stress test will tell us more.", timestamp: "00:03:12" },
];

// ─── Extraction Patterns (Deterministic) ────────────────────────

// In production: structured LLM output with section classification
// Here: keyword-based extraction to demonstrate the pipeline architecture

const SUBJECTIVE_PATTERNS = [
  { keywords: ["pain", "pijn", "chest pain", "borstpijn"], category: "chief_complaint" },
  { keywords: ["days", "weeks", "since", "started"], category: "duration" },
  { keywords: ["stairs", "exercise", "exertion", "walking"], category: "triggers" },
  { keywords: ["rest", "resolves", "goes away", "better"], category: "relieving_factors" },
  { keywords: ["breath", "shortness", "dyspnoe", "ademhaling"], category: "associated_symptoms" },
  { keywords: ["dizz", "faint", "tired", "fatigue", "moe"], category: "associated_symptoms" },
  { keywords: ["cough", "nausea", "swelling", "palpitation"], category: "negative_symptoms" },
];

const OBJECTIVE_PATTERNS = [
  { keywords: ["blood pressure", "bp", "bloeddruk", "/"], category: "vitals", requiresNumber: true },
  { keywords: ["heart rate", "pulse", "hartslag", "bpm"], category: "vitals", requiresNumber: true },
  { keywords: ["lungs", "auscultation", "longen", "bilateral"], category: "examination" },
  { keywords: ["edema", "oedeem", "swelling"], category: "examination" },
  { keywords: ["troponin", "cholesterol", "ldl", "hdl", "hba1c"], category: "lab_results" },
  { keywords: ["ecg", "ekg", "electrocardiogram"], category: "investigations" },
  { keywords: ["hypertrophy", "lvh", "arrhythmia"], category: "investigations" },
];

const ASSESSMENT_PATTERNS = [
  { keywords: ["looks like", "suspect", "diagnos", "consistent with"], category: "diagnosis" },
  { keywords: ["angina", "infarct", "failure", "arrhythmia"], category: "diagnosis" },
  { keywords: ["stable", "acute", "chronic", "worsening"], category: "severity" },
  { keywords: ["reassuring", "concerning", "serious", "benign"], category: "prognosis" },
  { keywords: ["not an acute", "no heart damage", "catching early"], category: "prognosis" },
];

const PLAN_PATTERNS = [
  { keywords: ["prescri", "start", "add", "increase", "decrease", "stop"], category: "medication" },
  { keywords: ["mg", "daily", "twice", "morning", "evening"], category: "medication" },
  { keywords: ["refer", "stress test", "echo", "scan", "blood test"], category: "investigation" },
  { keywords: ["come back", "follow", "weeks", "return", "appointment"], category: "follow_up" },
  { keywords: ["sooner if", "worse", "emergency", "urgent"], category: "safety_net" },
];

// ─── Negation Detection ─────────────────────────────────────────

const NEGATION_MARKERS = [
  "no", "not", "without", "absent", "denies", "negative", "geen", "niet",
  "nor", "neither", "never", "none",
];

function detectNegations(transcript: TranscriptUtterance[]): NegationCheck[] {
  const clinicalTerms = [
    "pain", "cough", "dizziness", "fainting", "edema", "fever",
    "nausea", "vomiting", "diabetes", "hypertension",
  ];

  const checks: NegationCheck[] = [];

  for (const utterance of transcript) {
    const words = utterance.text.toLowerCase().split(/\s+/);

    for (const term of clinicalTerms) {
      const termIndex = words.findIndex((w) => w.includes(term));
      if (termIndex === -1) continue;

      // Check for negation markers within 3 words before the term
      const windowStart = Math.max(0, termIndex - 3);
      const window = words.slice(windowStart, termIndex);
      const isNegated = window.some((w) =>
        NEGATION_MARKERS.some((neg) => w.includes(neg))
      );

      // Also check "no X though" pattern
      const afterTerm = words.slice(termIndex, termIndex + 3).join(" ");
      const hasThoughPattern = afterTerm.includes("though");

      checks.push({
        term,
        isNegated: isNegated || hasThoughPattern,
        context: utterance.text,
        lineNumber: utterance.lineNumber,
      });
    }
  }

  return checks;
}

// ─── SOAP Extraction Pipeline ───────────────────────────────────

function matchesPatterns(
  text: string,
  patterns: Array<{ keywords: string[]; category: string; requiresNumber?: boolean }>
): Array<{ category: string; confidence: number }> {
  const lower = text.toLowerCase();
  const matches: Array<{ category: string; confidence: number }> = [];

  for (const pattern of patterns) {
    const matchedKeywords = pattern.keywords.filter((kw) => lower.includes(kw));
    if (matchedKeywords.length === 0) continue;

    // Require number if specified
    if (pattern.requiresNumber && !/\d/.test(text)) continue;

    const confidence = Math.min(
      0.95,
      0.5 + (matchedKeywords.length / pattern.keywords.length) * 0.4
    );

    matches.push({ category: pattern.category, confidence });
  }

  return matches;
}

function extractSOAPNote(transcript: TranscriptUtterance[]): SOAPNote {
  const note: SOAPNote = {
    subjective: [],
    objective: [],
    assessment: [],
    plan: [],
  };

  for (const utterance of transcript) {
    const citation: SOAPCitation = {
      sourceLineNumbers: [utterance.lineNumber],
      sourceText: utterance.text,
      confidence: 0,
    };

    // Patient statements → primarily Subjective
    if (utterance.speaker === "patient") {
      const matches = matchesPatterns(utterance.text, SUBJECTIVE_PATTERNS);
      if (matches.length > 0) {
        const bestMatch = matches.reduce((a, b) =>
          a.confidence > b.confidence ? a : b
        );
        citation.confidence = bestMatch.confidence;
        note.subjective.push({
          text: utterance.text,
          citations: [citation],
        });
      }
    }

    // Doctor statements → can be O, A, or P
    if (utterance.speaker === "doctor") {
      const objectiveMatches = matchesPatterns(utterance.text, OBJECTIVE_PATTERNS);
      const assessmentMatches = matchesPatterns(utterance.text, ASSESSMENT_PATTERNS);
      const planMatches = matchesPatterns(utterance.text, PLAN_PATTERNS);

      // Pick the strongest match
      const allMatches = [
        ...objectiveMatches.map((m) => ({ ...m, section: "objective" as const })),
        ...assessmentMatches.map((m) => ({ ...m, section: "assessment" as const })),
        ...planMatches.map((m) => ({ ...m, section: "plan" as const })),
      ];

      if (allMatches.length > 0) {
        const best = allMatches.reduce((a, b) =>
          a.confidence > b.confidence ? a : b
        );
        citation.confidence = best.confidence;

        note[best.section].push({
          text: utterance.text,
          citations: [citation],
        });
      }
    }
  }

  return note;
}

// ─── Evaluation Metrics ─────────────────────────────────────────

function computeExtractionMetrics(note: SOAPNote): ExtractionMetrics {
  const sections = {
    subjective: note.subjective,
    objective: note.objective,
    assessment: note.assessment,
    plan: note.plan,
  };

  let totalEntries = 0;
  let totalCitations = 0;
  let totalConfidence = 0;
  let uncitedEntries = 0;
  const sectionCoverage: Record<string, number> = {};

  for (const [name, entries] of Object.entries(sections)) {
    totalEntries += entries.length;
    sectionCoverage[name] = entries.length;

    for (const entry of entries) {
      totalCitations += entry.citations.length;
      if (entry.citations.length === 0) uncitedEntries++;
      for (const c of entry.citations) totalConfidence += c.confidence;
    }
  }

  return {
    totalEntries,
    totalCitations,
    averageCitationConfidence:
      totalCitations > 0
        ? Math.round((totalConfidence / totalCitations) * 1000) / 1000
        : 0,
    uncitedEntries,
    sectionCoverage,
  };
}

// ─── Reference SOAP Note (Gold Standard) ────────────────────────

const REFERENCE_SOAP = {
  subjective: [
    "Chest pain for 3 days, pressure-like, exertional (stairs), resolves with rest",
    "Shortness of breath with exertion",
    "No cough",
    "No dizziness or fainting",
    "Increased fatigue",
    "Adherent to medications (Metoprolol 50mg, Lisinopril, Aspirin)",
  ],
  objective: [
    "BP 148/92 mmHg",
    "HR 78, regular rhythm",
    "Lungs clear bilaterally",
    "No peripheral edema",
    "Troponin negative",
    "Cholesterol 6.2 mmol/L (elevated)",
    "ECG: no acute changes, known LVH",
  ],
  assessment: [
    "Stable angina — exertional chest pain resolving with rest",
    "Not an acute event",
    "Negative troponin reassuring (no heart damage)",
  ],
  plan: [
    "Start Isosorbide Mononitrate 30mg daily",
    "Increase statin to Atorvastatin 40mg",
    "Refer for stress test within 2 weeks",
    "Follow-up in 4 weeks",
    "Safety net: return sooner if pain worsens or occurs at rest",
  ],
};

// ─── Rendering ──────────────────────────────────────────────────

function renderSOAPNote(note: SOAPNote): string {
  const lines: string[] = [];

  const sections: Array<{ title: string; key: keyof SOAPNote }> = [
    { title: "S — Subjective", key: "subjective" },
    { title: "O — Objective", key: "objective" },
    { title: "A — Assessment", key: "assessment" },
    { title: "P — Plan", key: "plan" },
  ];

  for (const { title, key } of sections) {
    lines.push(`\n  ${title}`);
    lines.push("  " + "─".repeat(50));

    if (note[key].length === 0) {
      lines.push("    (no entries extracted)");
      continue;
    }

    for (const entry of note[key]) {
      const citation = entry.citations[0];
      const confLabel =
        citation && citation.confidence >= 0.8
          ? "high"
          : citation && citation.confidence >= 0.6
            ? "med"
            : "low";
      const lineRef = citation
        ? `[L${citation.sourceLineNumbers.join(",")}]`
        : "[no citation]";

      lines.push(
        `    • ${entry.text.slice(0, 70)}${entry.text.length > 70 ? "..." : ""}`
      );
      lines.push(`      ${lineRef} (conf: ${confLabel})`);
    }
  }

  return lines.join("\n");
}

// ─── Main Demo ──────────────────────────────────────────────────

console.log("=== SOAP Note Extraction Pipeline Demo ===\n");

// Step 1: Show the transcript
console.log("  Transcript: Mock consultation with Mrs. de Vries");
console.log("  Utterances:", MOCK_TRANSCRIPT.length);
console.log(
  "  Doctor lines:",
  MOCK_TRANSCRIPT.filter((u) => u.speaker === "doctor").length
);
console.log(
  "  Patient lines:",
  MOCK_TRANSCRIPT.filter((u) => u.speaker === "patient").length
);

// Step 2: Negation detection
console.log("\n  Negation Detection");
console.log("  " + "─".repeat(50));
const negations = detectNegations(MOCK_TRANSCRIPT);
for (const check of negations) {
  const icon = check.isNegated ? "⊘" : "●";
  console.log(
    `    ${icon} "${check.term}" — ${check.isNegated ? "NEGATED" : "PRESENT"} (L${check.lineNumber})`
  );
  console.log(`      Context: "${check.context.slice(0, 60)}..."`);
}

// Step 3: Extract SOAP note
console.log("\n  Extracted SOAP Note");
const soapNote = extractSOAPNote(MOCK_TRANSCRIPT);
console.log(renderSOAPNote(soapNote));

// Step 4: Metrics
const metrics = computeExtractionMetrics(soapNote);
console.log("\n  Extraction Metrics");
console.log("  " + "─".repeat(50));
console.log(`    Total entries: ${metrics.totalEntries}`);
console.log(`    Total citations: ${metrics.totalCitations}`);
console.log(`    Average citation confidence: ${metrics.averageCitationConfidence}`);
console.log(`    Uncited entries: ${metrics.uncitedEntries}`);
console.log(`    Section coverage: S=${metrics.sectionCoverage.subjective} O=${metrics.sectionCoverage.objective} A=${metrics.sectionCoverage.assessment} P=${metrics.sectionCoverage.plan}`);

// Step 5: Compare to reference
console.log("\n  Reference Comparison");
console.log("  " + "─".repeat(50));

const sectionKeys: Array<keyof typeof REFERENCE_SOAP> = ["subjective", "objective", "assessment", "plan"];
for (const key of sectionKeys) {
  const extracted = soapNote[key].length;
  const reference = REFERENCE_SOAP[key].length;
  const coverage = reference > 0 ? Math.round((extracted / reference) * 100) : 0;
  const label = key.charAt(0).toUpperCase();
  console.log(
    `    ${label}: ${extracted}/${reference} items (${coverage}% recall)`
  );
}

// Step 6: Clinical safety check
console.log("\n  Clinical Safety Checks");
console.log("  " + "─".repeat(50));

const safetyChecks = [
  {
    name: "Medication list extracted",
    pass: soapNote.subjective.some((e) =>
      e.text.toLowerCase().includes("metoprolol") || e.text.toLowerCase().includes("lisinopril")
    ) || soapNote.plan.some((e) => e.text.toLowerCase().includes("atorvastatin")),
  },
  {
    name: "Allergies checked",
    pass: false, // Not mentioned in this consultation
  },
  {
    name: "Negations correctly detected",
    pass: negations.filter((n) => n.isNegated).every((n) =>
      ["cough", "dizziness", "fainting"].includes(n.term)
    ),
  },
  {
    name: "Vital signs captured",
    pass: soapNote.objective.some((e) =>
      e.text.includes("148") || e.text.includes("92")
    ),
  },
  {
    name: "Follow-up plan specified",
    pass: soapNote.plan.some((e) =>
      e.text.toLowerCase().includes("week") || e.text.toLowerCase().includes("come back")
    ),
  },
  {
    name: "Safety net instructions included",
    pass: soapNote.plan.some((e) =>
      e.text.toLowerCase().includes("sooner") || e.text.toLowerCase().includes("worse")
    ),
  },
];

for (const check of safetyChecks) {
  console.log(`    ${check.pass ? "✓" : "✕"} ${check.name}`);
}

const passCount = safetyChecks.filter((c) => c.pass).length;
console.log(
  `\n    Safety score: ${passCount}/${safetyChecks.length} (${Math.round((passCount / safetyChecks.length) * 100)}%)`
);

// Summary
console.log(`\n${"═".repeat(56)}`);
console.log("  Pipeline Architecture Demonstrated:");
console.log(`${"═".repeat(56)}`);
console.log(`
  1. Speaker-labeled transcript → SOAP section routing
     (patient statements → S, doctor observations → O/A/P)

  2. Pattern-based extraction with confidence scoring
     (production: structured LLM output replaces keyword matching)

  3. Citation linking: every claim traces to source transcript line
     ("retrieve, don't reason" — the AI structures, not invents)

  4. Negation detection as a separate safety layer
     (critical in clinical AI: "no pain" ≠ "pain")

  5. Reference comparison for evaluation
     (gold-standard SOAP enables precision/recall measurement)

  6. Clinical safety checks as guardrails
     (medications, allergies, vitals, follow-up, safety net)
`);

console.log("=== Pipeline Demo Complete ===");
