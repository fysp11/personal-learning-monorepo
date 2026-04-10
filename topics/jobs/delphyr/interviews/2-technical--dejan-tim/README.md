# Delphyr Technical Interview Prep — Tim & Dejan

Date: 2026-04-03
Interview: Friday, 10:00 local time
Interviewers: Tim de Boer (AI Engineer), Dejan Petković (Lead Engineer)

## Top Strategy

This interview is not just "do you know RAG?" It is closer to: **can you talk like someone who has built real AI systems under constraints, understands reliability, and would work well in a small high-ownership team?**

The best positioning is:
- practical, not hypey
- technical, but not academic for its own sake
- calm about trade-offs and failure modes
- honest about gaps, strong on learning speed and system judgment

Lead with **production experience over messy data**, then connect that to Delphyr's world:
- medical RAG over fragmented records
- exact citations and verification
- guardrails and evaluation
- integration inside existing clinical systems
- privacy / EU constraints

## What To Optimize For

### 1. Technical credibility first
They want to hear concrete implementation judgment, not generic AI enthusiasm.

Good signals:
- architecture decisions and trade-offs
- evaluation and monitoring thinking
- how you handle failure modes
- how you balance speed vs correctness

### 2. Practical relevance
Especially with Tim, good answers should sound clinically useful, not just technically clever.

### 3. Strong working style
They also want to know how you work:
- individually
- in small teams
- with business/product constraints
- under ambiguity

### 4. Cultural fit
Cultural fit is explicitly important. Come across as:
- thoughtful
- low-ego
- high-ownership
- collaborative
- genuinely interested in their mission and team

## What Tim Likely Cares About

Based on his notes and Delphyr writing:
- citations as a hard requirement for trust
- exact source quotes, not vague references
- practical medical RAG reliability
- evaluation frameworks for factuality and safety
- clinical usefulness over buzzwords

### Best angle with Tim
Talk about:
- claim-level grounding
- no-source-no-claim behavior
- how you would verify citations and support
- how to make outputs cheap for clinicians to trust and review

### Best Tim Answer Style
- Start from the clinical risk.
- Explain how to make outputs verifiable.
- Mention concrete checks: citations, support validation, and abstention.
- Prefer traceable correctness over speed.

### Strong Tim Phrases
- "In medical AI, retrieval without verifiability is only a partial solution."
- "I would rather make the system slower but easier to trust."
- "Claim-level evidence matters more than document-level references."

### Avoid With Tim
- Treating citations like a UX add-on.
- Talking about RAG like it automatically solves hallucinations.
- Sounding impressed by model capability without discussing trust.

## What Dejan Likely Cares About

Based on his notes:
- implementation depth
- systems/integration thinking
- agentic workflows
- building in-house vs buying
- technical decision-making in a small engineering team

### Best angle with Dejan
Talk about:
- how you structure systems under real constraints
- how you evaluate architecture trade-offs
- how you deal with integrations and operational complexity
- when you would build specialized components vs rely on external tools

### Best Dejan Answer Style
- Explain the problem.
- Describe the architecture.
- Name trade-offs.
- Discuss failure modes.
- Explain monitoring and iteration.

### Strong Dejan Phrases
- "I try to optimize for operability, not just elegance."
- "I would separate what must be deterministic from what can be model-driven."
- "Build-vs-buy depends on trust boundaries, speed, and how core the capability is."

### Avoid With Dejan
- Hand-wavy system descriptions.
- Ideology about frameworks or vendors.
- Overfocusing on prompts instead of architecture and operations.

## Best Topics To Be Ready On

### 1. Your project stories
Be ready to talk concretely about:
- engineering analytics platform from scratch
- AI moderation systems processing 30k–60k docs/day
- RAG systems over messy / fragmented data
- agentic workflows and LangChain integrations
- self-healing monitoring agents that saved time

For each one, be ready with:
- the problem
- architecture
- trade-offs
- failure modes
- what you measured / monitored
- what you would improve in hindsight

### 2. Medical RAG
Best practical topics to have fresh:
- why medical RAG is a verification system, not just retrieval
- patient-scoped retrieval
- exact citations vs document-level references
- hybrid retrieval over fragmented data
- context precision, faithfulness, and support validation
- intended-use boundaries: retrieve/summarize vs diagnose/prescribe

### 3. Guardrails and evals
Be ready to explain:
- staged guardrails, not one moderation call
- support vs severity as separate axes
- how you would evaluate extraction, retrieval, generation, final output
- realistic scenario testing and monitoring after deployment

### 4. Way of working
They will likely probe:
- how you manage projects
- how you balance technical and business thinking
- how you work in small teams
- how you communicate risks early
- how you collaborate cross-functionally

## Best Positioning For You

These are the strongest positioning lines from the current prep materials:

- I build production AI systems over messy data, not just demos.
- I care about correctness, traceability, and failure modes.
- I can discuss retrieval, grounding, and evaluation concretely.
- I work well in high-ownership teams and communicate risks early.

### Strong bridge into Delphyr
"What attracts me here is that Delphyr seems to care about the same things I care about in production AI: correctness, auditability, fitting into real workflows, and building trustworthy systems rather than flashy demos."

## Best Answer Shape

For most technical questions, use this structure:

1. **Start with the real problem**
   - what made it hard in practice?
2. **Explain your approach**
   - architecture or process, at a useful level of depth
3. **Name the trade-offs**
   - speed vs recall, simplicity vs control, build vs buy, etc.
4. **Discuss failure modes**
   - what could go wrong?
5. **Explain how you evaluated / monitored it**
6. **End with practical judgment**
   - what you learned or would change

This answer shape will make you sound experienced and calm.

## What To Avoid

- generic LLM hype
- speaking only in abstractions without implementation details
- overclaiming healthcare expertise
- sounding dogmatic about one architecture choice
- getting lost in theory without connecting it to workflow value
- acting like citations or guardrails are just UX features
- making build-vs-buy sound ideological instead of practical

## Known Gaps — And How To Handle Them

### Healthcare domain gap
Do not fake medical depth.

Better framing:
- you already understand the systems problem
- you take high-risk domains seriously
- you know where healthcare changes the engineering bar
- you are excited to learn domain specifics quickly

### Microsoft / Azure gap
If it comes up, be direct. Position yourself as someone who learns infrastructure stacks quickly once the problem and constraints are clear.

### MDR / medical-device gap
Do not pretend expertise. Show respect for regulated environments and explain how your instincts already fit them:
- auditability
- traceability
- explicit failure handling
- strong boundaries

## Good Questions To Ask Them

Ask only a few, but make them strong.

Best options:
- What is the biggest technical challenge you are facing right now?
- How do you evaluate retrieval quality and output reliability in production?
- What is the trust boundary today between deterministic logic and model reasoning?
- How are citations generated and verified in practice?
- What does success look like in the first 3 months for this role?

## Interviewer-Specific Pivots

If Tim asks how to make medical RAG trustworthy:
- Pivot to citations, support validation, patient scope, and abstention.

If Tim asks how to evaluate output quality:
- Pivot to support vs severity, scenario testing, and clinician review.

If Dejan asks about a system you built:
- Pivot to architecture, trade-offs, monitoring, and lessons learned.

If Dejan asks how you would design this at Delphyr:
- Pivot to integrations, trust boundaries, operational simplicity, and staged rollout.

## Best Overall Positioning

To Tim:
> I care about whether the system can justify what it says.

To Dejan:
> I care about whether the system can run reliably in the real world.

To both:
> I like building AI systems that are useful, testable, and trustworthy, not just impressive in demos.

## Final Reminder

The goal is not to prove you know everything about healthcare AI.

The goal is to show that you:
- think clearly about real systems
- care about reliability and trust
- can talk concretely about architecture and trade-offs
- would be a strong engineer to build with in a small team
