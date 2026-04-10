# Cross-Company Insight: AI Adoption as an Engineering Discipline

Saved: 2026-04-10

## Purpose

Both Finom and Delphyr need AI that gets adopted by the people who matter — accountants and product teams at Finom, clinicians and hospital staff at Delphyr. Ivo explicitly described "adoption" as a dedicated workstream at Finom with its own owner, internal workshops, and practical AI-tool rollout. This document captures the transferable engineering patterns behind successful AI adoption, drawn from both interview preparation contexts and current industry trends.

---

## The Core Insight: Adoption Is a Product, Not a Memo

The 2026 industry pattern is clear: organizations that treat AI adoption as a product problem — with its own UX, metrics, and iteration cycles — succeed. Those that treat it as a rollout announcement fail.

**Ivo's framing at Finom:** Adoption has a dedicated owner. There are internal workshops. AI-tool usage is spread across teams through practical enablement, not mandates.

**Delphyr's context:** Clinical adoption is even harder — clinicians are time-poor, skeptical of tools that add steps, and will abandon anything that doesn't demonstrably save time within the first interaction.

---

## Pattern 1: The Adoption Funnel (Shared Shape)

Both companies face the same adoption funnel, just with different users:

```
Awareness  → "This exists and might help me"
Trial      → "I tried it on a real task"
Habit      → "I use it without thinking about it"
Trust      → "I rely on it and would notice if it broke"
Advocacy   → "I tell colleagues to use it"
```

### Finom Instantiation

| Stage | What it looks like | Engineering lever |
|-------|-------------------|-------------------|
| Awareness | Product team knows the central AI pattern exists | Internal catalog, discovery UX |
| Trial | Team tries the transaction categorization pipeline on their domain | Self-serve onboarding, sandbox data |
| Habit | Team uses AI-assisted categorization in daily workflow | Defaults that work, not opt-in features |
| Trust | Team relies on auto-booking for high-confidence transactions | Calibration curves, transparent accuracy metrics |
| Advocacy | Team suggests new AI capabilities for their domain | Feedback channels, visible roadmap |

### Delphyr Instantiation

| Stage | What it looks like | Engineering lever |
|-------|-------------------|-------------------|
| Awareness | Clinician sees the tool in their HIS/EHR sidebar | Integration placement, contextual activation |
| Trial | Clinician uses patient summary for one MDT case | Zero-friction first use, pre-loaded context |
| Habit | Clinician opens AI summary as default MDT prep step | Speed (faster than manual), quality (catches things they missed) |
| Trust | Clinician uses AI briefing as primary source, reviews highlights | Citation quality, consistent accuracy over weeks |
| Advocacy | Clinician recommends to colleagues, requests new features | Visible improvement in their workflow metrics |

---

## Pattern 2: The Adoption Failure Modes

Both companies can fail at adoption in the same ways:

### Failure Mode 1: The "Too Much Setup" Trap

If the AI feature requires more than 30 seconds of configuration before delivering value, most users will never try it.

- **Finom fix:** Pre-configure categorization rules based on the user's industry and country. The system should work on day one.
- **Delphyr fix:** Auto-detect the patient context from where the clinician navigated. Never ask "which patient?" if the HIS already knows.

### Failure Mode 2: The "Black Box" Rejection

Users who don't understand why the AI made a decision won't trust it, especially in high-stakes domains.

- **Finom fix:** Show the reasoning chain: "Categorized as Bürobedarf (SKR03 4930) because merchant 'Büro Discount' matched office supplies pattern. Confidence: 92%."
- **Delphyr fix:** Every claim cites its source. Every recommendation shows which guideline it matched. No unsupported assertions.

### Failure Mode 3: The "Extra Work" Backlash

If the AI creates review work without reducing other work, it's a net negative.

- **Finom fix:** Only surface items that need attention. High-confidence items should auto-complete silently. The user's inbox should shrink, not grow.
- **Delphyr fix:** The MDT briefing should replace manual prep, not supplement it. If clinicians still do the old prep plus review the AI output, adoption will collapse.

### Failure Mode 4: The "Accuracy Cliff" Erosion

If accuracy degrades and users notice before the system does, trust is permanently damaged.

- **Finom fix:** Continuous calibration monitoring. Alert engineering before users notice drift.
- **Delphyr fix:** Golden-set regression tests on every model update. Clinician feedback loops that catch degradation early.

---

## Pattern 3: Adoption Metrics That Matter

### What NOT to measure

- Login counts (vanity)
- Feature activation rates (surface-level)
- "NPS for AI features" (lagging, unreliable)

### What TO measure

| Metric | Finom meaning | Delphyr meaning |
|--------|--------------|-----------------|
| **Time to first value** | How long from account creation to first auto-categorized transaction | How long from tool activation to first useful patient summary |
| **Override rate** | How often users correct AI categorizations | How often clinicians edit AI-generated summaries |
| **Silent acceptance rate** | How often users accept without checking | Dangerous if accuracy isn't validated — need to distinguish trust from neglect |
| **Workflow compression** | Reduction in time-per-transaction or manual steps-per-month | Reduction in MDT prep time or clicks-per-patient |
| **Return rate** | Do users come back after first use? | Do clinicians use it for the second MDT meeting? |
| **Escalation volume** | How many items end up in the review queue vs auto-completed | How many AI outputs need clinician correction vs used as-is |

### The Critical Metric: Earned Autonomy Rate

Both companies should track the percentage of decisions where the system operates autonomously (no human review) while maintaining acceptable accuracy. This is the purest measure of adoption success.

```
Earned Autonomy Rate = (Auto-completed decisions with acceptable quality) / (Total decisions)
```

Finom target: 80%+ of standard domestic transactions auto-booked correctly.
Delphyr target: 70%+ of clinical summaries used without substantive edits.

---

## Pattern 4: The Central AI Team's Role in Adoption

### What Ivo Described

- Adoption has a **dedicated owner** (not a side project)
- Internal **workshops** to teach teams how to use AI tools
- Explicit work to spread AI-first behavior across the company

### What This Means Architecturally

The central AI team doesn't just build capabilities — it builds **adoption infrastructure**:

1. **Pattern library:** Proven workflow templates that teams can adopt in < 1 day
2. **Observability by default:** Every AI-powered workflow ships with metrics that show whether it's working
3. **Escape hatches:** Easy fallback to manual mode if the AI breaks — reduces adoption risk
4. **Success stories:** Internal case studies showing time saved, errors reduced, throughput gained
5. **Feedback channels:** Structured way for domain teams to report issues and request improvements

### Interview-Ready Framing

> "I think about adoption as a product surface, not a rollout event. The central AI team's job is to make the reusable path faster and more trustworthy than the local workaround. That means good defaults, observability built in, one-click escape hatches, and proving value with metrics instead of mandates."

---

## Pattern 5: Industry Context (2026)

Current industry trends reinforce these patterns:

- **Senior engineers are shifting from writing syntax to orchestrating and reviewing AI agents.** The adoption challenge is helping this transition happen without losing engineering rigor.
- **Organizations that segment adoption data by team and function** (not just company-wide averages) are identifying pockets of success and failure faster.
- **Human-in-the-loop workflows are re-emerging** as a practical response to the volume of AI-generated code and decisions. The key is making the human loop efficient, not eliminating it.
- **The defining advantage in 2026 is not access to AI, but the ability to deploy it with intent.** Strategy and data discipline determine outcomes.

---

## Practical Application

### For Finom Interview 3

If asked about adoption:

> "Adoption is an engineering problem, not a communication problem. I'd focus on three things: making the first use require zero setup, making the ongoing use save measurable time, and making the fallback path painless so teams adopt without fear of being locked in."

### For Delphyr Follow-Up

If asked about clinical adoption:

> "Clinical adoption has a harder trust bar than most domains. The system needs to prove itself on the clinician's terms — faster prep, better coverage, verifiable sources — within the first interaction. If the second use doesn't happen, the feature is dead."

---

## Sources

- [Insight Partners: Patterns shaping AI adoption in 2026](https://www.insightpartners.com/ideas/ai-adoption-2026/)
- [Swarmia: Staged approach to AI adoption for engineering teams](https://www.swarmia.com/blog/staged-approach-AI-adoption-for-engineering/)
- [ShiftMag: Many engineering leaders are getting AI adoption wrong](https://shiftmag.dev/ai-is-changing-development-8791/)
- [Grant Thornton: 6 AI adoption strategies that stick](https://www.grantthornton.com/insights/articles/advisory/2026/ai-adoption-strategies-that-stick)
