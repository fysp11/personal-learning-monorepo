# Finom Interview 3 - Lead AI Engineer Round

Saved: 2026-04-09

Canonical public intel: `../../prep/fresh-intel-april-2026.md`

## Format

- `90 minutes` total
- `30 minutes` technical questions
- `60 minutes` live problem-solving / coding
- live exercise explicitly uses `Claude Code` or `Codex`
- this is **not** a manual whiteboard coding round

## Recruiter Call Highlights

- Finom wants to move forward with a `90-minute technical interview`.
- The live exercise is intentionally designed around Claude Code or Codex because Finom does not consider manual coding skills especially relevant for this round.
- Samuel told Finom there is another offer on the table, so he is trying to keep the process moving quickly.
- Friday, April 10, 2026 and Monday, April 13, 2026 are holidays across much of the team, which blocks earlier scheduling.
- The relevant Finom engineer was only available Tuesday, April 14, 2026.
- Availability discussed was roughly Tuesday afternoon Central Europe time, with Sao Paulo five hours behind at that moment.
- Samuel was trying to clarify what remains after this technical step, because the delay creates pressure against the competing offer timeline.
- The process had some noisy names/threads in the recruiter chain, but they are not useful interview signals.
- Samuel treated a founder reaching out directly as a positive signal.
- Samuel said he would send over the prep details he had been given.

## Grounded Signals From Interview 2

- Ivo said the next step is with one of Finom's `leading engineer[s]` (now user-confirmed as `Viktar Adynets`)
- he said he is `a little bit technical` but `not super technical`, which implies this round is where deeper technical judgment gets checked
- he wants the technical round to be `creative`, not a stock question set
- he cares whether `Codex` / `Claude` make engineers faster or slower in reality
- these Interview 2 signals are strong enough to treat as grounded prep inputs
- he described Finom's AI work as a mix of:
  - `operational excellence`
  - `AI-first product work`
  - `adoption`
- he distinguishes `AI team` from classic `ML team`
- he wants proactive systems that `do the work`, not just assistants that explain the next step
- he described the desired behavior as closer to `go do the task, then come back`, not a passive copilot UX
- he repeatedly framed team quality as `small`, `high-caliber`, and direct rather than process-heavy
- he described `adoption` as a real workstream with a dedicated owner, internal workshops, and explicit AI-tool rollout across teams
- he framed success in business terms like replacing manual work and reducing `FTE per active customer`
- he pointed to a concrete workflow anchor: tax automation already running in `Germany`, with movement toward `France`

## Best Read On The Interviewer

- updated 2026-04-11: user-confirmed interviewer is `Viktar Adynets`
- full public profile remains unconfirmed; detailed note: `../../interviewers/V-Adynets.md`
- safest assumption: this is a senior / lead AI engineer close to implementation, not a pure manager or recruiter
- best org model to assume: `core > layers > product`, spanning `central > integration > embed(domain)`
- likely treats AI-tool usage as a team operating capability, not just an individual preference
- likely cares about owning relationships with teams to increase engagement, adoption, and vision around enterprise-grade novelty

## What This Round Is Probably Testing

- can you decompose ambiguous workflow problems into explicit stages
- can you separate `AI judgment` from `deterministic policy`
- can you add confidence routing, observability, and approval paths without being asked
- can you use a coding agent as a force multiplier without letting it drive the architecture
- can you connect technical choices to operational leverage
- can you design an agentic flow that actually completes work and returns a result, instead of leaving the user with the next manual step
- can you work with low ceremony inside a small, opinionated engineering group
- can you make AI-tool usage concretely useful for a small team instead of just sounding enthusiastic about it
- can you tie architecture choices back to shipped workflow outcomes instead of abstract agent talk
- can you influence the relationship layer between central, integration, and embedded teams so the system spreads well

## Strongest Positioning

> Production AI engineer who builds observable workflow systems, keeps policy deterministic, uses AI for ambiguity, and earns autonomy step by step.

Short version:

> AI for ambiguity. Software for policy. Measurable leverage over demo energy.

## Likely Technical Themes

- staged workflow vs single opaque agent
- confidence-aware routing
- proposal mode vs action mode
- `do the work, then report back` workflow design
- evaluation and failure severity
- `Germany`-first workflow design that can generalize cleanly toward `France` / multi-market rollout
- product integration in a `Python + C#` environment
- reusable central-AI patterns that domain teams will actually adopt
- why AI coding tools help only when scoped and verified well
- adoption mechanics for getting those patterns used by real teams
- operational compression metrics such as steps removed, review load reduced, or lower human-touch cost

## Recruiter Follow-Up Signal

- the strongest technical signal was that the live round uses **Claude Code or Codex**
- Finom is **not** treating this as a manual coding interview

## Good Re-entry Order

1. `../../prep/3-lead-ai-engineer-day-of-card.md` — quick reference card with answer skeleton, vocabulary, and interviewer profile
2. `../../prep/3-lead-ai-engineer-prep-plan.md` — full prep plan with drills
3. `../../prep/3-live-round-scenarios.md` — scenario playbook for the 60-min live coding exercise
4. `../../NEXT_STEP.md`
5. `../2-central-ai--ivo/README.md`
6. `../../application/senior-ai-engineer-match-analysis.md`
7. `../../code/README.md` — three runnable demos: MAS pipeline, live rehearsal, eval harness