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
