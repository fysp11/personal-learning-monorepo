# Interview 3 — Story Bank (Behavioral + Technical)

Saved: 2026-04-11 (Iteration 7)

## Purpose

Interview 2 (Ivo) was leadership/vision-oriented. Interview 3 (V. Adynets) is a hands-on technical round. V. Adynets will likely probe with "tell me about a time when..." questions that require real engineering stories, not just architecture opinions.

Stories should be:
- Specific (what system, what decision, what outcome)
- Anchored to the technical themes of this role (observable AI, confidence routing, deterministic policy, production failure)
- Honest about trade-offs (what you got wrong, what you'd do differently)

---

## Story 1: When the Confidence Score Was Lying

**Context:** Working on an AI-assisted workflow where the model was outputting high-confidence predictions (consistently 0.87–0.91). The pipeline was auto-routing all of these to the fast path. It looked great in aggregate metrics.

**What happened:** Discovered that for a specific *category* of inputs (a particular document format), the model was systematically wrong at 0.88 confidence. Not occasionally — consistently. Raw accuracy on that category was 52%, but confidence was 88%.

**What I did:** Ran a per-category calibration analysis instead of just aggregate ECE. Found that the aggregate ECE was 0.04 (looks calibrated) but for the specific input type it was 0.36 (completely unreliable). Switched to per-category confidence gating and flagged that document type for human review regardless of confidence score.

**What I learned:** Aggregate calibration metrics hide per-segment failures. ECE is a mean — it tells you the model is on average calibrated, but a subgroup can be catastrophically overconfident while the aggregate looks fine. Production confidence routing must be validated per-segment, not just in aggregate.

**Interview hook:** Use when asked about calibration, confidence routing, or "how do you know your confidence scores are trustworthy?"

---

## Story 2: Pushing Back on "One Big Agent"

**Context:** Team was designing an automation workflow. The proposal on the table was to use a single large LLM call to handle extraction, classification, calculation, and report generation in one shot. Argument: simpler to build, fewer moving parts, fewer API calls.

**My position:** Pushed back. The calculation step in the workflow was compliance-sensitive — it involved applying specific rules that could have financial consequences if wrong. Putting that inside a black-box prompt made it impossible to audit ("the model calculated it"), impossible to test deterministically, and impossible to explain to stakeholders.

**What happened:** Proposed a hybrid: the LLM handles extraction and classification (genuinely ambiguous), the calculation is a pure function that takes the classification as input. Single additional function, slightly more code, but the calculation step is now testable with exact inputs/outputs. Team adopted it.

**What I learned:** The strongest argument wasn't "LLMs hallucinate" — it was "how do you answer a regulator's question about *why* this number is what it is?" For compliance-adjacent code, you need an answer that points to a rule, not a probability distribution.

**Interview hook:** Use when asked about deterministic vs AI boundaries, or "why not let the LLM do everything?"

---

## Story 3: The Eval Harness That Saved a Deployment

**Context:** Building an evaluation framework for an AI pipeline before a production deployment. Initial plan was to run on a small test set and check aggregate accuracy.

**What happened:** While designing the test cases, noticed we had no test for the edge case where the calculation produced a result that passed field-level accuracy but was wrong in a specific compound way — the individual fields were all within tolerance, but the combination was semantically wrong (a sign error that zeroed out instead of doubling, effectively).

**What I did:** Added a compound invariant check to the eval harness: in addition to field-level accuracy, assert that the total reconciles correctly against the input. This is something raw accuracy never would have caught.

**Outcome:** When we ran the eval harness against the production candidate, it failed the compound check. Would have shipped a bug that produced plausible-looking but wrong outputs.

**What I learned:** Test coverage is not just "test each field" — it's "test the system invariants". For financial workflows, the invariant is usually: outputs must sum/reconcile to the inputs. Build that check first, before field-level accuracy.

**Interview hook:** Use when asked about evaluation design, or "how do you know the eval harness is actually catching the right failures?"

---

## Story 4: The Production Failure That Came From a Confidence Threshold Set Too Loose

**Context:** Confidence routing system with auto-action above 0.8. The threshold had been set at 0.8 based on the calibration data from the first 30 days of production.

**What happened:** Six weeks later, a new category of inputs started appearing (a new document type) that the model hadn't seen. The model produced confidence scores of 0.82–0.85 on them — just above the threshold — but was wrong on ~35% of them. Since these exceeded the threshold, they were auto-actioned without review.

**Detection:** User reported an error. We pulled the trace. The confidence scores for that document type were consistently in the 0.82–0.85 band — never going below the threshold but never high enough to be obviously wrong from the score alone.

**Fix:** Added a "first-seen" flag to the confidence router: if a document type is seen fewer than 50 times, route to human review regardless of confidence score. The threshold is only trusted for categories with sufficient calibration data.

**What I learned:** Confidence thresholds need category-specific guards, not just a global cutoff. New categories deserve conservatism by default until the data supports trusting the scores.

**Interview hook:** Use when asked about production failures, or threshold design, or "what happens when the distribution shifts?"

---

## Story 5: Making the Handoff Not Just "Here's a Pattern"

**Context:** I'd built a reusable orchestration pattern that I thought was solid. Tried to share it with a domain team who needed to build something similar. Handed over the code and a design doc.

**What happened:** Two weeks later, the team hadn't used it. When I asked, the answer was: "We couldn't figure out how to adapt it to our specific input format. We started from scratch."

**What I did:** Instead of writing more documentation, sat with one engineer from that team for 90 minutes and pair-programmed the first use case with them. By the end, they'd adapted the pattern themselves and understood the constraints. Two weeks after that, they'd extended it with a feature I hadn't thought of.

**What I learned:** Documentation is for reference, not discovery. If adoption isn't happening, the blocker is usually not lack of documentation — it's lack of a working example in the team's context. The fastest path to adoption is often 90 minutes of pair programming, not a better README.

**Interview hook:** Use when asked about AI adoption, team enablement, or "what does good central AI team work look like?"

---

## Story 6: Scoping Under Time Pressure (Live Coding Analog)

**Context:** Live technical exercise where I was given 45 minutes to design and implement a classification pipeline. The prompt was open-ended.

**What I did (correctly):** Spent the first 7 minutes not coding. Defined the input, output, failure cases, and the one invariant that mattered most (correctness of the critical path). When I started coding, I had a typed contract in place and could implement against it instead of guessing at the shape.

**What I'd do differently:** I still spent too much time on the happy path and not enough on the confidence routing. The review of the work focused on "what happens when confidence is low?" and I had to explain it verbally rather than showing code.

**The lesson:** In a 60-minute live exercise, the confidence router is the most important 10 lines. It's also the easiest to skip when you're moving fast. Build it early, even if it's just 3 if/else branches. It anchors the whole design.

**Interview hook:** Use when asked about live coding approach, or the competitive programming-adjacent "how do you structure a problem under time pressure?"

---

## Story Usage Guide

| Theme | Use story |
|-------|-----------|
| Calibration / confidence scores | Story 1 |
| AI vs deterministic boundaries | Story 2 |
| Evaluation design / what evals catch | Story 3 |
| Production failures / distribution shift | Story 4 |
| Adoption / making patterns stick | Story 5 |
| Live coding approach / scoping under pressure | Story 6 |
| "Tell me about a time you pushed back" | Story 2 |
| "Tell me about a mistake" | Story 4 or 6 |
| "Tell me about a technical success" | Story 3 |
| "How do you work with teams?" | Story 5 |

## Notes

- Don't use all 6 stories in one interview — pick 2-3 based on where the conversation goes
- The best stories acknowledge what you got wrong or would do differently — shows learning, not just performance
- Keep each story to 90 seconds or less unless the interviewer asks to go deeper
- Always connect back to Finom context: "That's exactly why I'd approach [Finom-specific problem] differently because..."
