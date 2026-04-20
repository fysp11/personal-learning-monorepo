"""
Production Resilience Patterns for Financial AI Workflows

Demonstrates the reliability patterns any production AI pipeline needs.
Each pattern prevents a named failure mode:

  CircuitBreaker        → FM-14: Escalation Storm (review queue flood)
  IdempotencyRegistry   → FM-16: Stage Leak (double-booking on retry)
  RetryWithBackoff      → FM-12: Transient API failures corrupting pipeline state
  LifecycleRegistry     → FM-15: Silent Reject (ingested but never terminal)
  BatchAnomalyDetector  → FM-04: Confidence Inflation (confidence drift early warning)

Interview framing:
  "The pipeline isn't reliable because the model is good.
   It's reliable because each failure mode has a named control."

Run:
    python3 resilience_patterns.py
"""

import time
import hashlib
import json
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any, Callable


# ─────────────────────────────────────────
# Shared types
# ─────────────────────────────────────────

class TransactionState(str, Enum):
    INGESTED = "ingested"
    EXTRACTING = "extracting"
    CATEGORIZING = "categorizing"
    VAT_CALCULATED = "vat_calculated"
    ROUTING = "routing"
    AUTO_BOOKED = "auto_booked"
    PROPOSAL_SENT = "proposal_sent"
    REJECTED = "rejected"
    ERROR_LOGGED = "error_logged"

TERMINAL_STATES = {
    TransactionState.AUTO_BOOKED,
    TransactionState.PROPOSAL_SENT,
    TransactionState.REJECTED,
    TransactionState.ERROR_LOGGED,
}


# ─────────────────────────────────────────
# Pattern 1: LifecycleRegistry — FM-15: Silent Reject
#
# Every transaction must reach a terminal state within SLA.
# A transaction that was ingested but never terminates is a silent reject:
# the customer sees a missing booking entry, no error, no notification.
# ─────────────────────────────────────────

@dataclass
class LifecycleRecord:
    state: TransactionState
    updated_at: float   # monotonic timestamp
    trace: list[str] = field(default_factory=list)


class LifecycleRegistry:
    """
    Tracks every transaction from ingest to terminal state.
    A reconciliation job calls find_stranded() to detect FM-15.
    """

    def __init__(self) -> None:
        self._registry: dict[str, LifecycleRecord] = {}

    def ingest(self, tx_id: str) -> None:
        self._registry[tx_id] = LifecycleRecord(
            state=TransactionState.INGESTED,
            updated_at=time.monotonic(),
        )

    def transition(self, tx_id: str, new_state: TransactionState, note: str = "") -> None:
        record = self._registry.get(tx_id)
        if not record:
            raise KeyError(f"unknown transaction: {tx_id}")
        record.state = new_state
        record.updated_at = time.monotonic()
        if note:
            record.trace.append(note)

    def is_terminal(self, tx_id: str) -> bool:
        record = self._registry.get(tx_id)
        return record is not None and record.state in TERMINAL_STATES

    def find_stranded(self, sla_seconds: float = 30.0) -> list[str]:
        """
        Returns IDs of transactions not yet terminal past the SLA window.
        Call this in a scheduled reconciliation job (e.g., every 5 minutes).
        """
        now = time.monotonic()
        return [
            tx_id
            for tx_id, rec in self._registry.items()
            if rec.state not in TERMINAL_STATES
            and (now - rec.updated_at) > sla_seconds
        ]

    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for rec in self._registry.values():
            counts[rec.state] = counts.get(rec.state, 0) + 1
        return counts


# ─────────────────────────────────────────
# Pattern 2: IdempotencyRegistry — FM-16: Stage Leak
#
# Before running any stage, check if (tx_id, stage, input_hash) already ran.
# If yes: return the cached result. Don't re-run the LLM call.
#
# Critical for: retry logic, at-least-once delivery queues,
# and preventing double ELSTER submissions (FM-18).
# ─────────────────────────────────────────

class IdempotencyRegistry:
    """
    Content-addressable result cache keyed on (tx_id, stage_name, sha256(input)).
    In production: back this with Redis or a Postgres table with TTL.
    """

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}
        self.hit_count = 0
        self.miss_count = 0

    def _key(self, tx_id: str, stage: str, input_data: Any) -> str:
        payload = json.dumps({"tx_id": tx_id, "stage": stage, "input": input_data}, sort_keys=True)
        digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
        return f"{tx_id}:{stage}:{digest}"

    def get(self, tx_id: str, stage: str, input_data: Any) -> tuple[bool, Any]:
        """Returns (is_cached, result). On miss, call record() after executing."""
        key = self._key(tx_id, stage, input_data)
        if key in self._store:
            self.hit_count += 1
            return True, self._store[key]
        self.miss_count += 1
        return False, None

    def record(self, tx_id: str, stage: str, input_data: Any, result: Any) -> None:
        key = self._key(tx_id, stage, input_data)
        self._store[key] = result


# ─────────────────────────────────────────
# Pattern 3: RetryWithBackoff — FM-12: Transient failures
#
# LLM API calls fail transiently. A naive retry immediately hammers
# the provider and makes rate limiting worse.
# Exponential backoff with jitter is the production pattern.
# ─────────────────────────────────────────

class TransientError(Exception):
    """Raised when an operation should be retried."""


def retry_with_backoff(
    fn: Callable[[], Any],
    max_attempts: int = 3,
    base_delay_s: float = 0.1,
    max_delay_s: float = 2.0,
    jitter: bool = True,
) -> Any:
    """
    Retries fn() up to max_attempts times on TransientError.
    Delay doubles each attempt; jitter prevents thundering herd.

    Interview point: "I use jitter because without it, all retrying
    clients synchronize on the same backoff interval — that's a thundering
    herd problem that makes recovery slower, not faster."
    """
    rng = random.Random()
    for attempt in range(max_attempts):
        try:
            return fn()
        except TransientError as exc:
            if attempt == max_attempts - 1:
                raise
            delay = min(base_delay_s * (2 ** attempt), max_delay_s)
            if jitter:
                delay *= (0.5 + rng.random() * 0.5)
            print(f"    [retry] attempt {attempt + 1} failed ({exc}). retrying in {delay:.3f}s")
            time.sleep(delay)


# ─────────────────────────────────────────
# Pattern 4: CircuitBreaker — FM-14: Escalation Storm
#
# If confidence drops below threshold for too many transactions in a row,
# open the circuit: stop auto-booking the whole batch, not just individual items.
#
# Financial AI variant: the circuit trips on LOW CONFIDENCE RATE,
# not just error rate. A stream of 0.60-confidence categorizations
# would pass individual threshold checks but signal a model problem.
#
# States: CLOSED (normal) → OPEN (tripped) → HALF_OPEN (probing)
# ─────────────────────────────────────────

class CircuitState(str, Enum):
    CLOSED = "CLOSED"       # normal operation
    OPEN = "OPEN"           # tripped — reject all requests
    HALF_OPEN = "HALF_OPEN" # probing — let one through


@dataclass
class CircuitBreakerConfig:
    name: str
    failure_threshold_pct: float = 0.30  # trip if >30% of window are failures
    window_size: int = 20                # rolling window of N calls
    recovery_s: float = 10.0            # seconds before probing after OPEN
    # Financial AI extension: confidence-based tripping
    min_confidence_threshold: float = 0.70  # trip if avg confidence < this
    confidence_window: int = 10              # rolling window for confidence check


class CircuitBreaker:
    """
    Prevents FM-14: review queue flood from a degraded model.
    Trips when: error rate > threshold OR avg confidence < min_confidence.
    """

    def __init__(self, config: CircuitBreakerConfig) -> None:
        self.config = config
        self.state = CircuitState.CLOSED
        self._results: list[bool] = []        # True = success
        self._confidences: list[float] = []
        self._opened_at: Optional[float] = None

    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            elapsed = time.monotonic() - (self._opened_at or 0)
            if elapsed > self.config.recovery_s:
                self.state = CircuitState.HALF_OPEN
                print(f"    [circuit:{self.config.name}] → HALF_OPEN (probing after {elapsed:.1f}s)")
                return True
            return False
        # HALF_OPEN: let one through
        return True

    def record(self, success: bool, confidence: Optional[float] = None) -> None:
        self._results = (self._results + [success])[-self.config.window_size:]
        if confidence is not None:
            self._confidences = (self._confidences + [confidence])[-self.config.confidence_window:]

        if self.state == CircuitState.HALF_OPEN:
            if success:
                self.state = CircuitState.CLOSED
                print(f"    [circuit:{self.config.name}] probe succeeded → CLOSED")
            else:
                self.state = CircuitState.OPEN
                self._opened_at = time.monotonic()
                print(f"    [circuit:{self.config.name}] probe failed → OPEN again")
            return

        # Check error rate in window
        if len(self._results) >= self.config.window_size:
            fail_rate = self._results.count(False) / len(self._results)
            if fail_rate > self.config.failure_threshold_pct:
                self._trip(f"error rate {fail_rate:.0%} > {self.config.failure_threshold_pct:.0%}")
                return

        # Check confidence in window (financial AI extension)
        if len(self._confidences) >= self.config.confidence_window:
            avg_conf = sum(self._confidences) / len(self._confidences)
            if avg_conf < self.config.min_confidence_threshold:
                self._trip(f"avg confidence {avg_conf:.2f} < {self.config.min_confidence_threshold:.2f}")

    def _trip(self, reason: str) -> None:
        self.state = CircuitState.OPEN
        self._opened_at = time.monotonic()
        print(f"    [circuit:{self.config.name}] OPEN — {reason}")


# ─────────────────────────────────────────
# Pattern 5: BatchAnomalyDetector — FM-04: Confidence Inflation
#
# Compares the current batch's confidence distribution against a rolling
# 30-day baseline. A significant drop in P50 is the leading indicator
# of model degradation — detected before accuracy metrics degrade.
# ─────────────────────────────────────────

@dataclass
class BatchHealthSummary:
    batch_id: str
    count: int
    p50_confidence: float
    p90_confidence: float
    baseline_p50: float
    delta_p50: float
    auto_book_rate: float
    alert_fired: bool
    alert_reason: str = ""


def detect_confidence_anomaly(
    confidences: list[float],
    batch_id: str,
    baseline_p50: float = 0.85,
    alert_threshold_delta: float = 0.08,
) -> BatchHealthSummary:
    """
    FM-04 prevention: alert if batch P50 drops more than threshold below baseline.
    This is the leading indicator — fires before accuracy metrics degrade.
    """
    sorted_confs = sorted(confidences)
    n = len(sorted_confs)
    p50 = sorted_confs[n // 2] if n else 0.0
    p90 = sorted_confs[int(n * 0.9)] if n else 0.0
    delta = p50 - baseline_p50
    auto_book_rate = sum(1 for c in confidences if c >= 0.85) / n if n else 0.0

    alert = delta < -alert_threshold_delta
    reason = f"P50 dropped {abs(delta):.3f} below baseline" if alert else ""

    return BatchHealthSummary(
        batch_id=batch_id,
        count=n,
        p50_confidence=round(p50, 3),
        p90_confidence=round(p90, 3),
        baseline_p50=baseline_p50,
        delta_p50=round(delta, 3),
        auto_book_rate=round(auto_book_rate, 3),
        alert_fired=alert,
        alert_reason=reason,
    )


# ─────────────────────────────────────────
# Demo: run all patterns together
# ─────────────────────────────────────────

def run_demo() -> None:
    print("\n══════════════════════════════════════════════════════════")
    print("  Production Resilience Patterns — Demo")
    print("══════════════════════════════════════════════════════════\n")

    # ── Pattern 1: LifecycleRegistry ──
    print("  [1] LifecycleRegistry — FM-15: Silent Reject Prevention")
    registry = LifecycleRegistry()
    for tx_id in ["tx-001", "tx-002", "tx-003"]:
        registry.ingest(tx_id)

    registry.transition("tx-001", TransactionState.CATEGORIZING, "started categorization")
    registry.transition("tx-001", TransactionState.AUTO_BOOKED, "confidence=0.92")
    registry.transition("tx-002", TransactionState.CATEGORIZING)
    # tx-003 is never updated — simulates a crash after ingest (silent reject scenario)
    # Pretend 35 seconds have passed for demonstration
    registry._registry["tx-003"].updated_at = time.monotonic() - 35

    stranded = registry.find_stranded(sla_seconds=30.0)
    print(f"  Summary: {registry.summary()}")
    print(f"  Stranded transactions (>30s, non-terminal): {stranded}")
    print(f"  → Alert: tx-003 would fire a PagerDuty/Slack notification\n")

    # ── Pattern 2: IdempotencyRegistry ──
    print("  [2] IdempotencyRegistry — FM-16: Stage Leak Prevention")
    idempotency = IdempotencyRegistry()
    stage_input = {"merchant": "AWS", "amount": 119.0}

    is_cached, _ = idempotency.get("tx-004", "categorize", stage_input)
    if not is_cached:
        # Simulate the expensive LLM call
        result = {"account_code": "4940", "confidence": 0.95}
        idempotency.record("tx-004", "categorize", stage_input, result)
        print(f"  Miss → executed stage, cached result: {result}")

    # Simulate retry (e.g., the batch job restarted after a crash)
    is_cached, cached_result = idempotency.get("tx-004", "categorize", stage_input)
    print(f"  Retry → cache HIT: {cached_result} (LLM call skipped)")
    print(f"  Idempotency stats: {idempotency.hit_count} hits, {idempotency.miss_count} misses\n")

    # ── Pattern 3: RetryWithBackoff ──
    print("  [3] RetryWithBackoff — FM-12: Transient Failure Recovery")
    attempts = {"count": 0}

    def flaky_llm_call():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise TransientError(f"rate limited (attempt {attempts['count']})")
        return {"account_code": "4670", "confidence": 0.88}

    result = retry_with_backoff(flaky_llm_call, max_attempts=4, base_delay_s=0.01)
    print(f"  Succeeded after {attempts['count']} attempts: {result}\n")

    # ── Pattern 4: CircuitBreaker ──
    print("  [4] CircuitBreaker — FM-14: Escalation Storm Prevention")
    cb = CircuitBreaker(CircuitBreakerConfig(
        name="categorizer",
        failure_threshold_pct=0.40,
        window_size=10,
        recovery_s=0.1,  # short for demo
        min_confidence_threshold=0.70,
        confidence_window=5,
    ))

    print("  Normal operation (8 successes):")
    for _ in range(8):
        if cb.can_execute():
            cb.record(success=True, confidence=0.88)

    print("  Model degrades — confidence drops below threshold:")
    for _ in range(5):
        if cb.can_execute():
            cb.record(success=True, confidence=0.62)  # low confidence triggers trip

    print(f"  Circuit state: {cb.state}")
    print(f"  can_execute(): {cb.can_execute()}  ← False means batch is protected\n")

    # ── Pattern 5: BatchAnomalyDetector ──
    print("  [5] BatchAnomalyDetector — FM-04: Confidence Inflation Early Warning")

    # Normal batch
    normal_confidences = [random.uniform(0.82, 0.96) for _ in range(50)]
    normal_summary = detect_confidence_anomaly(normal_confidences, "batch-001", baseline_p50=0.85)
    status = "⚠ ALERT" if normal_summary.alert_fired else "✓ healthy"
    print(f"  Normal batch:   P50={normal_summary.p50_confidence:.3f}  Δ={normal_summary.delta_p50:+.3f}  {status}")

    # Degraded batch (confidence inflation reversed — model got worse)
    degraded_confidences = [random.uniform(0.60, 0.78) for _ in range(50)]
    degraded_summary = detect_confidence_anomaly(degraded_confidences, "batch-002", baseline_p50=0.85)
    status = "⚠ ALERT" if degraded_summary.alert_fired else "✓ healthy"
    print(f"  Degraded batch: P50={degraded_summary.p50_confidence:.3f}  Δ={degraded_summary.delta_p50:+.3f}  {status}")
    if degraded_summary.alert_fired:
        print(f"  → Alert reason: {degraded_summary.alert_reason}")
        print(f"  → Action: pause auto-book, notify on-call, keep proposals flowing")

    print("\n  ── Interview framing ───────────────────────────────────")
    print("  The pipeline isn't reliable because the model is good.")
    print("  It's reliable because each failure mode has a named control.")
    print("    FM-15 → LifecycleRegistry (stranded detection)")
    print("    FM-16 → IdempotencyRegistry (no double-booking)")
    print("    FM-12 → RetryWithBackoff (transient recovery)")
    print("    FM-14 → CircuitBreaker (queue protection)")
    print("    FM-04 → BatchAnomalyDetector (leading indicator)\n")


if __name__ == "__main__":
    run_demo()
