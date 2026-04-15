# Finom

## Snapshot
- Company: Finom
- Focus: SMB financial platform combining banking, invoicing, and AI accounting
- Relevant role: Senior AI Engineer
- Current next interview: Interview 3, a 90-minute technical round with Viktar Adynets
- Org model expectation: a normal `core > layers > product` structure, spanning `central > integration > embed(domain)`
- Role expectation: own the relationships with teams to positively influence engagement, adoption, and vision around enterprise-grade novelty

## Start Here
- `interviews/3-lead-ai-engineer/README.md` - round-specific dashboard for Interview 3
- `prep/3-lead-ai-engineer-prep-plan.md` - main prep plan for the current technical round
- `prep/3-lead-ai-engineer-day-of-card.md` - one-page day-of reference for Interview 3
- `prep/3-live-round-scenarios.md` - scenario playbook for the 60-min live coding exercise
- `prep/3-technical-answer-bank.md` - full-depth answers for the hardest likely technical questions
- `prep/3-latest-finom-intel.md` - latest Finom product/AI updates for interview currency
- `application/senior-ai-engineer-match-analysis.md` - strongest fit and objection-handling summary
- `interviews/1-introduction--dmitry/README.md` - first-round dashboard with raw assets and cleaned summary
- `interviews/3-lead-ai-engineer/README.md` - recruiter-confirmed third-round format and grounded prep signals
- `interviews/2-central-ai--ivo/README.md` - prior round materials for the Ivo interview
- `prep/2-central-ai--ivo-day-of-card.md` - **day-of quick reference** for the Ivo interview
- `prep/2-central-ai--ivo-story-bank.md` - pre-formatted STAR stories mapped to Finom
- `prep/2-central-ai--ivo-rehearsal-flow.md` - **walk-through rehearsal** for the actual interview
- `prep/2-central-ai--ivo-48h-prep-focus.md` - highest-signal short prep note for the next interview
- `prep/finom-ai-competitive-landscape.md` - AI competitive landscape analysis
- `prep/multi-agent-system-architecture-for-fintech.md` - MAS architecture prep (matches Finom's public AI Accountant design)
- `prep/german-sme-accounting-domain-primer.md` - German tax forms and SME accounting domain vocabulary
- `code/README.md` - MAS coordination pipeline, live rehearsal, and eval harness code demos
- `code/python-sync-async-refactor/README.md` - Python drill: bad sync AI REST API to async refactor with contract parity
- `../eu-ai-act-regulatory-prep.md` - EU AI Act awareness (shared with Delphyr)
- `finom_cheatsheet.pdf` - compact company and role cheat sheet

## Company Notes
- Amsterdam-based SMB financial platform spanning banking, invoicing, and AI accounting.
- Existing prep notes now center on 200K+ accounts, AI Accountant GA for all German customers, 500+ employees, and strong growth after the June 2025 Series C.
- Competitive set called out in existing materials: Qonto, Revolut Business, N26 Business, and Tide.

## AI and Product Direction
- Finom is pushing beyond "AI sprinkled on top" toward agentic workflows that proactively complete work.
- **The AI Accountant is a distributed multi-agent system (MAS)** — multiple autonomous AI agents collaborating within a shared environment. This is publicly stated.
- **5-10 active AI products** with sub-agents connected to dedicated MCP servers and backend microservices (confirmed from Confident AI case study).
- Auto-reconciliation engine matches invoices to payments with ~99% accuracy.
- Accounting appears to be the first major workflow area rebuilt around this model.
- Example from the first interview summary: the system drafts a preliminary tax record, asks for approval, and then files it.
- The broader platform vision includes proactive cash-flow monitoring, missing-item detection, and negative-trend alerts.
- **DATEV export now live** — AI Accounting output flows directly to the German accountant's professional workflow.
- **ZM reports (EC Sales List) shipped for Germany** — roadmap items becoming production features.
- **F24 tax payments live for Italy** — Italy is now a live tax-filing market (third after Germany).
- Target: 1 million business customers by end of 2026.

## Team and Stack Signals
- Interviewers in scope so far:
  - Dmitry Ivanov - CTO
  - Ivo Dimitrov - co-founder, **Chief AI Officer (CAIO)** per TheOrg; recruiter described him as running the central AI team
  - Interview 3 interviewer: Viktar Adynets
- Stack notes from current materials:
  - Python for LLM-heavy services and agent harnesses
  - .NET / C# across the broader backend platform
  - likely polyglot environment with AI work embedded into product delivery
- Org notes now grounded by the Ivo conversation:
  - separate `ML team` and `AI team`
  - AI team focuses on LLM/product-pattern work rather than classic predictive ML
  - some people are embedded in domains, others move across projects
  - explicit `adoption` stream exists to spread AI-first behavior across the company
  - useful mental model: `core > layers > product`, with `central > integration > embed(domain)`

## Interview Timeline
- Monday, March 31, 2026 - first conversation with Dmitry Ivanov in `interviews/1-introduction--dmitry/`
- Sunday, April 6, 2026 - recruiter update that Ivo wants to meet
- Wednesday, April 8, 2026 - second interview with Ivo in `interviews/2-central-ai--ivo/`
- Thursday, April 9, 2026 - recruiter moved you to Interview 3: 30 minutes of technical questions with a Senior AI Engineer, then 60 minutes of live problem-solving with Claude Code or Codex

## Current Status: CLOSED — No Offer

**Outcome:** Rejected after Interview 3 (April 14, 2026). Finom communicated a profile mismatch at the final round — they are looking for a different profile than what this application presented.

**Timeline outcome:**
- Interview 1 (Dmitry) — positive, moved forward
- Interview 2 (Ivo) — positive, moved to technical round
- Interview 3 (Viktar) — final round, no offer due to profile mismatch

**What this means:** The role they need filled has different requirements than the Senior AI Engineer positioning this workspace was built around. This is a calibration gap, not a skills gap — the prep work here is transferable.

**Observations for future reference:**
- Strongest angles identified (production AI systems, agentic workflows, evaluation discipline) remain valid positioning for similar roles
- The MAS architecture, multi-agent coordination, and Finom domain research in `insights/` and `prep/` are high-value reusable material
- The interview workspace structure (dashboard, round folders, prep/insights split) worked well — use this pattern going forward
- Cross-company insights connecting Finom and Delphyr prep: `../cross-company-insights.md`

## New Insights (Apr 11-12)
- `insights/live-coding-with-ai-agents-advanced-patterns.md` — three modes of agent-assisted coding, verbal checkpoints, common pitfalls for live rounds
- `insights/confidence-calibration-deep-dive.md` — ECE, Platt scaling, per-market calibration, calibration drift monitoring, earned autonomy as a measurable ratchet
- `insights/agent-safety-transaction-semantics.md` — commit/rollback architecture, autonomy ladder, compensation chains, HITL taxonomy
- `insights/design-patterns-correctness-sensitive-ai.md` — 7 patterns: confidence threshold cascade, HITL selection, market config schema, error taxonomy, staging/commit, MCP tool boundary, evasion detection
- `insights/mental-models-interview-discussions.md` — 7 mental models for explaining architecture choices: earned trust, separation of concerns, market config as data, calibration, compensation chains, agent as contract, observability
- `insights/observability-production-agents.md` — production tracing, confidence histograms, correction feedback loops, canary routing, A/B testing agents, alert taxonomy
- `insights/mas-coordination-patterns.md` — MAS coordination: orchestrator-worker, fan-out/fan-in, saga pattern, circuit breaker, shared state, MAS testing pyramid
- `prep/proposals/3-sync-async-python-refactor-pack.md` — persisted implementation spec for Python sync→async interview drill

## Best Angles
- Production AI systems with end-to-end ownership
- Agentic workflows over document-heavy operations
- Evaluation, observability, and reliability discipline
- Strong product-engineering judgment without overclaiming fintech specialization
- Proactive workflow execution with explicit approval and control surfaces
- Ability to use `Codex` / `Claude` to accelerate delivery without losing rigor

## Open Questions For The Next Round
- What would this role own first if hired?
- How does Finom evaluate quality and failure handling for accounting and financial workflows?
- Where do they currently see AI coding tools increasing speed versus causing drag?
- How should central, integration, and embedded domain teams share ownership without creating friction?

## Maintenance Notes
- Keep this README as the one-minute dashboard for current stage, next action, and strongest support files.
- Update the relevant `interviews/<round>/` folder first after each interview, then refresh the timeline and current status here.
