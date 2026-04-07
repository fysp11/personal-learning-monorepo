# RAG Guardrail Architecture Design - Delphyr Context

Saved: 2026-04-07

## Purpose

This is a deeper technical exploration of how a multi-stage guardrail pipeline would work in a medical RAG system like Delphyr's. It builds on the conceptual guardrail notes in `Medical-RAG-Guardrails-Landscape.md` and `Guardrails-In-Code.md` with a concrete architectural design.

---

## Architecture Overview

A medical RAG guardrail pipeline operates at four boundaries:

```
Input → [Stage 1: Input Guard] → Query Processing
    → [Stage 2: Retrieval Guard] → Context Assembly
    → [Stage 3: Generation Guard] → Response Generation
    → [Stage 4: Output Guard] → Final Response
```

Each stage has its own failure modes, metrics, and escalation behavior.

---

## Stage 1: Input Guard

**Purpose:** Validate and sanitize the incoming query before retrieval.

### Checks

1. **Intent classification** — Is this query within intended use?
   - Allowed: patient data lookup, guideline search, summary request, correspondence draft
   - Blocked: diagnosis request, treatment recommendation, medication prescribing
   - Edge: questions that look clinical but are information retrieval

2. **Prompt injection detection** — Does the query contain adversarial instructions?
   - Pattern matching for common injection templates
   - Semantic similarity to known injection patterns
   - Length and structure anomaly detection

3. **PHI boundary check** — Is the query scoped to an authorized patient context?
   - Verify patient context token is present and valid
   - Prevent cross-patient data leakage in query construction

4. **Language and quality check** — Is the query processable?
   - Language detection (Dutch/English for Delphyr context)
   - Minimum query quality threshold

### Metrics

- `input_guard_block_rate`: % of queries blocked at input
- `input_guard_intent_distribution`: distribution of classified intents
- `input_guard_injection_rate`: % flagged as potential injection
- `input_guard_latency_p95`: added latency

### Failure behavior

- Blocked queries return a structured refusal with reason code
- Edge cases route to a "clarify intent" response rather than hard block
- All blocks are logged with full query context for review

---

## Stage 2: Retrieval Guard

**Purpose:** Validate retrieved context before it reaches the generation model.

### Checks

1. **Relevance threshold** — Are the retrieved documents sufficiently relevant?
   - Minimum similarity score per chunk
   - Minimum number of relevant chunks required
   - If below threshold: respond with "insufficient information" rather than generating from weak context

2. **Source freshness** — Are the retrieved documents current enough?
   - Check document timestamps against clinical relevance windows
   - Flag stale lab results, outdated medication lists, superseded guidelines

3. **Patient scope verification** — Do all retrieved documents belong to the correct patient?
   - Cross-check patient identifiers in retrieved chunks
   - Hard fail if cross-patient contamination is detected

4. **Context completeness** — Is critical information missing?
   - Check for expected document types given the query intent
   - Flag when key sections (e.g., medication list, allergy list) are absent

### Metrics

- `retrieval_relevance_mean`: average relevance score of top-k chunks
- `retrieval_below_threshold_rate`: % of queries where no chunk meets minimum relevance
- `retrieval_stale_source_rate`: % of queries returning outdated documents
- `retrieval_patient_scope_violation_rate`: should be ~0, alert on any non-zero

### Failure behavior

- Below-threshold retrieval: return "I don't have enough information to answer this" with a list of what was searched
- Stale sources: include freshness warning in response
- Patient scope violation: hard block, log as critical incident

---

## Stage 3: Generation Guard

**Purpose:** Constrain the generation model during response creation.

### Mechanisms

1. **System prompt enforcement** — Structured instructions that define boundaries:
   - "Only make claims supported by the provided context"
   - "If information is not in the context, say so explicitly"
   - "Do not provide treatment recommendations or prescriptions"
   - "Cite specific source passages for each claim"

2. **Structured output enforcement** — Require structured response format:
   - Response body (constrained to retrieved context)
   - Citations array (each claim linked to source passage)
   - Confidence indicator (high/medium/low based on source coverage)
   - Limitations note (what the response does NOT cover)

3. **Temperature and sampling control** — Lower randomness for clinical content:
   - Low temperature for factual retrieval responses
   - Beam search or constrained decoding where available
   - Deterministic mode for reproducible outputs

### Metrics

- `generation_citation_rate`: % of claims with citations
- `generation_confidence_distribution`: distribution of confidence levels
- `generation_limitation_mention_rate`: % of responses that include limitations

### Failure behavior

- If the model cannot produce a structured response: fall back to "I was unable to generate a reliable answer"
- If citation rate is below threshold: flag response for human review before delivery

---

## Stage 4: Output Guard

**Purpose:** Validate the final response before delivery to the clinician.

### Checks

1. **Citation verification** — Are citations actually supported by source text?
   - For each citation, verify the claim is present in the cited passage
   - Score: exact match, partial match, unsupported
   - Block or flag responses with high unsupported citation rates

2. **Safety pattern check** — Does the response contain prohibited patterns?
   - Treatment recommendations
   - Diagnosis statements
   - Medication prescriptions
   - Legal/liability language
   - Direct patient identifiers beyond what's clinically necessary

3. **Consistency check** — Is the response internally consistent?
   - Contradictory claims within the same response
   - Claims that conflict with retrieved context

4. **Length and format check** — Is the response appropriate for clinical use?
   - Not too long for quick clinical review
   - Not too short to be useful
   - Properly formatted for the target interface (HIS sidebar, mobile view, etc.)

### Metrics

- `output_citation_verification_rate`: % of citations verified as supported
- `output_safety_block_rate`: % of responses blocked at output
- `output_consistency_score`: internal consistency measure
- `output_format_compliance_rate`: % meeting format requirements

### Failure behavior

- High unsupported citation rate: block response, return "I couldn't verify my sources for this query"
- Safety pattern violation: block response, log incident
- Consistency failure: flag for review, optionally regenerate

---

## Cross-Stage Observability

### Request-level trace

Every query gets a correlation ID that spans all four stages. The trace captures:
- Input query (sanitized for logging)
- Intent classification result
- Retrieved document IDs and relevance scores
- Generation parameters and raw output
- Output guard results and final delivery status

### Aggregate dashboards

- **Quality dashboard**: citation rates, relevance scores, safety block rates over time
- **Failure dashboard**: block reasons, escalation patterns, incident clusters
- **Performance dashboard**: latency per stage, throughput, queue depth
- **Drift dashboard**: metric trends over time, regression detection

### Alert rules

- Patient scope violation: immediate alert
- Safety block rate spike: alert if >2x baseline
- Citation verification rate drop: alert if below threshold
- Retrieval relevance drop: alert if mean drops >10%

---

## Evaluation Strategy

### Offline

- **Golden set evaluation**: curated queries with known-good responses, run weekly
- **Adversarial testing**: injection attempts, out-of-scope queries, edge cases
- **Regression suite**: cases that previously failed, verified as fixed

### Online

- **Shadow mode**: new pipeline version runs alongside production, compare results
- **A/B testing**: for non-safety-critical improvements, measure clinical utility
- **Clinician feedback loop**: structured feedback capture from users

### Per-stage evaluation

Each stage should have independent evaluation:
- Input guard: precision/recall on intent classification
- Retrieval guard: relevance metrics on retrieval quality
- Generation guard: faithfulness and citation quality
- Output guard: safety and verification accuracy

---

## Implementation Priority

If building this incrementally:

1. **Start with output guard** — highest impact, catches the most dangerous failures
2. **Add input guard** — prevents obviously wrong queries from wasting compute
3. **Add retrieval guard** — improves response quality by ensuring good context
4. **Add generation guard** — refines the generation process itself

This ordering maximizes safety impact with minimum initial complexity.

---

## Relationship To Existing Code

The existing `medical-extraction.impl.ts` demonstrates several of these concepts at the extraction level:
- `safetyNoAdviceScorer` → maps to Stage 4 safety pattern check
- `safetyPhiMinimizationScorer` → maps to Stage 4 PHI check
- `supportClaimCoverageScorer` → maps to Stage 4 citation verification
- `workflowJsonParseScorer` → maps to Stage 4 format check

The next natural extension would be to implement Stage 2 (retrieval guard) as a retrieval evaluation experiment, measuring context relevance and patient-scope verification.
