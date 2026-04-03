# Delphyr Interview Prep Notes

Date: 2026-04-02

## Interview Context
- Interviewers: Tim de Boer and Dejan Petković
- Role focus: technical depth, medical RAG, current working style, and cultural fit
- Cultural fit is described as at least as important as technical ability

## Confirmed Public Stack Signals
- Marketing site is built in Framer
- Google Tag Manager is installed on the public site
- Delphyr positions itself as an integration-first product that works inside existing EHR / GP systems
- InterSystems is a public integration / infrastructure partner
- Bricks is a live primary-care integration point
- Delphyr has an in-house M1 clinical model
- The public product messaging emphasizes citations, guardrails, monitoring, auditability, and EU data residency
- Delphyr’s public messaging says it retrieves and condenses labs, notes, imaging, medications, and correspondence into one clinically relevant view
- Their integrations are described as working through existing systems and open APIs
- M1 is described publicly as a 7B-parameter model, Dutch-native, and designed to run on modest hardware while keeping patient data in Europe
- Their citation approach is public-facing and centered on exact, verifiable source quotes rather than vague references

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
- How do you evaluate retrieval quality in medical RAG?
- What is the trust boundary between deterministic logic and model reasoning?
- How do citations get generated and verified?
- What does the current stack look like around integration, storage, and orchestration?
- What are the biggest sources of failure in production today?

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
