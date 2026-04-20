# Payroll (Lohnsteueranmeldung) and ZM — AI Design Patterns

Saved: 2026-04-17

Context: Finom's publicly stated roadmap (April 2026) targets Lohnsteueranmeldung (LStA) and Zusammenfassende Meldung (ZM) as next expansions beyond the core AI Accountant. These domains are structurally different from transaction categorization and require different AI system designs.

---

## 1. Why These Differ From Transaction Categorization

| Dimension | Transaction Categorization | Payroll (LStA) | Intra-EU (ZM) |
|-----------|--------------------------|----------------|---------------|
| Input ambiguity | High (merchant names messy) | Low (structured payroll data) | Medium (cross-border intent detection) |
| AI value-add | Categorizing ambiguous text | Computing conditional tax rates, detecting flags | Classifying transactions as EC-reportable |
| Failure cost | Correction click | Tax penalty + amended filing | EC Sales List error (VAT audit) |
| Cadence | Continuous (per transaction) | Monthly/quarterly (filing deadline) | Monthly/quarterly |
| Primary risk | Wrong account code | Wrong tax class, wrong period | Missing transaction or wrong reverse-charge flag |

**Key insight:** LStA has very little AI value in the core calculation — payroll tax rules are explicit. The AI value is in (1) classifying employees into the right Steuerklasse from messy onboarding data, and (2) detecting edge cases (mini-jobbers, partially year-employed, pauschal-taxed). ZM has more AI value in the transaction classification step.

---

## 2. Payroll (Lohnsteueranmeldung) AI Design

### What LStA requires

Germany's Lohnsteueranmeldung is a monthly or quarterly declaration of:
- Total gross wages paid
- Income tax withheld (Lohnsteuer) by Steuerklasse
- Solidarity surcharge (Solidaritätszuschlag) — partially phased out
- Church tax (Kirchensteuer) where applicable

The calculation is fully deterministic once you know: gross pay, Steuerklasse (I–VI), number of children (Kinderfreibetrag), age, employer share / employee share split.

### Where AI helps

**Stage 1 — Employee data extraction and classification (AI)**
- Onboarding documents are unstructured: scan of ID + Lohnsteuerkarte, self-declared Steuerklasse
- AI extracts: name, tax ID (Steuer-ID), Steuerklasse, Kinderfreibetrag, religious denomination
- Risk: Steuerklasse III vs I misclassification = significant withheld-tax error

**Stage 2 — Payroll computation (Deterministic)**
- Given the classified employee record, apply the Bundesministerium für Finanzen (BMF) tables
- These tables are released annually and must be encoded as code, not prompt
- Never let an LLM calculate a wage tax amount — the formula is public and deterministic

**Stage 3 — Edge case detection (AI)**
- Mini-jobber threshold detection: grosses up to €538/month → pauschal 2% tax
- Kurzarbeit (short-time work) periods: different rules for Kurzarbeitergeld
- Year-of-entry/exit proration: employee worked 7 of 12 months — correct annual amounts
- These are messy natural-language scenarios in onboarding; AI classifies them with high confidence or escalates

**Stage 4 — Filing preparation (Deterministic)**
- Aggregate by Steuerklasse, compute Kirchensteuer by denomination, apply solidarity surcharge rules
- Generate ELSTER-compatible XML for electronic filing
- This is 100% deterministic policy → code only

### Pipeline shape

```
Onboarding doc (PDF/image)
  → Stage 1: Employee extraction (AI) — Steuerklasse, Steuer-ID, flags
  → Stage 2: Edge case classification (AI) — mini-job, Kurzarbeit, partial year
  → Stage 3: Computation gate (deterministic) — verify extracted fields are complete
  → Stage 4: Payroll calculation (deterministic) — BMF tables, exact math
  → Stage 5: Aggregation + filing (deterministic) — ELSTER XML
```

### Confidence routing for payroll

Standard transaction routing applies: extracted fields below threshold → human review before calculation.

**Payroll-specific invariant:** Any Steuerklasse field with confidence < 0.90 must go to human review. There is no proposal mode for Steuerklasse — the financial consequence of a wrong class is too high (over/under-withholding, employee dispute).

### Multi-employer edge case

GmbH employees who also hold a Einzelunternehmen (freelance business) may have split Steuerklassen across employers. The AI system must detect multi-employer situations and flag them as `requires_manual_review` — not attempt to resolve automatically.

---

## 3. Zusammenfassende Meldung (ZM) — Intra-EU VAT Reporting

### What ZM requires

The ZM (EC Sales List / Recapitulative Statement) reports all:
- Goods supplied to VAT-registered buyers in other EU member states
- Services supplied to VAT-registered buyers in other EU member states (since 2010)
- Triangular transactions

Filed monthly or quarterly to the BZSt (Bundeszentralamt für Steuern) via ELSTER or the Meldungsportal.

### Where AI helps

**Stage 1 — Transaction classification (AI)**
- Is this transaction subject to ZM reporting? Requires detecting:
  - Buyer's country (EU or non-EU)
  - Buyer's VAT ID (present → EU business)
  - Nature of supply (goods vs services)
  - Whether this is a triangular supply
- Input is messy: bank transaction data, linked invoices, customer master data
- AI adds value here because the natural-language signals (invoice description, customer name, address) are ambiguous

**Stage 2 — Counterparty VAT ID validation (Deterministic + external)**
- Validate the buyer's VAT ID against VIES (EU-wide VAT information exchange system)
- A transaction with an invalid or unverifiable VAT ID cannot be reported as reverse-charge intra-EU
- This must be a deterministic check against VIES, not an LLM guess

**Stage 3 — Amount aggregation (Deterministic)**
- Sum by counterparty VAT ID and member state
- Apply transaction-type flags: N (normal), D (triangular/Dreiecksgeschäft), S (services)

**Stage 4 — ZM XML generation (Deterministic)**
- ELSTER-compatible format, monthly or quarterly
- Quarterly is allowed only if total amount < €50,000/quarter (annual threshold check)

### Pipeline shape

```
Invoice / transaction batch
  → Stage 1: EC classification (AI) — is this intra-EU? goods or services? triangular?
  → Stage 2: VAT ID validation (deterministic + VIES call)
  → Stage 3: Amount aggregation by counterparty (deterministic)
  → Stage 4: ZM XML generation + ELSTER filing (deterministic)
```

### Confidence routing for ZM

**ZM-specific invariant:** Any transaction flagged as "possibly EC-reportable" with confidence < 0.80 must go to human review before inclusion in ZM. Under-reporting is a VAT audit trigger; over-reporting creates a corrected ZM.

The correct default is: when in doubt, route to review — never silently include or silently exclude.

### Triangular transaction (Dreiecksgeschäft) edge case

A supplier in DE sells goods to a buyer in FR, but the goods ship directly from a third supplier in PL. This creates a triangular supply: DE reports with flag D, FR buyer self-assesses, PL supplier is out of scope. AI must detect this three-party pattern from linked invoice data — a genuinely hard classification problem that benefits from LLM reasoning over unstructured invoice text.

---

## 4. Shared Architecture Principles: LStA and ZM

Both domains share the same architectural principle as the core AI Accountant:

> **Policy (rules) → deterministic code. Classification (judgment from messy input) → AI.**

The stages differ, but the AI/deterministic boundary is always in the same place:

| Layer | AI or deterministic | Why |
|-------|---------------------|-----|
| Raw document → structured fields | AI | Unstructured input, genuine ambiguity |
| Edge case / exception detection | AI | Natural language signals, context needed |
| Policy-bound calculation | Deterministic | Failure = tax error, cannot be probabilistic |
| Filing format generation | Deterministic | Schema is fixed, non-negotiable |
| External validation (VIES, ELSTER ping) | Deterministic (external call) | Ground truth, not a model opinion |

---

## 5. Multi-Domain Eval Implications

When extending the eval harness to cover LStA and ZM, severity weights shift:

| Case type | Severity | Why |
|-----------|----------|-----|
| Wrong Steuerklasse applied | Critical | Under/over-withholding, employee dispute |
| Mini-jobber detected as regular employee | Critical | Wrong tax regime applied from day one |
| ZM: intra-EU transaction missed (not included) | Critical | VAT audit risk |
| ZM: wrong counterparty VAT ID | High | ZM amendment required |
| ZM: quarterly vs monthly threshold error | High | Wrong filing cadence = late-filing notice |
| LStA: wrong Kinderfreibetrag count | Medium | Partial under-withholding |
| LStA: solidarity surcharge miscalculated | Low | Small amounts, easily amended |

The eval harness for these domains should add a `domain` field to test cases and track critical error rates by domain separately — LStA has different criticality calibration than ZM.

---

## 6. Interview Hook

If asked about Finom's roadmap:

> "The payroll and ZM expansion is architecturally interesting because the AI/deterministic boundary moves compared to transaction categorization. In categorization, the AI does the core judgment. In payroll, the calculation is almost entirely deterministic — the AI's job is to extract clean inputs from unstructured onboarding data and detect edge cases. In ZM, the AI classifies whether a transaction is EC-reportable, which requires reading invoice text, but the VAT ID validation and amount aggregation are pure external calls. Same pattern, different split."

Sharper version:

> "Payroll adds AI only at the input-extraction and edge-case-detection stage. Everything after Steuerklasse is BMF tables — deterministic code. ZM adds AI at the transaction classification stage but then hands off to VIES validation and strict aggregation rules. The pipeline shape is the same; the stage where AI adds value just moves."

---

## 7. What This Means for System Design

If asked to design an LStA or ZM system in a live round:

1. **Start with the failure cost hierarchy** — payroll tax errors → employee disputes; ZM errors → audit triggers
2. **Identify the AI/deterministic split immediately** — which inputs are ambiguous, which outputs are regulated
3. **Design the deterministic core first** — BMF tables as code, ELSTER schema as code
4. **Wrap AI around the messy input layer** — onboarding docs, invoice text, counterparty detection
5. **Add a high-confidence gate before any deterministic calculation** — never pass a low-confidence Steuerklasse to the payroll engine
6. **Treat external validation as a deterministic stage** — VIES is ground truth, not an opinion
7. **Design for amendment workflows** — ZM and LStA can both be amended; the system must support generating an amended filing from a correction event

The same 7-step skeleton applies: Scope → AI boundary → Pipeline → Confidence routing → Observability → Scale → Failures.
