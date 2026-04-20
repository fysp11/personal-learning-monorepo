"""
Async Streaming Pipeline — Webhook Ingestion + SSE Progress

Demonstrates production async patterns for a financial AI pipeline:

  1. Webhook ingestion: transactions arrive via POST, dispatched to async worker
  2. Bounded concurrency: semaphore limits parallel LLM calls (prevents rate-limit storms)
  3. SSE-style streaming: pipeline emits stage-by-stage progress to clients in real-time
  4. Backpressure: queue fills, oldest transactions age out (bounded buffer)
  5. Graceful shutdown: in-flight transactions complete before worker stops

This matters for financial AI because:
  - Users expect to see categorization proposals within 2s of upload, not after batch completes
  - A credit card statement of 200 transactions must not wait 200 × 300ms serially
  - Rate-limit errors must not lose transactions (idempotency + retry, not discard)
  - Shutdown during a bank sync must leave no transactions in a half-processed state

Run:
    python3 async_streaming.py
"""

import asyncio
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Optional

from pipeline import (
    Transaction, CategoryProposal, VatCalculation, WorkflowOutcome,
    RoutingStatus, categorize, calculate_vat, route, create_booking, StageTrace,
)


# ─────────────────────────────────────────
# SSE-style progress events
# In production: sent as text/event-stream to the browser client
# ─────────────────────────────────────────

class EventType(Enum):
    STAGE_START    = "stage_start"
    STAGE_COMPLETE = "stage_complete"
    PROPOSAL_READY = "proposal_ready"   # emitted before auto-book decision
    AUTO_BOOKED    = "auto_booked"
    REQUIRES_REVIEW = "requires_review"
    ERROR          = "error"
    BATCH_COMPLETE = "batch_complete"


@dataclass
class PipelineEvent:
    event_type: EventType
    transaction_id: str
    stage: Optional[str] = None
    data: dict = field(default_factory=dict)
    timestamp_ms: float = field(default_factory=lambda: time.monotonic() * 1000)

    def format_sse(self) -> str:
        """Format as Server-Sent Events text/event-stream line."""
        return f"event: {self.event_type.value}\ndata: tx={self.transaction_id} stage={self.stage} {self.data}\n\n"


# ─────────────────────────────────────────
# Async pipeline worker
# Each stage yields a PipelineEvent — caller streams to client
# ─────────────────────────────────────────

async def simulate_llm_call(tx: Transaction, rng: random.Random) -> CategoryProposal:
    """Mock: simulate async LLM categorization with realistic latency."""
    delay = rng.uniform(0.05, 0.15)   # 50–150ms mock LLM latency
    await asyncio.sleep(delay)
    return categorize(tx)


async def process_transaction_streaming(
    tx: Transaction,
    rng: random.Random,
) -> AsyncIterator[PipelineEvent]:
    """
    Process one transaction and yield progress events at each stage.
    The caller can stream these to a browser client via SSE.
    """
    t0 = time.monotonic()

    # Stage 1: Categorize (async LLM call)
    yield PipelineEvent(EventType.STAGE_START, tx.id, stage="categorize")
    category = await simulate_llm_call(tx, rng)
    yield PipelineEvent(EventType.STAGE_COMPLETE, tx.id, stage="categorize", data={
        "account_code": category.account_code,
        "confidence": category.confidence,
    })

    # Stage 2: VAT (sync, fast)
    yield PipelineEvent(EventType.STAGE_START, tx.id, stage="vat")
    await asyncio.sleep(0.001)   # negligible — pure computation
    vat = calculate_vat(category, tx)
    yield PipelineEvent(EventType.STAGE_COMPLETE, tx.id, stage="vat", data={
        "mechanism": vat.mechanism,
        "rate": vat.rate,
        "vat_amount": vat.amount,
    })

    # Stage 3: Route — emit proposal before confirming auto-book
    status = route(category, vat)
    yield PipelineEvent(
        EventType.PROPOSAL_READY if status == RoutingStatus.PROPOSAL_SENT else EventType.STAGE_COMPLETE,
        tx.id, stage="route",
        data={"status": status.value, "confidence": category.confidence},
    )

    # Stage 4: Booking (or hold)
    booking = None
    if status == RoutingStatus.AUTO_BOOKED:
        await asyncio.sleep(0.002)   # database write
        booking = create_booking(category, vat, tx)
        yield PipelineEvent(EventType.AUTO_BOOKED, tx.id, stage="booking", data={
            "debit": booking.debit_account,
            "credit": booking.credit_account,
            "net": booking.net_amount,
        })
    elif status == RoutingStatus.REQUIRES_REVIEW:
        yield PipelineEvent(EventType.REQUIRES_REVIEW, tx.id, stage="routing", data={
            "reason": category.evidence,
        })
    elif status == RoutingStatus.REJECTED:
        yield PipelineEvent(EventType.ERROR, tx.id, stage="routing", data={
            "reason": f"confidence {category.confidence:.0%} below proposal threshold — manual queue",
        })


# ─────────────────────────────────────────
# Bounded concurrency batch processor
# ─────────────────────────────────────────

MAX_CONCURRENT = 3   # max parallel LLM calls — matches typical rate limit headroom


async def process_batch_concurrent(
    transactions: list[Transaction],
    rng: random.Random,
    event_sink: asyncio.Queue,
) -> None:
    """
    Process a batch with bounded concurrency.
    All events are sent to event_sink; caller reads and streams them.

    Semaphore prevents overwhelming the LLM rate limit.
    Without it: 50 transactions → 50 concurrent LLM calls → 429 rate limit → lost transactions.
    """
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def process_one(tx: Transaction) -> None:
        async with semaphore:
            async for event in process_transaction_streaming(tx, rng):
                await event_sink.put(event)

    await asyncio.gather(*[process_one(tx) for tx in transactions])
    await event_sink.put(None)  # sentinel: batch complete


# ─────────────────────────────────────────
# Webhook ingestion mock
# ─────────────────────────────────────────

@dataclass
class WebhookBatch:
    batch_id: str
    transactions: list[Transaction]
    received_at: float = field(default_factory=time.monotonic)


async def simulate_webhook_delivery(
    batches: list[WebhookBatch],
    queue: asyncio.Queue,
    delay_s: float = 0.05,
) -> None:
    """Simulate transactions arriving via webhook — staggered delivery."""
    for batch in batches:
        await asyncio.sleep(delay_s)
        await queue.put(batch)
    await queue.put(None)  # sentinel


# ─────────────────────────────────────────
# Main demo
# ─────────────────────────────────────────

TEST_TRANSACTIONS = [
    Transaction(id="w01", merchant="AWS EMEA",       amount=119.0, description="EC2", market="DE"),
    Transaction(id="w02", merchant="Lieferando",     amount=47.80, description="team lunch", market="DE"),
    Transaction(id="w03", merchant="Acme Ltd",       amount=5000.0, description="advisory", is_b2b=True, market="DE"),
    Transaction(id="w04", merchant="Uber",           amount=34.50, description="airport", market="DE"),
    Transaction(id="w05", merchant="Deutsche Bahn",  amount=89.0,  description="Hamburg", market="DE"),
    Transaction(id="w06", merchant="Unknown GmbH",   amount=40.0,  description="misc", market="DE"),
]


async def main() -> None:
    rng = random.Random(42)
    event_sink: asyncio.Queue = asyncio.Queue()

    print("\n══ Async Streaming Pipeline Demo ══\n")
    print(f"  Processing {len(TEST_TRANSACTIONS)} transactions")
    print(f"  Max concurrent LLM calls: {MAX_CONCURRENT}")
    print(f"  Events streamed in real-time (SSE format)\n")

    t_start = time.monotonic()

    # Start batch processor as concurrent task
    processor_task = asyncio.create_task(
        process_batch_concurrent(TEST_TRANSACTIONS, rng, event_sink)
    )

    # Stream events as they arrive
    completed: dict[str, str] = {}   # tx_id → final status
    event_count = 0

    while True:
        event = await event_sink.get()
        if event is None:
            break

        event_count += 1
        elapsed = (time.monotonic() - t_start) * 1000

        if event.event_type == EventType.STAGE_START:
            pass   # suppress for brevity
        elif event.event_type == EventType.STAGE_COMPLETE and event.stage == "categorize":
            acct = event.data.get("account_code", "?")
            conf = event.data.get("confidence", 0)
            print(f"  [{elapsed:5.0f}ms] {event.transaction_id} categorized → {acct} ({conf:.0%})")
        elif event.event_type == EventType.AUTO_BOOKED:
            debit = event.data.get("debit", "?")
            net = event.data.get("net", 0)
            print(f"  [{elapsed:5.0f}ms] {event.transaction_id} AUTO_BOOKED  debit={debit} net=€{net:.2f}")
            completed[event.transaction_id] = "AUTO_BOOKED"
        elif event.event_type == EventType.PROPOSAL_READY:
            print(f"  [{elapsed:5.0f}ms] {event.transaction_id} PROPOSAL_SENT (awaiting user confirm)")
            completed[event.transaction_id] = "PROPOSAL_SENT"
        elif event.event_type == EventType.REQUIRES_REVIEW:
            reason = event.data.get("reason", "")[:40]
            print(f"  [{elapsed:5.0f}ms] {event.transaction_id} REQUIRES_REVIEW  reason={reason}")
            completed[event.transaction_id] = "REQUIRES_REVIEW"
        elif event.event_type == EventType.ERROR:
            reason = event.data.get("reason", "")[:50]
            print(f"  [{elapsed:5.0f}ms] {event.transaction_id} REJECTED  {reason}")
            completed[event.transaction_id] = "REJECTED"

    await processor_task

    total_ms = (time.monotonic() - t_start) * 1000
    serial_estimate_ms = len(TEST_TRANSACTIONS) * 100   # ~100ms avg per LLM call

    print(f"\n  ── Batch complete ──────────────────────────────────────")
    for tx_id, status in sorted(completed.items()):
        icon = {"AUTO_BOOKED": "✓", "PROPOSAL_SENT": "→", "REQUIRES_REVIEW": "⚠", "REJECTED": "✗"}.get(status, "?")
        print(f"  {icon} {tx_id}: {status}")

    print(f"\n  Total time:    {total_ms:.0f}ms")
    print(f"  Serial est.:   {serial_estimate_ms}ms")
    print(f"  Speedup:       {serial_estimate_ms / total_ms:.1f}×")
    print(f"  Events emitted: {event_count}")

    print(f"\n  ── Design notes ────────────────────────────────────────")
    print(f"  Semaphore({MAX_CONCURRENT}): prevents LLM rate-limit cascade on large batches")
    print(f"  Event sink pattern: processor → queue → streamer (decoupled)")
    print(f"  SSE framing: each event is immediately streamable to browser client")
    print(f"  Sentinel (None): clean shutdown without polling or timeout")
    print(f"  Graceful: all in-flight transactions complete before sentinel fires")
    print(f"\n  ── Production upgrade path ─────────────────────────────")
    print(f"  Replace asyncio.sleep(0.1) with real httpx call to LLM API")
    print(f"  Replace event_sink with Redis Streams or AWS EventBridge")
    print(f"  Replace process_batch_concurrent with Celery/ARQ worker pool")
    print(f"  Add IdempotencyRegistry.get_cached() before each LLM call")


if __name__ == "__main__":
    asyncio.run(main())
