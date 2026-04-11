# Delphyr Code Examples

## File layout

- `medical-extraction.contracts.ts`: types and contracts (schemas + shared types)
- `medical-extraction.impl.ts`: pure implementation (normalization, parsing, scorers, agent wiring)
- `medical-extraction.experiments.ts`: experiments and sample use cases (dataset + eval run + verbose logs)
- `medical-extraction-agent.ts`: compatibility barrel/wrapper

Self-contained Mastra example for a clinical extraction agent with grouped custom scorers:
- Extraction: `accuracy`, `precision`, `recall`, `completeness`
- Support/Citation: `support-claim-coverage`, `support-unsupported-claim-penalty`
- Safety/Guardrails: `safety-no-advice`, `safety-phi-minimization`
- Workflow/Operational: `workflow-json-parse`, `workflow-non-empty-output`

### What it demonstrates

- A `Mastra` agent that extracts structured clinical data from free text
- Custom deterministic scorers built with `createScorer(...)`
- Explicit formulas so the metrics stay separable in discussion
- `runEvals(...)` over a tiny sample dataset with ground truth

## Citation Verification Pipeline

`citation-verification.ts` — Demonstrates claim-level citation verification for medical RAG outputs, matching Delphyr's emphasis on exact, verifiable source quotes.

### What it shows

- **Claim-to-source matching**: Each claim is traced back to its cited source passage
- **Verification levels**: supported (exact match), partial (paraphrase/missing terms), unsupported (hallucination)
- **Hallucination detection**: Catches hallucinated details (e.g., "anaphylaxis" when source says "rash")
- **Missing source detection**: Catches citations pointing to nonexistent documents
- **Aggregate metrics**: Support rate, average match score, trustworthiness assessment

### Run

```bash
bun run citation
```

### Three test scenarios

1. **Well-cited summary**: All claims verified against real sources → trustworthy
2. **Hallucinated detail**: Source says "rash" but output claims "anaphylaxis" → partial, flagged
3. **Nonexistent source**: Citation points to document that doesn't exist → unsupported, blocked

---

---

## SOAP Note Extraction Pipeline

`soap-extraction-pipeline.ts` — Demonstrates the ambient listening → structured clinical note pipeline, implementing the architecture from `insights/ambient-listening-architecture-analysis.md`.

### What it shows

- **Speaker-labeled transcript → SOAP routing**: Patient statements → Subjective, doctor observations → Objective/Assessment/Plan
- **Pattern-based extraction with confidence scoring**: Each SOAP entry has a confidence score and citation to source transcript line
- **Negation detection**: Separate safety layer that catches "no cough" vs "cough", "no dizziness" vs "dizziness"
- **Reference comparison**: Gold-standard SOAP note enables precision/recall measurement per section
- **Clinical safety checks**: Medications extracted? Allergies checked? Vital signs captured? Follow-up planned? Safety net included?
- **Citation linking**: Every claim traces to source transcript line number (the "retrieve, don't reason" principle)

### Run

```bash
bun run soap
```

### Scenarios covered

- Realistic Dutch patient consultation (Mrs. de Vries, chest pain workup)
- 22 transcript utterances with doctor/patient speaker labels
- Negation handling (no cough, no dizziness, no fainting)
- Medication reconciliation (existing + new prescriptions)
- Safety net instructions (return sooner if worsens)

### Interview talking point

> "The hardest part of ambient listening isn't the ASR — it's the structuring. A transcript can be word-perfect but still generate a wrong SOAP note if the model misattributes a statement or misses a negation. That's why negation detection is a separate safety layer, and every SOAP entry cites its source line."

---

## Clinical Extraction Agent

## Run in terminal

From this folder:

```bash
cd /Users/fysp/personal/learning/topics/jobs/delphyr/code
bun install
```

Set your OpenAI key for the current shell session:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

Run the experiments demo:

```bash
bun run eval
```

You will see:
- startup summary with scorer groups
- per-item input + ground truth logs
- grouped metric summary + detailed metric reasons
- final average scores, summary, and raw result payload

### Metric definitions in this implementation

- `Extraction / Accuracy`: exact value correctness for extracted facts whose keys overlap with expected facts
- `Extraction / Precision`: exact matches divided by all extracted facts
- `Extraction / Recall`: exact matches divided by all expected facts
- `Extraction / Completeness`: section-level coverage of clinically important categories
- `Support / Claim Coverage`: percentage of extracted claims directly supported by source note text
- `Support / Unsupported Claim Penalty`: inverse unsupported-claim rate
- `Safety / No-Advice`: output avoids prescriptive treatment guidance
- `Safety / PHI Minimization`: output avoids direct identifiers (phone/email/MRN/DOB patterns)
- `Workflow / JSON Parse`: output is parseable JSON that matches schema
- `Workflow / Non-Empty Output`: output is present and non-empty

### Notes

- This is intentionally interview-friendly rather than production-complete.
- In production you would normally add stronger normalization, section-specific ontologies, synonym handling, temporal reasoning, uncertainty modeling, and retrieval-trace evaluation.

## Example output shape

```text
=== Starting Clinical Extraction Eval ===
Dataset size: 2
Scorers by group: Extraction (...), Support (...), Safety (...), Workflow (...)

--- Item 1/2 complete ---
...
Grouped metric summary:
- Extraction: clinical-extraction-accuracy=1, ...
- Support: support-claim-coverage=1, ...
- Safety: safety-no-advice=1, ...
- Workflow: workflow-json-parse=1, ...

=== Evaluation complete ===
Average scores: { ... }
Summary: { totalItems: 2 }
Raw result payload: { ... }
```
