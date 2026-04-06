# Tim vs Dejan — Interview Cheat Sheet

Date: 2026-04-03
Scope: Technical interview prep for Tim de Boer and Dejan Petković

## Shared Baseline For Both

Lead with:
- production AI over messy data
- correctness, traceability, and failure modes
- practical trade-offs
- low-ego, high-ownership teamwork

Avoid:
- generic LLM hype
- vague abstractions
- pretending deep healthcare expertise you do not have

---

## Tim de Boer

### He likely values
- citations as a hard trust requirement
- claim-level grounding
- practical reliability in medical RAG
- safety / evals tied to real clinical use

### Emphasize
- exact evidence over vague references
- no-source-no-claim
- support validation
- why clinicians need outputs that are cheap to verify
- why speed is less important than traceable correctness

### Best answer style
- start from the risk
- explain how you would make outputs verifiable
- mention concrete checks: citations, support validation, abstention

### Good phrases to use
- “In medical AI, retrieval without verifiability is only a partial solution.”
- “I’d rather make the system slower but easy to trust.”
- “Claim-level evidence matters more than document-level references.”

### Likely follow-up areas
- how citations are generated
- how you validate support
- how you evaluate factuality
- what happens when evidence is weak or conflicting

### Avoid with Tim
- treating citations like a UX add-on
- talking about RAG like it automatically solves hallucinations
- sounding impressed by model capability without discussing trust

---

## Dejan Petković

### He likely values
- implementation depth
- architecture choices under constraints
- integrations and platform thinking
- agentic workflows without hype
- build-vs-buy judgment

### Emphasize
- system design
- trade-offs
- operational complexity
- integration realities
- how you reason about architecture in small teams

### Best answer style
- explain the problem
- describe the architecture
- name trade-offs
- discuss failure modes
- explain monitoring / iteration

### Good phrases to use
- “I try to optimize for operability, not just elegance.”
- “I’d separate what must be deterministic from what can be model-driven.”
- “Build-vs-buy depends on trust boundaries, speed, and how core the capability is.”

### Likely follow-up areas
- how you structured previous systems
- how you handled scale or reliability
- integration / orchestration choices
- agent workflows and how to evaluate them
- how you work in high-ownership teams

### Avoid with Dejan
- hand-wavy system descriptions
- ideology about frameworks or vendors
- overfocusing on prompts instead of architecture / operations

---

## If Tim Asks X, Pivot To Y

- **“How would you make medical RAG trustworthy?”**
  - citations, support validation, patient scope, abstention
- **“How do you evaluate output quality?”**
  - support vs severity, scenario testing, clinician review

## If Dejan Asks X, Pivot To Y

- **“Tell me about a system you built”**
  - architecture, trade-offs, monitoring, lessons learned
- **“How would you design this at Delphyr?”**
  - integrations, trust boundaries, operational simplicity, staged rollout

---

## Best Overall Positioning

### To Tim
“I care about whether the system can justify what it says.”

### To Dejan
“I care about whether the system can run reliably in the real world.”

### To both
“I like building AI systems that are useful, testable, and trustworthy — not just impressive in demos.”
