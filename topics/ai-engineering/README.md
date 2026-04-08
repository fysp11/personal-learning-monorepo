# AI Engineering

This workspace is for learning practical AI engineering with a strong bias toward:
- production AI over demos
- orchestration over raw model hype
- deterministic controls around probabilistic systems
- business-critical workflows such as finance, accounting, compliance, and operations

The focus here is shaped by the Finom notes: central AI vs embedded teams, proactive workflows, high-trust automation, evaluation, observability, and safe rollout.

## Core Thesis

For this topic, `AI engineering` means:

- turning ambiguous business problems into reliable AI systems
- wrapping models with retrieval, tools, rules, approvals, and monitoring
- knowing where automation should stop
- making systems measurable, explainable, and safe enough for real operations

This is not primarily a model-research workspace.

It is a systems-and-product workspace.

## What To Know By Heart

These are the concepts and technologies you should be able to explain clearly without hand-waving.

### 1. LLM system design

You should know:
- prompt design basics: system prompts, task decomposition, structured outputs
- context management: what to include, what to exclude, how to control token pressure
- function/tool calling: when the model should act vs when code should act
- multi-step orchestration: planner, executor, verifier, fallback paths
- failure modes: hallucination, instruction drift, tool misuse, over-confidence

Why it matters:
- this is the baseline for any production AI workflow
- Finom-like environments care about orchestration quality more than model novelty

### 2. RAG and grounding

You should know:
- embeddings and vector search
- chunking tradeoffs
- hybrid retrieval: semantic + keyword
- metadata filtering
- reranking
- citation / evidence attachment
- when not to use RAG

Why it matters:
- financial and compliance workflows need grounded outputs, not free-form guessing
- retrieval is often the difference between useful assistance and un-auditable nonsense

### 3. Deterministic guardrails

You should know:
- schema validation
- typed outputs
- rule engines
- confidence thresholds
- allowlists / denylists
- constrained generation
- approval flows
- fallback and rollback behavior

Why it matters:
- this is the core Finom pattern: deterministic rails around probabilistic engines
- in accounting or tax contexts, graceful degradation is not enough

### 4. Evaluation

You should know:
- offline evals vs online evals
- task-specific eval design
- golden sets / benchmark sets
- regression testing for prompts and workflows
- LLM-as-judge tradeoffs
- human review calibration
- metrics for precision, recall, abstention, latency, and cost

Why it matters:
- if you cannot evaluate the workflow, you do not control the workflow
- central AI teams create leverage through shared eval patterns

### 5. Observability and monitoring

You should know:
- request tracing across model + retrieval + tools
- prompt / response logging with privacy boundaries
- error taxonomy
- latency breakdowns
- confidence and abstention monitoring
- drift detection
- escalation monitoring

Why it matters:
- AI systems fail in messy, distributed ways
- production ownership requires runtime visibility, not just offline benchmarks

### 6. Human-in-the-loop workflow design

You should know:
- approval checkpoints
- exception routing
- reviewer UX
- low-confidence handling
- high-impact action gating
- audit trails for who approved what and why

Why it matters:
- in high-stakes domains, automation is usually partial
- trust is built by making escalation and review explicit

### 7. Agentic workflow architecture

You should know:
- when an agent is actually needed
- when a deterministic workflow is better than an autonomous agent
- state machines and graph-based orchestration
- retries, idempotency, and step isolation
- tool permissions and execution boundaries
- delegation patterns

Why it matters:
- Finom-style workflows are closer to controlled agent graphs than to chatbots
- the engineering challenge is workflow safety, not agent theater

### 8. Data and document pipelines

You should know:
- OCR and document parsing basics
- invoice / receipt extraction flows
- normalization into structured records
- reconciliation against transactions or ledgers
- handling ambiguous or low-quality input

Why it matters:
- document-heavy workflows are one of the strongest AI opportunities in finance and operations
- this is one of the most obvious Finom-relevant workflow classes

### 9. Build vs buy

You should know:
- when to use hosted foundation models
- when to add your own control layer
- where proprietary value actually lives
- how to compare vendors on latency, reliability, privacy, and cost
- why most teams should not train their own frontier models

Why it matters:
- founder-level AI conversations care about durable leverage, not just implementation
- the differentiator is often workflow design, evaluation, and integration

### 10. Product judgment for AI

You should know:
- signal vs noise in proactive AI
- when an alert is useful vs spam
- when a recommendation should be passive, proactive, or automatic
- how to measure trust and adoption
- what should be centralized vs embedded in product teams

Why it matters:
- AI engineering is not only technical
- Finom notes repeatedly point to org design, workflow value, and selective centralization

## Technologies To Be Comfortable With

This is the practical stack to understand well enough to discuss, prototype, and evaluate.

### Model APIs and inference

- OpenAI / Anthropic / Gemini style API patterns
- local inference tradeoffs
- model routing
- structured output modes
- batch vs real-time inference

### Retrieval stack

- vector databases: Pinecone, Weaviate, Qdrant, pgvector
- keyword search: Elasticsearch / OpenSearch / Postgres full-text
- rerankers
- embeddings pipelines

### Orchestration frameworks

- LangGraph
- LangChain
- workflow-first designs without heavy frameworks

What matters most:
- understand the pattern, not just the library names

### Backend and platform

- Python
- TypeScript / Node.js
- FastAPI or equivalent service layer
- queues / async jobs
- Postgres
- Redis
- object storage

### Observability

- OpenTelemetry concepts
- logs, traces, metrics
- prompt / tool tracing systems
- evaluation dashboards

### Security and governance

- PII handling
- secrets management
- audit logs
- permission boundaries for tools
- environment separation

## Finom-Shaped Learning Priorities

If you want this topic to stay aligned with the strongest Finom signals, prioritize these areas first:

1. `Evaluation and observability`
2. `Deterministic controls for high-stakes workflows`
3. `RAG for policy / rules / document-backed tasks`
4. `Agentic workflow design with approvals and fallbacks`
5. `Central AI vs embedded product team design`
6. `Proactive AI that avoids noisy, low-value alerts`

## Folder Use

- `prep/`
  Use for active study notes, topic breakdowns, flashcards, and interview-style question banks.

- `resources/`
  Use for canonical papers, docs, blog posts, architecture references, and curated reading lists.

- `experiments/`
  Use for prototypes, scripts, small services, notebooks, and eval harnesses.

- `artifacts/`
  Use for generated summaries, study decks, NotebookLM packs, and reusable outputs.

## Good Study Tracks

### Track 1: Reliable AI workflows

Study:
- structured outputs
- validation
- abstention
- approval design
- offline and online evals

Build:
- a workflow that extracts data from a document, validates it, and routes low-confidence cases to review

### Track 2: RAG for regulated knowledge

Study:
- chunking
- retrieval quality
- metadata filters
- citations
- evidence-backed answers

Build:
- a small assistant that answers only from a trusted corpus and cites its sources

### Track 3: Central AI platform thinking

Study:
- what capabilities should be shared
- what should stay with product squads
- how to avoid duplicated prompt / eval / tooling work

Build:
- a minimal shared evaluation and tracing layer that two different workflows can use

## Practical Standard

If you cannot explain:
- how the system fails
- how the system is evaluated
- how the system is monitored
- where human review enters
- why this should be automated at all

then you do not understand the AI system well enough yet.
