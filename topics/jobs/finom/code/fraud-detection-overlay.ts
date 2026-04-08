/**
 * Fraud Detection Overlay for MAS Accounting Pipeline
 *
 * Demonstrates fraud detection as a cross-cutting concern that runs
 * alongside the main accounting pipeline — not a separate system,
 * but an overlay that scores every transaction for risk.
 *
 * Patterns shown:
 * - Behavioral baseline building per customer
 * - Multi-signal anomaly scoring (amount, timing, counterparty, velocity)
 * - Rule + ML hybrid detection (rules for known patterns, scoring for novel)
 * - Risk-based routing (allow / flag / hold / block)
 * - Aggregate risk monitoring across the customer portfolio
 *
 * No LLM calls — structural demo showing the fraud architecture.
 */

import { z } from 'zod';

// ── Types ──────────────────────────────────────────────────────

const RiskLevel = z.enum(['clear', 'monitor', 'flag', 'hold', 'block']);
type RiskLevel = z.infer<typeof RiskLevel>;

interface Transaction {
  id: string;
  customerId: string;
  amount: number;
  currency: string;
  counterparty: string;
  category: string;
  description: string;
  timestamp: Date;
  channel: 'online' | 'card' | 'transfer' | 'direct_debit';
}

interface CustomerBaseline {
  customerId: string;
  avgTransactionAmount: number;
  stdDevAmount: number;
  avgDailyTransactionCount: number;
  knownCounterparties: Set<string>;
  typicalCategories: Set<string>;
  accountAgeMonths: number;
  totalTransactions: number;
}

interface RiskSignal {
  signalType: string;
  score: number; // 0.0 (no risk) to 1.0 (maximum risk)
  detail: string;
  source: 'rule' | 'statistical' | 'behavioral' | 'graph';
}

interface FraudAssessment {
  transactionId: string;
  customerId: string;
  riskLevel: RiskLevel;
  compositeScore: number;
  signals: RiskSignal[];
  action: 'allow' | 'flag_async' | 'hold_for_review' | 'block';
  explanation: string;
}

// ── Rules Engine (Known Patterns) ──────────────────────────────

class RulesEngine {
  private amlDailyLimit = 10_000; // EUR, simplified
  private velocityWindow = 60; // minutes
  private velocityLimit = 5; // transactions per window
  private recentTransactions: Map<string, Date[]> = new Map();

  evaluate(tx: Transaction, baseline: CustomerBaseline): RiskSignal[] {
    const signals: RiskSignal[] = [];

    // Rule 1: AML threshold (structuring detection)
    if (tx.amount >= this.amlDailyLimit * 0.8) {
      signals.push({
        signalType: 'aml_threshold_proximity',
        score: tx.amount >= this.amlDailyLimit ? 0.9 : 0.4,
        detail: `Transaction €${tx.amount} is ${tx.amount >= this.amlDailyLimit ? 'above' : 'near'} AML reporting threshold (€${this.amlDailyLimit})`,
        source: 'rule',
      });
    }

    // Rule 2: Velocity check
    const customerRecent = this.recentTransactions.get(tx.customerId) || [];
    const windowStart = new Date(tx.timestamp.getTime() - this.velocityWindow * 60 * 1000);
    const recentCount = customerRecent.filter(t => t > windowStart).length;
    if (recentCount >= this.velocityLimit) {
      signals.push({
        signalType: 'velocity_breach',
        score: 0.7,
        detail: `${recentCount + 1} transactions in ${this.velocityWindow} minutes (limit: ${this.velocityLimit})`,
        source: 'rule',
      });
    }

    // Track for velocity
    customerRecent.push(tx.timestamp);
    this.recentTransactions.set(tx.customerId, customerRecent);

    // Rule 3: Round amount structuring (common in money laundering)
    if (tx.amount > 1000 && tx.amount % 1000 === 0) {
      signals.push({
        signalType: 'round_amount_pattern',
        score: 0.3,
        detail: `Exact round amount €${tx.amount} — potential structuring indicator`,
        source: 'rule',
      });
    }

    // Rule 4: New account + large transaction
    if (baseline.accountAgeMonths < 3 && tx.amount > baseline.avgTransactionAmount * 5) {
      signals.push({
        signalType: 'new_account_large_tx',
        score: 0.6,
        detail: `Account age ${baseline.accountAgeMonths} months, transaction 5x above average`,
        source: 'rule',
      });
    }

    return signals;
  }
}

// ── Statistical Anomaly Scorer ─────────────────────────────────

class AnomalyScorer {
  evaluate(tx: Transaction, baseline: CustomerBaseline): RiskSignal[] {
    const signals: RiskSignal[] = [];

    // Amount anomaly (z-score)
    if (baseline.stdDevAmount > 0) {
      const zScore = Math.abs(tx.amount - baseline.avgTransactionAmount) / baseline.stdDevAmount;
      if (zScore > 2) {
        signals.push({
          signalType: 'amount_anomaly',
          score: Math.min(zScore / 5, 1.0), // Normalize to 0-1
          detail: `Amount €${tx.amount} is ${zScore.toFixed(1)} standard deviations from mean (€${baseline.avgTransactionAmount.toFixed(0)})`,
          source: 'statistical',
        });
      }
    }

    // New counterparty
    if (!baseline.knownCounterparties.has(tx.counterparty)) {
      const newCounterpartyRisk = baseline.totalTransactions > 50 ? 0.3 : 0.1;
      signals.push({
        signalType: 'new_counterparty',
        score: newCounterpartyRisk,
        detail: `First transaction with "${tx.counterparty}" (customer has ${baseline.knownCounterparties.size} known counterparties)`,
        source: 'behavioral',
      });
    }

    // Unusual category
    if (!baseline.typicalCategories.has(tx.category)) {
      signals.push({
        signalType: 'unusual_category',
        score: 0.25,
        detail: `Category "${tx.category}" not in customer's typical categories: [${[...baseline.typicalCategories].join(', ')}]`,
        source: 'behavioral',
      });
    }

    return signals;
  }
}

// ── Risk Router ────────────────────────────────────────────────

class RiskRouter {
  private thresholds = {
    block: 0.85,    // Very high risk → block transaction
    hold: 0.65,     // High risk → hold for manual review
    flag: 0.40,     // Medium risk → allow but flag for async review
    monitor: 0.20,  // Low risk → allow, log for pattern building
    // < 0.20 → clear
  };

  route(compositeScore: number): { riskLevel: RiskLevel; action: FraudAssessment['action'] } {
    if (compositeScore >= this.thresholds.block) {
      return { riskLevel: 'block', action: 'block' };
    }
    if (compositeScore >= this.thresholds.hold) {
      return { riskLevel: 'hold', action: 'hold_for_review' };
    }
    if (compositeScore >= this.thresholds.flag) {
      return { riskLevel: 'flag', action: 'flag_async' };
    }
    if (compositeScore >= this.thresholds.monitor) {
      return { riskLevel: 'monitor', action: 'allow' };
    }
    return { riskLevel: 'clear', action: 'allow' };
  }
}

// ── Fraud Detection Overlay ────────────────────────────────────

class FraudDetectionOverlay {
  private rulesEngine = new RulesEngine();
  private anomalyScorer = new AnomalyScorer();
  private riskRouter = new RiskRouter();

  assess(tx: Transaction, baseline: CustomerBaseline): FraudAssessment {
    // Collect signals from all sources
    const ruleSignals = this.rulesEngine.evaluate(tx, baseline);
    const anomalySignals = this.anomalyScorer.evaluate(tx, baseline);
    const allSignals = [...ruleSignals, ...anomalySignals];

    // Compute composite score
    // Strategy: weighted maximum (not average — one strong signal matters more than many weak ones)
    const compositeScore = allSignals.length === 0
      ? 0
      : Math.max(
          ...allSignals.map(s => s.score),
          // Bonus for signal count (multiple weak signals = higher concern)
          allSignals.filter(s => s.score > 0.2).length * 0.1,
        );

    // Route based on composite score
    const routing = this.riskRouter.route(Math.min(compositeScore, 1.0));

    // Generate human-readable explanation
    const topSignals = allSignals
      .sort((a, b) => b.score - a.score)
      .slice(0, 3);
    const explanation = topSignals.length === 0
      ? 'No risk signals detected'
      : `Top signals: ${topSignals.map(s => `${s.signalType} (${(s.score * 100).toFixed(0)}%)`).join(', ')}`;

    return {
      transactionId: tx.id,
      customerId: tx.customerId,
      riskLevel: routing.riskLevel,
      compositeScore: Math.min(compositeScore, 1.0),
      signals: allSignals,
      action: routing.action,
      explanation,
    };
  }
}

// ── Portfolio Risk Monitor ─────────────────────────────────────

class PortfolioRiskMonitor {
  private assessments: FraudAssessment[] = [];

  record(assessment: FraudAssessment): void {
    this.assessments.push(assessment);
  }

  getSummary(): {
    totalAssessed: number;
    byRiskLevel: Record<string, number>;
    byAction: Record<string, number>;
    avgCompositeScore: number;
    topSignalTypes: { type: string; count: number }[];
  } {
    const byRiskLevel: Record<string, number> = {};
    const byAction: Record<string, number> = {};
    const signalCounts: Record<string, number> = {};

    for (const a of this.assessments) {
      byRiskLevel[a.riskLevel] = (byRiskLevel[a.riskLevel] || 0) + 1;
      byAction[a.action] = (byAction[a.action] || 0) + 1;
      for (const s of a.signals) {
        signalCounts[s.signalType] = (signalCounts[s.signalType] || 0) + 1;
      }
    }

    const topSignalTypes = Object.entries(signalCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([type, count]) => ({ type, count }));

    return {
      totalAssessed: this.assessments.length,
      byRiskLevel,
      byAction,
      avgCompositeScore: this.assessments.length > 0
        ? this.assessments.reduce((sum, a) => sum + a.compositeScore, 0) / this.assessments.length
        : 0,
      topSignalTypes,
    };
  }
}

// ── Demo ───────────────────────────────────────────────────────

function main(): void {
  console.log('═══════════════════════════════════════════════════');
  console.log('  Fraud Detection Overlay — MAS Integration Demo');
  console.log('═══════════════════════════════════════════════════\n');

  const overlay = new FraudDetectionOverlay();
  const monitor = new PortfolioRiskMonitor();

  // Established customer baseline
  const establishedBaseline: CustomerBaseline = {
    customerId: 'CUST-001',
    avgTransactionAmount: 250,
    stdDevAmount: 150,
    avgDailyTransactionCount: 3,
    knownCounterparties: new Set(['Büromaterial GmbH', 'Deutsche Bahn', 'REWE', 'Amazon']),
    typicalCategories: new Set(['Betriebsausgabe', 'Reisekosten', 'Bewirtung']),
    accountAgeMonths: 18,
    totalTransactions: 450,
  };

  // New customer baseline
  const newBaseline: CustomerBaseline = {
    customerId: 'CUST-002',
    avgTransactionAmount: 100,
    stdDevAmount: 50,
    avgDailyTransactionCount: 1,
    knownCounterparties: new Set(['Startup Supplies']),
    typicalCategories: new Set(['Betriebsausgabe']),
    accountAgeMonths: 1,
    totalTransactions: 12,
  };

  const testTransactions: { tx: Transaction; baseline: CustomerBaseline; label: string }[] = [
    {
      label: 'Normal transaction (established customer)',
      tx: {
        id: 'TX-001',
        customerId: 'CUST-001',
        amount: 180,
        currency: 'EUR',
        counterparty: 'Büromaterial GmbH',
        category: 'Betriebsausgabe',
        description: 'Office supplies monthly order',
        timestamp: new Date('2026-04-08T10:30:00'),
        channel: 'transfer',
      },
      baseline: establishedBaseline,
    },
    {
      label: 'Large unusual transaction (established customer)',
      tx: {
        id: 'TX-002',
        customerId: 'CUST-001',
        amount: 4500,
        currency: 'EUR',
        counterparty: 'Unknown Consulting Ltd',
        category: 'Fremdleistungen',
        description: 'Consulting services Q1',
        timestamp: new Date('2026-04-08T10:35:00'),
        channel: 'transfer',
      },
      baseline: establishedBaseline,
    },
    {
      label: 'Near AML threshold (established customer)',
      tx: {
        id: 'TX-003',
        customerId: 'CUST-001',
        amount: 9000,
        currency: 'EUR',
        counterparty: 'Equipment Dealer GmbH',
        category: 'Anlagevermögen',
        description: 'Industrial equipment purchase',
        timestamp: new Date('2026-04-08T10:40:00'),
        channel: 'transfer',
      },
      baseline: establishedBaseline,
    },
    {
      label: 'New account + large round amount',
      tx: {
        id: 'TX-004',
        customerId: 'CUST-002',
        amount: 5000,
        currency: 'EUR',
        counterparty: 'Foreign Supplier',
        category: 'Wareneinkauf',
        description: 'Bulk inventory purchase',
        timestamp: new Date('2026-04-08T11:00:00'),
        channel: 'transfer',
      },
      baseline: newBaseline,
    },
    {
      label: 'Structuring attempt (multiple round amounts)',
      tx: {
        id: 'TX-005',
        customerId: 'CUST-001',
        amount: 3000,
        currency: 'EUR',
        counterparty: 'Unknown Entity',
        category: 'Sonstiges',
        description: 'Payment',
        timestamp: new Date('2026-04-08T10:42:00'),
        channel: 'transfer',
      },
      baseline: establishedBaseline,
    },
  ];

  console.log(`Assessing ${testTransactions.length} transactions...\n`);

  for (const { tx, baseline, label } of testTransactions) {
    const assessment = overlay.assess(tx, baseline);
    monitor.record(assessment);

    const riskIcon = {
      clear: '✅',
      monitor: '👁',
      flag: '⚡',
      hold: '⏸',
      block: '🛑',
    }[assessment.riskLevel];

    console.log(`─── ${tx.id}: ${label} ───`);
    console.log(`  Amount: €${tx.amount} → ${tx.counterparty}`);
    console.log(`  ${riskIcon} Risk: ${assessment.riskLevel.toUpperCase()} (score: ${(assessment.compositeScore * 100).toFixed(0)}%)`);
    console.log(`  Action: ${assessment.action}`);
    console.log(`  ${assessment.explanation}`);

    if (assessment.signals.length > 0) {
      console.log('  Signals:');
      for (const signal of assessment.signals) {
        console.log(`    [${signal.source}] ${signal.signalType}: ${(signal.score * 100).toFixed(0)}% — ${signal.detail}`);
      }
    }
    console.log();
  }

  // Portfolio summary
  const summary = monitor.getSummary();
  console.log('═══════════════════════════════════════════════════');
  console.log('  Portfolio Risk Summary');
  console.log('═══════════════════════════════════════════════════\n');
  console.log(`  Total assessed: ${summary.totalAssessed}`);
  console.log(`  Avg risk score: ${(summary.avgCompositeScore * 100).toFixed(1)}%`);
  console.log(`  By risk level: ${JSON.stringify(summary.byRiskLevel)}`);
  console.log(`  By action: ${JSON.stringify(summary.byAction)}`);
  console.log('  Top signal types:');
  for (const { type, count } of summary.topSignalTypes) {
    console.log(`    ${type}: ${count} occurrences`);
  }
  console.log();

  console.log('═══════════════════════════════════════════════════');
  console.log('  Key Takeaways');
  console.log('═══════════════════════════════════════════════════\n');
  console.log('  1. Fraud detection is a cross-cutting overlay, not a separate pipeline');
  console.log('  2. Rules catch known patterns (AML, velocity, structuring)');
  console.log('  3. Statistical scoring catches novel anomalies (amount, counterparty, category)');
  console.log('  4. Risk routing minimizes customer friction (flag async vs. block)');
  console.log('  5. Portfolio monitoring tracks aggregate risk trends');
  console.log('  6. Every assessment has an explanation — required for compliance');
  console.log();
}

main();
