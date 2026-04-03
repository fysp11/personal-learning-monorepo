# Slide Deck: Retrieval & Grounding

Create a **7-slide** interview-prep presentation for **myself** on how medical RAG systems find, rank, cite, and verify the right evidence.

## Slides

1. **Title: Retrieval & Grounding**
   - How to explain evidence quality, provenance, and support clearly

2. **What Good Retrieval Actually Means**
   - Not just “semantic similarity,” but evidence that is useful enough to verify a claim
   - Clinical retrieval quality = relevance + provenance + patient scope
   - Good interview line: retrieval quality is **evidence quality**, not just search quality

3. **Weak vs Strong Grounding**
   - Weak: “Per guideline X…” with no precise snippet
   - Strong: exact source snippet tied to the exact claim
   - Best phrasing: claim-level evidence beats document-level references

4. **Hybrid Retrieval Recipe**
   - Start with patient scope and authorized sources
   - Combine structured filters, metadata, and semantic retrieval
   - Pull from notes, meds, labs, imaging, and guidelines together
   - Do not rely on vector-only retrieval by default

5. **Mini Query Examples I Can Reuse in the Interview**
   - “Show me the most recent A1C”
   - “Has this patient ever been treated with a cephalosporin?”
   - “Summarize aspirin uses for this patient”
   - Bad query: “What is going on with them?” because it is too vague and inferential

6. **Where Grounding Breaks**
   - Wrong patient scope
   - Missing historical onset context
   - Contradictory sources across the chart
   - Model adds unsupported glue text between facts
   - No-source-no-claim should prevent this from leaking into output

7. **What I’d Say in the Interview**
   - “I’d use hybrid retrieval, preserve provenance, and only generate claims I can support.”
   - “Context precision, faithfulness, and abstention matter more than flashy retrieval demos.”

## Style
- Example-heavy and practical
- Keep terms like context precision and faithfulness, but explain them naturally
- Use query examples as memory anchors
- Optimize for short, reusable interview phrasing
