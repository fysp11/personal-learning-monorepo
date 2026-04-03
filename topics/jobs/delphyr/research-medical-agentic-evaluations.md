# Research Report: Medical Agentic Evaluations

## Executive Summary

The phrase **"medical agentic evaluations"** is **not a standardized term** in the healthcare AI literature. However, the underlying concept—evaluating AI agents in clinical workflows—is well-supported by recent research. The field uses terms like "agent-based medical AI evaluation," "multi-agent evaluation loops," or "end-to-end clinical workflow evaluation."

---

## Authoritative Sources (6)

### 1. Nature - "AI agent in healthcare: applications, evaluations, and future directions" (2026)
**Direct Support: HIGH**

- **Source**: Zhao et al., Nature (s44387-026-00076-4)
- **Relevance**: Comprehensive review specifically addressing AI agent evaluation in healthcare
- **Key Contribution**: Proposes a **multi-dimensional evaluation framework** with two tiers:
  - **Basic indicators**: Objective correctness (accuracy, F1, ROC-AUC), semantic correctness (BLEU, BERTScore), task completion rates
  - **Development indicators**: Efficiency (response time, interaction rounds), content quality (readability, safety, ethical compliance), humanistic care (empathy, patient satisfaction)
- **Agentic Angle**: Explicitly evaluates agents on "task completion" which includes "autonomously select, invoke, and coordinate external tools to achieve a given objective, reflecting the agent's procedural reasoning and execution capability"
- **Mapping**: Directly supports workflow-level evaluation of agentic systems

---

### 2. Microsoft Healthcare AI Model Evaluator (2025)
**Direct Support: HIGH**

- **Source**: Microsoft Tech Community / GitHub (github.com/microsoft/Healthcare-AI-Model-Evaluator)
- **Relevance**: First-party platform guidance for healthcare AI evaluation
- **Key Contribution**: 
  - Open-source framework for "healthcare agent orchestrator" evaluation
  - Supports "chaining multiple AI models and tools to complete complex clinical tasks"
  - **Human-in-the-loop evaluation** with role-based access control
  - Customizable clinical task framework with "task-specific metrics"
- **Agentic Angle**: Explicitly designed for "intelligent, auditable workflows that reflect the complexities of clinical practice"
- **Mapping**: Directly addresses evaluation of multi-step, orchestrated agent workflows

---

### 3. arXiv - "Improving the Safety and Trustworthiness of Medical AI via Multi-Agent Evaluation Loops" (2026)
**Direct Support: HIGH**

- **Source**: Ghafoor et al., arXiv:2601.13268
- **Relevance**: Academic research on multi-agent evaluation specifically
- **Key Contribution**:
  - **Deterministic multi-agent evaluation loop** combining generative models with evaluator agents
  - Uses AMA Principles of Medical Ethics + 5-tier Safety Risk Assessment (SRA-5)
  - Achieved 89% reduction in ethical violations, 92% risk downgrade rate
  - Inference-time refinement without model retraining
- **Agentic Angle**: Explicitly tests "iterative multi-agent loop" for safety verification
- **Mapping**: Direct evidence for agentic evaluation loops in medical AI

---

### 4. AgentClinic - Multimodal Agent Benchmark (2024/2025)
**Direct Support: HIGH**

- **Source**: Schmidgall et al., arXiv:2405.07960 / agentclinic.github.io
- **Relevance**: First dedicated benchmark for clinical AI agents
- **Key Contribution**:
  - Evaluates LLMs as agents in **simulated clinical environments**
  - Tests "multimodal data collection under incomplete information" and "usage of various tools"
  - Covers 9 medical specialties, 7 languages
  - Finds diagnostic accuracy drops to "below a tenth of original accuracy" in sequential decision-making vs static QA
- **Agentic Angle**: Explicitly designed for "agent" evaluation, not just model accuracy
- **Mapping**: Direct support for scenario-based, interactive agent evaluation

---

### 5. Doctorina MedBench - End-to-End Evaluation of Agent-Based Medical AI (2026)
**Direct Support: HIGH**

- **Source**: Kozlova et al., arXiv:2603.25821
- **Relevance**: Comprehensive evaluation framework for AI physician agents
- **Key Contribution**:
  - **D.O.T.S. metric**: Diagnosis, Observations/Investigations, Treatment, Step Count
  - Simulates realistic physician-patient interactions (not static QA)
  - Multi-level testing: Trap-based (L1), Category sampling (L2), Full regression (L3)
  - Real-time monitoring with "anomaly detection" and "hierarchical escalation"
- **Agentic Angle**: Explicitly evaluates "agent-based medical AI" with workflow efficiency metrics
- **Mapping**: Direct support for end-to-end workflow evaluation

---

### 6. NEJM AI - "Gauging Health Care's Readiness for Agentic AI Innovation" (2025)
**Direct Support: MEDIUM (adjacent)**

- **Source**: NEJM AI (ai.nejm.org/doi/full/10.1056/AI-S2501336)
- **Relevance**: Premier medical journal addressing "agentic AI" specifically
- **Key Contribution** (from search snippets):
  - Outlines "foundational steps health systems must take to bridge this gap"
  - Addresses readiness assessment for "agentic AI transformation"
- **Agentic Angle**: Uses the term "agentic AI" explicitly
- **Mapping**: Adjacent support—focuses on readiness, not evaluation methodology

---

## Terminology Assessment

| Phrase | Usage in Literature | Recommendation |
|--------|---------------------|----------------|
| "Medical agentic evaluations" | **Not found** as standard phrase | Avoid as primary term |
| "Agent-based medical AI evaluation" | Used in Doctorina MedBench | ✅ Preferred |
| "Multi-agent evaluation loops" | Used in Ghafoor et al. | ✅ Preferred |
| "End-to-end clinical workflow evaluation" | Used in Microsoft, Nature | ✅ Preferred |
| "Agentic AI" (alone) | Used in NEJM AI, Deloitte | ✅ Acceptable |

**Recommendation**: The concept is valid and well-supported, but the exact phrasing "medical agentic evaluations" should be refined to align with established terminology.

---

## Suggested Framing Alternatives

1. **"End-to-End Clinical AI Evaluation"** - Emphasizes workflow completeness (Microsoft, Nature)
2. **"Multi-Agent Medical AI Assessment"** - Emphasizes agent orchestration (Ghafoor et al.)
3. **"Agent-Based Clinical Workflow Evaluation"** - Emphasizes scenario-based testing (Doctorina)
4. **"Interactive Clinical Agent Benchmarking"** - Emphasizes simulation approach (AgentClinic)

---

## Key Evaluation Patterns Identified

1. **Sequential Decision-Making**: Static QA insufficient; must test multi-step interactions
2. **Tool Use & Orchestration**: Evaluating agent's ability to coordinate multiple tools/models
3. **Human-in-the-Loop**: Expert clinical judgment integrated into evaluation pipeline
4. **Scenario-Based Testing**: Simulated clinical environments vs. real patient data
5. **Safety-First Metrics**: Risk grading, ethical compliance, critical condition overrides
6. **Continuous Monitoring**: Real-time quality assurance with anomaly detection

---

## Conclusion

**Verdict**: The concept of evaluating agentic/workflow-level medical AI systems is **strongly supported** by 5+ authoritative sources from 2024-2026. However, the exact phrase "medical agentic evaluations" is not standard. 

**Recommendation for slide design**: Use **"End-to-End Clinical AI Evaluation"** or **"Agent-Based Medical AI Assessment"** as the primary framing, with "agentic" as a supporting descriptor if needed.

---

*Report compiled: April 3, 2026*
*Sources: Nature, Microsoft, NEJM AI, arXiv (3 papers)*
