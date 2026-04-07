# German SME Accounting — Domain Primer for Finom Interview

Saved: 2026-04-07

## Purpose

Finom's AI Accountant launched in Germany first (largest EU SME market). Knowing the basic domain vocabulary and pain points shows homework without overclaiming expertise.

**Do not pretend to be a tax expert.** Use this to sound informed when Ivo mentions specific German accounting concepts.

---

## Key German Tax Forms Finom Automates

| Abbreviation | Full name | What it is |
|------|-----------|------------|
| **UStVA** | Umsatzsteuervoranmeldung | VAT advance return — filed monthly or quarterly |
| **UStE** | Umsatzsteuererklärung | Annual VAT return |
| **EÜR** | Einnahmenüberschussrechnung | Simplified profit & loss statement (cash-basis) |
| **GeSt** | Gewerbesteuererklärung | Trade tax return |
| **ESt** | Einkommensteuererklärung | Income tax return |
| **ZM** | Zusammenfassende Meldung | EU recapitulative statement (cross-border VAT) |

**Why this matters:** Finom's product page explicitly lists these as automated outputs. When Ivo talks about "tax preparation," these are the actual artifacts.

---

## Who Uses Finom's Accounting

### Freelancers (Freiberufler)
- Always allowed to use EÜR (simplified accounting), regardless of income
- Must file electronically via ELSTER since 2018
- Subject to UStVA if not registered as Kleinunternehmer (small entrepreneur, < €22,000 revenue)
- Main pain: keeping track of receipts, categorizing expenses, filing quarterly VAT returns on time

### Small businesses (Gewerbetreibende)
- Can use EÜR if annual revenue < €600,000 AND annual profit < €60,000
- Must switch to full bookkeeping (Bilanz) if either threshold is exceeded
- Subject to Gewerbesteuer (trade tax) on top of income tax
- Main pain: more complex categorization, trade tax calculations, multiple filing deadlines

### The SME pain point Finom targets
- EU SMEs spend ~5% of annual turnover on accounting and compliance
- Manual data entry: receipts → categories → tax forms
- Deadline tracking: UStVA monthly/quarterly, EÜR annually, various other deadlines
- Error risk: miscategorization leads to tax corrections, penalties, or missed deductions

---

## What AI Accounting Automates (mapped to Finom)

| Manual task | AI automation | Quality bar |
|-------------|--------------|-------------|
| Sort receipts and invoices | Document intake + classification agent | Must correctly identify invoice vs receipt vs statement |
| Enter amounts and details | Extraction agent | Must correctly read amounts, dates, tax rates from diverse document formats |
| Assign accounting category | Categorization agent | Must correctly map to German accounting categories (SKR 03/04) |
| Match invoices to bank transactions | Reconciliation agent | ~99% accuracy claimed — must handle partial matches, timing differences |
| Calculate VAT (Vorsteuer) | Tax preparation agent | Must correctly apply 19% standard, 7% reduced, or 0% rates |
| Prepare UStVA, EÜR, etc. | Report generation | Must produce forms that are correct for filing with Finanzamt |
| File with tax authority | Filing agent (via ELSTER) | Must handle electronic signatures and submission protocols |

---

## Domain Vocabulary To Use Naturally

- **Vorsteuerabzug**: Input VAT deduction — the tax you paid on business expenses that gets deducted from VAT you owe
- **SKR 03 / SKR 04**: Standard chart of accounts used in German bookkeeping (Standardkontenrahmen)
- **Finanzamt**: Local tax office — where returns are filed
- **ELSTER**: Electronic tax filing system — mandatory since 2018
- **Kleinunternehmer**: Small entrepreneur exemption (< €22K revenue, exempt from VAT filing)
- **Betriebsausgabe**: Business expense — the core categorization output
- **Buchungssatz**: Booking entry — the fundamental accounting record

---

## How To Reference This In The Interview

**If Ivo mentions German accounting or tax workflows:**
> "I understand the AI Accountant handles the full chain from document recognition through categorization to UStVA and EÜR preparation. The hard part is getting the categorization and VAT treatment right across diverse document types — that's where the multi-agent architecture and confidence thresholds really matter."

**If asked about cross-country expansion challenges:**
> "Each EU country has different tax forms, categorization standards, and filing protocols. The central AI team should own the reusable parts — document understanding, extraction, reconciliation — while country-specific tax logic stays as configuration that domain experts can maintain."

**Do NOT:**
- Pretend to know German tax law in depth
- Name specific SKR account numbers unless asked
- Offer opinions on tax optimization strategies
- Overclaim understanding of ELSTER integration specifics

Sources:
- [German Bookkeeping Guide - TaxRep](https://taxrep.us/tax_guide/german-bookkeeping-and-accounting-guide/)
- [EÜR explained - Firma.de](https://www.firma.de/en/accountancy/eur-everything-you-need-to-know-about-the-einnahmenuberschussrechnung/)
- [German VAT guide for freelancers - Qonto](https://qonto.com/en/blog/freelancers/accounting/your-guide-to-german-vat-umsatzsteuer-as-a-freelancer)
