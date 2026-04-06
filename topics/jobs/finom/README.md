# Finom

## Snapshot
- Company: Finom
- Focus: SMB financial platform combining banking, invoicing, and AI accounting
- Relevant role: Senior AI Engineer
- Main interview artifact: `finom_cheatsheet.pdf`
- Conversation artifact: `interviews/Mar 31 at 12-29.txt`

## What We Have
- `finom_cheatsheet.pdf`: strong prep summary for the CTO conversation with company context, fit map, gaps, and suggested questions.
- `interviews/Mar 31 at 12-29.txt`: transcript fragment from the March 31, 2026 conversation.
- `interviews/Mar 31 at 12-29.m4a`: source audio recording.

## Company Notes
- Amsterdam-based SMB challenger bank / financial platform.
- Product scope called out in prep notes: banking, invoicing, and AI accounting in one mobile-first platform.
- Cheatsheet notes: 125K+ customers across DE, FR, IT, ES, NL; 500+ employees; Series C in June 2025; profitability and strong ARR growth were highlighted there.
- Growth target noted in cheatsheet: 1M business customers by end of 2026.
- Competitive set noted in cheatsheet: Qonto, Revolut Business, N26 Business, Tide.

## AI / Product Direction
- Finom is pushing beyond "AI sprinkled on top" toward agentic workflows that proactively complete work.
- Accounting was described as the first major area rebuilt around this model.
- Example workflow from the transcript: the system notices it is time to prepare a preliminary tax record, drafts it, asks for approval, and then files it.
- The broader vision is a platform that proactively performs jobs, monitors cash flow, flags missing items, and warns about negative trends.
- Internal naming mentioned in the transcript: `AICore` / `AIC core`; the speaker also noted the scope is growing beyond that label.

## Team / Engineering Notes
- Organization is split between core platform/infrastructure and product engineering domains.
- Product engineering domains are vertically aligned squads built around missions.
- Current direction is to spread AI capabilities across the platform rather than isolate "AI teams" from "traditional product teams."
- The transcript suggests Finom is moving away from AI engineer as a fully separate craft and toward product engineers with stronger AI specialization.
- There is still a core AI-oriented team working on foundational experiences.
- This role would likely sit in a product-facing team working at the "bleeding edge."

## Stack Notes
- `Python`: used heavily for LLM-powered services and agent-related harnesses.
- `.NET / C#`: core backend engineering runtime across the platform.
- The speaker framed the environment as effectively polyglot, with Python added where it makes more sense than building AI harnesses in C#.
- Cheatsheet also suggests an analytics/data angle worth probing, including ClickHouse.

## Interview Signals
- The conversation ended with a clear positive signal: "it's worth continuing the conversation."
- Next step mentioned: follow-up conversation with the CTO's colleague, `Rita`, for a deeper discussion on experience and fit.
- The transcript also contains useful answers to ask/follow up on:
- Where AI sits organizationally.
- How AI specialization is treated inside engineering.
- How cross-stack ownership works for agentic products.

## Fit Summary From Existing Notes
- Strongest overlaps called out in the cheatsheet:
- Multi-agent orchestration
- RAG + tool calling
- Document understanding pipelines
- Quality / measurement / observability
- Kubernetes / cloud / CI/CD
- Main gaps called out in the cheatsheet:
- Model training with PyTorch / TensorFlow / Hugging Face
- Direct fintech domain experience
- Fraud / anomaly detection
- Kafka / Flink depth

## Good Questions Already Prepared
- How inter-agent coordination and failure isolation work.
- How quality is measured for domain-heavy tasks like tax categorization.
- How Finom handles multi-country expansion in AI/accounting workflows.
- Whether AI engineers are embedded in squads or organized as a platform team.
- Balance of new AI feature development vs reliability/observability hardening.

## Gaps In The Workspace
- `CLAUDE.md` only says to read `AGENTS.md` first.
- `AGENTS.md` is empty.
- This `README.md` was empty before this summary.
- The transcript appears partial; if more complete notes exist elsewhere, they are not in this folder.
