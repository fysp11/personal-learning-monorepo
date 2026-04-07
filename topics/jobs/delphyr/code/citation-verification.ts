/**
 * Citation Verification Pipeline — Delphyr Context
 *
 * Demonstrates claim-level citation verification for medical RAG outputs.
 * Delphyr's public messaging emphasizes exact, verifiable source quotes
 * rather than vague references. This experiment implements that concept.
 *
 * No LLM calls — uses deterministic string matching to show the pattern.
 * In production, you'd use semantic similarity for fuzzy claim-to-source matching.
 */

// ─── Types ─────────────────────────────────────────────────────────

type Citation = {
  claimText: string;
  sourcePassage: string;
  sourceDocumentId: string;
};

type VerifiedCitation = Citation & {
  verificationStatus: 'supported' | 'partial' | 'unsupported';
  matchScore: number;
  matchedTerms: string[];
  unmatchedTerms: string[];
};

type SourceDocument = {
  id: string;
  content: string;
  type: 'clinical_note' | 'lab_result' | 'guideline' | 'correspondence';
};

type RAGResponse = {
  responseText: string;
  citations: Citation[];
  sourceDocuments: SourceDocument[];
};

// ─── Verification Logic ────────────────────────────────────────────

function normalizeForComparison(text: string): string {
  return text
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .replace(/[^\w\s/%.,-]/g, '')
    .trim();
}

function extractKeyTerms(text: string): string[] {
  const normalized = normalizeForComparison(text);
  // Extract meaningful terms (skip very short words)
  const words = normalized.split(/\s+/).filter(w => w.length > 2);

  // Also extract numeric patterns (dosages, values, dates)
  const numbers = text.match(/\d+(?:[.,]\d+)?(?:\s*(?:mg|ml|mmol|%|mmhg|bpm|kg))?/gi) ?? [];

  return [...new Set([...words, ...numbers.map(n => n.toLowerCase().trim())])];
}

function verifyCitation(citation: Citation, sourceDocuments: RAGResponse['sourceDocuments']): VerifiedCitation {
  const sourceDoc = sourceDocuments.find(d => d.id === citation.sourceDocumentId);

  if (!sourceDoc) {
    return {
      ...citation,
      verificationStatus: 'unsupported',
      matchScore: 0,
      matchedTerms: [],
      unmatchedTerms: extractKeyTerms(citation.claimText),
    };
  }

  const claimTerms = extractKeyTerms(citation.claimText);
  const normalizedSource = normalizeForComparison(sourceDoc.content);
  const normalizedPassage = normalizeForComparison(citation.sourcePassage);

  // Check if the cited passage actually exists in the source document
  const passageTerms = extractKeyTerms(citation.sourcePassage);
  const passageInSource = passageTerms.filter(t => normalizedSource.includes(t));
  const passageMatchRate = passageTerms.length > 0 ? passageInSource.length / passageTerms.length : 0;

  // Check if the claim terms are present in the cited passage
  const matchedTerms = claimTerms.filter(t => normalizedPassage.includes(t) || normalizedSource.includes(t));
  const unmatchedTerms = claimTerms.filter(t => !normalizedPassage.includes(t) && !normalizedSource.includes(t));

  const claimMatchRate = claimTerms.length > 0 ? matchedTerms.length / claimTerms.length : 0;

  // Combined score: passage must exist in source AND claim must be supported by passage
  const matchScore = Math.round(((passageMatchRate + claimMatchRate) / 2) * 100) / 100;

  let verificationStatus: 'supported' | 'partial' | 'unsupported';
  if (matchScore >= 0.8) {
    verificationStatus = 'supported';
  } else if (matchScore >= 0.5) {
    verificationStatus = 'partial';
  } else {
    verificationStatus = 'unsupported';
  }

  return {
    ...citation,
    verificationStatus,
    matchScore,
    matchedTerms,
    unmatchedTerms,
  };
}

// ─── Aggregate Metrics ─────────────────────────────────────────────

type CitationMetrics = {
  totalCitations: number;
  supported: number;
  partial: number;
  unsupported: number;
  supportRate: number;
  averageMatchScore: number;
  trustworthy: boolean; // all citations supported or partial, none unsupported
};

function computeCitationMetrics(verified: VerifiedCitation[]): CitationMetrics {
  const total = verified.length;
  const supported = verified.filter(v => v.verificationStatus === 'supported').length;
  const partial = verified.filter(v => v.verificationStatus === 'partial').length;
  const unsupported = verified.filter(v => v.verificationStatus === 'unsupported').length;
  const avgScore = total > 0 ? verified.reduce((sum, v) => sum + v.matchScore, 0) / total : 0;

  return {
    totalCitations: total,
    supported,
    partial,
    unsupported,
    supportRate: total > 0 ? Math.round(((supported + partial) / total) * 100) / 100 : 0,
    averageMatchScore: Math.round(avgScore * 100) / 100,
    trustworthy: unsupported === 0 && total > 0,
  };
}

// ─── Demo Scenarios ────────────────────────────────────────────────

const scenarios: { name: string; response: RAGResponse }[] = [
  {
    name: 'Well-cited patient summary',
    response: {
      responseText:
        'Patient presents with hypertension (BP 145/92 mmHg) and is currently on Lisinopril 10mg daily. Recent lab results show creatinine at 1.2 mg/dL.',
      citations: [
        {
          claimText: 'hypertension with BP 145/92 mmHg',
          sourcePassage: 'Blood pressure measured at 145/92 mmHg, consistent with stage 1 hypertension',
          sourceDocumentId: 'note-001',
        },
        {
          claimText: 'currently on Lisinopril 10mg daily',
          sourcePassage: 'Current medications: Lisinopril 10mg once daily',
          sourceDocumentId: 'note-001',
        },
        {
          claimText: 'creatinine at 1.2 mg/dL',
          sourcePassage: 'Creatinine: 1.2 mg/dL (within normal range)',
          sourceDocumentId: 'lab-001',
        },
      ],
      sourceDocuments: [
        {
          id: 'note-001',
          type: 'clinical_note',
          content:
            'Patient visit 2026-03-10. Chief complaint: routine follow-up for hypertension. Blood pressure measured at 145/92 mmHg, consistent with stage 1 hypertension. Current medications: Lisinopril 10mg once daily. No reported side effects. Patient reports good adherence.',
        },
        {
          id: 'lab-001',
          type: 'lab_result',
          content:
            'Lab results 2026-03-08. Complete metabolic panel. Creatinine: 1.2 mg/dL (within normal range). eGFR: 78 mL/min. Potassium: 4.1 mmol/L. Sodium: 139 mmol/L.',
        },
      ],
    },
  },
  {
    name: 'Partially supported with hallucinated detail',
    response: {
      responseText:
        'Patient has a known penicillin allergy causing anaphylaxis. They were recently prescribed Amoxicillin 500mg three times daily for a respiratory infection.',
      citations: [
        {
          claimText: 'penicillin allergy causing anaphylaxis',
          sourcePassage: 'Allergies: Penicillin - rash',
          sourceDocumentId: 'note-002',
        },
        {
          claimText: 'prescribed Amoxicillin 500mg three times daily',
          sourcePassage: 'New prescription: Amoxicillin 500mg TID x 7 days',
          sourceDocumentId: 'note-002',
        },
      ],
      sourceDocuments: [
        {
          id: 'note-002',
          type: 'clinical_note',
          content:
            'Patient visit 2026-03-12. Allergies: Penicillin - rash (NOT anaphylaxis). Presenting with upper respiratory symptoms x 5 days. New prescription: Amoxicillin 500mg TID x 7 days. Note: cross-reactivity risk discussed with patient given penicillin sensitivity.',
        },
      ],
    },
  },
  {
    name: 'Citation pointing to nonexistent source',
    response: {
      responseText: 'Patient has diabetes mellitus type 2 with HbA1c of 7.8%.',
      citations: [
        {
          claimText: 'diabetes mellitus type 2 with HbA1c of 7.8%',
          sourcePassage: 'Diagnosis: DM2, most recent HbA1c 7.8%',
          sourceDocumentId: 'note-999', // doesn't exist
        },
      ],
      sourceDocuments: [
        {
          id: 'note-003',
          type: 'clinical_note',
          content: 'Routine follow-up visit. No new concerns. Continue current management plan.',
        },
      ],
    },
  },
];

// ─── Run ───────────────────────────────────────────────────────────

console.log('=== Citation Verification Pipeline Demo ===\n');

for (const scenario of scenarios) {
  console.log(`--- Scenario: ${scenario.name} ---`);
  console.log(`  Response: "${scenario.response.responseText.slice(0, 80)}..."`);
  console.log(`  Citations: ${scenario.response.citations.length}`);
  console.log(`  Source documents: ${scenario.response.sourceDocuments.length}\n`);

  const verified = scenario.response.citations.map(c => verifyCitation(c, scenario.response.sourceDocuments));

  for (const v of verified) {
    const icon = v.verificationStatus === 'supported' ? '✓' : v.verificationStatus === 'partial' ? '~' : '✕';
    console.log(`  ${icon} [${v.verificationStatus}] "${v.claimText.slice(0, 50)}..."`);
    console.log(`    Score: ${v.matchScore}`);
    if (v.unmatchedTerms.length > 0) {
      console.log(`    Unmatched terms: ${v.unmatchedTerms.join(', ')}`);
    }
  }

  const metrics = computeCitationMetrics(verified);
  console.log(`\n  Metrics:`);
  console.log(`    Support rate: ${metrics.supportRate}`);
  console.log(`    Average match score: ${metrics.averageMatchScore}`);
  console.log(`    Trustworthy: ${metrics.trustworthy}`);
  console.log(`    Breakdown: ${metrics.supported} supported / ${metrics.partial} partial / ${metrics.unsupported} unsupported`);
  console.log();
}

console.log('=== Verification Complete ===');
