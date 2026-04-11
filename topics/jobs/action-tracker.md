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

### Before Finom 2nd Round (if scheduled)
- [ ] Complete MCP skill server experiment
- [ ] Practice system design answer: "Design German SMB transaction categorization"
- [ ] Know UStVA filing process step-by-step
- [ ] Research Qonto's AI features for comparison talking point
- [ ] Review Dmitry Ivanov's recent LinkedIn posts for conversation hooks

### Before Delphyr 2nd Round (if scheduled)
- [ ] Complete agent safety harness experiment
- [ ] Practice MDT preparation agent design answer
- [ ] Know MDR Class IIa requirements and 2-3 examples of certified AI SaMD
- [ ] Read about HL7 FHIR Patient/Observation resources
- [ ] Review clinical AI landscape for recent developments

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

| # | Experiment | Role | Time | Signal Value |
|---|-----------|------|------|--------------|
| 1 | MCP Skill Server (accounting tools) | Finom | 3-4h | Very High |
| 2 | Agent Safety Harness (commit/rollback) | Delphyr | 3-4h | Very High |
| 3 | Multi-Agent Transaction Pipeline | Finom | 4-5h | High |
| 4 | Clinical RAG Evaluation Pipeline | Delphyr | 3-4h | High |
| 5 | Polyglot C#/.NET + Python Service | Finom | 2-3h | Medium |
| 6 | Clinical Decision Graph Generator | Delphyr | 3-4h | Medium |
| 7 | Financial Accuracy Eval Framework | Finom | 3-4h | Medium |
| 8 | Privacy-Preserving Embedding Eval | Delphyr | 2-3h | Low-Medium |

**Total estimated time**: ~25-30 hours across all experiments
**Recommended subset for this week**: Experiments 1 + 2 (~7 hours)

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
