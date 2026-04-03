# Slide Deck: Retrieval & Grounding in Medical RAG

Create a presentation covering how Medical RAG systems find and cite the right context:

## Slides (10-15 slides)

1. **Title Slide**
   - Retrieval & Grounding
   - Subtitle: Finding the right context and proving it

2. **The Retrieval Challenge**
   - Vector search alone is insufficient
   - Need exact snippet support, not semantic similarity
   - Hybrid retrieval: vector + keyword

3. **Citation Quality Levels**
   - Document-level references (weak)
   - Section-level citations (better)
   - Claim-level snippets (strongest)

4. **Hybrid Retrieval Architecture**
   - BM25/keyword for precise matches
   - Dense vectors for semantic retrieval
   - Reranking with cross-encoders

5. **Source Verification Pipeline**
   - Verify retrieved context supports each claim
   - Flag unsupported claims before generation
   - Contradiction detection

6. **The No-Source-No-Claim Principle**
   - If retrieval fails, generation should abstain
   - Slow verified answers over fast unverified ones
   - Clinical safety depends on this

7. **Context Precision**
   - Retrieve only what's needed
   - Avoid information overload
   - Precision vs recall trade-offs

8. **Handling Multiple Sources**
   - When sources conflict
   - Ranking by relevance and reliability
   - Transparency about source quality

9. **Patient-Specific Retrieval**
   - Patient ID-scoped search
   - Relevant history vs everything
   - Avoiding context contamination

10. **Key Takeaways**
    - Citation quality is clinical safety
    - Hybrid retrieval beats vector-only
    - Verification before generation

## Style
- Technical presentation with diagrams
- Include speaker notes
