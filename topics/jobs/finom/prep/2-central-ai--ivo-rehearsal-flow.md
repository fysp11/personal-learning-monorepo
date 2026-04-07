# Ivo Interview — Rehearsal Flow

Saved: 2026-04-07
Interview: Wednesday, April 8, 2026 — 45 minutes

## How To Use This

Walk through each block in order. Say the answers out loud. Time yourself. The goal is muscle memory on the key answers so you can be present and conversational in the actual interview rather than searching for words.

---

## Block 1: Opening (first 5 minutes)

### Ivo says: "Tell me about yourself and why Finom."

**Your 30-second version:**
> "I build production AI systems for workflows where correctness matters. My strongest work is in agentic pipelines, document-heavy operations, and evaluation discipline. Finom interests me because you're not adding a chatbot — you're rebuilding financial operations around proactive AI, using a multi-agent architecture. That's the kind of problem where production reliability, staged automation, and reusable capability design actually matter."

**Your 2-minute version (add):**
> "Concretely, I've built and operated multi-agent pipelines processing tens of thousands of documents per day — classification, extraction, reconciliation, routing — with confidence-based automation and human review for edge cases. The architecture is structurally very similar to what Finom describes publicly for the AI Accountant. What pulls me here is the combination of agentic ambition with real financial workflows where you can't ship demo quality."

**Checkpoint:** Did you mention MAS? Did you mention correctness? Did you avoid framework names?

---

## Block 2: Central AI Mandate (minutes 5-15)

### Ivo says: "What should a central AI team own?"

**Your answer (60 seconds):**
> "Centralize the hard reusable layers: evaluation patterns, observability instrumentation, workflow conventions, shared document and retrieval primitives, guardrails and approval rails. Don't centralize domain workflow design, user interactions, or product prioritization. Product squads own the workflow outcome. Central AI raises the floor and prevents repeated mistakes."

### Follow-up: "How do you keep it from becoming a bottleneck?"

> "Three things. One: ship at least one direct workflow win for credibility. Two: build reusable primitives that teams adopt because they help, not because they're mandated. Three: paved roads, not gatekeeping. If teams bypass the shared path, treat that as a product signal — either the tooling is too heavy or the team genuinely needs local ownership."

**Checkpoint:** Did you say what to centralize AND what not to? Did you give the three concrete mechanisms?

---

## Block 3: MAS Architecture (minutes 15-25)

### Ivo says: "Tell me about your experience with multi-agent systems."

**Your answer (2 minutes):**
> "I've built production pipelines that are structurally multi-agent systems — multiple stages with typed interfaces, independent evaluation, confidence propagation between stages, and circuit-breaking when upstream quality drops. For example, a document processing pipeline doing classification, extraction, reconciliation, and action routing across tens of thousands of documents per day.

> The key architectural decisions that make this work in production: typed agent boundaries for failure isolation, confidence signals that propagate not just data, per-agent metrics plus end-to-end workflow metrics, and a shared context store so agents reference the same truth.

> The hard parts aren't the individual agents — they're the coordination: cascading failures, state management across agent boundaries, version coordination when you update one agent, and observability that traces a request across the full pipeline."

### Follow-up: "How would you apply that to our AI Accountant?"

> "The decomposition maps naturally: intake agent, classification, extraction, reconciliation against transactions, categorization, tax preparation, review routing, and filing. Each agent has different failure modes and different evaluation criteria. The orchestration layer handles sequencing and confidence-based routing — high-confidence cases auto-complete, medium draft for approval, low escalate immediately."

**Checkpoint:** Did you ground it in real experience? Did you name the hard parts? Did you map it to Finom's product?

---

## Block 4: Risk and Quality (minutes 25-35)

### Ivo says: "In accounting, 96% accuracy — is that good enough?"

**Your answer:**
> "Not as a single number. I'd ask: 96% on what distribution? What's the cost of the wrong 4%? Are failures concentrated in predictable edge cases? Is this a draft-for-approval stage or an autonomous action?

> For a draft workflow with strong routing and reviewer context, maybe. For autonomous filing, almost certainly not yet. The path to more autonomy is earned per workflow class: stable performance across real case classes, clear understanding of failure clusters, and trust in the review and rollback mechanisms."

### Follow-up: "What failure modes worry you most?"

> "False confidence on messy documents. Silent mismatch between extraction and transaction context. Brittle handling of country-specific tax edge cases. And weak observability where you only discover problems from customer complaints."

**Checkpoint:** Did you avoid giving a yes/no answer? Did you frame it as workflow-level, not model-level?

---

## Block 5: Your Questions (minutes 35-45)

**Ask in this order (pick top 3 based on flow):**

1. "How do you define the mandate of the central AI team today?"
2. "What are the biggest problems you want that team to solve in the next 6-12 months?"
3. "If this role joined, what would be the first high-leverage area to own?"
4. "Where has the current setup already created friction between central AI and product squads?"
5. "Are you optimizing more for speed of experimentation right now, or for reusable foundations and quality?"

**If only time for 1:** Ask #3.

**Checkpoint:** Did your questions show org and platform judgment, not just curiosity?

---

## Block 6: Closing

### If Ivo says: "Any final thoughts?"

> "What excites me about this role is that Finom is treating AI as a production engineering problem across critical business workflows — not as a research project. That matches exactly where my strongest experience is. I'd want to come in, get one visible win quickly, and build the minimum reusable quality layer that prevents the next teams from reinventing the same problems."

**Checkpoint:** Did you end with energy and specificity? Did you avoid generic closing language?

---

## Altitude Reminder

| With Dmitry | With Ivo |
|-------------|----------|
| Can you build serious production AI? | Can you shape how AI creates leverage across the company? |
| Implementation depth | Platform and org judgment |
| Agent systems, reliability | Reusable capability, quality systems |

Stay higher. Ground with one concrete example per answer.

---

## Emergency Pivots

**If the conversation goes deep technical early:**
- Pull from the story bank (`2-central-ai--ivo-story-bank.md`)
- Use the MAS architecture talking points

**If it goes pure strategy/org:**
- Pull from simulation 1 (founder/org-design)
- Keep grounding in "I would..." not "one should..."

**If he asks about fintech domain gaps:**
- "I won't claim fintech expertise I don't have. My transferable discipline is evaluation, routing, observability, and failure handling around high-cost workflows. I'd pair that with Finom's domain experts."

**If he probes on model training/ML depth:**
- "My center of gravity is production AI systems — orchestration, evaluation, reliability. That's what the role's center of gravity appears to be too. Model training is adjacent growth space, not a core claim."
