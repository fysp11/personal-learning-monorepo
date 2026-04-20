/**
 * autonomous-batch-processor.ts
 *
 * Demonstrates the "go do the task, then come back" agentic pattern
 * that Ivo Dimitrov described as the product goal for Finom's AI Accountant.
 *
 * This is distinct from per-transaction pipeline demos (live-round-rehearsal.ts,
 * mcp-accounting-server.ts). Those process one transaction at a time.
 * This shows what a month-end autonomous close looks like:
 *
 *   Input:  [N transactions for a user's accounting period]
 *   Output: {
 *     autoProcessed: [...],       → handled without user input
 *     proposalsForApproval: [...],→ system's recommendation, user confirms
 *     requiresAttention: [...],   → genuinely ambiguous, user decides
 *     draftUStVA: {...},          → ready for user signature, not filed yet
 *     auditLog: [...],            → what the system did and why
 *     summary: string             → natural-language closing statement
 *   }
 *
 * Key design: the workflow earns autonomy by category.
 *   - SaaS subscriptions from known vendors → auto-book
 *   - New vendors → propose
 *   - B2B EU transactions → always surface for reverse-charge review
 *   - Filing → always require explicit user approval (FM-18 prevention)
 *
 * Run: bun run autonomous-batch
 */

import { z } from "zod";

// ─────────────────────────────────────────────────────────────────────────────
// Input types
// ───────────────────────────────────────��─────────────────────────────���───────

const RawTransaction = z.object({
  id: z.string(),
  date: z.string(), // ISO date
  merchantName: z.string(),
  amount: z.number(), // gross amount in EUR
  description: z.string().optional(),
  counterpartyVatId: z.string().optional(), // triggers reverse-charge check
  isInbound: z.boolean().default(false),    // true = income, false = expense
});
type RawTransaction = z.infer<typeof RawTransaction>;

// ──────────────────���───────────────────────────────────────────────────────��──
// Market policy (Germany — SKR03)
// ─────────────────────────────��───────────────────────────────────────────────

const DE_POLICY = {
  market: "DE" as const,
  standardVatRate: 0.19,
  reducedVatRate: 0.07,
  vatAccountInput: "1576",  // Vorsteuer
  vatAccountOutput: "1776", // Umsatzsteuer
  accounts: {
    "4920_software":       { code: "4920", name: "EDV-Software, Lizenzen" },
    "4210_rent":           { code: "4210", name: "Miete und Pacht" },
    "4650_entertainment":  { code: "4650", name: "Repräsentationskosten" },
    "4670_travel":         { code: "4670", name: "Reisekosten" },
    "4930_office":         { code: "4930", name: "Bürobedarf" },
    "8400_revenue":        { code: "8400", name: "Erlöse 19 % USt" },
    "8300_revenue_exempt": { code: "8300", name: "Erlöse 7 % USt" },
  },
};

// ───────────────────��─────────────────────────────────��───────────────────────
// Simulated AI categorization (in prod: LLM with Zod structured output)
// ─────────────────────────────────────────────────────────────────────────────

interface Categorization {
  accountKey: string;
  vatRate: number;
  confidence: number;
  reasoning: string;
  isReverseCharge: boolean;
}

function categorizeSim(tx: RawTransaction): Categorization {
  // Reverse charge: EU vendor with VAT ID, 0% on invoice
  const euVatIdCountries = ["IE", "FR", "NL", "ES", "IT", "PL", "AT", "BE"];
  const isEuVendor = euVatIdCountries.some(
    (c) => tx.counterpartyVatId?.startsWith(c)
  );
  if (isEuVendor && !tx.isInbound) {
    return {
      accountKey: "4920_software",
      vatRate: 0.19,
      confidence: 0.72,
      reasoning: `EU vendor ${tx.counterpartyVatId} — reverse charge §13b UStG applies`,
      isReverseCharge: true,
    };
  }

  // Inbound revenue
  if (tx.isInbound) {
    return {
      accountKey: "8400_revenue",
      vatRate: 0.19,
      confidence: 0.95,
      reasoning: "Inbound payment — invoice revenue at 19% USt",
      isReverseCharge: false,
    };
  }

  const name = tx.merchantName.toLowerCase();

  if (name.includes("adobe") || name.includes("github") || name.includes("linear") || name.includes("notion")) {
    return { accountKey: "4920_software", vatRate: 0.19, confidence: 0.92, reasoning: "Known SaaS vendor", isReverseCharge: false };
  }
  if (name.includes("coworking") || name.includes("wework") || name.includes("spaces")) {
    return { accountKey: "4210_rent", vatRate: 0.19, confidence: 0.88, reasoning: "Coworking space — Miete", isReverseCharge: false };
  }
  if (name.includes("db ") || name.includes("bahn") || name.includes("lufthansa") || name.includes("ryanair")) {
    return { accountKey: "4670_travel", vatRate: 0.07, confidence: 0.90, reasoning: "Travel — 7% reduced VAT", isReverseCharge: false };
  }
  if (name.includes("restaurant") || name.includes("café") || name.includes("bistro") || name.includes("essen")) {
    return { accountKey: "4650_entertainment", vatRate: 0.19, confidence: 0.71, reasoning: "Hospitality — Repräsentationskosten, 70% deductible", isReverseCharge: false };
  }
  if (name.includes("staples") || name.includes("bürobedarf") || name.includes("office")) {
    return { accountKey: "4930_office", vatRate: 0.19, confidence: 0.82, reasoning: "Office supplies", isReverseCharge: false };
  }

  return { accountKey: "9999_unknown", vatRate: 0.19, confidence: 0.28, reasoning: "Unknown vendor — manual review required", isReverseCharge: false };
}

// ───────────────────────��────────────────────────────────���────────────────────
// Deterministic VAT calculation
// ─────────────────────────────────────────────────────────────────────────────

interface VatBreakdown {
  grossAmount: number;
  netAmount: number;
  vatAmount: number;
  vatRate: number;
  vorsteuerClaimable: number; // may differ from vatAmount (entertainment rule)
  isReverseCharge: boolean;
  reverseChargeVatOwed?: number;
}

function calculateVat(tx: RawTransaction, cat: Categorization): VatBreakdown {
  const { grossAmount: gross, isReverseCharge } = { grossAmount: tx.amount, isReverseCharge: cat.isReverseCharge };
  const rate = cat.vatRate;
  const net = gross / (1 + rate);
  const vat = gross - net;

  // Entertainment rule: only 70% of Vorsteuer is claimable (§4 Abs. 5 Nr. 2 EStG)
  const isEntertainment = cat.accountKey === "4650_entertainment";
  const vorsteuerClaimable = isEntertainment ? vat * 0.7 : vat;

  // Reverse charge: add self-assessed VAT entry
  const reverseChargeVatOwed = isReverseCharge ? net * rate : undefined;

  return {
    grossAmount: gross,
    netAmount: parseFloat(net.toFixed(2)),
    vatAmount: parseFloat(vat.toFixed(2)),
    vatRate: rate,
    vorsteuerClaimable: parseFloat(vorsteuerClaimable.toFixed(2)),
    isReverseCharge,
    reverseChargeVatOwed: reverseChargeVatOwed !== undefined
      ? parseFloat(reverseChargeVatOwed.toFixed(2))
      : undefined,
  };
}

// ──────────────────────���───────────────────────────────��──────────────────────
// Routing decision
// ───────────────────────────────────────────��─────────────────────────────────

type RoutingDecision = "auto_book" | "propose" | "requires_attention";

function route(cat: Categorization): RoutingDecision {
  // Reverse charge always surfaced for review — compliance risk too high to auto-book
  if (cat.isReverseCharge) return "requires_attention";
  // Unknown vendor
  if (cat.accountKey === "9999_unknown") return "requires_attention";
  if (cat.confidence >= 0.85) return "auto_book";
  if (cat.confidence >= 0.55) return "propose";
  return "requires_attention";
}

// ─────────────────────────────────────────────────────────────────────────────
// Output types
// ────────────────────────────────────────���────────────────────────────────────

interface ProcessedLine {
  txId: string;
  date: string;
  merchant: string;
  amount: number;
  account: string;
  vatBreakdown: VatBreakdown;
  confidence: number;
  reasoning: string;
}

interface ProposalItem {
  txId: string;
  date: string;
  merchant: string;
  amount: number;
  proposedAccount: string;
  proposedVatRate: number;
  confidence: number;
  reasoning: string;
  userAction: "confirm" | "override" | "skip";
}

interface AttentionItem {
  txId: string;
  date: string;
  merchant: string;
  amount: number;
  reason: string;
  hint?: string;
  isReverseCharge: boolean;
}

interface DraftUStVA {
  period: string;             // e.g. "2026-03"
  totalOutputVat: number;     // Kz 81: total VAT on sales
  totalInputVat: number;      // Kz 63: total Vorsteuer (input VAT)
  reverseChargeOutputVat: number; // Kz 67: self-assessed VAT from reverse charge
  reverseChargeInputVat: number;  // included in Kz 63 if claimable
  zahllast: number;           // net amount owed to Finanzamt
  requiresUserSignature: true; // always — filing is irreversible
}

interface MonthCloseReport {
  userId: string;
  period: string;
  processedAt: string;
  autoProcessed: ProcessedLine[];
  proposalsForApproval: ProposalItem[];
  requiresAttention: AttentionItem[];
  draftUStVA: DraftUStVA;
  auditLog: string[];
  summary: string;
}

// ────────────────────────────────────────��────────────────────────────────────
// Autonomous batch processor
// ─────────────────────────────────────��─────────────────────────────��─────────

function processMonthBatch(
  userId: string,
  period: string,
  transactions: RawTransaction[]
): MonthCloseReport {
  const auditLog: string[] = [];
  const autoProcessed: ProcessedLine[] = [];
  const proposalsForApproval: ProposalItem[] = [];
  const requiresAttention: AttentionItem[] = [];

  auditLog.push(`[${new Date().toISOString()}] Starting batch close for ${userId}, period ${period}`);
  auditLog.push(`[input] ${transactions.length} transactions to process`);

  let totalOutputVat = 0;
  let totalInputVat = 0;
  let reverseChargeOutputVat = 0;
  let reverseChargeInputVat = 0;

  for (const tx of transactions) {
    const cat = categorizeSim(tx);
    const vat = calculateVat(tx, cat);
    const decision = route(cat);

    auditLog.push(
      `  tx ${tx.id}: ${tx.merchantName} €${tx.amount} → ${decision} (conf ${cat.confidence.toFixed(2)}, ${cat.accountKey})`
    );

    // Accumulate VAT totals (only for confirmed bookings and auto-books)
    // Proposals and attention items not counted until confirmed
    if (decision === "auto_book") {
      if (tx.isInbound) {
        totalOutputVat += vat.vatAmount;
      } else {
        totalInputVat += vat.vorsteuerClaimable;
        if (vat.isReverseCharge && vat.reverseChargeVatOwed !== undefined) {
          reverseChargeOutputVat += vat.reverseChargeVatOwed;
          reverseChargeInputVat += vat.vorsteuerClaimable;
        }
      }

      const policy = DE_POLICY.accounts[cat.accountKey as keyof typeof DE_POLICY.accounts];
      autoProcessed.push({
        txId: tx.id,
        date: tx.date,
        merchant: tx.merchantName,
        amount: tx.amount,
        account: policy ? `${policy.code} ${policy.name}` : cat.accountKey,
        vatBreakdown: vat,
        confidence: cat.confidence,
        reasoning: cat.reasoning,
      });
    } else if (decision === "propose") {
      const policy = DE_POLICY.accounts[cat.accountKey as keyof typeof DE_POLICY.accounts];
      proposalsForApproval.push({
        txId: tx.id,
        date: tx.date,
        merchant: tx.merchantName,
        amount: tx.amount,
        proposedAccount: policy ? `${policy.code} ${policy.name}` : cat.accountKey,
        proposedVatRate: vat.vatRate,
        confidence: cat.confidence,
        reasoning: cat.reasoning,
        userAction: "confirm", // default — user changes if needed
      });
    } else {
      requiresAttention.push({
        txId: tx.id,
        date: tx.date,
        merchant: tx.merchantName,
        amount: tx.amount,
        reason: cat.isReverseCharge
          ? `Reverse charge detected (§13b UStG): ${cat.reasoning}`
          : cat.confidence < 0.35
          ? `Unknown vendor — cannot classify with confidence ${cat.confidence.toFixed(2)}`
          : `Low confidence (${cat.confidence.toFixed(2)}): ${cat.reasoning}`,
        hint: cat.isReverseCharge
          ? `Self-assess ${vat.reverseChargeVatOwed?.toFixed(2)} EUR as both input and output VAT`
          : undefined,
        isReverseCharge: cat.isReverseCharge,
      });
    }
  }

  // Draft UStVA — uses only auto-booked amounts (conservative)
  // In production: add confirmed proposals after user approval
  const zahllast = totalOutputVat + reverseChargeOutputVat - totalInputVat;
  const draftUStVA: DraftUStVA = {
    period,
    totalOutputVat: parseFloat(totalOutputVat.toFixed(2)),
    totalInputVat: parseFloat(totalInputVat.toFixed(2)),
    reverseChargeOutputVat: parseFloat(reverseChargeOutputVat.toFixed(2)),
    reverseChargeInputVat: parseFloat(reverseChargeInputVat.toFixed(2)),
    zahllast: parseFloat(zahllast.toFixed(2)),
    requiresUserSignature: true,
  };

  auditLog.push(`[ustava-draft] Zahllast: €${draftUStVA.zahllast} (output: €${totalOutputVat.toFixed(2)}, input: -€${totalInputVat.toFixed(2)})`);
  auditLog.push(`[complete] ${autoProcessed.length} auto-booked, ${proposalsForApproval.length} proposals, ${requiresAttention.length} require attention`);

  const autoCount = autoProcessed.length;
  const propCount = proposalsForApproval.length;
  const attCount = requiresAttention.length;
  const total = transactions.length;

  const summary =
    `I processed ${total} transactions for ${period}. ` +
    `${autoCount} were categorized and booked automatically. ` +
    `${propCount > 0 ? `${propCount} need your confirmation — I've prepared proposals showing what I'd do and why. ` : ""}` +
    `${attCount > 0 ? `${attCount} require your attention, including ${requiresAttention.filter((a) => a.isReverseCharge).length} reverse-charge item(s) where I need you to confirm the VAT self-assessment. ` : ""}` +
    `Your draft UStVA for ${period} shows a Zahllast of €${draftUStVA.zahllast.toFixed(2)}. ` +
    `Review the ${attCount > 0 ? "flagged items and " : ""}draft before I submit to ELSTER — I'll wait for your signature.`;

  return {
    userId,
    period,
    processedAt: new Date().toISOString(),
    autoProcessed,
    proposalsForApproval,
    requiresAttention,
    draftUStVA,
    auditLog,
    summary,
  };
}

// ──────��─────────────────────────────────────────────────────────���────────────
// Demo — Anna's March 2026 batch
// ───────────────────────────────────────���─────────────────────────────────────

function printReport(report: MonthCloseReport): void {
  console.log("═══════���═══════════════════════════════════════════════════════");
  console.log("  Autonomous Month-Close Report");
  console.log(`  User: ${report.userId}   Period: ${report.period}`);
  console.log("═════════════════════��════════════════════════════���════════════\n");

  // Auto-processed
  console.log(`── Auto-booked (${report.autoProcessed.length}) — no action needed ─────────────────\n`);
  for (const item of report.autoProcessed) {
    const vatLabel = item.vatBreakdown.isReverseCharge ? "[reverse charge]" : `[Vorsteuer €${item.vatBreakdown.vorsteuerClaimable.toFixed(2)}]`;
    console.log(`  ✓  ${item.date}  ${item.merchant.padEnd(28)} €${item.amount.toFixed(2).padStart(8)}  →  ${item.account}  ${vatLabel}`);
  }

  // Proposals
  if (report.proposalsForApproval.length > 0) {
    console.log(`\n── Proposals (${report.proposalsForApproval.length}) — confirm or override ──────────────────\n`);
    for (const item of report.proposalsForApproval) {
      console.log(`  ?  ${item.date}  ${item.merchant.padEnd(28)} €${item.amount.toFixed(2).padStart(8)}`);
      console.log(`     → Proposed: ${item.proposedAccount}  (conf: ${item.confidence.toFixed(2)})`);
      console.log(`     → Reason: ${item.reasoning}`);
    }
  }

  // Requires attention
  if (report.requiresAttention.length > 0) {
    console.log(`\n── Requires your attention (${report.requiresAttention.length}) ──────────────────────────────\n`);
    for (const item of report.requiresAttention) {
      const flag = item.isReverseCharge ? "⚑ RC" : "  ! ";
      console.log(`  ${flag}  ${item.date}  ${item.merchant.padEnd(28)} €${item.amount.toFixed(2).padStart(8)}`);
      console.log(`     → ${item.reason}`);
      if (item.hint) console.log(`     → Hint: ${item.hint}`);
    }
  }

  // Draft UStVA
  console.log("\n── Draft UStVA ──────────────────────────────────────────────────\n");
  const u = report.draftUStVA;
  console.log(`  Period:              ${u.period}`);
  console.log(`  Output VAT (Kz 81):  €${u.totalOutputVat.toFixed(2)}`);
  if (u.reverseChargeOutputVat > 0) {
    console.log(`  Reverse charge VAT:  €${u.reverseChargeOutputVat.toFixed(2)}`);
  }
  console.log(`  Input VAT (Kz 63):  -€${u.totalInputVat.toFixed(2)}`);
  console.log(`  ────────────��───────────────────`);
  console.log(`  Zahllast:            €${u.zahllast.toFixed(2)}`);
  console.log(`\n  ⚠  Filing requires your explicit signature — not auto-submitted`);

  // Summary (the "come back" message)
  console.log("\n── Summary ───────���────────────────────────���─────────────────────\n");
  console.log(`  ${report.summary}`);

  // Audit log
  console.log("\n── Audit log ─────────────────────────���──────────────────────────\n");
  for (const entry of report.auditLog) {
    console.log(`  ${entry}`);
  }
  console.log();
}

async function main() {
  // Anna's March 2026 transactions — a realistic freelancer month
  const transactions: RawTransaction[] = [
    // Revenue
    { id: "tx_01", date: "2026-03-03", merchantName: "Client A GmbH (invoice IN-2026-03)", amount: 4760.00, isInbound: true },
    { id: "tx_02", date: "2026-03-17", merchantName: "Client B AG (invoice IN-2026-04)", amount: 3808.00, isInbound: true },

    // Known SaaS — high confidence auto-book
    { id: "tx_03", date: "2026-03-01", merchantName: "Adobe Creative Cloud", amount: 71.39, isInbound: false },
    { id: "tx_04", date: "2026-03-01", merchantName: "GitHub Team Plan", amount: 47.60, isInbound: false },
    { id: "tx_05", date: "2026-03-01", merchantName: "Linear (project management)", amount: 22.61, isInbound: false },
    { id: "tx_06", date: "2026-03-05", merchantName: "Notion Team", amount: 16.00, isInbound: false },

    // Coworking — high confidence auto-book
    { id: "tx_07", date: "2026-03-01", merchantName: "Coworking Berlin Mitte", amount: 238.00, isInbound: false },

    // Travel — auto-book (7% VAT)
    { id: "tx_08", date: "2026-03-12", merchantName: "DB Bahn ICE Hamburg-Berlin", amount: 52.00, isInbound: false },

    // Restaurant — medium confidence (70% deductibility rule)
    { id: "tx_09", date: "2026-03-10", merchantName: "Restaurant Grill 36", amount: 87.50, isInbound: false },
    { id: "tx_10", date: "2026-03-22", merchantName: "Café Espresso Bar", amount: 34.00, isInbound: false },

    // EU reverse charge — always surfaces for attention
    { id: "tx_11", date: "2026-03-01", merchantName: "AWS EMEA Sarl (cloud infra)", amount: 198.40, isInbound: false, counterpartyVatId: "IE9740425P", description: "Reverse charge" },
    { id: "tx_12", date: "2026-03-01", merchantName: "Google Ireland Ltd (Workspace)", amount: 59.50, isInbound: false, counterpartyVatId: "IE6388047V", description: "Reverse charge" },

    // Unknown vendor — low confidence, requires attention
    { id: "tx_13", date: "2026-03-15", merchantName: "TKS Telepost Kabel AG", amount: 45.00, isInbound: false },
    { id: "tx_14", date: "2026-03-28", merchantName: "Unbekannt 4927482", amount: 12.00, isInbound: false },

    // Office supplies — auto-book
    { id: "tx_15", date: "2026-03-08", merchantName: "Staples Office Supplies", amount: 34.00, isInbound: false },
  ];

  const report = processMonthBatch("anna_freelancer_de", "2026-03", transactions);
  printReport(report);
}

main().catch(console.error);
