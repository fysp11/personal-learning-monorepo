# Finom — 1st Interview Analysis (CTO Call)
**Date**: March 31, 2026 | **With**: Dmitry Ivanov (CTO) | **Duration**: ~25 min

## Key Signals from the Interview

### What They're Building (AIC4 Platform)
- **Multi-agent accounting system** — agents that proactively react to events (not just chat assistants)
- **Example**: Agent sees it's time to create a preliminary tax record → prepares it → presents to user → user approves → files to government
- **Cash flow monitoring**: Proactive alerts on trends, missing items, negative trajectories
- **Vision**: Scale these agentic experiences across the ENTIRE product platform, not just accounting
- **MCP-based interfaces**: Connecting new "skills" to the platform easily — agents as composable capabilities

### Architecture Revelations
- **C#/.NET core backend** — NOT a Windows shop, just .NET as runtime
- **Python as secondary language** — specifically for LLM-powered services
- **Already multi-language**: They acknowledged it "didn't make sense to build all the harnesses in C#"
- **MCP as the interface layer**: Skills are connected via MCP, making it easy to add new agent capabilities
- **Product engineering domains**: Vertically-aligned squads around missions, multiple crafts per squad

### Team Structure & Where You'd Sit
- **Product engineering domains** — vertically aligned squads built around missions
- **AIC Core team** — the team building core agentic experiences (most likely landing spot)
- **AI engineer as craft merging with product engineering** — historically separate, now merging
- "You're a product engineer with AI flavor" — not a siloed AI specialist
- **Cross-stack work**: Backend systems + AI agents, not just agent building

### What Dmitry Values (Behavioral Signals)
1. **Product thinking over tech tourism**: "It's just that, you're a little bit more AI leaning"
2. **Production engineering standards**: "You thought about latency, observability" — agents need real engineering
3. **Anti-silo mentality**: Explicitly against separating AI engineers from product engineers
4. **Pragmatic language choices**: Chose Python for AI not out of trend but because C# harnesses didn't make sense
5. **Genuinely curious**: The DSPy mention got an authentic "that's pretty cool" — he's hands-on enough to appreciate novel tools

### Key Moment: DSPy Recommendation
- User recommended DSPy → Dmitry's genuine interest showed he's technically engaged
- This builds rapport and positions user as someone who brings knowledge TO the team, not just executes

## What Went Well
- **Mutual signal of interest**: "It sounds to me like it's worth continuing the conversation"
- **Next round confirmed**: With a colleague for deeper technical dive
- **Organic conversation flow**: Not an interrogation — genuine technical exchange
- **User demonstrated breadth**: Tooling awareness (DSPy), agent architecture understanding, production mindset

## Preparation Priorities for 2nd Round

### Technical Deep-Dives to Expect
1. **System design**: "Design an agent that handles German VAT categorization for incoming invoices"
2. **MCP architecture**: How would you structure skills/tools for a multi-agent accounting platform?
3. **Agent reliability**: How do you handle when an agent makes a wrong tax categorization?
4. **Observability**: How do you monitor and debug multi-agent systems in production?
5. **Scale**: Processing millions of transactions across 5 EU markets with different tax regimes

### Domain Knowledge to Build
1. **EU tax regimes** — German Steuerberater workflows, French TVA, Italian IVA, Spanish IVA, Dutch BTW
2. **SMB accounting workflows** — expense categorization, receipt matching, tax filing
3. **Banking compliance** — EMI license requirements, PSD2, transaction monitoring
4. **Finom's competitors** — Qonto, Revolut Business, N26 Business, Tide

### Architecture Questions for 2nd Round
1. "How do agents coordinate when multiple skills need to collaborate on a single workflow — e.g., receipt OCR → categorization → tax calculation?"
2. "What's the rollback strategy when an agent makes a tax categorization error that's already been filed?"
3. "How do you handle the cold-start problem for new markets — bootstrapping agents for a tax regime you haven't seen before?"
4. "What does the MCP skill registry look like — centralized catalog or decentralized discovery?"
5. "How do you evaluate agent performance across markets — same metrics for DE and FR, or market-specific?"

### Stories to Have Ready
| Story | Numbers | Map to Finom |
|-------|---------|-------------|
| Self-healing scraper | 80-95% maint reduction | Agent autonomy, production reliability |
| Doc processing pipeline | 30-60K docs/day | Scale, document understanding (receipts/invoices) |
| Hybrid search | 10M+ records, sub-second | RAG for financial data retrieval |
| NextGear platform | 40-60% speedup | Cross-stack engineering, team leadership |
| Eval frameworks | LLM-as-judge loops | Agent quality measurement |

## Competitive Advantage — What You Bring
1. **Production agent experience**: Not just prototypes — agents running in production with monitoring
2. **Multi-agent orchestration**: LangGraph + Agno + Pydantic AI — exactly what AIC4 needs
3. **Document processing at scale**: 30-60K docs/day maps directly to receipt/invoice processing
4. **Eval framework experience**: Critical for ensuring tax categorization accuracy
5. **MCP familiarity**: Already working with MCP-based architectures
6. **European context**: Moving to Europe, running own EU entity, understanding SMB pain firsthand
