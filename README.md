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
    langgraph/
    ai-engineering/
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
  notes/

topics/jobs/
  delphyr/          # Research, interview prep, transcripts
  finom/            # Research, cheatsheets
```

## Suggested Workflow

- Use issues/projects in GitHub when a topic grows in scope

---

This repo is designed to make learning structured, searchable, and easy to maintain over time.
