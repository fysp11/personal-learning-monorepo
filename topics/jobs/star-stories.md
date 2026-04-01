# STAR Story Bank — Mapped to Both Companies

Pre-structured stories in STAR format, with explicit mapping to each company's needs. Each story has a "deploy when" trigger so you know exactly when to use it.

---

## Story 1: Self-Healing Scraper Agent

### STAR
**Situation**: Commodity website data collection with 30+ sources. Websites changed HTML structure regularly, breaking scrapers. ~20 hours/week of manual tag maintenance.

**Task**: Eliminate manual maintenance by building an autonomous self-healing system.

**Action**:
- Set up Sentry monitoring for scraper failures
- Built agent triggered by alerts: analyze new site structure → propose updated tags → test against known-good data → deploy if passing
- Introduced LLM-as-judge scoring for quality measurement
- Integrated DSPy for self-improving prompts with metrics
- Decomposed monolithic agent into specialized skills (detection, analysis, fix-proposal, testing)

**Result**: 80-95% reduction in maintenance effort. Agent runs overnight, fixes issues in ~10 minutes. Saved ~20 hours/week engineering time. Evolved into proactive page quality monitoring.

### Deploy When
| Trigger Question | Company |
|-----------------|---------|
| "Tell me about production AI agents you've built" | Both |
| "How do you handle agent reliability?" | Both |
| "How do you approach agent evaluation?" | Both |
| "Give me an example of automation ROI" | Both |
| "How do you handle failure recovery in agents?" | Delphyr |
| "Tell me about production-scale agent work" | Finom |

### Tailored Ending
- **For Delphyr**: "The reliability patterns — staged actions, confidence scoring, rollback capability — translate directly to clinical workflows where the stakes are even higher."
- **For Finom**: "The same architecture applies to financial agents — confidence-based routing ensures we never silently miscategorize a transaction."

---

## Story 2: Document Processing Pipeline at Scale

### STAR
**Situation**: Client needed to process 30-60K documents per day — classification, data extraction, enrichment. Manual process was consuming 60-80% of team's time.

**Task**: Build an automated pipeline that classifies, extracts, and enriches documents at scale with high accuracy.

**Action**:
- Designed multi-stage pipeline: ingestion → classification → extraction → enrichment → validation
- Implemented hybrid approach: rule-based pre-filtering + LLM for complex classification
- Built structured output schemas (Pydantic) for every document type
- Created evaluation framework: human-annotated ground truth → automated scoring → continuous monitoring
- Set up Langfuse observability for tracing every document through the pipeline

**Result**: 60-80% reduction in manual effort. Processing 30-60K docs/day reliably. Sub-second latency for classification. Continuous accuracy monitoring caught model drift before users noticed.

### Deploy When
| Trigger Question | Company |
|-----------------|---------|
| "How do you handle document understanding at scale?" | Both |
| "Tell me about a data pipeline you built" | Both |
| "How do you balance automation with accuracy?" | Both |
| "Experience with receipt/invoice processing?" | Finom |
| "Experience with clinical document processing?" | Delphyr |

### Tailored Ending
- **For Delphyr**: "Clinical documents are more complex — semi-structured EHR data, free-text notes, imaging reports — but the pipeline architecture and evaluation approach are the same."
- **For Finom**: "Receipts and invoices are structured enough that accuracy should be higher than general documents. The key is handling the long tail — handwritten receipts, foreign-language invoices, unusual formats."

---

## Story 3: Hybrid Search at Scale (10M+ Records)

### STAR
**Situation**: RAG system needed to handle 10M+ records with sub-second latency. Pure semantic search was missing keyword-important results; pure keyword search missed semantically similar content.

**Task**: Build a hybrid retrieval system that combines semantic and keyword search for optimal recall and precision.

**Action**:
- Implemented hybrid search: pgvector for semantic + full-text search for keyword, with reciprocal rank fusion
- Tested multiple embedding models, benchmarked on domain-specific queries
- Built evaluation pipeline: precision@K, recall@K, nDCG measured against human-annotated relevance
- Optimized indexing: HNSW parameters tuned for latency vs. recall tradeoff
- Added query analysis: classify query intent to weight semantic vs. keyword differently

**Result**: 10M+ records, sub-second latency. Measurable improvement in retrieval quality vs. either approach alone. Query-adaptive weighting improved edge cases significantly.

### Deploy When
| Trigger Question | Company |
|-----------------|---------|
| "Tell me about your RAG experience" | Both |
| "How do you handle retrieval at scale?" | Both |
| "How do you choose between embedding models?" | Delphyr |
| "How would you build search for financial data?" | Finom |

### Tailored Ending
- **For Delphyr**: "For clinical data, I'd expect even more value from hybrid search — medical terms are precise (keyword matters) but clinical reasoning is nuanced (semantic matters). And you'd want separate indices for patient data vs. clinical knowledge with different access controls."
- **For Finom**: "For financial data, the challenge is different — transaction descriptions are short and noisy, merchant names vary, and historical categorization is the strongest signal. I'd weight user history heavily alongside semantic search."

---

## Story 4: NextGear Platform Rebuild

### STAR
**Situation**: NextGear (Amsterdam) had only spreadsheets for engineering analytics. No visibility into team performance, delivery metrics, or resource allocation.

**Task**: Build an engineering analytics platform from the ground up. Led a team of 3 engineers.

**Action**:
- Designed the data model and pipeline architecture
- Built ingestion from multiple sources: Jira, GitHub, CI/CD, Slack
- Implemented dashboards for engineering leadership
- Led 3 engineers through design → implementation → deployment
- Iterated based on user feedback: what metrics actually mattered vs. vanity metrics

**Result**: 40-60% speedup in reporting. 20-30% adoption lift as managers found insights useful. Platform became the standard for engineering decision-making.

### Deploy When
| Trigger Question | Company |
|-----------------|---------|
| "Tell me about leading a team" | Both |
| "Have you built something from scratch?" | Both |
| "How do you approach a greenfield project?" | Both |
| "How do you handle stakeholder requirements?" | Finom |

### Tailored Ending
- **For Delphyr**: "Small team, high impact — exactly the dynamic you have. I thrive in environments where every person's contribution is visible and you ship meaningful work every week."
- **For Finom**: "This was about understanding what stakeholders actually need vs. what they ask for. The same product thinking applies to AI accounting — 'categorize my transactions' is the ask, but 'never worry about bookkeeping again' is the actual need."

---

## Story 5: Airflow/ClickHouse Migration

### STAR
**Situation**: Legacy report generation system was slow and unreliable. Reports took hours, often failed, no orchestration.

**Task**: Migrate to modern orchestrated pipelines with fast analytical queries.

**Action**:
- Migrated to Airflow for pipeline orchestration: DAGs, retry logic, monitoring, alerting
- Introduced ClickHouse for analytical queries: columnar storage, 30x speedup on report generation
- Built monitoring and alerting for pipeline health
- Documented and trained team on the new stack

**Result**: 30x improvement in report generation time. Reliable, monitored, self-healing pipelines. Team could now iterate on analytics without worrying about infrastructure.

### Deploy When
| Trigger Question | Company |
|-----------------|---------|
| "Experience with data platform work?" | Both |
| "How do you handle migration projects?" | Both |
| "Experience with ClickHouse?" | Finom (Dmitry opened a ClickHouse PR!) |
| "How do you approach observability?" | Both |

### Tailored Ending
- **For Delphyr**: "Pipeline reliability is everything when you're processing clinical data. A failed pipeline in healthcare isn't just an engineering issue — it could mean a doctor doesn't have the data they need for a decision."
- **For Finom**: "I noticed Dmitry opened a ClickHouse PR — I'd love to hear about your analytics stack. My experience with ClickHouse + Airflow translates directly to financial reporting pipelines."

---

## Story 6: LLM Evaluation Framework

### STAR
**Situation**: AI agents were deployed but accuracy was measured anecdotally. No systematic way to know if agents were improving or degrading over time.

**Task**: Build a comprehensive evaluation framework for LLM-based agents.

**Action**:
- Designed multi-level evaluation: retrieval quality → generation accuracy → action correctness
- Implemented LLM-as-judge with structured rubrics and scoring
- Built automated evaluation pipeline that runs on every prompt/model change
- Created evaluation datasets with expected behaviors (not just expected outputs)
- Integrated Langfuse for production observability: trace every inference, track cost, measure latency

**Result**: Caught model degradation within 24 hours (previously took weeks to notice). Enabled confident prompt iteration: change, evaluate, ship if better. Made quality a measurable metric, not a feeling.

### Deploy When
| Trigger Question | Company |
|-----------------|---------|
| "How do you measure AI quality?" | Both |
| "How do you know your agents are working correctly?" | Both |
| "How do you handle model degradation?" | Both |
| "How do you approach clinical accuracy measurement?" | Delphyr |
| "How do you ensure financial accuracy?" | Finom |

### Tailored Ending
- **For Delphyr**: "In clinical settings, I'd add domain expert review on a sample to calibrate the LLM judge, and I'd track 'dangerous misses' as a separate critical metric — cases where the system missed something a doctor should have seen."
- **For Finom**: "For financial accuracy, I'd split the metrics: category accuracy can tolerate some error (users correct it), but VAT accuracy must be near-perfect because it's a compliance issue. Different thresholds for different consequences."

---

## Quick Reference: Which Story for Which Question

| Question Theme | Best Story | Backup Story |
|---------------|-----------|--------------|
| Production agents | Self-Healing Scraper | Doc Processing |
| Scale/throughput | Doc Processing (30-60K/day) | Hybrid Search (10M+) |
| Agent evaluation | Eval Framework | Self-Healing Scraper |
| Team leadership | NextGear Platform | Airflow Migration |
| RAG/retrieval | Hybrid Search | Doc Processing |
| Data platforms | Airflow/ClickHouse | NextGear Platform |
| From-scratch building | NextGear Platform | Doc Processing |
| Reliability/safety | Self-Healing Scraper | Eval Framework |
| Observability | Eval Framework | Airflow/ClickHouse |
