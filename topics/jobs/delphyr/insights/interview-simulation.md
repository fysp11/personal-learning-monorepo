# Delphyr — 2nd Round Interview Simulation

Practice questions with structured answers (STAR-format where applicable). Based on signals from the 1st round — they'll go deeper on evaluation, agent safety, and clinical domain understanding.

---

## Category 1: Technical Depth — Agent Evaluation

### Q1: "Walk us through how you'd build an evaluation framework for a clinical RAG system."

**Answer structure:**

> I'd approach this in three layers, each measuring a different aspect of quality:
>
> **Layer 1 — Retrieval quality**: Are we finding the right documents?
> - Build a ground-truth dataset: clinical queries paired with known-relevant documents (annotated by domain experts)
> - Measure precision@K, recall@K, nDCG, and MRR
> - Separate evaluation for patient data retrieval vs. clinical knowledge retrieval — they have different characteristics
> - Track "dangerous misses" separately: cases where a critical document was NOT retrieved (recall matters more than precision in clinical settings)
>
> **Layer 2 — Generation quality**: Is the output clinically accurate?
> - Factual consistency check: does the generated text faithfully represent the source documents? (No hallucination tolerance in clinical)
> - LLM-as-judge with a medical-domain system prompt, scoring on: accuracy, completeness, appropriate caveats
> - Human expert review on a sample — this is the gold standard, but expensive, so use it to calibrate the LLM judge
> - Citation accuracy: every claim must trace back to a specific source document
>
> **Layer 3 — Action correctness**: Did the agent do the right things?
> - For agentic workflows: define expected action traces per case type
> - "For a lung cancer MDT prep, I expect: retrieve patient history → retrieve recent imaging → retrieve relevant ESMO guideline → generate case summary"
> - Score: did the agent take these actions? In a reasonable order? Did it retrieve from the right indices?
>
> **Continuous evaluation**: Run this in production as a shadow mode — agent generates output, doctor also prepares independently, compare. Build a feedback loop from doctor corrections.

**Key phrase to deploy**: "In clinical settings, recall matters more than precision — a missed relevant document could mean a missed diagnosis. So I'd weight dangerous misses much more heavily than false positives in the retrieval evaluation."

---

### Q2: "How do you handle the speed vs. accuracy tradeoff in agent systems?"

**Answer structure:**

> It depends on the task criticality. I use a **thinking budget** approach:
>
> **Low-stakes tasks** (e.g., formatting a report, extracting metadata):
> - Fast model, minimal chain-of-thought, timeout of 5-10 seconds
> - Accuracy target: 90%+ is fine, user can easily correct
>
> **Medium-stakes tasks** (e.g., categorizing a patient condition):
> - Stronger model, structured output with confidence scoring
> - If confidence < 0.85, escalate to a second pass with more context or human review
> - Timeout: 30 seconds acceptable
>
> **High-stakes tasks** (e.g., suggesting a treatment pathway):
> - Strongest model available, full chain-of-thought, multi-step verification
> - Always goes through human review regardless of confidence
> - No timeout — correctness over speed
>
> The key insight from my scraper agent experience: when we introduced **granular action-level evaluation** instead of just end-to-end binary scoring, we could identify WHERE in the pipeline accuracy was being lost. That let us apply speed optimizations to the non-critical steps while keeping the critical steps rigorous.

---

### Q3: "Tell us about a time you built an agent that had to be reliable in production."

**STAR Answer — Self-Healing Scraper Agent:**

> **Situation**: At my previous engagement, we had a commodity website data collection project with 30+ sources. Websites would change their HTML structure regularly, breaking the scrapers. This required manual tag updates — about 20 hours per week of engineering time.
>
> **Task**: Build an automated system that could detect broken scrapers and fix them without human intervention.
>
> **Action**:
> - Set up Sentry monitoring to detect when scrapers failed
> - Built an agent triggered by Sentry alerts that would:
>   1. Receive the alert context (which site, which tags broke)
>   2. Navigate to the site and analyze the new structure
>   3. Propose updated tag mappings
>   4. Test the new mappings against known-good data
>   5. Deploy if tests passed
> - Introduced LLM-as-judge evaluation scoring to measure quality
> - Discovered and integrated DSPy for self-improving prompts
> - Broke the monolithic agent into **specialized skills** (detection, analysis, fix-proposal, testing)
>
> **Result**: 80-95% reduction in manual maintenance. Agent would run overnight, fix issues in ~10 minutes, and the scrapers would resume correctly. Saved ~20 hours/week of engineering time. We evolved it to proactively report on page quality before they broke.
>
> **Connection to Delphyr**: "The reliability patterns translate directly — staged actions, confidence scoring, rollback capability. In clinical settings, the stakes are higher, so you'd add stricter confidence thresholds and mandatory human review, but the architecture is the same."

---

## Category 2: Clinical Domain Understanding

### Q4: "What's your understanding of how MDR applies to AI software?"

**Answer:**

> MDR — EU Regulation 2017/745 — classifies software that provides clinical decision support as a **Software as a Medical Device (SaMD)**. For a system like yours that helps doctors make diagnostic or treatment decisions, you're likely targeting **Class IIa** — medium risk, intended to inform clinical decisions.
>
> The key requirements I'd be working within:
> - **IEC 62304** for software lifecycle — every code change is traceable and documented
> - **ISO 14971** for risk management — identify hazards (e.g., wrong guideline retrieved, outdated information), assess severity, and mitigate
> - **Clinical evaluation** — demonstrate that the system actually improves clinical outcomes vs. the status quo
> - **Post-market surveillance** — continuous monitoring of accuracy and safety after deployment
>
> The unique challenge for AI/LLM systems is **non-determinism**. MDR expects predictable, reproducible behavior, but LLMs are probabilistic. I think the way to bridge this is:
> - Use the LLM for retrieval and summarization (where variability is acceptable)
> - Use **deterministic rules** for critical decision points (where MDR expects consistency)
> - Treat the harness/guardrails as the "medical device," not just the model
> - Log every inference for reproducibility — same input should produce traceable, explainable output even if not identical
>
> I noticed you mentioned you're among the first pursuing this classification — that's a significant competitive moat.

---

### Q5: "How would you approach building an agent for MDT meeting preparation?"

**Answer:**

> An MDT prep agent needs to create a "digital case" — a structured brief that gives each specialist the context they need for a multi-disciplinary discussion. Here's how I'd architect it:
>
> **Input**: Patient ID + MDT meeting context (which specialty is presenting, what decision is pending)
>
> **Agent pipeline:**
> 1. **Patient History Agent** — retrieves recent records, labs, imaging reports from the patient data index. Structures into a timeline. Highlights recent changes.
> 2. **Clinical Guidelines Agent** — matches the patient's condition to relevant guidelines. Uses the clinical knowledge index. Identifies the specific decision point in the care pathway.
> 3. **Decision Graph Agent** — maps the patient's current state to the decision tree. Shows: "the patient is HERE in the pathway, the next decision is THIS, the options are A, B, C with these evidence levels."
> 4. **Case Synthesis Agent** — combines outputs into a structured brief: patient summary, relevant history, current decision point, applicable guidelines, suggested discussion topics.
>
> **Safety considerations:**
> - Every fact in the brief must cite its source (which EHR record, which guideline section)
> - Confidence scoring on the guideline matching — if the patient's case doesn't cleanly match any guideline, flag it explicitly
> - The brief is always a DRAFT — doctor reviews and approves before the MDT meeting
> - Audit trail: full trace of what was retrieved, why, and how it was synthesized
>
> **What "good enough" looks like**: The agent saves the presenting doctor 30-60 minutes of manual case preparation. It doesn't replace clinical judgment — it structures the information so the doctor can focus on the decision, not the data gathering.

---

### Q6: "How do you think about privacy when building RAG systems over medical data?"

**Answer:**

> My wife is a privacy specialist, so this is something I think about structurally, not as an afterthought. For medical data under GDPR:
>
> **Architecture-level:**
> - **Separate indices**: Patient data and clinical knowledge should be in separate systems with different access controls
> - **European hosting only**: Data residency is non-negotiable for medical data
> - **Encryption at rest AND in transit**: For patient data specifically
> - **No patient data in LLM training**: Inference only, with strict data processing agreements
>
> **Access-level:**
> - Role-based access: an agent processing Patient X's data should only access Patient X's records
> - Audit logging: every retrieval is logged — who, what, when, why
> - Purpose limitation: data retrieved for MDT prep can only be used for that MDT
>
> **Practical approach:**
> - I know you mentioned you sign data processing contracts with hospital clients that give you the legal basis to process patient data
> - The key question is: does patient data ever leave the hospital's boundary, or do you deploy within their infrastructure?
> - If data leaves: pseudonymization, encryption, strict DPA
> - If you deploy in-hospital: simpler, but you need to maintain access controls within the deployment
>
> I'm curious about your approach — it seems like you've solved this given you said it's "not necessarily" needed to encrypt/pseudonymize because your contracts handle the legal basis.

---

## Category 3: Culture & Working Style

### Q7: "How do you approach a new project — project management and technical perspective?"

**Answer (refined from what worked in round 1):**

> I start by understanding whether this is a **technical improvement for the company** or a **value-creating feature for the product/customer** — these have different approaches.
>
> **For product features:**
> - Understand the impact first: how will we measure success? What changes for the user?
> - I find that the technical challenge is rarely the hard part — it's understanding what "done" looks like and how to measure it
> - Two-week rule: if after two weeks nothing measurably changed, the approach is wrong
>
> **Technical approach:**
> - Go broad first, specific later — explore what could be the best option, but evaluate it within the context
> - I use structured frameworks for task decomposition — plan, research, execute — and I give quality information to my agents
> - I also evaluate my agents' contributions — understanding which tools can reliably do which parts
>
> **For Delphyr specifically:**
> - I'd start by deeply understanding the current RAG pipeline — sit with the data, run queries, understand where it excels and where it fails
> - Then understand the clinical workflow I'm automating — shadow a doctor preparing for an MDT meeting if possible
> - Only then start building — with a clear evaluation framework already in place before writing the first line of agent code

---

### Q8: "What tools do you use to build AI systems?"

**Answer (refined from round 1):**

> I use a range depending on the task:
> - **Claude Code / Cursor** for development — agentic coding with structured workflows
> - **LangGraph + Agno + Pydantic AI** for agent orchestration
> - **DSPy** for systematic prompt optimization (this is what I mentioned last time — self-improving prompts with metrics and LLM judges)
> - **Langfuse** for observability and tracing
> - **OpenAI / Anthropic / Gemini APIs** — I'm model-agnostic, use whatever works best for the task
>
> But honestly, the tooling matters less than the evaluation framework you wrap around it. The best agent with bad evaluation will silently degrade. A mediocre agent with great evaluation will rapidly improve.

---

## Pre-Interview Checklist

- [ ] Re-read the first-round README to recall specific moments
- [ ] Review MDR classification requirements (IEC 62304, ISO 14971)
- [ ] Look up one recent NICE or ESMO clinical guideline to reference specifically
- [ ] Prepare a question about their embedding model training process
- [ ] Have the DSPy example ready in case they followed up on it
- [ ] Know the Dutch healthcare context (UMC Amsterdam, ChipSoft HiX)
