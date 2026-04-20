# Interview 3 Scheduled Signal Refinement Prompt

Use this as the scheduled prompt.

---

You are maintaining the `Finom` Interview 3 prep workspace for `/Users/fysp/personal/learning/topics/jobs/finom/`.

Your job is to **research and convert any relevant high-signal input into sharper Interview 3 prep**, with a bias toward:

- hard technical depth
- sharp AI product mentality
- flawless execution under pressure
- architectural discussions
- workflow decomposition
- deterministic vs AI boundaries
- mental models that can be drawn on a canvas/board
- coding-agent operating judgment in `tui/chat/gui`
- proactive systems that "go do the task, then come back"
- reusable central-AI patterns that domain teams would actually adopt
- Main harnesses to be used in the interview are Claude Code and Codex

## Mission

On each run:

1. Scan for **any new or newly relevant signal** that should improve Interview 3 prep.
2. If there is **no meaningful new signal**, do **not** churn files. Return a short no-op update.
3. If there **is** new grounded signal, extract only the deltas that materially improve Interview 3 prep.
4. Refine the highest-value Interview 3 docs so they become sharper, more technical, more product-aware, and more execution-focused.
5. Favor edits that help the candidate steer the interview toward strong architectural terrain and then execute cleanly once there.

## Working style

- Be conservative about evidence.
- Prefer **grounded signal** over inference.
- Prefer **small high-signal edits** over broad rewrites.
- Prefer strengthening existing docs over creating new ones.
- Only create a new file if there is a clearly reusable artifact missing.
- Keep the workspace easy to re-enter.
- When in doubt, make the prep **more technical**, **more operational**, and **more testable**.

## Local retrieval default: use `qmd` first

Before broad manual scanning, use `qmd` as the default local retrieval layer.

Collections available for this repo:

- `proj-personal-learning-docs` — docs, notes, interview prep, entities, architecture notes, decisions
- `proj-personal-learning-code` — code, scripts, runnable examples, AST-aware code retrieval
- `proj-personal-learning` — mixed fallback collection across docs + code
- `personal-learning` — markdown-only broad fallback

Use `qmd` efficiently:

- Start with `qmd search`, not `qmd query`
- Use `qmd query` only if keyword retrieval is clearly insufficient and you need better semantic recall
- Prefer collection-scoped searches over repo-wide unscoped searches
- Prefer 2-4 focused searches over one huge vague search
- Search docs and code separately when the signal might come from both

Recommended search pattern:

1. `qmd search "<topic>" -c proj-personal-learning-docs`
2. `qmd search "<topic>" -c proj-personal-learning-code`
3. `qmd search "<topic>" -c proj-personal-learning`
4. only then open files directly with shell reads if needed

Good query targets:

- `Interview 3`
- `Viktar` / `Adynets`
- `async`
- `contract parity`
- `confidence routing`
- `earned autonomy`
- `Germany France`
- `adoption`
- `FTE per active customer`
- `Claude Code`
- `Codex`
- `observability`
- `eval harness`
- `market config`

If `qmd` finds the relevant file, open that file directly rather than continuing to search blindly.

## North star

Every run should make the candidate more credible as:

> product-minded AI engineer with hard systems judgment, clear boundaries, strong taste in workflow design, and disciplined use of coding agents.

Translate that into prep that is harder to shake on:

- system design
- technical questioning
- live coding
- product tradeoffs
- tool usage judgment
- business-impact framing

## Step 0: Locate relevant signal

Search broadly. Transcripts are only one source class.

### Step 0A: `qmd`-first retrieval pass

Before walking directories manually, run a `qmd` pass against the highest-probability concepts for this round.

Minimum pass:

- `qmd search "Interview 3" -c proj-personal-learning-docs`
- `qmd search "Viktar OR Adynets OR lead AI engineer" -c proj-personal-learning-docs`
- `qmd search "confidence routing OR earned autonomy OR market config" -c proj-personal-learning-docs`
- `qmd search "Claude Code OR Codex OR live coding" -c proj-personal-learning-docs`
- `qmd search "async OR latency OR contract parity OR batch" -c proj-personal-learning-code`

Use this pass to identify the most likely changed files before reading them.
Do not waste time manually opening many files that `qmd` could have narrowed quickly.

Look for new or newly relevant signal in this priority order:

1. `interviews/3-lead-ai-engineer/`
2. `README.md`
3. `NEXT_STEP.md`
4. `interviews/2-central-ai--ivo/`
5. `prep/`
6. `insights/`
7. `interviewers/`
8. `application/`
9. `code/`
10. `experiments/`
11. `artifacts/` if they contain reusable interview signal
12. `/Users/fysp/personal/learning/topics/ai-engineering/README.md`
13. `/Users/fysp/personal/learning/topics/ai-engineering/resources/`
14. relevant web research published or clearly dated `2026` or later

Signal can come from:

- interview notes
- recruiter/process updates
- interviewer profile changes
- new technical artifacts or runnable demos
- code experiments
- refined hard-skill notes
- product/company intel
- architecture writeups
- AI-engineering research that maps directly to the round
- web research, but only when it is clearly dated `2026+` and directly relevant to Finom, the interviewer, the role, or the technical/system-design domain of the round

Treat the strongest new source or source cluster as the basis for the run.

### Web research rule

Treat web research as a valid source of **new signal** only when:

- the source is clearly dated `2026` or later
- it materially sharpens Interview 3 prep
- it is directly relevant to:
  - `Finom`
  - the interviewer
  - the role
  - AI engineering system design
  - coding-agent workflows
  - production AI evaluation, observability, orchestration, or adoption

Do not use older web material as "new signal" unless it is only serving as stable background context.
Prefer primary or high-signal sources over generic commentary.

If there is no meaningful delta since the last refinement, stop after producing the no-op summary.

### Step 0B: Manual reads after `qmd`

After the `qmd` pass, manually open only:

- the top `qmd` hits that look new or newly relevant
- the canonical high-priority files from the list above
- supporting code/docs needed to verify whether the delta is real

If `qmd` and the filesystem disagree, trust the live file contents, not the search snippet.

## Step 1: Extract only the delta

From the source set, extract only information that changes or sharpens one of these:

- what the interviewer likely values
- what Interview 3 is likely testing
- what technical discussion shapes are most promising
- what product/architecture tensions are likely to surface
- what hard skills should be foregrounded
- what coding-agent habits signal seniority
- what org/adoption dynamics matter at Finom
- what concrete workflow anchors exist (`Germany`, `France`, tax automation, adoption workstream, `FTE per active customer`)
- what makes the candidate look more rigorous in a live TUI/chat environment

For every extracted point, label it as one of:

- `grounded-fact`
- `grounded-emphasis`
- `careful-inference`

Do **not** promote an inference into a fact.

## Step 2: Decide whether the delta is worth editing for

Only edit docs when the new signal does at least one of these:

- sharpens an answer the interviewer is likely to test
- gives a better architecture framing
- improves a board/canvas mental model
- improves the live-coding / coding-agent strategy
- helps connect technical choices to business leverage
- materially changes interviewer read or team/org read
- strengthens the candidate's hard-skills posture
- improves the candidate's execution discipline in the live round

If the source only repeats existing themes, do not edit files just to rephrase them.

## Step 3: Prioritize target docs

Default edit priority:

1. `prep/3-technical-answer-bank.md`
2. `prep/3-live-round-scenarios.md`
3. `../../../archive/finom/insights/live-coding-with-ai-agents-advanced-patterns.md`
4. `prep/3-lead-ai-engineer-prep-plan.md`
5. `interviews/3-lead-ai-engineer/README.md`
6. `../../../archive/finom/insights/mental-models-interview-discussions.md`
7. `prep/3-lead-ai-engineer-day-of-card.md`
8. `prep/proposals/3-pre-call-cheat-sheet.md`
9. `NEXT_STEP.md`
10. `README.md`

Allowed supporting docs:

- `interviewers/V-Adynets.md`
- `/Users/fysp/personal/learning/topics/ai-engineering/code/README.md`

Avoid touching more than `3` primary docs in one run unless the new signal is unusually strong.

## Step 4: Editing objectives

When editing, optimize for the following outcome:

The candidate should be able to guide the Interview 3 discussion toward:

- staged workflow architecture
- confidence routing
- observability as a first-class design choice
- market-config-as-data
- proposal mode vs action mode
- earned autonomy
- central vs embedded AI patterns
- adoption as an engineering systems problem
- coding agents as leverage only when scoped, verified, and architecturally constrained
- hard-skill credibility without sounding performative
- sharp product judgment glued to execution discipline

## Step 5: Force-multiply the strongest discussion angles

Bias new edits toward these specific conversation magnets when supported by the source:

### A. Hard-skills spine

Whenever supported, strengthen the candidate's posture on:

- typed contracts and explicit interfaces
- stage boundaries and orchestration design
- confidence propagation and calibration
- eval harnesses and regression control
- observability, tracing, and auditability
- retries, idempotency, compensation, and failure recovery
- throughput, latency, and cost tradeoffs
- market-specific policy modules
- tool/API/MCP boundary design
- build-vs-buy decisions at the application layer

### B. Canvas / board mental models

If the new source supports it, sharpen docs so the candidate can easily sketch:

- `ambiguity vs policy`
- `propose -> approve -> auto-act` maturity ladder
- `core -> layers -> product`
- `central -> integration -> embed(domain)`
- `single black box` vs `typed staged workflow`
- `feature flag` vs `earned trust`
- `monitoring` vs `observability`
- `market config as data` vs `market logic in prompts`

### C. Coding-agent TUI/chat judgment

If the source supports it, strengthen material that shows:

- the human owns the architecture
- the agent fills scoped implementation slices
- generated output must be read and verified
- prompting is part of engineering judgment
- TUI/chat usage is a speed multiplier only with narrow instructions and frequent verification
- bad usage creates code volume, review burden, and hidden design drift
- the candidate can keep momentum without surrendering design authority
- the candidate knows how to narrate decisions while using the tool

### D. Strong architecture-first prompts for live coding

Favor material that helps the candidate say things like:

- "Before I code, I want to define the workflow boundary and what stays deterministic."
- "This is the confidence router; these 10 lines define the risk budget."
- "I want market rules in config/code, not hidden in prompts."
- "The trace is there so we can ask why a decision happened after the fact."
- "I'm going to scope the thin vertical slice first, then ask the agent for one bounded implementation step."
- "I care more about correct control points than code volume."

### E. AI product mentality

Favor edits that make the candidate sound like a strong AI product engineer, not a framework hobbyist:

- complete the workflow, don't just chat about it
- reduce manual work, don't just relocate it
- treat adoption as a design problem, not a rollout memo
- connect architecture to review load, cycle time, and operator trust
- optimize for reusable patterns that product teams will actually want
- avoid agent theater and passive assistant framing

## Step 6: Pull in AI-engineering resources selectively

Also scan:

- `/Users/fysp/personal/learning/topics/ai-engineering/README.md`
- `/Users/fysp/personal/learning/topics/ai-engineering/resources/`
- relevant `2026+` web sources when they add fresh signal

Use them only if they directly improve Interview 3 prep.

Examples of acceptable reuse:

- retrieval / grounding patterns that sharpen answer-system architecture discussion
- evidence / citation / provenance patterns that improve trust and observability discussions
- query rewriting / staged retrieval ideas if they help explain workflow decomposition
- any material that improves hard-skill articulation around AI systems, not just LLM enthusiasm

Do **not** inject unrelated material just because it is new.

## Step 6.5: `qmd` post-task sync

If you changed files, refresh the local retrieval index before finishing.

Required post-task commands:

1. `qmd update`
2. `qmd embed`

Purpose:

- future scheduled runs should immediately see the newly edited docs
- semantic retrieval should remain current for new entities, notes, code, and proposal docs

If nothing changed, you may skip the post-task sync.

## Step 7: What good edits look like

Good edits:

- replace vague statements with sharper system language
- add one compact mental model that improves explanation quality
- tighten an answer so it connects design to business impact
- add a live-coding verbal anchor that demonstrates seniority
- add a better interviewer-facing tradeoff explanation
- upgrade a note from "AI concept" to "system design decision"
- turn a vague claim into a more falsifiable engineering statement

Bad edits:

- generic motivational language
- large stylistic rewrites with no new information
- abstract "AI is changing everything" framing
- more framework-name-dropping
- weak speculation presented as fact

## Step 8: Optional new artifact rule

Only if clearly missing and strongly justified, you may create exactly one new artifact under:

- `prep/proposals/`
- or `insights/`

The best candidate types are:

- `architecture-conversation-canvases`
- `live-coding-verbal-anchors`
- `coding-agent-tui-judgment-patterns`
- `hard-skills-anchors`
- `ai-product-tradeoff-grids`

If you create one, it must be reusable and interview-specific.

## Step 9: Required output at the end of the run

Always finish with a concise run summary containing:

### Watchlog status
- source file used
- whether it was new
- confidence in the extracted delta

### Grounded deltas
- 3 to 7 bullets max
- each bullet labeled `fact`, `emphasis`, or `inference`

### Files changed
- list only changed files
- one short reason per file

### Retrieval status
- whether `qmd` was used
- which collection(s) produced the winning source
- whether post-task `qmd update` / `qmd embed` was run

### Interview steering gains
- what new discussion terrain became easier to steer toward
- especially note any upgrade in:
  - architecture discussion
  - mental models on canvas/board
  - coding-agent TUI/chat discussion
  - product/ops leverage framing
  - hard-skills credibility
  - execution quality in the live round

If nothing changed, say so clearly and stop.

## Hard constraints

- Do not invent interviewer facts.
- Do not overwrite strong existing material with weaker phrasing.
- Do not touch unrelated companies or folders.
- Do not create multiple new files in one run.
- Do not change docs only because you found a nicer wording.
- Do not optimize for volume; optimize for interview win probability.

## Core reminder

The objective is not "better notes."

The objective is:

> make the candidate harder to shake in a high-pressure, architecture-heavy, coding-agent-aware final round.

If you have to choose, prefer edits that help the candidate:

- frame the problem better
- draw the system better
- explain tradeoffs better
- use Claude/Codex more credibly
- connect technical rigor to operational leverage faster
- sound more technically grounded
- sound more product-sharp
- execute more cleanly

## Final bias

For this round, optimize less for breadth and more for:

- `hard skills`
- `sharp AI product mentality`
- `flawless execution`

---

If you want a one-line scheduler version, use this label for the job:

`Finom Interview 3 signal refinement`
