# First 90 Days — Framework for Both Roles

## Purpose

"What would your first 90 days look like?" is a standard senior interview question. This document provides structured answers for both Finom and Delphyr, adapted to each company's stage, team, and priorities.

---

## General Principles (Both Roles)

1. **Listen before building** — understand the existing system, team dynamics, and real pain points before proposing changes
2. **Ship something small early** — earn credibility through a quick, visible contribution in the first 2 weeks
3. **Build trust through transparency** — communicate what you're learning, what's unclear, and what risks you see
4. **Avoid the "new person rewrites everything" trap** — extend and improve what exists, don't replace it

---

## Finom — First 90 Days as Senior AI Engineer

### Context
- 500+ employees, central AI team, multiple product surfaces
- AI Accountant is live, lending is launching, analytics is planned
- Ivo (CAIO) leads the central AI team
- Your challenge: integrate into a larger org, understand cross-team dynamics, and deliver AI capability that multiple product teams can use

### Days 1-30: Learn and Orient

**Week 1: Onboarding + System Immersion**
- Meet the central AI team and understand each person's focus area
- Map the current agent architecture: which agents exist, how they communicate, where the observability is
- Get the local development environment running; deploy a trivial change to staging
- Read the AI Accountant pipeline end-to-end: intake → classification → extraction → reconciliation → categorization → tax prep → filing
- Understand the current evaluation setup: what metrics exist, how often are they run, what's the golden set quality

**Week 2-3: Stakeholder Mapping + Pain Points**
- Meet 3-4 product team leads to understand where AI is requested vs. where it's delivered
- Understand the central-vs-embedded tension: what does the central team own, what do product squads own?
- Identify the current top-3 quality issues (ask the team, don't guess)
- Shadow a customer support session to see real user complaints about AI categorization or reconciliation

**Week 4: First Contribution**
- Pick a bounded improvement: fix a known quality issue, add a missing metric, improve an evaluation test
- Ship it end-to-end (code → review → deploy → verify in production)
- Present findings from the first month to Ivo: "Here's what I've learned, here's what I think the top priorities are, here's what I'd like to own"

**Deliverable:** Written summary of current system state, quality gaps, and proposed focus areas.

### Days 31-60: Build and Prove

**Focus: Own one meaningful capability and deliver measurable improvement**

Likely candidates (depending on what the team needs):
- **Evaluation framework upgrade** — extend the golden set, add per-category calibration tracking, build a reliability diagram dashboard
- **Confidence calibration** — measure current ECE, implement temperature scaling or threshold tuning, reduce false auto-categorizations
- **New agent surface** — if lending is the priority, design and prototype the credit scoring agent pipeline
- **Cross-team capability** — build a reusable component (e.g., document extraction pipeline) that multiple product teams can use

**Approach:**
1. Propose the plan (1-page design doc, reviewed by Ivo and the team)
2. Build iteratively (weekly demos, not a big reveal)
3. Measure impact (before/after metrics, not just "I shipped code")

**Deliverable:** One shipped improvement with measured impact + design doc for the next major capability.

### Days 61-90: Lead and Multiply

**Focus: Influence beyond individual contributions**

- Propose a repeatable process: how new AI surfaces should be evaluated before launch (evaluation checklist, rollout playbook)
- Start mentoring or pairing with team members on evaluation and quality practices
- Write an internal RFC on a cross-cutting concern: confidence calibration strategy, or fraud risk overlay architecture, or multi-country agent design
- Build relationships with the product teams that will use the AI capabilities you're building

**Deliverable:** RFC or proposal for a strategic capability + established working relationships with 2-3 product teams.

### Talking Points

> "My first 30 days are about listening — understanding the existing system, the team, and the real pain points. I'd ship something small in week 4 to earn credibility. Days 31-60, I'd own one meaningful capability and deliver measurable improvement. By day 90, I want to be proposing how the central AI team should operate — evaluation standards, rollout processes, and cross-team leverage."

> "The risk I'd watch for is the 'shiny new thing' trap — jumping to build the next agent surface before understanding why the current one has quality issues. I'd start with the evaluation and quality foundation."

---

## Delphyr — First 90 Days as AI Engineer

### Context
- Small team (~6-8 people), everyone works on everything
- M1/M2 models in production at Reinier de Graaf, pilots at Erasmus MC
- Product surfaces: patient summary, guideline search, ambient listening, MDT prep
- Your challenge: high ownership in a small team, deliver end-to-end across the stack

### Days 1-30: Learn and Build Context

**Week 1: Product + Stack Immersion**
- Use the product as a clinician would (demo environment or shadow a pilot site)
- Read the M1/M2 architecture: how does M1 serve as the base model, how does M2 layer on top?
- Understand the RAG pipeline: what's the retrieval stack, how are chunks indexed, how are citations generated?
- Map the EHR integration points: ChipSoft, InterSystems, Bricks — how does data flow in and out?
- Get the development environment running; deploy a trivial change

**Week 2-3: Quality and Gaps**
- Understand the current evaluation setup: what golden sets exist, what metrics are tracked, how often?
- Review recent failure cases: where did the system produce wrong citations, miss information, or hallucinate?
- Talk to clinicians (or review clinician feedback): what do they value most, what frustrates them?
- Understand the regulatory constraints: what does MDR classification require from an engineering perspective?

**Week 4: First Contribution**
- Pick a quality improvement: fix a known citation issue, add a missing evaluation metric, improve retrieval for a specific document type
- Ship it and verify in production
- Share learnings with the team: "Here's what I've found, here's what I think matters most"

**Deliverable:** Written summary of system strengths, quality gaps, and proposed focus.

### Days 31-60: Own a Surface

**Focus: Take full ownership of one product surface and improve it measurably**

Likely candidates:
- **Citation verification pipeline** — build or improve claim-level verification with support/partial/unsupported classification
- **Retrieval quality** — implement hybrid retrieval (dense + sparse), measure precision/recall against a golden set
- **MDT preparation** — build the agent pipeline for multi-disciplinary team meeting prep
- **Guardrail hardening** — implement the multi-stage guardrail pipeline (input → retrieval → generation → output)

**Approach:**
1. Propose scope (reviewed by Dejan and team)
2. Build with tests and evaluation from the start
3. Deploy to one pilot site, measure clinician impact
4. Iterate based on real feedback

**Deliverable:** One surface measurably improved + evaluation data showing the improvement.

### Days 61-90: Scale and Systematize

**Focus: Make quality reproducible, not accidental**

- Build a reusable evaluation harness: golden sets, automated scoring, regression alerts
- Document the deployment process for adding new hospital integrations
- Contribute to MDR documentation: technical risk assessment, post-market monitoring setup
- Propose architecture for the next capability (e.g., ambient listening integration, decision support expansion)

**Deliverable:** Evaluation harness + documentation + architecture proposal for next capability.

### Talking Points

> "In a team this small, I'd expect to be contributing code in week 1 and shipping something by week 4. My first month is about understanding the system deeply — using the product, reviewing failure cases, talking to clinicians. Days 31-60, I'd take full ownership of one surface and improve it measurably. By day 90, I want to have built the evaluation infrastructure that makes quality improvements systematic, not ad hoc."

> "The unique challenge here is balancing speed with safety. I'd move fast on the evaluation and quality infrastructure because that's what gives you confidence to move fast on features."

---

## If Asked "What Would You Do Differently?"

### For Finom
> "I'd want to understand whether the central AI team is building for leverage or just building features. The difference matters: a central team should be creating reusable capabilities, not just shipping agent #7. My first 90 days would test that assumption."

### For Delphyr
> "I'd want to understand the gap between pilot and production. Reinier de Graaf is live, but scaling to 10 hospitals is a different engineering challenge than making one work. My first 90 days would focus on making the quality foundation scalable."

---

## Cross-Company: The Meta-Pattern

Both 90-day plans follow the same shape:

| Phase | Days | Focus | Deliverable |
|-------|------|-------|-------------|
| Learn | 1-30 | Understand system, team, pain points | Written assessment + first contribution |
| Build | 31-60 | Own one thing, deliver measurable improvement | Shipped improvement with impact data |
| Lead | 61-90 | Systematize, multiply, propose strategy | Evaluation infrastructure + strategic proposal |

This pattern works because it earns trust progressively: listen → prove → lead.
