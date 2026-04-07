# Cross-Company Insights: Finom x Delphyr

Saved: 2026-04-07

## Purpose

This note captures transferable patterns and insights between the Finom and Delphyr interview preparations. Both roles involve production AI systems in correctness-sensitive domains, but with different domain constraints and team shapes.

---

## Shared Themes

### 1. Correctness Over Demo Quality

Both companies operate in domains where "mostly right" is not enough:
- **Finom:** Financial operations — wrong tax records, incorrect reconciliation, missed compliance items
- **Delphyr:** Clinical systems — wrong citations, missed diagnoses, hallucinated medical facts

**Transferable insight:** The evaluation and quality discipline is the same. Component-level accuracy is necessary but not sufficient. End-to-end workflow correctness is what matters. Both need confidence-based routing, human review for edge cases, and audit trails.

### 2. Staged Automation / Earned Autonomy

Both roles reward someone who understands that full automation is earned, not declared:
- **Finom:** Shadow mode → draft-only → approval-gated → selective automation
- **Delphyr:** Retrieve-only → summarize-with-citations → assist-with-review → guided-decision-support

**Transferable insight:** The rollout maturity model is the same shape. Start with the system showing its work, then gradually increase autonomy as trust is earned through measured quality.

### 3. Document-Heavy Operations

Both involve AI operating over messy, real-world documents:
- **Finom:** Invoices, receipts, tax artifacts, bank statements
- **Delphyr:** Clinical notes, lab results, correspondence, imaging reports

**Transferable insight:** The extraction pipeline architecture is structurally similar — intake → normalize → classify → extract → enrich → route. The domain specifics differ (financial entity types vs clinical entity types) but the engineering patterns are shared.

### 4. Evaluation As Core Capability

Both roles value evaluation discipline as a differentiator:
- **Finom:** Offline evals + workflow metrics + failure review
- **Delphyr:** Golden set evaluation + adversarial testing + clinician feedback loops

**Transferable insight:** Three-layer evaluation (offline, online, review) is the pattern. The existing Delphyr code demonstrates this concretely with custom scorers grouped by concern (extraction, support, safety, workflow).

### 5. Integration Into Existing Systems

Neither company wants a standalone AI product:
- **Finom:** AI embedded in the banking/invoicing/accounting platform
- **Delphyr:** AI embedded in existing HIS/EHR systems (ChipSoft, Bricks, InterSystems)

**Transferable insight:** The candidate needs to show they understand integration constraints — the AI system must fit into existing user workflows, not demand new ones.

---

## Contrasting Themes

### Team Shape

- **Finom:** 500+ employees, multiple product squads, central AI team as a cross-cutting function. The org design question (central vs embedded) is a major interview topic.
- **Delphyr:** Small startup team (~6 core). High ownership per person. No org-design complexity — everyone works on everything.

**Implication:** With Finom, emphasize org judgment and reusable capability design. With Delphyr, emphasize hands-on execution, small-team collaboration, and end-to-end ownership.

### Regulatory Pressure

- **Finom:** Fintech regulation (banking licenses, compliance, audit requirements) but AI itself is less regulated
- **Delphyr:** Medical device regulation (MDR), medical device classification, GDPR for health data, EU AI Act implications

**Implication:** With Delphyr, regulatory awareness is a core requirement. With Finom, it's more about operational correctness and business risk than regulatory certification.

### Model Strategy

- **Finom:** Likely uses external models (the posting mentions PyTorch/HF but the role leans application-layer)
- **Delphyr:** Built an in-house model (M1, 7B parameters, Dutch-native) — fine-tuning and model ownership are real

**Implication:** With Delphyr, deeper ML/model questions are more likely. With Finom, the focus is more on orchestration and workflow design around external models.

### Data Sensitivity

- **Finom:** Financial data — sensitive but not health-data-level
- **Delphyr:** Patient health data — highest sensitivity tier, strict GDPR health provisions, EU data residency requirements

**Implication:** With Delphyr, data handling architecture is a first-class concern. With Finom, it matters but the constraint is less extreme.

---

## What Prepares For One Also Prepares For The Other

| Prep area | Finom value | Delphyr value |
|-----------|-------------|---------------|
| Evaluation frameworks | Central AI quality bar | Clinical reliability assurance |
| Confidence-based routing | Accounting approval flows | Clinical escalation logic |
| Citation/grounding | Financial document traceability | Medical citation verification |
| Staged rollout | Automation maturity in finance | Trust building in clinical workflows |
| Guardrail architecture | Operational safety in finance | Patient safety in healthcare |
| Multi-stage pipeline design | Document processing at scale | Clinical data consolidation |
| Observability | Cross-team quality monitoring | Clinical reliability monitoring |

---

## Career-Level Insight

Both opportunities point to the same career thesis:

**Production AI systems in correctness-sensitive domains require a specific engineering profile:** someone who understands that the model is a component, the workflow is the product, and trust is earned through evaluation, transparency, and staged autonomy.

This profile is rarer than "I can build agents" or "I know RAG." The prep work for both Finom and Delphyr strengthens the same core capability set, regardless of which opportunity advances.

---

## Practical Reuse

### From Delphyr prep → Finom interview

- The guardrail architecture design maps directly to financial workflow safety
- The evaluation scorer patterns translate to accounting quality metrics
- The citation verification concept applies to financial document traceability
- "Intended use boundaries" framing translates to "automation scope" in finance

### From Finom prep → Delphyr follow-up

- The central-vs-embedded AI thinking applies if Delphyr grows beyond the founding team
- The competitive landscape analysis pattern could be applied to Delphyr's healthcare AI competitors
- The story bank format could be replicated for Delphyr-specific narratives
- The "first 90 days" framework applies to any role

---

## Next Steps

1. **After the Finom Ivo interview (April 8):** Capture outcome, assess whether the central AI framing landed
2. **After Delphyr outcome is known:** Record what happened, identify what transferred
3. **Regardless of outcomes:** Continue building the evaluation and guardrail code examples — they are portfolio pieces that work for any correctness-sensitive AI role
