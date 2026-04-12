# Ambient Listening Architecture — Engineering Analysis for Delphyr

Saved: 2026-04-11

## Context

Delphyr's March 2026 funding announcement added **ambient listening** as a product surface: "Securely capturing consultations and automatically transforming them into structured clinical notes." This is a distinct engineering challenge from RAG/summarization and warrants dedicated analysis.

---

## The Pipeline: Audio → Structured Clinical Notes

### Stage 1: Audio Capture & Pre-Processing

**Challenge:** Clinical consultations happen in diverse acoustic environments — exam rooms, phone calls, bedside.

- **Input:** Raw audio stream (likely via browser/app microphone)
- **Processing:** Noise reduction, voice activity detection (VAD), chunking into utterance segments
- **Privacy constraint:** Audio must never leave the practice environment. Processing must be local or on EU-resident infrastructure.

**Key engineering decision:** Stream processing vs batch processing. Real-time feedback (showing notes as the conversation happens) is much harder than post-consultation processing, but significantly more valuable clinically — the doctor can verify notes while context is fresh.

### Stage 2: Automatic Speech Recognition (ASR)

**Options landscape (2026):**

| Approach | Pros | Cons |
|----------|------|------|
| **Whisper (open-source)** | Self-hosted, EU-compliant, Dutch support | Requires GPU infra, latency trade-offs |
| **WhisperKit (Apple)** | On-device, zero-network, fast | Apple-only, limited customization |
| **Azure Speech** | Production-grade, medical vocabulary | Data leaves practice to Microsoft cloud |
| **In-house fine-tuned** | Maximum control, clinical vocabulary | Huge investment for 6-person team |

**Likely Delphyr approach:** Whisper-based, self-hosted on EU infrastructure, potentially fine-tuned on Dutch medical vocabulary. The HuggingFace investor connection makes this approach natural.

**Dutch language nuance:** Dutch medical terminology mixes Dutch, Latin, and English. ASR must handle code-switching within a single consultation. Example: "De patiënt presenteert met dyspnoe, we doen een CT-thorax en checken de D-dimeer."

### Stage 3: Speaker Diarization

**Challenge:** Distinguishing doctor from patient in audio.

**Why this matters clinically:**
- Patient statements → Subjective section (S in SOAP)
- Doctor observations → Objective section (O in SOAP)
- Mis-attribution corrupts the clinical record

**Technical approaches:**
1. **Pre-registered voices:** Doctor enrolls their voice profile → simpler diarization
2. **Turn-based heuristics:** Doctor speaks first, longer utterances, medical terminology density
3. **Neural diarization:** Speaker embedding models (e.g., pyannote.audio)

**Practical pattern:** Combine approaches 1+3. Pre-register the doctor's voice (known speaker), then classify all other speakers as patient/family/other.

### Stage 4: Clinical Note Structuring

**The core AI challenge.** Convert free-form conversation into structured clinical notes.

**Target format: SOAP Notes**

| Section | Source | AI Task |
|---------|--------|---------|
| **S**ubjective | Patient statements | Extract chief complaint, history, symptoms |
| **O**bjective | Doctor observations | Extract exam findings, test results, vital signs |
| **A**ssessment | Doctor reasoning | Extract diagnosis, differential, clinical impression |
| **P**lan | Doctor decisions | Extract treatment, prescriptions, follow-up, referrals |

**Why this is harder than it looks:**
- Medical conversations are non-linear (patient returns to earlier symptoms mid-conversation)
- Implicit information (doctor doesn't say "blood pressure is normal" — they just don't mention it)
- Negation matters enormously ("no chest pain" vs "chest pain")
- Abbreviations and shorthand vary by doctor and specialty

### Stage 5: Citation & Verification

**Every structured note element must link back to source audio.**

```
SOAP Note:
  S: Patient reports chest pain for 3 days [audio: 02:15-02:45]
  O: Blood pressure 140/90 [audio: 08:30-08:42]
  A: Suspected hypertension [audio: 12:10-12:25]
  P: Start amlodipine 5mg, follow-up in 2 weeks [audio: 14:00-14:30]
```

This is the same **"retrieve, don't reason"** principle from MDT prep — the AI structures and links, it doesn't invent clinical facts.

### Stage 6: Human Review & Sign-off

The doctor reviews the generated note before it enters the patient record. This is not optional — it's both a quality gate and a legal requirement.

**UI implication:** The review interface must make it fast to:
1. Scan the structured note
2. Click any claim to hear the source audio
3. Edit/correct any section
4. Approve and push to the EHR (ChipSoft/InterSystems)

---

## Privacy Architecture: The Highest Stakes

Ambient listening processes **live patient conversations** — the most sensitive data category in healthcare.

### Data Flow Constraints

```
Microphone → [Local/EU processing only]
    ↓
Audio buffer → [Encrypted at rest, auto-deleted after note approval]
    ↓
ASR → Transcript → [PHI tagged, access-logged]
    ↓
Structuring → SOAP Note → [Human review required]
    ↓
Approved note → EHR integration → [Patient record]
    ↓
Audio buffer → [Deleted after approval + retention period]
```

**Key principle:** Audio is transient. The structured note is the artifact. Audio exists only long enough for verification, then must be deleted.

### Consent Architecture

- **Patient consent:** Must be obtained before recording starts (informed consent)
- **Opt-out:** Patient can request recording stops at any point
- **Selective deletion:** Patient can request deletion of their audio/notes
- **Audit trail:** Every access to audio/transcript is logged

### GDPR + EU AI Act Implications

- **Data minimization:** Don't store more audio than needed for verification
- **Purpose limitation:** Audio captured for note generation can't be repurposed for model training without separate consent
- **Transparency:** Patient must know AI is generating notes from their conversation
- **High-risk AI system:** Ambient listening in healthcare is almost certainly Class III under EU AI Act → requires conformity assessment

---

## Engineering Challenges Unique to Ambient Listening

### 1. Real-Time vs Batch Trade-off

| Aspect | Real-Time | Batch (Post-Consultation) |
|--------|-----------|--------------------------|
| User experience | Notes appear during conversation | Notes available after |
| Accuracy | Lower (streaming ASR) | Higher (full-context ASR) |
| Correction ease | Doctor can fix while memory is fresh | Harder to verify later |
| Infrastructure | WebSocket + streaming pipeline | Simpler batch job |
| Latency budget | ~2-5 seconds per utterance | Minutes acceptable |

**Likely Delphyr approach:** Hybrid — real-time draft (lower accuracy, serves as live memory aid), batch refinement after consultation (higher accuracy, generates final note).

### 2. Multi-Language Consultations

In the Netherlands, consultations may mix Dutch, English, and patient native languages. The ASR and structuring pipeline must handle this gracefully.

### 3. Specialty-Specific Structuring

SOAP is standard for primary care, but:
- Psychiatry uses different note structures (process notes, mental status exam)
- Surgery has operative notes
- Radiology has structured reporting templates

The structuring model must be specialty-aware.

---

## How This Connects to Existing Prep

| Existing Concept | Ambient Listening Application |
|-----------------|------------------------------|
| **Citation verification** (`code/citation-verification.ts`) | Audio timestamp → claim linking |
| **Guardrail pipeline** (`prep/rag-guardrail-architecture-design.md`) | Input guard: consent check; Output guard: clinical accuracy |
| **Safety harness** (`experiments/agent-safety-harness/`) | Staged processing with human sign-off before commit to EHR |
| **Confidence routing** (cross-company pattern) | Low-confidence sections flagged for doctor attention |
| **MDT prep** (`insights/agentic-mdt-workflow-deep-dive.md`) | Both are about structuring unstructured clinical information |

---

## Interview Follow-Up Angle

If advancing to another round at Delphyr:

> "I've been thinking about the ambient listening surface since I saw the announcement. The engineering challenge that interests me most is the gap between ASR accuracy and clinical accuracy — a transcript can be word-perfect but still generate a wrong SOAP note if the structuring model misattributes a statement or misses a negation. That's where evaluation frameworks for clinical note quality become critical, and it's very similar to the citation verification work I explored in our earlier conversation."

---

## Potential Experiment: Mock Consultation → SOAP Pipeline

**Input:** A text-based mock consultation transcript (doctor/patient labeled)
**Pipeline:**
1. Parse speaker labels
2. Extract SOAP components using structured LLM output
3. Link each SOAP element to source transcript lines
4. Evaluate: completeness, speaker attribution accuracy, negation handling
5. Compare against hand-written reference SOAP note

**Why build this:** Demonstrates understanding of Delphyr's newest product direction, goes beyond the search/summary features that were the earlier focus.
