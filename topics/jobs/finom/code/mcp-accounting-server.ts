/**
 * MCP Accounting Skills Server (TypeScript)
 *
 * A minimal Model Context Protocol server exposing three accounting tools:
 *   1. categorize_transaction (AI-powered — keyword-based simulation)
 *   2. calculate_vat (Deterministic — rule engine)
 *   3. create_booking (Deterministic — double-entry record)
 *
 * Key design principle: VAT and booking are deterministic because compliance
 * errors are non-negotiable. Categorization is the AI step because merchant
 * text is genuinely ambiguous.
 *
 * This demonstrates MCP fluency for Finom's "stitched with MCP" architecture.
 * In production, each skill would be a separate MCP server deployed independently.
 *
 * Run with: bun run mcp-server
 *
 * Note: This is a standalone demo that simulates MCP tool semantics without
 * requiring the full MCP SDK. It shows the tool contracts, input/output schemas,
 * and the separation of concerns that MCP enables.
 */

import { z } from "zod";

// ─── Tool Schemas (MCP Tool Contracts) ───────────────────────

const CategorizeInput = z.object({
  merchant: z.string().describe("Merchant or vendor name"),
  amount: z.number().describe("Transaction amount in EUR"),
  description: z.string().describe("Transaction description from bank statement"),
  market: z.enum(["DE", "FR", "ES", "IT", "NL"]).default("DE").describe("ISO market code"),
});

const CategorizeOutput = z.object({
  accountCode: z.string(),
  accountName: z.string(),
  confidence: z.number().min(0).max(1),
  reasoning: z.string(),
  market: z.string(),
});

const VatInput = z.object({
  amount: z.number().describe("Gross transaction amount in EUR"),
  market: z.enum(["DE", "FR", "ES", "IT", "NL"]).describe("Market code"),
  category: z.string().describe("Expense category (e.g., 'office', 'travel')"),
  isB2B: z.boolean().default(false).describe("Is this a B2B transaction?"),
  counterpartyVatId: z.string().optional().describe("EU VAT ID for reverse charge"),
});

const VatOutput = z.object({
  grossAmount: z.number(),
  netAmount: z.number(),
  vatAmount: z.number(),
  vatRate: z.number(),
  mechanism: z.enum(["standard", "reduced", "reverse_charge", "exempt"]),
  note: z.string().optional(),
});

const BookingInput = z.object({
  date: z.string().describe("Transaction date (YYYY-MM-DD)"),
  description: z.string().describe("Booking description"),
  expenseAccount: z.string().describe("Debit account code"),
  bankAccount: z.string().default("1200").describe("Credit account (bank)"),
  netAmount: z.number().describe("Net transaction amount"),
  vatAmount: z.number().default(0).describe("VAT amount"),
  vatAccount: z.string().default("1576").describe("Input tax account"),
  market: z.enum(["DE", "FR", "ES", "IT", "NL"]).default("DE"),
});

const BookingOutput = z.object({
  id: z.string(),
  date: z.string(),
  description: z.string(),
  entries: z.array(z.object({
    account: z.string(),
    accountName: z.string(),
    debit: z.number(),
    credit: z.number(),
  })),
  balanced: z.boolean(),
  grossAmount: z.number(),
});

// ─── Market Policy Modules ───────────────────────────────────

interface MarketPolicy {
  standardRate: number;
  reducedRate: number;
  reducedCategories: string[];
  accounts: Record<string, { code: string; name: string }>;
  vatAccount: string;
  vatAccountName: string;
}

const POLICIES: Record<string, MarketPolicy> = {
  DE: {
    standardRate: 0.19,
    reducedRate: 0.07,
    reducedCategories: ["food_basic", "books", "public_transport"],
    accounts: {
      office: { code: "4930", name: "Bürobedarf" },
      travel: { code: "4660", name: "Reisekosten" },
      restaurant: { code: "4650", name: "Bewirtungskosten" },
      software: { code: "4964", name: "EDV-Kosten" },
      telecom: { code: "4920", name: "Telefon" },
      postage: { code: "4910", name: "Porto" },
      consulting: { code: "4900", name: "Sonstige Betriebsausgaben" },
      insurance: { code: "4360", name: "Versicherungen" },
      rent: { code: "4210", name: "Miete" },
    },
    vatAccount: "1576",
    vatAccountName: "Vorsteuer 19%",
  },
  FR: {
    standardRate: 0.20,
    reducedRate: 0.055,
    reducedCategories: ["food_basic", "books", "water"],
    accounts: {
      office: { code: "6064", name: "Fournitures administratives" },
      travel: { code: "6251", name: "Voyages et déplacements" },
      restaurant: { code: "6257", name: "Réceptions" },
      software: { code: "6156", name: "Maintenance informatique" },
      telecom: { code: "626", name: "Frais postaux et télécommunications" },
      postage: { code: "626", name: "Frais postaux et télécommunications" },
      consulting: { code: "6226", name: "Honoraires" },
      insurance: { code: "616", name: "Primes d'assurance" },
      rent: { code: "613", name: "Locations" },
    },
    vatAccount: "44566",
    vatAccountName: "TVA déductible",
  },
  ES: {
    standardRate: 0.21,
    reducedRate: 0.10,
    reducedCategories: ["food_basic", "public_transport", "hospitality"],
    accounts: {
      office: { code: "629", name: "Material de oficina" },
      travel: { code: "629", name: "Gastos de viaje" },
      restaurant: { code: "627", name: "Gastos de representación" },
      software: { code: "629", name: "Software y licencias" },
      telecom: { code: "629", name: "Telecomunicaciones" },
      postage: { code: "629", name: "Correos y mensajería" },
      consulting: { code: "623", name: "Servicios profesionales" },
      insurance: { code: "625", name: "Primas de seguros" },
      rent: { code: "621", name: "Arrendamientos" },
    },
    vatAccount: "472",
    vatAccountName: "IVA soportado",
  },
  IT: {
    standardRate: 0.22,
    reducedRate: 0.10,
    reducedCategories: ["food_basic", "public_transport", "tourism"],
    accounts: {
      office: { code: "6400", name: "Cancelleria e stampati" },
      travel: { code: "6300", name: "Viaggi e trasferte" },
      restaurant: { code: "6310", name: "Spese di rappresentanza" },
      software: { code: "6500", name: "Software e licenze" },
      telecom: { code: "6200", name: "Telefono e internet" },
      postage: { code: "6210", name: "Spese postali" },
      consulting: { code: "6100", name: "Consulenze" },
      insurance: { code: "6800", name: "Assicurazioni" },
      rent: { code: "6000", name: "Affitti" },
    },
    vatAccount: "2600",
    vatAccountName: "IVA a credito",
  },
  NL: {
    standardRate: 0.21,
    reducedRate: 0.09,
    reducedCategories: ["food_basic", "books", "accommodation"],
    accounts: {
      office: { code: "4100", name: "Kantoorbenodigdheden" },
      travel: { code: "4300", name: "Reiskosten" },
      restaurant: { code: "4310", name: "Representatiekosten" },
      software: { code: "4400", name: "Software en licenties" },
      telecom: { code: "4200", name: "Telefoon en internet" },
      postage: { code: "4210", name: "Portokosten" },
      consulting: { code: "4500", name: "Advieskosten" },
      insurance: { code: "4600", name: "Verzekeringen" },
      rent: { code: "4000", name: "Huur" },
    },
    vatAccount: "1510",
    vatAccountName: "BTW voorbelasting",
  },
};

// ─── Tool 1: Categorize Transaction (AI-Powered) ────────────

type CategorizeInput = z.infer<typeof CategorizeInput>;
type CategorizeOutput = z.infer<typeof CategorizeOutput>;

function categorizeTransaction(input: CategorizeInput): CategorizeOutput {
  const policy = POLICIES[input.market]!;
  const combined = `${input.merchant} ${input.description}`.toLowerCase();

  const rules: Array<{ keywords: string[]; category: string; confidence: number }> = [
    { keywords: ["office", "büro", "staples", "bureau", "oficina", "ufficio", "kantoor"], category: "office", confidence: 0.92 },
    { keywords: ["restaurant", "café", "bistro", "dining", "ristorante", "restaurante"], category: "restaurant", confidence: 0.88 },
    { keywords: ["software", "saas", "cloud", "aws", "azure", "github", "jira"], category: "software", confidence: 0.95 },
    { keywords: ["train", "flight", "hotel", "sncf", "db ", "lufthansa", "ryanair", "trenitalia", "renfe"], category: "travel", confidence: 0.90 },
    { keywords: ["vodafone", "telekom", "orange", "o2", "telefonica", "tim "], category: "telecom", confidence: 0.94 },
    { keywords: ["post", "dhl", "ups", "fedex", "la poste", "correos", "poste italiane"], category: "postage", confidence: 0.91 },
    { keywords: ["consult", "beratung", "conseil", "asesor", "consulenz"], category: "consulting", confidence: 0.85 },
    { keywords: ["versicherung", "assurance", "seguro", "assicuraz", "verzekering", "insurance"], category: "insurance", confidence: 0.93 },
    { keywords: ["miete", "loyer", "alquiler", "affitto", "huur", "rent"], category: "rent", confidence: 0.96 },
  ];

  for (const rule of rules) {
    if (rule.keywords.some(kw => combined.includes(kw))) {
      const account = policy.accounts[rule.category];
      if (account) {
        return {
          accountCode: account.code,
          accountName: account.name,
          confidence: rule.confidence,
          reasoning: `Matched '${rule.category}' from merchant/description keywords in ${input.market} market`,
          market: input.market,
        };
      }
    }
  }

  return {
    accountCode: policy.accounts.consulting?.code ?? "9999",
    accountName: "Unknown — needs review",
    confidence: 0.25,
    reasoning: "No keyword match. Low confidence — routing to human review.",
    market: input.market,
  };
}

// ─── Tool 2: Calculate VAT (Deterministic) ──────────────────

type VatInput = z.infer<typeof VatInput>;
type VatOutput = z.infer<typeof VatOutput>;

function calculateVat(input: VatInput): VatOutput {
  const policy = POLICIES[input.market]!;

  // Reverse charge: B2B intra-EU with valid VAT ID
  if (input.isB2B && input.counterpartyVatId) {
    return {
      grossAmount: input.amount,
      netAmount: input.amount,
      vatAmount: 0,
      vatRate: 0,
      mechanism: "reverse_charge",
      note: `Reverse charge applies. Counterparty VAT: ${input.counterpartyVatId}`,
    };
  }

  // Check for reduced rate categories
  const isReduced = policy.reducedCategories.includes(input.category);
  const rate = isReduced ? policy.reducedRate : policy.standardRate;
  const net = Math.round((input.amount / (1 + rate)) * 100) / 100;
  const vat = Math.round((input.amount - net) * 100) / 100;

  return {
    grossAmount: input.amount,
    netAmount: net,
    vatAmount: vat,
    vatRate: rate,
    mechanism: isReduced ? "reduced" : "standard",
  };
}

// ─── Tool 3: Create Booking (Deterministic) ─────────────────

type BookingInput = z.infer<typeof BookingInput>;
type BookingOutput = z.infer<typeof BookingOutput>;

let bookingCounter = 0;

function createBooking(input: BookingInput): BookingOutput {
  const policy = POLICIES[input.market]!;
  bookingCounter++;
  const id = `BK-${String(bookingCounter).padStart(4, "0")}`;

  const entries: BookingOutput["entries"] = [
    {
      account: input.expenseAccount,
      accountName: Object.values(policy.accounts).find(a => a.code === input.expenseAccount)?.name ?? "Expense",
      debit: input.netAmount,
      credit: 0,
    },
    {
      account: input.bankAccount,
      accountName: "Bank",
      debit: 0,
      credit: input.netAmount + input.vatAmount,
    },
  ];

  if (input.vatAmount > 0) {
    entries.splice(1, 0, {
      account: input.vatAccount || policy.vatAccount,
      accountName: policy.vatAccountName,
      debit: input.vatAmount,
      credit: 0,
    });
  }

  const totalDebit = entries.reduce((s, e) => s + e.debit, 0);
  const totalCredit = entries.reduce((s, e) => s + e.credit, 0);

  return {
    id,
    date: input.date,
    description: input.description,
    entries,
    balanced: Math.abs(totalDebit - totalCredit) < 0.01,
    grossAmount: input.netAmount + input.vatAmount,
  };
}

// ─── MCP Tool Registry ──────────────────────────────────────

interface McpToolDefinition {
  name: string;
  description: string;
  inputSchema: z.ZodType;
  handler: (input: unknown) => unknown;
}

const TOOLS: McpToolDefinition[] = [
  {
    name: "categorize_transaction",
    description: "Categorize a bank transaction to the appropriate chart-of-accounts code. AI-powered with confidence scoring.",
    inputSchema: CategorizeInput,
    handler: (input) => categorizeTransaction(CategorizeInput.parse(input)),
  },
  {
    name: "calculate_vat",
    description: "Calculate VAT for a transaction. Deterministic rule engine — handles standard, reduced, reverse charge, and exempt.",
    inputSchema: VatInput,
    handler: (input) => calculateVat(VatInput.parse(input)),
  },
  {
    name: "create_booking",
    description: "Create a double-entry bookkeeping record (Buchungssatz). Deterministic — no AI involved.",
    inputSchema: BookingInput,
    handler: (input) => createBooking(BookingInput.parse(input)),
  },
];

// ─── Simulated MCP Request Handler ──────────────────────────

interface McpRequest {
  tool: string;
  input: unknown;
}

interface McpResponse {
  tool: string;
  success: boolean;
  result?: unknown;
  error?: string;
  durationMs: number;
}

function handleToolCall(request: McpRequest): McpResponse {
  const start = performance.now();
  const tool = TOOLS.find(t => t.name === request.tool);

  if (!tool) {
    return {
      tool: request.tool,
      success: false,
      error: `Unknown tool: ${request.tool}`,
      durationMs: performance.now() - start,
    };
  }

  try {
    const result = tool.handler(request.input);
    return {
      tool: request.tool,
      success: true,
      result,
      durationMs: performance.now() - start,
    };
  } catch (err) {
    return {
      tool: request.tool,
      success: false,
      error: String(err),
      durationMs: performance.now() - start,
    };
  }
}

// ─── End-to-End Workflow Demo ────────────────────────────────

interface WorkflowTrace {
  steps: McpResponse[];
  totalDurationMs: number;
  outcome: "auto_booked" | "needs_review" | "rejected";
}

function processTransactionE2E(tx: {
  merchant: string;
  amount: number;
  description: string;
  market: string;
  date: string;
  isB2B?: boolean;
  counterpartyVatId?: string;
}): WorkflowTrace {
  const steps: McpResponse[] = [];
  const start = performance.now();

  // Step 1: Categorize
  const catResponse = handleToolCall({
    tool: "categorize_transaction",
    input: { merchant: tx.merchant, amount: tx.amount, description: tx.description, market: tx.market },
  });
  steps.push(catResponse);

  if (!catResponse.success) {
    return { steps, totalDurationMs: performance.now() - start, outcome: "rejected" };
  }

  const category = catResponse.result as CategorizeOutput;

  // Confidence routing
  if (category.confidence < 0.5) {
    return { steps, totalDurationMs: performance.now() - start, outcome: "rejected" };
  }
  if (category.confidence < 0.85) {
    return { steps, totalDurationMs: performance.now() - start, outcome: "needs_review" };
  }

  // Step 2: Calculate VAT
  const vatResponse = handleToolCall({
    tool: "calculate_vat",
    input: {
      amount: tx.amount,
      market: tx.market,
      category: Object.entries(POLICIES[tx.market]!.accounts)
        .find(([, v]) => v.code === category.accountCode)?.[0] ?? "consulting",
      isB2B: tx.isB2B ?? false,
      counterpartyVatId: tx.counterpartyVatId,
    },
  });
  steps.push(vatResponse);

  if (!vatResponse.success) {
    return { steps, totalDurationMs: performance.now() - start, outcome: "rejected" };
  }

  const vat = vatResponse.result as VatOutput;

  // Step 3: Create booking
  const bookingResponse = handleToolCall({
    tool: "create_booking",
    input: {
      date: tx.date,
      description: `${tx.merchant} — ${tx.description}`,
      expenseAccount: category.accountCode,
      netAmount: vat.netAmount,
      vatAmount: vat.vatAmount,
      market: tx.market,
    },
  });
  steps.push(bookingResponse);

  return {
    steps,
    totalDurationMs: performance.now() - start,
    outcome: bookingResponse.success ? "auto_booked" : "rejected",
  };
}

// ─── Demo ────────────────────────────────────────────────────

console.log("=== MCP Accounting Skills Server — Demo ===\n");

// Show available tools
console.log("Registered tools:");
for (const tool of TOOLS) {
  console.log(`  ${tool.name}: ${tool.description}`);
}
console.log();

// Run end-to-end transactions across multiple markets
const transactions = [
  { merchant: "Büro Discount GmbH", amount: 119.0, description: "Office supplies", market: "DE", date: "2026-04-10" },
  { merchant: "SNCF", amount: 120.0, description: "Train ticket Paris-Lyon", market: "FR", date: "2026-04-10" },
  { merchant: "Telefonica", amount: 45.0, description: "Mobile plan", market: "ES", date: "2026-04-10" },
  { merchant: "Consulenza Rossi Srl", amount: 2400.0, description: "Consulenze Q1", market: "IT", date: "2026-04-10", isB2B: true, counterpartyVatId: "IT12345678901" },
  { merchant: "Unknown Corp", amount: 999.0, description: "Misc payment", market: "NL", date: "2026-04-10" },
];

for (const tx of transactions) {
  console.log(`--- ${tx.merchant} (${tx.market}, €${tx.amount}) ---`);
  const result = processTransactionE2E(tx);
  console.log(`  Outcome: ${result.outcome}`);
  console.log(`  Steps: ${result.steps.length}`);
  console.log(`  Duration: ${result.totalDurationMs.toFixed(1)}ms`);

  for (const step of result.steps) {
    if (step.success) {
      const r = step.result as Record<string, unknown>;
      if (step.tool === "categorize_transaction") {
        console.log(`  → ${step.tool}: ${r.accountCode} ${r.accountName} (conf: ${r.confidence})`);
      } else if (step.tool === "calculate_vat") {
        console.log(`  → ${step.tool}: ${r.mechanism} @ ${((r.vatRate as number) * 100).toFixed(0)}% — €${r.netAmount} net + €${r.vatAmount} VAT`);
      } else if (step.tool === "create_booking") {
        const entries = r.entries as Array<{ account: string; accountName: string; debit: number; credit: number }>;
        console.log(`  → ${step.tool}: ${r.id} (balanced: ${r.balanced})`);
        for (const e of entries) {
          const side = e.debit > 0 ? `debit €${e.debit}` : `credit €${e.credit}`;
          console.log(`      ${e.account} ${e.accountName}: ${side}`);
        }
      }
    } else {
      console.log(`  ✕ ${step.tool}: ${step.error}`);
    }
  }
  console.log();
}

console.log("=== MCP Server Demo Complete ===");
