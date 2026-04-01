# Delphyr — Gap Mitigation: Turning Weaknesses Into Strengths

The 1st round went well, but the gaps identified in the fit analysis need proactive bridging before a technical 2nd round. This document provides concrete scripts and evidence for each gap.

---

## Gap 1: No Clinical/Healthcare Domain Experience

### The Concern
"You've never worked in healthcare. How do you know clinical workflows?"

### Bridge Strategy: Demonstrate Adjacent Expertise + Rapid Learning

**Script:**
> "I don't have direct clinical experience, but I have three things that transfer directly:
>
> First, I've built high-reliability data pipelines where correctness is non-negotiable — 30-60K documents per day with classification and enrichment. In healthcare, the stakes are higher, but the engineering patterns are the same: validate every step, audit every decision, never silently fail.
>
> Second, my wife is a privacy/GDPR specialist. I live with someone whose daily work is data protection impact assessments and privacy-by-design. Medical data under GDPR Article 9 is the hardest privacy challenge — special category data, explicit consent, strict purpose limitation. I think about this structurally, not as a checkbox.
>
> Third, I was a patient at UMC Amsterdam — I experienced the healthcare system from the inside. I also hired a data analyst from AMC who showed me how hospital data workflows actually function day-to-day. I understand the pain points: scattered data, manual prep work, time pressure."

### Concrete Evidence to Build (Before Next Round)
- [ ] Read one NICE or ESMO clinical guideline end-to-end (e.g., NICE NG12 for suspected cancer)
- [ ] Understand what an MDT meeting agenda looks like (find examples online)
- [ ] Learn 10 key clinical abbreviations (see technical-deep-dive.md vocabulary section)
- [ ] Sign up for PubMed and run 5 clinical queries to understand the data
- [ ] Read about HL7 FHIR Patient and Observation resources

---

## Gap 2: No MDR (Medical Device Regulation) Experience

### The Concern
"MDR compliance is a huge part of our work. You've never navigated this."

### Bridge Strategy: Show Regulatory Pattern Recognition

**Script:**
> "I haven't gone through MDR certification, but I understand the pattern from working in regulated environments. MDR for AI/SaMD essentially requires:
>
> - A quality management system (ISO 13485) — I've worked with quality processes in enterprise settings
> - Risk management (ISO 14971) — I already think about failure modes and mitigations in my agent architectures. The commit/rollback pattern I described is essentially risk mitigation for agent actions
> - Software lifecycle documentation (IEC 62304) — traceability from requirement to implementation to test is something I practice with structured development workflows
> - Clinical evaluation — demonstrating that the system works better than the alternative is evaluation, which is my strongest area
>
> The unique challenge for LLM systems is non-determinism vs. MDR's expectation of predictability. I think the answer is: certify the harness, not the model. The guardrails, validation layers, and safety checks are deterministic even if the model isn't. The model is a component; the certified device is the whole system."

### Concrete Evidence to Build
- [ ] Read the EU AI Act high-risk requirements summary (overlaps with MDR)
- [ ] Find 2-3 examples of AI/SaMD companies that achieved MDR certification (Viz.ai, Aidoc)
- [ ] Understand the Notified Body process — who certifies in NL? (BSI, TÜV SÜD)
- [ ] Know the difference between Class I, IIa, IIb, III for software

---

## Gap 3: No Experience with Custom Embedding Models

### The Concern
"We train our own embeddings. Have you fine-tuned embedding models?"

### Bridge Strategy: Show Evaluation Competence + Learning Willingness

**Script:**
> "My hands-on work with embeddings has been at the evaluation and deployment layer — choosing the right model for the task, benchmarking retrieval quality, optimizing chunking strategies, and building hybrid search (semantic + keyword). I've worked with pgvector, Pinecone, SurrealDB, and ChromaDB at scale — 10M+ records with sub-second latency.
>
> For fine-tuning specifically: I understand the contrastive learning approach (positive/negative pairs), the training loop, and why domain-specific fine-tuning matters for clinical text where general models miss specialized vocabulary. I've used DSPy for prompt optimization, which shares the same evaluation-driven iteration pattern.
>
> I'd be excited to get into embedding model training — it's a natural extension of the retrieval evaluation work I already do. The gap is in the training loop mechanics, not in understanding what makes a good embedding."

### Concrete Evidence to Build
- [ ] Run the Experiment 1 from experiments.md: compare general vs. biomedical embeddings on PubMed data
- [ ] Read the Sentence-BERT / Sentence-Transformers fine-tuning guide
- [ ] Understand the contrastive learning loss functions (InfoNCE, triplet loss)
- [ ] Know the key biomedical embedding models: PubMedBERT, BioClinicalBERT, MedCPT

---

## Gap 4: No Dutch Language NLP Experience

### The Concern
"Our patient data is in Dutch. Can you handle Dutch clinical text?"

### Bridge Strategy: Show Multilingual Awareness

**Script:**
> "I haven't worked with Dutch NLP specifically, but I understand the challenges:
>
> - Dutch medical text has its own abbreviations and conventions that differ from English
> - Compound words in Dutch (like German) can challenge tokenizers
> - Available clinical NLP models for Dutch are fewer than English — but multilingual models like XLM-RoBERTa and mBERT provide a foundation
> - For retrieval: multilingual embedding models (like Cohere multilingual or E5-mistral) handle Dutch well for semantic search
>
> The practical approach: use multilingual models as the base, fine-tune on your Dutch clinical corpus (which you already do), and build evaluation datasets in Dutch to measure quality specifically.
>
> Living in Amsterdam, I'll naturally pick up Dutch — and my wife is already learning. But for NLP, the model handles the language; the engineer handles the evaluation and pipeline architecture."

### Concrete Evidence to Build
- [ ] Test a multilingual embedding model on Dutch text samples
- [ ] Look up available Dutch clinical NLP resources (e.g., MedSpaCy for Dutch, A-PROOF project)
- [ ] Know that Amsterdam UMC uses Epic (or ChipSoft HiX) — understand what data formats come out

---

## Meta-Strategy: How to Present Gaps

### Do
- Acknowledge honestly: "I haven't done X specifically"
- Bridge immediately: "But I have Y which transfers because Z"
- Show learning velocity: "I did [concrete thing] to prepare"
- Ask smart questions: show you've thought about the gap

### Don't
- Hand-wave: "I'm a fast learner, I'll figure it out"
- Overstate: "I basically know this already"
- Be defensive: acknowledge, bridge, move on
- Ignore the gap: they know it's there, so address it proactively
