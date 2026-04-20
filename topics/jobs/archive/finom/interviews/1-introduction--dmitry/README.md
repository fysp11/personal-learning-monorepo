# Finom First Interview - Dmitry Ivanov

## Round Summary
- Date: Monday, March 31, 2026
- Interviewer: Dmitry Ivanov, CTO
- Candidate: Fysp
- Format: intro call, about 8.5 minutes
- Main value of this round: product, org, and stack signals that shaped the next interview

## Distilled Highlights
- Dmitry described Finom's differentiation as authentic AI workflows, not AI sprinkled onto existing interfaces.
- The accounting example was concrete: background jobs react to events, prepare preliminary tax reports, ask for approval, and then can file to the government.
- The wider platform vision goes beyond CFO workflows and aims to proactively handle work, monitor cash flow, detect missing items, and flag negative trends.
- Dmitry said the foundation already works and that multiple projects around this vision were being built at the time of the call.
- Org-wise, Finom has platform infrastructure teams plus product engineering domains made of mission-oriented, vertically aligned squads.
- The `EIC4` / `IC4` team was described as the core team building agentic experiences, while the broader platform is expected to expose MCP-based interfaces for connecting new skills.
- Dmitry explicitly did not want a future split where one part of the company builds AI-native experiences and another part only maintains old-school UI surfaces.
- He framed AI engineering as product engineering with extra LLM, prompting, model-integration, and system-stitching expertise.
- He emphasized that productionizing an agent means building a full system, including backend, latency, observability, and reliability.

## Candidate Questions Asked
- What would be an amazing start date, especially considering a potential move to the Netherlands?
- How is the team separated: AI-native developers inside product teams, or an agentic layer that talks to other teams?

## Company Direction
Finom started as a business product platform and is now trying to differentiate through authentic AI experiences. Dmitry framed the goal as more than adding assistants or AI wrappers to traditional interfaces: the company wants to rethink workflows so software can eliminate or automate whole jobs to be done.

The clearest product example was accounting. One product team rebuilt an accounting flow around background jobs and agentic automation. The system reacts to events, prepares preliminary tax reports, asks for user approval, and can then file to the government.

That accounting product became both a shipped product and a broader vision for the platform.

## Agentic Platform Vision
Finom originally called the wider platform vision `IC4`, though Dmitry said the name may change. The idea is to scale agentic workflows across the product platform:

- Proactively reach out to users.
- Do work on the user's behalf.
- Monitor cash flow.
- Alert users when something is missing.
- Warn when trends become negative.
- Make new AI skills easy to connect through MCP-based interfaces.

The message: Finom is treating AI as workflow infrastructure, not just UI decoration.

## Organization Model
Finom's engineering organization has:

- Core platform infrastructure teams that keep the foundation alive.
- Product engineering domains built around missions.
- Vertically aligned product squads.
- An `EIC4` or `IC4` core team focused on the core agentic experiences.

Dmitry pushed back on a hard split between "AI team" and "traditional team." The stated direction is that everyone is a product engineer, with some engineers having stronger AI and LLM expertise.

Historically, at Dmitry's previous company Phenom, AI engineer was a separate craft. At Finom, they are discussing merging that craft into product engineering. AI skill is treated as a flavor of product engineering: knowing how to harness LLMs, prompt, integrate models, and stitch them into coherent products.

## Role Signals
If joining, the likely paths are:

- Work on a product at the bleeding edge of AI-native workflows.
- Join the `IC4` core team building AI agents across the stack.

Dmitry emphasized that productionizing an agent means building a system. The work is not limited to prompt or agent logic; it includes backend systems, latency, observability, reliability, and production engineering foundations.

## Technical Stack
- Primary backend: C# / .NET.
- AI service language: Python.
- Architecture direction: MCP-based interfaces across the platform.
- Interesting mention: Dmitry asked about `DSPy`, which he described as one of the most interesting AI software technologies he had recently found.

The stack signal is practical: C# remains the core backend runtime, while Python is used where it makes sense for LLM-powered services and AI harnesses.

## Strongest Signals
| Area | Signal |
| --- | --- |
| Company direction | Agentic AI workflows across the product suite |
| Role fit | Product engineering with strong AI depth |
| Technical fit | Python plus C#/.NET, MCP-based architecture, interest in DSPy |
| Evaluation lens | Production reliability matters as much as model capability |
| Org model | AI expertise embedded into product engineering, not isolated as research |
| Next step | Dmitry wanted to set up a deeper follow-up call with a colleague |

## Most Useful Takeaways
- Finom cares about production AI engineering more than AI novelty.
- The role is not a detached research role.
- Reliability, observability, and real workflow integration are likely central evaluation criteria.
- The strongest alignment story is agentic systems that are operational, measurable, and production-grade.
- The accounting workflow is the best concrete product example to reference in follow-up conversations.

## Good Follow-Up Angles
- Ask how inter-agent coordination and failure isolation are handled.
- Ask how quality is measured for tax and accounting workflows across countries.
- Ask how embedded the AI-specialist role really is inside product squads.
- Ask how they divide responsibility between the `IC4` core layer and broader product engineering teams.
- Ask where reliability hardening currently constrains rollout.
- Ask how reusable AI capability is shared across teams without slowing product delivery.

## Handoff To The Next Round
Use this round to ground the org and platform narrative. Then move to `../2-central-ai--ivo/README.md` and `../../prep/2-central-ai--ivo-48h-prep-focus.md` for the April 8, 2026 conversation.
