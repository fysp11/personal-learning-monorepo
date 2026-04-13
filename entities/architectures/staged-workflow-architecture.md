# Entity: Staged Workflow Architecture

type: architectures
aliases:
  - staged workflow
  - staged workflow vs single opaque agent
tags:
  - system-design
  - orchestration
  - reliability
relationships:
  - confidence-routing
  - market-config-as-data
  - mcp
confidence: high
generated_by: scripts/extract-entities.ts
generated_at: 2026-04-13T03:25:20.530Z

## Evidence
- [topics/jobs/finom/interviews/3-lead-ai-engineer/README.md](/Users/fysp/personal/learning/topics/jobs/finom/interviews/3-lead-ai-engineer/README.md:77) — matched `staged workflow`: - staged workflow vs single opaque agent
- [topics/jobs/finom/NEXT_STEP.md](/Users/fysp/personal/learning/topics/jobs/finom/NEXT_STEP.md:103) — matched `staged workflow`: 6. When do you use a staged workflow versus a single agent?
- [topics/jobs/finom/NEXT_STEP.md](/Users/fysp/personal/learning/topics/jobs/finom/NEXT_STEP.md:155) — matched `staged workflow`: - `prep/3-technical-answer-bank.md` — **12 full-depth answers** including maturity ladder, staged workflow, observability
- [topics/jobs/finom/prep/3-lead-ai-engineer-prep-plan.md](/Users/fysp/personal/learning/topics/jobs/finom/prep/3-lead-ai-engineer-prep-plan.md:112) — matched `staged workflow`: - How do you decide between a single agent and a staged workflow?
- [topics/jobs/finom/prep/3-lead-ai-engineer-prep-plan.md](/Users/fysp/personal/learning/topics/jobs/finom/prep/3-lead-ai-engineer-prep-plan.md:294) — matched `staged workflow`: - choose `staged workflow` over `single opaque agent`
- [topics/jobs/finom/prep/3-technical-answer-bank.md](/Users/fysp/personal/learning/topics/jobs/finom/prep/3-technical-answer-bank.md:269) — matched `staged workflow`: ## Q11: "When would you use a staged workflow versus a single agent?"
- [topics/jobs/finom/prep/3-technical-answer-bank.md](/Users/fysp/personal/learning/topics/jobs/finom/prep/3-technical-answer-bank.md:273) — matched `staged workflow`: > A single agent is right when the problem fits in one context window and tolerates graceful degradation. A staged workflow is right when failure modes are heterogeneous, steps have different trust levels, or you need independent testability per stage.
- [topics/jobs/finom/prep/3-technical-answer-bank.md](/Users/fysp/personal/learning/topics/jobs/finom/prep/3-technical-answer-bank.md:281) — matched `staged workflow`: If a task can fail in only one way (e.g., "classify this text into one of ten categories"), a single agent is fine. If different sub-tasks can fail differently — OCR degrades, VAT rules change, confidence calibration drifts per market — then a staged workflow is required. You need to fail, alert, and fix each stage independently, not debug a combined blob.
- [topics/jobs/finom/prep/3-technical-answer-bank.md](/Users/fysp/personal/learning/topics/jobs/finom/prep/3-technical-answer-bank.md:287) — matched `staged workflow`: A single agent cannot have one part that auto-executes and one part that requires human approval. In a staged workflow, you can insert an approval gate between the proposal stage and the booking stage. The agent that generates proposals has no access to the booking ledger. The booking step only runs after explicit confirmation.
- [topics/jobs/finom/prep/3-technical-answer-bank.md](/Users/fysp/personal/learning/topics/jobs/finom/prep/3-technical-answer-bank.md:306) — matched `staged workflow`: > "I use a single agent to explore and a staged workflow to ship. Once I know what can go wrong, I formalize the stages — because each named failure mode deserves its own circuit breaker."
- [topics/jobs/finom/prep/proposals/3-scheduled-signal-refinement-prompt.md](/Users/fysp/personal/learning/topics/jobs/finom/prep/proposals/3-scheduled-signal-refinement-prompt.md:248) — matched `Staged Workflow Architecture`: - staged workflow architecture
- [topics/jobs/finom/prep/proposals/3-scheduled-signal-refinement-prompt.md](/Users/fysp/personal/learning/topics/jobs/finom/prep/proposals/3-scheduled-signal-refinement-prompt.md:287) — matched `staged workflow`: - `single black box` vs `typed staged workflow`
