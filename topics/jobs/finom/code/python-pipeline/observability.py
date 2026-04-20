"""
Pipeline Observability — Span Tracing & Production Metrics

Demonstrates OpenTelemetry-style instrumentation for the categorization pipeline:

  1. Trace context: correlation ID threads through all stages for a transaction
  2. Span per stage: start time, end time, duration, status, metadata
  3. Nested spans: batch → transaction → stage (parent/child hierarchy)
  4. Error recording: exceptions captured in span, not swallowed
  5. Aggregate metrics: P50/P95/P99 latency, error rate, throughput per stage

Why observability matters for financial AI:
  - "Categorization is slow" is not actionable; "categorize P99 = 2.8s for FR market" is
  - Debugging a wrong booking requires knowing which prompt version, confidence score,
    and retrieval result were active — all in the span metadata
  - Compliance asks "what happened to transaction tx-12345?" — the trace answers it
  - Stage latency trends reveal model API degradation before users complain

Run:
    python3 observability.py
"""

import time
import random
import math
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from pipeline import (
    Transaction, CategoryProposal, VatCalculation, WorkflowOutcome,
    RoutingStatus, categorize, calculate_vat, route, create_booking, StageTrace,
    MERCHANT_PATTERNS,
)


# ─────────────────────────────────────────
# Span model (OpenTelemetry-aligned)
# ─────────────────────────────────────────

class SpanStatus(Enum):
    OK    = "ok"
    ERROR = "error"


@dataclass
class Span:
    trace_id: str         # shared across all spans for one transaction
    span_id: str          # unique per span
    parent_span_id: Optional[str]
    name: str             # stage name: "categorize", "vat", "route", "booking"
    start_ns: int         # monotonic nanoseconds
    end_ns: int = 0
    status: SpanStatus = SpanStatus.OK
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)

    @property
    def duration_ms(self) -> float:
        return (self.end_ns - self.start_ns) / 1_000_000

    def finish(self, status: SpanStatus = SpanStatus.OK) -> None:
        self.end_ns = time.monotonic_ns()
        self.status = status

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def add_event(self, name: str, **kwargs) -> None:
        self.events.append({"name": name, "ts_ns": time.monotonic_ns(), **kwargs})

    def record_exception(self, exc: Exception) -> None:
        self.status = SpanStatus.ERROR
        self.add_event("exception", type=type(exc).__name__, message=str(exc))


# ─────────────────────────────────────────
# Tracer
# ─────────────────────────────────────────

class Tracer:
    """
    Lightweight in-process tracer. In production: export spans to Jaeger, Datadog, or OTLP.
    """
    def __init__(self) -> None:
        self._spans: list[Span] = []

    def start_span(
        self,
        name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
    ) -> Span:
        span = Span(
            trace_id=trace_id or uuid.uuid4().hex[:16],
            span_id=uuid.uuid4().hex[:8],
            parent_span_id=parent_span_id,
            name=name,
            start_ns=time.monotonic_ns(),
        )
        self._spans.append(span)
        return span

    def all_spans(self) -> list[Span]:
        return list(self._spans)

    def spans_for_trace(self, trace_id: str) -> list[Span]:
        return [s for s in self._spans if s.trace_id == trace_id]


# ─────────────────────────────────────────
# Instrumented pipeline
# Each stage starts/finishes a span; attributes capture business context
# ─────────────────────────────────────────

def instrumented_categorize(
    tx: Transaction,
    tracer: Tracer,
    trace_id: str,
    parent_span_id: str,
) -> CategoryProposal:
    span = tracer.start_span("categorize", trace_id=trace_id, parent_span_id=parent_span_id)
    span.set_attribute("tx.merchant", tx.merchant)
    span.set_attribute("tx.market", tx.market)
    span.set_attribute("tx.amount", tx.amount)
    span.set_attribute("tx.is_b2b", tx.is_b2b)
    try:
        proposal = categorize(tx)
        span.set_attribute("result.account_code", proposal.account_code)
        span.set_attribute("result.confidence", proposal.confidence)
        span.finish(SpanStatus.OK)
        return proposal
    except Exception as exc:
        span.record_exception(exc)
        span.finish(SpanStatus.ERROR)
        raise


def instrumented_vat(
    category: CategoryProposal,
    tx: Transaction,
    tracer: Tracer,
    trace_id: str,
    parent_span_id: str,
) -> VatCalculation:
    span = tracer.start_span("vat", trace_id=trace_id, parent_span_id=parent_span_id)
    span.set_attribute("tx.market", tx.market)
    span.set_attribute("tx.is_b2b", tx.is_b2b)
    try:
        vat = calculate_vat(category, tx)
        span.set_attribute("result.mechanism", vat.mechanism)
        span.set_attribute("result.rate", vat.rate)
        span.set_attribute("result.vat_amount", vat.amount)
        span.finish(SpanStatus.OK)
        return vat
    except Exception as exc:
        span.record_exception(exc)
        span.finish(SpanStatus.ERROR)
        raise


def instrumented_pipeline(tx: Transaction, tracer: Tracer) -> WorkflowOutcome:
    """
    Full instrumented pipeline: each stage creates a child span under the transaction span.
    The transaction span is the root; its trace_id links all stages.
    """
    trace_id = uuid.uuid4().hex[:16]
    tx_span = tracer.start_span(f"transaction.{tx.id}", trace_id=trace_id)
    tx_span.set_attribute("tx.id", tx.id)
    tx_span.set_attribute("tx.market", tx.market)

    try:
        category = instrumented_categorize(tx, tracer, trace_id, tx_span.span_id)
        vat      = instrumented_vat(category, tx, tracer, trace_id, tx_span.span_id)

        route_span = tracer.start_span("route", trace_id=trace_id, parent_span_id=tx_span.span_id)
        status = route(category, vat)
        route_span.set_attribute("result.status", status.value)
        route_span.finish()

        booking = None
        if status == RoutingStatus.AUTO_BOOKED:
            book_span = tracer.start_span("booking", trace_id=trace_id, parent_span_id=tx_span.span_id)
            booking = create_booking(category, vat, tx)
            book_span.set_attribute("result.debit", booking.debit_account)
            book_span.set_attribute("result.net", booking.net_amount)
            book_span.finish()

        tx_span.set_attribute("result.status", status.value)
        tx_span.finish(SpanStatus.OK)

        trace = [StageTrace(stage=s.name, duration_ms=round(s.duration_ms), decision="")
                 for s in tracer.spans_for_trace(trace_id) if s.name != f"transaction.{tx.id}"]
        return WorkflowOutcome(
            transaction_id=tx.id, status=status,
            category=category, vat=vat, booking=booking, trace=trace,
        )
    except Exception as exc:
        tx_span.record_exception(exc)
        tx_span.finish(SpanStatus.ERROR)
        raise


# ─────────────────────────────────────────
# Aggregate metrics (P50/P95/P99 per stage)
# ─────────────────────────────────────────

def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * p / 100
    f = int(k)
    c = f + 1
    if c >= len(sorted_vals):
        return sorted_vals[-1]
    return sorted_vals[f] + (k - f) * (sorted_vals[c] - sorted_vals[f])


@dataclass
class StageMetrics:
    name: str
    count: int
    error_count: int
    durations_ms: list[float] = field(default_factory=list)

    @property
    def error_rate(self) -> float:
        return self.error_count / self.count if self.count > 0 else 0.0

    @property
    def p50(self) -> float: return percentile(self.durations_ms, 50)
    @property
    def p95(self) -> float: return percentile(self.durations_ms, 95)
    @property
    def p99(self) -> float: return percentile(self.durations_ms, 99)


def compute_metrics(spans: list[Span]) -> dict[str, StageMetrics]:
    metrics: dict[str, StageMetrics] = {}
    for span in spans:
        if span.name.startswith("transaction."):
            continue
        if span.name not in metrics:
            metrics[span.name] = StageMetrics(name=span.name, count=0, error_count=0)
        m = metrics[span.name]
        m.count += 1
        if span.status == SpanStatus.ERROR:
            m.error_count += 1
        if span.end_ns > 0:
            m.durations_ms.append(span.duration_ms)
    return metrics


# ─────────────────────────────────────────
# Simulate a batch with realistic latency variation
# ─────────────────────────────────────────

def simulate_latency(stage: str, rng: random.Random, market: str) -> None:
    """Add realistic stage latency with market variation."""
    base = {"categorize": 0.08, "vat": 0.001, "route": 0.0005, "booking": 0.002}
    # FR market has higher LLM latency (different routing in mock)
    multiplier = 1.3 if market == "FR" else 1.0
    delay = base.get(stage, 0.001) * multiplier * rng.uniform(0.5, 2.0)
    time.sleep(delay)


TEST_TRANSACTIONS = [
    Transaction(id="o01", merchant="AWS EMEA",      amount=119.0, description="EC2",     market="DE"),
    Transaction(id="o02", merchant="Lieferando",    amount=47.80, description="lunch",   market="DE"),
    Transaction(id="o03", merchant="Acme Ltd",      amount=5000.0,description="advisory",is_b2b=True, market="DE"),
    Transaction(id="o04", merchant="AWS EMEA",      amount=95.0,  description="S3",      market="FR"),
    Transaction(id="o05", merchant="Uber",          amount=34.50, description="airport", market="FR"),
    Transaction(id="o06", merchant="Unknown GmbH",  amount=40.0,  description="misc",    market="DE"),
]


if __name__ == "__main__":
    rng = random.Random(42)
    tracer = Tracer()

    print("\n══ Pipeline Observability Demo ══\n")
    print("  Demonstrates: span-per-stage tracing with business context attributes\n")

    outcomes = []
    for tx in TEST_TRANSACTIONS:
        outcome = instrumented_pipeline(tx, tracer)
        outcomes.append(outcome)

    # Print trace for first transaction
    first_trace_id = tracer.all_spans()[0].trace_id
    trace_spans = tracer.spans_for_trace(first_trace_id)

    print(f"  ── Trace: {TEST_TRANSACTIONS[0].id} (trace_id={first_trace_id}) ─────────────────")
    for span in trace_spans:
        indent = "    " if span.parent_span_id else "  "
        status_icon = "✓" if span.status == SpanStatus.OK else "✗"
        attrs_str = ", ".join(f"{k}={v}" for k, v in list(span.attributes.items())[:3])
        print(f"  {indent}{status_icon} [{span.duration_ms:5.2f}ms] {span.name:<20} {attrs_str}")

    # Aggregate metrics
    all_spans = tracer.all_spans()
    metrics = compute_metrics(all_spans)

    print(f"\n  ── Stage metrics ({len(TEST_TRANSACTIONS)} transactions) ────────────────────────")
    print(f"  {'Stage':<12} {'Count':<8} {'Errors':<8} {'P50':<10} {'P95':<10} {'P99':<10} {'Error rate'}")
    for stage_name, m in sorted(metrics.items()):
        err_icon = "⚠" if m.error_rate > 0.05 else " "
        print(f"  {err_icon}{m.name:<11} {m.count:<8} {m.error_count:<8} "
              f"{m.p50:.2f}ms    {m.p95:.2f}ms    {m.p99:.2f}ms    {m.error_rate:.0%}")

    print(f"\n  ── Final statuses ─────────────────────────────────────")
    for tx, outcome in zip(TEST_TRANSACTIONS, outcomes):
        icons = {RoutingStatus.AUTO_BOOKED: "✓", RoutingStatus.PROPOSAL_SENT: "→",
                 RoutingStatus.REQUIRES_REVIEW: "⚠", RoutingStatus.REJECTED: "✗"}
        print(f"  {icons.get(outcome.status, '?')} {tx.id} [{tx.market}] {tx.merchant:<20} → {outcome.status.value}")

    print(f"\n  ── What spans enable ──────────────────────────────────")
    print(f"  Query: 'all transactions where categorize > 200ms' → find slow merchants")
    print(f"  Query: 'all spans where confidence < 0.6' → audit low-confidence auto-books")
    print(f"  Query: 'trace for tx-12345' → full decision audit for a booked transaction")
    print(f"  Alert: P99 categorize > 2s → LLM provider degradation")
    print(f"  Alert: error_rate > 5% → prompt/model regression")
    print(f"\n  ── Production export ──────────────────────────────────")
    print(f"  Replace Tracer with opentelemetry-sdk → export to Jaeger/Datadog")
    print(f"  Each span: trace_id links to the booking record in the database")
    print(f"  Compliance: trace_id stored on BookingEntry → full audit chain")
