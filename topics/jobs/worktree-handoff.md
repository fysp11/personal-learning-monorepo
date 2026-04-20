# Worktree Handoff

Saved: 2026-04-10

## Scope

This file consolidates the relevant changes found across the active worktrees that touch the jobs prep area.

Included:
- Finom interview prep and live-round rehearsal material
- Delphyr interview prep and clinical retrieval architecture
- Delphyr landscape update with funding and ambient-listening context
- Cross-company AI adoption synthesis

Excluded:
- `langgraph` worktree, because it is a separate project and does not connect to the current jobs prep flow

## Finom

### What changed

- Added a clean Finom overview and interview-prep landing page.
- Added a concrete technical-round prep plan for Interview 3.
- Added a live-round rehearsal script showing the expected coding shape.
- Added a cross-company note about AI adoption as an engineering discipline.

### Relevant artifacts

- `topics/jobs/finom/README.md`
- `topics/jobs/finom/prep/3-lead-ai-engineer-prep-plan.md`
- `topics/ai-engineering/code/live-round-rehearsal.ts`
- `topics/jobs/cross-company-ai-adoption-engineering.md`

### Consolidated Finom read

- Role shape: Senior AI Engineer, likely close to the AI engineering lead.
- Interview 3 shape: `30 min` technical questions + `60 min` live problem-solving with `Claude Code` or `Codex`.
- Core thesis: production AI systems for workflows where correctness matters.
- Strong technical emphasis: deterministic vs AI boundaries, confidence routing, observability, evals, and failure handling.
- Strong org emphasis: central AI plus embedded delivery, with explicit adoption work.
- Strong behavioral emphasis: use AI tools to increase speed without losing rigor.

### Live-round pattern

- Keep stage boundaries explicit.
- Make policy-heavy parts deterministic.
- Let AI handle ambiguous classification or proposal generation.
- Route low-confidence outputs to review.
- End in a concrete action or result, not a vague suggestion.

## Delphyr

### What changed

- Added a concise Delphyr interview-prep landing page.
- Added a clinical hybrid retrieval pipeline prototype.
- The pipeline shows patient-scoped retrieval, dense + sparse fusion, clinical reranking, and context assembly.

### Relevant artifacts

- `topics/jobs/delphyr/README.md`
- `topics/jobs/delphyr/code/hybrid-retrieval.ts`
- `topics/jobs/delphyr/insights/clinical-ai-landscape-april-2026.md`

### Consolidated Delphyr read

- Company shape: medical AI for clinical decision support.
- Role shape: agentic workflows for doctors, RAG over patient data and clinical knowledge, and decision graphs.
- New product surface: ambient listening, which turns consultations into structured clinical notes.
- Team shape: very lean, high-leverage, and still early stage after the €1.75M round.
- Core technical pattern: retrieval must be patient-scoped first, then fused, then clinically reranked.
- Core safety pattern: patient isolation is a hard gate, not a prompt hint.
- Core product pattern: the retrieval layer feeds context assembly, then generation, then citation verification.

### Clinical retrieval pattern

- Dense retrieval handles semantic match.
- Sparse retrieval handles exact terms and codes.
- Reciprocal rank fusion merges both.
- Clinical reranking can use recency, document type, and query type.
- Context assembly should deduplicate and keep sources coherent.
- Ambient listening adds a separate real-time ASR + diarization + note-structuring problem.
- EU AI Act compliance is part of the product posture, not an afterthought.

## Cross-Company Synthesis

### Main insight

- AI adoption should be treated as an engineering product, not a memo.
- The reusable pattern is not just the model or the prompt.
- The reusable pattern is the adoption funnel, the metrics, the fallback path, and the visible trust story.

### Shared adoption funnel

- Awareness
- Trial
- Habit
- Trust
- Advocacy

### Shared failure modes

- Too much setup before first value
- Black-box behavior without explanations
- Extra review work instead of less work
- Accuracy drift that users notice before the system does
- Adding ambient or proactive features without a clean human handoff path

### Shared metrics

- Time to first value
- Override rate
- Silent acceptance rate
- Workflow compression
- Return rate
- Escalation volume
- Earned autonomy rate

## Continue From Here

1. Use Finom Interview 3 prep as the main active thread.
2. Use the Delphyr retrieval prototype as the technical pattern library for patient-scoped RAG.
3. Use the cross-company adoption note as the shared framing document for both jobs tracks.
