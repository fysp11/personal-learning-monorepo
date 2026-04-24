# Personal Learning Monorepo

This repository is a personal learning workspace organized as a monorepo. Each topic area lives in its own subdirectory ("subrepo" style) so you can learn and iterate independently while keeping everything in one GitHub project.

## Stack and Hosting

- Version control: `git`
- Hosting and repo operations: GitHub via `gh` CLI
- Repo model: monorepo with topic-focused subrepos

## Monorepo Layout

```text
learning/
  README.md
  topics/
    helm-mastery/
    jobs/
    ai-engineering/
    ai-sandboxes/
    codex/
    langgraph/
    mcp/
    notebooklm/
```

Each folder under `topics/` is a focused learning area. You can treat each one as an isolated mini-project with its own notes, code, and experiments.

## Getting Started

TODO

## Topic Conventions

For every topic folder `./topics/<topic-name>/`:

- Add a local `README.md` with learning goals and references
- Keep experiments in small, focused folders
- Track progress with short notes or checkpoints
- Prefer independent tooling per topic when useful

Example:

```text
topics/langgraph/
  README.md
  sources/

topics/jobs/
  delphyr/          # Research, interview prep, notes
  finom/            # Research, cheatsheets
```

## Knowledge Layout

For insights you want `qmd` to retrieve well, prefer a few stable file shapes over ad hoc notes:

```text
learning/
  entities/         # durable people/systems/concepts
  topics/           # topic-specific notes, code, experiments
```

Within a topic or shared area, these patterns work best:

- `entities/` - one file per person, team, system, concept, or vendor
- `architecture/` - invariants, boundaries, tradeoffs, system diagrams
- `decisions/` - ADR-style choices and why they were made
- `experiments/` - hypothesis, setup, result, takeaway
- `code-notes/` - why code exists, not just what it does
- `maps/` - cross-links such as system -> owners -> risks -> workflows

Entity files should be explicit and compact. Prefer frontmatter or labeled fields for:

- `type`
- `aliases`
- `tags`
- `relationships`
- `confidence`

This keeps the repo easy to search with both keyword and semantic retrieval.

## QMD Collections

This repo is now indexed for `qmd` in three useful ways:

- `personal-learning` - markdown-focused broad docs collection
- `proj-personal-learning` - mixed docs + code collection
- recommended next split:
  - `proj-personal-learning-docs`
  - `proj-personal-learning-code`

Useful commands:

```bash
qmd search "query" -c proj-personal-learning
qmd search "query" -c proj-personal-learning-docs
qmd search "query" -c proj-personal-learning-code
qmd ls proj-personal-learning
qmd embed
```

## Suggested Workflow

- Use issues/projects in GitHub when a topic grows in scope

---

This repo is designed to make learning structured, searchable, and easy to maintain over time.
