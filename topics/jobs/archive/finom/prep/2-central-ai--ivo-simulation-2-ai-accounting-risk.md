# Finom Interview Simulation 2

## Direction

`AI accounting / risk / quality-in-production`

This is the simulation where Ivo uses accounting and operational AI as the concrete lens. The conversation is less about org charts and more about whether you can build trustworthy AI inside workflows where mistakes are expensive.

Why this direction is plausible:
- Finom's public accounting product is explicitly AI-enabled
- the public role covers accounting, fraud/risk, documents, onboarding, and customer workflows
- Finom publicly emphasizes human validation and AI Act readiness
- Ivo has publicly described AI as proactive financial assistance inside SME workflows

Cross-check sources:
- [Finom accounting product page](https://finom.co/en-de/accounting/)
- [General Catalyst - Senior AI Engineer at Finom](https://jobs.generalcatalyst.com/companies/finom/jobs/71195568-senior-ai-engineer)
- [Mobile Transaction interview with Ivo Dimitrov](https://es.mobiletransaction.org/entrevista-ivo-dimitrov-finom/)

## What he is likely testing

- Whether you understand that "mostly right" is not enough in accounting-adjacent flows
- Whether you know how to structure approval, review, and rollback
- Whether you can define evaluation beyond prompt quality
- Whether you can think in rollout stages rather than all-or-nothing automation
- Whether you sound calm and rigorous in a correctness-sensitive domain

## How to answer in this simulation

- Use a workflow lens, not a model lens
- Break the system into stages: ingest, classify, reconcile, propose action, review, finalize, audit
- Talk about confidence thresholds, failure taxonomies, human review points, and auditability
- Make it clear where you would deliberately stop short of autonomy

## 45-minute mock flow

### Opening

`Ivo:` We are serious about AI accounting. What do you think makes that hard in practice?

`Strong shape of answer:`
The hard part is not generating an answer. The hard part is making every step safe enough for a real financial workflow. You need reliable extraction, correct linkage to transactions and context, explicit uncertainty handling, approval rails, and a clean audit trail. In this kind of system, the workflow contract matters more than the model demo.

### Workflow decomposition

`Ivo:` Okay. How would you decompose an AI accounting workflow?

`Strong shape of answer:`
I would split it into stages:
- document intake and normalization
- extraction and classification
- reconciliation against transactions and historical patterns
- proposal generation for categorization / tax treatment
- confidence scoring and exception routing
- human approval for ambiguous or high-consequence cases
- final write-back and audit logging

That decomposition matters because each stage can have different failure modes, different metrics, and different escalation thresholds.

### Evaluation

`Ivo:` How would you evaluate such a system?

`Strong shape of answer:`
I would use at least three layers:
- offline evals on labeled or adjudicated cases
- workflow metrics in production, like approval rate, override rate, exception rate, time saved, and rework
- failure review for edge cases, especially costly false confidence

I would also separate component metrics from end-to-end workflow success, because a good extractor can still produce a bad operational outcome if reconciliation or routing is weak.

### Confidence thresholds

`Ivo:` What do confidence thresholds actually mean here?

`Strong shape of answer:`
Not a single model score. A workflow confidence policy.

For example:
- low-risk, high-repeat cases can auto-propose and auto-complete under tighter known conditions
- medium-confidence cases should draft and request approval
- high-ambiguity or high-impact cases should route to human review immediately

The threshold logic should combine model certainty, rule checks, business context, document quality, and downstream consequence.

### Human review

`Ivo:` Some teams add human review everywhere and call it safe. Is that enough?

`Strong shape of answer:`
No. Human review is only useful if the system routes the right cases, shows the reviewer the right evidence, and learns from reviewer corrections. Otherwise it just hides poor automation behind manual cleanup.

I would want:
- reason codes for why a case was escalated
- evidence bundles for the reviewer
- structured correction capture
- a feedback loop into evals and routing logic

### Rollout strategy

`Ivo:` How would you roll something like this out without creating trust issues?

`Strong shape of answer:`
I would stage it:
- shadow mode first
- draft-only recommendations second
- approval-gated actions third
- selective automation last, only for the most stable case classes

Trust is easier to build when the system earns more responsibility over time instead of claiming it upfront.

### Failure modes

`Ivo:` What failure modes worry you most?

`Strong shape of answer:`
- false confidence on messy or unusual documents
- silent mismatch between document extraction and transaction context
- brittle handling of country- or tax-specific edge cases
- automation that looks correct at the component level but creates downstream accounting errors
- weak observability where you only discover problems from customer pain

If pressed, add:
- drift in vendor/model behavior
- policy changes not reflected in prompts, rules, or reviewer guidance

### Build vs buy, concretely

`Ivo:` Would you build this mostly on external models?

`Strong shape of answer:`
I would treat foundation models as components, not the product. External models are fine for extraction, reasoning, or drafting if they meet quality and cost targets. But workflow control, auditability, policy enforcement, exception handling, and evaluation logic are where the real system value sits. That is the layer I would want strong internal ownership over.

### Your experience bridge

`Ivo:` You do not come from deep fintech. Why should I trust your judgment here?

`Strong shape of answer:`
I would not claim domain mastery I do not have. The reason my background is relevant is that I have worked on correctness-sensitive AI systems where you cannot rely on demo quality. The transferable part is how to structure evaluation, routing, observability, and failure handling around high-cost workflows. I would pair that discipline with Finom's domain experts rather than pretending domain nuance can be abstracted away.

### Practical scenario

`Ivo:` Imagine the system drafts a tax-related record that is correct 96 percent of the time. Is that good enough?

`Strong shape of answer:`
Not as a single number. I would ask:
- 96 percent on what distribution?
- what is the cost of the wrong 4 percent?
- are the failures concentrated in predictable edge cases?
- is this a draft-for-approval stage or an autonomous action stage?

For a draft workflow with strong routing and reviewer context, maybe. For autonomous filing, almost certainly not yet.

### Close

`Ivo:` How would you know this product is ready to take on more autonomy?

`Strong shape of answer:`
When three things are true:
- stable performance across real case classes, not just curated eval sets
- clear understanding of failure clusters and containment paths
- product and operations teams trust the review, rollback, and audit mechanisms enough to expand scope intentionally

Autonomy should be earned per workflow class, not declared globally.

## Reverse questions to ask Ivo in this version

- In AI accounting today, where do you most want stronger confidence: extraction, reconciliation, categorization, approval flow, or end-to-end orchestration?
- Which failure mode worries you most right now: wrong outputs, low adoption, excessive manual review, or weak observability?
- Where does Finom currently draw the line between recommendation, approval-gated action, and full automation?
- How do you think about human validation as a product feature versus an operational backstop?
- Which accounting or financial workflow would you most want this role to improve first?

## Red flags to avoid

- talking as if a good benchmark score is enough
- treating human review as a generic cure-all
- assuming one global confidence score solves workflow safety
- sounding allergic to staged rollout and approval gates
- overclaiming policy or tax-domain expertise

## One-sentence thesis to remember

`In accounting AI, the product is not the model output; the product is a controlled workflow that knows when to act, when to ask, and when to stop.`
