# Clinical AI Vocabulary Quick Reference

## Purpose
Rapid recall cheat sheet for healthcare AI and clinical terminology. Use for last-minute review before Delphyr interviews.

---

## Clinical Document Types

| Type | Abbreviation | What It Contains |
|------|-------------|------------------|
| **Progress note** | — | Daily clinician notes on patient status |
| **Discharge summary** | DC summary | Summary at patient discharge (diagnosis, treatment, follow-up) |
| **Consultation note** | Consult | Specialist opinion requested by another clinician |
| **Lab report** | Labs | Laboratory test results |
| **Radiology report** | Imaging | Imaging findings (CT, MRI, X-ray, ultrasound) |
| **Pathology report** | Path | Tissue/biopsy analysis results |
| **Medication list** | MAR | Current medications with doses and schedules |
| **Allergy list** | — | Known allergies and reactions |
| **Operative report** | Op note | Surgical procedure description |
| **Nursing notes** | — | Nursing observations and care actions |

## Clinical Abbreviations

| Abbreviation | Meaning |
|-------------|---------|
| **MDT** | Multi-Disciplinary Team (meeting) |
| **EHR** | Electronic Health Record |
| **HIS** | Hospital Information System |
| **EPD** | Elektronisch Patiëntendossier (Dutch EHR) |
| **FHIR** | Fast Healthcare Interoperability Resources (data standard) |
| **HL7** | Health Level 7 (messaging standard) |
| **ICD-10** | International Classification of Diseases |
| **SNOMED CT** | Systematized Nomenclature of Medicine (clinical terminology) |
| **LOINC** | Logical Observation Identifiers Names and Codes (lab codes) |
| **SaMD** | Software as a Medical Device |
| **MDR** | Medical Device Regulation (EU) |
| **IVDR** | In Vitro Diagnostic Regulation (EU) |
| **CE marking** | Conformité Européenne — regulatory approval mark |
| **QMS** | Quality Management System |
| **PMS** | Post-Market Surveillance |
| **GSPR** | General Safety and Performance Requirements |

## Dutch Healthcare System

| Term | Meaning |
|------|---------|
| **Huisarts** | General practitioner (GP) |
| **Ziekenhuis** | Hospital |
| **Polikliniek** | Outpatient clinic |
| **Verwijzing** | Referral (from GP to specialist) |
| **Zorgverzekeraar** | Health insurer |
| **NZa** | Nederlandse Zorgautoriteit (Dutch Healthcare Authority) |
| **IGJ** | Inspectie Gezondheidszorg en Jeugd (Healthcare Inspectorate) |
| **NHG** | Nederlands Huisartsen Genootschap (GP guidelines) |
| **NVvH** | Nederlandse Vereniging voor Heelkunde (Surgery association) |
| **ChipSoft** | Major Dutch EHR vendor (HiX system) — Delphyr integration partner |
| **InterSystems** | Healthcare IT vendor — Delphyr infrastructure partner |
| **Bricks** | Primary care platform — Delphyr integration via Tetra |

## MDR Classification (Medical Devices)

| Class | Risk | Examples | Assessment |
|-------|------|----------|-----------|
| **I** | Low | Bandages, tongue depressors | Self-declaration |
| **IIa** | Medium-low | Hearing aids, diagnostic imaging SW | Notified body |
| **IIb** | Medium-high | Ventilators, infusion pumps | Notified body |
| **III** | High | Implants, cardiac devices | Notified body + design exam |

**Delphyr is likely Class IIa** — clinical decision support software that provides information for clinical decisions but does not directly control treatment.

## Clinical AI Evaluation Terms

| Metric | What It Measures | Clinical Relevance |
|--------|------------------|-------------------|
| **Faithfulness** | Are claims supported by source docs? | Prevents hallucination |
| **Context precision** | Are retrieved chunks relevant? | Reduces noise in summaries |
| **Context recall** | Are all relevant chunks retrieved? | Prevents missed information |
| **Answer relevance** | Does the output address the query? | Ensures clinical usefulness |
| **Claim coverage** | % of claims with source citations | Verifiability requirement |
| **Safety: no-advice** | Output avoids treatment recommendations | Regulatory requirement |
| **Safety: PHI minimization** | Output avoids unnecessary identifiers | Privacy requirement |
| **Patient scope leakage** | Cross-patient data contamination | Must be 0% — safety-critical |

## RAG Architecture Terms

| Term | Meaning in Delphyr Context |
|------|---------------------------|
| **Dense retrieval** | Embedding-based semantic search (good for concept matching) |
| **Sparse retrieval** | BM25/keyword search (good for exact terms like drug names) |
| **Hybrid retrieval** | Dense + sparse combined via RRF (best for clinical data) |
| **RRF** | Reciprocal Rank Fusion — method for combining ranked lists |
| **Re-ranking** | Second-pass scoring of retrieved chunks (recency, doc type) |
| **Chunking** | Splitting documents into retrieval-sized pieces |
| **Grounding** | Connecting generated text to source documents |
| **Citation** | Explicit reference to source passage for a claim |
| **Hallucination** | Generated content not supported by any source |

---

## Delphyr-Specific Technical Terms

| Term | Meaning |
|------|---------|
| **M1** | Delphyr's 7B clinical language model (Dutch-native) |
| **M2** | Delphyr's AI Copilot — product layer on top of M1 |
| **Ambient listening** | Capturing consult audio and converting to structured notes |
| **MDT preparation** | Automated assembly of patient briefs for team meetings |
| **Guardrail pipeline** | Multi-stage safety checks (input → retrieval → generation → output) |
| **Commit/rollback** | Transactional safety pattern for agent actions |
| **Staged autonomy** | Gradually increasing AI automation as trust is earned |
| **Confidence routing** | Directing outputs to auto-complete, review, or reject based on score |
