# Entity: Model Context Protocol

type: systems
aliases:
  - MCP
  - MCP-based
tags:
  - ai-engineering
  - tools
  - architecture
relationships:
  - finom
  - claude-code
  - codex
confidence: medium
generated_by: scripts/extract-entities.ts
generated_at: 2026-04-13T03:14:54.581Z

## Evidence
- [topics/jobs/finom/code/README.md](/Users/fysp/personal/learning/topics/jobs/finom/code/README.md:149) — matched `MCP`: ## 6. MCP Accounting Skills Server
- [topics/jobs/finom/code/README.md](/Users/fysp/personal/learning/topics/jobs/finom/code/README.md:151) — matched `Model Context Protocol`: `mcp-accounting-server.ts` — A Model Context Protocol skill server exposing accounting tools across 5 EU markets.
- [topics/jobs/finom/code/README.md](/Users/fysp/personal/learning/topics/jobs/finom/code/README.md:155) — matched `MCP`: - **MCP tool contracts**: Three tools with Zod input/output schemas (categorize, VAT, booking)
- [topics/jobs/finom/code/README.md](/Users/fysp/personal/learning/topics/jobs/finom/code/README.md:158) — matched `MCP`: - **End-to-end workflow**: Chains all three tools with confidence routing to demonstrate the composable MCP architecture
- [topics/jobs/finom/code/README.md](/Users/fysp/personal/learning/topics/jobs/finom/code/README.md:163) — matched `MCP`: Dmitry said "the whole platform is going to be stitched with MCP-based interfaces." This demo makes that architecture concrete. Each tool is stateless, independently testable, and composable. The orchestration lives in the client, not the tool server.
- [topics/jobs/finom/code/README.md](/Users/fysp/personal/learning/topics/jobs/finom/code/README.md:168) — matched `MCP`: bun run mcp-server
- [topics/jobs/finom/code/README.md](/Users/fysp/personal/learning/topics/jobs/finom/code/README.md:173) — matched `MCP`: "I built an MCP skill server with three accounting tools — categorization, VAT, and booking — across five EU markets. The key design decision was making VAT and booking deterministic while keeping categorization AI-powered. Adding a new market is just a policy config object — the workflow shape and tool contracts don't change. This maps directly to how Finom can scale from Germany to France without rewriting the pipeline."
- [topics/jobs/finom/experiments/mcp-accounting-skills/README.md](/Users/fysp/personal/learning/topics/jobs/finom/experiments/mcp-accounting-skills/README.md:1) — matched `MCP`: # MCP Accounting Skills Server
- [topics/jobs/finom/experiments/mcp-accounting-skills/README.md](/Users/fysp/personal/learning/topics/jobs/finom/experiments/mcp-accounting-skills/README.md:3) — matched `MCP`: A working MCP server exposing German SMB accounting tools — transaction categorization, VAT calculation, and double-entry booking. Built to demonstrate MCP fluency for the Finom 2nd round interview.
- [topics/jobs/finom/experiments/mcp-accounting-skills/README.md](/Users/fysp/personal/learning/topics/jobs/finom/experiments/mcp-accounting-skills/README.md:13) — matched `MCP`: cd topics/jobs/finom/experiments/mcp-accounting-skills
- [topics/jobs/finom/experiments/mcp-accounting-skills/README.md](/Users/fysp/personal/learning/topics/jobs/finom/experiments/mcp-accounting-skills/README.md:21) — matched `MCP`: # Run the MCP server (stdio transport for Claude Desktop)
- [topics/jobs/finom/experiments/mcp-accounting-skills/requirements.txt](/Users/fysp/personal/learning/topics/jobs/finom/experiments/mcp-accounting-skills/requirements.txt:1) — matched `MCP`: mcp>=1.0.0
