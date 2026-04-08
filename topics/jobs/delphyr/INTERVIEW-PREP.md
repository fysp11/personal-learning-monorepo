# Delphyr Interview Prep Notes

Date: 2026-04-02 (updated 2026-04-08)

## Interview Context
- Round 1: Michel Abdel Malek (CEO) — completed March 31, 2026
- Round 2: Tim de Boer + Dejan Petković — completed April 4, 2026
- Role focus: technical depth, medical RAG, current working style, and cultural fit
- Cultural fit is described as at least as important as technical ability

## Post-Round-1 Learnings (Michel Interview, March 31)
- Self-healing scraper agent story resonated well (production reliability angle)
- Commit/rollback pattern was discussed and valued — led to building the safety harness experiment
- Evaluation depth was a positive signal — systematic quality over "it works"
- DSPy familiarity noted as staying current with AI tooling
- Privacy-first thinking aligned (GDPR, EU data residency)
- Culture signal: quick decisions, flexibility, trust-driven, first-mover advantage

**Note:** April 4 technical round outcome NOT yet recorded. Fill in when available.

## Confirmed Public Stack Signals
- Marketing site is built in Framer
- Google Tag Manager is installed on the public site
- Delphyr positions itself as an integration-first product that works inside existing EHR / GP systems
- InterSystems is a public integration / infrastructure partner
- Bricks (via Tetra) is a live primary-care integration point
- Delphyr has in-house models: **M1** (7B clinical language model) and **M2** (AI Copilot product layer)
- The public product messaging emphasizes citations, guardrails, monitoring, auditability, and EU data residency
- **Messaging shifted to "AI agents for clinicians" in March 2026** — agentic framing is now explicit
- Delphyr’s public messaging says it retrieves and condenses labs, notes, imaging, medications, and correspondence into one clinically relevant view
- Their integrations are described as working through existing systems and open APIs
- M1 is described publicly as a 7B-parameter model, Dutch-native, designed for modest hardware, EU data residency
- M1 benchmarks: PubMedQA 76.8%, MedMCQA 62.5%, MedQA 64.7%
- **Reinier de Graaf Hospital** is a confirmed live production deployment (not just pilot)
- Pilots: Erasmus MC, Dutch Endometriosis Center
- Their citation approach is centered on exact, verifiable source quotes rather than vague references
- Ambient listening for consult capture is a stated capability
- MDT preparation is explicitly listed as an M1 capability

## Likely Technical Topics In The Interview
- Production RAG over messy clinical data
- Retrieval quality: chunking, ranking, grounding, citations, precision / recall
- Safety and guardrails: topic drift, malicious instructions, source attribution
- Compliance and privacy: GDPR, EU data residency, medical-device constraints
- Observability: evals, monitoring, regressions, failure recovery
- Workflow embedding: fitting inside existing clinical systems instead of adding a new screen

## Likely Stack Pieces That Are Not Publicly Confirmed
- Backend language and framework
- Vector store / retrieval database
- RAG / agent orchestration framework
- Cloud provider and deployment stack

## Best Positioning For Me
- I build production AI systems over messy data, not just demos
- I care about correctness, traceability, and failure modes
- I can discuss retrieval, grounding, and evaluation concretely
- I work well in high-ownership teams and communicate risk early

## Questions Worth Asking
- How does M2 relate to M1 architecturally? Fine-tuned version, prompt layer, or separate model?
- How do you evaluate retrieval quality in medical RAG?
- What is the trust boundary between deterministic logic and model reasoning?
- How do citations get generated and verified?
- What does the current stack look like around integration, storage, and orchestration?
- What are the biggest sources of failure in production today?
- With Reinier de Graaf in production and Erasmus as a pilot, what's the deployment model for adding new hospitals?
- How does the Hugging Face investor connection influence your model development pipeline?
- What's the next major capability after MDT preparation and ambient listening?

## Source Links
- https://www.delphyr.ai/
- https://www.delphyr.ai/blog
- https://www.delphyr.ai/blog/delphyr-m1-best-in-class-medical-model
- https://www.delphyr.ai/blog/does-delphyr-integrate-with-other-electronic-health-record-systems
- https://www.delphyr.ai/nl/blog/delphyr-partners-intersystems
- https://www.linkedin.com/jobs/view/4394529807

## Related Prep Notes
- prep/Medical-RAG-Guardrails-Landscape.md
- prep/Guardrails-In-Code.md
- prep/Medical-AI-Eval-Metrics-Cheat-Sheet.md
- prep/Mastra-Scorers-Implementation.md
- prep/hybrid-retrieval-architecture-deep-dive.md — patient-scoped hybrid retrieval design
- prep/mdt-preparation-agent-design.md — MDT meeting preparation agent architecture
- prep/healthcare-ai-competitive-landscape.md — competitive landscape analysis
- updates/delphyr-april-2026-intel.md — fresh April 2026 intelligence
- ../confidence-calibration-patterns.md — confidence calibration deep-dive (shared)

## Code Examples
- code/medical-extraction-agent.ts — clinical extraction with custom scorers
- code/citation-verification.ts — claim-level citation verification
- code/agent-safety-harness.ts — **transactional commit/rollback for clinical agents** (NEW)
