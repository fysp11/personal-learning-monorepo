# Slide Deck: Agent-Based Medical AI Assessment

Create a **7-slide** interview-prep presentation for **myself** on how to evaluate agent-like clinical workflows without drifting into hype or overclaiming Delphyr’s current implementation.

## Slides

1. **Title: Agent-Based Medical AI Assessment**
   - Evaluating workflows, tool use, and sequential clinical reasoning

2. **Why Static QA Is Not Enough**
   - Agent-like systems do more than answer a prompt once
   - They decompose tasks, call tools, gather evidence, and coordinate steps
   - Evaluation should test the process, not just the final sentence

3. **Conservative Clinical Workflow Example**
   - Example: prepare a digital patient case or MDT briefing pack
   - Pull patient history, relevant labs, correspondence, and guideline support
   - Draft a structured summary for human review rather than acting autonomously

4. **What to Evaluate in Agent Workflows**
   - Step sequencing
   - Tool orchestration quality
   - Evidence handling and citation discipline
   - Escalation behavior when support is weak or tasks go out of scope

5. **The Sharper Agentic Slide: Safety / Evaluator Loops**
   - Use evaluator or critic logic to challenge risky outputs before human review
   - Think iterative verification, not blind autonomy
   - Good phrasing: the more agentic the workflow, the more explicit the safety loop should be

6. **What Good Agent Tests Look Like**
   - Incomplete information
   - Tool failures or missing data
   - Branching decisions
   - Safe handoff to a clinician when the workflow cannot complete reliably

7. **What I’d Say in the Interview**
   - “For agent-like systems, I’d evaluate sequential reasoning, tool use, evidence discipline, and escalation—not just the final text.”
   - “Delphyr’s direction toward decision graphs and MDT preparation makes workflow evaluation more relevant than static QA.”

## Style
- Forward-looking but conservative
- Use practical workflow examples, not hype language
- Keep Delphyr context clearly separated from broader agent-eval concepts
- Make the deck easy to speak from in an interview
