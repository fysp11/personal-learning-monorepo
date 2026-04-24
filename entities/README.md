# Entities

This folder is now mainly for extraction infrastructure and templates.

Canonical durable notes that were previously stored here have been moved into topic homes under `topics/`, for example:

- `topics/ai-engineering/foundations/`
- `topics/codex/notes/`
- `topics/mcp/notes/`
- `topics/notebooklm/notes/`
- `topics/jobs/archive/finom/entities/`

Use this folder for durable entities that should stay easy to retrieve across topics.

Good entity types:

- products
- systems
- concepts
- vendors
- patterns
- tools
- frameworks
- protocols
- methodologies
- libraries
- architectures

Discover mode treats these as valid target buckets for proposed entities.
The only types excluded from the qmd-backed entity layer are people and companies.

Recommended filename pattern:

```text
entities/<type>/<slug>.md
```

Examples:

```text
entities/systems/mcp.md
entities/concepts/confidence-routing.md
```

Each entity file should stay compact and explicit.

Suggested structure:

```md
# Entity: Confidence Routing

type: concept
aliases:
  - confidence router
tags:
  - ai-engineering
  - reliability
relationships:
  - human-review
  - calibration
confidence: high

## Facts
- ...

## Why it matters
- ...

## Open questions
- ...
```

Why this shape works:

- strong keyword retrieval
- good semantic retrieval after `qmd embed`
- durable cross-topic references
- easy to update without rewriting large notes

## Reproducible extraction

For backfills from any dataset, use the checked-in extractor instead of ad hoc manual extraction:

```bash
bun run entities:finom
bun run entities:finom:sync
bun run entities:finom:strict
bun run entities:discover:finom
bun run entities:discover:finom:sync
bun run entities:discover:finom:lexical
```

What it does:

- scans the configured source files
- matches checked-in entity aliases deterministically
- writes entity files under `entities/<type>/<slug>.md`
- supports any `type` string present in the checked-in config (no hardcoded type enum in code)
- can auto-expand with qmd-discovered candidates during `entities:finom` runs
- promotes useful discovered items into `entities/<type>/<slug>.md` when they are durable enough to keep
- optionally runs `qmd update` and `qmd embed`
- in `--discover` mode, proposes candidate entities into `entities/_discover/<config>.md`

Candidate handling:

- `_discover/` is a review queue, not the canonical layer
- promote a candidate when it is repeated, specific, durable, and useful for retrieval
- leave it in `_discover/` when it is vague, one-off, duplicate, or unstable
- keep the canonical entity files compact and explicit

Note:

- the extraction step is the important deterministic part
- the `:sync` variant will warn, not fail, if `qmd` cannot write its home-directory index in the current environment
- discover supports pluggable engines via `--discover-engine` (`qmd` default, `lexical` fallback)
- qmd discover can be scoped with `--qmd-collection`, `--qmd-top-k`, and `--qmd-seed-limit`
- auto-expansion can be toggled with `--expand-from-discover` / `--no-expand-from-discover`

The extractor config lives in the checked-in config directory:

- `/Users/fysp/personal/learning/scripts/entity-configs/`
