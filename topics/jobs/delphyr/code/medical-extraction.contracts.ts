import { z } from 'zod';

export const clinicalExtractionSchema = z.object({
  summary: z.string().default(''),
  problems: z.array(z.object({ name: z.string() })).default([]),
  medications: z
    .array(
      z.object({
        name: z.string(),
        dose: z.string().optional(),
        frequency: z.string().optional(),
      }),
    )
    .default([]),
  allergies: z
    .array(
      z.object({
        substance: z.string(),
        reaction: z.string().optional(),
      }),
    )
    .default([]),
  vitals: z
    .array(
      z.object({
        name: z.string(),
        value: z.string(),
      }),
    )
    .default([]),
});

export type ClinicalExtraction = z.infer<typeof clinicalExtractionSchema>;
export type SectionName = 'summary' | 'problems' | 'medications' | 'allergies' | 'vitals';

export type CanonicalFact = {
  section: Exclude<SectionName, 'summary'>;
  key: string;
  exact: string;
  supportTerms: string[];
};

export type ExtractionStats = {
  rawOutputText: string;
  sourceText: string;
  normalizedSourceText: string;
  predicted: ClinicalExtraction;
  expected: ClinicalExtraction;
  predictedFacts: CanonicalFact[];
  expectedFacts: CanonicalFact[];
  predictedCount: number;
  expectedCount: number;
  exactMatches: number;
  overlappingKeyCount: number;
  supportedPredictedCount: number;
  unsupportedPredictedCount: number;
  parseableJson: boolean;
  requiredSections: SectionName[];
  coveredSections: number;
};

export type EvalDatasetItem = {
  input: string;
  groundTruth: ClinicalExtraction;
};

