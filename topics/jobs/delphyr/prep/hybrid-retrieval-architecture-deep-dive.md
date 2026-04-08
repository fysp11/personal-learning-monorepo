# Hybrid Retrieval Architecture for Clinical AI

## Purpose

Technical deep-dive on patient-scoped hybrid retrieval — combining dense embeddings, sparse keyword matching, and graph traversal for clinical data. This is the next technical experiment to build if the Delphyr process continues.

---

## Why Hybrid Retrieval Matters for Delphyr

Single-modality retrieval fails in clinical settings for predictable reasons:

| Retrieval Type | Strength | Failure Mode in Clinical Context |
|---------------|----------|----------------------------------|
| Dense (embeddings) | Semantic similarity, handles paraphrasing | Misses exact drug names, dosages, lab values |
| Sparse (BM25/keyword) | Exact term matching, drug names, codes | Misses semantic equivalents ("chest pain" vs "angina pectoris") |
| Graph traversal | Relationship-aware, temporal ordering | Requires pre-built knowledge graph, cold start problem |

**The research consensus (2026):** Hybrid retrieval combining at least two modalities consistently outperforms single-modality in clinical QA tasks. MediGRAF (Frontiers in Digital Health, 2026) demonstrated 100% recall for factual queries with zero safety violations using a hybrid graph + vector approach.

---

## Architecture Design

### Layer 1: Patient-Scoped Pre-Filtering

Before any retrieval, scope the search to the correct patient:

```
Input Query + Patient ID
       │
       ▼
┌─────────────────────┐
│ Patient Scope Filter │ ← Enforced at infrastructure level, not model level
│ - Filter by patient  │
│ - Filter by time     │
│ - Filter by doc type │
└─────────────────────┘
       │
       ▼
  Scoped Document Set
```

**Critical design principle:** Patient scoping is a hard filter, not a soft ranking signal. A query about Patient A must NEVER retrieve Patient B's data. This is a safety and privacy requirement, not an optimization.

Implementation approaches:
- **Namespace isolation** — separate vector store namespaces per patient (Pinecone, Qdrant)
- **Metadata filtering** — pre-filter by patient ID before similarity search
- **Row-level security** — database-level enforcement for graph stores

### Layer 2: Dual-Path Retrieval

Run dense and sparse retrieval in parallel over the scoped document set:

```
Scoped Document Set
       │
       ├──────────────────────┐
       ▼                      ▼
┌──────────────┐    ┌──────────────────┐
│ Dense Path    │    │ Sparse Path       │
│ (Embeddings)  │    │ (BM25 / keyword)  │
│               │    │                   │
│ Semantic sim  │    │ Exact match:      │
│ for concepts, │    │ drug names, ICD   │
│ paraphrases,  │    │ codes, lab values,│
│ clinical      │    │ dosages, dates    │
│ reasoning     │    │                   │
└──────┬───────┘    └────────┬──────────┘
       │                      │
       ▼                      ▼
   Top-K dense           Top-K sparse
```

### Layer 3: Reciprocal Rank Fusion (RRF)

Merge dense and sparse results using RRF:

```
RRF Score = Σ 1 / (k + rank_i)

Where:
- k = smoothing constant (typically 60)
- rank_i = rank of document in retrieval path i
```

RRF is preferred over learned fusion because:
- No training data needed
- Robust across query types
- Handles missing documents (a document only in one path still gets scored)
- Interpretable and debuggable

### Layer 4: Clinical Re-Ranking

After fusion, apply domain-specific re-ranking:

```
Fused Results (Top-N)
       │
       ▼
┌──────────────────────┐
│ Clinical Re-Ranker    │
│                       │
│ Boost factors:        │
│ - Recency (newer      │
│   notes > older)      │
│ - Document type        │
│   (discharge summary   │
│   > progress note for  │
│   overview queries)    │
│ - Authorship (attending│
│   > resident for dx)   │
│ - Section relevance    │
│   (findings > history  │
│   for lab queries)     │
└──────────────────────┘
       │
       ▼
  Re-Ranked Top-K
```

### Layer 5: Context Assembly

Package retrieved chunks for the generation model:

```
Re-Ranked Top-K
       │
       ▼
┌─────────────────────────┐
│ Context Assembly         │
│                          │
│ 1. Deduplicate           │
│ 2. Order chronologically │
│ 3. Add source metadata   │
│    (doc type, date,      │
│     author, section)     │
│ 4. Truncate to context   │
│    window budget         │
│ 5. Attach citation IDs   │
└─────────────────────────┘
       │
       ▼
  Structured Context → Generation Model
```

---

## Evaluation Framework for Retrieval

### Retrieval-Specific Metrics

| Metric | What It Measures | Why It Matters |
|--------|------------------|----------------|
| Recall@K | % of relevant chunks in top-K | Did we find what we need? |
| Precision@K | % of top-K that are relevant | Are we feeding noise to the model? |
| MRR (Mean Reciprocal Rank) | How high is the first relevant result? | Generation models weight early context |
| NDCG | Quality of full ranking | Are better sources ranked higher? |
| Patient Scope Leakage | Any cross-patient contamination? | Safety-critical — must be 0% |
| Modality Contribution | Dense-only vs sparse-only vs hybrid | Is hybrid actually helping? |

### Clinical-Specific Evaluation

Beyond standard IR metrics, clinical retrieval needs:

1. **Temporal correctness** — for "current medication" queries, are we returning the most recent medication list, not an old one?
2. **Contradiction handling** — if two notes disagree (e.g., allergy documented in one, absent in another), are both surfaced?
3. **Completeness for safety-critical queries** — for "allergies" or "contraindications", recall matters more than precision
4. **Section-level accuracy** — did we retrieve the right section of a long document, not just the right document?

### Golden Set Design

Build evaluation golden sets with:

- **Factual queries:** "What is the patient's creatinine level from last lab?" (single correct answer)
- **Aggregation queries:** "Summarize the patient's medication history" (multiple relevant sources)
- **Temporal queries:** "What changed in the treatment plan after the last MDT?" (recency matters)
- **Safety queries:** "What are the patient's allergies?" (recall is critical)
- **Negative queries:** "Does the patient have a history of cardiac disease?" when they don't (must not hallucinate)

---

## Implementation Plan (If Building as Technical Experiment)

### Phase 1: Minimal Viable Hybrid (4-6 hours)

1. Set up a small synthetic patient dataset (5-10 patients, 20-50 documents each)
2. Implement dense retrieval with embeddings (e.g., BGE-M3 or clinical embeddings)
3. Implement sparse retrieval with BM25
4. Implement RRF fusion
5. Evaluate: compare dense-only, sparse-only, hybrid on a small golden set

### Phase 2: Patient Scoping + Re-Ranking (3-4 hours)

1. Add patient namespace isolation
2. Add recency-aware re-ranking
3. Add document type boost factors
4. Evaluate: patient scope leakage test (must be 0%)
5. Evaluate: temporal correctness on time-sensitive queries

### Phase 3: Context Assembly + Citation (2-3 hours)

1. Build context assembly pipeline with source metadata
2. Attach citation IDs for downstream verification
3. Connect to existing citation-verification.ts for end-to-end flow
4. Evaluate: end-to-end retrieval → generation → citation verification

### Total: ~10-13 hours for a complete, interview-ready experiment

---

## Connection to Existing Code

The existing Delphyr code experiments provide building blocks:

- **medical-extraction.impl.ts** — scorer patterns that could evaluate retrieval quality
- **citation-verification.ts** — downstream verification that consumes retrieval context
- **medical-extraction.contracts.ts** — type definitions that could be extended for retrieval

The hybrid retrieval experiment would sit upstream of both:

```
[Hybrid Retrieval] → [Context Assembly] → [Generation] → [Citation Verification]
                                                              ↑
                                                    (existing code)
```

---

## Key Talking Points for Interview

### If Asked "How would you improve retrieval for clinical data?"

> "Single-modality retrieval isn't enough for clinical data. Dense embeddings miss exact drug names and lab values; keyword search misses semantic equivalents like 'chest pain' and 'angina pectoris.' I'd build a hybrid pipeline — dense and sparse in parallel, merged with reciprocal rank fusion, then re-ranked with clinical heuristics like recency and document type. And patient scoping must be a hard filter at the infrastructure level, never a soft signal."

### If Asked "How do you evaluate retrieval quality?"

> "Standard IR metrics — recall, precision, MRR — but with clinical-specific layers. Temporal correctness: are we returning current medications, not discontinued ones? Completeness for safety queries: allergies and contraindications need high recall, even at the cost of some noise. And patient scope leakage must be tested explicitly — zero tolerance."

---

## References

- MediGRAF: Hybrid Graph RAG for Clinical AI (Frontiers in Digital Health, 2026)
- Self-correcting Agentic Graph RAG for hepatology (PMC, 2026)
- RAG in Healthcare: Comprehensive Review (MDPI, 2026)
- Fine-Tuning and RAG Integration for Healthcare AI (Bioengineering, 2026)
