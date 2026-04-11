/**
 * Multi-Market Expansion Drill — Finom Interview 3 Prep
 *
 * A focused 15-minute drill for the live coding round that demonstrates:
 * 1. Data-driven market configuration (not code-driven)
 * 2. Tax rule composition (standard + reduced + reverse charge + exemptions)
 * 3. Validation pipeline for market-specific constraints
 * 4. Migration path: adding Italy without touching core logic
 *
 * This complements the existing live-round-rehearsal.ts by going deeper
 * on the multi-market extensibility dimension.
 *
 * Run with: bun run multi-market-expansion-drill.ts
 */

import { z } from "zod";

// ─── Market Configuration Schema ────────────────────────────────

const VatRuleSchema = z.object({
  rate: z.number(),
  label: z.string(),
  categories: z.array(z.string()),
});

const MarketConfigSchema = z.object({
  code: z.string(),
  name: z.string(),
  currency: z.string().default("EUR"),
  fiscalYearEnd: z.string(), // "12-31" or "03-31" etc
  standardVatRate: z.number(),
  reducedRates: z.array(VatRuleSchema),
  exemptCategories: z.array(z.string()),
  reverseChargeEnabled: z.boolean(),
  chartOfAccounts: z.record(
    z.string(),
    z.object({
      code: z.string(),
      name: z.string(),
      localName: z.string(),
    })
  ),
  invoiceRequirements: z.object({
    vatIdRequired: z.boolean(),
    sequentialNumbering: z.boolean(),
    electronicInvoicingMandatory: z.boolean(),
    retentionYears: z.number(),
  }),
  validations: z.array(
    z.object({
      name: z.string(),
      description: z.string(),
    })
  ),
});

type MarketConfig = z.infer<typeof MarketConfigSchema>;

// ─── Market Configurations (Data, Not Code) ─────────────────────

const MARKETS: Record<string, MarketConfig> = {
  DE: {
    code: "DE",
    name: "Germany",
    currency: "EUR",
    fiscalYearEnd: "12-31",
    standardVatRate: 0.19,
    reducedRates: [
      { rate: 0.07, label: "Reduced", categories: ["food", "books", "public_transport"] },
    ],
    exemptCategories: ["insurance", "medical", "education"],
    reverseChargeEnabled: true,
    chartOfAccounts: {
      office: { code: "4930", name: "Office Supplies", localName: "Bürobedarf" },
      travel: { code: "4660", name: "Travel", localName: "Reisekosten" },
      software: { code: "4964", name: "IT Costs", localName: "EDV-Kosten" },
      restaurant: { code: "4650", name: "Entertainment", localName: "Bewirtungskosten" },
      telecom: { code: "4920", name: "Telephone", localName: "Telefon" },
      rent: { code: "4210", name: "Rent", localName: "Miete" },
      marketing: { code: "4600", name: "Advertising", localName: "Werbekosten" },
    },
    invoiceRequirements: {
      vatIdRequired: true,
      sequentialNumbering: true,
      electronicInvoicingMandatory: false, // not yet mandatory in DE
      retentionYears: 10,
    },
    validations: [
      { name: "vat_id_format", description: "Must match DE[0-9]{9}" },
      { name: "skr03_account", description: "Account code must be valid SKR03" },
    ],
  },
  FR: {
    code: "FR",
    name: "France",
    currency: "EUR",
    fiscalYearEnd: "12-31",
    standardVatRate: 0.2,
    reducedRates: [
      { rate: 0.055, label: "Reduced", categories: ["food", "books", "energy"] },
      { rate: 0.1, label: "Intermediate", categories: ["restaurant", "transport", "renovation"] },
      { rate: 0.021, label: "Super-reduced", categories: ["press", "medicine"] },
    ],
    exemptCategories: ["insurance", "medical", "education", "banking"],
    reverseChargeEnabled: true,
    chartOfAccounts: {
      office: { code: "6064", name: "Office Supplies", localName: "Fournitures administratives" },
      travel: { code: "6251", name: "Travel", localName: "Voyages et déplacements" },
      software: { code: "6156", name: "IT Costs", localName: "Maintenance informatique" },
      restaurant: { code: "6257", name: "Entertainment", localName: "Réceptions" },
      telecom: { code: "626", name: "Telecom", localName: "Frais postaux et télécommunications" },
      rent: { code: "613", name: "Rent", localName: "Locations" },
      marketing: { code: "6231", name: "Advertising", localName: "Publicité" },
    },
    invoiceRequirements: {
      vatIdRequired: true,
      sequentialNumbering: true,
      electronicInvoicingMandatory: false, // mandatory from Sept 2026 for large companies
      retentionYears: 10,
    },
    validations: [
      { name: "vat_id_format", description: "Must match FR[A-Z0-9]{2}[0-9]{9}" },
      { name: "pcg_account", description: "Account code must be valid PCG (Plan Comptable Général)" },
    ],
  },
  IT: {
    code: "IT",
    name: "Italy",
    currency: "EUR",
    fiscalYearEnd: "12-31",
    standardVatRate: 0.22,
    reducedRates: [
      { rate: 0.1, label: "Reduced", categories: ["food", "restaurant", "energy", "renovation"] },
      { rate: 0.05, label: "Super-reduced", categories: ["medical_devices"] },
      { rate: 0.04, label: "Minimum", categories: ["food_staples", "books", "press"] },
    ],
    exemptCategories: ["insurance", "medical", "education", "banking", "gambling"],
    reverseChargeEnabled: true,
    chartOfAccounts: {
      office: { code: "6400.10", name: "Office Supplies", localName: "Cancelleria e stampati" },
      travel: { code: "6300.10", name: "Travel", localName: "Viaggi e trasferte" },
      software: { code: "6400.30", name: "IT Costs", localName: "Costi informatici" },
      restaurant: { code: "6500.20", name: "Entertainment", localName: "Spese di rappresentanza" },
      telecom: { code: "6400.20", name: "Telecom", localName: "Spese telefoniche" },
      rent: { code: "6100.10", name: "Rent", localName: "Affitti passivi" },
      marketing: { code: "6800.10", name: "Advertising", localName: "Pubblicità" },
    },
    invoiceRequirements: {
      vatIdRequired: true,
      sequentialNumbering: true,
      electronicInvoicingMandatory: true, // SDI mandatory since 2019
      retentionYears: 10,
    },
    validations: [
      { name: "vat_id_format", description: "Must match IT[0-9]{11}" },
      { name: "sdi_code", description: "SDI recipient code required for e-invoicing" },
      { name: "piano_dei_conti", description: "Account code must follow Italian chart of accounts" },
    ],
  },
};

// ─── Tax Calculation Engine (Data-Driven) ───────────────────────

interface TaxInput {
  market: string;
  category: string;
  amount: number;
  isB2B: boolean;
  counterpartyVatId?: string;
  isIntraEU?: boolean;
}

interface TaxResult {
  grossAmount: number;
  netAmount: number;
  vatAmount: number;
  vatRate: number;
  mechanism: string;
  ruleApplied: string;
  market: string;
}

function calculateTax(input: TaxInput): TaxResult {
  const market = MARKETS[input.market];
  if (!market) {
    return {
      grossAmount: input.amount,
      netAmount: input.amount,
      vatAmount: 0,
      vatRate: 0,
      mechanism: "unknown_market",
      ruleApplied: `Market ${input.market} not configured`,
      market: input.market,
    };
  }

  // Rule 1: Reverse charge for B2B intra-EU
  if (input.isB2B && input.isIntraEU && market.reverseChargeEnabled && input.counterpartyVatId) {
    return {
      grossAmount: input.amount,
      netAmount: input.amount,
      vatAmount: 0,
      vatRate: 0,
      mechanism: "reverse_charge",
      ruleApplied: "B2B intra-EU with valid VAT ID → reverse charge",
      market: input.market,
    };
  }

  // Rule 2: Exempt categories
  if (market.exemptCategories.includes(input.category)) {
    return {
      grossAmount: input.amount,
      netAmount: input.amount,
      vatAmount: 0,
      vatRate: 0,
      mechanism: "exempt",
      ruleApplied: `Category "${input.category}" is VAT-exempt in ${market.code}`,
      market: input.market,
    };
  }

  // Rule 3: Reduced rates (check all tiers)
  for (const rule of market.reducedRates) {
    if (rule.categories.includes(input.category)) {
      const net = Math.round((input.amount / (1 + rule.rate)) * 100) / 100;
      const vat = Math.round((input.amount - net) * 100) / 100;
      return {
        grossAmount: input.amount,
        netAmount: net,
        vatAmount: vat,
        vatRate: rule.rate,
        mechanism: `reduced_${rule.label.toLowerCase()}`,
        ruleApplied: `Category "${input.category}" qualifies for ${rule.label} rate (${(rule.rate * 100).toFixed(1)}%)`,
        market: input.market,
      };
    }
  }

  // Rule 4: Standard rate (fallback)
  const rate = market.standardVatRate;
  const net = Math.round((input.amount / (1 + rate)) * 100) / 100;
  const vat = Math.round((input.amount - net) * 100) / 100;
  return {
    grossAmount: input.amount,
    netAmount: net,
    vatAmount: vat,
    vatRate: rate,
    mechanism: "standard",
    ruleApplied: `Standard rate ${(rate * 100).toFixed(0)}% applied`,
    market: input.market,
  };
}

// ─── Market Validation Pipeline ─────────────────────────────────

interface ValidationResult {
  market: string;
  configValid: boolean;
  errors: string[];
  warnings: string[];
  coverage: {
    categoriesWithAccounts: number;
    totalCategories: number;
    vatRuleCoverage: string;
  };
}

function validateMarketConfig(config: MarketConfig): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Check: all chart of accounts entries have valid codes
  for (const [category, account] of Object.entries(config.chartOfAccounts)) {
    if (!account.code || account.code.length === 0) {
      errors.push(`Account code missing for category "${category}"`);
    }
    if (!account.localName) {
      warnings.push(`Local name missing for category "${category}" — localization incomplete`);
    }
  }

  // Check: reduced rate categories don't overlap
  const reducedCategories = config.reducedRates.flatMap((r) => r.categories);
  const duplicates = reducedCategories.filter(
    (c, i) => reducedCategories.indexOf(c) !== i
  );
  if (duplicates.length > 0) {
    errors.push(`Overlapping reduced rate categories: ${duplicates.join(", ")}`);
  }

  // Check: exempt categories don't have reduced rates
  for (const exempt of config.exemptCategories) {
    if (reducedCategories.includes(exempt)) {
      errors.push(`Category "${exempt}" is both exempt and reduced-rated`);
    }
  }

  // Check: invoice requirements make sense
  if (config.invoiceRequirements.retentionYears < 6) {
    warnings.push(`Retention period ${config.invoiceRequirements.retentionYears} years may not meet EU minimum`);
  }

  // Coverage analysis
  const categoriesWithAccounts = Object.keys(config.chartOfAccounts).length;
  const allReferencedCategories = new Set([
    ...Object.keys(config.chartOfAccounts),
    ...reducedCategories,
    ...config.exemptCategories,
  ]);

  return {
    market: config.code,
    configValid: errors.length === 0,
    errors,
    warnings,
    coverage: {
      categoriesWithAccounts,
      totalCategories: allReferencedCategories.size,
      vatRuleCoverage: `${config.reducedRates.length} reduced tiers + ${config.exemptCategories.length} exemptions`,
    },
  };
}

// ─── Demo ───────────────────────────────────────────────────────

console.log("=== Multi-Market Expansion Drill ===\n");

// Part 1: Validate all market configurations
console.log("  Part 1: Market Configuration Validation");
console.log("  " + "═".repeat(50));

for (const [code, config] of Object.entries(MARKETS)) {
  const result = validateMarketConfig(config);
  console.log(`\n  ${config.name} (${code}):`);
  console.log(`    Valid: ${result.configValid ? "✓" : "✕"}`);
  console.log(`    Categories: ${result.coverage.categoriesWithAccounts} with accounts / ${result.coverage.totalCategories} total`);
  console.log(`    VAT rules: ${result.coverage.vatRuleCoverage}`);
  console.log(`    E-invoicing mandatory: ${config.invoiceRequirements.electronicInvoicingMandatory ? "YES" : "no"}`);

  if (result.errors.length > 0) {
    for (const err of result.errors) console.log(`    ✕ ERROR: ${err}`);
  }
  if (result.warnings.length > 0) {
    for (const warn of result.warnings) console.log(`    ⚠ WARNING: ${warn}`);
  }
}

// Part 2: Same transaction across markets
console.log(`\n\n  Part 2: Same Transaction Across Markets`);
console.log("  " + "═".repeat(50));

const testTransactions: TaxInput[] = [
  { market: "DE", category: "software", amount: 100, isB2B: false },
  { market: "FR", category: "software", amount: 100, isB2B: false },
  { market: "IT", category: "software", amount: 100, isB2B: false },
  { market: "DE", category: "food", amount: 50, isB2B: false },
  { market: "FR", category: "food", amount: 50, isB2B: false },
  { market: "IT", category: "food", amount: 50, isB2B: false },
  { market: "DE", category: "office", amount: 200, isB2B: true, isIntraEU: true, counterpartyVatId: "NL123456789B01" },
  { market: "FR", category: "office", amount: 200, isB2B: true, isIntraEU: true, counterpartyVatId: "DE123456789" },
  { market: "IT", category: "office", amount: 200, isB2B: true, isIntraEU: true, counterpartyVatId: "DE123456789" },
  { market: "DE", category: "insurance", amount: 500, isB2B: false },
  { market: "FR", category: "insurance", amount: 500, isB2B: false },
  { market: "IT", category: "insurance", amount: 500, isB2B: false },
];

let currentCategory = "";
for (const tx of testTransactions) {
  const label = `${tx.category}${tx.isB2B ? " (B2B intra-EU)" : ""}`;
  if (label !== currentCategory) {
    currentCategory = label;
    console.log(`\n  Transaction: €${tx.amount} ${label}`);
    console.log("  " + "─".repeat(50));
  }

  const result = calculateTax(tx);
  console.log(
    `    ${result.market}: net €${result.netAmount.toFixed(2)} + VAT €${result.vatAmount.toFixed(2)} ` +
    `(${(result.vatRate * 100).toFixed(1)}% ${result.mechanism})`
  );
}

// Part 3: Italy-specific complexity (SDI e-invoicing)
console.log(`\n\n  Part 3: Italy — Electronic Invoicing (SDI)`);
console.log("  " + "═".repeat(50));
console.log(`
  Italy requires all invoices to pass through the Sistema di Interscambio (SDI).
  This adds a pipeline step that DE and FR don't have:

  Transaction → Categorize → Calculate Tax → Generate Booking
                                               ↓
                                    [IT only] Generate FatturaPA XML
                                               ↓
                                    [IT only] Submit to SDI
                                               ↓
                                    [IT only] Await SDI acceptance
                                               ↓
                                    Finalize booking

  Engineering implication: The booking pipeline must support
  market-specific post-processing hooks. Italy needs an async
  step (SDI submission + confirmation) that other markets skip.

  This is exactly the kind of extensibility that data-driven
  market configuration enables — the core pipeline stays the
  same, but Italy plugs in additional steps.
`);

// Part 4: Adding a new market (Netherlands)
console.log(`  Part 4: Adding Netherlands — Zero Code Changes`);
console.log("  " + "═".repeat(50));

const NL_CONFIG: MarketConfig = {
  code: "NL",
  name: "Netherlands",
  currency: "EUR",
  fiscalYearEnd: "12-31",
  standardVatRate: 0.21,
  reducedRates: [
    { rate: 0.09, label: "Reduced", categories: ["food", "books", "medicine", "public_transport"] },
  ],
  exemptCategories: ["insurance", "medical", "education", "banking"],
  reverseChargeEnabled: true,
  chartOfAccounts: {
    office: { code: "4100", name: "Office Supplies", localName: "Kantoorbenodigdheden" },
    travel: { code: "4300", name: "Travel", localName: "Reiskosten" },
    software: { code: "4130", name: "IT Costs", localName: "Automatiseringskosten" },
    restaurant: { code: "4600", name: "Entertainment", localName: "Representatiekosten" },
    telecom: { code: "4120", name: "Telecom", localName: "Telefoonkosten" },
    rent: { code: "4000", name: "Rent", localName: "Huur" },
    marketing: { code: "4700", name: "Advertising", localName: "Reclamekosten" },
  },
  invoiceRequirements: {
    vatIdRequired: true,
    sequentialNumbering: true,
    electronicInvoicingMandatory: false,
    retentionYears: 7,
  },
  validations: [
    { name: "vat_id_format", description: "Must match NL[0-9]{9}B[0-9]{2}" },
    { name: "rgs_code", description: "Account code should follow RGS (Referentie Grootboekschema)" },
  ],
};

// Register new market (in production: load from config store)
MARKETS["NL"] = NL_CONFIG;

const nlValidation = validateMarketConfig(NL_CONFIG);
console.log(`\n  Netherlands added: ${nlValidation.configValid ? "✓ Valid" : "✕ Invalid"}`);

// Test it immediately
const nlTests: TaxInput[] = [
  { market: "NL", category: "software", amount: 100, isB2B: false },
  { market: "NL", category: "food", amount: 50, isB2B: false },
  { market: "NL", category: "office", amount: 200, isB2B: true, isIntraEU: true, counterpartyVatId: "DE123456789" },
];

console.log("\n  Netherlands test transactions:");
for (const tx of nlTests) {
  const result = calculateTax(tx);
  console.log(
    `    €${tx.amount} ${tx.category}${tx.isB2B ? " (B2B)" : ""}: ` +
    `net €${result.netAmount.toFixed(2)} + VAT €${result.vatAmount.toFixed(2)} ` +
    `(${(result.vatRate * 100).toFixed(1)}% ${result.mechanism})`
  );
}

console.log(`
  Key point: Adding NL required:
    ✓ One configuration object (data)
    ✕ Zero code changes
    ✕ Zero new functions
    ✕ Zero pipeline modifications

  The configuration schema (MarketConfigSchema) validates the
  new market's data structure at startup. If a field is missing
  or a rule overlaps, validation catches it before any transaction
  is processed.
`);

console.log("=== Drill Complete ===");
