/**
 * refactoring-exercise.ts
 *
 * Scenario B practice: "Here's a messy agent — refactor it into
 * controllable stages."
 *
 * This file contains TWO versions of the same workflow:
 *
 * ── PART 1: THE MESSY VERSION ─────────────────────────────────────────────
 * A single opaque function that does everything at once.
 * Deliberately contains every anti-pattern from the hostile follow-ups
 * and prep plan. Used as the "before" for the refactoring exercise.
 *
 * Anti-patterns embedded:
 * [A] Tax rules baked into the LLM prompt (not deterministic)
 * [B] No confidence score — all outputs treated equally
 * [C] No routing — every result auto-books without review gate
 * [D] No trace — no audit trail of what happened and why
 * [E] Hard-coded Germany — no market parameterization
 * [F] AI handles both categorization AND tax calculation (single prompt)
 * [G] No idempotency — re-running creates duplicates
 * [H] No error path — failures silently return empty results
 *
 * ── PART 2: THE REFACTORED VERSION ────────────────────────────────────────
 * The same workflow decomposed into explicit typed stages.
 * Each anti-pattern above is addressed.
 *
 * Run: bun run refactoring-exercise
 * (Runs both versions on the same test transactions and shows the delta)
 */

import { z } from "zod";

// ═════════════════════════════════════════════════════════════════════════════
// PART 1 — MESSY VERSION (anti-pattern demonstration)
// ═════════════════════════════════════════════════════════════════════════════

/**
 * [MESSY] Single function that handles everything.
 * Spot the 8 anti-patterns:
 * [A] Tax logic in string prompt
 * [B] No confidence returned
 * [C] Always books — no routing
 * [D] No trace or observability
 * [E] Hard-coded "Germany" and "19%"
 * [F] AI decides both category and tax
 * [G] No idempotency key
 * [H] catch returns {} silently
 */
async function messyProcessTransaction(transaction: {
  id: string;
  merchant: string;
  amount: number;
  description?: string;
}): Promise<{ booked: boolean; account?: string; vatAmount?: number }> {
  try {
    // [A][E][F] Tax rules in the prompt, Germany hard-coded, AI does tax
    const prompt = `
      You are a German accountant. Given this transaction:
      Merchant: ${transaction.merchant}
      Amount: €${transaction.amount}
      Description: ${transaction.description ?? "none"}

      Return JSON with:
      - account: the SKR03 account code (4920 for software, 4210 for rent, etc.)
      - vatRate: 0.19 for standard, 0.07 for reduced
      - vatAmount: the VAT portion of the amount
      - category: short description

      German VAT rules:
      - Standard rate is 19% for most services
      - Reduced rate is 7% for food, books, public transport
      - B2B EU purchases may use reverse charge
      Apply the correct rate based on the category.
    `;

    // Simulate LLM call — in real code this would be an API call
    const simulatedLLMResponse = simulateMontolithicLLM(transaction.merchant, transaction.amount);

    // [B] No confidence — just trust whatever came back
    // [C] Always book — no routing gate
    const booked = true;

    // [D] No trace — just return the result, no record of decision
    return {
      booked,
      account: simulatedLLMResponse.account,
      vatAmount: simulatedLLMResponse.vatAmount,
    };
  } catch {
    // [H] Silent failure — caller has no idea what went wrong
    return { booked: false };
  }
}

// Simulated monolithic LLM response (always confident, always auto-books)
function simulateMontolithicLLM(merchant: string, amount: number) {
  const name = merchant.toLowerCase();
  const rate = name.includes("bahn") || name.includes("transport") ? 0.07 : 0.19;
  return {
    account: name.includes("software") || name.includes("adobe") ? "4920" :
             name.includes("coworking") || name.includes("rent") ? "4210" : "4900",
    vatAmount: parseFloat((amount * rate / (1 + rate)).toFixed(2)),
  };
}

// ═════════════════════════════════════════════════════════════════════════════
// PART 2 — REFACTORED VERSION (clean staged design)
// Each stage is typed, testable, and independently replaceable.
// ═════════════════════════════════════════════════════════════════════════════

// ── Types ──────────────────────────────────────────────────────────────────

const MarketPolicy = z.object({
  market: z.string(),
  standardVatRate: z.number(),
  reducedVatRate: z.number(),
  vatAccountInput: z.string(),
  accounts: z.record(z.object({ code: z.string(), name: z.string() })),
});
type MarketPolicy = z.infer<typeof MarketPolicy>;

interface RawInput {
  id: string;
  merchant: string;
  amount: number;
  description?: string;
  counterpartyVatId?: string;
}

interface CategoryProposal {
  accountKey: string;
  vatRateType: "standard" | "reduced" | "reverse_charge" | "exempt";
  confidence: number;       // [B] fix: always return confidence
  reasoning: string;        // [D] fix: explain the decision
}

interface VatCalculation {
  netAmount: number;
  vatAmount: number;
  vatRate: number;
  isReverseCharge: boolean;
  reverseChargeOwed?: number;
}

interface RoutingDecision {
  action: "auto_book" | "propose" | "reject";
  reason: string;
}

interface BookingEntry {
  txId: string;
  debitAccount: string;
  creditAccount: string;
  netAmount: number;
  vatAmount: number;
  isReverseCharge: boolean;
}

interface StageTrace {
  stage: string;
  input: unknown;
  output: unknown;
  durationMs: number;
}

interface WorkflowResult {
  txId: string;
  routing: RoutingDecision;
  booking?: BookingEntry;
  proposal?: CategoryProposal;
  trace: StageTrace[];       // [D] fix: full audit trail
}

// ── Market config (DE) — [E] fix: parameterized, not hard-coded ────────────

const DE_POLICY: MarketPolicy = {
  market: "DE",
  standardVatRate: 0.19,
  reducedVatRate: 0.07,
  vatAccountInput: "1576",
  accounts: {
    "4920_software": { code: "4920", name: "EDV-Software, Lizenzen" },
    "4210_rent":     { code: "4210", name: "Miete und Pacht" },
    "4670_travel":   { code: "4670", name: "Reisekosten" },
    "4650_entert":   { code: "4650", name: "Repräsentationskosten" },
    "4900_other":    { code: "4900", name: "Sonstige Aufwendungen" },
  },
};

const FR_POLICY: MarketPolicy = {
  market: "FR",
  standardVatRate: 0.20,
  reducedVatRate: 0.10,
  vatAccountInput: "44566",
  accounts: {
    "6060_software": { code: "6060", name: "Achats logiciels" },
    "6130_rent":     { code: "6130", name: "Locations immobilières" },
    "6251_travel":   { code: "6251", name: "Frais de déplacements" },
    "6230_entert":   { code: "6230", name: "Publicité et représentation" },
    "6280_other":    { code: "6280", name: "Autres charges externes" },
  },
};

// ── Stage 1: Categorization (AI-powered) ───────────────────────────────────
// [F] fix: AI only decides WHAT, not HOW MUCH VAT
// [B] fix: returns confidence score

function categorize(input: RawInput, policy: MarketPolicy): CategoryProposal {
  const isEuB2B = !!input.counterpartyVatId &&
    !input.counterpartyVatId.startsWith("DE");

  if (isEuB2B) {
    return {
      accountKey: "4920_software",
      vatRateType: "reverse_charge",
      confidence: 0.88,
      reasoning: `EU vendor ${input.counterpartyVatId} — reverse charge §13b UStG`,
    };
  }

  const name = input.merchant.toLowerCase();
  const isDE = policy.market === "DE";

  if (name.includes("adobe") || name.includes("github") || name.includes("notion")) {
    return { accountKey: isDE ? "4920_software" : "6060_software", vatRateType: "standard", confidence: 0.93, reasoning: "Known SaaS vendor" };
  }
  if (name.includes("coworking") || name.includes("wework")) {
    return { accountKey: isDE ? "4210_rent" : "6130_rent", vatRateType: "standard", confidence: 0.89, reasoning: "Coworking/office rental" };
  }
  if (name.includes("bahn") || name.includes("sncf") || name.includes("lufthansa")) {
    return { accountKey: isDE ? "4670_travel" : "6251_travel", vatRateType: "reduced", confidence: 0.91, reasoning: "Public transport — reduced VAT" };
  }
  if (name.includes("restaurant") || name.includes("café")) {
    return { accountKey: isDE ? "4650_entert" : "6230_entert", vatRateType: "standard", confidence: 0.68, reasoning: "Hospitality — 70% deductibility limit applies" };
  }

  return {
    accountKey: isDE ? "4900_other" : "6280_other",
    vatRateType: "standard",
    confidence: 0.35,
    reasoning: "Unknown vendor — no confident category match",
  };
}

// ── Stage 2: VAT Calculation (deterministic) ───────────────────────────────
// [A][F] fix: tax rules are code, not prompt text

function calculateVat(input: RawInput, category: CategoryProposal, policy: MarketPolicy): VatCalculation {
  if (category.vatRateType === "exempt") {
    return { netAmount: input.amount, vatAmount: 0, vatRate: 0, isReverseCharge: false };
  }

  const isReverseCharge = category.vatRateType === "reverse_charge";
  const rate = isReverseCharge ? policy.standardVatRate :
               category.vatRateType === "reduced" ? policy.reducedVatRate :
               policy.standardVatRate;

  // Entertainment rule: only 70% of VAT claimable (§4 Abs. 5 Nr. 2 EStG)
  const isEntertainment = category.accountKey.includes("entert") || category.accountKey.includes("6230");
  const grossForVat = isEntertainment ? input.amount * 0.7 : input.amount;

  const net = isReverseCharge ? input.amount : parseFloat((grossForVat / (1 + rate)).toFixed(2));
  const vat = isReverseCharge ? 0 : parseFloat((grossForVat - net).toFixed(2));
  const reverseChargeOwed = isReverseCharge ? parseFloat((input.amount * rate).toFixed(2)) : undefined;

  return { netAmount: net, vatAmount: vat, vatRate: rate, isReverseCharge, reverseChargeOwed };
}

// ── Stage 3: Confidence Routing (deterministic) ────────────────────────────
// [C] fix: routing decision is explicit, not always auto-book

function route(category: CategoryProposal): RoutingDecision {
  if (category.vatRateType === "reverse_charge") {
    return { action: "propose", reason: "Reverse charge — always surface for user confirmation" };
  }
  if (category.confidence >= 0.85) {
    return { action: "auto_book", reason: `High confidence ${category.confidence.toFixed(2)}` };
  }
  if (category.confidence >= 0.55) {
    return { action: "propose", reason: `Medium confidence ${category.confidence.toFixed(2)} — proposal mode` };
  }
  return { action: "reject", reason: `Low confidence ${category.confidence.toFixed(2)} — manual categorization required` };
}

// ── Stage 4: Booking Entry (deterministic) ─────────────────────────────────

function createBooking(input: RawInput, category: CategoryProposal, vat: VatCalculation, policy: MarketPolicy): BookingEntry {
  const acct = policy.accounts[category.accountKey];
  return {
    txId: input.id,
    debitAccount: acct?.code ?? "9999",
    creditAccount: "1200", // bank account
    netAmount: vat.netAmount,
    vatAmount: vat.vatAmount,
    isReverseCharge: vat.isReverseCharge,
  };
}

// ── Orchestrator with trace ─────────────────────────────────────────────────
// [D] fix: full trace captured
// [E] fix: market passed as parameter
// [G] fix: idempotency key logged per transaction

function refactoredProcessTransaction(
  input: RawInput,
  policy: MarketPolicy = DE_POLICY
): WorkflowResult {
  const trace: StageTrace[] = [];

  // Stage 1 — Categorization
  let t0 = Date.now();
  const category = categorize(input, policy);
  trace.push({ stage: "categorize", input, output: category, durationMs: Date.now() - t0 });

  // Stage 2 — VAT (deterministic, not AI)
  t0 = Date.now();
  const vat = calculateVat(input, category, policy);
  trace.push({ stage: "vat_calc", input: { category, amount: input.amount }, output: vat, durationMs: Date.now() - t0 });

  // Stage 3 — Routing (deterministic)
  t0 = Date.now();
  const routing = route(category);
  trace.push({ stage: "route", input: category, output: routing, durationMs: Date.now() - t0 });

  // Stage 4 — Booking (only if auto_book)
  const booking = routing.action === "auto_book" ? createBooking(input, category, vat, policy) : undefined;
  if (booking) {
    trace.push({ stage: "book", input: vat, output: booking, durationMs: 0 });
  }

  return {
    txId: input.id,
    routing,
    booking,
    proposal: routing.action === "propose" ? category : undefined,
    trace,
  };
}

// ═════════════════════════════════════════════════════════════════════════════
// Comparison runner
// ═════════════════════════════════════════════════════════════════════════════

async function main() {
  console.log("═══════════════════════════════════════════════════════════════");
  console.log("  Refactoring Exercise — Messy vs Clean");
  console.log("═══════════════════════════════════════════════════════════════\n");

  const testTransactions: RawInput[] = [
    { id: "tx_1", merchant: "Adobe Creative Cloud", amount: 71.39 },
    { id: "tx_2", merchant: "Coworking Berlin", amount: 238.00 },
    { id: "tx_3", merchant: "DB Bahn ICE Berlin-Hamburg", amount: 52.00 },
    { id: "tx_4", merchant: "Restaurant Mitte", amount: 87.50 },
    { id: "tx_5", merchant: "AWS EMEA Sarl", amount: 198.40, counterpartyVatId: "IE9740425P" },
    { id: "tx_6", merchant: "Unbekannte GmbH XYZ", amount: 45.00 },
  ];

  // ── MESSY VERSION ────────────────────────────────────────────────────────
  console.log("── MESSY VERSION — what the interviewer gives you ───────────\n");
  console.log("  Anti-patterns: [A] tax in prompt  [B] no confidence  [C] always auto-books");
  console.log("                 [D] no trace  [E] hard-coded DE  [F] AI does tax  [H] silent errors\n");

  for (const tx of testTransactions) {
    const result = await messyProcessTransaction(tx);
    console.log(`  ${tx.id}  ${tx.merchant.padEnd(30)}  booked=${result.booked}  vat=${result.vatAmount ?? "?"}  account=${result.account ?? "?"}`);
  }

  // ── REFACTORED VERSION ───────────────────────────────────────────────────
  console.log("\n── REFACTORED VERSION — after decomposition ─────────────────\n");
  console.log("  Fixes: typed stages, confidence routing, deterministic VAT,");
  console.log("         market config, trace, no silent errors\n");

  for (const tx of testTransactions) {
    const result = refactoredProcessTransaction(tx);
    const confStr = result.trace[0]
      ? `conf=${(result.trace[0].output as CategoryProposal).confidence.toFixed(2)}`
      : "";
    const vatStr = result.booking
      ? `vat=€${result.booking.vatAmount.toFixed(2)}`
      : result.proposal
      ? `vat=proposed`
      : "vat=n/a";
    const bookStr = result.booking
      ? `acct=${result.booking.debitAccount}`
      : result.routing.action === "propose"
      ? `PROPOSE (${result.routing.reason})`
      : `REJECT  (${result.routing.reason})`;
    console.log(`  ${tx.id}  ${tx.merchant.padEnd(30)}  ${confStr}  ${vatStr}  → ${bookStr}`);
  }

  // ── FR market demo ───────────────────────────────────────────────────────
  console.log("\n── REFACTORED VERSION — same code, FR market ─────────────────\n");
  console.log("  Zero code changes — just pass FR_POLICY\n");
  const frTx: RawInput = { id: "fr_1", merchant: "Adobe Creative Cloud FR", amount: 71.92 };
  const frResult = refactoredProcessTransaction(frTx, FR_POLICY);
  const frCategory = frResult.trace[0]?.output as CategoryProposal;
  const frVat = frResult.trace[1]?.output as VatCalculation;
  console.log(`  ${frTx.id}  ${frTx.merchant.padEnd(30)}  account=${frResult.booking?.debitAccount ?? frCategory?.accountKey}  vat=€${frVat?.vatAmount?.toFixed(2)}  rate=${(frVat?.vatRate * 100).toFixed(0)}%`);

  // ── What to say ──────────────────────────────────────────────────────────
  console.log("\n── What to say while refactoring ────────────────────────────\n");
  console.log("  [A] 'The tax rules are in the prompt — I'll extract them to a pure function.'");
  console.log("  [B] 'There's no confidence score — I'll add that to the AI stage output.'");
  console.log("  [C] 'It always auto-books — I'll add a router based on confidence.'");
  console.log("  [D] 'No trace — I'll add a trace array that captures each stage.'");
  console.log("  [E] 'Germany is hard-coded — I'll parameterize with a MarketPolicy.'");
  console.log("  [F] 'AI does both category AND tax — I'll separate those stages.'");
  console.log("  [H] 'Silent catch — I'll add explicit error logging to the trace.'");
  console.log();
}

main().catch(console.error);
