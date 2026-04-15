# Delphyr

## Snapshot
- Company: Delphyr
- Focus: healthcare AI assistants embedded in existing clinical systems
- Relevant themes: medical RAG, citations, guardrails, monitoring, EU privacy
- Last interview: Monday, March 31, 2026 with Michel Abdel Malek
- Last scheduled round: Friday, April 4, 2026 technical interview with Tim de Boer and Dejan Petkovic

## Start Here
- `INTERVIEW-PREP.md` - main evergreen prep note for Delphyr
- `interviews/2-technical--dejan-tim/README.md` - round-specific technical interview prep
- `prep/Medical-RAG-Guardrails-Landscape.md` - focused RAG and safety review
- `prep/Medical-AI-Eval-Metrics-Cheat-Sheet.md` - evaluation and monitoring refresh
- `prep/rag-guardrail-architecture-design.md` - deep technical guardrail pipeline architecture
- `prep/post-technical-interview-analysis.md` - post-April-4 analysis and next steps
- `prep/healthcare-ai-competitive-landscape.md` - competitive landscape analysis
- `code/README.md` - technical rehearsal code index (extraction agent + citation verification)

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
- Delphyr M1 is positioned as the first Dutch-built clinical language model.
- Product messaging emphasizes citations, guardrails, auditability, and EU data residency.
- Public partners and integration signals include ChipSoft, InterSystems, and Bricks.
- Public pilots include Erasmus MC and the Dutch Endometriosis Center.

## Team
- Michel Abdel Malek, MD - CEO and Founder
- Dejan Petkovic - Lead Engineer
- Tim de Boer - AI Engineer
- Joseph Shepherd, PhD - Medical Data Scientist
- Myrthe Kleijn - Commercial Lead
- Elise Wardenaar - Data Protection Officer

## Interview Timeline
- Monday, March 31, 2026 - initial interview with Michel in `interviews/1-introduction--michel/`
- Friday, April 4, 2026 - technical round prepared in `interviews/2-technical--dejan-tim/`

## Current Status: OFFER ACCEPTED — Joining Delphyr

**Outcome:** Offer received and accepted after the technical round with Michel, Dejan, and Tim. Joining Delphyr in Amsterdam.

**Next phase:** Relocation to Amsterdam. See `TRANSITION.md` for planning.

**Workspace purpose shift:** This folder now transitions from interview prep to onboarding and ramp-up context. The research, insights, and code here are foundational for the first 90 days.

- `insights/ambient-listening-architecture-analysis.md` — Delphyr's newest product surface: ASR → diarization → SOAP → privacy
- `insights/mdt-evaluation-benchmark-framework.md` — evaluation framework for MDT briefing quality
- `insights/clinical-ai-landscape-april-2026.md` — updated competitive landscape
- `prep/Medical-RAG-Guardrails-Landscape.md` — RAG and safety review
- `prep/rag-guardrail-architecture-design.md` — guardrail pipeline architecture
- `prep/healthcare-ai-competitive-landscape.md` — competitive landscape analysis
- `code/README.md` — technical rehearsal code (extraction agent + citation verification)
- Cross-company insights: `../cross-company-insights.md`

## Best Angles
- Production AI systems over messy data, not demos
- Correctness, traceability, and failure-mode awareness
- Practical retrieval, grounding, and evaluation judgment
- High-ownership working style with early risk communication

## Maintenance Notes
- Keep this README as the dashboard only; detailed prep stays in `INTERVIEW-PREP.md`, `prep/`, and round folders.
- After each Delphyr interview, update the relevant `interviews/<round>/` folder first, then refresh the timeline and current status here.
