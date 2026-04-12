/**
 * observability-patterns.ts
 *
 * Three-layer observability for financial AI workflows.
 *
 * Layer 1: Confidence distribution monitoring (leading indicator — add day one)
 * Layer 2: Terminal state tracking (catches silent rejects and stranded transactions)
 * Layer 3: Business KPI dashboard (connects AI health to FTE impact)
 *
 * Each layer is independently runnable. The demo runs a simulated 30-transaction
 * batch across two weeks, introducing drift in week 2 to show what alerts look like.
 *
 * Run: bun run observability
 */

// ─── Types ────────────────────────────────────────────────────────────────────

type Market = "DE" | "FR";
type TerminalState =
  | "auto_booked"
  | "proposal_sent"
  | "rejected"
  | "requires_review"
  | "error_logged";

interface StageTrace {
  name: string;
  durationMs: number;
  confidence: number;
  decision: string;
}

interface TransactionSpan {
  correlationId: string;
  transactionId: string;
  market: Market;
  batchId: string;
  stages: StageTrace[];
  terminalState: TerminalState | null; // null = stranded
  totalDurationMs: number;
  createdAt: number; // epoch ms
  resolvedAt: number | null; // null = not yet resolved
}

interface BatchHealthSummary {
  batchId: string;
  batchSize: number;
  confidenceP10: number;
  confidenceP50: number;
  confidenceP90: number;
  historicalP50Baseline: number;
  strandedCount: number;
  autoBookRate: number;
  overrideRate: number; // fraction of auto-booked that were later corrected
  proposalAcceptanceRate: number;
  severeErrorCount: number; // wrong VAT or wrong account code
  reviewQueueDepth: number;
  alertFired: boolean;
  alertReasons: string[];
}

// ─── Layer 1: Confidence Distribution Monitor ─────────────────────────────────

class ConfidenceDistributionMonitor {
  private readonly history: number[][] = []; // rolling 30-day batches
  private readonly SLA_SIGMA = 2.0;

  recordBatch(confidenceScores: number[]): void {
    this.history.push(confidenceScores);
    // Keep last 30 batches (simulate 30 days)
    if (this.history.length > 30) this.history.shift();
  }

  private percentile(sorted: number[], p: number): number {
    const idx = Math.floor((sorted.length - 1) * p);
    return sorted[idx];
  }

  computeStats(scores: number[]): { p10: number; p50: number; p90: number } {
    const sorted = [...scores].sort((a, b) => a - b);
    return {
      p10: this.percentile(sorted, 0.1),
      p50: this.percentile(sorted, 0.5),
      p90: this.percentile(sorted, 0.9),
    };
  }

  computeHistoricalBaseline(): { mean: number; stddev: number } | null {
    if (this.history.length < 7) return null; // need a week of data
    const allP50s = this.history.map((batch) => {
      const sorted = [...batch].sort((a, b) => a - b);
      return this.percentile(sorted, 0.5);
    });
    const mean = allP50s.reduce((a, b) => a + b) / allP50s.length;
    const variance =
      allP50s.reduce((sum, v) => sum + (v - mean) ** 2, 0) / allP50s.length;
    return { mean, stddev: Math.sqrt(variance) };
  }

  checkForDrift(currentBatchScores: number[]): {
    isDrifting: boolean;
    reason: string | null;
    currentP50: number;
    baselineP50: number | null;
  } {
    const { p50: currentP50 } = this.computeStats(currentBatchScores);
    const baseline = this.computeHistoricalBaseline();

    if (!baseline) {
      return {
        isDrifting: false,
        reason: null,
        currentP50,
        baselineP50: null,
      };
    }

    const zScore = (baseline.mean - currentP50) / (baseline.stddev || 0.01);
    const isDrifting = zScore > this.SLA_SIGMA;

    return {
      isDrifting,
      reason: isDrifting
        ? `Confidence P50 ${currentP50.toFixed(3)} is ${zScore.toFixed(1)}σ below historical baseline ${baseline.mean.toFixed(3)}`
        : null,
      currentP50,
      baselineP50: baseline.mean,
    };
  }
}

// ─── Layer 2: Terminal State Tracker ──────────────────────────────────────────

class TransactionLifecycleTracker {
  private readonly spans = new Map<string, TransactionSpan>();
  private readonly SLA_WINDOW_MS = 2 * 60 * 60 * 1000; // 2 hours

  register(span: TransactionSpan): void {
    this.spans.set(span.transactionId, span);
  }

  resolve(transactionId: string, state: TerminalState): void {
    const span = this.spans.get(transactionId);
    if (!span) return;
    span.terminalState = state;
    span.resolvedAt = Date.now();
  }

  findStranded(nowMs: number): TransactionSpan[] {
    const stranded: TransactionSpan[] = [];
    for (const span of this.spans.values()) {
      if (
        span.terminalState === null &&
        nowMs - span.createdAt > this.SLA_WINDOW_MS
      ) {
        stranded.push(span);
      }
    }
    return stranded;
  }

  getTerminalStateDistribution(): Record<TerminalState | "stranded", number> {
    const dist: Record<TerminalState | "stranded", number> = {
      auto_booked: 0,
      proposal_sent: 0,
      rejected: 0,
      requires_review: 0,
      error_logged: 0,
      stranded: 0,
    };
    for (const span of this.spans.values()) {
      if (span.terminalState === null) {
        dist.stranded++;
      } else {
        dist[span.terminalState]++;
      }
    }
    return dist;
  }
}

// ─── Layer 3: Business KPI Dashboard ──────────────────────────────────────────

interface WeeklyKPIs {
  week: number;
  autoBookRate: number;
  overrideRate: number;
  proposalAcceptanceRate: number;
  reviewQueueDepth: number;
  severeErrorCount: number;
  fteImpactScore: number; // 0–1, higher = more FTE time saved
}

function computeFteImpactScore(kpis: Omit<WeeklyKPIs, "fteImpactScore" | "week">): number {
  // FTE impact is a weighted combination of the metrics Ivo tracks:
  // - auto-book rate: each auto-booked transaction is ~3 min of accountant time saved
  // - override rate: corrections cost more time than manual entry would have
  // - review queue depth: growing queue = AI generating work, not reducing it
  const autoBookWeight = 0.5;
  const overridePenalty = 0.3;
  const queuePenalty = 0.2;

  const base = kpis.autoBookRate * autoBookWeight;
  const penalty = Math.min(1, kpis.overrideRate * 5) * overridePenalty; // 20% override = full penalty
  const queueScore = Math.max(0, 1 - kpis.reviewQueueDepth / 20) * queuePenalty;

  return Math.max(0, base - penalty + queueScore);
}

// ─── Simulation Engine ────────────────────────────────────────────────────────

function generateBatch(
  batchId: string,
  week: number,
  isDrifting: boolean
): { spans: TransactionSpan[]; corrections: Set<string> } {
  const corrections = new Set<string>();
  const spans: TransactionSpan[] = [];
  const batchSize = 15;
  const now = Date.now();

  for (let i = 0; i < batchSize; i++) {
    const txId = `tx_w${week}_${i.toString().padStart(3, "0")}`;
    // In week 2, inject drift: confidence drops by ~0.15
    const baseConfidence = isDrifting
      ? 0.55 + Math.random() * 0.25 // 0.55–0.80 (drifted)
      : 0.70 + Math.random() * 0.25; // 0.70–0.95 (healthy)

    const confidence = Math.min(0.99, baseConfidence);

    // Route to terminal state based on confidence thresholds
    let terminalState: TerminalState;
    if (confidence >= 0.85) {
      terminalState = "auto_booked";
      // In drifted week, auto-booked transactions get overridden at higher rate
      if (isDrifting && Math.random() < 0.12) {
        corrections.add(txId);
      } else if (!isDrifting && Math.random() < 0.015) {
        corrections.add(txId);
      }
    } else if (confidence >= 0.55) {
      terminalState = "proposal_sent";
    } else {
      terminalState = "rejected";
    }

    // Inject one stranded transaction per batch in week 2
    const isStranded = isDrifting && i === 7;

    spans.push({
      correlationId: `corr_${batchId}_${i}`,
      transactionId: txId,
      market: i % 4 === 0 ? "FR" : "DE",
      batchId,
      stages: [
        {
          name: "categorize",
          durationMs: 120 + Math.floor(Math.random() * 80),
          confidence,
          decision: `confidence:${confidence.toFixed(2)}`,
        },
        {
          name: "vat",
          durationMs: 2,
          confidence: 1.0,
          decision: "19%:standard",
        },
        {
          name: "route",
          durationMs: 1,
          confidence: 1.0,
          decision: terminalState,
        },
      ],
      terminalState: isStranded ? null : terminalState,
      totalDurationMs: 123 + Math.floor(Math.random() * 80),
      createdAt: now - (isStranded ? 3 * 60 * 60 * 1000 : 0), // stranded = 3h ago
      resolvedAt: isStranded ? null : now,
    });
  }

  return { spans, corrections };
}

// ─── Report Rendering ─────────────────────────────────────────────────────────

function renderBatchHealthReport(
  summary: BatchHealthSummary,
  driftCheck: ReturnType<ConfidenceDistributionMonitor["checkForDrift"]>
): void {
  const prefix = summary.alertFired ? "⚠️  ALERT" : "✓  OK";
  console.log(`\n${prefix} — Batch ${summary.batchId} (n=${summary.batchSize})`);

  console.log(`\n  Confidence Distribution`);
  const bar = (v: number) => "█".repeat(Math.round(v * 20)).padEnd(20, "░");
  console.log(`    P10  ${bar(summary.confidenceP10)}  ${(summary.confidenceP10 * 100).toFixed(0)}%`);
  console.log(`    P50  ${bar(summary.confidenceP50)}  ${(summary.confidenceP50 * 100).toFixed(0)}%  ${driftCheck.isDrifting ? "← DRIFTING" : ""}`);
  console.log(`    P90  ${bar(summary.confidenceP90)}  ${(summary.confidenceP90 * 100).toFixed(0)}%`);
  if (driftCheck.baselineP50 !== null) {
    console.log(`    Baseline P50: ${(driftCheck.baselineP50 * 100).toFixed(0)}%`);
  }

  console.log(`\n  Terminal State Distribution`);
  console.log(`    Auto-booked:     ${(summary.autoBookRate * 100).toFixed(0)}%`);
  console.log(`    Override rate:   ${(summary.overrideRate * 100).toFixed(1)}%  ${summary.overrideRate > 0.05 ? "← ALERT: above 5% threshold" : ""}`);
  console.log(`    Proposal accept: ${(summary.proposalAcceptanceRate * 100).toFixed(0)}%`);
  console.log(`    Review queue:    ${summary.reviewQueueDepth}  ${summary.reviewQueueDepth > 10 ? "← GROWING" : ""}`);
  console.log(`    Stranded:        ${summary.strandedCount}  ${summary.strandedCount > 0 ? "← SEND TO DEAD LETTER QUEUE" : ""}`);
  console.log(`    Severe errors:   ${summary.severeErrorCount}  ${summary.severeErrorCount > 0 ? "← P1: review immediately" : ""}`);

  if (summary.alertFired) {
    console.log(`\n  Alert reasons:`);
    for (const reason of summary.alertReasons) {
      console.log(`    • ${reason}`);
    }
  }
}

function renderWeeklyKPIDashboard(weeks: WeeklyKPIs[]): void {
  console.log(`\n${"─".repeat(72)}`);
  console.log(`Weekly Business KPI Dashboard — FTE / Active Customer Impact`);
  console.log(`${"─".repeat(72)}`);
  console.log(`  Week │ Auto-Book │ Override │ Proposal Accept │ Queue │ FTE Score`);
  console.log(`  ─────┼───────────┼──────────┼─────────────────┼───────┼──────────`);
  for (const w of weeks) {
    const autoBook = `${(w.autoBookRate * 100).toFixed(0)}%`.padStart(8);
    const override = `${(w.overrideRate * 100).toFixed(1)}%`.padStart(7);
    const accept = `${(w.proposalAcceptanceRate * 100).toFixed(0)}%`.padStart(14);
    const queue = `${w.reviewQueueDepth}`.padStart(4);
    const score = `${(w.fteImpactScore * 100).toFixed(0)}%`.padStart(8);
    const flag = w.overrideRate > 0.05 || w.reviewQueueDepth > 10 ? " ⚠️" : "";
    console.log(`    W${w.week}  │${autoBook} │${override} │${accept} │${queue}  │${score}${flag}`);
  }
  console.log(`${"─".repeat(72)}`);
  console.log(`
  Reading key:
    Auto-Book > 70%:        target steady-state automation rate
    Override < 2%:          alert threshold — model may be miscategorizing
    Proposal Accept > 85%:  below this, proposals are unhelpful to users
    FTE Score:              composite impact on time-per-active-customer
`);
}

// ─── Main Demo ────────────────────────────────────────────────────────────────

async function runObservabilityDemo(): Promise<void> {
  console.log("=".repeat(72));
  console.log("Observability Patterns — Three-Layer Financial AI Monitoring");
  console.log("=".repeat(72));
  console.log(`
Layer 1: Confidence Distribution  — leading indicator, detects drift before errors accumulate
Layer 2: Terminal State Tracking  — catches silent rejects and stranded transactions
Layer 3: Business KPI Dashboard   — connects AI health to FTE / active customer metric
`);

  const confidenceMonitor = new ConfidenceDistributionMonitor();
  const lifecycleTracker = new TransactionLifecycleTracker();
  const weeklyKPIs: WeeklyKPIs[] = [];

  // ── Simulate 2 weeks ──────────────────────────────────────────────────────
  for (let week = 1; week <= 2; week++) {
    const isDrifting = week === 2;
    const batchId = `batch_w${week}`;

    console.log(`\n${"─".repeat(72)}`);
    console.log(`Week ${week}${isDrifting ? " — simulating confidence drift (OCR quality degraded)" : " — baseline healthy operation"}`);
    console.log(`${"─".repeat(72)}`);

    const { spans, corrections } = generateBatch(batchId, week, isDrifting);

    // Register spans in lifecycle tracker
    for (const span of spans) {
      lifecycleTracker.register(span);
    }

    // Feed confidence scores to distribution monitor
    const confidenceScores = spans.map((s) => s.stages[0].confidence);
    const driftCheck = confidenceMonitor.checkForDrift(confidenceScores);
    confidenceMonitor.recordBatch(confidenceScores);

    // Compute batch health summary
    const { p10, p50, p90 } = confidenceMonitor.computeStats(confidenceScores);
    const stateDist = lifecycleTracker.getTerminalStateDistribution();
    const stranded = lifecycleTracker.findStranded(Date.now());
    const autoBooked = stateDist.auto_booked;
    const total = spans.length;
    const proposalSent = stateDist.proposal_sent;

    // Simulate proposal acceptance (not tracked in this demo — use historical rate)
    const proposalAcceptanceRate = isDrifting ? 0.78 : 0.91;

    const summary: BatchHealthSummary = {
      batchId,
      batchSize: total,
      confidenceP10: p10,
      confidenceP50: p50,
      confidenceP90: p90,
      historicalP50Baseline: driftCheck.baselineP50 ?? p50,
      strandedCount: stranded.length,
      autoBookRate: autoBooked / total,
      overrideRate: corrections.size / Math.max(1, autoBooked),
      proposalAcceptanceRate,
      severeErrorCount: 0,
      reviewQueueDepth: isDrifting ? 12 : 3,
      alertFired: false,
      alertReasons: [],
    };

    // Fire alerts
    if (driftCheck.isDrifting && driftCheck.reason) {
      summary.alertFired = true;
      summary.alertReasons.push(driftCheck.reason);
    }
    if (summary.overrideRate > 0.05) {
      summary.alertFired = true;
      summary.alertReasons.push(
        `Override rate ${(summary.overrideRate * 100).toFixed(1)}% exceeds 5% threshold — check categorization accuracy`
      );
    }
    if (summary.strandedCount > 0) {
      summary.alertFired = true;
      summary.alertReasons.push(
        `${summary.strandedCount} stranded transaction(s) past SLA window — action: dead letter queue + ops alert (FM-15 prevention)`
      );
    }
    if (summary.reviewQueueDepth > 10) {
      summary.alertFired = true;
      summary.alertReasons.push(
        `Review queue depth ${summary.reviewQueueDepth} exceeds threshold — potential escalation storm (FM-14)`
      );
    }

    renderBatchHealthReport(summary, driftCheck);

    // Record weekly KPIs
    const kpiInputs = {
      autoBookRate: summary.autoBookRate,
      overrideRate: summary.overrideRate,
      proposalAcceptanceRate: summary.proposalAcceptanceRate,
      reviewQueueDepth: summary.reviewQueueDepth,
      severeErrorCount: summary.severeErrorCount,
    };
    weeklyKPIs.push({
      week,
      ...kpiInputs,
      fteImpactScore: computeFteImpactScore(kpiInputs),
    });
  }

  // ── Layer 3: Business KPI Dashboard ───────────────────────────────────────
  renderWeeklyKPIDashboard(weeklyKPIs);

  // ── Summary and interview talking points ──────────────────────────────────
  console.log("Architecture Principles Demonstrated");
  console.log("─".repeat(72));
  console.log(`
  1. Confidence distribution is a LEADING indicator.
     Add it on day one. Accuracy metrics require corrections to accumulate
     before they show anything. Confidence drift is visible in real time.

  2. Terminal state tracking catches FM-15 (silent reject).
     A transaction dropped by an unhandled exception has no accuracy metric
     representation — it just disappears. The lifecycle tracker surfaces it.

  3. Business KPIs connect AI health to FTE / active customer.
     Auto-book rate, override rate, and review queue depth are the metrics
     Ivo will ask about. The FTE impact score makes the connection explicit.

  4. Alerts are named failure modes, not thresholds.
     "Override rate > 5%" maps to FM-04 (overconfident miscategorization).
     "Review queue depth > 10" maps to FM-14 (escalation storm).
     Naming the failure mode makes the alert actionable, not just noisy.
`);
}

runObservabilityDemo().catch(console.error);
