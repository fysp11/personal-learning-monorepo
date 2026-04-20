# Finom Second Interview Prep - Ivo

**Interview date:** Wednesday, April 8, 2026  
**Interviewer:** Ivo  
**Role/context:** One of the co-founders, described by recruiter Samuel as running Finom's `central AI team`  
**Contact:** `ivo@pnlfin.tech`  
**Planned duration:** 45 minutes  

---

## Recommended Re-entry Order

- `IVO-WEB-RESEARCH.md` - external cross-check on Ivo, Finom AI signals, and interview-pattern evidence
- `glassdoor-research.md` - Finom-specific hiring-process and interview-pattern signals
- `../../prep/2-central-ai--ivo-question-drafting-strategy.md` - how to build a deliberate question bank across design, technical, and product angles
- `../../prep/2-central-ai--ivo-simulation-1-founder-org-design.md` - mock for the founder / central-AI / org-design path
- `../../prep/2-central-ai--ivo-simulation-2-ai-accounting-risk.md` - mock for the AI accounting / quality / trust path
- `../../prep/2-central-ai--ivo-48h-prep-focus.md` - compressed final prep note
- `../../prep/2-central-ai--ivo-mental-models.md` - sharpened zoom-in / zoom-out model plus the best decomposition example

## What Changed Since The First Interview

The first useful update is organizational.

From Dmitry's conversation, the picture sounded like Finom wanted AI capabilities to spread throughout product engineering rather than live in a separate silo. From Samuel's recruiter messages, there is also a separate `central AI team` run by Ivo, and Finom is still deciding who the hiring manager for this role will be.

That means this next conversation is not just another technical screen. It is probably also an org-design and mandate-calibration conversation.

## Ivo Background Signals

- Ivo described himself as originally a designer, then head of design, then co-founder of a startup incubator that scaled from about 5 to 120 people and worked with hundreds of startups.
- He spent about five years as CPO at a banking-like startup before co-founding Finom.
- He said he was CTO at Finom for about five years and is now focused on the next zero-to-one AI push while Christian scales the company from one-to-many.
- He said he is "a little bit technical but not super technical", which is why he wanted a later technical interview with one of Finom's leading engineers.

## Conversation-Backed Highlights

- Ivo framed the market shift as moving from software engineers who just write code toward product engineers who can rethink how work gets done.
- He described AI at Finom as three streams: operational excellence, AI inside products, and AI adoption across the company.
- Operational excellence is explicitly measured in hard efficiency terms, including FTE per active customer.
- User-facing AI includes AI Accounting and the broader AI-first product experience.
- AI Accounting has already automated tax work from preparation to submission in Germany, and Finom is moving the pattern to France.
- The product goal is proactive action: not "here is how to issue a card", but issuing the card when the user asks for the outcome.
- Ivo wants AI systems that "go and do stuff" and return with completed work, not passive support assistants.
- Finom separates classic ML from AI: ML covers things like credit/risk scoring; AI covers LLM-based product and workflow systems.
- The AI team is both central and embedded: some people work inside domains, others move across projects.
- The AI team can influence domain processes directly, but adoption is not treated as a mandate; they use internal influence, hackathons, workshops, tools, and enablement.
- Ivo is looking for people who are open-minded, can think differently, know what to do technically, and execute fast.
- He explicitly prefers a small, high-caliber team with good tools over a large average team.
- He is skeptical that Codex, Claude Code, or similar tools automatically make engineers faster; sometimes they do the opposite.

## Candidate Technical Discussion

- You explained the transition from software/data engineering into AI engineering through product delivery, not just model work.
- You connected psychology to AI engineering through communication, prioritization, hallucinations, memory, bias, and human-facing deliverables.
- On LangChain/LangGraph, you positioned LangChain as useful for primitives and LangGraph as better for controllable workflows, while preferring functional APIs over graph-object ceremony when the function of each component needs to stay obvious.
- On AI-generated software, you argued that programming languages exist for humans, and that skipping human-readable representations creates accountability and inspection problems.
- On coding agents and harnesses, you highlighted deterministic guardrails, sandbox limits, and the risk that agents do wrong things faster.
- On RAG and Karpathy-style ideas, you treated new research patterns as useful signals, but not strategy by themselves.
- On choosing agent architecture, you described isolating optimizable components, separating workflow from agentic uncertainty, and using a zoom-in / zoom-out model.
- Your best technical framing was: decompose workflows until controllable pieces become reliable, leave bounded judgment to AI, and connect local AI capability back to user and company value.

## Candidate Fit Signals From Ivo's Questions

- Ivo probed whether you can think about AI beyond implementation details.
- He tested whether you can reason philosophically but still stay practical.
- He cared whether you can influence people and drive adoption without authority.
- He asked about comfort working with direct communication styles, especially given Finom's Russian-heavy engineering legacy.
- Your strongest fit answers were listening, translating pain into practical solutions, influencing through small context-aware steps, and being comfortable with direct cultures from Dutch-market experience.

## Next-Step Outcome

- Ivo proposed a technical interview with one of Finom's leading engineers.
- He said the usual flow is recruiter, Ivo, technical interview, then decision, with possible extra team meetings if needed.
- He wanted the next technical interview to be creative, not just standard question transfer.

## Strongest Refinements

These are the most important refinements after the Ivo conversation:

- Ivo is explicitly pushing `AI-native` and `AI-first` product/workflow design, not just internal enablement
- He repeatedly frames the AI mission in hard operational terms: `replace people`, `eliminate tax advisors`, reduce `FTE per active customer`
- He described three broad AI directions, with one aimed at operational excellence across internal teams and another aimed at user-facing AI products
- He said Finom already automated the tax workflow `from preparation to submission` in `Germany` and is moving to `France`
- He wants a system that is `proactive`, not a support chatbot that only answers and redirects
- He referenced the desired UX as closer to an agent that `goes and does stuff`, then comes back
- He explicitly wants a `small`, high-caliber team with `good salaries`, `good tools`, and people who execute fast with judgment
- He is skeptical of shallow AI-tool usage: using Codex or Claude does not automatically make people faster
- He said he is `a little bit technical but not super technical`, which matters for how to communicate with him
- He described the next round as a technical interview with one of the engineers, and said he wanted it to be `creative`, not just standard questions

## What Samuel's Messages Tell Us

Based on the screenshots:
- Samuel told Finom he is keen to continue the conversation with you.
- Finom is still deciding who the hiring manager for the role will be.
- Ivo runs a separate `central AI team`.
- Samuel pitched you to Ivo and Ivo was keen to meet.
- Ivo was traveling until Wednesday, so the interview was scheduled for Wednesday or Thursday.
- A booking link was sent for a 45-minute conversation.

## Best Interpretation

This interview is likely testing some combination of:
- whether you fit a more central AI mandate
- whether you can work across multiple product surfaces rather than one narrow squad
- whether your background is strong enough for a founder-level AI conversation
- whether you should report into a central AI group versus an embedded product engineering team

## What Ivo Likely Cares About

Because he is a co-founder and apparently runs central AI, expect him to care less about isolated implementation details and more about:
- where AI can create real leverage across the business
- what should be centralized versus embedded
- how to avoid fragmented AI efforts across teams
- how quality, governance, and reuse should work
- whether you can operate with broad product and business context, not just engineering tickets
- whether you have enough judgment to choose durable patterns instead of trendy ones

Additional stronger interpretations:
- whether you are comfortable with aggressive automation, not just assistive AI
- whether you can build systems that `act`, not just classify or answer
- whether you can combine imagination with operational discipline
- whether you can thrive in a small, opinionated, direct team

## Best Positioning For This Conversation

Position yourself as:

Senior product-minded AI systems engineer who can help turn AI into reusable, production-grade business capability across multiple workflows.

That is slightly different from the Dmitry angle.

With Dmitry, the strongest emphasis was engineering depth, agent productionization, and embedded product work. With Ivo, you should keep that technical grounding, but elevate the frame:
- reusable AI patterns
- cross-team leverage
- quality systems
- platform thinking
- which work should be centralized versus left to product teams

Add one more layer:
- proactive workflow execution over passive copilots
- operational automation with hard business impact
- strong judgment while using AI coding tools

## Strongest Angles To Lean On

### 1. Production AI, not demos
- You ship AI systems that work under operational constraints.
- You care about latency, observability, evaluation, fallback behavior, and measurable outcomes.

### 2. Reusable patterns across workflows
- Your experience is useful not only for one feature, but for repeated workflow classes:
- document-heavy processes
- agent handoffs
- retrieval-backed assistants
- evaluation pipelines
- operational automation

### 3. Judgment under ambiguity
- You do not treat every new model or framework as strategy.
- You choose what is worth productizing and what should remain experimental.

### 4. Business-critical AI
- Your best work sits in workflows where correctness matters and failures are costly.
- That maps well to finance, accounting, compliance, and operational support.

### 5. Proactive systems, not assistant UX
- Ivo clearly wants AI that can `do the work`, not just answer questions.
- Your examples should emphasize action loops, approvals, confidence thresholds, and observable completion.

### 6. Small-team leverage
- He strongly prefers a small elite team over a large average one.
- Show that you increase leverage, reduce coordination cost, and use tools well without creating noise.

## Topics To Prepare For

### Central AI team vs product squads
Be ready to discuss:
- what capabilities should be centralized
- what should stay embedded in product teams
- how to avoid duplicated prompting, eval, and tooling work
- how platform teams can enable product teams without becoming a bottleneck

### AI roadmap leverage
Be ready to speak concretely about:
- which workflow categories are best for agentic systems
- what prerequisites matter before scaling them
- how to identify strong early use cases

### Proactive product behavior
Be ready to discuss:
- when a workflow should act automatically versus propose
- what approval surfaces should exist
- how to avoid fake autonomy that still pushes work back to the user
- what makes an AI experience meaningfully more proactive than chat

### Evaluation and governance
This is likely a major founder-level concern.

Be ready to discuss:
- offline evals
- runtime monitoring
- confidence thresholds
- human review flows
- rollback / safe-failure design
- where you would insist on stronger controls in financial workflows

### Build vs buy
A co-founder may care more explicitly about this tradeoff.

Be ready to explain:
- when you prefer external models or tooling
- when you would build internal harnesses and control layers
- where proprietary workflow knowledge creates defensibility

## Likely Questions

- Why Finom specifically, beyond "AI role in fintech"?
- If you were dropped into a central AI team, where would you start?
- What AI capabilities should be shared across the company?
- What should not be centralized?
- How do you know an agentic workflow is ready for production?
- What are the biggest failure modes in financial/operational AI?
- How would you structure evaluation for accounting or finance workflows?
- What makes a central AI team useful rather than decorative?
- How do you work with product teams that want to move fast but lack AI rigor?
- How would you design something proactive instead of just assistive?
- How do you make sure AI coding tools actually increase speed and not the opposite?
- Can you operate in a small team where communication is direct and expectations are high?

## Best Answers To Have Ready

### Why Finom
"What pulls me to Finom is that you are applying AI to workflows where correctness matters and where the outcome is operational, not cosmetic. I like that because my strongest work has been in production systems where you need agents, retrieval, evaluation, and observability to work together, not just impressive demos."

### How you would add value in a central AI team
"I would focus on reusable capability layers first: shared evaluation patterns, observability, retrieval/tooling conventions, and a few high-value workflow templates. That gives product teams leverage without forcing every team to rediscover the same failure modes independently."

### Centralized vs embedded
"I would centralize the hard reusable parts, not the entire product decision process. Shared infrastructure, eval patterns, safety controls, and good defaults benefit from central ownership. Domain-specific workflow design and user experience should stay close to product teams."

### Proactive AI
"The bar for a strong AI workflow is not that it can answer a question. The bar is that it can complete meaningful work safely. That means clear task boundaries, deterministic control over policy-heavy parts, confidence-aware routing, and human approval where failure cost is high."

## Good Questions To Ask Ivo

- How do you define the mandate of the central AI team today?
- What are the biggest problems you want that team to solve in the next 6 to 12 months?
- Where do you see the boundary between central AI and product engineering squads?
- What has already worked well, and where has the current setup created friction?
- Are you optimizing more for speed of experimentation right now, or for reusable foundations and quality?
- If this role joined, what would be the first high-leverage area to own?
- Is the hiring manager question still open because the role itself is evolving?

## What To Avoid

- Do not over-focus on framework names.
- Do not sound like you only want to build a centralized AI platform detached from users.
- Do not contradict Dmitry's view; instead, reconcile it:
- central AI can provide leverage and standards
- product squads still own domain workflows and outcomes
- do not overclaim fintech depth

## Practical Reminder

Use absolute dates in your own notes and messages:
- the interview is on **Wednesday, April 8, 2026**

That avoids ambiguity around `8/4`.
