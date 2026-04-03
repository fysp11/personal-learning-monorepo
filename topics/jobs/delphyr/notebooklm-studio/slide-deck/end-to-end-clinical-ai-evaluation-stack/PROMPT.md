# Slide Deck: End-to-End Clinical AI Evaluation Stack

Create an **8-slide** interview-prep presentation for **myself** on how to evaluate clinical AI as a full system, not just as a model benchmark.

## Slides

1. **Title: End-to-End Clinical AI Evaluation Stack**
   - Why “the model scored well” is not enough

2. **What Benchmarks Miss**
   - Benchmarks test what the model knows, not how the system behaves in workflow
   - Static QA misses scope drift, unsupported synthesis, refusal failures, and bad handoffs
   - Best line: “A model can ace a benchmark and still fail clinically” 

3. **Component-Level Evaluation**
   - Evaluate extraction, retrieval, generation, and final answer separately
   - Retrieval questions: Did we fetch the right evidence?
   - Generation questions: Was the answer faithful and supported?
   - Final answer questions: Did the system behave safely?

4. **Workflow-Level Evaluation**
   - Evaluate the full path from user request to reviewed output
   - Test whether the system narrows, refuses, or escalates correctly
   - Mini example: summary request vs prescription request should produce different system behavior

5. **Human Evaluation**
   - Clinician review is needed for safety, not just polish
   - Human review catches failure modes automated metrics miss
   - Strong example: review before notes or sensitive drafts enter the EHR

6. **Monitoring After Deployment**
   - Track recurring failure patterns, regressions, and drift
   - Use logs, red-team review, and case audits
   - Good phrase: evaluation continues after launch

7. **Practical Examples I Can Reuse**
   - “Show most recent A1C” → did retrieval return the right source?
   - “Summarize recent medication changes” → did output stay grounded?
   - “What should I prescribe?” → did the system refuse or escalate correctly?

8. **What I’d Say in the Interview**
   - “The app works is not an evaluation plan.”
   - “I’d evaluate components, scenarios, human review, and post-deployment monitoring as one stack.”

## Style
- Practical and interview-ready
- Prefer examples and contrasts over theory
- Keep terminology concrete and reusable
- Make this the anchor eval deck, not a research summary
