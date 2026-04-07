# Interview Summary - March 31, 2025

**Date:** March 31, 2025  
**Interviewer:** Dmitry Ivanov (CTO) at Finom  
**Candidate:** Fysp  
**Format:** Intro call (~8.5 minutes)

---

## Transcript Quality

- Full transcript now available and reformatted
- Clean read from WhisperKit local inference

---

## Company Overview

Finom is a product platform for businesses, originally starting with 10-20 people. The company's differentiation strategy focuses on **authentic AI experiences** — not just sprinkling AI on top of traditional interfaces, but genuinely rethinking workflows to eliminate certain types of jobs to be done.

### Key Product: Agentic Accounting

Last year, one product team launched a new rethinking of the accounting product. Rather than bolting AI onto existing interfaces, they built it from the ground up with:

- **Background jobs** that react to events
- **Agentic automation** that proactively creates preliminary tax reports and asks for approval before filing to the government

This took off as both a vision and a product.

### The Vision: IC4 Platform

The company is now scaling this agentic approach across the entire product platform, originally called **IC4** (though the name may change). The vision is a platform that:

- Proactively reaches out to users and does jobs for them
- Monitors cash flow
- Alerts users when something is missing or trending negatively

They have the foundation in place and are actively building more projects around this vision.

---

## Organization Structure

### Team Setup

- **Core platform infrastructure** teams (standard foundation teams that keep the platform alive)
- **Product engineering domains** — squads built around missions, usually vertically aligned
- **EIC4** — the core team building the core agentic experiences

### AI Integration Philosophy

The vision is that the **whole platform will be stitched with MCP-based interfaces**, making it easy to connect new AI skills. They don't want a separation between "AI team" and "traditional team" — everyone is a product engineer, with some being more AI-leaning.

### AI Engineer Role

Historically at Phenom (Dmitry's previous company), AI engineers were a separate craft. But Finom is moving toward **merging AI expertise with existing product engineering crafts**. The ideal is:

- Everyone is a product engineer
- Some have extra expertise in AI/ML (LLMs, model integration, prompting)
- This is considered a "flavor" of product engineering, not a separate role

For someone joining, they'd likely work on one of the products at the bleeding edge, or join the **IC4 core team** that builds AI agents across the stack.

---

## Technical Stack

- **Primary backend:** C# / .NET (core backend engineering language)
- **Secondary language:** Python (for LLM-powered services)
- **Philosophy:** Two languages in the toolbelt — Python makes sense for building AI harnesses, C# for everything else

### Interesting Tech Mentioned

Dmitry asked about **DSPy** (Declarative Self-Improving Python) — found two weeks ago, described as "really cool" and "one of the most interesting tech in software for AI recently."

---

## Interviewer Questions

1. **When would be amazing for someone to start?** — Dmitry is flexible on Netherlands timing
2. **How is the team separated?** — AI-native developers in product teams, or an agentic layer? How does it work?

---

## Next Steps

- Dmitry wants to set up a call with a colleague to spend more time discussing the experiences and role
- Expressed mutual interest in continuing the conversation
- Will follow up

---

## Key Signals

| Area | Signal |
|------|--------|
| **Company direction** | Agentic AI platform across entire product suite |
| **Role fit** | IC4 core team building AI agents, or product teams at bleeding edge |
| **Technical alignment** | Python + C# stack, interest in DSPy, MCP-based architecture |
| **Culture** | No AI/non-AI separation — everyone is product engineer with AI-leaning optional |
| **Next step** | Call with colleague confirmed |

---

## Most Useful Takeaways

- Finom cares about production AI engineering more than AI novelty
- The role is product engineering with strong AI depth, not a detached research or platform-only role
- Reliability, observability, and real workflow integration are likely central evaluation criteria
- Strongest alignment: agentic systems that are operational, measurable, and production-grade

---

## Good Follow-Up Angles

- Ask how inter-agent coordination and failure isolation are handled
- Ask how quality is measured for tax/accounting workflows across different countries
- Ask how embedded the AI-specialist role really is inside product squads
- Ask how they divide responsibility between the IC4 core layer and broader product engineering teams
- Ask where reliability hardening currently constrains rollout
