# Audio Overview Prompt — Episode 6: Evaluation Frameworks in Medical AI

**Episode Type:** Critique  
**Duration:** 10-15 minutes  
**Target Characters:** ~4000-4500 (within NotebookLM limits)

---

## Episode Structure

### [1 min] Frame the Critique — Why Current Benchmarks Are Insufficient

Open by establishing what's wrong with how medical AI is typically evaluated:

- Most benchmarks focus on knowledge recall (USMLE, MedQA, etc.)
- These measure what the model knows, not how it behaves in real clinical workflows
- A model can pass medical exams but fail in practical clinical use
- The critique: **offline benchmarks are necessary but insufficient for medical AI safety**

Set up the core tension: How do you evaluate whether a medical AI system is safe for real-world deployment?

---

### [4 min] Limitations of Offline Benchmarks and LLM-as-a-Judge

Walk through the specific limitations:

**Knowledge vs. Behavior**
- Benchmarks test medical knowledge, not clinical behavior
- A model can correctly answer a medical question but give dangerous advice in a specific patient context
- Real clinical use involves patient-specific scoping, citation verification, and appropriate abstention
- Google Cloud's pattern: the system is for retrieving and summarizing, not diagnosing

**Static Evaluation**
- Benchmarks are point-in-time snapshots
- Don't capture how the system behaves over time, with different patients, in different contexts
- No measure of consistency, drift, or degradation

**LLM-as-a-Judge Limitations**
- AWS recommends LLM-as-a-judge approaches (pairwise comparison, single-answer grading, reference-guided grading)
- But: LLMs are biased toward their own knowledge, not the retrieved evidence
- Can be gamed by models that sound confident
- Doesn't capture real-world failure modes

**Missing the Safety Dimension**
- Standard benchmarks don't measure: prompt injection resilience, scope drift, unsupported claim detection
- Don't measure: whether the system correctly refuses when it should
- Don't measure: citation accuracy and verification
- Abridge's insight: support quality and clinical severity are different axes

**Abridge's Factuality Taxonomy**
- Directly supported, reasonable inference, questionable inference, unmentioned, contradiction
- Severity: minimal, moderate, major
- This is more nuanced than binary "hallucination" labels
- But: even this taxonomy is an offline measure—it doesn't capture real-world deployment

---

### [4 min] What Real-World Evaluation Looks Like

Present the alternative: evaluation that mirrors real clinical use:

**Scenario-Based Output Testing**
- Hippocratic AI's approach: output testing in realistic scenarios
- Not just "can the model answer this question" but "does the system behave safely in this clinical situation?"
- Test specific failure modes: prompt injection, scope creep, unsupported claims
- Test the full pipeline, not just the model

**Clinician Review**
- Abridge: clinician review required before notes enter the EHR
- Human-in-the-loop for high-risk workflows
- Not just for quality, but for safety validation
- The insight: clinicians catch failures that automated metrics miss

**Hippocratic AI's Real-World Evaluation**
- 6,234 licensed clinicians evaluating 307,038 unique calls
- Multi-step safety process: output testing, human clinical supervision, escalations, cross-validation
- Real-world error management and feedback loops
- Their public positioning: real-world evaluation is necessary for safe deployment

**AWS Component-Level Evaluation**
- Evaluate extraction separately from RAG response generation
- Extraction metrics: accuracy, completeness, adjusted recall/capture rate, precision
- RAG metrics: response relevancy, context precision, faithfulness
- The insight: "the app works" is not an evaluation plan

**Safety Monitoring After Deployment**
- Post-deployment monitoring for failure patterns
- Logging and adversarial testing loops
- Continuous improvement based on real-world feedback
- Delphyr's pattern: security, accuracy, and focus as three safety buckets

---

### [2 min] Building a Practical Evaluation Stack

Close with a practical framework for medical AI evaluation:

**Layer 1: Offline Benchmarks**
- Use them for baseline capability assessment
- Don't rely on them for safety validation
- Track over time to detect degradation

**Layer 2: Component-Level Metrics**
- Extraction quality (accuracy, completeness)
- Retrieval quality (precision, recall, ranking)
- Generation quality (faithfulness, relevance)
- AWS's approach: split evaluation by component

**Layer 3: Scenario-Based Testing**
- Test specific clinical situations, not just questions
- Include failure mode scenarios: prompt injection, scope drift, unsupported claims
- Test the full pipeline, not just the model

**Layer 4: Human Evaluation**
- Clinician review for quality and safety
- Not just for quality—specifically for safety validation
- Abridge's pattern: required clinician review before EHR entry

**Layer 5: Post-Deployment Monitoring**
- Real-time monitoring for failure patterns
- Logging for later analysis
- Continuous feedback loops

**The key insight**: A credible evaluation story combines offline benchmarks (necessary but insufficient), component-level metrics, scenario-based testing, human clinician review, and post-deployment monitoring. No single layer is enough.

---

## Optimized Prompt for NotebookLM

Copy and paste this into NotebookLM:

```
Create a 10-15 minute critique-style podcast episode exploring "Evaluation Frameworks in Medical AI."

Structure:
[1 min] Frame the critique: current benchmarks measure knowledge recall, not clinical behavior. A model can pass USMLE but fail in real clinical use. Offline benchmarks are necessary but insufficient for safety.

[4 min] Limitations: benchmarks test what the model knows, not how it behaves; static point-in-time evaluation; LLM-as-a-judge is biased toward model knowledge, not retrieved evidence; missing safety dimensions like prompt injection, scope drift, citation accuracy. Abridge's insight: support quality and clinical severity are different axes.

[4 min] What real-world evaluation looks like: Hippocratic AI's output testing (6,234 clinicians, 307k calls), scenario-based testing for failure modes, clinician review (Abridge requires it before EHR entry), AWS component-level evaluation (extraction vs RAG metrics), post-deployment monitoring. The full pipeline evaluation, not just model benchmarks.

[2 min] Building a practical evaluation stack: Layer 1 offline benchmarks (baseline), Layer 2 component metrics (extraction, retrieval, generation), Layer 3 scenario testing (failure modes), Layer 4 human clinician review (safety validation), Layer 5 post-deployment monitoring. No single layer is enough.

Tone: critical but constructive. Educational but technical. Mention Abridge (factuality taxonomy, clinician review), Hippocratic AI (real-world evaluation at scale), AWS (component-level evaluation), Google Cloud (intended-use boundaries).
```

---

## Settings Recommendation

```json
{
  "artifact_type": "audio-overview",
  "settings": {
    "duration": "long",
    "tone": "educational",
    "hosts": "auto",
    "custom_prompt": "Two hosts - one critical of benchmarks, one explaining the real-world alternative. Make it practical, not just critical."
  },
  "tips": [
    "Be critical but constructive - offer alternatives, not just complaints",
    "Use specific company examples: Hippocratic AI's 6k clinician evaluation, Abridge's clinician review requirement",
    "Emphasize the multi-layer approach - no single evaluation method is sufficient",
    "Connect to the safety implications - this is about patient harm prevention"
  ]
}
```
