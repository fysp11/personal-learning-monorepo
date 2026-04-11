# Delphyr Status Assessment & Next-Round Angles

Saved: 2026-04-11

## Current Status

The technical interview with Tim de Boer and Dejan Petkovic was scheduled for **Friday, April 4, 2026**. As of April 11, no outcome has been recorded. This is **7 calendar days / 5 business days** since the interview.

### Most Likely State

1. **Interview happened, decision pending** — Delphyr is a 6-person startup; decision cycles can be quick or slow depending on other priorities
2. **Waiting for internal alignment** — Michel (CEO), Tim, and Dejan need to align; may be waiting for a time slot
3. **Recruiter backlog** — Samuel may have multiple candidates and limited bandwidth

### Recommended Action

- **By April 14 (10 days post-interview):** Send a brief follow-up to Samuel expressing continued interest
- **By April 18 (2 weeks post-interview):** If no response, direct reach-out to Michel is appropriate
- **Template:**

> Hi Samuel, hope you're doing well. Just wanted to check in on next steps following the technical conversation with Tim and Dejan on April 4. I've continued exploring some of the topics we discussed — particularly around clinical evaluation frameworks and ambient listening architectures — and would be happy to share my thinking if there's interest. Looking forward to hearing from you.

---

## What To Prepare If Advancing

### Most Likely Next Round: Culture/Team Fit + Deeper Technical

With only 6 people, Delphyr likely has 2-3 rounds total. If the technical was round 2, round 3 would probably be:
- **Michel (CEO) again** — deeper culture/vision conversation
- **Possibly with a hospital partner or advisor** — clinical domain validation
- **Focus:** how you'd work day-to-day, what you'd own, technical vision alignment

### New Angles Since April 4

The workspace has expanded significantly since the technical interview. These are new conversation pieces:

#### 1. Ambient Listening Architecture (New)

Delphyr's March 2026 funding announcement revealed ambient listening as a product surface. This wasn't discussed in the technical interview (it wasn't prominent in prep at that time).

**Conversation hook:**
> "I noticed the ambient listening announcement since we spoke. I've been thinking about the pipeline architecture — the gap between ASR accuracy and clinical note accuracy is where the real engineering challenge lives. A transcript can be word-perfect but still generate a wrong SOAP note if the model misattributes a statement or misses a negation."

**Evidence:** `code/soap-extraction-pipeline.ts` — working demo with negation detection and citation linking

#### 2. MDT Evaluation Benchmark Framework (New)

The agentic MDT workflow was discussed with Michel in round 1, but now there's a concrete evaluation framework.

**Conversation hook:**
> "I've sketched a 6-dimension evaluation framework for MDT briefing quality — completeness, citation accuracy, factual accuracy, hallucination rate, omission detection, and guideline relevance. Each dimension has a different clinical severity weight because not all errors are equal. I'd love to discuss whether this aligns with how you're thinking about quality assurance."

**Evidence:** `insights/mdt-evaluation-benchmark-framework.md`

#### 3. Clinical AI Landscape Intelligence (Updated)

Fresh competitive analysis with Delphyr's positioning vs. Abridge, Nabla, Hippocratic AI.

**Conversation hook:**
> "Looking at the landscape, Delphyr's positioning is very defensible — Dutch-native model, deep EHR integrations, EU data residency. Most competitors are US-based or documentation-focused. The full-workflow approach — ambient listening + search + summarization + decision support — is harder to replicate than any single capability."

**Evidence:** `insights/clinical-ai-landscape-april-2026.md`

#### 4. EU AI Act Enforcement Urgency (Contextual)

August 2026 is 4 months away. For a medical AI pursuing device classification, this is an active engineering deadline.

**Conversation hook:**
> "With August 2026 approaching for EU AI Act high-risk enforcement, how is Delphyr thinking about the conformity assessment timeline? The engineering requirements — human oversight, audit trails, data quality documentation — are things you'd want anyway for clinical safety, but the regulatory deadline makes them non-negotiable."

---

## Strongest Technical Positioning for Next Round

### What the Technical Interview Probably Validated

Based on the prep quality:
- Medical RAG understanding (retrieval → grounding → citations)
- Evaluation framework thinking (multi-layer, severity-weighted)
- Safety-first engineering (guardrails, human review, abstention behavior)
- Working style (high-ownership, early risk communication)

### What a Next Round Should Deepen

1. **How you'd work at a 6-person startup** — what do you do when there's no one to review your code? How do you prioritize when everything is urgent?
2. **Technical vision** — where should Delphyr invest engineering effort in the next 6 months?
3. **Ambient listening as a new frontier** — shows you're tracking their latest direction, not just prepping for a static role
4. **Regulatory as engineering** — EU AI Act compliance is not a legal problem, it's an engineering problem that Delphyr must solve with code

### Your Top 3 Talking Points for a Next Round

1. **"I build production AI over messy data with safety-first engineering."**
   - Evidence: extraction agent, citation verification, safety harness, SOAP pipeline
   - Frame: this is what Delphyr does — I'm already thinking in your problem space

2. **"The ambient listening surface is the most interesting engineering challenge I've seen."**
   - Evidence: detailed architecture analysis, working SOAP extraction demo
   - Frame: shows you're forward-looking, not just reacting to what was discussed

3. **"Evaluation is a first-class capability, not an afterthought."**
   - Evidence: MDT benchmark framework, severity-weighted scoring, correction-driven eval suite growth
   - Frame: at 6 people, you can't afford to learn about quality problems from clinicians — you need automated detection

---

## Transferable Value Regardless of Outcome

Even if Delphyr doesn't advance, this workspace has produced:

| Asset | Transferable To |
|-------|----------------|
| Medical RAG architecture patterns | Any clinical AI role (Nabla, Abridge, Glass Health) |
| Citation verification pipeline | Any correctness-sensitive AI role |
| Evaluation frameworks (severity-weighted) | Any regulated-domain AI role |
| EU AI Act compliance understanding | Any EU-based AI role |
| Ambient listening architecture | Any clinical documentation AI role |
| Agent safety harness (commit/rollback) | Any agentic AI role with safety requirements |
| SOAP extraction pipeline | Healthcare IT, clinical documentation, EHR integration |

The "correctness-sensitive AI engineer" positioning gets stronger regardless of which company advances.
