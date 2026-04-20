# Interview 3 — Hostile Follow-Up Question Bank

Saved: 2026-04-11

## Purpose

The existing interview simulation targets Interview 2 signals. This document covers **Interview 3-specific hostile follow-ups** — the hard questions a lead AI engineer would ask to test depth beyond prepared answers. These are the questions that separate "read about it" from "built it."

---

## Category 1: Confidence Routing (Depth Probe)

### Q: "You keep mentioning confidence thresholds. How do you know 0.85 is the right number?"

**Target answer:**
> "You don't — not a priori. The threshold comes from calibration data. You measure: of all predictions where the model said 0.85+, what percentage were actually correct? If the answer is 82%, your threshold is too low. If it's 95%, you have room to relax it. The concrete metric is ECE — Expected Calibration Error. Below 0.05 means the scores are trustworthy enough for threshold-based routing."

**Hostile follow-up:** "What if you don't have calibration data yet — it's a new market?"

> "Then you start at maximum conservatism — nothing auto-books. You collect the first 500-1000 human-reviewed transactions, fit a calibration curve, and only then set thresholds. The earned autonomy ratchet: Level 0 is 100% human review, Level 1 is conservative auto-booking after calibration is verified."

### Q: "What happens when your confidence is well-calibrated but the accuracy is just low?"

> "Then you have a model quality problem, not a calibration problem. A perfectly calibrated model that says '40% sure' and is right 40% of the time is honest but useless for auto-booking. The fix is upstream: better features, more training data, or different model architecture. Calibration only fixes the mapping from raw scores to probabilities — it can't fix the underlying prediction quality."

---

## Category 2: AI vs Deterministic Boundaries

### Q: "Why not let the LLM calculate VAT too? It would be simpler."

**Target answer:**
> "Because VAT is law, not judgment. The standard rate in Germany is 19%, the reduced rate is 7% — that's not a prediction, it's a lookup. When you let an LLM calculate tax, you've made your compliance-critical path probabilistic. If the model hallucinates 18% instead of 19% on 10,000 transactions, you have a tax audit problem. The boundary is: AI decides *what* the transaction is (category), deterministic code decides *how* it's taxed."

**Hostile follow-up:** "But what about edge cases — reduced rate items, reverse charge?"

> "Those are still rules, just more complex ones. 'Food is 7%' is a rule. 'B2B intra-EU with valid VAT ID uses reverse charge' is a rule. The complexity is in the rule graph, not in the prediction. You can have a complex deterministic rule engine without any AI — and you should, because when the tax authority asks 'why did you apply 7%?', you need to point to a rule, not a probability."

### Q: "Where does the AI boundary get blurry?"

> "In the category-to-tax-treatment mapping. Is a 'business lunch' entertainment (fully deductible) or restaurant (partially deductible)? That's where the AI judgment meets the tax rule, and the answer can differ by country. The clean design: AI outputs a category with confidence, a deterministic mapper converts category to tax treatment, and the mapper has explicit edge-case rules for ambiguous categories."


## Category 3: Live Coding Pressure

### Q: "You've been using Claude Code for 10 minutes and haven't written any tests. Why?"

**Target answer:**
> "Fair point. In a 60-minute exercise, I'd normally write the type contracts first, implement the core pipeline, and then add at least one happy-path test and one edge-case test. Let me add those now — the most valuable test is the confidence router: verify that a 0.3 confidence routes to 'reject', 0.6 routes to 'review', and 0.9 routes to 'auto_book'."

**Why this works:** Acknowledges the gap without being defensive, then immediately demonstrates you know which test is most valuable.

### Q: "Your agent just generated 50 lines of code. Did you actually read it?"

> "Let me walk through it. [Read the actual code aloud, pointing out: the type contract matches what we discussed, the confidence threshold is parameterized, the trace capture looks correct. One thing I'd change: the error handling here is too generic — a parse error and a timeout should route differently.]"

**Why this works:** Proves you're not blindly accepting agent output. The correction shows you're actively reviewing.

### Q: "This solution only works for Germany. How would you extend it to France in 20 minutes?"

> "The key insight is that market config should be data, not code. Let me show you — I'll add a MARKET_CONFIG object for France: different chart of accounts codes, 20% standard rate, and France has three reduced tiers instead of one. The tax calculation function takes the market config as input, so no function changes needed. The only new code is the config data."

---

## Category 4: Production Thinking

### Q: "This categorization pipeline works in your demo. What breaks at 10 million transactions per month?"

**Target answer:**
> "Three things: latency, cost, and monitoring. Latency: batch categorization with async processing instead of synchronous per-transaction. Cost: caching — if we've seen 'GitHub Inc' 50,000 times, we shouldn't call the LLM each time; merchant-level caching with periodic recalibration. Monitoring: at 10M/month, a 0.1% error rate is 10,000 wrong bookings. You need automated anomaly detection on the correction rate, not just aggregate accuracy."

**Hostile follow-up:** "What about the 1% of transactions that are genuinely hard?"

> "Those are your long-tail. The 80/20 insight: 80% of transactions match 20% of merchants (AWS, GitHub, Vodafone — well-known, cacheable). The remaining 20% are novel merchants where the model adds the most value. The architecture should treat these differently: cached merchants bypass the LLM entirely, novel merchants get full classification with higher human-review sampling."

### Q: "How do you debug a wrong categorization that happened three weeks ago?"

> "The trace. Every transaction gets a correlation ID linking: the raw input, extracted features, the model's category prediction + confidence, the routing decision, and the final booking. When an accountant corrects a booking three weeks later, you pull the trace and immediately see: was the input bad (OCR error), was the model wrong (category prediction), or was the routing too aggressive (confidence was 0.86, threshold was 0.85)? Without the trace, you're guessing."

---

## Category 5: Product and Adoption

### Q: "Ivo mentioned adoption as a dedicated workstream. What does that mean to you as an engineer?"

**Target answer:**
> "It means the AI patterns we build are only valuable if teams actually use them. Adoption engineering is about removing friction: clear APIs, good documentation, observable behavior, and measurable value. Concretely: if we build a categorization service, adoption means the domain team can integrate it without reading the model internals — they call an API, get a structured response with confidence, and decide their routing. If integration takes more than a day, the adoption failed."

**Hostile follow-up:** "What if teams don't trust the AI output?"

> "Trust is earned, not declared. Start with proposal mode: the AI suggests, the human confirms. Track the confirmation rate. When the human confirms 95%+ of suggestions without changes, you've earned the right to propose auto-mode. Show the team the data: 'You confirmed 97% of suggestions last month, 0 were wrong — want to try auto-booking the high-confidence ones?' That's how earned autonomy works in practice."

### Q: "What's the difference between a useful AI feature and an AI demo?"

> "A demo shows what the model can do. A useful feature shows what the workflow no longer requires a human for. The metric isn't 'the model got it right' — it's 'this process used to take 40 minutes and now takes 5.' Finom's framing of FTE per active customer is exactly this: the AI is useful when it measurably reduces human cost in the workflow."

---

## Category 6: Self-Awareness and Gaps

### Q: "You don't have fintech experience. Why should we hire you?"

> "I don't have fintech domain experience, but that's exactly where domain arbitrage applies — industry knowledge is the #1 differentiator in AI engineering right now. I have SMB experience from running Fysp Tech, which means I've actually done the accounting workflows you're automating. I know what UStVA filing feels like from the user side — where the friction is, what a bad auto-categorization does to your month-end close. The engineering patterns — confidence routing, evaluation, observability, multi-agent coordination — are domain-agnostic. What's domain-specific is the chart of accounts and tax rules, which are learnable and deterministic. I already have the harder part: understanding the user's problem."

### Q: "You don't know C#/.NET. Half our backend is C#."

> "That's true. But Ivo described the AI work as primarily Python, with C#/.NET as the broader platform. I'd expect to work in Python for agent/LLM services and interact with C# through APIs and event-driven boundaries. Learning C# to the point of reading and reviewing it is weeks, not months. And the integration pattern — AI services as Python microservices called from a C# platform — is a well-understood architecture."

### Q: "What's the biggest risk if we hire you?"

> "Ramp time on fintech domain specifics — German accounting conventions, banking integrations, regulatory nuance. The mitigation is that I learn fast and I have real SMB context from running my own company. The engineering patterns are already there; the domain knowledge is the growth area."

---

## Category 7: Algorithmic Precision (Viktar's Competitive Programming Background)

Viktar has a competitive programming background (ICPC/NERC 2019-2020). He may probe whether you think precisely about invariants, edge cases, and correctness — not just architecture.

### Q: "What are the invariants your system must maintain?"

> "Three that must hold on every transaction, always:
> 1. **Terminal state**: every ingested transaction reaches exactly one terminal state within SLA — no silent drops, no dual-processing.
> 2. **Idempotency**: re-processing the same transaction (same idempotency key) produces the same output — idempotency key = hash(transaction_id + batch_id).
> 3. **Auditability**: every routing decision is logged with the input hash, confidence score, threshold, and outcome at time-of-decision — not reconstructed afterward.
>
> These aren't aspirational — they're things you enforce in the code. Terminal state is enforced by the lifecycle registry. Idempotency is enforced by checking the key before any write. Auditability is enforced by logging before returning, not after."

**Why this works**: Names invariants specifically, distinguishes enforcement from aspiration.

### Q: "How do you prove your confidence router is correct?"

> "I write it as a pure function with no side effects, then test it against a complete coverage of the input space. There are 4 terminal states and 2 hard constraints (reverse charge, confidence thresholds). Every path through the routing logic maps to exactly one terminal state — that's testable exhaustively with a small input set. The correctness argument is: (a) I can enumerate all inputs that produce each output, (b) every input maps to exactly one output, (c) there's no input that maps to zero outputs (no unhandled case). That's a property test, not just a unit test."

**Hostile follow-up:** "What if a new market has a different compliance override?"

> "The override list is part of the MarketPolicy, not hardcoded in the router. Each market policy declares which transaction properties trigger a mandatory human-review override. The router evaluates the policy's override list before applying confidence thresholds — so the invariant holds: override wins, confidence routing is secondary."

### Q: "Your pipeline has 5 stages. How do you handle a failure in stage 3?"

> "Each stage has an explicit failure contract — it either returns a valid typed result or throws a typed error. On stage failure: (1) log the failure with correlation ID and stage name, (2) the transaction moves to an explicit `error_logged` terminal state — not dropped, (3) the error is routed to a dead-letter queue for replay or manual triage. I don't catch-all-and-continue because that would let a failed extraction silently propagate into a wrong categorization. Fail fast, log explicitly, never swallow."

**Hostile follow-up:** "What if you want to retry just stage 3?"

> "If stage 3 is idempotent and has a known transient failure (timeout, rate limit), you can retry it up to N times with exponential backoff before marking `error_logged`. If the first two stages are expensive (OCR), you cache their outputs by transaction hash — on retry, you skip them and resume from stage 3. This only works if stage outputs are stored, not streamed. The trade-off: more storage, but stage-level retry without re-running the full pipeline."

### Q: "How do you handle the case where the same transaction is submitted twice?"

> "Idempotency key. Every transaction gets a key derived from its content (or the upstream system's identifier) before it enters the pipeline. On receipt, I check: has this key already been processed? If yes, return the existing result — no new pipeline run. This prevents double-booking. The idempotency check must happen before any side effect, including the first LLM call. The key is stored in a fast lookup (Redis or similar) with TTL matching the deduplication window."

---

## Category 8: System Behavior Under Load

### Q: "Your categorization service is 60% of the latency. How do you fix it?"

> "Two passes. First: does it need to be in the hot path? If this is batch processing (month-end), I can move categorization to a background queue — the user doesn't need the result synchronously. If it must be synchronous, second pass: can I skip the model for most calls? Merchant caching means AWS, GitHub, Stripe categorize instantly from cache — those are 60%+ of real-world volume. For the remaining 40% that need the model, I apply bounded async concurrency: semaphore-limited `asyncio.gather`, not sequential calls. On a 20-item batch at 40ms/item: sequential = 864ms, async with concurrency 5 = ~164ms."

**Why specific numbers matter**: Shows you've actually measured this, not just described it conceptually.

### Q: "What's your approach to testing a categorization model before it goes to production?"

> "Four-level evaluation framework. Level 1: field-level accuracy against labeled test set — per-field, not just end-to-end. Level 2: severity-weighted accuracy — wrong VAT rate is catastrophically worse than wrong description; weight failures accordingly. Level 3: calibration check — ECE below 0.05 means confidence scores are trustworthy for routing. Level 4: regression detection — compare this run against the baseline run; any case that changed from pass to fail is a regression and blocks shipping. I'd run all four in CI against every model or prompt change."

---

## Pre-Interview Drill

Run through these 5 scenarios in 15 minutes:

1. **Confidence threshold justification** — explain ECE in 30 seconds
2. **AI vs deterministic boundary** — defend why VAT must be rules, handle the "but edge cases" follow-up
3. **Live coding recovery** — acknowledge a gap, pivot to the most valuable next action
4. **Scale challenge** — merchant caching, batch processing, anomaly detection
5. **Self-awareness** — fintech gap answer, delivered without defensiveness

Viktar precision drills (add 5 min):
6. **State the 3 invariants** — terminal state, idempotency, auditability — in 45 seconds
7. **Describe stage failure handling** — fail fast, error_logged terminal state, dead-letter queue

