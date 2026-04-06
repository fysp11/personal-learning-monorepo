# Medical AI Evaluation Metrics Cheat Sheet

Date: 2026-04-03

This is a quick-reference list for interview prep.

The goal is to explain each metric clearly without blending it with nearby terms.

## Extraction Metrics

- `Accuracy`: how often extracted facts exactly match the source record.
- `Precision`: of the extracted items, how many are actually correct and relevant.
- `Recall`: of the items that should have been extracted, how many the system successfully captured.
- `Completeness`: whether the output includes all clinically important details, even if each individual fact is correct.

## Retrieval Metrics

- `Context precision`: how much of the retrieved context is actually useful for answering the question.
- `Context recall`: how much of the necessary supporting evidence was retrieved.
- `Retrieval relevance`: how well the retrieved documents or chunks match the user’s question.
- `Ranking quality`: whether the most useful evidence appears near the top of the retrieved results.

## Generation Metrics

- `Faithfulness`: whether the generated answer is supported by the retrieved evidence, without inventing new facts.
- `Groundedness`: whether the answer stays anchored to real source material rather than model priors.
- `Answer relevance`: whether the response actually answers the question asked, not just something adjacent.
- `Correctness`: whether the final answer is medically and factually right.

## Citation and Support Metrics

- `Citation quality`: whether citations are specific, useful, and attached to the right claims.
- `Citation accuracy`: whether a cited source really supports the claim it is attached to.
- `Support quality`: how strongly each claim is backed by evidence, for example directly supported versus weak inference.
- `Contradiction rate`: how often the answer conflicts with the retrieved evidence or source record.

## Safety Metrics

- `Hallucination rate`: how often the model generates unsupported or fabricated claims.
- `Omission rate`: how often the system leaves out important clinical facts that should have been included.
- `Clinical severity`: how harmful an error would be if a clinician relied on it.
- `Abstention quality`: whether the system correctly refuses or defers when evidence is weak or scope is unsafe.

## Agent and Workflow Metrics

- `Task completion rate`: how often the agent finishes the intended workflow successfully.
- `Tool-use accuracy`: how reliably the agent chooses and uses the right tools or actions.
- `Escalation accuracy`: whether the system correctly routes high-risk or uncertain cases to human review.
- `Workflow robustness`: how well the system handles retries, ambiguity, and intermediate failures.

## Operational Metrics

- `Latency`: how long it takes to produce a usable answer.
- `Token usage`: how expensive the workflow is in model tokens.
- `Turn count`: how many interaction or reasoning steps the agent needs before finishing.
- `Coverage`: how broadly the system performs across different case types, specialties, or workflows.
