# Slide Deck: Medical RAG Architecture

Create an **8-slide** interview-prep presentation for **myself** on the big-picture architecture of medical RAG systems. Keep it broad, practical, and easy to explain out loud.

## Slides

1. **Title: Medical RAG Architecture**
   - What a production-ready clinical retrieval system is actually trying to do
   - Mental model: retrieve trusted evidence, then answer carefully

2. **Why Vanilla AI Fails in Medicine**
   - Standard LLMs guess from training data; medical systems need verified patient context
   - Longitudinal records do not fit neatly into a normal context window
   - Good interview line: medical RAG is a **verification system**, not just a chatbot with search

3. **Plain-English System Map**
   - Pull from structured + unstructured clinical data already in EHR / GPIS / HIS systems
   - Retrieve approved evidence for the current patient and task
   - Generate grounded claims with linked evidence
   - Validate before release; escalate when confidence/support is weak

4. **EHR-RAG for Long Patient Histories**
   - Years of notes, meds, labs, and correspondence create a long-horizon retrieval problem
   - The goal is not “load everything,” but “retrieve the right evidence efficiently”
   - Mini example: “Summarize this patient’s diabetes management across the last 2 years”

5. **U-Shaped Retrieval, Explained Simply**
   - Recent events matter because they show current status
   - Early events matter because they show onset and baseline
   - Mid-history often gets downweighted unless clearly relevant
   - Interview phrasing: “I want the onset and the current state, not a flat dump of the chart”

6. **ETHER / AIR / DER Cheat Sheet**
   - **ETHER**: event- and time-aware hybrid retrieval; good for numeric trends + text together
   - **AIR**: adaptive iterative retrieval; expands the search when first-pass evidence is incomplete
   - **DER**: dual-path evidence reasoning; compares what happened with alternative possibilities
   - Keep each term in plain English rather than sounding academic

7. **What Good Grounded Output Looks Like**
   - Claim-level citations, not vague “according to the chart” references
   - Linked evidence a clinician can inspect quickly
   - Good query example: “Show me the most recent A1C and where it came from”
   - Unsafe query example: “What should I prescribe?”

8. **What I’d Say in the Interview**
   - “The hard part isn’t embeddings. It’s patient-scoped, source-grounded, clinically bounded retrieval over messy longitudinal records.”
   - “I’d use EHR-RAG with time-aware retrieval, linked evidence, and validation before release.”

## Style
- Broad and practical, not academic
- Use mini examples to make each concept memorable
- Explain each framework term in plain English immediately
- Optimize for quick verbal recall in the interview
