# MCP Accounting Skills Server

A working MCP server exposing German SMB accounting tools — transaction categorization, VAT calculation, and double-entry booking. Built to demonstrate MCP fluency for the Finom 2nd round interview.

## Key Design Decisions
1. **VAT calculation is deterministic** (rule engine, not LLM) — correctness is non-negotiable for tax
2. **Categorization is LLM-powered** (with confidence scoring) — judgment calls benefit from AI
3. **Booking entries follow SKR03** — standard German chart of accounts
4. **Confidence-based routing** — high confidence auto-books, low confidence queues for review

## Setup
```bash
cd topics/jobs/finom/experiments/mcp-accounting-skills
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
# Run the MCP server (stdio transport for Claude Desktop)
python -m accounting_skills

# Or test directly
python -m pytest tests/
```

## Claude Desktop Integration
Add to `~/.config/claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "accounting": {
      "command": "python",
      "args": ["-m", "accounting_skills"],
      "cwd": "/path/to/this/folder"
    }
  }
}
```
