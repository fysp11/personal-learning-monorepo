"""
Structured Output Parsing — LLM JSON Reliability Patterns

A common live-round scenario: "the LLM doesn't always return valid JSON — how do you handle it?"

This demo shows the full reliability stack for structured LLM output in production:

  1. Strict parse:   JSON.loads() → validate schema → done (happy path, ~85% of calls)
  2. Repair:         fix common LLM JSON errors (trailing commas, unquoted keys, etc.)
  3. Regex fallback: extract fields from freeform text when JSON is absent
  4. Retry with prompt fix: re-prompt with explicit format reminder
  5. Partial extraction: take what's recoverable, flag the rest for manual review
  6. Schema validation: required fields, type checking, value range enforcement

Why this matters for financial AI:
  - A malformed response that gets swallowed silently → wrong booking, no error
  - "Just retry" without parsing the error → burns tokens, same failure
  - The schema is the contract; partial compliance is not compliance

Run:
    python3 structured_output.py
"""

import json
import re
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ─────────────────────────────────────────
# Target schema
# What the LLM is supposed to return
# ─────────────────────────────────────────

@dataclass
class ParsedCategoryOutput:
    account_code: str        # e.g. "4940"
    confidence: float        # 0.0 – 1.0
    evidence: str            # human-readable reasoning
    requires_review: bool    # compliance flag

    def validate(self) -> list[str]:
        """Returns list of validation errors (empty = valid)."""
        errors = []
        if not re.match(r"^\d{4,5}$", self.account_code):
            errors.append(f"account_code '{self.account_code}' must be 4-5 digit string")
        if not (0.0 <= self.confidence <= 1.0):
            errors.append(f"confidence {self.confidence} out of range [0, 1]")
        if not self.evidence:
            errors.append("evidence must not be empty")
        return errors


class ParseOutcome(Enum):
    STRICT      = "strict"       # clean JSON, schema valid
    REPAIRED    = "repaired"     # JSON fixed, schema valid after repair
    REGEX       = "regex"        # extracted from freeform text
    PARTIAL     = "partial"      # some fields missing; confidence set to 0
    FAILED      = "failed"       # nothing recoverable; route to manual


@dataclass
class ParseResult:
    outcome: ParseOutcome
    output: Optional[ParsedCategoryOutput]
    raw_response: str
    parse_attempts: int = 1
    errors: list[str] = field(default_factory=list)
    repair_applied: Optional[str] = None


# ─────────────────────────────────────────
# Stage 1: Strict JSON parse + schema validation
# ─────────────────────────────────────────

REQUIRED_FIELDS = {"account_code", "confidence", "evidence", "requires_review"}

def try_strict_parse(raw: str) -> Optional[ParsedCategoryOutput]:
    """Parse and validate; return None if anything is wrong."""
    try:
        data = json.loads(raw)
        missing = REQUIRED_FIELDS - set(data.keys())
        if missing:
            return None
        raw_conf = float(data["confidence"])
        # Normalize percentage confidence (LLMs sometimes return 90 instead of 0.90)
        confidence = raw_conf / 100.0 if raw_conf > 1.0 else raw_conf
        output = ParsedCategoryOutput(
            account_code=str(data["account_code"]),
            confidence=round(confidence, 4),
            evidence=str(data["evidence"]),
            requires_review=bool(data["requires_review"]),
        )
        if output.validate():
            return None
        return output
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


# ─────────────────────────────────────────
# Stage 2: JSON repair
# LLMs commonly produce: trailing commas, single quotes, unquoted keys,
# Python booleans (True/False), missing closing braces.
# ─────────────────────────────────────────

def repair_json(raw: str) -> tuple[str, str]:
    """
    Apply common LLM JSON fixes. Returns (repaired_string, repair_description).
    Does NOT guarantee valid JSON — try_strict_parse still needed after repair.
    """
    s = raw.strip()
    repairs: list[str] = []

    # Extract JSON object if buried in text
    match = re.search(r"\{[^{}]*\}", s, re.DOTALL)
    if match and match.group() != s:
        s = match.group()
        repairs.append("extracted JSON block from surrounding text")

    # Python booleans → JSON
    s_orig = s
    s = re.sub(r'\bTrue\b', 'true', s)
    s = re.sub(r'\bFalse\b', 'false', s)
    if s != s_orig:
        repairs.append("Python booleans → JSON booleans")

    # Single quotes → double quotes (careful: don't break possessives in strings)
    if "'" in s and '"' not in s:
        s = s.replace("'", '"')
        repairs.append("single → double quotes")

    # Trailing commas before } or ]
    s_orig = s
    s = re.sub(r',\s*([}\]])', r'\1', s)
    if s != s_orig:
        repairs.append("removed trailing commas")

    # Unquoted keys: { key: value } → { "key": value }
    s_orig = s
    s = re.sub(r'(\{|,)\s*([a-zA-Z_]\w*)\s*:', r'\1 "\2":', s)
    if s != s_orig:
        repairs.append("quoted unquoted keys")

    return s, "; ".join(repairs) if repairs else "no repairs needed"


# ─────────────────────────────────────────
# Stage 3: Regex fallback
# When JSON is absent but fields are present in freeform text
# ─────────────────────────────────────────

ACCOUNT_CODE_RE = re.compile(r'\b(\d{4,5})\b')
CONFIDENCE_RE   = re.compile(r'confidence[:\s]+([0-9]+\.?[0-9]*)', re.IGNORECASE)
REVIEW_RE       = re.compile(r'(requires?\s*review|manual\s*review|flag)', re.IGNORECASE)
EVIDENCE_RE     = re.compile(r'(?:evidence|reason|because)[:\s]+([^\n.]+)', re.IGNORECASE)


def try_regex_extract(raw: str) -> Optional[ParsedCategoryOutput]:
    """Extract fields from freeform text when JSON is absent."""
    # Account code: first 4-5 digit sequence (likely to be an account code)
    account_matches = ACCOUNT_CODE_RE.findall(raw)
    if not account_matches:
        return None
    account_code = account_matches[0]

    # Confidence: numeric value near "confidence"
    conf_match = CONFIDENCE_RE.search(raw)
    confidence = float(conf_match.group(1)) if conf_match else 0.50

    # Clamp to [0, 1] — LLMs sometimes return percentages
    if confidence > 1.0:
        confidence = confidence / 100.0
    confidence = max(0.0, min(1.0, confidence))

    # Review flag
    requires_review = bool(REVIEW_RE.search(raw))

    # Evidence: text after "evidence:" or "reason:"
    ev_match = EVIDENCE_RE.search(raw)
    evidence = ev_match.group(1).strip() if ev_match else f"regex-extracted from: {raw[:50]}"

    return ParsedCategoryOutput(
        account_code=account_code,
        confidence=round(confidence, 3),
        evidence=evidence,
        requires_review=requires_review,
    )


# ─────────────────────────────────────────
# Full parsing pipeline
# ─────────────────────────────────────────

def parse_llm_response(
    raw: str,
    retry_fn: Optional[callable] = None,
) -> ParseResult:
    """
    Full parse with repair and regex fallback.
    retry_fn: if provided, called with a format hint prompt and returns a new raw response.
    """
    # Stage 1: strict
    output = try_strict_parse(raw)
    if output:
        return ParseResult(outcome=ParseOutcome.STRICT, output=output, raw_response=raw)

    # Stage 2: repair
    repaired, repair_desc = repair_json(raw)
    output = try_strict_parse(repaired)
    if output:
        return ParseResult(
            outcome=ParseOutcome.REPAIRED, output=output,
            raw_response=raw, repair_applied=repair_desc,
        )

    # Stage 3: retry with format hint
    if retry_fn:
        retried = retry_fn(raw)
        output = try_strict_parse(retried)
        if output:
            return ParseResult(
                outcome=ParseOutcome.REGEX, output=output,
                raw_response=raw, parse_attempts=2,
                repair_applied="retried with format hint prompt",
            )

    # Stage 4: regex fallback
    output = try_regex_extract(raw)
    if output and not output.validate():
        return ParseResult(
            outcome=ParseOutcome.REGEX, output=output,
            raw_response=raw, repair_applied="regex field extraction",
        )

    # Stage 5: partial extraction (confidence = 0 → will route to PROPOSAL or REVIEW)
    account_matches = ACCOUNT_CODE_RE.findall(raw)
    if account_matches:
        partial = ParsedCategoryOutput(
            account_code=account_matches[0],
            confidence=0.0,
            evidence=f"partial extraction — parse failed: {raw[:60]}",
            requires_review=True,
        )
        return ParseResult(
            outcome=ParseOutcome.PARTIAL, output=partial,
            raw_response=raw, errors=["full parse failed; confidence zeroed"],
        )

    return ParseResult(
        outcome=ParseOutcome.FAILED, output=None,
        raw_response=raw, errors=["no recoverable fields found"],
    )


# ─────────────────────────────────────────
# Simulated LLM responses — realistic failure modes
# ─────────────────────────────────────────

MOCK_RESPONSES = [
    # Happy path
    ('clean', '{"account_code": "4940", "confidence": 0.95, "evidence": "AWS → IT costs", "requires_review": false}'),
    # Python booleans
    ('python_bool', '{"account_code": "4650", "confidence": 0.82, "evidence": "Lieferando → meals", "requires_review": False}'),
    # Trailing comma
    ('trailing_comma', '{"account_code": "4670", "confidence": 0.90, "evidence": "Uber → travel", "requires_review": false,}'),
    # Unquoted keys
    ('unquoted_keys', '{account_code: "4920", confidence: 0.78, evidence: "Telekom → telecom", requires_review: false}'),
    # JSON buried in explanation
    ('buried_json', 'Based on the merchant, this is IT costs. The result is: {"account_code": "4940", "confidence": 0.88, "evidence": "cloud service", "requires_review": false}. Let me know if you need more.'),
    # Freeform text (no JSON)
    ('freeform', 'The account code should be 4940 for this AWS transaction. Confidence: 0.91. Evidence: cloud infrastructure costs. No review required.'),
    # Partial — only account code recoverable
    ('partial', 'I think this should go to account 6825 but I am not confident.'),
    # Complete failure
    ('failure', 'I cannot categorize this transaction without more context.'),
    # Percentage confidence
    ('pct_confidence', '{"account_code": "4670", "confidence": 90, "evidence": "travel expense", "requires_review": false}'),
]


if __name__ == "__main__":
    print("\n══ Structured Output Parsing Demo ══\n")
    print("  Reliability stack: strict → repair → retry → regex → partial → failed\n")

    outcomes_seen: dict[ParseOutcome, int] = {}

    print(f"  {'Case':<16} {'Outcome':<12} {'Acct':<6} {'Conf':<7} {'Attempts':<10} {'Repair'}")
    print(f"  {'─'*16} {'─'*12} {'─'*6} {'─'*7} {'─'*10} {'─'*30}")

    for case_name, raw in MOCK_RESPONSES:
        result = parse_llm_response(raw)
        outcomes_seen[result.outcome] = outcomes_seen.get(result.outcome, 0) + 1

        acct = result.output.account_code if result.output else "—"
        conf = f"{result.output.confidence:.2f}" if result.output else "—"
        repair = (result.repair_applied or "")[:32] if result.repair_applied else "—"
        print(f"  {case_name:<16} {result.outcome.value:<12} {acct:<6} {conf:<7} {result.parse_attempts:<10} {repair}")

    print(f"\n  ── Parse outcome distribution ───────────────────────")
    total = len(MOCK_RESPONSES)
    for outcome in ParseOutcome:
        count = outcomes_seen.get(outcome, 0)
        bar = "█" * count
        print(f"  {outcome.value:<12}: {count}/{total}  {bar}")

    print(f"\n  ── Routing implications ─────────────────────────────")
    print(f"  STRICT/REPAIRED/REGEX: confidence is meaningful → normal routing")
    print(f"  PARTIAL:               confidence = 0.0 → PROPOSAL_SENT at best")
    print(f"  FAILED:                no account code → REQUIRES_REVIEW (manual queue)")
    print(f"\n  ── Production hardening ─────────────────────────────")
    print(f"  1. Log all non-STRICT outcomes — high REPAIRED/REGEX rate = prompt regression")
    print(f"  2. Alert if FAILED rate > 2% — likely a model or prompt change broke output format")
    print(f"  3. Never swallow ParseErrors silently — they become silent wrong bookings")
    print(f"  4. Include output format in prompt: 'Respond ONLY with valid JSON: {{...}}'")
    print(f"  5. Use structured output API (OpenAI function calling / Anthropic tool use)")
    print(f"     when available — pushes schema enforcement to the API layer")
