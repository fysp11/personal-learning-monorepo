# Human-in-the-Loop Design Patterns for Financial AI

Saved: 2026-04-17

The pipeline has four terminal states: `AUTO_BOOKED`, `PROPOSAL_SENT`, `REQUIRES_REVIEW`, `REJECTED`. Two of those four states require a human to act. The quality of that human interaction determines the quality of the feedback loop that trains the next model iteration.

This is product thinking, not just engineering. Getting the HITL design wrong means:
- Users reject proposals they would have accepted (friction → worse coverage)
- Users accept wrong proposals (noise → bad training signal)
- Users don't explain why they overrode (no learning signal)
- The feedback loop is noisy → ECE degrades over time instead of improving

---

## What the Human Sees in Each State

### PROPOSAL_SENT (`confidence ∈ [0.55, 0.85)`)

The system has a view but isn't confident enough to act autonomously. What to show:

```
┌──────────────────────────────────────────────────────────────┐
│ Lieferando — €47.80                          Tue 15 Apr      │
│                                                              │
│ Suggested: Meals & Entertainment (4650)                      │
│ Reason: food delivery service — similar to 3 prior bookings  │
│ Confidence: 82%                                              │
│                                                              │
│  [✓ Book as 4650]  [✎ Change account]  [Skip for now]       │
└──────────────────────────────────────────────────────────────┘
```

Key design decisions:
1. **Show the account name, not just the code** — "4650" is meaningless to a small business owner; "Meals & Entertainment" is not
2. **Show why** — "similar to 3 prior bookings" is the retrieval evidence surfaced; it builds trust and helps the user make a better decision
3. **One-click accept** — the happy path must be frictionless; a user who has to click 3 times to accept a proposal accepts fewer proposals
4. **Change is explicit** — choosing a different account opens a picker, not a freeform field; structured corrections are better training signal
5. **"Skip for now"** is allowed, but with a 7-day cap before escalation (GoBD timeliness constraint)

### REQUIRES_REVIEW (`is_b2b = True` or compliance trigger)

Higher stakes than PROPOSAL_SENT — the system is specifically flagging a compliance concern.

```
┌──────────────────────────────────────────────────────────────┐
│ Acme Ltd — €5,000.00                    ⚠ Needs Your Review  │
│                                                              │
│ B2B transaction — EU reverse charge may apply               │
│ Suggested: Professional Fees (6825)                          │
│                                                              │
│ If counterparty is VAT-registered in EU:                     │
│  • VAT = €0 (reverse charge applies)                         │
│  • You report this on your ZM filing                         │
│                                                              │
│ Counterparty VAT ID: [________________]  [Look up VIES]      │
│                                                              │
│  [✓ Confirm reverse charge]  [✗ Standard VAT applies]        │
└──────────────────────────────────────────────────────────────┘
```

Key design decisions:
1. **Explain the implication** — "reverse charge may apply" with brief explanation; the user must understand *why* this matters
2. **Enable the action directly** — VIES lookup inline; don't make them tab to another browser
3. **Two explicit paths** — confirm or deny, not a freeform field; structured choices = clean training signal
4. **No "skip"** — `REQUIRES_REVIEW` must be resolved before month-end close; "skip" creates a compliance backlog

---

## The Feedback Loop Architecture

Every human decision in PROPOSAL_SENT or REQUIRES_REVIEW is training signal. The quality of that signal determines how fast the model improves.

```
User confirms proposal
    → record: {tx_id, merchant, amount, proposed_code, confirmed_code, signal="confirm"}
    → if confirmed_code == proposed_code: positive signal (model was right)
    → if confirmed_code != proposed_code: negative + correction signal (model was wrong)

User overrides proposal
    → record: {tx_id, merchant, amount, proposed_code, override_code, signal="override",
               override_reason: enum[wrong_account | wrong_vat | other]}
    → override_reason is required — "other" with optional freeform note
    → this feeds directly into the merchant pattern update queue

User confirms REQUIRES_REVIEW as reverse charge
    → record: {tx_id, counterparty_vat_id, vies_result, confirmed_mechanism="reverse_charge"}
    → this trains the VIES-lookup pattern

User rejects reverse charge classification
    → record: {tx_id, counterparty_vat_id, confirmed_mechanism="standard"}
    → this is a training signal that the B2B flag on this type of transaction is unreliable
```

### Override rate as the primary signal

The most important metric from the HITL system is the **override rate per merchant pattern**:

```python
override_rate[merchant][account_code] = (
    overrides_from_X_to_Y / (confirms_to_X + overrides_from_X) 
)
```

If `override_rate["lieferando"]["4650"] > 2%`, the Lieferando → meals mapping is losing trust. Before the next model deployment, this rate should be reviewed.

**Key invariant**: if override_rate for any AUTO_BOOKED merchant rises above 5% sustained for 30 days, that merchant should be demoted from AUTO_BOOKED to PROPOSAL_SENT until the cause is diagnosed.

---

## Learning Loop Design

```
                 ┌─────────────────────────────────┐
                 │   Pipeline (current model/prompt) │
                 └───────────────┬─────────────────┘
                                 │ categories + confidence
                                 ▼
                ┌──────────────────────────────────────┐
                │     Routing (AUTO_BOOKED /           │
                │     PROPOSAL / REQUIRES_REVIEW)      │
                └───────────────┬──────────────────────┘
                                │ human decisions
                                ▼
                ┌──────────────────────────────────────┐
                │     Feedback Store                    │
                │   (confirms, overrides, corrections)  │
                └──────────┬───────────┬───────────────┘
                           │           │
                    override           confirm
                    rate > 5%          rate > 98%
                           │           │
                           ▼           ▼
                    ┌──────────┐  ┌──────────────┐
                    │ Pattern  │  │ Threshold    │
                    │ review   │  │ widening     │
                    │ queue    │  │ candidate    │
                    └──────────┘  └──────────────┘
```

The threshold widening path: if a merchant pattern has a 30-day confirm rate > 98% and override rate < 1%, it's a candidate for auto-booking even at lower confidence — but this must go through the shadow rollout gates first.

---

## REJECTED State — Special Case

`REJECTED` transactions (`confidence < 0.55`) don't get a proposal. They go straight to a manual categorization queue. This is intentional — showing a very low-confidence proposal creates noise (users override it so often that it provides little signal).

But `REJECTED` transactions still generate learning signal:
- When the user manually categorizes them, that becomes a high-quality training example
- The merchant + human-assigned account = ground truth for future retrieval (RAG pipeline)
- High volume of REJECTED transactions for the same merchant → add it to the keyword patterns

### REJECTED queue UX:

```
┌──────────────────────────────────────────────────────────────┐
│ 3 transactions need manual categorization                    │
│                                                              │
│ Unknown GmbH — €40.00                     New vendor        │
│ [Search accounts...]                                         │
│  4990 Miscellaneous                                          │
│  4940 IT Costs                                               │
│  6825 Professional Fees                                      │
│                                                              │
│ □ Remember this for "Unknown GmbH" (always suggest 4990)    │
└──────────────────────────────────────────────────────────────┘
```

The "Remember this" checkbox is the explicit training signal trigger. When checked:
1. Merchant + account code added to the business's custom patterns
2. Retrieval store updated with this transaction as a high-signal example
3. On next occurrence, this merchant will route to PROPOSAL_SENT at minimum

---

## Interview Answer: "How does the model learn from user feedback?"

> "The HITL system captures three signal types: confirms (user accepts proposal → positive signal), overrides (user changes account → correction signal with required reason), and manual categorizations from the rejected queue. Override rate is the primary alert metric — if any merchant's override rate rises above 5% for 30 days, that merchant is demoted from auto-book to proposal. Manual categorizations feed directly into the RAG retrieval store as high-confidence examples: 'this business manually categorized Unknown GmbH as miscellaneous' is stronger evidence than a model prediction. The learning loop means the pipeline gets more accurate for each specific business over time, not just at the model level — which is the argument for RAG over static rules."

The phrase "three signal types" and "override rate is the primary alert metric" signals operational maturity.

---

## What a Good HITL System Prevents

Without structured HITL:
- Noisy training signal → model oscillates between wrong answers
- No distinction between "user accepted reluctantly" and "user was confident" → same positive signal
- No learning from corrections → override rates stay high forever
- GoBD traceability fails — "the user clicked OK" is not an audit trail

With structured HITL:
- Override rate per merchant is a tracked metric, not a surprise
- Every correction carries a reason code → structured training signal
- The model learns from this business's specific vocabulary, not just global patterns
- Every human decision is logged with timestamp + user ID → GoBD audit trail
