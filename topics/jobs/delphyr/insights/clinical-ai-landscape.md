# Clinical AI Landscape — Industry Context for Delphyr

## The Clinical Decision Support Market

### Market Size & Growth
- Clinical Decision Support Systems (CDSS) market valued at ~$1.5-2B globally
- Growing at 12-15% CAGR driven by AI integration
- EU is the second-largest market after North America
- Netherlands is a hub for health-tech innovation (UMC Utrecht, Amsterdam UMC, Philips)

### Key Players in Clinical AI
| Company | Focus | Stage | Differentiator |
|---------|-------|-------|----------------|
| **Delphyr** | Clinical RAG + agentic workflows | Early | In-house everything, MDR-pursuing |
| **Hippocratic AI** | Clinical AI agents | Well-funded | Agent safety focus |
| **Glass Health** | Clinical decision support | Series A | Evidence-based recommendations |
| **Viz.ai** | Medical imaging AI | Growth | FDA-cleared stroke detection |
| **PathAI** | Pathology AI | Growth | Diagnostic precision |
| **Abridge** | Clinical documentation | Series C | Real-time medical capture |
| **Nuance/DAX** | Clinical documentation | Microsoft-owned | Ambient clinical intelligence |

### Delphyr's Unique Position
- **Full in-house stack** — most competitors use off-the-shelf LLMs + vector DBs
- **MDR certification pursuit** — positions as a medical device, not just "software"
- **RAG + agents for clinical workflows** — beyond chat, into actionable decision support
- **European-first** — built for EU privacy and regulatory requirements from day one

## Regulatory Landscape

### EU AI Act Impact on Clinical AI
- Clinical decision support likely classified as **High Risk** under EU AI Act
- Requirements: risk management, data governance, transparency, human oversight
- Overlap with MDR creates dual regulatory burden but also double moat

### MDR Timeline for AI/SaMD
```
Pre-market:
  ├─ Risk classification (Rule 11 for software)
  ├─ Quality Management System (ISO 13485)
  ├─ Technical documentation
  ├─ Clinical evaluation (literature review + possibly clinical investigation)
  ├─ Notified Body assessment (for Class IIa+)
  └─ CE marking

Post-market:
  ├─ Post-Market Clinical Follow-up (PMCF)
  ├─ Periodic Safety Update Reports (PSUR)
  ├─ Vigilance reporting (adverse events)
  └─ Continuous software lifecycle management (IEC 62304)
```

### IVDR vs MDR
- In Vitro Diagnostic Regulation (IVDR) applies to lab/diagnostic software
- MDR applies to clinical decision support and therapeutic software
- Delphyr likely falls under MDR (decision support for doctors)

## Technical Landscape

### RAG for Clinical Data — State of the Art

#### Embedding Models for Clinical Text
- **General purpose**: text-embedding-3-large (OpenAI), Voyage-3, Cohere embed-v3
- **Biomedical**: PubMedBERT, BioClinicalBERT, BioGPT embeddings
- **Retrieval-specific**: MedCPT (contrastive pre-trained model for medical retrieval)
- **Delphyr builds custom**: Fine-tuned embeddings on their clinical corpus (competitive advantage)

#### Clinical Knowledge Sources
1. **PubMed/MEDLINE**: 35M+ biomedical abstracts
2. **Cochrane Library**: Systematic reviews and clinical evidence
3. **NICE/WHO guidelines**: Treatment protocols and clinical pathways
4. **Drug databases**: DrugBank, RxNorm, ATC classification
5. **ICD-10/ICD-11**: Disease classification codes
6. **SNOMED CT**: Clinical terminology standard
7. **HL7 FHIR**: Healthcare data interoperability standard

#### Privacy-Preserving RAG Architectures
1. **Federated retrieval**: Query distributed across hospital systems, results aggregated centrally
2. **Differential privacy**: Add noise to embeddings/results to prevent re-identification
3. **Homomorphic encryption**: Search encrypted data without decryption (computationally expensive)
4. **On-premise deployment**: Keep everything within hospital network boundaries
5. **Pseudonymization + access control**: Most practical approach — de-identify patient data, strict role-based access

### Agent Safety in Clinical AI

#### The Core Challenge
Medical AI errors can harm patients. Unlike a wrong product recommendation, a wrong clinical suggestion could lead to:
- Missed diagnosis
- Wrong treatment
- Drug interaction
- Delayed care

#### Safety Patterns Being Adopted
1. **Guardrails**: Constitutional AI-style constraints on clinical agent outputs
2. **Retrieval grounding**: Force agents to cite specific clinical evidence, not generate from training data
3. **Confidence calibration**: Ensure model confidence correlates with actual accuracy
4. **Multi-agent verification**: Second agent reviews first agent's output
5. **Structured output validation**: Enforce schema compliance for clinical data
6. **Deterministic fallbacks**: If LLM confidence < threshold, fall back to rule-based system

## Dutch Healthcare Context

### Why Netherlands Matters for Delphyr
- Amsterdam UMC, UMC Utrecht, Erasmus MC — world-class academic hospitals
- Strong digital health infrastructure (EPD systems widely deployed)
- Progressive regulation — Netherlands often first-mover on health-tech adoption
- GDPR enforcement is pragmatic — focus on enabling innovation within boundaries

### Hospital Data Systems
- **EPD (Elektronisch Patiëntendossier)**: Electronic health record systems
  - Major vendors: Epic, ChipSoft (HiX), Cerner
- **PACS**: Picture Archiving for medical imaging
- **LIS**: Laboratory Information Systems
- **RIS**: Radiology Information Systems

### Integration Challenges
- Each hospital has its own EPD vendor and configuration
- HL7 v2/FHIR interoperability is improving but not universal
- Data extraction often requires custom integration per hospital
- Clinical data is semi-structured at best (free text, structured fields, imaging)

## Key Trends to Watch

1. **EU AI Act enforcement** (2025-2026) — new compliance requirements for clinical AI
2. **MDR enforcement tightening** — transition period ending, enforcement increasing
3. **Multimodal clinical AI** — combining text, imaging, genomics in RAG
4. **Clinical LLM benchmarks** — MedQA, PubMedQA, clinical trial matching
5. **Federated learning for clinical models** — training across hospitals without sharing data
6. **Agent-based clinical workflows** — moving from chatbot to autonomous task completion

## Interview Preparation: Clinical Domain Vocabulary

### Common Clinical Abbreviations
| Abbreviation | Meaning |
|--------------|---------|
| MDT | Multi-Disciplinary Team |
| EHR/EPD | Electronic Health Record |
| CDSS | Clinical Decision Support System |
| SaMD | Software as a Medical Device |
| PMCF | Post-Market Clinical Follow-up |
| DDI | Drug-Drug Interaction |
| CDS | Clinical Decision Support |
| FHIR | Fast Healthcare Interoperability Resources |
| SNOMED | Systematized Nomenclature of Medicine |
| ICD | International Classification of Diseases |
| CPT | Current Procedural Terminology |
| ADR | Adverse Drug Reaction |
| NLP/NLU | Natural Language Processing/Understanding |
