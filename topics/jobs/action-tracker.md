# Job Preparation — Weekly Action Tracker

## Week 1: Apr 1-7, 2026 (Current)

### Completed
- [x] Analyze both 1st round interview source records
- [x] Create structured preparation materials (interview analysis, technical deep-dives)
- [x] Build interview simulation Q&A for both roles
- [x] Create experiment blueprints for hands-on demonstrations
- [x] Draft gap mitigation strategies with scripts
- [x] Write recruiter feedback summary for Samuel (Delphyr)
- [x] Create cross-company comparison and strategy document

### This Week — High Priority
- [ ] **Send feedback to Samuel** about the Delphyr call (use recruiter-feedback-samuel.md)
- [ ] **Sign up for Finom** free tier and explore the product (screenshots, notes on UX)
- [ ] **Build Experiment: MCP Skill Server** (Finom — highest signal experiment, 3-4 hours)
- [ ] **Build Experiment: Agent Safety Harness** (Delphyr — highest signal experiment, 3-4 hours)
- [ ] **Memorize SKR03 basics**: top 10 account codes for freelancers

### This Week — Medium Priority
- [ ] Read one ESMO clinical guideline (e.g., breast cancer, lung cancer)
- [ ] Set up Docker Kafka locally, produce/consume transaction events
- [ ] Write a minimal .NET 8 API (5 endpoints, 2 hours)

---

## Week 2: Apr 7-14, 2026

### Before Finom 3rd Round (Apr 14)
- [x] Complete MCP skill server experiment (built in `finom/experiments/mcp-accounting-skills/`)
- [x] Practice system design answer — system design template built (`cross-company-system-design-template.md`)
- [x] Build confidence calibration experiment (`finom/code/confidence-calibration.ts` — verified running)
- [x] Build multi-market expansion drill (`finom/code/multi-market-expansion-drill.ts` — verified running)
- [x] Create hostile follow-up question bank (`finom/prep/3-lead-ai-hostile-followups.md`)
- [x] Create day-of quick reference card (`finom/prep/3-lead-ai-engineer-day-of-card.md`)
- [ ] Know UStVA filing process step-by-step
- [ ] Research Qonto's AI features for comparison talking point
- [ ] Sign up for Finom free tier and explore the product

### Delphyr Follow-Up (Awaiting Response)
- [x] Complete agent safety harness experiment (built in `delphyr/experiments/agent-safety-harness/`)
- [x] Review clinical AI landscape for recent developments (`delphyr/insights/clinical-ai-landscape-april-2026.md`)
- [x] Build SOAP extraction pipeline (`delphyr/code/soap-extraction-pipeline.ts` — verified running)
- [x] Create status assessment and next-round angles (`delphyr/prep/status-assessment-and-next-round-angles.md`)
- [x] Build MDT evaluation benchmark framework (`delphyr/insights/mdt-evaluation-benchmark-framework.md`)
- [ ] Practice MDT preparation agent design answer
- [ ] Know MDR Class IIa requirements and 2-3 examples of certified AI SaMD
- [ ] Send follow-up to Samuel by Apr 14 if no news

### Gap Closing
- [ ] Fine-tune DistilBERT on a transaction categorization dataset (bridges PyTorch gap)
- [ ] Compare biomedical vs. general embeddings on PubMed data (bridges clinical RAG gap)
- [ ] Build C#/.NET + Python polyglot service demo (bridges .NET gap)

---

## Week 3: Apr 14-21, 2026

### Post-Interview Follow-Up
- [ ] Send thank-you notes after any 2nd rounds
- [ ] Document new signals from 2nd round conversations
- [ ] Update preparation materials based on what was asked
- [ ] Evaluate offers (if both progress) using comparison-strategy.md framework

### Ongoing Learning
- [ ] Build multi-agent accounting pipeline experiment (LangGraph)
- [ ] Build clinical decision graph experiment
- [ ] Deepen EU tax regime knowledge (Italian e-invoicing SDI is a good talking point)
- [ ] Study event sourcing / CQRS patterns (relevant to Finom's architecture)

---

## Experiment Priority (Both Roles)

| # | Experiment | Role | Status | Signal Value |
|---|-----------|------|--------|--------------|
| 1 | MCP Skill Server (accounting tools) | Finom | ✅ Built | Very High |
| 2 | Agent Safety Harness (commit/rollback) | Delphyr | ✅ Built | Very High |
| 3 | Multi-Agent Transaction Pipeline | Finom | ✅ Built (`accounting-mas-pipeline.ts`) | High |
| 4 | Clinical RAG Evaluation Pipeline | Delphyr | ✅ Built (`medical-extraction-agent.ts`) | High |
| 5 | Confidence Calibration Experiment | Both | ✅ Built (`confidence-calibration.ts`) | High |
| 6 | SOAP Extraction Pipeline | Delphyr | ✅ Built (`soap-extraction-pipeline.ts`) | High |
| 7 | Multi-Market Expansion Drill | Finom | ✅ Built (`multi-market-expansion-drill.ts`) | High |
| 8 | Live-Round Rehearsal | Finom | ✅ Built (`live-round-rehearsal.ts`) | Very High |
| 9 | Citation Verification | Delphyr | ✅ Built (`citation-verification.ts`) | High |
| 10 | Polyglot C#/.NET + Python Service | Finom | Not started | Medium |
| 11 | Clinical Decision Graph Generator | Delphyr | Not started | Medium |
| 12 | Privacy-Preserving Embedding Eval | Delphyr | Not started | Low-Medium |

**9 of 12 experiments built and verified running.** Remaining 3 are lower priority.

---

## Communication Tracker

| Date | Company | Contact | Action | Status |
|------|---------|---------|--------|--------|
| Mar 31 | Delphyr | Michel | 1st round call | Done |
| Mar 31 | Finom | Dmitry (CTO) | 1st round call | Done |
| Apr 1 | Delphyr | Samuel | Send detailed feedback | TODO |
| Apr 4 | Delphyr | Tim & Dejan | 2nd round (technical) | Done — outcome not recorded |
| Apr 8 | Finom | Ivo (CAIO) | 2nd round (central AI) | Done |
| ~Apr 14 | Finom | Senior AI Engineer | 3rd round (90 min technical + live) | Upcoming |
| Apr 18 | Delphyr | Michel/Samuel | Follow up if no news | Pending |

---

## Week 3: Apr 7-14, 2026 — New Materials Added (Apr 11)

### Finom — New Insights
- [x] `insights/live-coding-with-ai-agents-advanced-patterns.md` — meta-patterns for the 60-min live round: scaffold/implement/debug modes, verbal checkpoints, pitfalls
- [x] `insights/confidence-calibration-deep-dive.md` — ECE, Platt scaling, per-market calibration, calibration drift monitoring, earned autonomy ratchet

### Delphyr — New Insights
- [x] `insights/ambient-listening-architecture-analysis.md` — full pipeline analysis: ASR → diarization → SOAP structuring → citation → privacy architecture
- [x] `insights/mdt-evaluation-benchmark-framework.md` — 6-dimension evaluation framework with severity-weighted scoring, benchmark dataset design, practical targets

### Cross-Company — New Insights
- [x] `cross-company-production-feedback-loops.md` — correction classification, signal routing, eval suite growth, calibration drift detection, earned autonomy ratchet
- [x] `cross-company-error-taxonomy-worked-examples.md` — concrete error trees for both Finom (transaction processing) and Delphyr (clinical AI), with severity matrices and worked examples
- [x] `cross-company-system-design-template.md` — reusable 7-step system design answer framework with Finom and Delphyr instantiations

### Finom — New Code Experiments (Apr 11)
- [x] `finom/code/confidence-calibration.ts` — ECE, Platt scaling, per-market comparison, threshold analysis (verified running)
- [x] `finom/code/multi-market-expansion-drill.ts` — DE/FR/IT/NL tax rules, config validation, zero-code market addition (verified running)

### Delphyr — New Code Experiments (Apr 11)
- [x] `delphyr/code/soap-extraction-pipeline.ts` — transcript → SOAP notes, negation detection, citation linking, safety checks (verified running)

### Finom — Tactical Prep (Apr 11)
- [x] `finom/prep/3-lead-ai-hostile-followups.md` — 18 hostile follow-up questions across 6 categories
- [x] `finom/prep/3-lead-ai-engineer-day-of-card.md` — day-of quick reference card with thesis, environment checklist, verbal checkpoints, key numbers, gap responses, and questions to ask

### Delphyr — Tactical Prep (Apr 11)
- [x] `delphyr/prep/status-assessment-and-next-round-angles.md` — status assessment, follow-up templates, 4 new conversation hooks, transferable value inventory

### All Code Experiments Verified Running
All 5 runnable experiments tested successfully with `bun run`:
- `finom/code`: `rehearsal`, `calibration`, `multi-market` ✅
- `delphyr/code`: `soap`, `citation` ✅
