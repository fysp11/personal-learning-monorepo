# Audio Overview 3: Agentic Coding Execution (Claude Code/Codex)

Create an audio overview on how to use Claude Code or Codex like a disciplined engineer during a live coding interview.

Explain the execution mindset: scope before coding, define the workflow boundary, clarify input and output contracts, separate AI-powered logic from deterministic logic, and state the success metric before implementation starts. Emphasize contracts first, implementation second: the human owns the architecture and interfaces, while the coding agent helps fill in scoped pieces of implementation.

Cover continuous verification: read every generated output, inspect it critically, correct it early, and do not confuse plausible-looking code with correct code. Explain bounded concurrency as a concrete example of disciplined implementation, including why a semaphore is a control point and why unbounded fan-out is risky. Include the three main failure modes of AI coding tools: volume without judgment, architecture delegation, and verification gap.

Keep the tone practical, rigorous, and interview-focused. Frame AI coding tools as force multipliers for a disciplined engineer, not substitutes for system design, judgment, or verification.
