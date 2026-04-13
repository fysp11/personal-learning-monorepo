# Cross-Company System Design Template

Saved: 2026-04-13

A 7-step skeleton for answering "design X" questions in any technical interview. Finom instantiation included.

---

## The 7 Steps

### Step 1: Scope

Clarify input, output, and success condition before proposing anything.

- What is the input? (raw bank transaction, scanned receipt, batch file, event stream)
- What must come out? (booking record, structured proposal, batch report, audit log)
- What is the worst kind of wrong? (wrong VAT = compliance; wrong description = cosmetic)
- What scale? (per-transaction interactive vs. batch month-end vs. event-driven)
- What is v1 vs. later? (Germany only? auto-book or proposal mode?)

**Say first**: "Before I design — the input is [X], the output is [Y], and a wrong output costs [Z]. Let me make sure we agree on that before I draw anything."

---

### Step 2: AI Boundary

State explicitly what is AI-powered vs. deterministic. Do not skip this.

| Component | AI or Deterministic | Why |
|-----------|--------------------|----|
| Document/text extraction | AI | Unstructured, messy input |
| Transaction categorization | AI | Merchant names are ambiguous |
| VAT rate calculation | Deterministic | Tax law, not judgment |
| Reverse charge detection | Deterministic | §13b UStG compliance |
| Account code lookup | Deterministic | Chart of accounts is fixed |
| Confidence routing | Deterministic | Threshold-based rules |
| Booking entry creation | Deterministic | Double-entry math |

**The rule**: If failure cost is compliance-related → deterministic. If input is genuinely ambiguous → AI.

**Say**: "The most important boundary is: categorization is AI because merchant text is ambiguous. Tax calculation is deterministic because the law specifies the rate — that's not a prediction."

---

### Step 3: Pipeline

Draw the stages as a flow with typed contracts between them.

```
Input Event
  → Stage 1: Feature Extraction (AI)
      Output: ExtractedFields { vendor, amount, date, description }
  → Stage 2: Category Proposal (AI)
      Output: CategoryProposal { accountCode, confidence, reasoning }
  → Stage 3: VAT Calculation (Deterministic)
      Output: VatResult { vatRate, netAmount, vatAmount, mechanism }
  → Stage 4: Confidence Router (Deterministic)
      Output: RoutingDecision { action: auto_book | propose | reject | requires_review }
  → Stage 5: Booking Entry (Deterministic)
      Output: BookingRecord { debitAccount, creditAccount, vatAccount, amounts }
```

**Say**: "I define typed contracts between stages so each one is independently testable and fails visibly instead of silently corrupting the next step."

---

### Step 4: Confidence Routing

Describe the routing logic. This is where most interviewers probe.

```
if mechanism == reverse_charge:      → requires_review (compliance override, never auto-book)
elif confidence >= 0.85:             → auto_booked
elif confidence >= 0.55:             → proposal_sent (structured recommendation)
else:                                → rejected (explicit terminal state)
```

**Key points to make**:
- Thresholds are calibration decisions, not constants. Start conservative (0.90), widen as override rate confirms.
- ECE must be below 0.05 before using confidence scores for routing at all.
- Reverse charge is a hard override — compliance beats confidence.
- Every transaction must reach exactly one terminal state (no silent drops).

**Say**: "0.85 isn't a magic number — it comes from calibration data. We'd start at 0.90, measure override rate on auto-booked transactions, and only widen the threshold when the data supports it."

---

### Step 5: Observability

Name the three layers of monitoring in priority order.

**Layer 1 (Day 1)**: Confidence distribution
- Track P10/P50/P90 per market, per stage, per day
- Alert if P50 drops >2σ below 30-day baseline
- Why: leading indicator — you see drift before accuracy degrades

**Layer 2 (Day 2)**: Terminal state tracking
- Every transaction has a lifecycle state: `ingested → processing → [terminal]`
- Alert if any transaction is non-terminal past the SLA window (e.g., 2 hours)
- Why: catches silent rejects (FM-15) that don't appear in accuracy metrics

**Layer 3 (End of Week 1)**: Business KPIs
- Auto-book rate (target: >70% steady-state, <30% at new market launch)
- Override rate on auto-booked items (target: <2%, alert at >5%)
- Proposal acceptance rate (target: >85%)
- Severe error rate (wrong VAT or wrong account code — target: zero)

**Say**: "I add confidence distribution monitoring on day one because it's the leading indicator. By the time accuracy metrics degrade, you've already misboked real transactions."

---

### Step 6: Scale

Address the three axes: latency, cost, and reliability.

**Latency**:
- Batch async instead of per-transaction sync
- Caching: common merchants (AWS, GitHub, Vodafone) bypass the LLM — merchant-level cache with periodic TTL
- The 80/20 rule: 80% of transactions match 20% of known merchants; cache those, classify the rest

**Cost**:
- Model cascade: cheap smaller model for high-confidence common cases, larger model for ambiguous long-tail
- Semantic caching: cache embedding of common merchant patterns
- Re-ranker before LLM to filter irrelevant context before it reaches the model

**Reliability**:
- Idempotency key on every transaction (idempotency_key = hash(transaction_id + batch_id))
- Circuit breaker on categorization service (trip at 40% failure rate, reset after 30s)
- Dead-letter queue for failed transactions — explicit failure, not silent drop

---

### Step 7: Failures

Name specific failure modes, not generic ones. See the named FM list.

**Most important to name**:
- FM-01 OCR drift: document quality degrades → confidence inflates without matching accuracy
- FM-04 Overconfident miscategorization: model says 0.92, actually wrong → needs Platt scaling calibration
- FM-07 Reverse charge miss: cross-border B2B auto-booked without §13b review → compliance violation
- FM-14 Escalation storm: bad batch floods human review queue → circuit breaker prevents
- FM-15 Silent reject: transaction ingested, never reaches terminal state → lifecycle registry
- FM-16 Stage leak: transaction double-processed on retry → idempotency key

---

## Finom Instantiation (Quick Reference)

| Step | Finom Answer |
|------|-------------|
| Scope | Input: bank transaction or receipt. Output: SKR03 booking record. Worst wrong: incorrect VAT rate (tax amendment). V1: Germany, proposal mode. |
| AI Boundary | AI: extraction + categorization. Deterministic: VAT, reverse charge, account lookup, routing, booking. |
| Pipeline | Extract → Categorize → Calculate VAT → Route → Book (5 stages) |
| Routing | 0.85 auto-book, 0.55 proposal, below → reject. Reverse charge always surfaces. |
| Observability | Confidence P50 per market (leading), terminal state lifecycle (silent rejects), auto-book rate + override rate (business) |
| Scale | Merchant cache (80/20), async batch, idempotency key, circuit breaker on categorization |
| Failures | FM-04 overconfidence, FM-07 reverse charge miss, FM-15 silent reject, FM-16 double-process |

---

## System Design Answer Skeleton (30-Second Version)

> "Before I design — input is [X], output is [Y], worst failure is [Z]. The core boundary: [AI part] is AI because the input is ambiguous. [Policy part] is deterministic because the failure cost is compliance-related. The pipeline has [N] stages with typed contracts: [list them]. Confidence routing uses [thresholds] with a hard override for [compliance edge case]. Observability starts with confidence distribution as the leading indicator. At scale, the main levers are [merchant caching, async batch, circuit breaker]. The specific failure modes I'd design against are [FM-XX]."

---

## Multi-Market Extension Pattern

When asked "how would you add France?":

**What changes (France)**:
- PCG account code mapping (6xx expense accounts vs SKR03 4xxx)
- 4-rate VAT: 20% standard, 10% food service, 5.5% essential food, 2.1% press
- CA3 VAT return → DGFiP (not ELSTER)
- Chorus Pro integration for B2B e-invoicing (Sept 2026 mandate)
- Cold-start calibration: start at max conservatism (Level 0: 100% human review)

**What doesn't change**:
- Pipeline shape (same 5 stages)
- Confidence routing logic
- Terminal state lifecycle
- Circuit breaker and idempotency
- Observability layers

**Implementation**:
- `FR_POLICY` implements the same `MarketPolicy` interface as `DE_POLICY`
- Orchestrator calls `policy.getAccountCode(category)` and `policy.calculateVat(...)` without knowing it's France
- Adding Italy → add `IT_POLICY`, zero changes to pipeline code

**Say**: "The orchestrator doesn't know about SKR03 or PCG. It calls policy methods. Adding France is writing one new policy module, not touching the pipeline."
