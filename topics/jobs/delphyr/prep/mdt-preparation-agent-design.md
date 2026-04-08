# MDT Preparation Agent Design

## Purpose

Technical design for a multi-disciplinary team (MDT) meeting preparation agent — a high-value use case for Delphyr's platform. MDT preparation is explicitly mentioned in Delphyr M1's capabilities and is a strong interview talking point.

---

## What Is an MDT Meeting?

A multi-disciplinary team meeting brings together clinicians from different specialties to discuss complex patient cases. Common in oncology, cardiology, transplant, and other multi-specialty pathways.

**Current pain point:** Preparing for an MDT meeting takes 30-60 minutes per patient case. A typical MDT reviews 10-20 patients. That's 5-20 hours of preparation for a single meeting — time that comes directly from clinical care.

**What preparation involves:**
1. Consolidate recent clinical events (labs, imaging, notes, referrals)
2. Identify the specific clinical question for discussion
3. Surface relevant clinical guidelines
4. Flag outstanding items (pending labs, missing imaging, incomplete referrals)
5. Prepare a structured summary for the team

---

## Agent Architecture

### Design Principle: Assistive, Not Decisional

The MDT prep agent **prepares information** — it does not make clinical decisions. It surfaces, organizes, and flags. The clinical team decides.

### Agent Decomposition

```
┌────────────────────────────────────────────────────┐
│                 MDT Orchestrator                    │
│                                                     │
│  Input: Patient list + MDT date + clinical context  │
│  Output: Structured MDT brief per patient           │
└────────┬────────┬─────────┬─────────┬──────────────┘
         │        │         │         │
         ▼        ▼         ▼         ▼
    ┌────────┐┌────────┐┌────────┐┌────────┐
    │Timeline││Clinical││Guideline││Gap     │
    │Agent   ││Question││Agent   ││Detection│
    │        ││Agent   ││        ││Agent   │
    └────────┘└────────┘└────────┘└────────┘
```

### Agent 1: Timeline Agent

**Purpose:** Build a chronological view of the patient's recent clinical journey.

**Inputs:**
- Patient ID
- Lookback window (e.g., last 3 months, or since last MDT)
- Document types to include

**Process:**
1. Retrieve all patient documents within the lookback window
2. Extract key events (admissions, procedures, lab results, imaging, consults)
3. Order chronologically
4. Classify each event by type and significance
5. Produce a structured timeline with source citations

**Output:**
```
Timeline:
  2026-03-15 — Lab: Creatinine 1.8 mg/dL (elevated) [Source: Lab Report #4521]
  2026-03-18 — Imaging: CT Abdomen — 2.3cm lesion, stable [Source: Radiology #892]
  2026-03-22 — Consult: Nephrology — recommends monitoring [Source: Consult Note #1203]
  2026-04-01 — Lab: Creatinine 2.1 mg/dL (rising) [Source: Lab Report #4587]
```

**Key challenge:** Temporal reasoning over inconsistent date formats and document structures.

### Agent 2: Clinical Question Agent

**Purpose:** Identify or refine the specific question for MDT discussion.

**Inputs:**
- Patient timeline (from Agent 1)
- Referral reason (if available)
- Previous MDT decisions (if returning patient)

**Process:**
1. Analyze the referral context and recent trajectory
2. Identify the implied clinical question
3. If a prior MDT decision exists, frame as follow-up
4. Formulate as a clear, structured question

**Output:**
```
Clinical Question:
  "Patient presents with rising creatinine (1.8 → 2.1 over 2 weeks) and
   stable abdominal lesion. Nephrology recommends monitoring. Question for
   MDT: Should treatment plan be adjusted given renal trajectory, or
   proceed with current approach?"

  Prior MDT (2026-02-10): "Continue current protocol, reassess in 6 weeks"
```

**Key challenge:** This agent must be conservative — surfacing the question, not answering it. Explicit "do not advise" guardrail needed.

### Agent 3: Guideline Agent

**Purpose:** Retrieve relevant clinical guidelines for the case.

**Inputs:**
- Clinical question (from Agent 2)
- Patient diagnosis and treatment context
- Guideline database (ESMO, NICE, NHG, NVvH, etc.)

**Process:**
1. Map clinical question to guideline search terms
2. Retrieve relevant guideline sections (not full guidelines)
3. Extract specific recommendations with evidence levels
4. Attach citations to exact guideline sections

**Output:**
```
Relevant Guidelines:
  1. ESMO Renal Cell Carcinoma (2024), Section 5.3:
     "Monitor renal function every 2 weeks during [treatment].
      Consider dose reduction if creatinine rises >50% from baseline."
     [Evidence Level: IIA]

  2. NVvH Guideline Nefrotoxiciteit, Section 3.1:
     "Creatinine rise >30% warrants nephrology consultation and
      potential treatment pause."
     [Evidence Level: III]
```

**Key challenge:** Clinical guidelines are long, complex documents. Retrieval must be section-level, not document-level. This is where hybrid retrieval architecture (see hybrid-retrieval-architecture-deep-dive.md) directly applies.

### Agent 4: Gap Detection Agent

**Purpose:** Flag missing information that the MDT should be aware of.

**Inputs:**
- Patient timeline (from Agent 1)
- Clinical question (from Agent 2)
- Expected information for this case type

**Process:**
1. Based on diagnosis and question type, determine expected data points
2. Cross-reference with available data
3. Flag missing or outdated items
4. Classify gaps by severity (blocking vs. informational)

**Output:**
```
Information Gaps:
  ⚠ BLOCKING: No follow-up imaging since 2026-03-18 (>3 weeks)
  ⚠ BLOCKING: Latest GFR not calculated (creatinine available but GFR missing)
  ℹ INFO: Nephrology consult note references "further workup pending" — no follow-up documented
  ℹ INFO: Patient preferences not documented in recent notes
```

**Key challenge:** Determining "expected" information requires clinical knowledge — either rule-based per pathway or learned from historical MDT patterns.

---

## Orchestrator Design

### Input
```typescript
interface MDTPrepRequest {
  patientIds: string[];
  mdtDate: string;
  mdtType: 'oncology' | 'cardiology' | 'general' | string;
  lookbackDays: number;
  requestedBy: string; // clinician ID for audit
}
```

### Per-Patient Pipeline
```
Patient ID
    │
    ▼
Timeline Agent ──→ Timeline
    │                  │
    ▼                  ▼
Clinical Question Agent ──→ Question
    │                          │
    ├──────────────────────────┤
    ▼                          ▼
Guideline Agent          Gap Detection Agent
    │                          │
    ▼                          ▼
Guidelines              Information Gaps
    │                          │
    └──────────┬───────────────┘
               ▼
    MDT Brief Assembly
               │
               ▼
    Structured MDT Brief
```

### Output: Structured MDT Brief

```markdown
## Patient: [Name] | DOB: [date] | MRN: [number]
### Diagnosis: [primary diagnosis]
### Reason for Discussion: [clinical question]

---

### Recent Timeline
[chronological events with citations]

### Clinical Question
[structured question with prior MDT context]

### Relevant Guidelines
[section-level extracts with evidence levels]

### Information Gaps
[blocking and informational gaps]

### Sources
[full list of source documents referenced]
```

---

## Guardrail Requirements

### Hard Rules

1. **No clinical advice** — the system surfaces information, never recommends treatment
2. **Patient scope isolation** — no cross-patient data leakage
3. **Citation required** — every factual claim must cite a source document
4. **Recency flagging** — information older than a configurable threshold is flagged
5. **Audit trail** — every retrieval, extraction, and assembly step is logged

### Confidence Signals

Each section of the MDT brief carries a confidence indicator:

- **HIGH** — all expected data present, sources verified, guidelines matched
- **MEDIUM** — some gaps flagged, some sources uncertain
- **LOW** — significant gaps, outdated information, or conflicting sources

Low-confidence briefs are flagged for human review before the MDT meeting.

### Escalation

If any of these conditions are met, the system escalates to a human reviewer:

- Information gap classified as BLOCKING
- Conflicting information between sources
- Patient has no recent clinical data (data freshness violation)
- System confidence below threshold

---

## Connection to Delphyr's Stack

| Component | Delphyr Capability | MDT Agent Need |
|-----------|-------------------|----------------|
| M1/M2 model | Clinical language understanding | Extraction and summarization |
| EHR integration | ChipSoft, InterSystems | Patient data retrieval |
| Citation system | Claim-level verification | Source attribution |
| Ambient listening | Consult capture | Could capture MDT discussion itself |
| Monitoring | End-to-end compliance | Audit trail |

---

## Evaluation Strategy

### Component-Level

| Agent | Key Metric | Target |
|-------|-----------|--------|
| Timeline | Event extraction recall | >95% |
| Timeline | Temporal ordering accuracy | >99% |
| Clinical Question | Question relevance (human-judged) | >80% rated "useful" |
| Guideline | Section-level retrieval precision | >85% |
| Gap Detection | True positive rate for blocking gaps | >90% |
| Gap Detection | False positive rate | <15% |

### End-to-End

- **Clinician time saved** — measure prep time with vs. without the agent
- **Brief completeness** — % of MDT discussions where all relevant data was surfaced
- **Brief accuracy** — % of factual claims that are correct (random audit)
- **Missed critical information** — safety metric, must be tracked

---

## Interview Talking Points

### If Asked "How would you design an MDT prep agent?"

> "I'd decompose it into four specialist agents — timeline construction, clinical question identification, guideline retrieval, and gap detection — orchestrated by a coordinator that assembles structured briefs. The critical design constraint is that this system prepares information, it never recommends treatment. Every claim needs a source citation. Every gap needs to be flagged, not filled. The evaluation strategy is component-level metrics plus end-to-end clinician time savings and a safety audit for missed critical information."

### If Asked "What's the hardest part?"

> "Gap detection. Knowing what *should* be there requires clinical pathway knowledge — either hard-coded rules per MDT type or learned from historical patterns. And the system has to be comfortable saying 'I don't know' — a false sense of completeness is worse than flagging gaps."

### If Asked "How does this connect to Delphyr's existing capabilities?"

> "M1 handles clinical language understanding. The EHR integrations provide the data pipeline. The citation system provides verifiable grounding. The MDT agent is an orchestration layer that combines these existing capabilities into a high-value workflow. It's not a new model — it's a new surface built on existing infrastructure."
