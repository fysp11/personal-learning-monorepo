# Interview 3 — First 90 Days Plan

Saved: 2026-04-11 (Iteration 5)

## Purpose

Answer: "What would you do in your first 90 days as Lead AI Engineer at Finom?"

This question usually comes in the last 10 minutes of the round. A weak answer sounds generic ("learn the codebase, meet the team, ship a small thing"). A strong answer mirrors the interviewer's own framing of the org back at them and names *specific* focus areas derived from what they've already told you.

Ivo described three workstreams: **operational excellence**, **AI-first product work**, and **adoption**. Structure the 90-day plan around these three dimensions, not a generic ramp arc.

---

## The Answer

### Days 1–30: Operational grounding

> "The first 30 days I'm learning, not building. I want to understand what's actually running in production before I touch anything."

**What I'd do:**
- Trace one live transaction end-to-end through the accounting pipeline: what systems does it touch, what are the latency and error rates at each stage, where is the observability today?
- Read the eval harness and last 30 days of severity-weighted eval results: where are the failures concentrating? Any systematic category mismatch?
- Sit with a tax accountant or customer success person who handles accounting support tickets: what are the top 5 mistakes users report the AI making?
- Understand the C# service boundary: what does the AI layer consume from the core banking services, what are the API contracts, where are the integration tests?
- Read the current market config for Germany and France: how are market policies represented, what's the delta between them?
- Have the "what keeps you up at night" conversation with V. Adynets and whoever owns the German accounting pipeline

**What I'm NOT doing:** Proposing rewrites. Making architectural opinions before I've seen the failure data.

**Output at 30 days:** A written "production risk snapshot" — the top 3 reliability concerns I'd want to address, ranked by impact on FTE per active customer. Share with the team, get alignment on whether my read matches theirs.

---

### Days 31–60: First focused contribution

> "The second month I want to make one thing meaningfully better — not greenfield, not a rewrite. Something that reduces real friction."

**How I'd pick the target:** From the production risk snapshot. Look for the highest-impact, most reversible improvement. Likely candidates based on the prep research:

- **Confidence calibration audit for Germany → France expansion**: if France is the next market, the model calibrated on DE transactions will have poor ECE on FR ones. Run calibration diagnostics on the first FR transaction batch and tune thresholds before GA
- **Override rate instrumentation**: if override rates aren't currently tracked per-market and per-category, add that first — it's the leading indicator for everything else
- **Add a missing test case type to the eval suite**: if the eval harness doesn't include reverse charge cases for all supported markets, add them — a direct response to FM-07

**Format:** One focused PR. Two reviewers. Verification before merge. Not a 500-line rewrite.

**Output at 60 days:** One shipped improvement, one new eval case or monitoring metric. Can name something concrete that's different because I was there.

---

### Days 61–90: Pattern and adoption leverage

> "The third month I want to take whatever I learned and make it easier for the next engineer, or the next product team, to do the right thing by default."

**What this looks like in practice:**

If the first 60 days surfaced a reliability pattern (say, how to handle OCR drift across different invoice formats), I'd write a 2-page internal doc and a reusable utility that prevents the same issue from recurring in other document types. Not a platform, not a framework — a function and a document.

If the first 60 days showed that the France expansion team is solving the same multi-market config problem from scratch, I'd propose a 30-minute sync to share the pattern — not mandate it, demonstrate it.

**On adoption specifically:** Ivo mentioned a dedicated adoption workstream. I'd want to understand what "adoption" currently means at Finom — are engineers using Claude/Codex but getting mixed results? Are product teams not using the shared AI orchestration patterns? The right answer depends on what's actually blocking adoption, not a generic "run a workshop."

**Output at 90 days:** One reusable pattern documented and shared. One adoption friction identified with a concrete proposal for how to reduce it. A view of what the 6-month roadmap should look like.

---

## Condensed Answer for the Interview (90 seconds)

> "First 30 days: operational grounding. I'd trace a live transaction end-to-end, read the eval results from the last month, and sit with a customer success person to understand what accounting mistakes real users are reporting. I wouldn't touch architecture until I understood what was actually failing in production.
>
> Days 31–60: one focused improvement. Based on what I learned — most likely something around confidence calibration for the next market expansion, or adding a missing category of test cases to the eval suite. Not a rewrite, something reversible and verifiable.
>
> Days 61–90: pattern and adoption leverage. Take the most important thing I learned and make it easier for the next person. That might be a reusable utility, a documented pattern, or a 30-minute sync with the France team. And I'd want to understand what's actually blocking adoption — not assume I know before I've seen how the team works."

---

## Hooks to the Finom-Specific Context

- Mention "FTE per active customer" as the metric you'd tie the production risk snapshot to — this was Ivo's phrase and signals you listened
- Mention the Germany → France expansion as the concrete context for the calibration work — shows you know their roadmap
- Mention the small, direct team — the 90-day plan should reflect low ceremony: a written snapshot, one PR, one sync — not a process rollout
- The competitive programming possible background of V. Adynets: he'll want to see that "first 30 days" means genuine diagnostic depth, not polite learning theatre
