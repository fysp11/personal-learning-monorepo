# Guardrails In Code

Date: 2026-04-02

This note focuses only on guardrails for medical AI.

The goal is interview readiness:
- what the wrong implementation looks like
- what the right implementation looks like
- why the right version matches the public patterns from Delphyr, Abridge, AWS, Google Cloud, and Hippocratic AI

## The core mistake

The wrong mental model is:

- "Guardrails" means one moderation call before the LLM

That is not enough for medical AI.

From the sources:
- Delphyr says safety checks must happen before, during, and after generation, and should cover security, accuracy, and focus
- Abridge uses post-generation claim detection and correction, plus clinician review
- Google Cloud narrows intended use and explicitly discourages diagnosis and treatment recommendation behavior
- AWS recommends component-level evaluation, not only end-to-end output checks

So the right mental model is:

- Guardrails are a staged pipeline

## Wrong way

This is the classic bad implementation for medical AI:

```ts
type Llm = {
  generate(prompt: string): Promise<string>;
};

async function answerMedicalQuestionBad(
  llm: Llm,
  patientContext: string,
  userQuestion: string
): Promise<string> {
  const prompt = `
You are a helpful medical assistant.

Patient context:
${patientContext}

Question:
${userQuestion}

Answer clearly and confidently.
`;

  return llm.generate(prompt);
}
```

Why this is wrong:
- no authentication or patient scoping
- no task boundary enforcement
- no prompt-injection defense
- no retrieval provenance
- no claim-level citations
- no output validation
- no contradiction checks
- no escalation path
- no logs for later evals

This is exactly the kind of setup that lets the model:
- invent symptoms not in the record
- follow malicious instructions
- give treatment advice outside allowed scope
- copy impossible values from the EHR without challenge

## Slightly less wrong, but still wrong

This version adds a single content filter and still fails the real problem.

```ts
async function answerMedicalQuestionStillBad(
  llm: Llm,
  patientContext: string,
  userQuestion: string
): Promise<string> {
  if (userQuestion.includes("kill") || userQuestion.includes("bomb")) {
    throw new Error("unsafe input");
  }

  const prompt = `
You are a medical AI. Use the patient context below.

${patientContext}

Question: ${userQuestion}
`;

  return llm.generate(prompt);
}
```

Why this is still wrong:
- it blocks generic abuse, but not medical prompt injection
- it does not verify whether the answer is supported
- it does not distinguish safe retrieval tasks from diagnosis or prescribing
- it does not verify whether the answer stayed inside the medical domain

This is the point Delphyr makes: normal filters do not catch the failures that matter in clinical systems.

## Right way

The correct pattern is a staged pipeline with narrow responsibilities.

```ts
type Intent =
  | "patient_summary"
  | "medication_history"
  | "guideline_lookup"
  | "draft_note"
  | "diagnosis_request"
  | "treatment_recommendation"
  | "other";

type GuardrailResult =
  | { ok: true }
  | { ok: false; code: string; message: string };

type RetrievedChunk = {
  id: string;
  sourceType: "ehr" | "guideline";
  sourceId: string;
  patientId?: string;
  text: string;
  timestamp?: string;
};

type Claim = {
  text: string;
  citationChunkIds: string[];
};

type DraftAnswer = {
  answer: string;
  claims: Claim[];
};

type FinalAnswer =
  | {
      status: "ok";
      answer: string;
      citations: Array<{ claim: string; snippets: string[] }>;
    }
  | {
      status: "blocked" | "needs_human_review";
      reason: string;
    };
```

### Step 1: classify intent and enforce intended use

This is where you stop the system from pretending it is a diagnostic engine when it is really a retrieval-and-summary tool.

```ts
function classifyIntent(question: string): Intent {
  const q = question.toLowerCase();

  if (q.includes("diagnosis") || q.includes("differential")) {
    return "diagnosis_request";
  }
  if (q.includes("what should i prescribe") || q.includes("treatment plan")) {
    return "treatment_recommendation";
  }
  if (q.includes("summarize") || q.includes("overview")) {
    return "patient_summary";
  }
  if (q.includes("medication")) {
    return "medication_history";
  }
  if (q.includes("guideline")) {
    return "guideline_lookup";
  }

  return "other";
}

function enforceIntendedUse(intent: Intent): GuardrailResult {
  if (intent === "diagnosis_request" || intent === "treatment_recommendation") {
    return {
      ok: false,
      code: "OUT_OF_SCOPE_CLINICAL_DECISION",
      message:
        "This workflow is restricted to retrieval and summarization, not diagnosis or treatment recommendation.",
    };
  }

  return { ok: true };
}
```

Why this is right:
- Matches Google Cloud’s public healthcare guidance: retrieve and summarize existing information, do not answer direct diagnosis or treatment questions.

### Step 2: require patient scoping and authorized sources

Medical retrieval should be narrow by default.

```ts
function requirePatientScope(patientId?: string): GuardrailResult {
  if (!patientId) {
    return {
      ok: false,
      code: "MISSING_PATIENT_SCOPE",
      message: "A patient-scoped request requires a patient ID.",
    };
  }

  return { ok: true };
}

function filterAuthorizedChunks(
  patientId: string,
  chunks: RetrievedChunk[]
): RetrievedChunk[] {
  return chunks.filter((chunk) => {
    if (chunk.sourceType === "guideline") return true;
    return chunk.patientId === patientId;
  });
}
```

Why this is right:
- Narrow scope reduces leakage and accidental cross-patient contamination.
- It matches the patient-specific retrieval pattern in Google’s healthcare search docs.

### Step 3: detect prompt injection and scope drift

Medical prompt injection is usually subtle, not dramatic.

```ts
function detectPromptInjection(question: string): GuardrailResult {
  const patterns = [
    /ignore (all|previous|prior) instructions/i,
    /generate a prescription/i,
    /pretend you are/i,
    /disregard safety/i,
    /override the system/i,
  ];

  const matched = patterns.some((p) => p.test(question));
  if (matched) {
    return {
      ok: false,
      code: "PROMPT_INJECTION_ATTEMPT",
      message:
        "The request attempts to override clinical safety or system instructions.",
    };
  }

  return { ok: true };
}

function detectTopicDrift(question: string): GuardrailResult {
  const nonMedicalPatterns = [
    /\blegal advice\b/i,
    /\btax\b/i,
    /\bstock\b/i,
    /\bpolitics\b/i,
  ];

  const matched = nonMedicalPatterns.some((p) => p.test(question));
  if (matched) {
    return {
      ok: false,
      code: "OUT_OF_DOMAIN",
      message: "This assistant only handles medical retrieval and summarization tasks.",
    };
  }

  return { ok: true };
}
```

Why this is right:
- Matches Delphyr’s public framing of `security` and `focus` guardrails.

### Step 4: retrieve first, generate only from approved evidence

The wrong approach is "give the model the full chart."
The right approach is "retrieve the minimum relevant evidence and keep provenance."

```ts
type Retriever = {
  search(input: {
    patientId: string;
    question: string;
    limit: number;
  }): Promise<RetrievedChunk[]>;
};

async function retrieveEvidence(
  retriever: Retriever,
  patientId: string,
  question: string
): Promise<RetrievedChunk[]> {
  const chunks = await retriever.search({
    patientId,
    question,
    limit: 12,
  });

  return filterAuthorizedChunks(patientId, chunks);
}
```

Interview point:
- This is where you mention hybrid retrieval, metadata filters, and chunk provenance.

### Step 5: force structured claims with citations

Do not ask for a free-form answer first and citations later.

```ts
type StructuredGenerator = {
  generateFromEvidence(input: {
    question: string;
    evidence: RetrievedChunk[];
  }): Promise<DraftAnswer>;
};

async function generateDraft(
  generator: StructuredGenerator,
  question: string,
  evidence: RetrievedChunk[]
): Promise<DraftAnswer> {
  return generator.generateFromEvidence({ question, evidence });
}
```

The generation contract should require:
- every factual claim must cite one or more chunk IDs
- no unsupported claims
- explicit uncertainty when evidence is incomplete

Why this is right:
- Matches Delphyr’s insistence on inline, exact, verifiable support instead of post-hoc citations.

### Step 6: validate support for every claim

This is where most bad implementations fail.

```ts
function getChunkMap(chunks: RetrievedChunk[]): Map<string, RetrievedChunk> {
  return new Map(chunks.map((c) => [c.id, c]));
}

function validateClaimSupport(
  draft: DraftAnswer,
  chunks: RetrievedChunk[]
): GuardrailResult {
  const chunkMap = getChunkMap(chunks);

  for (const claim of draft.claims) {
    if (claim.citationChunkIds.length === 0) {
      return {
        ok: false,
        code: "UNSUPPORTED_CLAIM",
        message: `Claim has no citation: ${claim.text}`,
      };
    }

    const citedChunks = claim.citationChunkIds
      .map((id) => chunkMap.get(id))
      .filter(Boolean) as RetrievedChunk[];

    if (citedChunks.length === 0) {
      return {
        ok: false,
        code: "INVALID_CITATION",
        message: `Claim cites missing evidence: ${claim.text}`,
      };
    }

    const supportFound = citedChunks.some((chunk) =>
      chunk.text.toLowerCase().includes(extractAnchorPhrase(claim.text))
    );

    if (!supportFound) {
      return {
        ok: false,
        code: "WEAK_SUPPORT",
        message: `Claim is not directly supported by retrieved evidence: ${claim.text}`,
      };
    }
  }

  return { ok: true };
}

function extractAnchorPhrase(text: string): string {
  return text.toLowerCase().replace(/[^\w\s]/g, "").split(/\s+/).slice(0, 8).join(" ");
}
```

This example is intentionally simple. In production, support validation is stronger if you:
- use span alignment instead of crude substring matching
- classify support as direct, reasonable inference, questionable inference, unmentioned, or contradiction
- store validator reasoning for review

Why this is right:
- Matches Abridge’s support taxonomy and Delphyr’s claim-level verification logic.

### Step 7: add domain-specific consistency checks

Generic moderation will not catch impossible medical values or contradictions.

```ts
function detectImpossibleValues(answer: string): GuardrailResult {
  const impossiblePatterns = [
    /heart rate\s+600\b/i,
    /temperature\s+15\b/i,
  ];

  if (impossiblePatterns.some((p) => p.test(answer))) {
    return {
      ok: false,
      code: "PHYSIOLOGICALLY_IMPLAUSIBLE_VALUE",
      message: "The output contains a medically implausible value and requires review.",
    };
  }

  return { ok: true };
}

function detectOverconfidence(answer: string): GuardrailResult {
  const patterns = [
    /\bdefinitely\b/i,
    /\bcertainly\b/i,
    /\bguaranteed\b/i,
    /\bwill work\b/i,
  ];

  if (patterns.some((p) => p.test(answer))) {
    return {
      ok: false,
      code: "OVERCONFIDENT_CLINICAL_LANGUAGE",
      message: "The answer overstates certainty relative to the available evidence.",
    };
  }

  return { ok: true };
}
```

Why this is right:
- Delphyr explicitly calls out copied EHR errors and overconfident clinical claims as real failure modes.

### Step 8: escalate instead of bluffing

The right system does not always answer.

```ts
function escalate(reason: string): FinalAnswer {
  return {
    status: "needs_human_review",
    reason,
  };
}
```

This is where you route to:
- a clinician
- a nurse review queue
- a lower-risk retrieval-only fallback

Why this is right:
- Matches the human supervision and escalation patterns Hippocratic AI and Abridge describe.

### Step 9: put it together as a pipeline

```ts
async function answerMedicalQuestionSafely(input: {
  patientId?: string;
  question: string;
  retriever: Retriever;
  generator: StructuredGenerator;
}): Promise<FinalAnswer> {
  const intent = classifyIntent(input.question);

  for (const check of [
    enforceIntendedUse(intent),
    detectPromptInjection(input.question),
    detectTopicDrift(input.question),
    requirePatientScope(input.patientId),
  ]) {
    if (!check.ok) {
      return {
        status: "blocked",
        reason: `${check.code}: ${check.message}`,
      };
    }
  }

  const evidence = await retrieveEvidence(
    input.retriever,
    input.patientId!,
    input.question
  );

  if (evidence.length === 0) {
    return escalate("No relevant evidence found for a grounded answer.");
  }

  const draft = await generateDraft(input.generator, input.question, evidence);

  for (const check of [
    validateClaimSupport(draft, evidence),
    detectImpossibleValues(draft.answer),
    detectOverconfidence(draft.answer),
  ]) {
    if (!check.ok) {
      return escalate(`${check.code}: ${check.message}`);
    }
  }

  return {
    status: "ok",
    answer: draft.answer,
    citations: draft.claims.map((claim) => ({
      claim: claim.text,
      snippets: evidence
        .filter((chunk) => claim.citationChunkIds.includes(chunk.id))
        .map((chunk) => chunk.text),
    })),
  };
}
```

## The critical design difference

The wrong implementation trusts the model and filters around it.

The right implementation distrusts the model by default and requires it to:
- stay in scope
- use patient-scoped evidence
- cite each claim
- pass validators
- escalate when uncertain

That is the strongest interview framing.

## What "right" means in medical AI

According to the public patterns we found, a correct guardrails implementation should do all of the following:

- constrain intended use
- narrow retrieval scope
- detect prompt injection and domain drift
- require claim-level support
- distinguish unsupported claims from contradictions
- treat high-severity errors differently from low-severity ones
- allow abstention and escalation
- keep logs for later evals and red-team review

If one of those is missing, the system may still be useful, but it is not robust medical AI.

## What to say in the interview

If they ask "how would you implement guardrails?" a strong answer is:

- I would not rely on a single moderation layer.
- I would build guardrails as a staged pipeline: intended-use checks, patient-scoped retrieval, prompt-injection and topic checks, claim-level grounding, output validation, and escalation.
- In medical workflows, the model should earn the right to answer by passing support and risk checks, not be trusted by default.

## Source alignment

This note is aligned to these public materials:
- Delphyr, multiple safety checks before, during, and after generation
- Delphyr, exact snippet-level citations rather than post-hoc references
- Abridge, support taxonomy plus severity taxonomy and correction pipeline
- AWS, context precision, response relevancy, and faithfulness as core RAG metrics
- Google Cloud, intended-use boundaries and patient-scoped retrieval
- Hippocratic AI, output testing, escalation, and human supervision

## Sources

- https://www.delphyr.ai/blog/why-medical-ai-needs-multiple-safety-checks
- https://www.delphyr.ai/blog/why-medical-ai-needs-citations-and-how-to-do-it-right
- https://www.abridge.com/ai/science-confabulation-hallucination-elimination
- https://docs.aws.amazon.com/prescriptive-guidance/latest/rag-healthcare-use-cases/evaluation.html
- https://docs.cloud.google.com/generative-ai-app-builder/docs/search-hc-data
- https://www.hippocraticai.com/real-world-evaluation-llm
- https://hippocraticai.com/safety/
