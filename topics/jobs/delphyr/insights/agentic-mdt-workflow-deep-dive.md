# Delphyr — Agentic MDT Workflow Deep Dive

Saved: 2026-04-09

## Purpose

MDT (Multi-Disciplinary Team) meeting preparation is one of Delphyr's core product directions. This document explores the technical architecture needed for an agentic MDT preparation system — the kind of deep thinking that would differentiate in a technical interview or follow-up.

---

## What Is An MDT Meeting?

In Dutch hospitals (and across Europe), complex cases are discussed in Multi-Disciplinary Team meetings where specialists from different disciplines review a patient case together:

- **Oncology MDT:** Surgeon + medical oncologist + radiation oncologist + radiologist + pathologist
- **Cardiology MDT:** Cardiologist + cardiac surgeon + interventional radiologist
- **Complex care MDT:** Multiple specialists coordinating treatment plan

### The Preparation Problem

Before each meeting, someone (often a registrar or junior doctor) must:
1. Gather all relevant patient data from multiple sources
2. Summarize the current clinical picture
3. Identify the key decision points for discussion
4. Present the case concisely to the team

This takes **30-60 minutes per patient**, and a typical MDT session reviews **8-15 patients**. That's 4-15 hours of preparation for a single meeting.

---

## Agentic MDT Preparation Architecture

### Agent Topology

```
MDT Preparation Orchestrator
    │
    ├── Patient Data Consolidation Agent
    │   ├── EHR Integration (ChipSoft HiX, Bricks)
    │   ├── Lab Results Retrieval
    │   ├── Imaging Reports Retrieval
    │   ├── Pathology Reports Retrieval
    │   └── Correspondence & Referral Letters
    │
    ├── Clinical Timeline Agent
    │   ├── Chronological event ordering
    │   ├── Treatment history extraction
    │   ├── Key decision point identification
    │   └── Medication history tracking
    │
    ├── Guideline Matching Agent
    │   ├── Clinical guideline retrieval (NICE, ESMO, NHG)
    │   ├── Patient profile → guideline mapping
    │   ├── Treatment option enumeration
    │   └── Contraindication checking
    │
    ├── Decision Point Synthesizer
    │   ├── Key questions for the MDT
    │   ├── Treatment options with evidence
    │   ├── Risk/benefit summary per option
    │   └── Patient preference notes (if available)
    │
    └── Briefing Generator
        ├── Structured case summary
        ├── Citation-backed claims
        ├── Visual timeline
        └── Discussion prompts
```

### Agent Communication Protocol

Each agent produces a structured output that feeds into downstream agents:

```typescript
interface AgentOutput<T> {
  agentId: string;
  patientScope: string; // Patient identifier for scoping
  timestamp: string;
  data: T;
  citations: Citation[];
  confidence: number;
  warnings: Warning[];
  missingData: string[]; // What the agent looked for but couldn't find
}

interface Citation {
  claimId: string;
  claim: string;
  sourceDocument: string;
  sourcePassage: string;
  retrievalScore: number;
  verificationLevel: "exact" | "paraphrased" | "inferred";
}

interface Warning {
  type: "missing_data" | "stale_data" | "conflicting_sources" | "low_confidence";
  message: string;
  severity: "info" | "warning" | "critical";
  affectedClaims: string[];
}
```

---

## Critical Safety Boundaries

### What The Agent MUST NOT Do

1. **Diagnose** — the agent retrieves and summarizes, it does not make diagnostic claims
2. **Recommend treatment** — it enumerates options from guidelines, it does not recommend
3. **Interpret imaging** — it retrieves radiologist reports, it does not read images
4. **Override clinical judgment** — it presents information, clinicians decide
5. **Mix patient data** — strict patient-scoping prevents cross-contamination

### The "Retrieve, Don't Reason" Principle

For clinical safety, the MDT agent should follow:

> **Every factual claim must be traceable to a source document. The agent retrieves and structures existing information — it does not generate new clinical knowledge.**

This means:
- Lab values come from the lab system, not from the model's knowledge
- Guideline recommendations come from retrieved guideline documents, not from training data
- Treatment history comes from EHR records, not from inference

### Abstention Protocol

When the agent cannot find sufficient information:

```
IF confidence < threshold:
  DO NOT hallucinate or fill in gaps
  DO flag the gap explicitly:
    "⚠ No pathology report found for this patient. Manual retrieval recommended."
```

This is better than a confident wrong answer. In clinical settings, a known gap is safer than an unknown error.

---

## Evaluation Framework For MDT Agent

### Component-Level Metrics

| Component | Key Metrics |
|-----------|-------------|
| Data Consolidation | Completeness (% of available records retrieved), Patient scope accuracy |
| Timeline Agent | Chronological accuracy, Event coverage, Treatment milestone detection |
| Guideline Matching | Guideline relevance, Option completeness, Contraindication detection recall |
| Decision Synthesizer | Question relevance, Option enumeration completeness, Evidence quality |
| Briefing Generator | Citation accuracy, Readability, Clinician satisfaction score |

### End-to-End Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Information completeness | % of relevant clinical data included in briefing | >95% |
| Citation accuracy | % of claims correctly attributed to sources | >98% |
| Hallucination rate | % of claims not supported by any source | <1% |
| Omission rate | % of clinically relevant facts missed | <5% |
| Preparation time savings | Time saved vs manual preparation | >60% |
| Clinician satisfaction | Post-meeting rating of briefing quality | >4.0/5.0 |

### Adversarial Test Cases

| Scenario | What To Test |
|----------|-------------|
| Conflicting lab results | Does the agent flag the conflict rather than picking one? |
| Outdated guideline | Does the agent prefer the most recent version? |
| Missing imaging report | Does the agent flag the gap vs hallucinating? |
| Patient with multiple conditions | Does the agent correctly scope to the relevant condition? |
| Cross-patient data leak | Does strict scoping prevent data from another patient appearing? |

---

## Integration Architecture With Dutch Healthcare Systems

### EHR Integration Points

| System | Type | Integration Method | Data Available |
|--------|------|-------------------|----------------|
| ChipSoft HiX | Hospital Information System | HL7 FHIR API / proprietary API | Full patient record, orders, notes |
| Bricks Huisarts | GP System | REST API | GP records, referrals, medications |
| InterSystems | Infrastructure | FHIR server | Cross-system data federation |
| PACS | Imaging archive | DICOM / FHIR ImagingStudy | Imaging reports (not images) |
| Lab systems | Lab results | HL7 v2 / FHIR DiagnosticReport | Lab values, reference ranges |

### FHIR Resources Relevant To MDT

| Resource | Use In MDT |
|----------|-----------|
| `Patient` | Patient identity and demographics |
| `Condition` | Active diagnoses and problem list |
| `MedicationStatement` | Current medications |
| `DiagnosticReport` | Lab results, pathology |
| `ImagingStudy` | Imaging metadata (link to report) |
| `DocumentReference` | Clinical notes, correspondence |
| `CarePlan` | Existing treatment plans |
| `Encounter` | Visit history and context |

---

## Technical Experiment: MDT Briefing Evaluator

A practical experiment that demonstrates understanding of MDT workflows:

### Approach

1. **Create synthetic MDT cases** — 10 cases with known clinical data
2. **Build a briefing evaluator** — scores generated briefings against ground truth
3. **Measure key metrics:**
   - Information completeness (did the briefing include all relevant data?)
   - Citation accuracy (are all claims sourced?)
   - Hallucination detection (are there unsourced claims?)
   - Gap reporting (are missing data points flagged?)

### Implementation Sketch

```typescript
interface MDTBriefing {
  patientId: string;
  presentingProblem: string;
  clinicalTimeline: TimelineEvent[];
  currentStatus: {
    diagnoses: CitedClaim[];
    medications: CitedClaim[];
    recentLabs: CitedClaim[];
    recentImaging: CitedClaim[];
  };
  guidelineContext: {
    relevantGuidelines: string[];
    treatmentOptions: CitedClaim[];
    contraindications: CitedClaim[];
  };
  questionsForMDT: string[];
  dataGaps: string[];
  generatedAt: string;
  modelVersion: string;
}

interface CitedClaim {
  claim: string;
  source: string;
  sourcePassage: string;
  confidence: number;
}

interface BriefingEvaluation {
  completeness: {
    score: number;
    missingElements: string[];
    extraElements: string[];
  };
  citationAccuracy: {
    score: number;
    verifiedClaims: number;
    unverifiedClaims: number;
    hallucinations: string[];
  };
  gapReporting: {
    score: number;
    correctlyFlagged: string[];
    missedGaps: string[];
    falseGaps: string[];
  };
  clinicalSafety: {
    score: number;
    unsafeClaims: string[];
    diagnosticOverreach: string[];
    treatmentRecommendations: string[]; // should be empty
  };
}
```

---

## Connection To Delphyr's Current Product

Based on public information, Delphyr currently has:
- **Two RAG systems** (patient-scoped and knowledge-based)
- **Decision graphs** (structured clinical pathways)
- **M1 model** (7B, Dutch-native, citation-focused)

The MDT preparation agent would combine all three:
1. Patient-scoped RAG → gather patient data
2. Knowledge RAG → match against clinical guidelines
3. Decision graphs → identify decision points and options
4. M1 model → generate the briefing with citations

This is the natural evolution from "retrieve and present" to "orchestrate and synthesize" — the agentic workflow direction Michel described in the first interview.

---

## Key Talking Points

1. **"MDT prep is a retrieval and synthesis problem, not a reasoning problem. The agent's job is to save the registrar 45 minutes of chart review, not to make clinical judgments."**

2. **"The most important metric is completeness — if the agent misses a relevant lab result, the MDT discussion is based on incomplete information. That's worse than no automation."**

3. **"Every claim in the briefing needs a citation. If I can't trace a statement back to a specific clinical note or lab result, it shouldn't be in the briefing."**

4. **"The abstention behavior is as important as the generation behavior. When the agent says 'I couldn't find a recent pathology report,' that's valuable information for the MDT."**
