# Fintech Vocabulary Quick Reference

## Purpose
Rapid recall cheat sheet for German SME accounting and fintech terminology. Use for last-minute review before Finom interviews.

---

## German Accounting Terms

| German | English | Context |
|--------|---------|---------|
| **Kontenrahmen** | Chart of accounts | Framework for organizing bookkeeping categories |
| **SKR03** | Standard chart of accounts (process-oriented) | Most common for SMEs; organized by business process |
| **SKR04** | Standard chart of accounts (function-oriented) | Alternative; organized by balance sheet function |
| **Betriebsausgabe** | Operating expense | Deductible business expense |
| **Vorsteuerabzug** | Input tax deduction | VAT paid on purchases, deductible from VAT owed |
| **Umsatzsteuer (USt)** | Value-added tax (VAT) | 19% standard, 7% reduced rate in Germany |
| **UStVA** | VAT advance return | Monthly/quarterly VAT filing to Finanzamt |
| **EÜR** | Income surplus calculation | Simplified profit/loss for small businesses |
| **GeSt** | Trade tax return | Municipal business tax filing |
| **ESt** | Income tax return | Personal income tax (for sole proprietors) |
| **Finanzamt** | Tax authority | Local tax office |
| **Buchführung** | Bookkeeping | General term for accounting records |
| **Belegpflicht** | Receipt obligation | Legal requirement to keep receipts |
| **Anlagevermögen** | Fixed assets | Long-term assets (equipment, vehicles) |
| **Umlaufvermögen** | Current assets | Short-term assets (cash, inventory, receivables) |
| **Bewirtung** | Business entertainment | Partially deductible expense category |
| **Reisekosten** | Travel expenses | Deductible business travel costs |
| **Fremdleistungen** | External services | Outsourced/contracted work |
| **Wareneinkauf** | Goods purchased | Inventory/materials for resale |
| **Abschreibung (AfA)** | Depreciation | Annual deduction for fixed asset value loss |
| **Kleinunternehmer** | Small business (VAT-exempt) | <€22K revenue → no VAT charged or reported |

## Key SKR03 Account Ranges

| Range | Category | Example |
|-------|----------|---------|
| 0000-0999 | Fixed assets | Equipment, vehicles |
| 1000-1999 | Financial assets + receivables | Bank accounts, customer receivables |
| 2000-2999 | Liabilities | Loans, supplier payables |
| 3000-3999 | Revenue | Sales income |
| 4000-4999 | Cost of materials | Goods purchased, external services |
| 5000-5999 | Personnel costs | Salaries, social contributions |
| 6000-6999 | Other operating expenses | Rent, insurance, travel |
| 7000-7999 | Extraordinary items | One-time events |
| 8000-8999 | Other revenue | Interest, asset sales |

## Tax Filing Calendar (Germany)

| Filing | Frequency | Deadline |
|--------|-----------|----------|
| UStVA | Monthly or quarterly | 10th of following month |
| EÜR | Annual | July 31 (with advisor) |
| ESt | Annual | July 31 (with advisor) |
| GeSt | Annual | July 31 (with advisor) |

---

## Fintech / Banking Terms

| Term | Meaning | Finom Context |
|------|---------|---------------|
| **EMI** | Electronic Money Institution | Finom's license type |
| **PSD2** | Payment Services Directive 2 | EU payment regulation; enables open banking |
| **SCA** | Strong Customer Authentication | Two-factor auth required for payments |
| **AML/CFT** | Anti-Money Laundering / Counter Financing of Terrorism | Compliance requirements |
| **KYC** | Know Your Customer | Identity verification at onboarding |
| **SAR** | Suspicious Activity Report | Mandatory fraud/AML report to authorities |
| **SEPA** | Single Euro Payments Area | EU-wide payment standard |
| **IBAN** | International Bank Account Number | Standard account identifier |
| **BIC/SWIFT** | Bank Identifier Code | Bank routing identifier |
| **Open Banking** | Third-party access to bank data via APIs | PSD2-enabled |
| **Embedded Finance** | Financial services built into non-financial platforms | Finom's strategy direction |

---

## AI / ML Terms in Finom Context

| Term | Finom Usage |
|------|-------------|
| **MAS** | Multi-Agent System — Finom's AI Accountant architecture |
| **MCP** | Model Context Protocol — tool/skill interface (Dmitry mentioned) |
| **DSPy** | Systematic prompt optimization framework (Dmitry interested) |
| **Confidence propagation** | Passing confidence scores between agents in the pipeline |
| **Circuit breaking** | Halting pipeline when upstream confidence is too low |
| **Shadow mode** | Running AI alongside human decisions without acting |
| **Staged autonomy** | Gradually increasing AI automation as trust is earned |
| **Golden set** | Labeled evaluation dataset for accuracy measurement |
| **ECE** | Expected Calibration Error — measures confidence vs. accuracy alignment |
