# Slide Deck: Scenario Testing, Safety Monitoring & Real-World Review

Create a **7-slide** interview-prep presentation for **myself** on realistic test scenarios and post-deployment monitoring for medical AI systems.

## Slides

1. **Title: Scenario Testing, Safety Monitoring & Real-World Review**
   - How to evaluate beyond static prompts and leaderboard metrics

2. **Why Realistic Scenarios Matter**
   - Static QA misses workflow failures
   - Real systems fail through unsupported synthesis, bad handoffs, scope drift, and refusal mistakes
   - Good line: one-turn tests miss conversational and workflow failure modes

3. **Scenario Types I’d Actually Run**
   - Routine chart summary
   - Longitudinal history retrieval
   - Conflicting-source synthesis
   - Out-of-scope clinical advice request
   - Make the test set look like real clinical work, not trivia questions

4. **Adversarial / Safety Scenarios**
   - Prompt injection attempts
   - Topic drift beyond intended use
   - Unsupported claims and contradictions
   - Over-generation of context beyond what the user asked for

5. **Clinician Review Drills**
   - What a reviewer should check: support, boundaries, risk, clarity
   - What gets blocked, what gets corrected, what gets approved
   - Human review is how lab evaluation becomes deployment trust

6. **What to Monitor in Production**
   - Repeated weak-support failures
   - Escalation frequency
   - Review outcomes and recurring failure categories
   - Regressions after prompt/model/retriever changes

7. **What I’d Say in the Interview**
   - “I want scenario tests that prove the system narrows, refuses, or escalates correctly.”
   - “Output testing in realistic workflows matters more than generic benchmark bragging rights.”

## Style
- Concrete, operational, and easy to rehearse
- Use scenario examples as memory aids
- Keep the contrast sharp: benchmark success vs real-world safety
- Make this deck feel like a practical evaluation playbook
