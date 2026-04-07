# Delphyr — Technical Deep-Dive Preparation

## 1. MDR (Medical Device Regulation) for AI Software

### What is MDR?
EU Regulation 2017/745 — governs medical devices sold in the EU. AI software that provides clinical decision support can be classified as a medical device (Software as a Medical Device — SaMD).

### Classification for Clinical Decision Support
- **Class I**: Low risk (e.g., simple data display)
- **Class IIa**: Medium risk — software intended to support clinical decisions (most CDSS fall here)
- **Class IIb**: Higher risk — software that diagnoses or suggests treatment
- **Class III**: Highest risk — implantable or life-sustaining

### Key Requirements for MDR Compliance
1. **Quality Management System (QMS)** — ISO 13485
2. **Risk Management** — ISO 14971 (identify hazards, assess risks, mitigate)
3. **Clinical Evaluation** — demonstrate clinical benefit and safety
4. **Post-Market Surveillance** — ongoing monitoring after deployment
5. **Technical Documentation** — complete record of design, development, testing
6. **Software Lifecycle** — IEC 62304 (software development lifecycle for medical devices)

### Why This Matters for AI/LLM Systems
- **Non-determinism challenge**: LLMs produce variable outputs → MDR expects predictable behavior
- **Explainability requirement**: Regulators want to understand HOW the system reached its recommendation
- **Version control**: Every model update potentially requires re-certification
- **Data drift monitoring**: Clinical accuracy must be continuously validated post-deployment

### Interview Angle
The interviewer mentioned pursuing MDR classification — ask about:
- Which class they're targeting (likely IIa for decision support)
- How they handle the non-determinism problem (likely hybrid: retrieval-grounded + rule-based constraints)
- Whether model updates trigger re-certification (and how they manage that)

---

## 2. RAG for Medical/Clinical Data

### Privacy-Preserving Retrieval Approaches

#### Data Categories in Clinical RAG
1. **Patient data** (highest sensitivity) — EHR records, lab results, imaging reports
2. **Clinical guidelines** (low sensitivity) — published medical guidelines, protocols
3. **Pharmaceutical data** (medium sensitivity) — drug interactions, dosages, contraindications
4. **Research literature** (low sensitivity) — PubMed, clinical trials

#### GDPR Special Category Data (Article 9)
Medical data is "special category data" under GDPR → requires:
- Explicit consent OR legal basis (healthcare provision)
- Data Processing Impact Assessment (DPIA)
- Data Protection Officer (DPO) involvement
- Strict access controls and audit trails

#### Architecture Patterns for Clinical RAG
```
Patient Data Index          Clinical Knowledge Index
(encrypted, access-controlled)   (shared, versioned)
        ↓                              ↓
    Query Router (intent classification)
        ↓                              ↓
   Patient Retriever           Knowledge Retriever
        ↓                              ↓
        └──────── Fusion / Reranking ────────┘
                       ↓
              Context Assembly + Safety Filters
                       ↓
                 LLM Generation
                       ↓
              Output Validation (clinical checks)
                       ↓
                 Doctor Review (HITL)
```

#### Key Design Decisions
- **Separate indices**: Patient data vs. clinical knowledge should be separate for access control
- **Encryption at rest AND in transit**: Patient data must be encrypted at all stages
- **Audit logging**: Every retrieval must be logged (who accessed what, when, why)
- **De-identification**: Consider pseudonymization for analytics/evaluation pipelines
- **European hosting**: Data residency requirements — must stay in EU

### Embedding Models for Clinical Text
- **General**: OpenAI embeddings, Cohere, Voyage
- **Clinical-specific**: PubMedBERT, BioClinicalBERT, MedCPT
- **Delphyr builds custom**: They train their own embedding models (mentioned in interview)

---

## 3. Agent Safety for Clinical Workflows

### The Commit/Rollback Pattern (from interview)
The user proposed a transactional model for agent actions:
```
Agent proposes action → Staged (not applied)
                      → Human reviews
                      → Commit (apply) OR Rollback (discard)
```

This maps to database transaction semantics applied to clinical workflows:
- **BEGIN**: Agent starts processing a case
- **SAVEPOINT**: After each significant decision/action
- **COMMIT**: Doctor approves the output
- **ROLLBACK**: If any step produces incorrect/unsafe output

### Confidence-Based Routing
```
High confidence (>0.95) → Auto-execute with audit log
Medium confidence (0.7-0.95) → Queue for human review
Low confidence (<0.7) → Flag + escalate + provide reasoning
```

### Evaluation Approaches for Clinical AI
1. **Retrieval quality**: Are the right documents/records being retrieved?
   - Precision@K, Recall@K, nDCG
   - Domain expert annotation for ground truth
2. **Generation quality**: Is the generated text clinically accurate?
   - LLM-as-judge (medical expert model)
   - Human expert review (gold standard)
   - Factual consistency checking against source documents
3. **Action correctness**: Did the agent take the right actions?
   - Action trace evaluation
   - Expected action sequences per case type
   - Tool call accuracy

---

## 4. MDT (Multi-Disciplinary Team) Meetings

### What They Are
Clinical meetings where doctors from different specialties review complex cases together. Common in oncology, rare diseases, complex surgery planning.

### Current Pain Points (What Delphyr Wants to Solve)
1. **Case preparation is manual**: Doctors spend hours gathering patient records, test results, imaging
2. **Information scattered**: Data across multiple systems (EHR, PACS, lab systems)
3. **Time pressure**: Limited meeting time, many cases to review
4. **Documentation burden**: Meeting outcomes need to be documented in structured format

### Agent Architecture for MDT Preparation
```
Trigger: MDT meeting scheduled
    ↓
Patient Data Retrieval Agent
  - Pulls recent records, labs, imaging reports
  - Structures into timeline
    ↓
Clinical Guidelines Agent
  - Matches patient condition to relevant guidelines
  - Identifies decision points
    ↓
Decision Graph Agent
  - Maps patient data to decision tree
  - Highlights decision points for discussion
    ↓
Case Synthesis Agent
  - Combines all inputs into structured "digital case"
  - Formats for MDT presentation
    ↓
Doctor Review (HITL)
  - Verify completeness
  - Add context only humans know
  - Approve for MDT presentation
```

---

## 5. Technical Experiments to Build

### Experiment 1: Clinical RAG Evaluation Pipeline
Build a mini evaluation framework for clinical retrieval:
- Use PubMed abstracts as document corpus
- Create synthetic clinical queries
- Compare embedding models (general vs. clinical-specific)
- Measure retrieval quality with domain-specific metrics

### Experiment 2: Agent Safety Harness
Build a proof-of-concept commit/rollback pattern:
- Agent with tool calls that are "staged" before execution
- Confidence scoring on each action
- Human-in-the-loop approval flow
- Rollback capability for multi-step workflows

### Experiment 3: Decision Graph Generator
Build a simple decision graph from clinical guidelines:
- Parse a clinical guideline document
- Extract decision points and branching logic
- Generate a structured decision tree
- Map patient data to decision paths

---

## 6. Key Vocabulary to Know
| Term | Meaning |
|------|---------|
| MDR | Medical Device Regulation (EU 2017/745) |
| SaMD | Software as a Medical Device |
| CDSS | Clinical Decision Support System |
| MDT | Multi-Disciplinary Team |
| EHR | Electronic Health Record |
| PACS | Picture Archiving and Communication System |
| IEC 62304 | Software lifecycle standard for medical devices |
| ISO 14971 | Risk management for medical devices |
| ISO 13485 | Quality management systems for medical devices |
| DPIA | Data Protection Impact Assessment |
| CE marking | Conformity marking for EU market access |
| Notified Body | Organization that certifies MDR compliance |
| UDI | Unique Device Identification |
