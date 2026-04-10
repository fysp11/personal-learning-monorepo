# Delphyr First Interview - Michel Abdel Malek

## Round Summary
- Date: Monday, March 31, 2026
- Interviewer: Michel Abdel Malek, CEO and Founder
- Candidate: Fysp
- Format: introductory interview, about 36 minutes
- Main value of this round: role fit, Delphyr technical direction, team shape, and next-step signals

## Candidate Signals Shared
- Currently freelancing and planning a move back to Europe with wife, who works in GDPR / privacy.
- Previous Amsterdam experience at Next Year, including building an engineering analytics platform from scratch.
- Built AI-powered content moderation services processing roughly 30k-60k documents per day.
- Worked on agentic workflows, LangChain/LangGraph-style integrations, RAG systems, and grounded workflows connected back to business systems.
- Built self-healing monitoring agents that recovered broken collection workflows and saved roughly 20 engineering hours per week.
- Strong recurring positioning: production AI over messy data, not demos.

## Technical Discussion Highlights
- Discussed agentic AI evaluation frameworks and the need to measure intermediate actions, not only final outputs.
- Framed speed vs recall/precision as an evaluation-design problem: define expected actions, retrieval requirements, scoring criteria, and failure thresholds.
- Emphasized granular evaluation: score actions, retrieval behavior, output quality, and business outcome separately.
- Discussed agentic workflows as systems that need rollback / commit-style safeguards before destructive or high-risk actions.
- Positioned clinical AI as needing runtime checks, offline trials, side-channel learning from failures, and confidence-aware routing.
- Argued that determinism is still needed around the model: the AI can be the flexible brain, but the harness and workflow boundaries carry trust.
- Described using AI coding and agent tools pragmatically, while keeping focus on whether they create business value instead of just novelty.

## Delphyr Context Learned
- Delphyr builds components in-house end to end: model, harness, platform, search engine, embedding models, and related control layers.
- In-house ownership gives flexibility over hosting, EU infrastructure, traceability, and control over every part of the stack.
- Delphyr is applying for medical device classification under MDR, aiming for clinical trust comparable to approved medical tools.
- Current product direction combines patient data with clinical knowledge so doctors can get advice and workflow support.
- Current technical focus includes decision graphs and agentic workflows.
- A concrete next use case is MDT preparation: build a digital case from patient data plus guideline knowledge, then help clinicians understand the decision to make.
- Other future workflow areas include patient intake and hospital administrative workflows.

## Team Signals
- Team included two senior architects, one mid-senior data scientist, and junior data engineers.
- Michel was leading the team from an HR perspective, with senior technical people leading engineering details.
- There is enough work to justify hiring if the person fits the team and knows what they are talking about.
- Delphyr is also hiring in GDPR/privacy-related areas.

## Strongest Fit Signals
| Area | Signal |
| --- | --- |
| Production AI | Your document-scale and agentic workflow experience maps well to Delphyr's practical needs |
| Healthcare AI | You treated privacy, correctness, and rollback as first-order constraints |
| RAG and grounding | Your instinct was to separate retrieval, evidence, evaluation, and final action |
| Team fit | High ownership, practical communication, and ability to work in ambiguity matched the team shape |
| Business fit | You connected technical choices to sustainability, trust, and actual workflow value |

## Follow-Up Angles
- Ask how Delphyr evaluates correctness for patient-data retrieval and clinical-guideline support.
- Ask what parts of the platform are already stable versus what still needs agentic workflow design.
- Ask where decision graphs sit between deterministic clinical logic and model-driven reasoning.
- Ask how MDR classification changes engineering process, documentation, and release cadence.
- Ask what success looks like for MDT preparation in the first production workflows.

## Handoff To The Next Round
Use this round to anchor Delphyr's real needs: medical RAG, citations, evaluation, decision graphs, agentic workflow safety, and in-house infrastructure control. Then move to `../2-technical--dejan-tim/README.md` and `../../INTERVIEW-PREP.md` for the technical interview prep.
