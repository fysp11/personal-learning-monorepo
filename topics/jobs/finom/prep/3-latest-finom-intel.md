# Finom Latest Intel — Interview 3 Prep

Saved: 2026-04-11

Research conducted for interview currency ahead of the April 14, 2026 technical round.

---

## AI Accountant Status

- **Beta launched March 2025**, rolled out to **all German customers by September 2025**
- Architecture: **distributed multi-agent system (MAS)** — multiple autonomous AI agents collaborating in a shared environment (publicly stated)
- Core capabilities: proactive transaction categorization, receipt/invoice recognition, bookkeeping record creation, automated tax filing to German authorities, TaxWallet for automated tax payments, real-time compliance notifications
- Integrates with **85% of popular German accounting software**
- **Next announced features**: Lohnsteueranmeldung (payroll tax) and Zusammenfassende Meldung (intra-EU transaction reports), plus GmbH and UG entity type support
- **AI Accountant is currently Germany-only** — expansion planned but no public timeline for France or other markets

## Funding & Business (Post-Series C)

- **May 2025**: EUR 92.7M growth investment from General Catalyst (non-dilutive)
- **June 2025**: EUR 115M Series C led by AVP, with Headline Growth, General Catalyst, Northzone, Cogito Capital
- **Total raised: over EUR 300M**
- Revenue doubled since Series B (Feb 2024). Positive unit economics across all markets. 500+ employees
- **125,000 customers** currently; target is **1 million by end of 2026** (CEO describes as "motivational")
- **M&A is on the table** — Sifted reported Finom is eyeing acquisitions

## Credit/Lending Expansion

- Credit lines piloted in Netherlands, **expanded to Germany**
- Plans to roll out credit across Europe
- AI-powered credit decisions use transaction history, behavioral patterns, and digital footprint analysis

## Market Presence

- Banking/invoicing live in **Germany, France, Italy, Spain, Netherlands** (local IBANs in all five)
- AI Accountant is **Germany-only** for now — this is a key gap the role would help close

## Engineering Signals

- **No public engineering blog** or tech talks found
- No public evidence of MCP usage (despite Dmitry's "stitched with MCP" comment in Interview 1)
- Most concrete architectural detail publicly: MAS architecture for AI Accountant

## Interview-Relevant New Vocabulary

| Term | Context |
|------|---------|
| Lohnsteueranmeldung | Payroll tax filing — announced as upcoming AI Accountant feature |
| Zusammenfassende Meldung | Intra-EU transaction reporting — upcoming feature |
| TaxWallet | Automated tax payment savings feature |
| GmbH / UG | German company types (next entity types for AI Accountant) |

## What This Means For The Interview

1. The AI Accountant is **real and shipped** — this is not a research project. Expect the interviewer to have strong opinions about production pain points.
2. **Multi-market expansion** is the next engineering challenge — your Germany→France architecture thinking is directly relevant.
3. The **MAS architecture** is publicly confirmed — your existing code demo maps directly to their approach.
4. **Credit/lending AI** is a new product surface — worth mentioning as a potential area where similar patterns apply.
5. The **absence of public engineering content** suggests the team is heads-down building. Don't expect them to be interested in thought leadership — they want execution.
