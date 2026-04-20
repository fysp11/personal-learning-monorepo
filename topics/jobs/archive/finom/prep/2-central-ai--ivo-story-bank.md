# Finom Ivo Interview - Story Bank

Saved: 2026-04-07

## Purpose

Compact story bank with pre-formatted answers mapped to what Ivo likely cares about. Each story has a 60-second and 3-minute version.

---

## Story 1: Production Agent Systems at Scale

**Maps to:** central AI leverage, production reliability, agentic workflows

### 60-second version

Built and operated multi-agent pipelines processing 30-60K documents per day. The system handled document classification, enrichment, and routing through multiple LLM-powered stages with human review for edge cases. Key design choices: structured tool use, confidence-based routing, and observable per-stage metrics. Reduced manual processing effort by over 80% while keeping false-positive rates within operational tolerance.

### 3-minute version

The problem was scaling document-heavy operations where every document needed classification, data extraction, and action routing. Manual processes were bottlenecked at ~2K items/day per operator.

Architecture:
- Multi-stage pipeline: intake → classification → extraction → enrichment → routing → action
- Each stage was an independently observable agent with clear input/output contracts
- Confidence scoring at each stage determined auto-proceed vs human-review routing
- Evaluation layer: offline evals on labeled sets + production monitoring on approval rates, override rates, and exception rates

Key tradeoffs:
- Chose staged pipeline over monolithic agent because failure isolation mattered more than latency
- Used external models for extraction but built internal control for routing and policy enforcement
- Human review was not blanket — it was targeted at low-confidence or high-consequence cases

Result: 30-60K documents/day, 80%+ reduction in manual effort, clear visibility into where the system was confident and where it was not.

**Why this matters to Finom:** This is the same shape as AI accounting — document intake, classification, reconciliation, action proposal, approval. The transferable insight is that the workflow contract matters more than any single model call.

---

## Story 2: Evaluation and Observability Discipline

**Maps to:** quality systems, governance, central AI standards

### 60-second version

Designed evaluation frameworks that combined offline evals on labeled datasets with runtime monitoring. The key insight was separating component metrics from end-to-end workflow success — a good classifier feeding into a bad routing layer still produces bad outcomes. Built dashboards that tracked approval rates, override rates, rework rates, and failure cluster analysis. This approach caught regressions that unit-level metrics missed.

### 3-minute version

The problem was that teams were evaluating AI components in isolation — good extraction accuracy, good classification F1 — but end-to-end workflow outcomes were still unpredictable.

Approach:
- Defined three evaluation layers: offline evals, production workflow metrics, failure-case reviews
- Offline evals used curated datasets with ground truth, tested at component and pipeline level
- Production metrics tracked operational outcomes: auto-complete rate, approval rate, override rate, time-to-resolution, rework
- Failure reviews captured patterns: which case types failed, which stages failed, and whether failures were correlated

Key tradeoffs:
- Component evals were cheap and fast but could miss interaction effects
- End-to-end evals were expensive but caught real-world failure patterns
- Chose to run both, with component evals as the daily regression check and end-to-end evals as the weekly quality review

Result: Earlier regression detection, clearer understanding of which workflow stages needed investment, and a shared evaluation vocabulary across teams.

**Why this matters to Finom:** A central AI team needs a quality bar. This story shows how to build one that is measurable and useful rather than just a set of guidelines.

---

## Story 3: Turning Ambiguity Into Repeatable Capability

**Maps to:** reusable patterns, business-problem-to-system, first-90-days credibility

### 60-second version

Was asked to "add AI" to a workflow with no clear spec. Started by mapping the existing manual process, identifying the highest-effort repeated steps, and scoping a first version that automated the most repetitive parts while keeping human judgment in the loop for edge cases. The first version shipped in weeks, not months. The architecture was then reused across three similar workflow types with minor adaptation. The key was designing the shared layer from the start — not generalizing after the fact, but building clean contracts between stages that made reuse natural.

### 3-minute version

The problem was vague: "we want AI to help with this workflow." No spec, no labeled data, no clear success metric.

Step 1: Process mapping. Observed the manual workflow for a week. Identified that 70% of operator time was spent on three predictable subtasks with clear right/wrong answers.

Step 2: Scoped v1. Automated those three subtasks with confidence-gated automation. High-confidence cases auto-completed. Medium cases drafted for review. Low cases escalated.

Step 3: Made it reusable. The stage contracts (intake → classify → extract → propose → review → finalize) were generic enough that two adjacent workflow types could reuse the pipeline with different domain configs.

Key tradeoffs:
- Deliberately did not build a "workflow platform" — built one good pipeline and extracted the reusable parts only when reuse was real
- Chose confidence-gated automation over full autonomy to earn trust incrementally
- Kept domain-specific logic in config, not in the shared pipeline code

Result: Shipped v1 in weeks, reused across 3 workflows, 60-80% effort reduction depending on workflow complexity.

**Why this matters to Finom:** This is the "first 90 days" story. It shows how to get a visible win while creating minimum reusable structure — exactly what a central AI team should do early.

---

## Story 4: Infrastructure Ownership End-to-End

**Maps to:** cross-stack ownership, production operations, not just AI layer

### 60-second version

Owned the full stack from model serving to Kubernetes deployment to monitoring. Built CI/CD pipelines, configured autoscaling for inference workloads, set up structured logging and alerting. The point is not that I love infra — it's that I can own the full lifecycle of an AI system in production, not hand it off to another team after the model works in a notebook.

### 3-minute version

In a small team, there was no separate platform or infra team for AI workloads. Took ownership of:
- Docker containerization of LLM-serving components
- Kubernetes deployment with Helm charts for reproducible environments
- CI/CD with automated eval checks before deployment
- Autoscaling configuration tuned for inference latency SLOs
- Structured logging with correlation IDs across pipeline stages
- Alerting on latency, error rates, and quality metrics drift

Key tradeoffs:
- Chose managed inference where cost/performance allowed, self-hosted where control was needed
- Built just enough tooling to keep operations sustainable, not a full internal platform
- Prioritized observability over perfection — if you can see it, you can fix it

Result: Sub-second P95 latency for most inference calls, zero undetected outages over 6 months, full deployment autonomy without ops bottleneck.

**Why this matters to Finom:** Finom's job posting expects cloud, containers, and scalable inference. This story shows the candidate can own the full lifecycle rather than needing a separate infra team.

---

## How To Use This Bank

1. **For "tell me about yourself"** → Use Story 1 + Story 3 as the backbone
2. **For "how would you add value in central AI"** → Lead with Story 2 (eval discipline) + Story 3 (reusable capability)
3. **For "give me a concrete example"** → Pick the story closest to the question axis
4. **For "what about infra/production"** → Story 4
5. **For any story** → End with the "why this matters to Finom" bridge

## Answer Shape Reminder

1. Frame the problem
2. Take a position
3. Explain the tradeoff
4. Give one concrete example
5. Name the metric or failure mode
