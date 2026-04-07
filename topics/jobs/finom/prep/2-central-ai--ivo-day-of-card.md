# Ivo Interview - Day-Of Quick Reference

Date: Wednesday, April 8, 2026
Duration: 45 minutes
Interviewer: Ivo Dimitrov (co-founder, **Chief AI Officer**)

> **Fresh intel (April 7):**
> - TheOrg lists Ivo as "Chief AI Officer" — this is a C-level AI mandate
> - Finom's AI Accountant is a **distributed multi-agent system (MAS)** — publicly stated
> - Finom targets **1M business customers by end of 2026**
> - **Ivo quote:** "The biggest mistake AI companies make is trying to build their own models instead of orchestrating existing foundations." → He believes in **orchestration over model-building**. Frame your answers around application-layer engineering, not foundation model work.
> - **AI-Powered Lending launched March 2026** in NL with AI credit scoring — a second major AI surface beyond accounting. This strengthens the case for a central AI team.
> - **Finom X:** Migrated off Solaris to own payments infrastructure + EMI license across 5 EU markets — more control over data pipelines feeding AI features.
> - **Hiring surge:** 45 hires in March alone, 500+ employees, 116 open positions.
> - **Qonto (main competitor):** Published AI Vision Statement March 2026, runs 50+ internal AI agents via Dust platform, partnered with Twin for autonomous agents. Pursuing "Jidoka" (automation with human touch).

---

## 30-Second Intro

"I build production AI systems for workflows where correctness matters. My strongest work is in agentic pipelines, document-heavy operations, and evaluation discipline. Finom interests me because you're embedding AI into real financial operations — not adding a chatbot, but rebuilding workflows around proactive AI. That's the kind of problem where my background in production reliability, staged automation, and reusable capability design creates the most value."

---

## Core Thesis (memorize this)

**Central AI should own the reusable hard parts and earn adoption through shipped value, while product teams stay closest to workflow outcomes and user reality.**

---

## Top 5 Ivo Priorities (what he cares about)

1. **Cross-company AI leverage** — not one feature, but patterns that scale
2. **Central vs embedded** — what to centralize, what to leave with squads
3. **Business-critical quality** — correctness in finance, not demo quality
4. **Build vs buy judgment** — where defensibility lives
5. **Practical execution** — can you ship, not just strategize

---

## My 3 Strongest Angles

1. **Production multi-agent systems at scale** → 30-60K docs/day, staged pipeline, confidence routing — maps directly to Finom's MAS architecture
2. **Eval and observability discipline** → 3-layer evals, workflow metrics > component metrics
3. **Ambiguity to repeatable capability** → vague mandate → shipped v1 in weeks → reused across 3 workflows

> **MAS talking point:** "Finom's AI Accountant is a multi-agent system — I've built production systems with the same shape: typed agent boundaries, confidence propagation between stages, failure isolation, and end-to-end observability. See `multi-agent-system-architecture-for-fintech.md` for full prep."

---

## Key Framing: "Orchestrate, Don't Build"

Ivo's public philosophy is orchestration over foundation model building. This means:
- **DO:** Talk about application-layer engineering, agent coordination, evaluation, workflow design, quality systems
- **DO:** Emphasize composing existing models with domain-specific orchestration
- **DON'T:** Talk about training models, fine-tuning at scale, or competing with model labs
- **Bridge:** "The defensible value in fintech AI isn't the models — it's the orchestration, domain policy enforcement, quality systems, and workflow control that sit on top."

## AI Surface Expansion (use to strengthen central AI case)

Finom's AI is no longer just accounting:
- **AI Accounting Agent** — live, MAS architecture, Germany + EU expansion
- **AI-Powered Lending** — launched March 2026 in NL, AI credit scoring
- **Coming:** AI-enhanced financial analytics, invoice financing, credit lines for freelancers

→ "With AI expanding from accounting into lending and analytics, the case for centralized AI capabilities is even stronger. Shared evaluation, observability, and quality infrastructure across these surfaces prevents each team from reinventing the wheel."

---

## Central AI Answer (have this ready cold)

Centralize:
- Evaluation patterns and quality bar
- Observability and runtime instrumentation
- Workflow and tool-use conventions
- Shared retrieval/document primitives
- Guardrails, approval rails, rollout defaults

Do NOT centralize:
- Domain workflow design
- User interaction details
- Product prioritization
- Feature-specific prompt engineering

How to not become a bottleneck:
- Ship one direct workflow win for credibility
- Build reusable primitives that teams adopt because they help, not because mandated
- Paved roads, not gatekeeping
- Treat bypass as product signal

---

## First 90 Days Answer

1. Map live AI and automation efforts across teams
2. Identify duplicate work and duplicate failure modes
3. Pick one high-leverage workflow to ship or stabilize
4. Establish minimal shared quality layer: eval definitions, runtime traces, failure taxonomy

Goal: one visible win + minimum reusable structure

---

## Fintech Bridge (handle the domain gap)

"I won't claim deep fintech expertise. What I bring is experience building correctness-sensitive systems where failure modes are expensive. The transferable discipline is: evaluation, routing, observability, staged rollout, and failure handling around high-cost workflows. I'd pair that with Finom's domain experts."

---

## Top 5 Questions To Ask Ivo

1. How do you define the mandate of the central AI team today?
2. What are the biggest problems you want that team to solve in the next 6-12 months?
3. Where do you see the boundary between central AI and product engineering squads?
4. What has already worked well, and where has the current setup created friction?
5. If this role joined, what would be the first high-leverage area to own?

## Top 2 If Time Is Short

1. How do you define the mandate of the central AI team today?
2. If this role joined, what would be the first high-leverage area to own?

---

## Red Flags To Avoid

- Do NOT name-drop frameworks
- Do NOT sound like you want to build a detached AI platform
- Do NOT overclaim fintech depth
- Do NOT contradict Dmitry — reconcile: central AI provides leverage, product squads own outcomes
- Do NOT make everything sound like an agent problem

---

## Altitude Reminder

Dmitry tested: **can you build serious production AI?**
Ivo tests: **can you help shape how AI creates leverage across the company?**

Stay higher altitude. Lead with capability design, business leverage, and org judgment. Ground with one concrete example per answer.
