# Agentic Design Patterns (System-Theoretic Framework) - Study

Saved: 2026-04-20
Source: https://arxiv.org/html/2601.19752v1

## Why This Matters

Most "agentic systems" writing is either:
- too high-level to implement
- too tool-specific to generalize
- too centered on prompting tricks instead of system structure

This paper is useful because it tries to be structural:
- define core subsystems of an agentic system
- map recurring failure classes to those subsystems
- propose reusable patterns that address those failures

Use this as an architecture lens for building a real agentic system, not as a complete production recipe.

## Core Decomposition (5 Subsystems)

The paper decomposes an agent into five interacting subsystems:

1. Reasoning and world model
2. Perception and grounding
3. Action execution
4. Learning and adaptation
5. Inter-agent communication (optional)

The key takeaway is separation: reliability comes from explicit subsystems, not one monolithic "LLM loop."

## Failure Taxonomy (5 Classes)

1. World modelling
2. Cognitive and decision
3. Execution and interaction
4. Learning and governance
5. Collaboration mechanism

Practical benefit: it forces the question "which failure class are we solving?" instead of vague fixes like "add memory."

## Pattern Catalogue (12 Patterns)

Foundational:
- Integrator
- Retriever
- Recorder

Cognitive and decisional:
- Selector
- Planner
- Deliberator

Execution and interaction:
- Executor
- Tool use
- Coordinator

Adaptive and learning:
- Reflector
- Skill build
- Controller

## What To Import Into Our Agentic Design

### 1) Integrator before reasoning

Treat this as a hard requirement: no raw input reaches the world model.

Integrator responsibilities:
- schema validation
- provenance tags (source, timestamp, trust level)
- normalization into typed internal state
- confidence scoring when possible

### 2) Separate planning from action choice

Keep two distinct artifacts:
- Planner output: explicit staged plan, inspectable
- Deliberator output: the next concrete action given current state and policy

Do not let execution improvise policy.

### 3) Recorder as first-class infrastructure

You want resumability and auditability.

Record:
- plan
- step state and tool call results
- checkpoints (resume tokens / state snapshots)
- failure snapshots for later diagnosis

### 4) Tool use is a controlled boundary

All side effects must cross a strict interface:
- typed schemas
- permission checks
- deterministic wrappers for side effects
- structured results (not free-form text)
- correlation IDs and tool-call logs

### 5) Governance is not "in the prompt"

Controller responsibilities:
- allow/deny checks for actions
- approval gates by risk tier
- invariant checks (never do X without Y)
- audit logging

### 6) Multi-agent is optional, not default

Add a Coordinator only when there is a real boundary:
- distinct permissions
- distinct toolsets or context constraints
- real parallel branches
- coordination boundary is easier to test than one large agent

Avoid multi-agent for theater.

### 7) Learning belongs post-run

Reflector and Skill build suggest:
- analyze outcomes after execution
- extract stable playbooks/skills from repeated success
- feed improvements into future runs, not ad-hoc mutation mid-run

## Minimal "Serious v1" Architecture

1. Integrator
2. Retriever + Recorder
3. Planner
4. Deliberator
5. Tool use + Executor
6. Controller
7. Reflector

This is enough to be agentic while keeping behavior observable, bounded, and debuggable.

## Concrete Rules (Fast Scan)

- Rule 1: No unvalidated input reaches reasoning.
- Rule 2: Plan, decision, execution, and outcome are separately observable.
- Rule 3: Tool execution is typed and permissioned.
- Rule 4: Workflow state is resumable from durable checkpoints.
- Rule 5: Learning updates future runs, not current runs unpredictably.
- Rule 6: Policy and approvals live outside the reasoning prompt.
- Rule 7: Multi-agent must justify itself with a real boundary.

## One-Sentence Takeaway

Reliable agentic systems are not smarter prompt loops; they are explicit subsystems for grounding, reasoning, execution, learning, and optional coordination.
