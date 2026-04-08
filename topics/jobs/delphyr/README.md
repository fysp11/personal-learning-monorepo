# Delphyr

## Snapshot
- Company: Delphyr
- Focus: healthcare AI assistants embedded in existing clinical systems
- Relevant themes: medical RAG, citations, guardrails, monitoring, EU privacy
- Last recorded interview: Monday, March 31, 2026 with Michel Abdel Malek
- Last scheduled round: Friday, April 4, 2026 technical interview with Tim de Boer and Dejan Petkovic

## Start Here
- `INTERVIEW-PREP.md` - main evergreen prep note for Delphyr
- `interviews/2-technical--dejan-tim/README.md` - round-specific technical interview prep
- `prep/Medical-RAG-Guardrails-Landscape.md` - focused RAG and safety review
- `prep/Medical-AI-Eval-Metrics-Cheat-Sheet.md` - evaluation and monitoring refresh
- `prep/rag-guardrail-architecture-design.md` - deep technical guardrail pipeline architecture
- `prep/post-technical-interview-analysis.md` - post-April-4 analysis and next steps
- `prep/hybrid-retrieval-architecture-deep-dive.md` - patient-scoped hybrid retrieval design with implementation plan
- `prep/mdt-preparation-agent-design.md` - MDT meeting preparation agent architecture (4-agent decomposition)
- `prep/healthcare-ai-competitive-landscape.md` - competitive landscape analysis
- `updates/delphyr-april-2026-intel.md` - fresh April 2026 intelligence (M1/M2, deployments, agentic shift)
- `../confidence-calibration-patterns.md` - confidence calibration deep-dive (shared with Finom)
- `code/README.md` - technical rehearsal code index (extraction + citation + safety harness)
- `../system-design-interview-frameworks.md` - system design answer frameworks (shared with Finom)

## Company Overview
- Amsterdam-based healthcare AI startup focused on reducing administrative burden on healthcare professionals.
- Funded by founders of Hugging Face and DEGIRO.
- Applied for medical device classification.

## Product Shape
- Patient data consolidation across notes, labs, and correspondence
- Clinical guideline search and retrieval
- Administrative task automation
- Ambient listening for consult notes
- Decision-support workflows inside existing HIS and EHR systems

## Key Milestones
- Delphyr M1 is positioned as the first Dutch-built clinical language model (7B parameters, Dutch-native).
- **M2 is the AI Copilot** — the product-facing layer on top of M1, integrated directly into EHRs.
- Product messaging emphasizes citations, guardrails, auditability, and EU data residency.
- **Public messaging shifted to "AI agents for clinicians"** in March 2026 — agentic framing is now explicit.
- Public partners and integration signals include ChipSoft, InterSystems, and Bricks (via Tetra).
- **Reinier de Graaf Hospital** — confirmed live production deployment (not just pilot).
- Erasmus MC and the Dutch Endometriosis Center — active pilots.
- M1 benchmarks: PubMedQA 76.8%, MedMCQA 62.5%, MedQA 64.7%.

## Team
- Michel Abdel Malek, MD - CEO and Founder
- Dejan Petkovic - Lead Engineer
- Tim de Boer - AI Engineer
- Joseph Shepherd, PhD - Medical Data Scientist
- Myrthe Kleijn - Commercial Lead
- Elise Wardenaar - Data Protection Officer

## Interview Timeline
- Monday, March 31, 2026 - initial interview captured in `interviews/1-introduction--michel/`
- Friday, April 4, 2026 - technical round prepared in `interviews/2-technical--dejan-tim/`

## Current Status
- The workspace is ready for Delphyr follow-up work, but no post-April-4 outcome has been captured yet.
- Next action: record outcome notes for the technical round, then either prepare the next interview folder or close the loop in this README.
- New deeper technical materials added: guardrail architecture design and post-interview analysis framework.
- Cross-company insights connecting Delphyr and Finom prep: `../cross-company-insights.md`

## Best Angles
- Production AI systems over messy data, not demos
- Correctness, traceability, and failure-mode awareness
- Practical retrieval, grounding, and evaluation judgment
- High-ownership working style with early risk communication

## Maintenance Notes
- Keep this README as the dashboard only; detailed prep stays in `INTERVIEW-PREP.md`, `prep/`, and round folders.
- After each Delphyr interview, update the relevant `interviews/<round>/` folder first, then refresh the timeline and current status here.
