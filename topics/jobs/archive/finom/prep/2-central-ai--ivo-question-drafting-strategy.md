# Finom Interview 2 - Question Drafting Strategy

Saved: 2026-04-06

## Bottom line

Do not draft practice questions by topic alone.

Draft them by decision axis.

The strongest public signals suggest Ivo is likely to care about:
- orchestration over raw model-building
- proactive workflows over passive chat
- trust and control in high-stakes domains
- translation from business ambiguity to working AI systems
- leverage across teams, not just one feature

That means the right prep is:

1. Pick the core decisions he is likely to care about.
2. For each decision, draft:
   - one `design` question
   - one `technical` question
   - one `product` question
3. Add one hostile follow-up to each.
4. Rehearse each answer in both `60 seconds` and `3 minutes`.

That gives you structure instead of gut feel.

## The 5 decision axes

### 1. Centralize vs embed

Question behind the question:
- what belongs to central AI
- what stays with product squads
- how central AI creates leverage without becoming a bottleneck

### 2. Trust and control

Question behind the question:
- where do you allow autonomy
- where do you require approval
- where should automation stop entirely

### 3. Orchestration vs model cleverness

Question behind the question:
- what do you buy
- what do you build
- where is the defensible layer

### 4. Signal vs noise

Question behind the question:
- which proactive actions are actually useful
- which alerts create spam
- how do you know an AI system is helping rather than distracting

### 5. Business problem to working system

Question behind the question:
- can you turn an ambiguous workflow into a scoped, measurable AI product

## Drafting formula

For each axis, draft questions using this pattern:

- `Design`: how would you structure the system, module, or workflow?
- `Technical`: what mechanisms, metrics, safeguards, or tradeoffs would you use?
- `Product`: how would you know this is useful, trusted, and worth expanding?
- `Pushback`: what is the hardest objection or failure mode?

This produces a compact but serious bank:
- `5 axes x 3 core questions = 15 questions`
- plus `15 follow-ups`

## Example question bank skeleton

### Axis 1: Centralize vs embed

- `Design`: How would you decide what belongs in a central AI layer versus a product squad when creating a new accounting module?
- `Technical`: What shared primitives would you centralize first: evals, observability, retrieval, routing, approval rails, or something else?
- `Product`: How do you keep a central AI team from becoming a bottleneck?
- `Pushback`: If squads bypass your shared path, what does that tell you?

### Axis 2: Trust and control

- `Design`: How would you design a workflow that drafts accounting actions but preserves trust?
- `Technical`: What are your top 3 ways to reduce hallucination in a financial workflow?
- `Product`: How do you decide when users are ready for more automation?
- `Pushback`: Why is human review everywhere not enough?

### Axis 3: Orchestration vs model cleverness

- `Design`: How would you go about creating a document-understanding module for receipts and invoices?
- `Technical`: When would you rely on external models versus building internal control layers?
- `Product`: How do you explain to leadership that the value is in workflow control, not model novelty?
- `Pushback`: Why not build your own stack for more control?

### Axis 4: Signal vs noise

- `Design`: How would you design a proactive alerting module for cash-flow or missing-item detection?
- `Technical`: How would you score and rank alerts so users do not get spammed?
- `Product`: How do you separate signal from noise in proactive AI?
- `Pushback`: What metric would tell you the system is useful but annoying?

### Axis 5: Business problem to working system

- `Design`: How would you scope the first version of an AI accounting assistant?
- `Technical`: How would you evaluate it offline and in production?
- `Product`: What user outcome would you optimize first: time saved, trust, approval rate, or accuracy?
- `Pushback`: What would you deliberately not automate in v1?

## Answer structure

Use the same answer shape every time:

1. Frame the problem
2. Take a position
3. Explain the tradeoff
4. Give one concrete example
5. Name the metric or failure mode

This keeps answers from turning into vague intuition or framework-listing.

## Example answer shape

For:
- `What are your top 3 ways to reduce hallucination in a financial workflow?`

Good answer shape:

1. Constrain the task to a workflow stage, not an open-ended generation task.
2. Ground the model in retrieved evidence, rules, and structured context.
3. Route low-confidence or high-impact cases to approval instead of forcing an answer.

Then add:
- how you would detect failure
- where you still would not trust the system

## Practice loop

Run each question in three passes:

- `Pass 1`: answer in `60 seconds`
- `Pass 2`: answer in `3 minutes`
- `Pass 3`: answer the hostile follow-up

Score each answer on:
- clear point of view
- concrete tradeoff
- workflow / risk awareness
- product usefulness
- low hype / low jargon

## Why this fits Ivo specifically

This structure matches the strongest public signals from the podcast and current Finom materials:
- orchestration over training your own models
- proactive AI over passive chatbot UX
- trust, transparency, and user control in accounting
- platform leverage without platform theater

## Related notes

- `../interviews/2-central-ai--ivo/IVO-WEB-RESEARCH.md`
- `../interviews/2-central-ai--ivo/glassdoor-research.md`
- `2-central-ai--ivo-simulation-1-founder-org-design.md`
- `2-central-ai--ivo-simulation-2-ai-accounting-risk.md`
- `2-central-ai--ivo-48h-prep-focus.md`
