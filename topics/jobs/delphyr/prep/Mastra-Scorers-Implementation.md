# Mastra Scorers Implementation

Date: 2026-04-03

## Core implementation model

Mastra scorers are built with `createScorer(...)`, which returns a `MastraScorer` instance.

Internally, a scorer is a small pipeline with up to four ordered steps:
- `preprocess`
- `analyze`
- `generateScore`
- `generateReason`

`generateScore` is required. The others are optional.

Source:
- `packages/core/src/evals/base.ts`

## How steps work

Each step can be implemented in one of two ways:

- function step
- prompt-object step

### Function step

A plain TypeScript function.

It does not call the LLM judge.

Example shape:

```ts
.generateScore(({ results }) => {
  return 1;
})
```

### Prompt-object step

An object with:
- `description`
- `createPrompt`
- `outputSchema` for `preprocess` and `analyze`

This does call the judge model.

Example shape:

```ts
.analyze({
  description: "Check support",
  outputSchema: z.object({ verdicts: z.array(z.string()) }),
  createPrompt: ({ run, results }) => "...",
})
```

## How the judge is used

If a step is a prompt-object step, Mastra:

1. builds the prompt with `createPrompt(...)`
2. resolves the model from the scorer-level `judge` or step-level `judge`
3. creates an internal `Agent` called `judge`
4. runs the prompt through that judge agent
5. parses structured output with the provided schema when needed

Implementation details:
- `generateScore` prompt steps must return `{ score: number }`
- `generateReason` prompt steps return plain text
- `preprocess` and `analyze` prompt steps return structured objects validated by schema

Source:
- `packages/core/src/evals/base.ts`

## Execution flow in code

When you call `await scorer.run(...)`, Mastra:

1. validates that `generateScore` exists
2. assigns a `runId` if missing
3. creates a scorer-run span for observability
4. converts the scorer into a workflow
5. runs each step in order
6. accumulates intermediate results under:
   - `preprocessStepResult`
   - `analyzeStepResult`
   - `generateScoreStepResult`
   - `generateReasonStepResult`
7. returns a final object with:
   - `score`
   - `reason`
   - intermediate results
   - prompts used by LLM-backed steps

Important:
- Mastra literally compiles the scorer into a workflow using `createWorkflow(...).then(step)...`

Source:
- `packages/core/src/evals/base.ts`

## What gets returned from `.run()`

Mastra returns:
- `score`
- `reason`
- `preprocessStepResult`
- `analyzeStepResult`
- `preprocessPrompt`
- `analyzePrompt`
- `generateScorePrompt`
- `generateReasonPrompt`

This is useful because scorer runs are inspectable, not just final numbers.

Source:
- `docs/src/content/en/reference/evals/mastra-scorer.mdx`
- `packages/core/src/evals/base.ts`

## Built-in scorer pattern

Built-in LLM scorers follow a common pattern:

1. `preprocess`
   - extract claims or intermediate structure from output
2. `analyze`
   - ask the judge to classify or verify those items
3. `generateScore`
   - compute a numeric score in plain TypeScript
4. `generateReason`
   - optionally ask the judge to explain the score

### Faithfulness scorer

Implementation:
- `preprocess` extracts claims from the answer
- `analyze` checks each claim against context
- `generateScore` computes:
  - supported claims / total claims
- `generateReason` summarizes the verdicts

Source:
- `packages/evals/src/scorers/llm/faithfulness/index.ts`

### Context precision scorer

Implementation:
- `analyze` checks each context chunk for relevance
- `generateScore` computes Mean Average Precision (MAP)
- supports either:
  - a static `context` array
  - a dynamic `contextExtractor(...)`

Source:
- `packages/evals/src/scorers/llm/context-precision/index.ts`

### Hallucination scorer

Implementation:
- `preprocess` extracts claims
- `analyze` checks whether claims are contradicted by context
- `generateScore` computes:
  - contradicted statements / total statements
- supports either:
  - static `context`
  - dynamic async `getContext(...)`

Source:
- `packages/evals/src/scorers/llm/hallucination/index.ts`

## Code-only scorer pattern

Not all scorers use an LLM judge.

Example: code tool-call accuracy scorer

Implementation:
- `preprocess` extracts actual tool calls from run output
- `generateScore` computes a deterministic score based on:
  - expected tool
  - optional strict mode
  - optional expected tool order

This is a pure TypeScript scorer with no judge model involved.

Source:
- `packages/evals/src/scorers/code/tool-call-accuracy/index.ts`

## Practical implications

### What Mastra scorers are good at

- making evaluation pipelines inspectable
- mixing deterministic scoring with LLM judgment
- exposing intermediate artifacts for debugging
- reusing a common scorer interface across agents and experiments

### What to watch out for

- prompt-object steps add judge-model latency and cost
- LLM-based scorer outputs are only as stable as the prompt and model
- some built-in metrics are implemented as judge classifications plus a simple ratio, so you should inspect how the verdicts are produced before trusting the score

## Interview-ready summary

If asked how Mastra scorers work internally:

- They are pipeline-based evaluators built with `createScorer`.
- Each scorer is compiled into a workflow with steps like `preprocess`, `analyze`, `generateScore`, and `generateReason`.
- Steps can be deterministic functions or LLM-judged prompt objects.
- Built-in scorers usually use the LLM to classify evidence or claims, then compute the final numeric score in TypeScript.
- The run output includes the score, reasoning, intermediate step results, and the prompts used, which makes the evaluation traceable.

## Sources

- https://github.com/mastra-ai/mastra/blob/main/packages/core/src/evals/base.ts
- https://github.com/mastra-ai/mastra/blob/main/docs/src/content/en/reference/evals/create-scorer.mdx
- https://github.com/mastra-ai/mastra/blob/main/docs/src/content/en/reference/evals/mastra-scorer.mdx
- https://github.com/mastra-ai/mastra/blob/main/packages/evals/src/scorers/llm/faithfulness/index.ts
- https://github.com/mastra-ai/mastra/blob/main/packages/evals/src/scorers/llm/context-precision/index.ts
- https://github.com/mastra-ai/mastra/blob/main/packages/evals/src/scorers/llm/hallucination/index.ts
- https://github.com/mastra-ai/mastra/blob/main/packages/evals/src/scorers/code/tool-call-accuracy/index.ts
