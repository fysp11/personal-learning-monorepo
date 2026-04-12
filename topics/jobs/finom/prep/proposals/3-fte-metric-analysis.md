# FTE per Active Customer — Metric Analysis for Interview 3

Saved: 2026-04-11 (Iteration 6)

## Purpose

Ivo Dimitrov used "FTE per active customer" as the concrete success metric for Finom's AI work. This is a specific and revealing choice of language. Use this document to understand the metric deeply, connect it to what the AI pipeline actually does, and have a confident answer if asked about measuring business impact.

---

## What the Metric Means

**FTE per active customer** = (total full-time-equivalent headcount in customer-facing operations) ÷ (number of active customers)

It measures operational *leverage*: how much human labor does each additional customer require?

- A high ratio: each customer requires significant manual handling → not scalable
- A low ratio: customers can be served with minimal marginal human effort → scalable
- Trend going down over time: automation is working

**Why Finom cares about this:**
- They're targeting 1 million customers by end of 2026 (up from 200K+ now)
- That's roughly 5x growth
- Without automation: need ~5x support/ops headcount
- With automation: the curve flattens — fixed engineering cost to build the AI pipeline, near-zero marginal cost per additional customer

**The business logic:**
```
Revenue per customer:  relatively fixed (subscription + transaction fees)
Marginal cost per customer without AI: high (manual accounting support, error remediation)
Marginal cost per customer with AI:    near-zero for automatable tasks
AI investment:         one-time + maintenance
Break-even point:      when AI saves (n × marginal_human_cost) > AI build cost
```

---

## How the AI Accounting Pipeline Moves This Metric

Break the FTE cost into components:

### Component 1: Transaction categorization manual effort
**Without AI:** Customer or support agent manually categorizes each expense, matching to SKR03 codes. For an SME with 50 transactions/month, this is ~2 hours/month of customer time or support overhead.
**With AI (85% auto-book rate):** ~7 transactions/month need customer review. Time: ~15 minutes/month. Support tickets about miscategorizations drop proportionally.
**Leverage on FTE:** Support overhead per customer drops ~85%.

### Component 2: VAT return preparation
**Without AI:** Customer or accountant manually tallies input/output VAT, checks rates, fills UStVA form. ~3-4 hours/year per filing period × 12 = significant time.
**With AI:** Auto-populated draft UStVA ready for signature. Customer reviews and approves in ~15 minutes if categorization is correct.
**Leverage on FTE:** Preparation work reduced to near-zero; human effort is now just approval.

### Component 3: Error remediation
**Without AI:** Miscategorization → wrong UStVA → amendment required → support ticket → accountant review → correction. Cost: high (customer time + support time + possible penalty).
**With AI + severity weighting:** Critical cases (wrong VAT rate) caught in eval before production. Reverse charge surfaced for manual review. Override rate tracked to detect systematic errors early.
**Leverage on FTE:** Prevents the *expensive* errors that drive support volume.

### Component 4: Document handling
**Without AI:** Customer uploads receipts, manually matches to bank transactions.
**With AI (receipt matching):** Auto-matched on amount + date + vendor. Unmatched receipts flagged.
**Leverage on FTE:** Receipt matching time eliminated for the ~70% of transactions that have clear matches.

### Component 5: Onboarding new markets (internal FTE)
**Without AI pipeline abstraction:** Adding France requires new engineering work, new accounting consultant work, new support training.
**With parameterized market config:** Adding FR = one policy config object + calibration data collection + CA3 integration. Engineering work much lower; support training focused on FR-specific edge cases only.
**Leverage on FTE (internal):** Market expansion becomes additive, not multiplicative.

---

## What a Good FTE/Customer Trend Looks Like

```
Quarter    Customers    Ops FTE    FTE/Customer
Q1 2025    100K         80         0.0008
Q2 2025    130K         88         0.00068
Q3 2025    160K         91         0.000569
Q4 2025    200K         93         0.000465     ← AI Accountant GA
Q1 2026    230K         90         0.000391     ← curve bending
Q4 2026    1M           100        0.0001       ← target (hypothetical)
```

The inflection point is where customer count grows faster than FTE count. That's when you know the AI is doing real work, not just adding automation overhead.

---

## How to Measure It in Practice

**Input metrics (leading indicators, fast to measure):**
- Auto-book rate: % of transactions that bypass human review
- Override rate: % of auto-booked transactions later corrected by users
- Proposal confirmation rate: % of proposals accepted without modification
- Time in proposal queue: how long proposals sit before users confirm
- Support ticket rate per active customer: tickets/month/customer

**Output metrics (lagging indicators, measure monthly/quarterly):**
- Actual FTE per active customer (from headcount and customer data)
- Average time per customer for monthly close (if tracked via product usage)
- Error remediation rate: how often amended tax filings are filed

**The danger metric:** If override rate is low AND support tickets are also low, the AI is doing well. But if override rate is low AND support tickets are high about *different* issues, you're measuring the wrong thing and missing problems.

---

## How to Answer If Asked About Metrics

**If asked "how would you know the AI accounting pipeline is working?"**
> "I'd look at two things together: override rate and FTE per active customer. Override rate tells me whether auto-bookings are trusted — if users correct the system more than ~2% of the time, the thresholds are too aggressive. FTE per active customer is the business proof — it should be trending down even as customer count grows. Ivo used that phrase specifically, and it's the right bar: the question isn't whether the AI categorizes correctly in a test suite, it's whether the human work of accounting at Finom actually shrinks as more people sign up."

**If asked "how do you know the confidence threshold is set right?"**
> "The threshold is a dial between FTE savings and error risk. Too aggressive (threshold too low): more auto-books, but higher override rate and more support tickets from miscategorizations. Too conservative (threshold too high): fewer auto-books, more human review — the FTE/customer ratio stays high. The right threshold is where override rate is below ~2% and FTE/customer is still declining. ECE calibration tells you whether the confidence scores are meaningful enough to use as a dial at all."

**If asked "what's the first metric you'd look at after going live in France?"**
> "Proposal confirmation rate for the first 1000 French transactions. Not auto-book rate — France launches in 100% proposal mode by design because we have zero calibration data. Confirmation rate tells me how close the uncalibrated model is to correct. If confirmation rate is above 85%, I'd widen the auto-book threshold in 2 weeks. If below 70%, the cold-start problem is worse than expected and I need more French training data before expanding autonomy."

---

## Connecting to the Live Coding Round

In the autonomous-batch-processor.ts demo:
- 8/15 auto-booked (53% auto-book rate — low, first month for this user)
- 3/15 proposals (20%)
- 4/15 requires attention (27% — high, due to reverse charge and unknown vendors)

The FTE analysis would say: without AI, processing 15 transactions = ~45 min of accounting work. With AI at current calibration: user reviews 7 items = ~15 min. That's a 67% time reduction for this user profile. At scale, this is the FTE/customer metric moving in the right direction. As the model learns Anna's specific vendor set, auto-book rate climbs toward 85%+ and review time drops to ~5 minutes/month.
