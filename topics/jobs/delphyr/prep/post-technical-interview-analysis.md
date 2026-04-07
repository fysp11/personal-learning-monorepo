# Delphyr Post-Technical Interview Analysis

Saved: 2026-04-07

## Status

The technical interview with Tim de Boer and Dejan Petkovic was scheduled for Friday, April 4, 2026. No outcome notes have been captured yet.

**Action needed:** Record the outcome of this interview — did it happen? What was the result? What's the next step?

This note exists as a placeholder and analysis framework until the outcome is recorded.

---

## What We Prepared Well

Based on the prep materials, the strongest areas going into the interview were:

1. **Medical RAG as verification system** — framing retrieval as correctness verification, not just search
2. **Staged guardrails** — input validation → retrieval quality → generation safety → output verification
3. **Citation mechanics** — exact source quotes, claim-level grounding, no-source-no-claim behavior
4. **Evaluation framework** — multi-layer evals with component and end-to-end metrics
5. **Working style positioning** — high-ownership, low-ego, early risk communication

## What Could Have Been Stronger

1. **Microsoft/Azure specifics** — if their stack is Azure-heavy, this was a known gap
2. **MDR/medical device regulatory depth** — correctly flagged as "show respect, don't fake expertise"
3. **Dutch healthcare system specifics** — GP workflows, specialist referral patterns, HIS ecosystem details
4. **M1/M2 model architecture questions** — the 7B parameter model is public, but fine-tuning details are not

---

## Deeper Technical Exploration: Areas Worth Building On

### 1. Clinical RAG Retrieval Patterns

The code example covers extraction and evaluation well but doesn't include a retrieval experiment. A useful next experiment would be:

**Patient-scoped hybrid retrieval:**
- Combine dense embeddings (semantic similarity) with sparse retrieval (keyword/entity matching)
- Scope all retrieval to a patient context window
- Track retrieval precision and recall separately from generation quality
- Demonstrate how retrieval quality is the ceiling for generation quality

### 2. Citation Verification Pipeline

Delphyr's public messaging emphasizes exact citations. A technical experiment could implement:

**Claim-level citation verification:**
- Extract individual claims from generated output
- For each claim, trace back to source document passage
- Score: supported (exact match), partial (paraphrase), unsupported (hallucination)
- This maps directly to the existing `support-claim-coverage` scorer but with retrieval tracing

### 3. Guardrail Architecture

The existing prep covers guardrails conceptually. A code-level implementation could show:

**Multi-stage guardrail pipeline:**
- Input sanitization: detect prompt injection, off-topic queries, requests for diagnosis
- Retrieval validation: minimum relevance threshold, source freshness check
- Generation safety: intended-use boundary enforcement, PHI minimization
- Output verification: citation verification, confidence scoring, escalation routing

### 4. Evaluation Beyond Extraction

The current code evaluates extraction quality. Extending to evaluate the full RAG pipeline would add depth:

**End-to-end RAG evaluation metrics:**
- Context precision: how much retrieved context is relevant
- Context recall: how much relevant context was retrieved
- Faithfulness: how much of the output is supported by retrieved context
- Answer relevance: how relevant is the answer to the original query
- Clinical safety: does the output stay within intended-use boundaries

---

## Next Steps For Delphyr Workspace

1. **Immediate:** Record the April 4 interview outcome
2. **If positive:** Prepare for the next round, likely deeper technical or team/culture
3. **If waiting:** Use the time to build one of the technical experiments above — it strengthens the portfolio regardless
4. **If negative:** Capture what was learned and what would transfer to other healthcare AI or regulated-domain opportunities

## Transferable Regardless Of Outcome

The Delphyr prep has produced highly reusable knowledge:
- Medical RAG architecture patterns
- Evaluation framework for correctness-sensitive systems
- Guardrail pipeline design
- Citation/grounding mechanics
- EU privacy and data residency considerations for AI systems

These apply directly to any healthcare AI, regulated AI, or high-correctness AI role.
