# Job Opportunities — Cross-Company Comparison & Strategy

## Side-by-Side Comparison

| Dimension | Delphyr | Finom |
|-----------|---------|-------|
| **Domain** | Clinical AI / Healthcare | Fintech / SMB Banking |
| **Stage** | Early-stage, small team | Series C, 500+ employees |
| **Funding** | Unknown (likely smaller) | €300M+ |
| **Location** | Netherlands (Amsterdam area) | Amsterdam HQ |
| **Team size** | ~6 people (2 seniors, DS, juniors) | 500+ (AI Core team ~10-15?) |
| **Tech stack** | Python, custom search/embeddings | C#/.NET + Python polyglot |
| **AI maturity** | In-house everything, research-oriented | Production MAS, scaling |
| **Regulation** | MDR (medical device), very heavy | EMI license, PSD2, moderate |
| **Role scope** | Wide — agent architect in small team | Focused — Sr. AI eng in squad |
| **Growth potential** | High ownership, shape the product | Career ladder, brand, scale |
| **Interview status** | 1st round done, next steps TBD | 1st round done, 2nd confirmed |

## What Each Opportunity Offers

### Delphyr — The Case For
1. **Massive impact per person**: Small team = you shape the entire agent architecture
2. **Deeply meaningful work**: Healthcare AI that directly helps doctors and patients
3. **Technical depth**: Building search, embeddings, agents from scratch — not stitching APIs
4. **MDR certification experience**: Rare and valuable — very few AI engineers have this
5. **Privacy/compliance depth**: Medical data is the hardest privacy challenge — transferable expertise
6. **First-mover advantage**: One of the first MDR-certified AI clinical decision support tools

### Delphyr — The Risks
1. **Small team/company**: Less stability, more dependent on funding
2. **Heavy regulation**: MDR compliance can slow down product iteration
3. **Domain steep learning curve**: Clinical medicine is complex and high-stakes
4. **Visibility**: Less brand recognition than a well-funded fintech

### Finom — The Case For
1. **Well-funded and profitable**: €300M+ raised, EBITDAM profitable — stability
2. **Scale**: 125K+ customers, growing to 1M — real production challenges
3. **Cutting-edge architecture**: MCP-based multi-agent system at scale
4. **Strong CTO**: Dmitry has deep systems background (TomTom, Picnic) — good mentor
5. **Career growth**: Large org with structured career paths
6. **Market timing**: AI-native accounting is a greenfield opportunity with massive TAM

### Finom — The Risks
1. **Larger org**: More process, less individual ownership per feature
2. **C#/.NET learning curve**: Secondary language you'd need to pick up
3. **Domain gap**: No fintech background (though bridgeable)
4. **AI team merging into product**: Organizational flux — role definition may shift

## Shared Technical Themes to Invest In

Both roles converge on these core competencies — study these regardless of which progresses:

### 1. Agent Safety & Reliability
- Commit/rollback patterns for agentic actions
- Confidence-based routing (auto vs. human review)
- Evaluation frameworks (LLM-as-judge, domain-specific metrics)
- Observability for multi-agent systems

### 2. Multi-Agent Orchestration
- Agent coordination and handoff patterns
- Failure isolation and recovery
- Skill/tool composition
- State management across agent chains

### 3. RAG at Scale
- Hybrid search (semantic + keyword)
- Domain-specific embedding models
- Retrieval evaluation (precision, recall, nDCG)
- Privacy-preserving retrieval

### 4. Evaluation Frameworks
- Granular, action-level evaluation (not just end-to-end)
- LLM-as-judge with domain expertise
- Continuous evaluation in production (not just pre-deployment)
- DSPy for systematic prompt optimization

### 5. European Regulatory Context
- GDPR data handling (both roles operate in EU)
- Domain-specific regulation (MDR for Delphyr, EMI/PSD2 for Finom)
- Data residency and sovereignty requirements

## Preparation Timeline

### Week of Apr 1-7 (NOW)
- [x] Analyze both interview source records
- [x] Create structured preparation materials
- [ ] Research both companies deeply (web, LinkedIn, product demos)
- [ ] Build MCP skill server experiment (relevant to Finom)
- [ ] Study MDR classification process (relevant to Delphyr)

### Week of Apr 7-14
- [ ] Practice system design answers for both roles
- [ ] Build mini eval framework experiment (relevant to both)
- [ ] Deep-dive into EU tax regimes (Finom) and clinical guidelines (Delphyr)
- [ ] Prepare STAR stories mapped to each company's needs

### Ongoing
- [ ] Follow both companies on LinkedIn for updates
- [ ] Read Dmitry's posts (Finom CTO) for conversation hooks
- [ ] Study clinical AI papers (Delphyr)
- [ ] Experiment with C#/.NET + Python integration (Finom)

## Strategic Decision Framework

When evaluating offers (if both progress), consider:

1. **Learning velocity**: Where will you grow fastest as an engineer?
2. **Impact visibility**: Where will your work matter most?
3. **Market value**: Which experience is more scarce/valuable?
4. **Personal mission**: Which domain resonates more deeply?
5. **Practical factors**: Compensation, work-life balance, visa support, team culture
