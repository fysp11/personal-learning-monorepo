import { runEvals } from '@mastra/core/evals';
import type { EvalDatasetItem } from './medical-extraction.contracts';
import {
  clinicalExtractionAgent,
  extractionAccuracyScorer,
  extractionCompletenessScorer,
  extractionPrecisionScorer,
  extractionRecallScorer,
  safetyNoAdviceScorer,
  safetyPhiMinimizationScorer,
  supportClaimCoverageScorer,
  supportUnsupportedClaimPenaltyScorer,
  workflowJsonParseScorer,
  workflowNonEmptyOutputScorer,
} from './medical-extraction.impl';

export const extractionEvalDataset: EvalDatasetItem[] = [
  {
    input:
      'Visit note: 64-year-old male with hypertension and type 2 diabetes. Current medications: metformin 500 mg twice daily and lisinopril 20 mg daily. Allergy to penicillin causing rash. Blood pressure today 138/86. Heart rate 74.',
    groundTruth: {
      summary: 'Patient with hypertension and type 2 diabetes on metformin and lisinopril.',
      problems: [{ name: 'hypertension' }, { name: 'type 2 diabetes' }],
      medications: [
        { name: 'metformin', dose: '500 mg', frequency: 'twice daily' },
        { name: 'lisinopril', dose: '20 mg', frequency: 'daily' },
      ],
      allergies: [{ substance: 'penicillin', reaction: 'rash' }],
      vitals: [
        { name: 'blood pressure', value: '138/86' },
        { name: 'heart rate', value: '74' },
      ],
    },
  },
  {
    input:
      'ED note: 41-year-old female with asthma exacerbation. Uses albuterol inhaler as needed. No known drug allergies. Temperature 37.1 C. Oxygen saturation 95% on room air.',
    groundTruth: {
      summary: 'Asthma exacerbation with albuterol PRN use and stable oxygen saturation.',
      problems: [{ name: 'asthma exacerbation' }],
      medications: [{ name: 'albuterol inhaler', frequency: 'as needed' }],
      allergies: [],
      vitals: [
        { name: 'temperature', value: '37.1 C' },
        { name: 'oxygen saturation', value: '95%' },
      ],
    },
  },
];

function toPrettyJson(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function formatMetricRows(
  scorerResults: Record<
    string,
    | {
        score?: number | null;
        reason?: string;
      }
    | undefined
  >,
): string[] {
  return Object.entries(scorerResults).map(([metricId, result]) => {
    const score = result?.score ?? null;
    const reason = result?.reason ?? 'No reason returned';
    return `- ${metricId}: score=${score} | reason=${reason}`;
  });
}

type MetricGroupKey = 'Extraction' | 'Support' | 'Safety' | 'Workflow';

function getMetricGroup(metricId: string): MetricGroupKey {
  if (metricId.startsWith('clinical-extraction-')) return 'Extraction';
  if (metricId.startsWith('support-')) return 'Support';
  if (metricId.startsWith('safety-')) return 'Safety';
  return 'Workflow';
}

function formatGroupedMetricSummary(
  scorerResults: Record<
    string,
    | {
        score?: number | null;
      }
    | undefined
  >,
): string[] {
  const grouped = new Map<MetricGroupKey, Array<{ metricId: string; score: number | null }>>();
  const keys: MetricGroupKey[] = ['Extraction', 'Support', 'Safety', 'Workflow'];

  for (const key of keys) grouped.set(key, []);
  for (const [metricId, result] of Object.entries(scorerResults)) {
    const group = getMetricGroup(metricId);
    grouped.get(group)?.push({ metricId, score: result?.score ?? null });
  }

  return keys.map(group => {
    const items = grouped.get(group) ?? [];
    if (items.length === 0) return `- ${group}: no metrics`;
    const rendered = items.map(item => `${item.metricId}=${item.score}`).join(', ');
    return `- ${group}: ${rendered}`;
  });
}

export async function runClinicalExtractionEval() {
  console.log('\n=== Starting Clinical Extraction Eval ===');
  console.log(`Dataset size: ${extractionEvalDataset.length}`);
  console.log(
    'Scorers by group: Extraction (accuracy, precision, recall, completeness), Support (coverage, unsupported-penalty), Safety (no-advice, PHI-minimization), Workflow (json-parse, non-empty-output)',
  );

  let itemCount = 0;
  return runEvals({
    target: clinicalExtractionAgent,
    data: extractionEvalDataset,
    scorers: [
      extractionAccuracyScorer,
      extractionPrecisionScorer,
      extractionRecallScorer,
      extractionCompletenessScorer,
      supportClaimCoverageScorer,
      supportUnsupportedClaimPenaltyScorer,
      safetyNoAdviceScorer,
      safetyPhiMinimizationScorer,
      workflowJsonParseScorer,
      workflowNonEmptyOutputScorer,
    ],
    concurrency: 1,
    onItemComplete: ({ item, scorerResults }) => {
      itemCount += 1;
      const preview = typeof item.input === 'string' ? item.input.slice(0, 120) : JSON.stringify(item.input);
      const compactScores = Object.fromEntries(
        Object.entries(scorerResults).map(([metricId, result]) => [metricId, result?.score ?? null]),
      );
      const metricRows = formatMetricRows(
        scorerResults as Record<string, { score?: number | null; reason?: string } | undefined>,
      );
      const groupedSummaryRows = formatGroupedMetricSummary(
        scorerResults as Record<string, { score?: number | null } | undefined>,
      );

      console.log(`\n--- Item ${itemCount}/${extractionEvalDataset.length} complete ---`);
      console.log(`Input preview: ${preview}${typeof item.input === 'string' && item.input.length > 120 ? '...' : ''}`);
      console.log('\nInput (full):');
      console.log(typeof item.input === 'string' ? item.input : toPrettyJson(item.input));
      console.log('\nGround truth:');
      console.log(toPrettyJson(item.groundTruth));
      console.log('Metric scores:', compactScores);
      console.log('\nGrouped metric summary:');
      for (const row of groupedSummaryRows) console.log(row);
      console.log('\nMetric details:');
      for (const row of metricRows) console.log(row);
    },
  });
}

if (import.meta.main) {
  const result = await runClinicalExtractionEval();
  console.log('\n=== Evaluation complete ===');
  console.log('Average scores:');
  console.log(result.scores);
  console.log('Summary:');
  console.log(result.summary);
  console.log('\nRaw result payload:');
  console.log(toPrettyJson(result));
}

