# Claude Instructions

## General Instructions
Keep findings, reseach, insights and other relevant information persisted in this folder, under grouped/organized sub-folders, following @README.md.

## Interview Posture: Architect, Not Implementer

Your role in technical interviews isn't to type code—it's to demonstrate you operate as an architect. Focus on:
- Product thinking and continuous orchestration
- Managing multiple agents/tasks in parallel
- Making decisions that shape what gets built
- Directing implementation, not just executing it

## Session Structure Pattern

**Plan → Spec → Execute (separate sessions)**

1. **Planning phase**: Use AskUserQuestion to interview yourself about technical implementation, UI/UX, edge cases, and tradeoffs. Dig deep until comprehensive.
2. **Spec phase**: Write a complete SPEC.md with all decisions documented.
3. **Execution phase**: Fresh session to implement against the spec. Narrator the flow as you go—this signals systems thinking.

## CLAUDE.md as Anchor

Keep this file under ~150-200 lines. Include:
- Tech stack and code conventions
- Architecture decisions
- Recurring instructions
- Token-efficiency directives

This is your persistent memory across sessions and signals production-minded thinking.

## Context Management Discipline

Primary failure mode: context degradation. Best practices:
- Use `/clear` between tasks
- Use `/compact` when switching context
- Maintain aggressive documentation
- Focus on API changes, not implementation details
- Consider token efficiency in tool design

## Two-Session Review Pattern

First Claude implements, second Claude reviews from fresh context (no knowledge of shortcuts). The reviewer challenges architectural decisions like a staff engineer would. Demonstrating this deliberately separates you from "vibe coders."

## Production Mindset

**Core principle**: Planning before implementation is non-negotiable. "Vibe coding" works for throwaway MVPs, but production code requires structured thinking, validation, and documentation.