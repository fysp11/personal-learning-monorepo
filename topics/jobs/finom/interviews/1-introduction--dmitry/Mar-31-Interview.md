# Interview Summary - March 31, 2026

**Date:** March 31, 2026  
**Interviewer:** Dmitry Ivanov (CTO) at Finom  
**Candidate:** Fysp  
**Duration:** ~8.5 minutes captured  

---

## Transcript Quality

- The source transcript appears to cover only the final portion of the interview.
- Despite the noisy transcription, the main product, org, and stack signals are fairly clear.

## Key Topics Discussed

### Finom product direction
- Finom is trying to go beyond "AI sprinkled on top" of existing interfaces.
- The focus is on agentic workflows that proactively complete real jobs to be done.
- Accounting was described as the first major area where this approach was pushed seriously.
- Example given: the system prepares a preliminary tax record, asks for approval, and then files it.
- The longer-term ambition is to extend this model across the full platform.
- The broader platform vision includes proactive support such as cash-flow monitoring, missing-item detection, and negative-trend alerts.

### Team and organization
- Engineering is split between core platform / infrastructure and product engineering domains.
- Product engineering domains are vertically aligned squads built around missions.
- Finom does not want a strict split between "AI product teams" and "traditional product teams."
- The direction appears to be embedding AI capabilities throughout the platform.
- Dmitry said they had historically treated AI engineer as a more separate craft, but are discussing merging that more tightly into the general product engineering craft.
- The framing was that everyone is fundamentally a product engineer, with some people leaning more heavily into AI specialization.

### Role shape
- The likely fit for this role is a team working at the bleeding edge of product development.
- Dmitry mentioned an `AIC` / `AI core` team that works on foundational experiences.
- The role is not limited to "just building agents."
- The expectation is cross-stack ownership: AI agents plus backend systems plus production concerns.
- Dmitry explicitly tied agent work to solid engineering fundamentals such as latency and observability.

### Stack signals
- LLM-powered services are more Python-heavy.
- The broader backend platform is primarily `.NET / C#`.
- The engineering environment is effectively polyglot, using the right language for the right layer.
- Dmitry explicitly said it did not make sense to build all AI harnesses in C#.

### Process / next step
- The conversation ended on a positive signal.
- Dmitry said it sounded worth continuing the conversation.
- He proposed a follow-up with his colleague `Rita` for a deeper discussion about experience and fit.

## Most Useful Takeaways

- Finom appears to care about production AI engineering more than AI novelty.
- The role is best understood as product engineering with strong AI depth, not as a detached research or platform-only role.
- Reliability, observability, and real workflow integration are likely central evaluation criteria.
- Your strongest alignment is with agentic systems that are operational, measurable, and production-grade.

## Good Follow-Up Angles

- Ask how inter-agent coordination and failure isolation are handled.
- Ask how quality is measured for tax/accounting workflows across different countries.
- Ask how embedded the AI-specialist role really is inside product squads.
- Ask how they divide responsibility between the `AI core` / `AIC` layer and the broader product engineering teams.
- Ask where reliability hardening currently constrains rollout.
