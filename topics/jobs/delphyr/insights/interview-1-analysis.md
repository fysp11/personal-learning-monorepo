# Delphyr — 1st Interview Analysis
**Date**: March 31, 2026 | **Duration**: ~30 min | **Format**: Introductory call

## Key Signals from the Interview

### What They Build
- **Full in-house stack**: Search engine, embedding models, platform, harness — all built end-to-end
- **RAG for clinical data**: Patient data search + clinical/pharmaceutical information (drug databases, guidelines)
- **MDR classification**: Pursuing EU Medical Device Regulation status — aiming to be certified like a CT scan or scalpel for doctor use
- **Decision graphs + care pathways**: Currently working on clinical decision trees combining patient data with guideline data

### What They Need (Next Phase)
- **Agentic workflows for MDT preparation**: Multi-Disciplinary Team meetings require a "digital case" combining patient data + guideline data + decision recommendations
- **Beyond MDT**: Intake automation, any doctor-facing workflow touching patient data
- **Someone who fits the team AND has experience** — they emphasized both cultural fit and hands-on depth

### Team Structure
- 2 senior engineers / architects
- 1 mid-senior data scientist
- Junior data engineers
- Interviewer leads the team from HR perspective, seniors lead technically
- Small team, high trust environment

### Technical Stack (Inferred)
- Python (likely, given data/AI focus)
- Custom search engine (not off-the-shelf)
- Custom embedding models (fine-tuned in-house)
- Sentry for monitoring/alerting
- European cloud hosting (compliance-driven)

### Key Themes the Interviewer Probed
1. **Agent optimization** — "How do you optimize your builds?" → wanted depth on agent evaluation and iteration
2. **Speed vs. recall/precision** — directly asked about balancing these tradeoffs
3. **Evaluation frameworks** — very interested in how to measure agent correctness
4. **Differentiation from model providers** — "What is the one thing models cannot copy from software?"

## What Resonated (User's Answers That Landed Well)
1. **Self-healing scraper agent story** — the Sentry alerting → agent trigger → tag fix → website collection resume flow
2. **Evaluation depth** — granular action-level evaluation, not just end-to-end binary pass/fail
3. **DSPy mention** — prompted genuine "that's pretty cool" reaction, showed mutual technical curiosity
4. **Privacy-first thinking** — mentioning wife's privacy specialization + genuine concern about medical data
5. **Commit/rollback pattern for agentic workflows** — the idea of transactional safety in agent actions

## What the Interviewer Revealed About Culture
- **Quick decision-making**: "We tend to take decisions quickly"
- **Flexibility on start date**: No fixed timeline, open to relocation logistics
- **Growth phase**: Expecting significant workload increase in coming 6 months
- **Trust-driven**: Small team where each person's contribution is visible
- **Building trust through being first**: "Trust is what you get" — first-mover advantage in clinical AI matters

## Areas to Deepen for Next Round

### Technical Preparation
1. **MDR (Medical Device Regulation)** — understand Class IIa/IIb requirements for AI-as-medical-device
2. **Clinical decision support systems** — state of the art, regulatory landscape
3. **RAG for medical data** — privacy-preserving retrieval approaches (differential privacy, federated search)
4. **Agent safety patterns** — rollback/commit patterns, confidence thresholds, human-in-the-loop escalation
5. **Evaluation frameworks for clinical AI** — beyond standard LLM evals, medical-specific metrics

### Domain Preparation
1. **MDT (Multi-Disciplinary Team) meetings** — understand the clinical workflow being automated
2. **GDPR for medical data** — special category data provisions, patient consent models
3. **Dutch healthcare system** — UMC Amsterdam context, hospital data workflows
4. **Drug databases and clinical guidelines** — types of data in pharmaceutical RAG

### Questions for Next Round
1. "What does your current evaluation pipeline look like for clinical accuracy — do you have domain expert annotators, or is it more automated?"
2. "How do you handle the tension between MDR compliance (deterministic requirements) and LLM non-determinism?"
3. "What's the split between patient data retrieval vs. clinical knowledge retrieval in the RAG system — are these separate indices or unified?"
4. "For the MDT preparation agent — what does 'good enough' look like? Is it a draft that doctors refine, or a fully autonomous output?"
5. "How do you handle versioning of clinical guidelines across different specialties?"

## Competitive Advantage — What You Bring
- **Agent evaluation depth**: Granular, action-level evaluation with LLM-as-judge — exactly what they need for clinical correctness
- **Self-healing agent patterns**: Direct analog to clinical agents that need rollback/retry capabilities
- **Privacy awareness**: Genuine understanding through partner's GDPR specialization
- **Full-stack agent builder**: Can work across the entire stack, not just prompt engineering
- **DSPy / prompt optimization**: Relevant for clinical prompt tuning where small accuracy gains matter enormously
