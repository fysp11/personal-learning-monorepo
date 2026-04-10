/**
 * Finom Interview 3 — Live Round Rehearsal
 *
 * A compact, self-contained orchestrator demonstrating the core patterns
 * the interviewer is likely testing:
 *
 * 1. Typed stage boundaries
 * 2. Deterministic vs AI-powered separation
 * 3. Confidence-based routing
 * 4. Proposal mode vs action mode
 * 5. Observability / trace
 * 6. Multi-market extensibility (DE → FR)
 *
 * This is a ~20-minute implementation drill. Run with: bun run rehearsal
 */

import { z } from "zod";

// ─── Stage Contracts ──────────────────────────────────────────

const TransactionInput = z.object({
  id: z.string(),
  merchant: z.string(),
  amount: z.number(),
  currency: z.string().default("EUR"),
  description: z.string(),
  market: z.enum(["DE", "FR"]),
  isB2B: z.boolean().default(false),
  counterpartyVatId: z.string().optional(),
});

type TransactionInput = z.infer<typeof TransactionInput>;

interface CategoryProposal {
  accountCode: string;
  accountName: string;
  confidence: number;
  reasoning: string;
}

interface VatCalculation {
  vatRate: number;
  netAmount: number;
  vatAmount: number;
  mechanism: "standard" | "reduced" | "reverse_charge" | "exempt";
}

interface BookingEntry {
  debitAccount: string;
  creditAccount: string;
  amount: number;
  vatAmount: number;
  vatAccount: string;
}

type WorkflowOutcome =
  | { status: "auto_booked"; booking: BookingEntry }
  | { status: "needs_review"; reason: string; proposal: CategoryProposal }
  | { status: "rejected"; reason: string };

interface StageTrace {
  stage: string;
  durationMs: number;
  confidence?: number;
  decision?: string;
}

interface WorkflowResult {
  transactionId: string;
  outcome: WorkflowOutcome;
  trace: StageTrace[];
  totalDurationMs: number;
}

// ─── Market Configuration (Deterministic) ─────────────────────

interface MarketConfig {
  standardVatRate: number;
  reducedVatRate: number;
  chartOfAccounts: Record<string, { code: string; name: string }>;
  vatAccount: string;
}

const MARKET_CONFIG: Record<string, MarketConfig> = {
  DE: {
    standardVatRate: 0.19,
    reducedVatRate: 0.07,
    chartOfAccounts: {
      office: { code: "4930", name: "Bürobedarf" },
      travel: { code: "4660", name: "Reisekosten" },
      restaurant: { code: "4650", name: "Bewirtungskosten" },
      software: { code: "4964", name: "EDV-Kosten" },
      telecom: { code: "4920", name: "Telefon" },
      postage: { code: "4910", name: "Porto" },
    },
    vatAccount: "1576", // Vorsteuer
  },
  FR: {
    standardVatRate: 0.2,
    reducedVatRate: 0.055,
    chartOfAccounts: {
      office: { code: "6064", name: "Fournitures administratives" },
      travel: { code: "6251", name: "Voyages et déplacements" },
      restaurant: { code: "6257", name: "Réceptions" },
      software: { code: "6156", name: "Maintenance informatique" },
      telecom: { code: "626", name: "Frais postaux et télécommunications" },
      postage: { code: "626", name: "Frais postaux et télécommunications" },
    },
    vatAccount: "44566", // TVA déductible
  },
};

// ─── Stage 1: Categorization (AI-Powered) ─────────────────────

function categorize(tx: TransactionInput): CategoryProposal {
  // In production: call LLM with structured output
  // For rehearsal: keyword-based with explicit confidence modeling

  const merchantLower = tx.merchant.toLowerCase();
  const descLower = tx.description.toLowerCase();
  const market = MARKET_CONFIG[tx.market];

  const rules: Array<{
    keywords: string[];
    category: string;
    baseConfidence: number;
  }> = [
    {
      keywords: ["office", "büro", "staples", "bureau"],
      category: "office",
      baseConfidence: 0.92,
    },
    {
      keywords: ["restaurant", "café", "bistro", "dining"],
      category: "restaurant",
      baseConfidence: 0.88,
    },
    {
      keywords: ["software", "saas", "cloud", "aws", "azure", "github"],
      category: "software",
      baseConfidence: 0.95,
    },
    {
      keywords: ["train", "flight", "hotel", "sncf", "db ", "lufthansa"],
      category: "travel",
      baseConfidence: 0.9,
    },
    {
      keywords: ["vodafone", "telekom", "orange", "o2"],
      category: "telecom",
      baseConfidence: 0.94,
    },
    {
      keywords: ["post", "dhl", "ups", "fedex", "la poste"],
      category: "postage",
      baseConfidence: 0.91,
    },
  ];

  const combined = `${merchantLower} ${descLower}`;

  for (const rule of rules) {
    if (rule.keywords.some((kw) => combined.includes(kw))) {
      const entry = market.chartOfAccounts[rule.category];
      return {
        accountCode: entry.code,
        accountName: entry.name,
        confidence: rule.baseConfidence,
        reasoning: `Matched category '${rule.category}' from merchant/description keywords`,
      };
    }
  }

  // Fallback: low confidence, will route to review
  return {
    accountCode: market.chartOfAccounts.office.code,
    accountName: "Unknown — needs review",
    confidence: 0.3,
    reasoning: "No keyword match. Defaulting to review queue.",
  };
}

// ─── Stage 2: VAT Calculation (Deterministic) ─────────────────

function calculateVat(
  tx: TransactionInput,
  _category: CategoryProposal
): VatCalculation {
  const market = MARKET_CONFIG[tx.market];

  // Reverse charge: B2B intra-EU with valid VAT ID
  if (tx.isB2B && tx.counterpartyVatId) {
    return {
      vatRate: 0,
      netAmount: tx.amount,
      vatAmount: 0,
      mechanism: "reverse_charge",
    };
  }

  // Standard rate (simplified — production would check reduced-rate categories)
  const rate = market.standardVatRate;
  const net = Math.round((tx.amount / (1 + rate)) * 100) / 100;
  const vat = Math.round((tx.amount - net) * 100) / 100;

  return {
    vatRate: rate,
    netAmount: net,
    vatAmount: vat,
    mechanism: "standard",
  };
}

// ─── Stage 3: Confidence Router ───────────────────────────────

const THRESHOLDS = {
  autoBook: 0.85,
  review: 0.5,
};

function routeByConfidence(
  category: CategoryProposal
): "auto_book" | "review" | "reject" {
  if (category.confidence >= THRESHOLDS.autoBook) return "auto_book";
  if (category.confidence >= THRESHOLDS.review) return "review";
  return "reject";
}

// ─── Stage 4: Booking (Deterministic) ─────────────────────────

function createBooking(
  tx: TransactionInput,
  category: CategoryProposal,
  vat: VatCalculation
): BookingEntry {
  const market = MARKET_CONFIG[tx.market];
  return {
    debitAccount: category.accountCode,
    creditAccount: "1200", // Bank account (simplified)
    amount: vat.netAmount,
    vatAmount: vat.vatAmount,
    vatAccount: market.vatAccount,
  };
}

// ─── Orchestrator ─────────────────────────────────────────────

function processTransaction(input: TransactionInput): WorkflowResult {
  const trace: StageTrace[] = [];
  const start = performance.now();

  // Stage 1: Categorize (AI-powered)
  const catStart = performance.now();
  const category = categorize(input);
  trace.push({
    stage: "categorize",
    durationMs: performance.now() - catStart,
    confidence: category.confidence,
    decision: `${category.accountCode} ${category.accountName}`,
  });

  // Stage 2: Route by confidence
  const routeStart = performance.now();
  const route = routeByConfidence(category);
  trace.push({
    stage: "route",
    durationMs: performance.now() - routeStart,
    decision: route,
  });

  if (route === "reject") {
    return {
      transactionId: input.id,
      outcome: {
        status: "rejected",
        reason: `Confidence ${category.confidence} below review threshold`,
      },
      trace,
      totalDurationMs: performance.now() - start,
    };
  }

  if (route === "review") {
    return {
      transactionId: input.id,
      outcome: {
        status: "needs_review",
        reason: `Confidence ${category.confidence} below auto-book threshold`,
        proposal: category,
      },
      trace,
      totalDurationMs: performance.now() - start,
    };
  }

  // Stage 3: VAT (deterministic)
  const vatStart = performance.now();
  const vat = calculateVat(input, category);
  trace.push({
    stage: "vat_calculation",
    durationMs: performance.now() - vatStart,
    decision: `${vat.mechanism} @ ${(vat.vatRate * 100).toFixed(0)}%`,
  });

  // Stage 4: Booking (deterministic)
  const bookStart = performance.now();
  const booking = createBooking(input, category, vat);
  trace.push({
    stage: "booking",
    durationMs: performance.now() - bookStart,
    decision: `${booking.debitAccount} ← ${booking.amount}€ + ${booking.vatAmount}€ VAT`,
  });

  return {
    transactionId: input.id,
    outcome: { status: "auto_booked", booking },
    trace,
    totalDurationMs: performance.now() - start,
  };
}

// ─── Demo ─────────────────────────────────────────────────────

const testCases: TransactionInput[] = [
  {
    id: "TX-001",
    merchant: "Büro Discount GmbH",
    amount: 89.5,
    currency: "EUR",
    description: "Office supplies order",
    market: "DE",
    isB2B: false,
  },
  {
    id: "TX-002",
    merchant: "SNCF",
    amount: 120.0,
    currency: "EUR",
    description: "Train ticket Paris-Lyon",
    market: "FR",
    isB2B: false,
  },
  {
    id: "TX-003",
    merchant: "Unknown Vendor XYZ",
    amount: 2500.0,
    currency: "EUR",
    description: "Consulting services",
    market: "DE",
    isB2B: true,
    counterpartyVatId: "NL123456789B01",
  },
  {
    id: "TX-004",
    merchant: "GitHub Inc",
    amount: 44.0,
    currency: "EUR",
    description: "GitHub Team subscription",
    market: "DE",
    isB2B: false,
  },
];

console.log("=== Transaction Categorization Pipeline — Rehearsal ===\n");

for (const tx of testCases) {
  const result = processTransaction(tx);
  console.log(`--- ${result.transactionId} (${tx.merchant}, ${tx.market}) ---`);
  console.log(`  Outcome: ${result.outcome.status}`);

  if (result.outcome.status === "auto_booked") {
    const b = result.outcome.booking;
    console.log(
      `  Booking: ${b.debitAccount} ← ${b.amount}€ net + ${b.vatAmount}€ VAT`
    );
  } else if (result.outcome.status === "needs_review") {
    console.log(`  Reason: ${result.outcome.reason}`);
    console.log(
      `  Proposal: ${result.outcome.proposal.accountCode} (${result.outcome.proposal.confidence})`
    );
  } else {
    console.log(`  Reason: ${result.outcome.reason}`);
  }

  console.log("  Trace:");
  for (const t of result.trace) {
    console.log(
      `    ${t.stage}: ${t.decision}${t.confidence ? ` (conf: ${t.confidence})` : ""} [${t.durationMs.toFixed(1)}ms]`
    );
  }
  console.log();
}

console.log("=== Rehearsal Complete ===");
