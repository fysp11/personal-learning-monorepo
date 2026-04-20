"""
Scenario B — The "Bad Agent"

This is the messy monolithic agent you receive at the start of a refactoring exercise.
It works, but it has every architecture sin that a senior AI engineer should immediately flag.

Your job before touching the keyboard:
  1. Read it and name what's wrong
  2. Draw the stage boundaries
  3. Refactor into `good_pipeline.py`

Do NOT start coding immediately. Spend 3-4 minutes narrating the problems.
See `REFACTOR_NOTES.md` for the analysis.

Run:
    python3 bad_agent.py
"""

import json
import time
import random


# ──────────────────────────────────────────────────────────────────────────────
# THIS IS THE BAD CODE. Read it. Name what's wrong. Then fix it in good_pipeline.py
# ──────────────────────────────────────────────────────────────────────────────

def categorize_and_book_transaction(merchant: str, amount: float, description: str, is_b2b: bool = False):
    """
    AI-powered categorization and booking.
    Takes a transaction and returns a booking entry.
    """

    # Step 1: Call AI to categorize
    # In production this would be: response = openai.chat.completions.create(...)
    # The model is also doing VAT calculation in the same prompt (BAD)
    def fake_ai_call(merchant, amount, description, is_b2b):
        time.sleep(0.01)  # simulate latency

        # The AI is doing category AND VAT AND booking in one shot
        # Policy (VAT rates, account codes) is baked into the prompt instructions
        # No confidence score returned
        # No separation of concerns
        merchant_lower = merchant.lower()
        if "aws" in merchant_lower or "amazon" in merchant_lower:
            # 19% VAT hardcoded in the function body instead of a config
            vat = round(amount * 0.19 / 1.19, 2)
            return {"category": "IT_COSTS", "account": "4940", "vat": vat, "mechanism": "standard"}
        elif "lieferando" in merchant_lower or "uber eats" in merchant_lower:
            vat = round(amount * 0.07 / 1.07, 2)
            return {"category": "MEALS", "account": "4650", "vat": vat, "mechanism": "reduced"}
        elif "uber" in merchant_lower:
            vat = round(amount * 0.07 / 1.07, 2)
            return {"category": "TRAVEL", "account": "4670", "vat": vat, "mechanism": "reduced"}
        else:
            # No confidence score — caller has no way to know this is uncertain
            vat = round(amount * 0.19 / 1.19, 2)
            return {"category": "MISC", "account": "4990", "vat": vat, "mechanism": "standard"}

    result = fake_ai_call(merchant, amount, description, is_b2b)

    # Step 2: Handle B2B / reverse charge
    # This compliance rule is buried after the AI call, not before routing
    # Also: it silently overwrites the category without logging why
    if is_b2b:
        result["mechanism"] = "reverse_charge"
        result["vat"] = 0.0

    # Step 3: "Confidence check" — but it's random, not calibrated
    # There's no per-field confidence, no threshold, no proposal mode
    confidence = random.uniform(0.5, 1.0)  # THIS IS WRONG — confidence should come from the model
    if confidence < 0.6:
        print(f"WARNING: low confidence {confidence:.2f} for {merchant} — but booking anyway")
        # It just warns and continues! No escalation, no human review queue.

    # Step 4: Create booking — but this is all mixed together in one return value
    # No typed output, no trace, no stage separation
    booking = {
        "debit": result["account"],
        "credit": "1200",
        "net": round(amount - result["vat"], 2),
        "vat": result["vat"],
        "vorsteuer_account": "1576",
        "mechanism": result["mechanism"],
        # No audit trail — we don't know what confidence was, what the AI returned,
        # or why this ended up as booked vs proposed vs rejected
    }

    # Step 5: No terminal state tracking
    # This function always returns a booking entry — there's no "requires_review" state,
    # no "rejected" state, no way for downstream systems to know what happened
    return booking


if __name__ == "__main__":
    transactions = [
        ("AWS", 119.0, "EC2 instance", False),
        ("Lieferando", 35.70, "team lunch", False),
        ("Acme Consulting", 5000.0, "advisory", True),
        ("Unknown Corp", 299.0, "mystery charge", False),
    ]

    for merchant, amount, desc, b2b in transactions:
        result = categorize_and_book_transaction(merchant, amount, desc, b2b)
        print(f"{merchant}: {result}")
