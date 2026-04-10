# EU AI Act — Regulatory Awareness for Interview Prep

Saved: 2026-04-07

## Purpose

Both Finom and Delphyr operate under EU AI Act requirements. Finom's accounting page says "AI Act-ready." Delphyr is pursuing medical device classification. Understanding the regulatory landscape strengthens interview credibility in both contexts without overclaiming legal expertise.

---

## EU AI Act Timeline

- **February 2025**: Prohibited AI practices enforceable
- **August 2026**: High-risk AI system obligations fully enforceable
- **August 2027**: Full enforcement across all categories

**Key implication:** Companies building AI systems in the EU right now are preparing for August 2026 compliance. This is an active engineering concern, not a future one.

---

## Risk Tiers

The AI Act classifies systems into four risk levels:

| Tier | Examples | Requirements |
|------|----------|-------------|
| Unacceptable | Social scoring, real-time mass biometric surveillance | Prohibited |
| High-risk | Credit scoring, medical devices, employment decisions | Conformity assessment, CE marking, human oversight, auditability, monitoring |
| Limited risk | Chatbots, deepfakes | Transparency obligations |
| Minimal risk | Spam filters, AI-powered games | No specific requirements |

---

## Finom Implications

### Is Finom's AI high-risk under the AI Act?

**Probably not for core accounting automation**, but it depends on the specific use case:

- **Credit scoring / loan decisions**: Explicitly listed as high-risk in Annex III
- **Fraud detection**: Explicitly excluded from high-risk classification
- **Accounting automation** (categorization, reconciliation, tax prep): Not explicitly listed as high-risk — likely falls under limited or minimal risk
- **Automated financial decisions affecting users**: Could be high-risk if the system makes autonomous decisions that significantly affect users' financial standing

### What "AI Act-ready" likely means for Finom

- Transparency: Users know when they're interacting with AI
- Human oversight: Approval gates before consequential actions (filing taxes, making payments)
- Auditability: Decision trails for AI-driven financial operations
- Risk management: Documented risk assessment for each AI capability
- Data quality: Training and evaluation data quality standards

### Interview talking point for Finom

> "AI Act readiness in fintech likely means the engineering bar is higher for transparency, auditability, and human oversight. The good news is that these are the same things that make AI systems production-ready anyway — approval gates, decision logging, evaluation, and staged rollout. Compliance and reliability are aligned here."

---

## Delphyr Implications

### Is Delphyr's AI high-risk under the AI Act?

**Almost certainly yes.** The AI Act classifies medical device AI as high-risk if:
- The AI is a safety component of a medical device, OR
- The AI is a medical device itself, AND
- It requires third-party conformity assessment by a notified body

Delphyr is pursuing medical device classification. Their AI agents process patient data and provide clinical information to healthcare professionals. Under MDR:
- **Class IIa, IIb, III** medical devices with AI → high-risk under AI Act
- **Class I** medical devices with ML → not high-risk under AI Act

Delphyr's clinical decision support tools likely fall into at least Class IIa, making them high-risk.

### What high-risk compliance requires (relevant to engineering)

1. **Risk management system**: Documented, continuous risk identification and mitigation
2. **Data governance**: Training data quality, relevance, representativeness, and freedom from bias
3. **Technical documentation**: Full system description, design choices, evaluation results
4. **Record-keeping / logging**: Automatic captured material of events for traceability
5. **Transparency**: Clear information to users about the system's capabilities and limitations
6. **Human oversight**: Designed to be overseen by humans, with ability to override or stop
7. **Accuracy, robustness, cybersecurity**: Appropriate levels for the intended purpose
8. **Post-market monitoring**: Ongoing monitoring of performance in the real world

### The MDR + AI Act overlap

The AI Act allows companies to integrate AI-specific requirements into existing MDR documentation and processes. This means Delphyr doesn't need two separate compliance tracks — they can extend their MDR quality management system to cover AI Act requirements.

### Interview talking point for Delphyr

> "For medical AI under the AI Act, the high-risk requirements — risk management, data governance, transparency, human oversight, and post-market monitoring — map directly to the engineering practices I'd build anyway: evaluation frameworks, audit trails, confidence thresholds, human review routing, and production monitoring. The regulatory requirement and the engineering best practice are the same thing."

---

## Shared Engineering Patterns That Satisfy Both Regulatory Contexts

| Requirement | Engineering implementation | Finom context | Delphyr context |
|-------------|--------------------------|---------------|-----------------|
| Human oversight | Approval gates, escalation routing | Tax filing approval flows | Clinical review before action |
| Transparency | Decision explanation, confidence display | "Why this category?" | Citation-backed responses |
| Auditability | Structured logging, decision traces | Financial audit trail | Clinical audit trail |
| Risk management | Evaluation framework, failure taxonomy | Workflow-level quality metrics | Clinical safety metrics |
| Data quality | Training data curation, bias checks | Financial document datasets | Clinical note datasets |
| Post-market monitoring | Production metrics, drift detection | Override rates, error rates | Clinician feedback loops |
| Record-keeping | Correlation IDs, event logging | Transaction-to-decision trace | Patient query trace |

---

## What NOT to Say in Interviews

- Don't claim regulatory expertise — you're an engineer, not a compliance lawyer
- Don't use regulatory requirements as a reason to slow things down — frame them as aligned with good engineering
- Don't assume you know the specific compliance path — ask about their approach
- Don't conflate AI Act with GDPR — they're separate regimes (though they interact)

## What TO Say

- "I see regulatory requirements as engineering requirements — they align with the reliability and transparency I'd build anyway"
- "Human oversight, auditability, and evaluation are both regulatory requirements and engineering best practices"
- "I'd want to understand your compliance roadmap so the systems I build are aligned from the start, not retrofitted later"

Sources:
- [EU AI Act high-risk compliance countdown](https://ai2.work/economics/eu-ai-act-high-risk-rules-hit-august-2026-your-compliance-countdown/)
- [AI Act guidelines for medical device manufacturers](https://quickbirdmedical.com/en/ai-act-medical-devices-mdr/)
- [EU AI Act impact on financial services](https://www.consultancy.eu/news/11237/the-eu-ai-act-the-impact-on-financial-services-institutions)
- [EBA: AI Act implications for banking sector](https://www.eba.europa.eu/sites/default/files/2025-11/d8b999ce-a1d9-4964-9606-971bbc2aaf89/AI%20Act%20implications%20for%20the%20EU%20banking%20sector.pdf)
