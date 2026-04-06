# Finom Interview Simulation 1

## Direction

`Founder / org-design / central-AI leverage`

This is the simulation where Ivo behaves less like a hiring manager for one feature team and more like a founder deciding whether you can help shape Finom's AI operating model.

Why this direction is plausible:
- the public role explicitly spans multiple domains and asks for cross-team AI reuse
- public signals suggest Ivo moved from CPO into a broader venture / AI scope
- public interviews suggest he cares about SME workflows, usability, and product leverage

Cross-check sources:
- [General Catalyst - Senior AI Engineer at Finom](https://jobs.generalcatalyst.com/companies/finom/jobs/71195568-senior-ai-engineer)
- [TuneIn podcast summary on Ivo's CPO -> Chief Venture Officer shift](https://tunein.com/podcasts/Business--Economics-Podcasts/The-Melting-Pot-with-Dominic-Monkhouse-p1610500/)
- [Mobile Transaction interview with Ivo Dimitrov](https://es.mobiletransaction.org/entrevista-ivo-dimitrov-finom/)

## What he is likely testing

- Whether you can think above one workflow
- Whether you know what should be centralized vs embedded
- Whether you default to leverage and standards without becoming a platform zealot
- Whether your judgment sounds durable rather than trend-driven
- Whether you can talk to a founder in terms of business leverage, not just tooling

## How to answer in this simulation

- Keep the altitude high first, then ground it in one concrete example
- Talk in capability layers: evals, observability, workflow patterns, retrieval/tooling conventions, approval rails
- Separate `shared primitives` from `product-specific workflow ownership`
- Avoid naming frameworks unless they clarify a tradeoff

## 45-minute mock flow

### Opening

`Ivo:` Walk me through your background and why Finom is interesting to you right now.

`Strong shape of answer:`
I build production AI systems for workflows where correctness matters and where the outcome is operational, not cosmetic. Finom is interesting because the public direction is not "add a chatbot," it is "embed AI into financial operations across accounting, support, onboarding, and risk-sensitive workflows." That is the kind of environment where product judgment, evaluation discipline, and reusable capability design actually matter.

### Central mandate

`Ivo:` If you joined a central AI team here, what should that team actually own?

`Strong shape of answer:`
I would centralize the hard reusable layers:
- evaluation patterns
- observability and runtime quality instrumentation
- workflow and tool-use conventions
- shared retrieval/document primitives
- guardrails, approval rails, and rollout defaults

I would not centralize domain workflow design, user interaction details, or product prioritization. Product squads should still own the workflow outcome. Central AI should reduce repeated mistakes and raise the floor without becoming the bottleneck.

`What he may challenge next:`
- How do you stop central AI from slowing everyone down?
- How do you decide when a team can bypass the shared stack?

### Central AI vs platform theater

`Ivo:` Many central AI teams become decorative. How do you make one actually useful?

`Strong shape of answer:`
It needs a measurable service model. I would expect the team to do three things visibly:
- ship at least one direct high-impact workflow itself
- build reusable primitives that other teams adopt because they help, not because they are mandated
- create a quality bar that prevents obvious regressions in risky workflows

If a central team only publishes guidelines and wrappers, it will lose credibility. It needs operating leverage and shipping credibility.

### First 90 days

`Ivo:` Say you start next month. Where do you begin?

`Strong shape of answer:`
I would do four things in parallel:
- map live AI and automation efforts across teams
- identify where duplicate work or duplicate failure modes already exist
- pick one high-leverage workflow to ship or stabilize
- establish a minimal shared quality layer: eval definitions, runtime traces, failure taxonomy

The goal in the first 90 days is not to build a full platform. It is to get one visible win while creating the minimum reusable structure that prevents the next three teams from reinventing the same problems.

### Build vs buy

`Ivo:` How do you think about external tools and models versus internal systems?

`Strong shape of answer:`
I would buy or use external components where the capability is commoditized and the value is mostly in speed. I would build internally around orchestration, evaluation, workflow state, domain-specific policy, approval handling, and the interfaces between AI and business operations. That is where company-specific knowledge becomes defensible and where switching costs matter.

`Bad answer pattern:`
"We should build our own stack for control."

Why bad:
- too ideological
- ignores speed
- sounds expensive before evidence

### Picking workflows

`Ivo:` Which categories of workflow are best suited for agentic systems here?

`Strong shape of answer:`
I would prioritize workflows with:
- repeated operator effort
- clear artifacts and tools
- partial automability before full autonomy
- meaningful business upside if latency and correctness are acceptable

At Finom that could plausibly include document understanding, reconciliation assistance, support resolution drafting, onboarding prep, and some accounting preparation flows. I would avoid starting with fully autonomous high-consequence decisions where the failure cost is high and the policy surface is still unstable.

### Handling product teams

`Ivo:` What if product teams say central AI is slowing them down?

`Strong shape of answer:`
Then the central team needs to earn the right to be involved. My bias would be:
- lightweight defaults
- paved roads, not gatekeeping
- opt-in where possible, mandatory rails only where failure cost is truly high

If teams are bypassing the shared path, I would treat that as a product signal. Either the central tooling is too heavy or the team's workflow genuinely needs local ownership.

### Probing your execution

`Ivo:` Tell me about a time you turned an ambiguous AI problem into something repeatable across multiple use cases.

`What your story needs to prove:`
- problem ambiguity
- concrete design choices
- one shared layer that reduced repeated work
- metrics or operational impact
- where you chose not to over-generalize

### Founder-level closer

`Ivo:` What would make this role a success or failure in 12 months?

`Strong shape of answer:`
Success:
- at least one major production AI capability with visible business value
- evidence that multiple teams can ship faster and safer because shared patterns exist
- better failure visibility and cleaner rollout discipline

Failure:
- lots of prototypes, little adoption
- vague platform work with no direct business win
- inconsistent quality across teams
- central AI becoming a second approval bureaucracy

## Reverse questions to ask Ivo in this version

- How do you define the mandate of the central AI team today?
- Which AI decisions do you want centralized because they create leverage, and which do you want left close to product squads?
- Where has the current setup already created duplicated effort or repeated failure modes?
- Do you expect this role to deliver a workflow first, or shape shared capability first?
- What would convince you in six months that central AI is genuinely helping the company?

## Red flags to avoid

- talking like you want to build a detached AI platform first
- making everything sound like an agent problem
- over-indexing on model novelty
- sounding indifferent to product-team autonomy
- giving centralization answers without operational examples

## One-sentence thesis to remember

`Central AI should own the reusable hard parts and earn adoption through shipped value, while product teams stay closest to workflow outcomes and user reality.`
