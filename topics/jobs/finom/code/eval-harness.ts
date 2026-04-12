/**
 * Financial Agent Evaluation Harness
 *
 * Demonstrates production-grade evaluation patterns for accounting AI:
 * - Field-level accuracy with severity weighting
 * - Confidence calibration assessment
 * - Per-market breakdown
 * - Regression detection against a baseline
 *
 * This is the evaluation infrastructure an AI team needs before
 * trusting any categorization or booking agent in production.
 *
 * Run with: bun run eval
 */

import { z } from "zod";

// ─── Test Case Schema ────────────────────────────────────────

const TestCase = z.object({
  id: z.string(),
  market: z.enum(["DE", "FR"]),
  description: z.string(),
  severity: z.enum(["critical", "high", "medium", "low"]),
  input: z.object({
    merchant: z.string(),
    amount: z.number(),
    description: z.string(),
    isB2B: z.boolean().default(false),
    counterpartyVatId: z.string().optional(),
  }),
  expected: z.object({
    accountCode: z.string(),
    vatRate: z.number(),
    vatAmount: z.number(),
    netAmount: z.number(),
    mechanism: z.enum(["standard", "reduced", "reverse_charge", "exempt"]),
  }),
});

type TestCase = z.infer<typeof TestCase>;

// ─── Agent Output Schema ─────────────────────────────────────

interface AgentOutput {
  accountCode: string;
  vatRate: number;
  vatAmount: number;
  netAmount: number;
  mechanism: string;
  confidence: number;
}

// ─── Field-Level Comparison ──────────────────────────────────

interface FieldResult {
  field: string;
  expected: string | number;
  actual: string | number;
  correct: boolean;
  delta?: number; // for numeric fields
}

interface CaseResult {
  testCaseId: string;
  market: string;
  severity: string;
  passed: boolean;
  fields: FieldResult[];
  confidence: number;
  severityWeight: number;
  weightedScore: number;
}

function compareFields(expected: TestCase["expected"], actual: AgentOutput): FieldResult[] {
  const results: FieldResult[] = [];

  results.push({
    field: "accountCode",
    expected: expected.accountCode,
    actual: actual.accountCode,
    correct: expected.accountCode === actual.accountCode,
  });

  results.push({
    field: "vatRate",
    expected: expected.vatRate,
    actual: actual.vatRate,
    correct: Math.abs(expected.vatRate - actual.vatRate) < 0.001,
    delta: Math.abs(expected.vatRate - actual.vatRate),
  });

  results.push({
    field: "vatAmount",
    expected: expected.vatAmount,
    actual: actual.vatAmount,
    correct: Math.abs(expected.vatAmount - actual.vatAmount) < 0.01,
    delta: Math.abs(expected.vatAmount - actual.vatAmount),
  });

  results.push({
    field: "netAmount",
    expected: expected.netAmount,
    actual: actual.netAmount,
    correct: Math.abs(expected.netAmount - actual.netAmount) < 0.01,
    delta: Math.abs(expected.netAmount - actual.netAmount),
  });

  results.push({
    field: "mechanism",
    expected: expected.mechanism,
    actual: actual.mechanism,
    correct: expected.mechanism === actual.mechanism,
  });

  return results;
}

// ─── Severity Weighting ──────────────────────────────────────

const SEVERITY_WEIGHTS: Record<string, number> = {
  critical: 4,
  high: 3,
  medium: 2,
  low: 1,
};

// ─── Calibration ─────────────────────────────────────────────

interface CalibrationBin {
  range: [number, number];
  count: number;
  correct: number;
  accuracy: number;
}

function computeCalibration(results: CaseResult[]): {
  bins: CalibrationBin[];
  expectedCalibrationError: number;
} {
  const binEdges = [0, 0.2, 0.4, 0.6, 0.8, 1.0];
  const bins: CalibrationBin[] = [];

  for (let i = 0; i < binEdges.length - 1; i++) {
    const low = binEdges[i];
    const high = binEdges[i + 1];
    const inBin = results.filter(
      (r) => r.confidence >= low && r.confidence < (i === binEdges.length - 2 ? high + 0.01 : high)
    );
    const correct = inBin.filter((r) => r.passed).length;
    bins.push({
      range: [low, high],
      count: inBin.length,
      correct,
      accuracy: inBin.length > 0 ? correct / inBin.length : 0,
    });
  }

  // Expected Calibration Error (ECE)
  const total = results.length;
  const ece = bins.reduce((sum, bin) => {
    if (bin.count === 0) return sum;
    const midpoint = (bin.range[0] + bin.range[1]) / 2;
    return sum + (bin.count / total) * Math.abs(bin.accuracy - midpoint);
  }, 0);

  return { bins, expectedCalibrationError: ece };
}

// ─── Report ──────────────────────────────────────────────────

interface EvalReport {
  totalCases: number;
  overallAccuracy: number;
  severityWeightedAccuracy: number;
  perMarket: Record<string, { accuracy: number; count: number; criticalErrors: number }>;
  perField: Record<string, { accuracy: number; count: number }>;
  calibration: ReturnType<typeof computeCalibration>;
  failures: Array<{ testCaseId: string; failedFields: string[]; severity: string }>;
}

function generateReport(results: CaseResult[]): EvalReport {
  const totalCases = results.length;
  const passed = results.filter((r) => r.passed).length;

  // Severity-weighted accuracy
  const totalWeight = results.reduce((s, r) => s + r.severityWeight, 0);
  const weightedCorrect = results
    .filter((r) => r.passed)
    .reduce((s, r) => s + r.severityWeight, 0);

  // Per-market
  const markets = [...new Set(results.map((r) => r.market))];
  const perMarket: EvalReport["perMarket"] = {};
  for (const m of markets) {
    const inMarket = results.filter((r) => r.market === m);
    const correct = inMarket.filter((r) => r.passed).length;
    const criticalErrors = inMarket.filter(
      (r) => !r.passed && r.severity === "critical"
    ).length;
    perMarket[m] = { accuracy: correct / inMarket.length, count: inMarket.length, criticalErrors };
  }

  // Per-field
  const allFields = results.flatMap((r) => r.fields);
  const fieldNames = [...new Set(allFields.map((f) => f.field))];
  const perField: EvalReport["perField"] = {};
  for (const f of fieldNames) {
    const fieldResults = allFields.filter((fr) => fr.field === f);
    const correct = fieldResults.filter((fr) => fr.correct).length;
    perField[f] = { accuracy: correct / fieldResults.length, count: fieldResults.length };
  }

  // Failures
  const failures = results
    .filter((r) => !r.passed)
    .map((r) => ({
      testCaseId: r.testCaseId,
      failedFields: r.fields.filter((f) => !f.correct).map((f) => f.field),
      severity: r.severity,
    }));

  return {
    totalCases,
    overallAccuracy: passed / totalCases,
    severityWeightedAccuracy: totalWeight > 0 ? weightedCorrect / totalWeight : 0,
    perMarket,
    perField,
    calibration: computeCalibration(results),
    failures,
  };
}

// ─── Simulated Agent Under Test ──────────────────────────────

function simulatedAgent(tc: TestCase): AgentOutput {
  // Simulates an agent that is mostly correct but has realistic failure modes
  const expected = tc.expected;

  // Introduce realistic errors for specific test cases
  if (tc.id === "TC-REVERSE-CHARGE") {
    // Agent misses reverse charge — common real-world failure
    return {
      accountCode: expected.accountCode,
      vatRate: 0.19, // Wrong: applied standard instead of reverse charge
      vatAmount: Math.round((tc.input.amount * 0.19 / 1.19) * 100) / 100,
      netAmount: Math.round((tc.input.amount / 1.19) * 100) / 100,
      mechanism: "standard", // Wrong
      confidence: 0.72,
    };
  }

  if (tc.id === "TC-MIXED-VAT") {
    // Agent gets the category wrong
    return {
      accountCode: "4930", // Wrong code
      vatRate: expected.vatRate,
      vatAmount: expected.vatAmount,
      netAmount: expected.netAmount,
      mechanism: expected.mechanism,
      confidence: 0.55,
    };
  }

  // Default: correct with high confidence
  return {
    ...expected,
    confidence: 0.92 + Math.random() * 0.05,
  };
}

// ─── Test Suite ──────────────────────────────────────────────

const TEST_SUITE: TestCase[] = [
  {
    id: "TC-OFFICE-DE",
    market: "DE",
    description: "Standard office supplies purchase, domestic",
    severity: "low",
    input: {
      merchant: "Büro Discount GmbH",
      amount: 119.0,
      description: "Office supplies",
      isB2B: false,
    },
    expected: {
      accountCode: "4930",
      vatRate: 0.19,
      vatAmount: 19.0,
      netAmount: 100.0,
      mechanism: "standard",
    },
  },
  {
    id: "TC-SOFTWARE-DE",
    market: "DE",
    description: "SaaS subscription, domestic",
    severity: "low",
    input: {
      merchant: "GitHub Inc",
      amount: 47.6,
      description: "GitHub Team monthly",
      isB2B: false,
    },
    expected: {
      accountCode: "4964",
      vatRate: 0.19,
      vatAmount: 7.6,
      netAmount: 40.0,
      mechanism: "standard",
    },
  },
  {
    id: "TC-REVERSE-CHARGE",
    market: "DE",
    description: "Cross-border B2B with VAT ID — reverse charge applies",
    severity: "critical",
    input: {
      merchant: "Dutch Consulting BV",
      amount: 5000.0,
      description: "Consulting services Q1",
      isB2B: true,
      counterpartyVatId: "NL123456789B01",
    },
    expected: {
      accountCode: "4900",
      vatRate: 0,
      vatAmount: 0,
      netAmount: 5000.0,
      mechanism: "reverse_charge",
    },
  },
  {
    id: "TC-TRAVEL-FR",
    market: "FR",
    description: "Train ticket, domestic France",
    severity: "medium",
    input: {
      merchant: "SNCF",
      amount: 120.0,
      description: "Train Paris-Lyon",
      isB2B: false,
    },
    expected: {
      accountCode: "6251",
      vatRate: 0.1,
      vatAmount: 10.91,
      netAmount: 109.09,
      mechanism: "reduced",
    },
  },
  {
    id: "TC-RESTAURANT-DE",
    market: "DE",
    description: "Business dinner, domestic",
    severity: "low",
    input: {
      merchant: "Steakhaus Berlin",
      amount: 178.5,
      description: "Business dinner with client",
      isB2B: false,
    },
    expected: {
      accountCode: "4650",
      vatRate: 0.19,
      vatAmount: 28.5,
      netAmount: 150.0,
      mechanism: "standard",
    },
  },
  {
    id: "TC-MIXED-VAT",
    market: "DE",
    description: "Receipt with standard and reduced VAT items",
    severity: "high",
    input: {
      merchant: "Supermarkt GmbH",
      amount: 53.5,
      description: "Office snacks and supplies",
      isB2B: false,
    },
    expected: {
      accountCode: "4650",
      vatRate: 0.19,
      vatAmount: 8.55,
      netAmount: 44.95,
      mechanism: "standard",
    },
  },
  {
    id: "TC-TELECOM-FR",
    market: "FR",
    description: "Mobile plan, domestic France",
    severity: "low",
    input: {
      merchant: "Orange France",
      amount: 35.99,
      description: "Forfait mobile pro",
      isB2B: false,
    },
    expected: {
      accountCode: "626",
      vatRate: 0.2,
      vatAmount: 6.0,
      netAmount: 29.99,
      mechanism: "standard",
    },
  },
  {
    id: "TC-EXEMPT-DE",
    market: "DE",
    description: "Kleinunternehmer §19 — no VAT charged",
    severity: "critical",
    input: {
      merchant: "Freelancer Schmidt",
      amount: 800.0,
      description: "Design work — Kleinunternehmer",
      isB2B: true,
    },
    expected: {
      accountCode: "4900",
      vatRate: 0,
      vatAmount: 0,
      netAmount: 800.0,
      mechanism: "exempt",
    },
  },
];

// ─── Run Evaluation ──────────────────────────────────────────

function runEvaluation(): EvalReport {
  const results: CaseResult[] = [];

  for (const tc of TEST_SUITE) {
    const output = simulatedAgent(tc);
    const fields = compareFields(tc.expected, output);
    const passed = fields.every((f) => f.correct);
    const severityWeight = SEVERITY_WEIGHTS[tc.severity];

    results.push({
      testCaseId: tc.id,
      market: tc.market,
      severity: tc.severity,
      passed,
      fields,
      confidence: output.confidence,
      severityWeight,
      weightedScore: passed ? severityWeight : 0,
    });
  }

  return generateReport(results);
}

// ─── Main ────────────────────────────────────────────────────

const report = runEvaluation();

console.log("=== Financial Agent Evaluation Report ===\n");
console.log(`Total test cases: ${report.totalCases}`);
console.log(`Overall accuracy: ${(report.overallAccuracy * 100).toFixed(1)}%`);
console.log(`Severity-weighted accuracy: ${(report.severityWeightedAccuracy * 100).toFixed(1)}%`);

console.log("\n--- Per-Market Breakdown ---");
for (const [market, stats] of Object.entries(report.perMarket)) {
  console.log(
    `  ${market}: ${(stats.accuracy * 100).toFixed(1)}% (${stats.count} cases, ${stats.criticalErrors} critical errors)`
  );
}

console.log("\n--- Per-Field Accuracy ---");
for (const [field, stats] of Object.entries(report.perField)) {
  console.log(`  ${field}: ${(stats.accuracy * 100).toFixed(1)}% (${stats.count} comparisons)`);
}

console.log("\n--- Calibration ---");
console.log(`  ECE: ${(report.calibration.expectedCalibrationError * 100).toFixed(2)}%`);
for (const bin of report.calibration.bins) {
  if (bin.count > 0) {
    console.log(
      `  [${bin.range[0].toFixed(1)}-${bin.range[1].toFixed(1)}]: accuracy=${(bin.accuracy * 100).toFixed(0)}%, count=${bin.count}`
    );
  }
}

if (report.failures.length > 0) {
  console.log("\n--- Failures ---");
  for (const f of report.failures) {
    console.log(`  ${f.testCaseId} [${f.severity}]: failed on ${f.failedFields.join(", ")}`);
  }
}

console.log("\n=== Evaluation Complete ===");
