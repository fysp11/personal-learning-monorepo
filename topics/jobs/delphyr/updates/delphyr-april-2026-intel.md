# Delphyr Intelligence Update — April 2026

## Fresh Information (Web Research, April 8, 2026)

### Funding Round Details

- **Amount:** €1.75M
- **Announced:** March 2026
- **Investors:** Founders of Hugging Face and DEGIRO
- **Coverage:** EU-Startups, Fintech Global, The AI Journal, PR Newswire, Beinsure
- This is a seed/pre-Series A round — small but strategic (Hugging Face founder backing signals model credibility)

### Product Positioning Shift

Public messaging has evolved toward **"AI agents for clinicians"** (not just "AI copilot"):
- "Scale AI agents for clinicians" language in funding coverage
- "Agentic AI" terminology appearing in March 2026 materials
- This aligns with the broader 2026 trend of agentic framing

### M1 Model Status

- 7B parameters, Dutch-native clinical language model
- Deployed at **Reinier de Graaf Hospital** (confirmed production deployment)
- Benchmarks: PubMedQA 76.8%, MedMCQA 62.5%, MedQA 64.7%
- Positioned as "first Dutch-built clinical language model"
- Capabilities beyond summarization: MDT prep, ward rounds, patient handovers, discharge letters

### M2 Model

- **M2 is the AI Copilot** — the product-facing model (M1 is the underlying language model)
- M2 helps doctors "reduce administrative burden, streamline clinical tasks, and focus more on patient care"
- Integrated directly into EHR systems

### Current Deployments and Partners

- **Reinier de Graaf Hospital** — live deployment
- **Erasmus MC** — pilot
- **Dutch Endometriosis Center** — pilot
- **Integration partners:** ChipSoft, InterSystems, Bricks (via Tetra)

### Compliance and Regulatory

- GDPR compliant
- ISO 27001
- SOC2
- Applied for MDR medical device classification
- EU AI Act compliance stated
- All patient data processed within European infrastructure

### Team

No new team member announcements detected. Still appears to be a small core team (~6-8 people).

---

## What This Means for Interview Preparation

### Reinforced Angles

1. **Agentic framing is now public** — can reference "AI agents for clinicians" language without inferring
2. **Production deployment confirmed** — Reinier de Graaf is real, not just a pilot
3. **MDT preparation is an explicit capability** — validates the MDT agent design document
4. **Small team + ambitious scope** = high ownership, exactly the working style to emphasize

### New Angles

1. **M1 → M2 architecture** — understanding the separation between the base model (M1) and the product layer (M2) is a good technical question to ask
2. **Hugging Face investor connection** — could ask about model training infrastructure, fine-tuning pipeline, and relationship with HF ecosystem
3. **Multi-hospital deployment** — scaling from single hospital to multiple introduces new challenges (data isolation, model generalization, deployment automation)

### Questions to Ask in Next Round

- "How does M2 relate to M1 architecturally? Is M2 a fine-tuned version, a prompt layer, or a separate model?"
- "With Reinier de Graaf in production and Erasmus as a pilot, what's the deployment model for adding new hospitals?"
- "How does the Hugging Face connection influence your model development pipeline?"
- "What's the next major capability after MDT preparation and ambient listening?"

---

## Sources

- [EU-Startups: Delphyr raises €1.75M](https://www.eu-startups.com/2026/03/amsterdam-based-delphy-raises-e1-75-million-to-reduce-healthcare-administrative-workloads-with-ai)
- [Fintech Global: Dutch health AI startup Delphyr raises €1.75m](https://fintech.global/2026/03/11/dutch-health-ai-startup-delphyr-raises-e1-75m/)
- [PR Newswire: Delphyr funding announcement](https://www.prnewswire.com/news-releases/delphyr-raises-1-75-million-to-give-healthcare-professionals-time-back-with-ai-302700171.html)
- [Delphyr M1 blog post](https://www.delphyr.ai/blog/delphyr-m1-best-in-class-medical-model)
- [Beinsure: Delphyr raises €1.75mn](https://beinsure.com/news/delphyr-raises-e1-75-mn-to-scale-ai-agents-for-clinicians/)
