# Draft: Python-First LangGraph Agent Orchestration

## Requirements (confirmed)
- [project focus]: "Python-first research/agent orchestration"
- [repo candidate 1]: `langchain-ai/langgraph-swarm-py`
- [repo candidate 2]: `NicholasGoh/fastapi-mcp-langgraph-template`
- [repo candidate 3]: `langchain-ai/langgraph-memory`
- [process]: "plan it first"
- [need]: "ask me clarifications questions to narrow it down"
- [deliverable]: runnable local starter
- [quality bar]: "advanced demo for real use case"
- [demo scenario]: research copilot
- [priority feature]: swarm multi-agent handoffs
- [priority feature]: MCP tool integration
- [priority feature]: HITL approval flow
- [priority feature]: memory/persistence
- [priority feature]: FastAPI serving layer
- [deliverable]: **Runnable local starter** — one working Python baseline on local machine.
## Technical Decisions
- [planning mode]: Generate a decision-complete plan before implementation.
- [research scope]: Prioritize official/maintained patterns and production-ready Python pathways.
- [initial architecture direction]: FastAPI + MCP boundary + LangGraph orchestration + explicit memory layer.

## Research Findings
- [local docs]: Existing repo docs emphasize LangGraph + MCP + control-plane architecture patterns.
- [web shortlist]: Candidate repos have validated community signals and feature coverage from prior search.
- [workspace status]: Repository is effectively greenfield for Python (no `pyproject.toml`, no `.github/workflows`, no existing `topics/` tree yet).
- [available tooling]: `python3`, `pytest`, `uv`, and `poetry` are available in environment; quality tooling is not configured in repo.
- [local infra]: `docker` and `docker compose` are available locally.
- [local infra]: `psql` client is not installed locally.
- [topic path]: repository README explicitly uses `topics/langgraph/` as the topic directory pattern.
- [repo role fit - swarm]: `langgraph-swarm-py` is strongest for dynamic handoffs and multi-agent swarm orchestration.
- [repo role fit - template]: `fastapi-mcp-langgraph-template` is strongest as API/deployment scaffold with MCP integration.
- [repo role fit - memory]: `langgraph-memory` offers useful extraction/persistence patterns but is reference-style and narrower in scope.
- [pattern maturity - swarm]: stable, production-ready, no custom glue needed.
- [pattern maturity - MCP]: stable via `langchain-mcp-adapters`; auth/user scoping is extra.
- [pattern maturity - memory]: stable for checkpointer/store; extraction service patterns are reference-grade.
- [pattern maturity - HITL]: stable via `interrupt()` and `Command`; timeout/cleanup is extra.
- [pattern maturity - retry]: stable via `RetryPolicy`.
- [pattern maturity - saga]: not native; requires custom implementation and is currently out of scope.
- [critical guardrail]: avoid `InMemorySaver` for any persistence claims beyond toy/demo runs.
- [critical guardrail]: set `tool_name_prefix=True` for MCP servers.
- [critical guardrail]: set `recursion_limit` to avoid infinite swarm loops.
- [surrealdb finding]: no native LangGraph Python checkpoint saver surfaced for SurrealDB in current evidence.
- [surrealdb finding]: LangChain community does expose `SurrealDBStore` as a vector store and a `SurrealDBLoader`, which makes it a stronger fit for long-term/semantic memory than for graph checkpoints.
- [surrealdb finding]: `surrealdb/langchain-surrealdb` is official for vector-store use; `langgraph-checkpoint-surrealdb` exists but is community-maintained and low-adoption.
- [surrealdb decision]: Use SurrealDB for long-term memory only in phase 1, not for LangGraph checkpoints.
- [pattern maturity - swarm]: STABLE, production-ready, no custom glue needed.
- [pattern maturity - MCP]: STABLE via `langchain-mcp-adapters`, needs auth middleware for multi-tenant.
- [pattern maturity - memory]: STABLE for checkpointer + store; memory extraction (langgraph-memory) is reference-only.
- [pattern maturity - HITL]: STABLE via `interrupt()` + `Command`, needs custom timeout handling.
- [pattern maturity - retry]: STABLE via `RetryPolicy`, exponential backoff with jitter.
- [pattern maturity - saga/compensation]: NOT NATIVE, requires full custom implementation.
- [pattern maturity - subgraphs]: STABLE, production-ready with state transforms.
- [critical pitfall]: InMemorySaver NOT for production; must use PostgresSaver.
- [critical pitfall]: set recursion_limit to prevent infinite agent loops.
- [critical pitfall]: tool_name_prefix=True with MCP to prevent collisions.

## Open Questions (remaining)
- none blocking; current defaults are local-first, advanced-demo depth, breadth includes all five requested features.

## Scope Boundaries
- INCLUDE: Python-first orchestration patterns grounded in the three selected repos.
- EXCLUDE: TypeScript-first implementation and unrelated framework migrations.

## Planning Session Updates
- [latest request]: "plan implementing this draft"
- [plan target]: `.sisyphus/plans/python-first-langgraph-agent-orchestration-implementation.md`
- [assumption]: proceed with local-first advanced demo defaults captured above unless user overrides.
