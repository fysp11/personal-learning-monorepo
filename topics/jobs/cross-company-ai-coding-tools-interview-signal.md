# Cross-Company Insight: AI Coding Tools — The Interview Signal

Saved: 2026-04-10

## Purpose

Ivo explicitly cares whether `Codex` / `Claude Code` make engineers faster or slower. Finom Interview 3 is a 60-minute live coding exercise that explicitly uses these tools. This document captures the patterns that separate teams (and engineers) who get faster from those who get slower — and how to demonstrate the right behavior in an interview context.

---

## The 2026 Landscape

- **Claude Code** is now the #1 AI coding tool, used by ~75% of small teams and companies, with an 80.8% SWE-bench Verified score
- **Codex** uses ~3x fewer tokens for equivalent tasks and costs roughly half as much as Claude Sonnet
- **70% of engineers** use 2-4 AI tools simultaneously
- Engineers who use agents are **nearly 2x as likely to feel positive** about AI; non-users are 2x as likely to be skeptical

The key finding: **having AI tools is table stakes in 2026. Using them well is the differentiator.**

---

## Why Some Teams Get Slower

### Anti-Pattern 1: The Volume Trap

AI tools make it trivially easy to generate large amounts of code. Teams that measure productivity by lines written or PRs merged get faster at producing code but slower at shipping correct software.

**What happens:** More code → more review burden → more bugs discovered late → net slowdown.

**The fix:** Measure workflow completion, not code volume. Constrain output to what's verifiable.

### Anti-Pattern 2: The Delegation Fallacy

Engineers who dump entire problems into the agent ("build me a transaction categorization service") get back plausible-looking code that embeds the agent's assumptions, not the engineer's judgment.

**What happens:** The code works for the happy path. Edge cases are wrong. Architecture doesn't fit the existing system. Debugging takes longer than writing it would have.

**The fix:** Break the problem into small, verifiable steps. Define the interfaces first. Let the agent implement the body, but own the boundaries.

### Anti-Pattern 3: The Review Skip

When the agent generates code that "looks right," there's a strong temptation to accept without reading. This is especially dangerous for correctness-sensitive domains.

**What happens:** Subtle bugs ship. A wrong VAT rate. An incorrect citation. A confidence threshold that's never checked.

**The fix:** Treat AI-generated code like a junior engineer's PR: read it, test it, question the assumptions.

### Anti-Pattern 4: The Framework Hallucination

AI agents will confidently use API patterns that don't exist in the current version of a library, or invent abstractions that sound right but don't match the codebase.

**What happens:** Code doesn't compile, or compiles but behaves wrong because it's using a deprecated or non-existent API.

**The fix:** Constrain the agent's context. Tell it which versions, which patterns, which conventions. Verify imports and method signatures.

---

## Why Some Teams Get Faster

### Pattern 1: Interface-First Development

Define types, contracts, and boundaries before asking the agent to implement anything. The agent fills in the body; you own the shape.

```typescript
// You write this:
interface TransactionResult {
  category: string;
  confidence: number;
  vatRate: number;
  needsReview: boolean;
  reasoning: string;
}

// Then ask the agent: "Implement categorizeTransaction returning TransactionResult"
```

**Why it works:** The agent has clear constraints. The output is verifiable against the interface. The architecture is yours.

### Pattern 2: Small Verifiable Steps

Instead of "build the whole pipeline," ask for one stage at a time. Verify each stage before moving to the next.

**Good:** "Implement the VAT calculation function for German transactions. Use a lookup table, not an LLM."

**Bad:** "Build a multi-agent accounting pipeline with VAT calculation, categorization, and booking."

### Pattern 3: Prompt Precision Over Prompt Length

Short, specific prompts produce better code than long, vague ones.

**Good:** "Add a confidence field to TransactionResult. If confidence < 0.85, set needsReview to true."

**Bad:** "Make the system smarter about knowing when it's not sure and handling those cases appropriately."

### Pattern 4: Test-Driven Agent Usage

Write the test first (or describe the expected behavior), then ask the agent to implement the code that passes. This is TDD applied to AI-assisted development.

**Good:** "Write a function that passes these tests: [specific test cases]"

**Bad:** "Write the function, then write some tests for it."

### Pattern 5: Explain While You Build

In a live coding interview, narrating your choices while using the agent shows that YOU are driving, not the tool. The interviewer wants to hear:

- "I'm going to define the interface first because..."
- "I'll ask Claude to implement this stage, but I'm going to check the confidence routing logic myself because..."
- "That generated code looks right for the happy path, but I need to add the low-confidence branch..."

---

## Interview Application: The 60-Minute Live Round

### First 5 Minutes: Show Architecture Ownership

- Define the workflow boundary on paper/whiteboard
- Identify which stages are deterministic vs AI-powered
- Describe the confidence routing approach
- THEN start coding

### During Implementation: Show Tool Mastery

- Give the agent specific, scoped instructions
- Review generated code out loud ("this looks correct for VAT... wait, it's not handling the reduced rate case")
- Correct mistakes immediately instead of generating more code on top
- Use the tool to compress implementation time, not to outsource thinking

### Final 10 Minutes: Show Verification Discipline

- Run the code (or walk through execution mentally if time is short)
- Check edge cases explicitly
- Name what you'd add with more time (tests, observability, error handling)

### The Meta-Signal

The interviewer is not evaluating whether you can use Claude Code. Everyone can prompt an LLM. They're evaluating:

1. **Do you own the architecture?** (You define interfaces and boundaries, not the agent)
2. **Do you verify outputs?** (You read generated code critically)
3. **Do you maintain pace?** (The tool makes you faster, not more verbose)
4. **Do you keep the system simple?** (You resist the agent's tendency to over-engineer)
5. **Can you debug the agent's mistakes?** (You catch wrong assumptions quickly)

### One-Liner For The Interview

> "I use AI coding tools to compress implementation time, not to outsource engineering judgment. I define the shape, the tool fills in the body, and I verify the result."

---

## Ivo's Specific Concern

Ivo asked whether Codex / Claude make people faster or slower. His framing suggests he's seen both outcomes on his team.

**Answer pattern:**

> "They make engineers faster when the problem is scoped, the interfaces are defined, and the engineer verifies the output. They make engineers slower when the problem is vague, the output is accepted without reading, and the generated code creates review debt. The skill is knowing when to use the tool and when to think first."

**Finom-specific addition:**

> "For a team building correctness-sensitive workflows, the risk is that AI tools generate plausible-looking code that embeds wrong assumptions about tax rules or compliance logic. The discipline is: keep policy deterministic, isolate AI to the ambiguous parts, and always verify the generated code against the contract."

---

## Sources

- [Builder.io: Codex vs Claude Code comparison](https://www.builder.io/blog/codex-vs-claude-code)
- [Pragmatic Engineer: AI Tooling for Software Engineers in 2026](https://newsletter.pragmaticengineer.com/p/ai-tooling-2026)
- [Ryz Labs: Cursor vs Copilot vs Claude Code 2026](https://learn.ryzlabs.com/ai-coding-assistants/cursor-vs-github-copilot-vs-claude-code-which-ai-assistant-wins-2026)
- [BuildFast with AI: Claude Code vs Codex 2026](https://www.buildfastwithai.com/blogs/claude-code-vs-codex-2026)
