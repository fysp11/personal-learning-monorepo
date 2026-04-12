# Finom Interview 3 - Preparation Plan

Saved: 2026-04-09

## Goal

Prepare for the `90-minute technical interview` with the `Senior AI Engineer`:

- `30 min` technical questioning
- `60 min` live problem-solving / coding with `Claude Code` or `Codex`

This is not a manual coding round. It is a `technical judgment + agentic execution` round.

Refined from the `2026-04-09` source record and follow-up context:

- the source record artifacts remained stable through `2026-04-09T21:49:07Z` with `no-whisper-processes-detected`, so they are safe to treat as grounded input
- user-confirmed Interview 3 interviewer is `Viktar Adynets`
- he wants the round to be `creative`, not a standard question drill
- he explicitly cares whether `Codex` / `Claude` make people faster or slower in practice
- he described the org as three streams: `operational excellence`, `AI-first product work`, and `adoption`
- he framed success in hard business terms: replacing manual work and lowering `FTE per active customer`
- he implicitly wants `product engineers`, not just code producers
- he wants workflow behavior closer to `do the task, then come back`, not a passive assistant pattern
- he appears to prefer a `small`, high-caliber, direct team over heavier process
- he described `adoption` as an explicit workstream with a dedicated owner, internal workshops, and practical AI-tool rollout across the company
- he gave a concrete domain anchor: tax workflow automation already shipped in `Germany`, with movement toward `France`
- use the mental model `core > layers > product`, or `central > integration > embed(domain)`

---

## North Star

Prove three things:

1. `You think clearly about production AI systems`
2. `You can decompose ambiguous workflows into controllable pieces`
3. `You can use an AI coding agent well without losing rigor`

Add the org/interviewer read from Interview 2:

4. `You understand how reusable AI patterns meet domain delivery`
5. `You can operate in a small, direct, high-judgment team`
6. `You can turn AI ambition into operational leverage, not just an interesting demo`
7. `You can make AI adoption practical instead of performative`

---

## What They Are Likely Testing

### 1. Technical depth

- agent orchestration
- evals and observability
- confidence routing
- deterministic vs AI boundaries
- failure modes in financial workflows
- API / tool / service integration
- proactive workflow execution, not passive assistant behavior

### 2. Working style

- how you reason under ambiguity
- whether you can keep structure while moving fast
- whether you can guide Codex / Claude instead of delegating your brain away
- whether you verify outputs instead of trusting them blindly
- whether your use of AI tools produces actual speed and clarity
- whether you behave like a `product engineer`: execution plus judgment plus influence
- whether you can operate well in a direct, low-ceremony team without hiding behind process
- whether you can influence adoption without turning into a process bottleneck

### 3. Product judgment

- can you pick the right slice of automation
- can you avoid over-agentic designs
- can you balance speed, safety, and user value
- can you decide what should stay with a central AI pattern versus what belongs in a domain workflow
- can you connect a design choice to operational leverage, adoption, or reduced human effort
- can you make the system complete meaningful work before handing a result back to the user
- can you explain how a good pattern spreads across teams in a way engineers will actually use
- can you tie the design back to measurable workflow compression instead of just elegance
- can you manage the relationship layer across central, integration, and embedded teams so adoption scales

---

## Interview Thesis

Use this frame throughout:

> I build production-grade AI systems for workflow-heavy, correctness-sensitive problems. I decompose black-box tasks into observable joints, keep policy deterministic, use AI where ambiguity is real, and ship with evals, routing, and clear rollback paths.

Shorter version:

> AI for ambiguity. Software for policy. Workflow quality over model cleverness.

Add this Interview 3 emphasis:

> Real leverage means the workflow gets faster and more autonomous without becoming opaque or unsafe.

And this Finom-specific emphasis from Ivo:

> The bar is not "interesting AI." The bar is fewer manual steps, better product behavior, and workflows that can actually replace low-leverage human effort.

---

## Part 1 - 30 Minute Technical Questions

### Questions to expect

- How would you design an expense categorization workflow for German SMBs?
- What should be deterministic vs LLM-based?
- How would you evaluate a financial AI workflow?
- How do you decide between a single agent and a staged workflow?
- How do you handle low-confidence outputs?
- What observability would you add?
- How would you integrate AI into an existing C# / Python system?
- How would you support multiple EU markets?
- How would you extend a `Germany`-first tax workflow toward `France` without turning market rules into prompt glue?
- How would you make the workflow proactive without removing the right approval gates?
- Why do many teams get slower after adopting Codex / Claude, and how would you avoid that?
- How do you decide when to automate the work itself versus just helping a human do it faster?
- How would you design something that product teams can adopt instead of bypass?
- How would you make the system `go do the task and come back` without hiding risky policy decisions inside prompts?
- How would you help a team adopt AI tooling without mandating shallow usage?
- What would make a central AI team useful instead of decorative?
- How would you know the workflow is actually reducing manual work or `FTE per active customer` rather than just moving work around?

### Answer shape

Use the same answer skeleton every time:

1. `Frame the problem`
2. `State the design choice`
3. `Explain the tradeoff`
4. `Name the failure mode`
5. `Describe the control / metric`

Example:

> For transaction categorization, I would separate receipt matching, feature extraction, category proposal, VAT rules, and booking. The category proposal can use AI because merchant text and document content are ambiguous. VAT logic should be deterministic because the failure cost is compliance-related. Low-confidence cases should route to proposal mode, not auto-booking. I would measure approval rate, override rate, and severe-error rate by market.

### Technical topics to rehearse

- `workflow decomposition`
- `confidence propagation`
- `human review design`
- `completed-workflow UX`, not just chat UX
- `severity-weighted evals`
- `idempotency`
- `event-driven architecture`
- `agent/tool boundary`
- `build vs buy`
- `cross-market localization`
- `MCP / tool interface design`
- `central AI pattern -> domain delivery translation`
- `AI team vs ML team separation`
- `ops leverage metrics`
- `adoption / enablement mechanics`
- `team-level AI tool rollout`
- `Germany-first workflow patterns that need to generalize toward France / multi-market rollout`
- `how to keep market-specific policy deterministic while reusing the same workflow shape`

---

## Part 2 - 60 Minute Live Problem Solving

### Most likely exercise shapes

1. `Design + implement a workflow skeleton`
For example:
- categorize transactions
- reconcile receipts
- propose tax handling
- route risky cases to human review

2. `Improve an existing code path`
For example:
- add confidence scoring
- add observability
- add fallback routing
- fix flaky behavior in an agent loop

3. `Build a minimal service / tool`
For example:
- tool-calling wrapper
- structured-output parser
- workflow orchestrator
- evaluation harness

4. `Refactor a fuzzy agent design into controllable stages`
For example:
- replace one large prompt with explicit stage contracts
- move tax / policy logic out of model instructions
- add proposal vs action modes

### What they are evaluating in the live part

- how you scope
- how you prompt the coding agent
- whether you inspect outputs critically
- whether you choose the right abstraction level
- whether you verify behavior before claiming done
- whether you can keep the exercise creative without letting the design become fuzzy
- whether you naturally build toward something a product team could ship and trust
- whether your implementation style would help a small team move faster instead of adding review burden

---

## Live Round Strategy

### First 5 minutes

Do not rush into code.

Say something like:

> Before I touch implementation, I want to define the workflow boundary, success condition, and what stays deterministic versus AI-driven.

If the task is open-ended, add:

> I also want to decide what should be proactive versus proposal-only, because that changes the control surface and the failure budget.

Then force clarity on:

- input
- output
- failure modes
- confidence / fallback path
- what can be mocked
- what is allowed to act automatically
- what must remain proposal-only in v1
- what business or operator metric this design should improve

### During implementation

Prefer:

- typed interfaces
- explicit stage boundaries
- small orchestrator functions
- mockable AI/tool functions
- one obvious verification path
- a flow that ends in a concrete action/result state, not only a suggestion state

Avoid:

- giant monolithic agent function
- unnecessary frameworks
- premature optimization
- vague "the model will decide" logic
- fake autonomy that still hides critical policy decisions inside prompts

### While using Codex / Claude

Good behavior:

- give precise instructions
- constrain output shape
- request small steps
- inspect generated code
- correct bad assumptions fast
- use the tool to compress implementation time, not to outsource the core reasoning
- keep proving that the tool is reducing work, not generating extra cleanup

Bad behavior:

- dumping the whole problem into the agent
- accepting first output without reading
- letting the agent invent architecture silently
- generating too much code because the tool makes it easy

The meta-signal they want:

> This person uses AI as a force multiplier, not as a substitute for engineering judgment.

More Finom-specific:

> This person could help a small team work better with AI tomorrow, not just talk about AI well in an interview.

---

## Coding Preferences For The Round

Default to these patterns:

- `clear contracts first`
- `deterministic control layer`
- `AI isolated behind an interface`
- `confidence-aware routing`
- `trace / log object for observability`
- `simple testable functions`

If asked to choose between options:

- choose `staged workflow` over `single opaque agent`
- choose `proposal mode` over `full autonomy`
- choose `typed outputs` over raw text parsing
- choose `few reliable components` over a clever architecture
- choose `earned autonomy by stage` over claiming the whole workflow is autonomous
- choose `clear operator surface` over hidden prompt magic
- choose `measurable operational gain` over technically impressive complexity

---

## Best Artifacts To Rehearse Against

Use these before the interview:

- [accounting-mas-pipeline.ts](topics/jobs/finom/code/accounting-mas-pipeline.ts)
- [README.md](/Users/fysp/personal/learning/topics/jobs/finom/code/README.md)
- [technical-deep-dive.md](/Users/fysp/personal/learning/topics/jobs/finom/insights/technical-deep-dive.md)
- [2-central-ai--ivo-story-bank.md](/Users/fysp/personal/learning/topics/jobs/finom/prep/2-central-ai--ivo-story-bank.md)
- [senior-ai-engineer-match-analysis.md](/Users/fysp/personal/learning/topics/jobs/finom/application/senior-ai-engineer-match-analysis.md)

---

## Practice Drills

### Drill 1 - 15 min

Explain out loud:

`Design transaction categorization for Finom in Germany`

Must include:

- AI vs deterministic split
- confidence routing
- auditability
- market localization

### Drill 2 - 20 min

Implement from scratch:

`A tiny orchestrator with 3 stages and low-confidence escalation`

Must include:

- typed input/output
- stage trace
- escalation branch
- one stage that is explicitly proposal-only

### Drill 3 - 10 min

Answer verbally:

`Why not just use one strong model end-to-end?`

Target answer:

> Because high-stakes workflows need local failure visibility, deterministic control over policy, and selective human escalation. A single end-to-end model can look elegant, but it hides where errors come from and makes safe rollout harder.

### Drill 4 - 10 min

Practice using Codex with:

`Implement a confidence-based routing layer around an agent response`

Focus on:

- prompt precision
- reviewing generated code
- asking for tests or verification
- rejecting unnecessary abstractions

### Drill 5 - 10 min

Answer verbally:

`How should a central AI team help without becoming a bottleneck?`

Target answer:

> I would centralize the reusable hard parts: eval patterns, orchestration conventions, safety controls, shared tooling, and a few proven workflow templates. I would not centralize every product decision. Domain teams should still own user outcomes, but they should not have to rediscover the same failure modes from scratch.

### Drill 6 - 10 min

Answer verbally:

`What is the difference between an AI team and an ML team here?`

Target answer:

> I would treat classic ML as prediction and optimization systems with their own lifecycle, while the AI team focuses on LLM-driven workflow execution, orchestration, tool use, and operator trust. The interfaces overlap, but the engineering patterns, risks, and product integration shape are different.

### Drill 7 - 10 min

Answer verbally:

`When should Finom automate the work instead of just assisting the user?`

Target answer:

> I would automate only when the task boundary is clear, the failure cost is bounded, the policy-heavy parts are deterministic, and the approval or rollback path is obvious. Otherwise I would start with proposal mode, measure overrides, and earn autonomy step by step.

### Drill 8 - 10 min

Answer verbally:

`How do you make a good AI pattern actually get adopted by product teams?`

Target answer:

> Adoption is not a memo, it is a product. I would make the reusable path faster than the local workaround: good defaults, observability out of the box, clear interfaces, and one or two proven workflow templates that already solve a painful problem.

### Drill 9 - 10 min

Answer verbally:

`Why do AI coding tools sometimes make teams slower, and how would you prevent that here?`

Target answer:

> Because they can increase output volume faster than they increase judgment. I would keep the problem scoped, define interfaces first, ask the tool for small verifiable steps, and insist on a short proof path before moving on. The goal is not more generated code, it is faster convergence to a controllable solution.

---

## Likely Strong Questions To Ask Them

Ask only 1-2, not a long list.

- In the live round, are you optimizing more for architecture judgment or for implementation speed?
- In your current AI workflows, where do you most often see the boundary between deterministic control and model judgment break down?
- How much of the team’s current work is greenfield orchestration versus hardening existing production paths?
- Where do strong ideas usually come from today: the central AI group, embedded teams, or both together?
- Where do AI adoption efforts break today: tooling quality, workflow fit, or engineering habits?

---

## Red Flags To Avoid

- sounding framework-first
- overusing the word `agentic`
- letting the coding tool lead the design
- overclaiming fintech expertise
- proposing LLMs for policy-bound tax logic
- skipping verification because "the code looks fine"
- sounding like centralization is the answer to everything
- confusing proactive automation with unsafe hidden autonomy
- sounding excited about AI without connecting it to operational leverage

---

## Day-Before Plan

### 1. Rehearse the thesis

Be able to say your core technical philosophy in `30 seconds`.

### 2. Re-run one small implementation drill

Not a huge session. One short, clean exercise.

### 3. Revisit the MAS example

You want the architecture in working memory:

- stage boundaries
- confidence propagation
- escalation
- traceability

### 4. Prepare your environment

- Codex / Claude accessible
- terminal shortcuts ready
- no auth surprises
- know how to explain while coding

---

## Last-Minute Card

If you blank during the round, return to this:

> First define the workflow boundary. Then separate ambiguity from policy. Keep AI on messy judgment, keep deterministic systems on control and compliance, add confidence-aware routing, and verify with observable outputs before calling it done.

---

## Success Condition

This round is successful if they leave with this impression:

> He is not just good at AI. He is good at building AI systems that can survive production reality.
