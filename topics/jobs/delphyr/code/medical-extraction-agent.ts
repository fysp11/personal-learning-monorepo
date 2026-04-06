export * from './medical-extraction.contracts';
export * from './medical-extraction.impl';
export * from './medical-extraction.experiments';

import { runClinicalExtractionEval } from './medical-extraction.experiments';

if (import.meta.main) {
  const result = await runClinicalExtractionEval();
  console.log('\n=== Evaluation complete ===');
  console.log('Average scores:');
  console.log(result.scores);
  console.log('Summary:');
  console.log(result.summary);
  console.log('\nRaw result payload:');
  console.log(JSON.stringify(result, null, 2));
}

