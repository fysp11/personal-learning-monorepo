# Medical RAG, Guardrails, and Evals

Date: 2026-04-02

## Why this matters for Delphyr

The recruiter explicitly called out three themes:
- guardrails
- evals
- RAG on medical data

This note gathers first-party material from real companies discussing those themes, then turns it into interview-ready intuition.

## Sources used

All sources below are first-party company docs, engineering blogs, product docs, or whitepapers:
- Delphyr Engineering
- Abridge
- Hippocratic AI
- AWS Prescriptive Guidance
- Google Cloud Vertex AI Search docs
- John Snow Labs

These are useful because they show how serious teams describe the problem in production. They are also biased toward each company’s product narrative, so use them as strong signals, not gospel.

## What real companies are saying

### 1. Delphyr: medical RAG is not enough without exact citations

Key takeaways:
- Delphyr argues that plain RAG is only a partial solution if the system cannot show exactly which source snippet supports each claim.
- Their design choice is inline citation generation during response generation, not post-hoc attachment of sources afterward.
- They explicitly prefer slower answers with deterministic verification over faster answers with ambiguous support.

Useful intuition:
- In medical settings, "this came from guideline X" is weak.
- "This sentence is supported by this exact snippet" is much stronger.
- Citation quality is part of the safety system, not just a UX feature.

Interview angle:
- If asked about trustworthy medical RAG, talk about claim-level grounding, not just retrieval quality.

### 2. Delphyr: guardrails must exist before, during, and after generation

Key takeaways:
- Delphyr describes multiple safety checks across the full lifecycle of an interaction.
- They group risks into three buckets: security, accuracy, and focus.
- They explicitly mention prompt injection, false medical content, topic drift, copied EHR mistakes, and unsupported additions to patient state.
- They say one-turn checks were not enough; full conversational context mattered.

Useful intuition:
- Medical guardrails are not only toxicity filters.
- You need layered controls for:
- request safety and scope
- retrieval constraints
- in-process behavior checks
- output validation
- logging and adversarial testing

Interview angle:
- A strong answer is not "I would add a content filter."
- A stronger answer is "I would design a staged validation pipeline with specialized checks for scope, support, and clinical risk."

### 3. Abridge: factuality needs a taxonomy, not a binary hallucination label

Key takeaways:
- Abridge breaks unsupported claims into categories such as directly supported, reasonable inference, questionable inference, unmentioned, and contradiction.
- They also rate severity separately: minimal, moderate, major.
- Their note-generation pipeline uses multiple models, a task-specific unsupported-claim detector, and an automated correction system.
- They report over 50,000 training examples for unsupported-claim detection and over 10,000 realistic clinical encounters in benchmark datasets.
- Clinician review remains required before notes are entered into the EHR.

Useful intuition:
- "Hallucination" is too blunt for medical systems.
- Some unsupported claims are annoying; others are dangerous.
- Evaluation should separate support quality from clinical severity.

Interview angle:
- If Tim or Dejan ask how you would evaluate output quality, use a two-axis framework:
- support / grounding quality
- clinical severity if wrong

### 4. Hippocratic AI: safety evals in healthcare need output testing at scale

Key takeaways:
- Hippocratic AI argues that traditional LLM benchmarking is too input-focused for healthcare.
- Their RWE-LLM framework emphasizes output testing in realistic scenarios.
- They report 6,234 licensed clinicians evaluating 307,038 unique calls.
- They describe a multi-step safety process including output testing, human clinical supervision, escalations, and cross-validation.
- Their public positioning is that real-world error management and feedback loops are necessary for safe deployment.

Useful intuition:
- In healthcare, offline benchmark scores are not enough.
- You need scenario-based output testing, expert review, escalation paths, and continuous monitoring.

Interview angle:
- If asked about evals, say you would combine offline benchmarks with structured real-world review loops and severity-based error handling.

### 5. AWS: evaluate medical AI component by component

Key takeaways:
- AWS recommends evaluating extraction separately from RAG response generation.
- For extraction they call out accuracy, completeness, adjusted recall / capture rate, and precision.
- For RAG they call out response relevancy, context precision, and faithfulness.
- They also recommend LLM-as-a-judge approaches such as pairwise comparison, single-answer grading, and reference-guided grading.

Useful intuition:
- "The app works" is not an evaluation plan.
- A serious eval stack splits the system into:
- extraction
- retrieval
- generation
- final answer quality

Interview angle:
- If asked how you’d set up evals, propose component-level dashboards and end-to-end scenario tests.

### 6. Google Cloud: bound intended use, restrict inference, and patient-scope retrieval

Key takeaways:
- Google’s healthcare search docs explicitly say the system is for retrieving and summarizing existing medical information, not for diagnosis or treatment recommendations.
- Their docs warn outputs are drafts and should be reviewed.
- They require a patient ID in console workflows and recommend patient-specific search scope.
- They recommend avoiding inference-heavy queries and breaking complex questions into simpler ones.
- They support relevance ordering over unstructured FHIR resources such as Composition, DiagnosticReport, and DocumentReference.

Useful intuition:
- Safety is also about product boundaries.
- Good medical retrieval systems reduce scope and ambiguity:
- one patient at a time
- clear task boundaries
- simpler queries
- less inferential answering

Interview angle:
- A strong answer acknowledges that "safe" sometimes means refusing or narrowing the task.

### 7. John Snow Labs: specialized smaller medical models plus RAG can be practical

Key takeaways:
- John Snow Labs presents a healthcare RAG setup using FAISS and healthcare-focused models.
- Their framing is that specialized smaller models can outperform or be more practical than general large models for medical tasks.
- They evaluate models on medically relevant questions and emphasize domain fit.

Useful intuition:
- Bigger is not automatically better in medical AI.
- Strong retrieval, domain-tuned models, and conservative answer behavior can matter more than headline model size.

Interview angle:
- If asked whether you would always use the biggest model, the good answer is no. Choose based on risk, latency, deployment constraints, and domain fit.

## Patterns across the landscape

### Pattern 1: Medical RAG is really a verification system

The strongest teams do not treat RAG as "retrieve chunks and hope."

They treat it as:
- retrieve the right patient-specific and domain-specific context
- generate only grounded claims
- attach precise evidence
- validate support before release

### Pattern 2: Guardrails are multi-stage, not single-stage

The recurring architecture pattern is:
- input guardrails
- retrieval constraints
- generation constraints
- output validators
- human escalation and review
- logging and red-team loops

### Pattern 3: Evals need to be component-level and scenario-level

A credible evaluation story usually includes:
- retrieval metrics
- grounding metrics
- output quality metrics
- adversarial tests
- clinician review
- post-deployment monitoring

### Pattern 4: Support and severity should be measured separately

A claim can be weakly supported but clinically harmless.
A different claim can be weakly supported and clinically dangerous.

That distinction is useful in interviews because it shows risk maturity.

### Pattern 5: Intended-use boundaries are part of the technical design

Many systems are safer because they narrow the task:
- retrieve and summarize, not diagnose
- answer with evidence, not unsupported advice
- stay in-domain
- keep a human in the loop for higher-risk actions

## Interview-ready intuition

If asked "what makes medical RAG hard?" a good answer is:

- The hard part is not embedding notes into a vector DB.
- The hard part is producing answers that are patient-scoped, source-grounded, clinically bounded, and cheap to verify.
- In medical contexts, you have to design for abstention, traceability, and severity-aware failure handling.

If asked "what would good guardrails look like?" a good answer is:

- Pre-answer checks for scope, prompt injection, and patient context
- Retrieval constraints so the system only sees allowed, relevant sources
- Generation rules requiring claim-level support and domain boundaries
- Post-generation validation for faithfulness, unsupported claims, contradictions, and high-risk medical content
- Logging, adversarial testing, and human escalation paths

If asked "how would you evaluate it?" a good answer is:

- Split evals into extraction, retrieval, generation, and final answer
- Measure context precision, response relevance, and faithfulness
- Add a claim-support taxonomy instead of binary hallucination labels
- Weight errors by clinical severity
- Use LLM-as-judge selectively, but back it with clinician-reviewed datasets and adversarial cases

## Practice questions

### 1. How would you design a medical RAG pipeline for patient data and guidelines?

Strong answer should include:
- patient-specific scoping
- structured plus unstructured retrieval
- hybrid retrieval, not vector-only by default
- citations tied to exact source snippets
- abstention when support is weak

### 2. How would you prevent hallucinations in medical RAG?

Strong answer should include:
- no-source-no-claim behavior
- post-generation support validation
- contradiction checks against retrieved evidence
- explicit refusal or uncertainty for unsupported conclusions

### 3. How would you evaluate whether retrieval is good enough?

Strong answer should include:
- context precision
- recall coverage on curated cases
- relevance ranking quality
- failure analysis on misses
- clinician review for ambiguous cases

### 4. How would you evaluate output safety?

Strong answer should include:
- support taxonomy
- severity taxonomy
- adversarial prompts
- human review for high-risk workflows
- monitoring after deployment

### 5. When would you keep a human in the loop?

Strong answer should include:
- anything near diagnosis, prognosis, prescribing, or treatment recommendation
- lower-risk automation can be more autonomous if bounded and auditable
- escalation rules should be designed, not improvised

### 6. Would you use one large model for everything?

Strong answer should include:
- not necessarily
- smaller domain-tuned models may be better for some tasks
- use specialized models or validators where they reduce risk

## What to borrow for the interview

The strongest ideas to echo back to Delphyr are:
- claim-level evidence beats document-level references
- guardrails should cover security, accuracy, and focus
- one-turn evals miss conversational failure modes
- support quality and clinical severity are different axes
- output testing in realistic workflows matters more than generic leaderboard scores
- safe product boundaries are part of the architecturea

## Sources

- Delphyr, "Why Medical AI Needs Citations": https://www.delphyr.ai/blog/why-medical-ai-needs-citations
- Delphyr, "Why Medical AI Needs Multiple Safety Checks": https://www.delphyr.ai/blog/why-medical-ai-needs-multiple-safety-checks
- Delphyr, "How Does Delphyr Know the Context of a Patient?": https://www.delphyr.ai/blog/how-does-delphyr-know-the-context-of-a-patient
- Abridge, "The Science of Confabulation Elimination": https://www.abridge.com/ai/science-confabulation-hallucination-elimination
- Hippocratic AI, "Real World Evaluation of Large Language Models in Healthcare": https://hippocraticai.com/real-world-evaluation-llm/
- Hippocratic AI, "Safety": https://hippocraticai.com/safety/
- AWS Prescriptive Guidance, "Evaluating generative AI solutions for healthcare": https://docs.aws.amazon.com/prescriptive-guidance/latest/rag-healthcare-use-cases/evaluation.html
- Google Cloud, "Get search results for healthcare data": https://docs.cloud.google.com/generative-ai-app-builder/docs/search-hc-data
- Google Cloud, "Order healthcare search results": https://cloud.google.com/generative-ai-app-builder/docs/order-hc-results
- John Snow Labs, "The Power of Small LLMs in Healthcare": https://www.johnsnowlabs.com/the-power-of-small-llms-in-healthcare-a-rag-framework-alternative-to-large-language-models/
