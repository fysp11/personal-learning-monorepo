# Finom — Gap Mitigation: Turning Weaknesses Into Strengths

Based on the cheatsheet fit map and CTO call signals. The gaps are smaller here (Finom is a stronger fit overall), but addressing them proactively shows preparation depth.

---

## Gap 1: No Fintech Domain Experience

### The Concern
"You haven't worked in financial services. Do you understand the regulatory and domain complexities?"

### Bridge Strategy: First-Person SMB Experience + Transferable Reliability Patterns

**Script:**
> "I don't have traditional fintech experience, but I have direct first-person SMB financial experience:
>
> I run my own entity — Fysp Tech. I deal with invoicing, multi-country tax compliance, and expense management myself. I AM your target user. I know the pain of 'I have a receipt in my camera roll and I'll categorize it later' — which becomes 'it's tax filing time and I have 200 uncategorized transactions.'
>
> From a systems perspective, the engineering patterns in financial data are the same as what I've built in document processing: correctness is non-negotiable, every operation must be auditable, errors compound downstream, and you need idempotency because operations get retried.
>
> The domain-specific knowledge — SKR03 account codes, UStVA filing, SEPA payment rules — is learnable. The engineering mindset of 'this data must be correct because real money and legal compliance depend on it' is something I already live."

### Concrete Evidence to Build
- [ ] Memorize top 10 SKR03 codes for freelancers/SMBs (4650 Bewirtung, 4930 Bürobedarf, etc.)
- [ ] Walk through a UStVA filing process — what data is needed, when is it due, how is it submitted to ELSTER
- [ ] Sign up for Finom free tier and explore the product — note UX patterns, categorization flow
- [ ] Compare Finom to Qonto: sign up for Qonto trial too, note the differences in AI features

---

## Gap 2: No C#/.NET Experience

### The Concern
"Our core platform is C#/.NET. You've never shipped C# in production."

### Bridge Strategy: Polyglot Confidence + Focus Where You'll Spend Time

**Script:**
> "I haven't written production C#, but I've worked in polyglot environments — Python, TypeScript, Go — and the patterns transfer: dependency injection, async/await, strong typing, LINQ-like query patterns.
>
> Practically, the AI work where I'd spend most of my time is Python anyway — your LLM services, agent orchestration, document understanding. The C# interaction is at the service boundary: calling .NET services from Python agents, understanding the API contracts, reading C# code during debugging.
>
> I'm comfortable ramping up on C# — the language isn't the hard part, understanding the domain and architecture is. And .NET 8+ with minimal APIs actually looks a lot like FastAPI or Express.
>
> For the MCP architecture you're building, the language boundary becomes even less relevant — MCP is protocol-level, not language-level. A Python agent calling a C# MCP server doesn't need to know it's C# underneath."

### Concrete Evidence to Build
- [ ] Build Experiment 3 from experiments.md: minimal C#/.NET service + Python AI service integration
- [ ] Write a simple .NET 8 minimal API (4-5 endpoints) to get comfortable with the syntax
- [ ] Read about C# async/await patterns — they're very similar to Python's
- [ ] Understand .NET DI (dependency injection) basics — it's pervasive in .NET codebases

---

## Gap 3: No PyTorch/TF Model Training

### The Concern
"Our JD mentions PyTorch/TensorFlow. You're API-focused, not model-training focused."

### Bridge Strategy: Production AI Systems > Training, But Willing to Deepen

**Script:**
> "My focus is production AI systems — taking models into reliable, observable services at scale. I work with model outputs extensively: structured extraction, evaluation, prompt optimization (DSPy), and quality monitoring. This is where the value is created for users.
>
> For training specifically: I understand the training loop, loss functions, fine-tuning approaches (LoRA, QLoRA), and evaluation methodology. I've evaluated fine-tuned vs. base models in production to decide when fine-tuning is worth the investment.
>
> The honest truth: for Finom's use case — transaction categorization, receipt understanding, financial summarization — the frontier is in prompt engineering, structured output, and agent orchestration, not in training custom models from scratch. You're calling GPT-4/Claude/Mistral APIs, not training a custom transformer. The skill that matters is making those models work reliably in production.
>
> That said, if the team needs grow in the training direction — for example, fine-tuning a categorization model on Finom-specific transaction data — I'm eager to deepen there."

### Concrete Evidence to Build
- [ ] Fine-tune a small model (e.g., DistilBERT) on transaction categorization data as a demo
- [ ] Understand LoRA/QLoRA for efficient fine-tuning
- [ ] Know when fine-tuning beats prompting: large volume, consistent format, cost optimization

---

## Gap 4: No Kafka/Flink (Event Streaming)

### The Concern
"Our event-driven architecture uses message buses. You've used Airflow, not Kafka."

### Bridge Strategy: Distributed Systems Concepts Transfer

**Script:**
> "I've worked with Airflow for orchestrated pipelines at scale — DAGs, task dependencies, retry logic, monitoring. The concepts transfer directly to event-driven architectures:
>
> - **Ordering guarantees** — understanding when order matters and when it doesn't
> - **At-least-once vs. exactly-once delivery** — and why idempotency is the practical answer
> - **Backpressure** — handling when consumers can't keep up with producers
> - **Dead letter queues** — for events that fail processing
>
> Kafka specifically adds partitioning, consumer groups, and log compaction — these are new to me in practice but well-understood conceptually. The pattern of 'transaction event emitted → multiple consumers react independently' is the same whether it's Kafka, RabbitMQ, or Azure Service Bus.
>
> For a .NET shop, I'd expect either Kafka (most common), RabbitMQ (simpler), or Azure Service Bus (if Azure-hosted). The agent integration pattern is the same regardless: agents react to events, process, and emit results."

### Concrete Evidence to Build
- [ ] Set up a local Kafka with Docker and produce/consume transaction events
- [ ] Understand Kafka consumer groups and partitioning
- [ ] Know the difference: Kafka (log-based, durable) vs. RabbitMQ (queue-based, transient) vs. Azure Service Bus (.NET-native)

---

## Gap 5: No Fraud/Anomaly Detection

### The Concern
"Financial services need fraud detection. No experience there."

### Bridge Strategy: Pattern Maps to LLM Quality Checks

**Script:**
> "The pattern is: streaming classification with confidence thresholds, human-in-the-loop escalation for ambiguous cases, and false-positive management. I've built exactly this for agent quality — confidence-based routing where low-confidence outputs get escalated to human review.
>
> For transaction anomaly detection specifically: 'is this transaction unusual for this user?' is a classification problem I can reason about. Historical baseline, deviation scoring, alert thresholds. The domain context (what makes a transaction 'suspicious' in fintech) is learnable; the engineering pattern of streaming classification + escalation is something I've done."

---

## Priority: What to Do This Week

| Priority | Gap | Action | Time |
|----------|-----|--------|------|
| 1 | Fintech domain | Sign up for Finom + Qonto, explore products | 1 hour |
| 2 | Fintech domain | Memorize SKR03 basics, UStVA process | 1 hour |
| 3 | C#/.NET | Build minimal .NET 8 API + Python client | 3 hours |
| 4 | Kafka | Docker Kafka + transaction event demo | 2 hours |
| 5 | PyTorch | Fine-tune DistilBERT on categorization task | 3 hours |
