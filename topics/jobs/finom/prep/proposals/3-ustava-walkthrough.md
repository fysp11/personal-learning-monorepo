# German SME Accounting — Practical UStVA Walkthrough

Saved: 2026-04-11 (Iteration 4)

## Purpose

This document bridges the gap between vocabulary (see `german-sme-accounting-domain-primer.md`) and lived procedural understanding. Use it to answer "walk me through what happens when a Finom user closes their month" or "what does the AI actually do step by step?"

---

## Context: Who Is the User?

Anna is a freelance UX designer in Hamburg. She earns ~€80K/year, is VAT-registered (not a Kleinunternehmer), files UStVA monthly, and uses Finom as her business bank + accounting tool.

**Her accounting burden without AI:**
- ~25 transactions/month from her business account
- Manually scan and upload receipts (software subscriptions, hardware, coworking space, meals)
- Enter each into a spreadsheet → assign a category → track Vorsteuer
- At month-end: tally gross sales, deduct input VAT (Vorsteuer), calculate net VAT owed
- File UStVA via ELSTER before the 10th of the following month (or request a permanent extension, Dauerfristverlängerung)

---

## Month-End Walkthrough — What Finom AI Does

### Step 1: Transaction ingestion (Days 1–31)

Every time a transaction clears Anna's Finom account, the system:
- Captures: merchant name, amount, IBAN, reference text, date
- Calls the **extraction agent** to normalize the merchant name, infer transaction type (inbound invoice, outbound invoice, bank fee, personal transfer)
- Stores a structured `ExtractedTransaction` object with an `extractionConfidence` score

**AI decision point:** Is this a business transaction or a personal one? If Anna pays for a meal at a restaurant, is it a deductible business expense (Betriebsausgabe) or a private meal? If confidence is low, the system flags it for Anna's review.

---

### Step 2: Receipt matching (Ongoing)

When Anna receives a PDF invoice (e.g., Adobe Creative Cloud €59.99 + €11.40 Umsatzsteuer = €71.39 gross), the system:
- Runs OCR extraction on the PDF
- Extracts: vendor name, invoice date, gross amount, net amount, VAT amount, VAT rate (19%), vendor VAT ID (Umsatzsteuer-Identifikationsnummer)
- Attempts to **match** the invoice to a bank transaction by amount + date window

**AI decision point:** Was the 19% VAT rate correctly extracted? Is this a standard-rated service or could it qualify for reduced rate (7%)? A software subscription is 19%; a book in digital form is 7% in Germany. Getting this wrong means claiming the wrong Vorsteuer.

---

### Step 3: Category assignment (Per transaction)

The categorization agent assigns each expense to an SKR03 account code:

| Expense | SKR03 code | VAT treatment |
|---------|-----------|---------------|
| Adobe subscription | 4920 (Software/SaaS) | 19% Vorsteuer claimable |
| Coworking space | 4210 (Miete und Pacht) | 19% Vorsteuer claimable |
| Business lunch (client present) | 4650 (Repräsentationskosten) | Only 70% of 19% claimable |
| Train ticket (business travel) | 4670 (Reisekosten) | 7% Vorsteuer claimable |
| Hardware (laptop) | 0490 (BGA) or 4980 | 19%, capitalized if >€800 |

**AI decision point:** The system proposes an SKR03 code + confidence. If confidence > 0.85, it auto-books. If 0.5–0.85, it shows Anna a proposal card: "We suggest this as *Software/SaaS (4920)* with 19% VAT — confirm?" Below 0.5, it asks Anna to categorize manually.

**Tricky case: business lunch.** German tax law only allows deduction of 70% of entertainment expenses (§4 Abs. 5 Nr. 2 EStG). The VAT rule is also limited to 70% of the input VAT. This cannot be left to AI — it's a deterministic rule based on category code. Once the category is confirmed as Repräsentationskosten, the VAT split must be calculated exactly.

---

### Step 4: VAT calculation — building the Voranmeldung (End of month)

At month-end, the system aggregates:

**Umsatzsteuer (output VAT — what Anna collected from clients):**
- Anna issued 3 invoices totaling €15,000 net + €2,850 VAT (19%)
- Umsatzsteuer: **€2,850**

**Vorsteuer (input VAT — what Anna paid to suppliers):**
- Adobe (19%): €11.40
- Coworking (19%): €190
- Train (7%): €3.50
- Lunch (70% × 19%): €8.19
- Vorsteuer total: **€213.09**

**Zahllast (VAT payment owed):**
- €2,850 − €213.09 = **€2,636.91 to Finanzamt**

This calculation is **entirely deterministic** once categories and amounts are confirmed. There is no AI in this step. A wrong AI categorization above flows into this as incorrect Vorsteuer.

---

### Step 5: Pre-flight validation

Before showing Anna the UStVA draft, the system runs deterministic checks:

- **Sum check:** Net sales × rate = gross. Any mismatch → flag extraction error
- **Reverse charge check:** Did Anna receive any invoices from EU vendors (e.g., AWS Ireland)? Those require reverse charge: Anna owes the VAT herself (as both payer and recipient). This must be detected from the vendor VAT ID pattern (IE for Ireland, FR for France, etc.)
- **Kleinunternehmer guard:** Is Anna still under the €22K threshold? If she crossed it this year, her next invoices must include VAT
- **Late receipt check:** Any transactions in the period with no matched receipt? Flag for Anna before filing

---

### Step 6: UStVA generation and ELSTER submission

The system:
- Populates the UStVA XML template with:
  - `Kz 81` (taxable sales at 19%): €15,000
  - `Kz 63` (input VAT): €213.09
  - `Kz 83` (VAT payable): €2,636.91
  - `Kz 09` (tax period): March 2026
- Validates the XML against the ELSTER schema
- Sends to ELSTER API using Anna's stored electronic signature (Elster-Zertifikat)
- Records confirmation number in the transaction log

**This step requires human approval before submission.** Filing a VAT return is legally irreversible without a formal amendment (Berichtigung). Finom must always present the draft to the user and require explicit sign-off.

---

## Where AI Errors Have Outsized Impact

```
Miscategorization
  └─ wrong SKR03 code
      └─ wrong VAT rate applied
          └─ wrong Vorsteuer claimed
              └─ UStVA filed with wrong amount
                  └─ Finanzamt issues correction notice (Änderungsbescheid)
                      └─ Possible penalty interest (Nachzahlungszinsen, 1.8%/year)
```

This is why severity weighting matters. A wrong category for a €50 subscription that doesn't affect VAT at all (both standard rate) is severity-LOW. A wrong category that incorrectly applies 7% instead of 19% to a €5,000 SaaS invoice is severity-CRITICAL — it under-claims VAT by €600.

---

## How To Use This In The Interview

**If asked "walk me through the accounting automation pipeline":**
> "Take Anna, a German freelancer. Every transaction triggers extraction and categorization. By month-end, we've built up a set of confirmed bookings. The VAT calculation is then purely arithmetic — all the AI work is done upstream. We aggregate output VAT from her invoices, subtract input VAT from her confirmed expenses, and produce the Zahllast. The UStVA XML goes to ELSTER with her explicit approval — never auto-filed."

**If asked "what's the hardest AI problem in German accounting automation?"**
> "Vorsteuer correctness — specifically when the right VAT treatment depends on context. Is this a business meal or a personal meal? Is this software at 19% or a digital book at 7%? These aren't lookup problems; they require transaction context and sometimes user intent. The defense is confidence routing: flag ambiguous cases rather than guess, and track the override rate to see where the AI is systematically wrong."

**If asked about the reverse charge case:**
> "A German freelancer buying AWS services from AWS Ireland gets an invoice with 0% VAT — AWS doesn't charge German VAT. But the German buyer still owes the VAT under §13b UStG: they self-assess it as both input and output VAT. We detect this by checking if the vendor is a non-German EU entity with a VAT ID. Then the booking is: debit the expense account, credit Vorsteuer (claimable), debit Umsatzsteuer (owed). This is deterministic once the vendor flag is detected — but getting the detection right is an AI categorization problem."

---

## Finom-Specific Angles

- **AI Accountant GA (April 2026):** The system described above is live for 200K+ accounts. The monthly UStVA filing is one of the primary automated outputs.
- **GmbH expansion:** GmbHs use full Buchführung (double-entry), not just EÜR. Their month-end involves trial balance, depreciation, and accruals — harder AI problem, more at stake per error.
- **Lohnsteueranmeldung (coming):** Payroll tax return. Same pattern: deterministic calculation once categories and hours are confirmed. The AI's job is extracting payroll data from invoices and employee contracts.
