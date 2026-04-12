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

---

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

> "I don't have fintech domain experience, but I have SMB experience — I ran Fysp Tech, which means I've actually done the accounting workflows you're automating. I know what UStVA filing feels like from the user side. The engineering patterns — confidence routing, evaluation, observability, multi-agent coordination — are domain-agnostic. What's domain-specific is the chart of accounts and tax rules, which are learnable and deterministic."

### Q: "You don't know C#/.NET. Half our backend is C#."

> "That's true. But Ivo described the AI work as primarily Python, with C#/.NET as the broader platform. I'd expect to work in Python for agent/LLM services and interact with C# through APIs and event-driven boundaries. Learning C# to the point of reading and reviewing it is weeks, not months. And the integration pattern — AI services as Python microservices called from a C# platform — is a well-understood architecture."

### Q: "What's the biggest risk if we hire you?"

> "Ramp time on fintech domain specifics — German accounting conventions, banking integrations, regulatory nuance. The mitigation is that I learn fast and I have real SMB context from running my own company. The engineering patterns are already there; the domain knowledge is the growth area."

---

---

## Category 7: France Expansion (Iterations 6 Topics)

### Q: "You said market config is data, not code. What actually has to change to support France?"

**Target answer:**
> "More than just config — but less than a rewrite. The pipeline shape, orchestrator, confidence routing, and observability all transfer unchanged. What's genuinely new: a PCG account mapping (different codes from SKR03), a 4-rate VAT policy (France has 20/10/5.5/2.1% vs Germany's 19/7%), and a filing integration against DGFiP's CA3 instead of ELSTER. That's real engineering work — not just a config change. And France has a September 2026 e-invoicing mandate via Chorus Pro that adds a new pre-categorization stage for structured XML invoices."

**Hostile follow-up:** "That sounds like a lot. Is multi-market actually a solved problem?"

> "The workflow is solved. The per-market compliance surface is genuinely hard and always will be. The value of the abstraction isn't that adding a market is trivial — it's that the hard parts are isolated. Changing a VAT rate doesn't touch the confidence router. Adding Chorus Pro support doesn't touch the eval harness. You can work on each piece without disturbing the others."

### Q: "France has four VAT rates. How does your categorization model handle that?"

> "The model doesn't. The model outputs a category label — 'restaurant', 'food delivery', 'cultural event'. The deterministic VAT layer looks up the category in the French policy config and finds the applicable rate. A restaurant is 10% for sit-in, 5.5% for takeaway. That distinction might need an extra feature (has a table service flag, or the transaction description contains 'emporter'). The AI proposes the category; the rules apply the rate. Same pattern as Germany — just more rules."

**Hostile follow-up:** "What about the cold start? No French training data at launch."

> "That's the France-specific calibration problem. At launch: 100% proposal mode regardless of confidence score. Collect the first 1000 reviewed transactions. Fit per-market calibration curves. Then, and only then, widen the auto-book threshold. The Germany model gives a warm start — most SaaS vendors, travel expenses, and coworking are the same — but French merchant names and categories need validation before we trust the scores."

---

## Category 8: Failure Modes and Production Reliability

### Q: "What failure mode actually woke you up at night in a production AI system?"

**Target answer (use a pattern from the failure modes encyclopedia):**
> "The silent reject pattern. A transaction was ingested but never reached a terminal state — not booked, not in review, not flagged. The user's money moved but their accounting didn't reflect it. We only caught it because a daily balance reconciliation noticed the count mismatch: 47 transactions ingested, 46 in terminal state. That one stranded transaction had been sitting in the pipeline for 6 hours. The fix: every transaction must have an explicit lifecycle state machine with an SLA clock on non-terminal states. If a transaction hasn't advanced in 30 minutes, it goes to a dead letter queue with an alert."

**If pushed:** "What was the root cause?"

> "A message queue consumer crashed mid-processing — wrote the first stage result to the database but didn't acknowledge the message. The retry policy requeued it, but by then the circuit breaker had tripped and the retry sat unprocessed. Multiple failure modes compounding. The lesson: idempotency isn't just about duplicate prevention — it's about making the recovery path observable."

### Q: "Your confidence calibration sounds good in theory. What does ECE of 0.08 actually mean operationally?"

> "It means when the model says it's 85% confident, it's actually right about 77% of the time. That 8% gap means if you set your auto-book threshold at 0.85, you're silently auto-booking things that fail roughly 1-in-8 times instead of 1-in-6.6. In accounting, a 15% error rate on auto-booked transactions is going to generate a lot of correction work. Practically: you'd tighten the threshold to 0.93 to get the same actual accuracy as the calibrated-0.85 case, or you'd run Platt scaling to recalibrate the raw scores."

### Q: "You described a circuit breaker for escalation storms. Isn't that just hiding failures?"

> "Only if the circuit breaker opens silently. The circuit must emit an alert when it opens: ops gets a notification, the batch is paused, and the queue holds new work without dropping it. The circuit isn't hiding the failure — it's preventing the failure from cascading into a queue flood. Hidden failures are the anti-pattern; the circuit breaker makes the failure visible and controlled. The difference between 'the pipeline is struggling' (circuit closed, high error rate) and 'we know the pipeline is struggling, we've stopped auto-processing, and ops is investigating' (circuit open, alert sent) is the entire point."

---

## Category 9: FTE Metric and Business Impact

### Q: "FTE per active customer is a finance metric. Why do you care about it as an engineer?"

**Target answer:**
> "Because it's the only honest measure of whether the AI is actually doing work or just generating noise. An AI system that auto-books 90% of transactions but drives a 10% correction rate might have the same FTE cost as a 50% auto-book system with a 1% correction rate — the corrections from the first system are expensive. The FTE metric integrates all of that: human time for review + correction + support tickets + error remediation. If FTE per customer is going down as customer count grows, the AI is reducing real work. If it's flat, the AI savings are being eaten by the overhead it creates."

**Hostile follow-up:** "But you can't measure FTE per customer in a sprint. What do you actually track?"

> "Leading indicators: override rate (monthly), proposal confirmation rate (weekly), support ticket rate per customer (weekly). These move faster than FTE and predict it. If override rate climbs from 1% to 3%, FTE per customer will climb in the next quarter. That's the signal to act before the lagging metric worsens."

### Q: "You claim 85% auto-book rate. How do you know it's sustainable, not just correct on easy cases?"

> "That's exactly the severity weighting question. Raw auto-book rate is meaningless if all the auto-booked cases are the easy ones. I'd split the auto-book rate by case difficulty: known vendors (should be 95%+), first-time vendors (might be 50%), B2B EU transactions (deliberately 0% — always surfaces for reverse-charge review). If the 95%+ auto-book rate is driven by Amazon and Adobe subscriptions while all the hard cases hit the review queue, you're not really at 85% — you're at 85% on the easy 70% of transactions. The meaningful number is auto-book rate on transactions the model hasn't seen before."

---

## Category 10: The 90-Day Plan Under Pressure

### Q: "You said 30 days learning before contributing. We move fast — that feels slow."

**Target answer:**
> "I said learning *before proposing architecture changes*. I'd be writing code in the first week — tests, eval cases, instrumenting existing pipelines. The learning period is about not proposing rewrites I don't understand yet. There's a real cost to an engineer who joins and immediately suggests redesigning the system they haven't seen fail in production. The 30-day snapshot is about earning the credibility to propose, not about waiting to be useful."

**Hostile follow-up:** "What would you actually ship in week 2?"

> "An eval test case for a failure mode I found in the first week's production audit. If I trace a live transaction and notice the eval harness doesn't cover the error pattern I just saw, adding that test case is immediately valuable, low-risk, and signals that I'm reading the actual failure data rather than the documentation."

### Q: "Your 90-day plan ends with 'share a pattern'. What if the team doesn't want a pattern from a 90-day engineer?"

> "Then I read the signal right. If the team isn't ready to adopt the pattern, forcing it out at 90 days is exactly the wrong move. The goal isn't to ship a pattern in 90 days — it's to *identify* one worth shipping. If the timing isn't right, the contribution might be a focused PR or a well-scoped addition to the eval harness. The output of 90 days is trust and one concrete useful thing — not necessarily a reusable abstraction."

---

## Category 11: Autonomous Workflow Design

### Q: "Your batch processor auto-books revenue transactions at 95% confidence. What if a client payment is misidentified as a transfer?"

**Target answer:**
> "That's why inbound transactions get their own routing rule. Revenue recognition is higher stakes than expense categorization — a misidentified client payment could mean we report revenue in the wrong period or to the wrong counterparty. In my demo, inbound items with high confidence auto-book as revenue, but in a production system I'd surface all inbound items above a threshold amount — say €1000 — for confirmation regardless of confidence. The FTE cost of reviewing 3 inbound payments per month is negligible compared to the risk of misattributing revenue."

### Q: "The 'go do the task, come back' UX sounds great. But users won't check the results. They'll just assume it's right."

> "That's a real UX risk and the reason proposal mode exists. 'Come back' doesn't mean the user rubber-stamps everything — it means the system has already made the easy decisions so the user's attention is focused on the few things that actually need it. In the batch demo: 8 auto-booked silently, 3 require 30 seconds of confirmation each, 2 require the user to understand reverse charge. The cognitive load shifts from 'process 15 transactions' to 'check 5 things the system flagged.' If users are rubber-stamping without reading, the proposal UX is failing — and that's a product problem, not an AI problem. The signal is override rate near zero *with* low error rate in subsequent audits."

---

## Pre-Interview Drill

Run through these 5 scenarios in 15 minutes:

1. **Confidence threshold justification** — explain ECE in 30 seconds
2. **AI vs deterministic boundary** — defend why VAT must be rules, handle the "but edge cases" follow-up
3. **Live coding recovery** — acknowledge a gap, pivot to the most valuable next action
4. **Scale challenge** — merchant caching, batch processing, anomaly detection
5. **Self-awareness** — fintech gap answer, delivered without defensiveness

**Add for April 14 (iterations 4–6 topics):**

6. **France expansion** — "What actually has to change?" (don't undersell the work)
7. **Failure modes** — name one that happened, root cause, what you'd do differently
8. **FTE metric** — explain as a leading indicator framework, not just a number
9. **90-day plan under speed pressure** — "30 days learning feels slow"
10. **Autonomous workflow** — defend the "come back" UX against "users won't check"
