# Delphyr — Clinical AI Landscape Update (April 2026)

Saved: 2026-04-10

## Purpose

Fresh intelligence on Delphyr and the clinical AI landscape, gathered to deepen preparation and identify new angles for follow-up conversations.

---

## Delphyr Company Update

### Funding Round Confirmed

- **€1.75 million** raised in March 2026
- Investors include **founders of Hugging Face and DEGIRO**
- This is a pre-seed/seed round — Delphyr is very early stage

### Product Updates

New public messaging includes:

1. **Ambient listening**: Securely capturing consultations and automatically transforming them into structured clinical notes, directly linked to the patient record
2. **Quick search and summary**: Consolidating patient data from notes, lab results, and correspondence for a clear overview
3. **Clinical guideline access**: Instant access to relevant guidelines and trusted sources
4. **Integration focus**: Does not replace existing systems; enhances them with an intelligent layer

### Technical Positioning

- Runs on **secure European infrastructure**
- Processes patient data **exclusively within the practice environment**
- Designed for compliance with **EU AI Act**
- Covers **hospitals, primary care, and mental health settings**

### Updated Team Signal

The confirmed team from public sources:
- Michel Abdel Malek, MD — CEO and Founder
- Dejan Petkovic — Lead Engineer
- Tim de Boer — AI Engineer
- Joseph Shepherd, PhD — Medical Data Scientist
- Myrthe Kleijn — Commercial Lead
- Elise Wardenaar — Data Protection Officer

With €1.75M and ~6 people, this is a very lean team. Every hire has massive leverage.

---

## Key New Angles

### 1. Ambient Listening Is a New Product Surface

This wasn't prominent in earlier prep. Ambient listening (capturing consultations → structured notes) is a separate technical challenge from the RAG/summarization work:

- **Real-time audio processing** — likely using Whisper or similar ASR
- **Speaker diarization** — distinguishing doctor from patient in audio
- **Clinical note structuring** — converting free-form conversation into SOAP notes or similar structured formats
- **Privacy implications** — processing live audio of patient conversations is the highest-sensitivity data category

**Interview angle:** "I noticed Delphyr has added ambient listening. The engineering challenge is fascinating — real-time ASR with clinical accuracy requirements, speaker diarization, and instant structuring into clinical note formats. How mature is this capability vs the search/summary features?"

### 2. Hugging Face Founder Investment

Having Hugging Face founders as investors is a strong signal:
- Access to model expertise and HF infrastructure
- Validation of the technical approach
- Potential strategic advantage for model training and deployment
- Aligns with the "in-house model" approach (M1/M2)

**Interview angle:** "With Hugging Face founders as investors, does Delphyr have access to specialized support for model training and deployment?"

### 3. EU AI Act Compliance as Feature

Delphyr explicitly positions EU AI Act compliance as a product feature, not just a legal requirement. This aligns with the prep insight that "compliance and good engineering are the same thing."

**Timeline pressure:** EU AI Act high-risk obligations are enforceable from **August 2026** — only 4 months away. For a medical AI classified as high-risk, this is an active engineering deadline.

---

## Competitive Landscape Update

### Direct Competitors in Clinical AI (Netherlands/EU)

| Company | Focus | Key Differentiator |
|---------|-------|-------------------|
| **Delphyr** | Clinical decision support, ambient listening | Dutch-built model, HIS integration, EU-only infrastructure |
| **Abridge** | Ambient clinical documentation | Largest in ambient documentation, US-focused |
| **Nabla** | Clinical documentation AI | French, strong EU presence, ambient + structured notes |
| **Hippocratic AI** | Clinical AI agents | US-focused, safety-first approach, recently raised $150M+ |
| **Glass Health** | Clinical decision support | Evidence-based treatment plans, US-focused |
| **Viz.ai** | Clinical AI for specific conditions | MDR Class IIa certified, stroke detection focus |

### Key Differentiators for Delphyr

1. **Dutch/EU-first**: Most competitors are US-based; EU data residency is a real advantage
2. **HIS integration**: ChipSoft/InterSystems integration positions for the Dutch hospital market
3. **In-house model**: M1 as a Dutch-native clinical model is differentiated vs pure API wrappers
4. **Full workflow**: Combining ambient listening + search + summarization in one platform

---

## Technical Experiments To Deepen

### Experiment: Ambient Clinical Note Structuring

Given the new product surface, a relevant experiment would be:

**Audio → structured clinical note pipeline:**

1. Take a mock consultation source record (text, not actual audio)
2. Apply speaker diarization labels (Doctor/Patient)
3. Extract structured SOAP note components:
   - **S**ubjective: Patient's chief complaint and history
   - **O**bjective: Examination findings, lab results
   - **A**ssessment: Diagnostic impression
   - **P**lan: Treatment plan, follow-up
4. Add citation links back to the source record
5. Evaluate: completeness, accuracy, PHI handling

**Why this matters:** Demonstrates understanding of Delphyr's newest product direction, not just the search/summary features that were the focus of earlier prep.

### Experiment: Clinical Confidence Calibration

Build on the existing evaluation code to add confidence calibration:

1. For each extraction/summarization output, include a confidence score
2. Bin predictions by confidence level
3. Measure actual accuracy per bin
4. Plot reliability diagram (calibration curve)
5. Calculate Expected Calibration Error (ECE)

**Why this matters:** Calibration is the bridge between Finom and Delphyr prep — both companies need confidence scores that are meaningful, not just numbers. Demonstrating this with clinical data adds domain specificity.

---

## Status Check: What Happened After April 4?

The technical interview with Tim de Boer and Dejan Petkovic was scheduled for Friday, April 4, 2026. **No outcome has been recorded.** Possible states:

1. **Interview happened, no follow-up yet** — Normal; 6 business days have passed
2. **Interview happened, waiting on next steps** — The technical materials were strong; follow-up should be checked
3. **Interview didn't happen / rescheduled** — Less likely given the prep level

**Recommended action:** Check email/messages for any Delphyr communication. If no news after 2 weeks (April 18), a polite follow-up to the recruiter/Michel is appropriate.

---

## Transferable Insights

### From This Update → Finom Prep

- The **ambient listening** pattern maps to Finom's document processing: real-time input → structured output → confidence routing
- The **EU AI Act compliance pressure** (August 2026) applies to both companies
- The **lean team, high leverage** dynamic at Delphyr contrasts with Finom's larger org — useful for framing why you're comfortable in either context

### From Finom Prep → Delphyr Follow-Up

- Finom's **adoption engineering** patterns apply directly to clinical tool adoption
- The **multi-market expansion** framework (DE → FR) parallels potential Delphyr expansion beyond Netherlands
- The **central AI vs embedded** org thinking becomes relevant as Delphyr grows past 6 people

---

## Sources

- [EU-Startups: Delphyr raises €1.75 million](https://www.eu-startups.com/2026/03/amsterdam-based-delphy-raises-e1-75-million-to-reduce-healthcare-administrative-workloads-with-ai)
- [Fintech Global: Dutch health AI startup Delphyr raises €1.75m](https://fintech.global/2026/03/11/dutch-health-ai-startup-delphyr-raises-e1-75m/)
- [Delphyr official site](https://www.delphyr.ai/)
- [AI Journal: Delphyr raises €1.75 million](https://aijourn.com/delphyr-raises-e1-75-million-to-give-healthcare-professionals-time-back-with-ai/)
- [PR Newswire: Delphyr funding announcement](https://www.prnewswire.com/news-releases/delphyr-raises-1-75-million-to-give-healthcare-professionals-time-back-with-ai-302700171.html)
