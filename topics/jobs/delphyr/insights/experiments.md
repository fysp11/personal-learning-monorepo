# Delphyr — Technical Experiments

Hands-on projects to build domain competence and demonstrate skills in a 2nd round interview. Each experiment is scoped to 2-4 hours.

---

## Experiment 1: Clinical RAG Evaluation Pipeline

**Goal**: Build an evaluation framework that measures retrieval quality on clinical queries — demonstrates understanding of the core problem Delphyr solves.

### Setup
```bash
pip install langchain chromadb sentence-transformers datasets rouge-score
```

### Architecture
```
PubMed Abstracts (corpus)
    ↓
Embedding + Indexing (compare models)
    ↓
Clinical Query Set (synthetic + real)
    ↓
Retrieval + Evaluation
    ↓
Metrics Dashboard (precision@k, recall@k, nDCG, MRR)
```

### Steps
1. **Corpus**: Download ~10K PubMed abstracts from a specific domain (e.g., oncology)
   - Use `datasets` library: `load_dataset("pubmed_qa", "pqa_labeled")`
2. **Embedding comparison**: Index with 3 different models:
   - `all-MiniLM-L6-v2` (general purpose, fast)
   - `pritamdeka/PubMedBERT-mnli-snli-scinli-scitail-mednli-stsb` (biomedical)
   - `OpenAI text-embedding-3-small` (commercial general)
3. **Query set**: Create 50 clinical queries with known-relevant documents:
   - "What is the first-line treatment for stage III non-small cell lung cancer?"
   - "What are the drug interactions between metformin and ACE inhibitors?"
4. **Evaluation**: Measure precision@5, recall@10, nDCG, MRR per model
5. **Analysis**: Document which model wins and why — biomedical models should excel on domain-specific queries

### Interview Talking Point
"I built an eval pipeline comparing general vs. clinical-specific embeddings on PubMed data. The biomedical model outperformed on domain-specific queries by X%, but the general model was surprisingly competitive on broad clinical questions. This informed my thinking about when custom embeddings are worth the training investment."

---

## Experiment 2: Agent Safety Harness with Commit/Rollback

**Goal**: Build a proof-of-concept transactional agent — demonstrates the commit/rollback pattern discussed in the interview.

### Architecture
```
Agent receives clinical task
    ↓
Plan: list of proposed actions
    ↓
Each action → STAGED (not executed)
    ↓
Confidence scoring per action
    ↓
Route: auto-commit (high) / human review (medium) / reject (low)
    ↓
COMMIT or ROLLBACK
```

### Implementation
```python
from pydantic import BaseModel
from enum import Enum

class ActionStatus(Enum):
    STAGED = "staged"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"

class StagedAction(BaseModel):
    action_id: str
    description: str
    tool_name: str
    tool_args: dict
    confidence: float
    status: ActionStatus = ActionStatus.STAGED
    result: str | None = None

class TransactionalAgent:
    def __init__(self, confidence_thresholds: dict):
        self.auto_commit_threshold = confidence_thresholds.get("auto", 0.95)
        self.review_threshold = confidence_thresholds.get("review", 0.70)
        self.staged_actions: list[StagedAction] = []
        self.committed_actions: list[StagedAction] = []

    def stage_action(self, action: StagedAction):
        """Stage an action without executing it."""
        self.staged_actions.append(action)
        return self._route_action(action)

    def _route_action(self, action: StagedAction):
        if action.confidence >= self.auto_commit_threshold:
            return self.commit(action)
        elif action.confidence >= self.review_threshold:
            return {"status": "needs_review", "action": action}
        else:
            return self.rollback(action, reason="confidence_below_threshold")

    def commit(self, action: StagedAction):
        """Execute the staged action."""
        action.status = ActionStatus.COMMITTED
        # Actually execute the tool call here
        self.committed_actions.append(action)
        return {"status": "committed", "action": action}

    def rollback(self, action: StagedAction, reason: str):
        """Reject and rollback the action."""
        action.status = ActionStatus.ROLLED_BACK
        return {"status": "rolled_back", "reason": reason, "action": action}

    def rollback_all(self):
        """Rollback all committed actions (undo)."""
        for action in reversed(self.committed_actions):
            # Execute compensating action
            action.status = ActionStatus.ROLLED_BACK
        self.committed_actions.clear()
```

### Extension: Clinical MDT Preparation Agent
Build on the harness to create a simple MDT prep agent:
1. Input: Patient ID (mock data)
2. Actions: retrieve_patient_history, retrieve_lab_results, match_guidelines, generate_summary
3. Each action is staged, confidence-scored, and routed
4. Output: Structured MDT case brief with audit trail

### Interview Talking Point
"I prototyped a transactional agent harness inspired by database commit/rollback semantics. The key insight is that in clinical workflows, you need both action-level confidence routing AND the ability to rollback an entire workflow if a downstream action reveals the upstream was wrong."

---

## Experiment 3: Clinical Decision Graph from Guidelines

**Goal**: Parse a clinical guideline and generate a structured decision graph — demonstrates understanding of MDT workflow automation.

### Setup
```bash
pip install networkx pyvis pydantic openai
```

### Architecture
```
Clinical Guideline (PDF/text)
    ↓
LLM Extraction (structured output)
    ↓
Decision Nodes + Edges (Pydantic models)
    ↓
NetworkX Graph
    ↓
Visualization (PyVis HTML)
```

### Implementation Sketch
```python
from pydantic import BaseModel

class DecisionNode(BaseModel):
    id: str
    question: str  # "Is the tumor resectable?"
    node_type: str  # "decision", "action", "outcome"
    evidence_level: str | None  # "1A", "2B", etc.

class DecisionEdge(BaseModel):
    from_node: str
    to_node: str
    condition: str  # "Yes", "No", "If PSA > 10"

class ClinicalDecisionGraph(BaseModel):
    guideline_name: str
    nodes: list[DecisionNode]
    edges: list[DecisionEdge]
```

### Source Material
Use a publicly available clinical guideline, e.g.:
- NICE guideline for Type 2 Diabetes management
- ESMO guideline for breast cancer treatment
- WHO guideline for hypertension management

### Interview Talking Point
"I experimented with extracting structured decision graphs from clinical guidelines using LLMs with structured output. The challenge is maintaining fidelity — clinical guidelines have nuance that's hard to capture in a binary decision tree. I used evidence grading levels and confidence annotations on each node to preserve that nuance."

---

## Experiment 4: Privacy-Preserving Embedding Evaluation

**Goal**: Test whether pseudonymization degrades retrieval quality — relevant to Delphyr's privacy constraints.

### Approach
1. Take clinical text samples with PII (mock patient data)
2. Apply pseudonymization (replace names, dates, IDs with tokens)
3. Embed both original and pseudonymized versions
4. Compare retrieval quality — does pseudonymization degrade results?

### Key Questions to Answer
- Does replacing patient names with `[PATIENT]` tokens affect embedding quality?
- Does date normalization (2024-03-15 → [DATE]) change retrieval relevance?
- What's the optimal pseudonymization strategy that preserves semantic meaning?

### Interview Talking Point
"I tested the impact of pseudonymization on embedding quality for clinical text. Replacing PII tokens had minimal impact on retrieval accuracy (<2% nDCG drop), but aggressive date normalization hurt temporal query performance. This suggests a tiered pseudonymization approach — aggressive for names/IDs, minimal for dates that carry clinical meaning."

---

## Priority Order
1. **Experiment 2** (Agent Safety Harness) — highest signal, directly referenced in interview
2. **Experiment 1** (Clinical RAG Eval) — core to Delphyr's product
3. **Experiment 3** (Decision Graphs) — maps to their current MDT work
4. **Experiment 4** (Privacy Embeddings) — differentiator, shows privacy awareness
