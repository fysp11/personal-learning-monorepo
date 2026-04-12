# Interview 3 — AI Adoption Mechanics Deep Dive

Saved: 2026-04-11 (Iteration 5)

## Purpose

Ivo called out "adoption" as a dedicated workstream with a real owner, internal workshops, and an explicit AI-tool rollout across teams. This is likely a theme in the Interview 3 Q&A, not just a throwaway mention.

The gap in current prep: the answer bank has a target answer ("Adoption is not a memo, it is a product") but no depth behind it. This doc adds the mechanics — what you'd actually do, what you'd measure, what you've seen fail.

---

## Why Adoption Is Hard (The Real Problem)

Engineers don't fail to adopt AI tools because they don't know they exist. They fail to adopt them because:

1. **The first experience is frustrating**: the tool generates code that looks right but needs significant cleanup. The net gain is zero. The engineer concludes it's not worth it.
2. **The usage pattern is wrong**: they dump a vague problem in and get a vague answer. Nobody taught them to scope and constrain.
3. **The organizational incentive is misaligned**: the engineer is measured on shipping features. Experimenting with new tools takes time. There's no explicit budget for "learning to use Claude better."
4. **There's no visible success story from someone they trust**: a workshop from a central team carries less weight than watching a peer solve a hard problem in 20 minutes.

This means adoption interventions that work look very different from the ones that don't:

| Doesn't work | Works |
|-------------|-------|
| Mandatory training video | Live pair session with a task that matters |
| "Here's how to use Claude" handout | "Here's how we built [feature X] 3x faster — let me walk you through it" |
| Asking teams to report usage | Instrumenting the tool so you can see where value is created vs where prompts fail |
| Claiming AI makes everything faster | Showing the delta: before/after on a real task the team recognized as painful |

---

## Finom Adoption Context

Based on what Ivo described:

- **The org has 3 streams**: operational excellence, AI-first product work, adoption
- **There's a dedicated owner for adoption** — not a committee, one person with this as their primary responsibility
- **Workshops exist** — but Ivo framed this as practical rollout, not onboarding theatre
- **The goal is concrete**: reducing FTE per active customer, not "AI literacy"

This suggests Finom is past the "should we use AI?" question and is on "how do we actually use it well?" The adoption gap is probably **usage pattern quality** (how engineers use Claude Code day-to-day) not awareness or access.

---

## What Good Adoption Work Looks Like in Practice

### 1. Diagnostic first: where is the friction?

Before running any workshop, understand what's actually blocking people. Three ways:
- **Usage pattern audit**: look at how engineers are using the tool (prompt length, how often they accept vs reject generation, where they stop using it mid-task)
- **"Last time you tried it" interviews**: ask 5 engineers to describe the last time they used Claude and what happened. Patterns emerge fast.
- **Override rate as a leading indicator**: if engineers are accepting AI output and then rewriting it, they don't trust it but feel pressure to use it. That's a different problem from "not using it at all."

### 2. Make the reusable path faster than the workaround

For the accounting team specifically:
- A workflow template that scaffolds the typed stage structure (ExtractedTransaction, CategoryProposal, VATCalc) is faster than starting from scratch
- An MCP skill server that works out of the box for DE and FR markets means the engineer doesn't have to invent the market-config pattern
- Eval test cases that cover reverse charge, mixed VAT, and Kleinunternehmer transitions means the engineer doesn't have to figure out which edge cases matter

**The measure**: how long does it take a new engineer to ship their first accounting workflow feature? If using the central patterns is faster than ignoring them, adoption follows.

### 3. The live demo > the workshop

The most effective adoption moment I've seen: one engineer watches another solve a real problem they'd been stuck on. Not a demo of toy examples — a real task from the actual sprint board, solved in real time.

For Finom, this could look like:
- "Live coding Friday": 45 minutes, one engineer solves a real open ticket using Claude Code while the team watches. No prep, no polish. The messy parts are the teaching.
- Post-session doc: "What worked, what we had to correct, what prompts to avoid."

### 4. Measure the right thing

Wrong metrics:
- "Number of engineers using Claude" (surface compliance)
- "Lines of AI-generated code" (volume is not quality)
- "Workshop attendance" (activity is not adoption)

Right metrics:
- **Override rate on AI-generated code**: if high, the tool is generating noise. Investigate why.
- **Net velocity change on tasks where Claude was used**: did features ship faster? By how much?
- **Time from problem to first passing test**: Claude Code should compress this. Measure before/after on the same type of task.
- **"Would you use it again for this type of task?"** — simple per-task survey, not annual satisfaction score

For accounting-specific AI:
- **Override rate by category type**: reveals where the categorization model needs work
- **Time in proposal review queue**: if proposals are sitting unreviewed, the UX is wrong or the proposals are low quality
- **Escalation storm detection**: if the circuit breaker trips on 10%+ of batches, something in the extraction pipeline degraded

### 5. Create the "fast path" and measure its adoption

The central AI team's output should be:
- A starter template (TypeScript): typed stages, confidence routing, trace object, basic market config
- An MCP skill server that works for DE (copy-paste to add FR)
- An eval harness template with the 8 critical test case types pre-populated
- A 1-page "how to add a new market" guide

**Adoption metric for this**: what fraction of new AI features at Finom use the shared template vs roll their own from scratch? This is the real adoption number.

---

## What Makes a Central AI Team Useful vs Decorative

This is the Q6 answer from the answer bank, but with operational detail added:

**Decorative central AI teams:**
- Ship patterns that nobody uses because they're too general
- Run workshops but don't track whether people use what they learned
- Own their own metrics (pattern downloads, workshop seats) instead of downstream impact
- Require teams to get approval from the central team before building AI features
- Build abstractions so elegant that nobody can add their own market config in a day

**Useful central AI teams:**
- Own the hard shared problems: confidence calibration, eval frameworks, MCP skill interfaces, safety routing
- Track downstream metrics: what fraction of the org uses shared patterns, how long does onboarding take, what's the aggregate override rate?
- Treat every "team bypassed our pattern" as a product failure, not a compliance failure: why did they bypass it? Fix the pattern.
- Rotate people: put central team engineers on domain projects for 2–3 weeks; bring domain engineers onto central team work. Knowledge flows both ways.
- Have a single success metric: **time to first shipped AI feature for a new product team**. If it's less than a week, the patterns are working.

---

## Interview Answers

**If asked "what does the adoption workstream actually do?"**
> "Based on what Ivo described, it sounds like adoption at Finom means making sure the org actually works better because of AI tools — not just has access to them. Concretely: running live coding sessions so engineers see real usage in context, not abstract demos. Tracking override rates and velocity deltas, not just workshop attendance. And making the reusable path faster than the local workaround — if using the central patterns isn't faster than ignoring them, the patterns need to change."

**If asked "how would you measure adoption success?"**
> "Wrong metric: number of engineers using Claude. Right metric: net velocity change on tasks where Claude was used, and override rate on AI outputs. High override rate means we're generating noise, not value. And for the accounting AI specifically: time in proposal review queue and fraction of new features using shared orchestration patterns."

**If asked "what's the hardest part of making a central AI team useful?"**
> "Avoiding the approval-gate trap. If product teams need the central team's sign-off to build AI features, the central team becomes a bottleneck disguised as a standard-setter. The right model: domain teams own outcomes, central team provides leverage. Every 'team bypassed our pattern' is a product failure for the central team, not a compliance failure for the domain team."
