# Entity: Earned Autonomy

type: concepts
aliases:
  - earned autonomy
tags:
  - ai-engineering
  - automation
  - finom
relationships:
  - confidence-routing
  - proposal-mode-vs-action-mode
confidence: high
generated_by: scripts/extract-entities.ts
generated_at: 2026-04-13T03:25:20.493Z

## Evidence
- [topics/jobs/finom/code/README.md](/Users/fysp/personal/learning/topics/jobs/finom/code/README.md:121) — matched `Earned Autonomy`: > "Confidence is just a number until you calibrate it. In a new market, the model may say 90% but only be right 70% of the time — that's over-confidence. Platt scaling fixes the mapping without retraining. The earned autonomy ratchet: start conservative, calibrate, then widen thresholds as trust is measured."
- [topics/jobs/finom/code/README.md](/Users/fysp/personal/learning/topics/jobs/finom/code/README.md:223) — matched `Earned Autonomy`: - **Earned autonomy by category**: Known SaaS/travel/coworking → auto-book. Restaurants, new vendors → propose. Reverse charge (AWS Ireland, Google Ireland) → always surfaces regardless of confidence. Filing → always requires explicit user signature.
- [topics/jobs/finom/code/README.md](/Users/fysp/personal/learning/topics/jobs/finom/code/README.md:262) — matched `Earned Autonomy`: "This is the distinction Ivo drew between a passive copilot and a proactive workflow agent. The batch processor doesn't ask the user to do the work — it does the work and comes back with the results, surfacing only what genuinely requires human judgment. The reverse-charge items always surface, and filing always requires explicit approval — the earned autonomy is selective, not blanket."
- [topics/jobs/finom/insights/agent-safety-transaction-semantics.md](/Users/fysp/personal/learning/topics/jobs/finom/insights/agent-safety-transaction-semantics.md:9) — matched `Earned Autonomy`: ## Core Principle: Earned Autonomy
- [topics/jobs/finom/insights/confidence-calibration-deep-dive.md](/Users/fysp/personal/learning/topics/jobs/finom/insights/confidence-calibration-deep-dive.md:13) — matched `Earned Autonomy`: This is the mathematical foundation for the "earned autonomy" pattern Ivo described.
- [topics/jobs/finom/insights/confidence-calibration-deep-dive.md](/Users/fysp/personal/learning/topics/jobs/finom/insights/confidence-calibration-deep-dive.md:115) — matched `Earned Autonomy`: The 5% audit rate is the cost of maintaining trust. As calibration improves, audit rate can decrease — another form of earned autonomy.
- [topics/jobs/finom/insights/live-coding-with-ai-agents-advanced-patterns.md](/Users/fysp/personal/learning/topics/jobs/finom/insights/live-coding-with-ai-agents-advanced-patterns.md:91) — matched `Earned Autonomy`: This is the "earned autonomy" pattern Ivo described — start conservative, widen as trust is measured.
- [topics/jobs/finom/NEXT_STEP.md](/Users/fysp/personal/learning/topics/jobs/finom/NEXT_STEP.md:161) — matched `Earned Autonomy`: - `insights/confidence-calibration-deep-dive.md` — ECE, Platt scaling, earned autonomy math
- [topics/jobs/finom/prep/3-lead-ai-engineer-prep-plan.md](/Users/fysp/personal/learning/topics/jobs/finom/prep/3-lead-ai-engineer-prep-plan.md:298) — matched `Earned Autonomy`: - choose `earned autonomy by stage` over claiming the whole workflow is autonomous
- [topics/jobs/finom/prep/3-lead-ai-hostile-followups.md](/Users/fysp/personal/learning/topics/jobs/finom/prep/3-lead-ai-hostile-followups.md:20) — matched `Earned Autonomy`: > "Then you start at maximum conservatism — nothing auto-books. You collect the first 500-1000 human-reviewed transactions, fit a calibration curve, and only then set thresholds. The earned autonomy ratchet: Level 0 is 100% human review, Level 1 is conservative auto-booking after calibration is verified."
- [topics/jobs/finom/prep/3-lead-ai-hostile-followups.md](/Users/fysp/personal/learning/topics/jobs/finom/prep/3-lead-ai-hostile-followups.md:91) — matched `Earned Autonomy`: > "Trust is earned, not declared. Start with proposal mode: the AI suggests, the human confirms. Track the confirmation rate. When the human confirms 95%+ of suggestions without changes, you've earned the right to propose auto-mode. Show the team the data: 'You confirmed 97% of suggestions last month, 0 were wrong — want to try auto-booking the high-confidence ones?' That's how earned autonomy works in practice."
- [topics/jobs/finom/prep/3-live-round-scenarios.md](/Users/fysp/personal/learning/topics/jobs/finom/prep/3-live-round-scenarios.md:36) — matched `Earned Autonomy`: 3. "Confidence routing gives us earned autonomy — high confidence auto-books, medium proposes for approval, low rejects"
