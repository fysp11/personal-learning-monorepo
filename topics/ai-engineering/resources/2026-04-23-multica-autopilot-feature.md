# Multica Autopilot Feature Research

Saved: 2026-04-23

Sources:
- Multica changelog: https://multica.ai/changelog
- GitHub PR #1028: https://github.com/multica-ai/multica/pull/1028
- CLI and daemon guide: https://github.com/multica-ai/multica/blob/main/CLI_AND_DAEMON.md
- GitHub releases: https://github.com/multica-ai/multica/releases

## Bottom Line

Multica Autopilot is a scheduled and manually triggered automation layer for AI coding agents. It turns recurring prompts into agent work, usually by creating an issue and assigning it to an agent.

The useful framing is:

- Autopilot is not a fully autonomous product manager.
- It is a repeatable job dispatcher for agent work.
- Its strongest near-term use is recurring engineering operations: triage, backlog grooming, dependency review, bug sweeps, documentation refresh, and scheduled code-health tasks.

## Timeline

- 2026-04-14: PR #1028 merged the core Autopilot feature.
- 2026-04-15: Multica v0.2.0 changelog announced "Autopilot - scheduled and triggered automations for AI agents."
- 2026-04-17: v0.2.5 added CLI `autopilot` commands and several Autopilot fixes.
- 2026-04-18: v0.2.6 fixed run-state UI and daemon workspace resolution for run-only tasks.
- 2026-04-22: v0.2.15 is the latest changelog entry at research time; newer releases focus on local skills, orphan-task recovery, LaTeX, and Focus Mode rather than a major Autopilot scope change.

## What It Does

Autopilots dispatch agent tasks through:

- scheduled triggers
- manual "run now" triggers
- run history
- issue creation and assignment to an agent
- status synchronization from issue/task lifecycle back to the Autopilot run

The CLI guide describes Autopilots as scheduled or triggered automations that dispatch agent tasks either by creating an issue or by running an agent directly.

## Current CLI Surface

The documented commands include:

```bash
multica autopilot list
multica autopilot get <id>
multica autopilot create --title "Nightly bug triage" --description "Scan todo issues and prioritize." --agent "Lambda" --mode create_issue
multica autopilot update <id> --status paused
multica autopilot delete <id>
multica autopilot trigger <id>
multica autopilot runs <id>
multica autopilot trigger-add <autopilot-id> --cron "0 9 * * 1-5" --timezone "America/New_York"
multica autopilot trigger-update <autopilot-id> <trigger-id> --enabled=false
multica autopilot trigger-delete <autopilot-id> <trigger-id>
```

Important limitation: the CLI currently exposes `create_issue` mode. The data model has `run_only`, but the CLI docs say it is not exposed there yet. Cron schedule triggers are exposed; webhook and API trigger kinds exist in the data model but are not surfaced because server endpoints do not fire them yet.

## Architecture Signal

PR #1028 describes a fairly complete first version:

- database tables for `autopilot`, `autopilot_trigger`, and `autopilot_run`
- background cron scheduler with a 30-second tick
- HTTP handlers for CRUD, triggering, run history, and trigger CRUD
- run lifecycle sync from issue/task events
- WebSocket cache invalidation in the frontend
- list/detail pages, trigger management, run history, and template gallery

The initial PR also mentioned concurrency policies and two execution modes, but later release notes show refactors and fixes, including removing broken concurrency policies and limiting CLI trigger support.

## Why It Matters

Autopilot is important because it converts agents from chat sessions into recurring operational workers.

Useful recurring jobs:

- daily bug triage
- dependency/update review
- issue deduplication
- documentation freshness checks
- code-health sweeps
- release-note drafts
- scheduled eval or benchmark analysis
- recurring research scans

The pattern maps well to production AI engineering:

- recurring work needs schedule, ownership, status, and history
- issue creation gives the agent an auditable work container
- run history lets humans inspect outcomes instead of trusting silent background work
- pausing and manual trigger controls keep autonomy bounded

## Maturity Check

Signal strength: Medium-high.

Reasons:

- The feature shipped into the public changelog and repository.
- The PR and CLI docs expose real implementation details.
- The release stream shows active hardening immediately after launch.

Risks:

- It is early and changing quickly.
- `run_only`, webhook, and API triggers appear not fully productized through the CLI.
- The feature depends on daemon/runtime reliability, workspace isolation, and agent CLI behavior.
- Autonomous recurring work can produce noisy issues unless prompts and review policies are tight.

## Design Lesson

For agent platforms, "autopilot" should be understood as a control-plane primitive, not a magic autonomy layer.

The durable pattern is:

1. Define recurring work as a prompt plus owner agent.
2. Put each run in an auditable container.
3. Trigger by schedule or explicit human action.
4. Track status, output, and failure.
5. Keep pause/delete/manual rerun controls close to the workflow.

That is a practical bridge between human-managed issue boards and autonomous coding agents.
