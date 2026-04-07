# Healthcare AI Competitive Landscape — Delphyr Context

Saved: 2026-04-07

## Purpose

Understanding where Delphyr sits in the healthcare AI landscape strengthens interview conversations about differentiation, market positioning, and engineering priorities. This is useful whether Delphyr advances or the knowledge transfers to other healthcare AI opportunities.

---

## Delphyr's Position

Delphyr is a Dutch healthcare AI startup building AI agents that integrate into existing clinical systems (HIS/EHR). Their approach:
- **Integration-first**: Works inside existing systems (ChipSoft, Bricks/Tetra, InterSystems) rather than replacing them
- **In-house model**: Delphyr M1 (7B parameter, Dutch-native, EU-hosted), M2 in trials
- **EU data residency**: All patient data processed within European infrastructure
- **Citation-first**: Exact verifiable source quotes, not vague references
- **Product scope**: Patient data consolidation, guideline search, ambient listening, correspondence automation

---

## Competitive Map

### Tier 1: Direct Competitors (European Clinical AI for Existing EHR)

#### Nabla (France)
- **What they do**: Ambient AI assistant for clinical documentation + dictation
- **Scale**: 150+ health systems, 35+ languages, deployed across US and European systems
- **Recent**: M Health Fairview systemwide deployment (2026), partnered with AMI for "world models" to build agentic healthcare AI
- **Stack**: Integrates with all major EHRs (Epic, Oracle Health, etc.)
- **Direction**: Moving from ambient documentation → agentic AI for autonomous workflows

**Compared to Delphyr:**
- Nabla is much larger (150+ health systems vs Delphyr's early pilots)
- Nabla focuses primarily on documentation; Delphyr's scope is broader (data consolidation, guidelines, decision support)
- Nabla's Dutch presence is unclear; Delphyr has native Dutch language and local integrations (ChipSoft, Bricks)
- Delphyr's in-house model is a differentiator vs Nabla's likely external model dependency
- **Key insight**: Delphyr's niche is the Dutch/EU market with native language and local EHR integrations

#### Patientdesk AI (Netherlands)
- **What they do**: Reduces administrative burden for medical professionals
- **Founded**: 2025
- **Scale**: Early stage

**Compared to Delphyr:**
- Direct Dutch competitor, similar mission
- Less publicly visible, less technical detail available
- Delphyr has more public traction (funding, pilots, partnerships)

### Tier 2: Adjacent Competitors (Clinical Documentation AI)

#### Abridge (US)
- **What they do**: AI-powered clinical documentation from patient-clinician conversations
- **Scale**: Large US health system deployments
- **Focus**: Ambient documentation, real-time note generation

#### Suki (US)
- **What they do**: AI assistant for clinical documentation, deeply integrated with EHRs
- **Scale**: Studies show 72% median reduction in documentation time
- **Integrations**: Epic, Oracle Health, athenahealth, MEDITECH

#### Commure (US)
- **What they do**: AI-driven operations from clinical documentation through claims processing
- **Scale**: Integrated with 60+ EHRs
- **Direction**: Revenue cycle management + clinical documentation

**Why these are Tier 2:** US-focused, English-first, and primarily documentation-centric. They don't directly compete with Delphyr in the Dutch/EU market, but they represent the global competitive pressure and where the market is heading.

### Tier 3: EHR Platform AI (incumbent moves)

#### Epic AI
- **What they do**: Adding AI-native features directly into Epic EHR
- **Significance**: When the incumbent platform adds AI, it pressures all overlay/integration startups

#### ChipSoft (Delphyr partner)
- **What they do**: Dutch EHR provider, Delphyr integration partner
- **Risk**: Could build their own AI layer or partner with a different AI provider
- **Opportunity**: For now, the partnership gives Delphyr distribution into Dutch hospitals

---

## Key Market Dynamics

### 1. The "Overlay vs Native" Tension
The biggest strategic question for Delphyr (and all clinical AI startups): will hospitals prefer AI that's native to their EHR, or AI that overlays across systems?

- **Native advantage**: Tighter integration, less friction, preferred by IT teams
- **Overlay advantage**: Works across multiple EHR systems, faster innovation, not locked to one vendor
- **Delphyr's bet**: Overlay approach with deep integration partnerships (ChipSoft, InterSystems, Bricks)

### 2. The Dutch Market Advantage
The Dutch healthcare market is small but structurally favorable for Delphyr:
- Strong EHR adoption (ChipSoft dominates)
- Dutch language creates a natural moat against English-first competitors
- Regulatory environment (MDR, GDPR) rewards EU-based, privacy-first approaches
- Government and institutional support for health innovation

### 3. From Documentation → Decision Support → Agentic Workflows
The market is moving in stages:
1. **Documentation** (current mainstream): Ambient listening, note generation
2. **Decision support** (emerging): Guideline retrieval, patient summary, clinical alerts
3. **Agentic workflows** (next wave): Autonomous preparation of patient cases, correspondence automation, MDT meeting prep

Delphyr is positioned at stages 2 and 3, which is ahead of most competitors who are still at stage 1.

### 4. In-House Model vs External Model
Most clinical AI startups use external models (GPT-4, Claude, etc.). Delphyr built M1 in-house (7B parameter, Dutch-native). This is:
- **Pro**: More control, EU data residency compliance, language specialization, potential cost advantage
- **Con**: Smaller model may have capability limits, higher engineering burden to maintain and improve
- **Strategic**: If MDR classification requires full model transparency, in-house is a significant advantage

---

## Engineering Implications

For someone joining Delphyr as an AI engineer, the competitive landscape suggests these priorities:

1. **Integration depth** is the moat — make the product indispensable inside existing workflows
2. **Citation quality** differentiates from "just another chatbot" — exact verifiable citations are trust-building
3. **Dutch language capability** is a real competitive advantage — don't underinvest
4. **Evaluation rigor** matters for medical device certification — build it early
5. **Agentic capabilities** (MDT prep, correspondence automation) are where the next value creation is
6. **Interoperability** across multiple Dutch EHR systems (not just ChipSoft) widens the addressable market

---

## Interview Value

If asked "where do you see Delphyr in the market?" or "what differentiates Delphyr?":

> "From what I can see, most clinical AI companies are still focused on documentation — ambient listening, note generation. Delphyr is already operating at the decision-support and workflow-automation level, which is where the market is heading. The combination of native Dutch language, in-house model, EU data residency, and deep EHR integrations creates a defensible position that English-first US companies can't easily replicate. The main competitive risk is the EHR platforms themselves building AI, but the partnership model — working inside ChipSoft and Bricks rather than against them — is the right approach."

Sources:
- [Nabla at HIT Consultant](https://hitconsultant.net/2026/03/10/nabla-ami-labs-world-models-agentic-ai-healthcare/)
- [EHR AI arena - TechTarget](https://www.techtarget.com/searchhealthit/feature/EHR-giants-have-entered-the-AI-arena-What-does-it-mean-for-startups)
- [Dutch HealthTech Leaders](https://www.healthcare.digital/single-post/20-future-dutch-healthtech-and-medtech-leaders)
- [Delphyr funding - EU-Startups](https://www.eu-startups.com/2026/03/amsterdam-based-delphy-raises-e1-75-million-to-reduce-healthcare-administrative-workloads-with-ai)
