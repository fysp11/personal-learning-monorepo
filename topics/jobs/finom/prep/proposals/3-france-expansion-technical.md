# France Expansion — Technical Specifics for Interview 3

Saved: 2026-04-11 (Iteration 6)

## Purpose

France is Finom's next market after Germany. This document covers the technical delta between a DE accounting pipeline and a FR one — where the patterns transfer, where new work is required, and what surprises are coming.

Use when asked: "How would you extend the Germany workflow to France?" or any multi-market question.

---

## The Core Claim to Make

> "The workflow shape is identical. The market policy is entirely different. And France has one time-sensitive complexity that Germany doesn't have yet: mandatory B2B e-invoicing from September 2026."

---

## VAT Structure: Germany vs France

| Dimension | Germany | France |
|-----------|---------|--------|
| Standard rate | 19% | 20% |
| Reduced rate(s) | 7% | 5.5%, 10% |
| Super-reduced rate | — | 2.1% (books, press, some drugs) |
| Zero rate | — | 0% (exports) |
| Filing form | UStVA | CA3 (Déclaration de TVA) |
| Filing system | ELSTER | DGFiP's impots.gouv.fr |
| Filing frequency | Monthly or quarterly | Monthly (most businesses) |
| Annual return | UStE | CA12 |

**The 4-rate problem:** Germany's 2 rates mean category → rate is usually unambiguous. France's 4 rates create more edge cases:

| Category | Rate | Example |
|----------|------|---------|
| Standard | 20% | Most services, SaaS, consulting |
| 10% | Services de rénovation, restaurants (sit-in) | Catering, building work |
| 5.5% | Essential goods | Books, food for takeaway, some cultural events |
| 2.1% | Super-reduced | Press subscriptions, some medicines |

**AI implication:** The categorization model needs to return the VAT rate alongside the account code, and the rate options must come from the market policy config — not the model's training weights. A category that's 7% in Germany might be 10% or 5.5% in France. The deterministic VAT layer reads from policy config, which is per-market.

---

## Chart of Accounts: SKR03 vs PCG

**Germany — SKR03 (Standardkontenrahmen 03):**
- 4-digit account codes
- Account 4920 = EDV-Software
- Account 4210 = Miete und Pacht
- Organized by business type (freelancers, SMEs)

**France — PCG (Plan Comptable Général):**
- Also numeric but different structure
- Account 6060 = Achats logiciels (software purchases)
- Account 6130 = Locations immobilières (property rental)
- Account 6230 = Publicité (advertising)
- Class 7 = Revenue accounts (711x–758x)
- Published by ANC (Autorité des normes comptables), updated periodically

**What this means for the AI layer:**
- The `chartOfAccounts` key in `MarketPolicy` just needs to be swapped — same interface, different data
- No model retraining needed if the input features are merchant-independent (which they should be by design)
- The mapping table (category → PCG code) is a new config artifact, not a code change
- However: test data needs French merchant examples. An initial cold-start problem exists for FR categorization.

**PCG vs SKR03 cold-start:**
- Germany has 200K+ accounts worth of training data from the AI Accountant GA
- France launch will start with zero real-user transactions
- Mitigation: bootstrap with synthetic French merchant data, use higher uncertainty thresholds, start 100% proposal mode → calibrate → widen

---

## CA3 Filing vs UStVA

**German UStVA (Umsatzsteuervoranmeldung):**
- Electronic via ELSTER API
- Monthly or quarterly depending on previous year's VAT liability
- Key line items: Kz 81 (19% sales), Kz 86 (7% sales), Kz 63 (Vorsteuer), Kz 83 (Zahllast)
- Annual: UStE

**French CA3 (Déclaration de TVA):**
- Electronic via impots.gouv.fr (DGFiP)
- Monthly for most businesses
- Key line items: ligne 08 (sales at 20%), ligne 09 (sales at other rates), ligne 20 (input VAT), ligne 25 (net amount due)
- Annual: CA12 (for quarterly filers)
- More complex multi-line structure — 20% has several sub-lines depending on transaction type

**API integration difference:**
- ELSTER uses a German-specific XML schema with strict validation; the integration is well-documented
- DGFiP's API (EDI/EFI via TDFC) is older and uses a different authentication scheme; Chorus Pro handles B2B e-invoices (see below)
- Finom will need a separate FR filing integration — not a config swap, actual API work

---

## The September 2026 E-Invoicing Mandate

This is the most time-sensitive piece for Finom's France expansion.

**What it is:** France is mandating electronic invoicing for all B2B transactions in stages:
- **September 1, 2026**: Large enterprises must **receive** e-invoices; obligated to send starting later
- **Rolling deadline**: SMEs (likely Finom's customer base) get later mandate dates, but they must be able to **receive** e-invoices by September 2026

**The platform:** All French B2B invoices must flow through either:
- **Chorus Pro** — the state-operated platform (already used for public sector invoicing)
- Or a certified **Plateforme de Dématérialisation Partenaire (PDP)** — private certified operator

**Technical format:** Factur-X (PDF + embedded XML, based on ZUGFeRD) or UBL or CII XML

**What this means for Finom:**
- A French user's Finom account needs to be able to receive e-invoices from Chorus Pro/PDP
- Outgoing invoices from French Finom users need to be in the correct e-invoice format
- The AI Accountant's document extraction pipeline needs to handle structured XML (easier than PDF OCR) AND the Factur-X format
- Italy has had SDI since 2019 — Finom's Italian work (or at least the architecture) is relevant here

**The implication for the AI layer:**
- Factur-X/UBL XML invoices contain structured data: VAT amounts, account codes, party VAT IDs are already extracted
- This *reduces* the AI extraction problem (less need for OCR on structured invoices)
- But adds a new pipeline stage: XML parsing and validation before categorization
- The e-invoice format effectively pre-populates some fields that the AI would otherwise have to guess

**Interview talking point:**
> "France has a September 2026 deadline for B2B e-invoicing through Chorus Pro. That actually makes the AI extraction problem easier for compliant invoices — structured XML means you get amounts and VAT IDs for free. The harder part is the filing integration: CA3 via DGFiP is a different API from ELSTER, not a config change. And for the AI side, the France cold-start is the first real calibration challenge — no training data at launch, so you start at 100% proposal mode and calibrate over the first few thousand transactions."

---

## What Transfers Directly from Germany

| Component | Transfers? | Notes |
|-----------|-----------|-------|
| Pipeline shape (5 stages) | ✓ Yes | Identical |
| Confidence routing logic | ✓ Yes | Same thresholds, potentially tightened at FR launch |
| Eval harness structure | ✓ Yes | New FR test cases needed |
| MCP skill server architecture | ✓ Yes | New FR MarketPolicy config object |
| Reverse charge detection | ✓ Yes | Same EU VAT ID detection logic |
| Idempotency / circuit breaker | ✓ Yes | Infra layer, market-agnostic |
| VAT calculation function | ✓ with change | 4 rates instead of 2 — policy config update |
| Chart of accounts mapping | ✗ New | PCG != SKR03 |
| Filing integration | ✗ New | DGFiP/Chorus Pro != ELSTER |
| Calibration data | ✗ New | Cold start — no FR training data |
| E-invoicing pipeline | ✗ New | Factur-X/UBL XML parsing stage |

**Punchline:** More than 60% of the work transfers directly. The new work is concentrated in market policy config, filing API integration, and the e-invoicing pipeline addition. No retraining, no pipeline redesign.

---

## Specific Numbers to Mention

- **20%** — French standard VAT rate (vs 19% DE)
- **5.5%** — French rate for essential food items (vs 7% DE for food)
- **September 1, 2026** — French B2B e-invoicing receive mandate (directly relevant to launch window)
- **Chorus Pro** — the state e-invoicing platform name
- **Factur-X** — the French e-invoice format (PDF + XML hybrid, also used in Germany as part of XRechnung)
- **CA3** — the French VAT filing form (equivalent to UStVA)
- **PCG** — Plan Comptable Général (French chart of accounts standard)

---

## How to Handle If Asked to Code France Expansion Live

If the live round asks you to add France to an existing DE pipeline:

1. **Define `FR_POLICY`** — identical structure to `DE_POLICY`, different values:
   - standardVatRate: 0.20
   - reducedVatRate: 0.10 (then 0.055 for a second tier)
   - vatAccountInput: "44566" (TVA déductible)
   - vatAccountOutput: "44571" (TVA collectée)
   - chartOfAccounts: PCG codes for the 5-6 most common categories

2. **Show the orchestrator is unchanged** — just pass `FR_POLICY` where `DE_POLICY` was

3. **Add one test case** — a French restaurant invoice at 10% rate and a takeaway at 5.5% to show the 4-rate handling

4. **Mention the cold-start threshold** — "For France at launch, I'd start with a higher proposal threshold since we have no calibration data yet — probably 0.95 auto-book minimum instead of 0.85"

5. **Mention e-invoicing** — "If we're thinking about September 2026, we also need a Factur-X parser stage before categorization for structured B2B invoices"
