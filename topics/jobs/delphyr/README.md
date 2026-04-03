# Delphyr

## Company Overview
- **Founded**: Amsterdam-based healthcare AI startup
- **Mission**: Reduce administrative burden on healthcare professionals so they can focus on patient care
- **Funding**: €1.75M from founders of Hugging Face and DEGIRO
- **Medical Device**: Applied for NDR (medical device) classification

## Product
AI assistants that integrate into existing healthcare systems (HIS/EHR):
- Patient data consolidation (notes, lab results, correspondence)
- Clinical guideline search and retrieval
- Administrative task automation
- Ambient listening for consult notes
- Decision support workflows

## Key Milestones
- **M1**: First Dutch-built clinical language model (native Dutch, privacy-first)
- **M2**: In trials, raising bar for clinical reliability
- Partnerships: ChipSoft, InterSystems, Tetra/Bricks
- Pilots: Erasmus MC (ICU), Dutch Endometriosis Center
- Won STZ Innovation Challenge

## Team (from LinkedIn)
- Michel Abdel Malek MD - CEO & Founder (anesthesiologist)
- Dejan Petković - Lead Engineer
- Tim de Boer - AI Engineer
- Joseph Shepherd, PhD - Medical Data Scientist
- Myrthe Kleijn - Commercial Lead
- Elise Wardenaar - Data Protection Officer

## Interview History
- **Mar 31** - Initial interview (recording + transcript in interviews/)

## Current Status
- Technical interview scheduled April 4, 10:00 with Tim de Boer and Dejan Petković
- Focus: Technical projects, Medical RAG, way of working, cultural fit
## Delphyr Interview Prep

### Logistics
- Interview: Friday, 10:00 local time
- Interviewers: Tim and Dejan
- Background: both are AI engineers

### What They Want To Hear
- Technical depth
- Projects I’ve worked on
- Medical RAG knowledge
- Current way of working, both individually and in a team
- Cultural fit, at least as important as technical skill

### Technical Areas To Prepare
- Production RAG over messy, fragmented clinical data
- Retrieval quality: precision, recall, ranking, chunking, citations
- Safety and guardrails: no-source-no-claim behavior, topic drift, malicious instruction handling
- Compliance and privacy: EU data residency, GDPR, medical-device constraints
- Observability: evaluation loops, monitoring, error recovery, regression prevention
- Workflow embedding: fitting inside existing EHR / GP systems instead of creating a new screen

### Public Stack Signals
Confirmed from Delphyr public pages:
- Site is built on Framer
- Google Tag Manager is installed
- Delphyr uses InterSystems as an integration / infrastructure partner
- Bricks is a live primary-care integration point
- Delphyr has its own M1 clinical model
- The product emphasizes inline citations, guardrails, and end-to-end monitoring
- The product is designed to stay inside existing clinical systems and keep data in Europe

Likely, but not publicly confirmed:
- Backend language / framework
- Vector database / retrieval store
- Orchestration framework for RAG / agents
- Cloud provider and deployment stack

### Delphyr Product Shape
- Clinical AI assistant for doctors and nurses
- Search and summarize patient data
- Access evidence-based guidance
- Ambient listening
- Workflow automation
- Built for Dutch / European healthcare

### Best Angles For Me
- I build production AI systems over messy data, not just demos
- I care about correctness, traceability, and failure modes
- I can talk concretely about retrieval, grounding, and evaluation
- I work well in high-ownership teams and communicate risk early

### Strong Questions To Ask
- How do you evaluate retrieval quality in medical RAG?
- What is the trust boundary between deterministic logic and model reasoning?
- How do citations get generated and verified?
- What does the current stack look like around integration, storage, and orchestration?
- What are the biggest sources of failure in production today?
