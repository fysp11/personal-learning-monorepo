# Finom Interview 3 — Day-of Card

Saved: 2026-04-11
Updated: 2026-04-11

## Round Shape
- 90 minutes total
- 30 min technical questions
- 60 min live problem-solving with Claude Code or Codex
- Not a manual whiteboard round
- **Interviewer:** V. Adynets — likely senior/lead AI engineer
- **Interviewer signal:** possible competitive-programming background (Grodno State University ICPC teams 2019-2020) — expect precision, clean invariants, fast detection of hand-wavy logic

## Core Thesis (say in 30 seconds)

> I build production-grade AI systems by keeping policy deterministic, isolating AI to the ambiguous parts, and shipping with evals, routing, and clear failure controls. Real leverage means the workflow gets faster and more autonomous without becoming opaque or unsafe.

Short version:
> AI for ambiguity. Software for policy. Workflow quality over model cleverness.

## What They Care About
- Does AI make the team faster, not slower?
- Can you decompose a workflow into controllable stages?
- Can you separate judgment from deterministic policy?
- Can you design proactive systems that actually complete work?
- Can you use Codex / Claude well without losing rigor?
- Can you tie design choices to operational leverage?
- Can you work in a small, direct, high-judgment team?
- Can you make patterns that domain teams will actually adopt?

## First 5 Minutes — DO NOT CODE

Say something like:
- Before I code, I want to define the workflow boundary, success condition, and what stays deterministic versus AI-driven.
- If the task is open-ended, I also want to decide what should be proactive versus proposal-only.

Then lock down:
- input
- output
- failure modes
- confidence / fallback path
- what can be mocked
- what can act automatically
- what must stay proposal-only in v1
- what metric this should improve

## Answer Skeleton (use for every technical question)

1. **Frame** the problem
2. **State** the design choice
3. **Explain** the tradeoff
4. **Name** the failure mode
5. **Describe** the control / metric

Example:
> For transaction categorization, I would separate receipt matching, feature extraction, category proposal, VAT rules, and booking. The category proposal uses AI because merchant text is ambiguous. VAT logic stays deterministic because the failure cost is compliance-related. Low-confidence cases route to proposal mode, not auto-booking. I would measure approval rate, override rate, and severe-error rate by market.

## Default Design Moves
- staged workflow over single opaque agent
- proposal mode over full autonomy
- typed outputs over raw text parsing
- explicit stage boundaries over one giant prompt
- AI behind an interface
- confidence-aware routing
- observability / trace object
- one obvious verification path
- earned autonomy by stage, not claimed upfront
- measurable operational gain over impressive complexity

## Questions To Expect
- What should be deterministic vs LLM-based?
- How would you design an expense categorization workflow?
- How would you evaluate a financial AI workflow?
- When do you use a staged workflow vs a single agent?
- How do you handle low-confidence outputs?
- What observability would you add first?
- How would you integrate AI into a Python + C# system?
- How would you make AI coding tools increase throughput instead of slowing people down?
- How would you generalize Germany-first workflows toward France / other markets?
- How should a central AI team help without becoming a bottleneck?
- What is the difference between an AI team and an ML team?
- When should you automate the work vs just assist the user?
- How do you know workflow is reducing FTE / manual work vs just moving work around?

## Live Round Tactics
- Give Codex / Claude small, precise steps
- Inspect generated code before moving on
- Keep policy and domain rules out of prompts when possible
- Prefer mockable functions and typed contracts
- Verify behavior before saying done
- Avoid unnecessary frameworks and monolithic agent loops
- The meta-signal: **you use AI as a force multiplier, not a substitute for engineering judgment**

## What To Say If Asked About Tradeoffs
- AI is best for ambiguity: extraction, classification, proposal generation
- Deterministic code should own policy, validation, routing, and rollback
- Safety comes from visibility, not from hiding decisions in prompts
- Good automation reduces manual steps and review load, not just demo time
- Central AI centralizes the hard reusable parts — not every product decision
- Adoption is a product, not a memo

## Key Vocabulary

| Term | Meaning |
|------|---------|
| SKR03/SKR04 | German standard chart of accounts |
| USt / UStVA | German VAT / VAT advance return |
| PCG | French chart of accounts (Plan Comptable Général) |
| Kleinunternehmer §19 | German small business VAT exemption |
| Reverse charge | VAT mechanism for cross-border B2B |
| MAS | Multi-Agent System (Finom's public architecture) |
| MCP | Model Context Protocol — Finom is stitching platform with MCP interfaces |
| FTE per active customer | Ivo's core efficiency metric |
| AIC4 | Finom's AI platform for proactive agent experiences |

## Good Closing Questions (pick 1-2)

1. In the live exercise, do you care more about a complete slice or the reasoning and verification path?
2. Which AI workflows are closest to production pain today?
3. Where do AI systems currently fail most: retrieval, tool use, orchestration, or integration?
4. What separates engineers who get faster with Codex/Claude from those who create review burden?
5. Where is the current friction: central AI discovering patterns, or domain teams adopting them?

## If You Blank

> First define the workflow boundary. Then separate ambiguity from policy. Keep AI on messy judgment, keep deterministic systems on control and compliance, add confidence-aware routing, and verify with observable outputs before calling it done.

## Success Condition

They leave thinking:

> He is not just good at AI. He is good at building AI systems that can survive production reality.

## One-line Reminder

Be the person who can make AI useful in production, not just interesting in a demo.
