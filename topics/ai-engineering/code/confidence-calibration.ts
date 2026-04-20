/**
 * Confidence Calibration Experiment — Finom Context
 *
 * Demonstrates the math and monitoring patterns behind confidence-based
 * routing in production AI systems. Directly implements the concepts
 * from insights/confidence-calibration-deep-dive.md.
 *
 * No LLM calls — uses simulated predictions to show calibration analysis.
 * Run with: bun run confidence-calibration.ts
 */

import { z } from "zod";

// ─── Types ──────────────────────────────────────────────────────

const PredictionSchema = z.object({
  id: z.string(),
  predictedCategory: z.string(),
  confidence: z.number().min(0).max(1),
  actualCategory: z.string(),
  market: z.enum(["DE", "FR", "IT"]),
});

type Prediction = z.infer<typeof PredictionSchema>;

interface CalibrationBin {
  binStart: number;
  binEnd: number;
  binCenter: number;
  count: number;
  averageConfidence: number;
  actualAccuracy: number;
  gap: number; // |accuracy - confidence|
}

interface CalibrationReport {
  bins: CalibrationBin[];
  ece: number; // Expected Calibration Error
  mce: number; // Maximum Calibration Error
  totalPredictions: number;
  overallAccuracy: number;
  diagnosis: "well-calibrated" | "over-confident" | "under-confident" | "mixed";
}

interface PlattParameters {
  a: number;
  b: number;
}

interface ThresholdAnalysis {
  threshold: number;
  autoBookCount: number;
  autoBookAccuracy: number;
  reviewCount: number;
  rejectCount: number;
  missedErrors: number; // bad predictions above threshold
  unnecessaryReviews: number; // good predictions below threshold
}

// ─── Simulated Prediction Data ──────────────────────────────────

function generatePredictions(
  count: number,
  market: "DE" | "FR" | "IT",
  calibrationBias: number // 0 = perfect, positive = over-confident, negative = under-confident
): Prediction[] {
  const categories = ["office", "travel", "software", "restaurant", "telecom", "marketing", "postage"];
  const predictions: Prediction[] = [];

  for (let i = 0; i < count; i++) {
    const trueCategory = categories[Math.floor(Math.random() * categories.length)] as string;

    // Generate a raw confidence score
    const rawConfidence = Math.min(1, Math.max(0.1, 0.5 + Math.random() * 0.5));

    // Apply calibration bias (over-confident models report higher confidence than warranted)
    const biasedConfidence = Math.min(0.99, Math.max(0.05, rawConfidence + calibrationBias));

    // The actual correctness depends on the raw confidence, not the biased one
    const isCorrect = Math.random() < rawConfidence;
    const predictedCategory = isCorrect
      ? trueCategory
      : categories[Math.floor(Math.random() * categories.length)] as string;

    predictions.push({
      id: `${market}-${String(i).padStart(4, "0")}`,
      predictedCategory,
      confidence: Math.round(biasedConfidence * 100) / 100,
      actualCategory: trueCategory,
      market,
    });
  }

  return predictions;
}

// ─── Calibration Analysis ───────────────────────────────────────

function computeCalibration(predictions: Prediction[], numBins = 10): CalibrationReport {
  const binWidth = 1 / numBins;
  const bins: CalibrationBin[] = [];

  for (let i = 0; i < numBins; i++) {
    const binStart = i * binWidth;
    const binEnd = (i + 1) * binWidth;
    const binCenter = (binStart + binEnd) / 2;

    const inBin = predictions.filter(
      (p) => p.confidence >= binStart && p.confidence < binEnd
    );

    if (inBin.length === 0) {
      bins.push({
        binStart,
        binEnd,
        binCenter,
        count: 0,
        averageConfidence: binCenter,
        actualAccuracy: 0,
        gap: 0,
      });
      continue;
    }

    const avgConf = inBin.reduce((s, p) => s + p.confidence, 0) / inBin.length;
    const accuracy =
      inBin.filter((p) => p.predictedCategory === p.actualCategory).length /
      inBin.length;

    bins.push({
      binStart,
      binEnd,
      binCenter,
      count: inBin.length,
      averageConfidence: Math.round(avgConf * 1000) / 1000,
      actualAccuracy: Math.round(accuracy * 1000) / 1000,
      gap: Math.round(Math.abs(accuracy - avgConf) * 1000) / 1000,
    });
  }

  // ECE: weighted average of bin gaps
  const totalPredictions = predictions.length;
  const ece =
    bins.reduce((sum, bin) => sum + (bin.count / totalPredictions) * bin.gap, 0);

  // MCE: maximum bin gap
  const mce = Math.max(...bins.filter((b) => b.count > 0).map((b) => b.gap));

  const overallAccuracy =
    predictions.filter((p) => p.predictedCategory === p.actualCategory).length /
    totalPredictions;

  // Diagnose calibration direction
  const weightedDirection = bins
    .filter((b) => b.count > 0)
    .reduce(
      (sum, bin) =>
        sum +
        (bin.count / totalPredictions) *
          (bin.averageConfidence - bin.actualAccuracy),
      0
    );

  let diagnosis: CalibrationReport["diagnosis"];
  if (Math.abs(weightedDirection) < 0.02) diagnosis = "well-calibrated";
  else if (weightedDirection > 0) diagnosis = "over-confident";
  else diagnosis = "under-confident";

  return {
    bins,
    ece: Math.round(ece * 1000) / 1000,
    mce: Math.round(mce * 1000) / 1000,
    totalPredictions,
    overallAccuracy: Math.round(overallAccuracy * 1000) / 1000,
    diagnosis,
  };
}

// ─── Platt Scaling (Post-Hoc Calibration) ───────────────────────

/**
 * Simplified Platt scaling: fits a logistic function to map raw
 * confidence scores to calibrated probabilities.
 *
 * In production, use proper logistic regression on a held-out set.
 * This is a closed-form approximation for demonstration.
 */
function fitPlattScaling(predictions: Prediction[]): PlattParameters {
  // Group by confidence bins and compute actual accuracy
  const bins = new Map<number, { correct: number; total: number }>();
  for (const p of predictions) {
    const bin = Math.round(p.confidence * 10) / 10;
    const entry = bins.get(bin) ?? { correct: 0, total: 0 };
    entry.total++;
    if (p.predictedCategory === p.actualCategory) entry.correct++;
    bins.set(bin, entry);
  }

  // Simple linear fit in log-odds space: log(accuracy/(1-accuracy)) = a*confidence + b
  const points: Array<{ x: number; y: number }> = [];
  for (const [conf, { correct, total }] of bins) {
    if (total < 5) continue; // skip sparse bins
    const acc = Math.max(0.01, Math.min(0.99, correct / total));
    points.push({ x: conf, y: Math.log(acc / (1 - acc)) });
  }

  if (points.length < 2) return { a: 1, b: 0 }; // can't fit

  // Least squares linear regression
  const n = points.length;
  const sumX = points.reduce((s, p) => s + p.x, 0);
  const sumY = points.reduce((s, p) => s + p.y, 0);
  const sumXY = points.reduce((s, p) => s + p.x * p.y, 0);
  const sumX2 = points.reduce((s, p) => s + p.x * p.x, 0);

  const a = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
  const b = (sumY - a * sumX) / n;

  return {
    a: Math.round(a * 1000) / 1000,
    b: Math.round(b * 1000) / 1000,
  };
}

function applyPlattScaling(
  confidence: number,
  params: PlattParameters
): number {
  const calibrated = 1 / (1 + Math.exp(-(params.a * confidence + params.b)));
  return Math.round(calibrated * 1000) / 1000;
}

function recalibratePredictions(
  predictions: Prediction[],
  params: PlattParameters
): Prediction[] {
  return predictions.map((p) => ({
    ...p,
    confidence: applyPlattScaling(p.confidence, params),
  }));
}

// ─── Threshold Analysis ─────────────────────────────────────────

function analyzeThreshold(
  predictions: Prediction[],
  threshold: number
): ThresholdAnalysis {
  const aboveThreshold = predictions.filter((p) => p.confidence >= threshold);
  const belowThreshold = predictions.filter(
    (p) => p.confidence < threshold && p.confidence >= 0.5
  );
  const rejected = predictions.filter((p) => p.confidence < 0.5);

  const autoBookCorrect = aboveThreshold.filter(
    (p) => p.predictedCategory === p.actualCategory
  ).length;
  const autoBookAccuracy =
    aboveThreshold.length > 0 ? autoBookCorrect / aboveThreshold.length : 0;

  const missedErrors = aboveThreshold.length - autoBookCorrect; // bad auto-books
  const unnecessaryReviews = belowThreshold.filter(
    (p) => p.predictedCategory === p.actualCategory
  ).length;

  return {
    threshold,
    autoBookCount: aboveThreshold.length,
    autoBookAccuracy: Math.round(autoBookAccuracy * 1000) / 1000,
    reviewCount: belowThreshold.length,
    rejectCount: rejected.length,
    missedErrors,
    unnecessaryReviews,
  };
}

// ─── ASCII Calibration Chart ────────────────────────────────────

function renderCalibrationChart(report: CalibrationReport): string {
  const height = 10;
  const lines: string[] = [];

  lines.push("  Calibration Curve (predicted vs actual accuracy)");
  lines.push("  " + "─".repeat(52));

  for (let row = height; row >= 0; row--) {
    const yValue = row / height;
    const label = row % 2 === 0 ? `${(yValue * 100).toFixed(0).padStart(3)}%` : "    ";
    let line = `${label} │`;

    for (const bin of report.bins) {
      if (bin.count === 0) {
        line += "    ";
        continue;
      }

      const barHeight = Math.round(bin.actualAccuracy * height);
      const perfectHeight = Math.round(bin.binCenter * height);

      if (row === barHeight && row === perfectHeight) {
        line += " ●  "; // actual matches perfect
      } else if (row === barHeight) {
        line += " ◆  "; // actual accuracy
      } else if (row === perfectHeight) {
        line += " ·  "; // perfect calibration line
      } else {
        line += "    ";
      }
    }

    lines.push(line);
  }

  lines.push("     └" + "────".repeat(10));
  lines.push(
    "      " +
      report.bins.map((b) => `.${(b.binCenter * 10).toFixed(0)}`.padEnd(4)).join("")
  );
  lines.push("       ◆ = actual accuracy    · = perfect calibration");

  return lines.join("\n");
}

// ─── Main Demo ──────────────────────────────────────────────────

console.log("=== Confidence Calibration Experiment ===\n");

// Simulate three markets with different calibration characteristics
const markets: Array<{
  name: string;
  market: "DE" | "FR" | "IT";
  count: number;
  bias: number;
  description: string;
}> = [
  {
    name: "Germany (mature)",
    market: "DE",
    count: 1000,
    bias: 0.05,
    description: "Slight over-confidence — well-trained, many examples",
  },
  {
    name: "France (new)",
    market: "FR",
    count: 300,
    bias: 0.15,
    description: "Significant over-confidence — limited training data",
  },
  {
    name: "Italy (zero-shot)",
    market: "IT",
    count: 100,
    bias: 0.25,
    description: "Severe over-confidence — no market-specific training",
  },
];

for (const { name, market, count, bias, description } of markets) {
  console.log(`\n${"═".repeat(60)}`);
  console.log(`  Market: ${name}`);
  console.log(`  ${description}`);
  console.log(`${"═".repeat(60)}`);

  // Generate and analyze
  const predictions = generatePredictions(count, market, bias);
  const report = computeCalibration(predictions);

  console.log(`\n  Predictions: ${report.totalPredictions}`);
  console.log(`  Overall accuracy: ${(report.overallAccuracy * 100).toFixed(1)}%`);
  console.log(`  ECE: ${report.ece} (${report.ece < 0.05 ? "good" : report.ece < 0.15 ? "moderate" : "poor"})`);
  console.log(`  MCE: ${report.mce}`);
  console.log(`  Diagnosis: ${report.diagnosis}`);

  // Render calibration chart
  console.log("\n" + renderCalibrationChart(report));

  // Threshold analysis before calibration
  console.log("\n  Threshold Analysis (before calibration):");
  console.log("  " + "─".repeat(50));
  for (const t of [0.95, 0.85, 0.75]) {
    const analysis = analyzeThreshold(predictions, t);
    console.log(
      `    ${(t * 100).toFixed(0)}%: ${analysis.autoBookCount} auto-booked ` +
      `(${(analysis.autoBookAccuracy * 100).toFixed(1)}% accurate), ` +
      `${analysis.missedErrors} errors slipped through, ` +
      `${analysis.unnecessaryReviews} unnecessary reviews`
    );
  }

  // Fit and apply Platt scaling
  const plattParams = fitPlattScaling(predictions);
  console.log(`\n  Platt Scaling Parameters: a=${plattParams.a}, b=${plattParams.b}`);
  console.log(`  Calibrated(0.5) = ${applyPlattScaling(0.5, plattParams)}`);
  console.log(`  Calibrated(0.8) = ${applyPlattScaling(0.8, plattParams)}`);
  console.log(`  Calibrated(0.95) = ${applyPlattScaling(0.95, plattParams)}`);

  const recalibrated = recalibratePredictions(predictions, plattParams);
  const recalReport = computeCalibration(recalibrated);

  console.log(`\n  After Platt Scaling:`);
  console.log(`  ECE: ${report.ece} → ${recalReport.ece} (${recalReport.ece < report.ece ? "improved" : "no improvement"})`);
  console.log(`  Diagnosis: ${report.diagnosis} → ${recalReport.diagnosis}`);

  // Threshold analysis after calibration
  console.log("\n  Threshold Analysis (after calibration):");
  console.log("  " + "─".repeat(50));
  for (const t of [0.95, 0.85, 0.75]) {
    const analysis = analyzeThreshold(recalibrated, t);
    console.log(
      `    ${(t * 100).toFixed(0)}%: ${analysis.autoBookCount} auto-booked ` +
      `(${(analysis.autoBookAccuracy * 100).toFixed(1)}% accurate), ` +
      `${analysis.missedErrors} errors slipped through, ` +
      `${analysis.unnecessaryReviews} unnecessary reviews`
    );
  }
}

// ─── Summary ────────────────────────────────────────────────────

console.log(`\n${"═".repeat(60)}`);
console.log("  Key Takeaways");
console.log(`${"═".repeat(60)}`);
console.log(`
  1. Over-confidence increases with less training data
     - DE (mature): slight bias → easy to calibrate
     - FR (new): significant bias → thresholds must be conservative
     - IT (zero-shot): severe bias → barely trust the model

  2. Platt scaling reduces ECE but doesn't fix fundamental accuracy
     - Calibration fixes the confidence mapping, not the predictions
     - A badly-performing model with perfect calibration just says "I'm 40% sure" instead of "I'm 90% sure"

  3. Threshold choice is a business decision, not a technical one
     - 95% threshold: fewer auto-books, fewer errors → use when launching
     - 85% threshold: balanced → use after calibration is verified
     - 75% threshold: more auto-books, more errors → use in mature markets

  4. The earned autonomy pattern:
     Launch → Conservative thresholds → Calibrate → Widen → Monitor → Repeat
`);

console.log("=== Experiment Complete ===");
