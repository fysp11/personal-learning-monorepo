/**
 * Multi-Agent System (MAS) Coordination Pattern for Fintech Accounting
 *
 * This demo shows the orchestration and coordination patterns for a
 * distributed multi-agent accounting system — typed agent boundaries,
 * confidence propagation, circuit breaking, and end-to-end observability.
 *
 * No LLM calls — this is a structural/architectural demo, not an AI demo.
 * The focus is on the coordination layer, not the intelligence layer.
 */

import { z } from 'zod';

// ─── Agent Contracts ───────────────────────────────────────────────

const ConfidenceLevel = z.enum(['high', 'medium', 'low']);
type ConfidenceLevel = z.infer<typeof ConfidenceLevel>;

const AgentResult = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    agentId: z.string(),
    success: z.boolean(),
    confidence: ConfidenceLevel,
    data: dataSchema.optional(),
    error: z.string().optional(),
    durationMs: z.number(),
    metadata: z.record(z.string(), z.unknown()).optional(),
  });

// ─── Domain Types ──────────────────────────────────────────────────

const DocumentSchema = z.object({
  id: z.string(),
  type: z.enum(['invoice', 'receipt', 'bank_statement', 'tax_document']),
  rawText: z.string(),
  sourceUrl: z.string().optional(),
});

const ExtractedDataSchema = z.object({
  documentId: z.string(),
  vendor: z.string().optional(),
  amount: z.number().optional(),
  currency: z.string().optional(),
  date: z.string().optional(),
  lineItems: z.array(z.object({ description: z.string(), amount: z.number() })).optional(),
  taxRate: z.number().optional(),
});

const ReconciliationSchema = z.object({
  documentId: z.string(),
  matchedTransactionId: z.string().optional(),
  matchType: z.enum(['exact', 'fuzzy', 'unmatched']),
  matchScore: z.number(),
});

const CategorizationSchema = z.object({
  documentId: z.string(),
  category: z.string(),
  taxTreatment: z.string(),
  confidence: ConfidenceLevel,
});

type Document = z.infer<typeof DocumentSchema>;
type ExtractedData = z.infer<typeof ExtractedDataSchema>;
type Reconciliation = z.infer<typeof ReconciliationSchema>;
type Categorization = z.infer<typeof CategorizationSchema>;

// ─── Trace / Observability ─────────────────────────────────────────

type TraceEntry = {
  timestamp: number;
  agentId: string;
  event: 'start' | 'complete' | 'error' | 'escalate' | 'circuit_break';
  confidence?: ConfidenceLevel;
  durationMs?: number;
  details?: string;
};

class WorkflowTrace {
  readonly correlationId: string;
  private entries: TraceEntry[] = [];

  constructor(correlationId: string) {
    this.correlationId = correlationId;
  }

  log(entry: Omit<TraceEntry, 'timestamp'>) {
    this.entries.push({ ...entry, timestamp: Date.now() });
  }

  summary(): { totalDurationMs: number; agentCount: number; escalated: boolean; entries: TraceEntry[] } {
    const starts = this.entries.filter(e => e.event === 'start');
    const completes = this.entries.filter(e => e.event === 'complete');
    const escalations = this.entries.filter(e => e.event === 'escalate');
    const firstStart = starts[0]?.timestamp ?? 0;
    const lastComplete = completes[completes.length - 1]?.timestamp ?? firstStart;

    return {
      totalDurationMs: lastComplete - firstStart,
      agentCount: new Set(starts.map(e => e.agentId)).size,
      escalated: escalations.length > 0,
      entries: this.entries,
    };
  }
}

// ─── Agent Base ────────────────────────────────────────────────────

type AgentConfig = {
  id: string;
  confidenceThreshold: ConfidenceLevel;
  circuitBreakOnUpstreamLow: boolean;
};

abstract class BaseAgent<TInput, TOutput> {
  constructor(protected config: AgentConfig) {}

  async execute(input: TInput, trace: WorkflowTrace): Promise<z.infer<ReturnType<typeof AgentResult<z.ZodAny>>>> {
    trace.log({ agentId: this.config.id, event: 'start' });
    const start = Date.now();

    try {
      const result = await this.process(input);
      const durationMs = Date.now() - start;

      trace.log({
        agentId: this.config.id,
        event: 'complete',
        confidence: result.confidence,
        durationMs,
      });

      if (result.confidence === 'low') {
        trace.log({
          agentId: this.config.id,
          event: 'escalate',
          details: 'Low confidence — routing to human review',
        });
      }

      return { ...result, agentId: this.config.id, durationMs };
    } catch (err) {
      const durationMs = Date.now() - start;
      trace.log({
        agentId: this.config.id,
        event: 'error',
        durationMs,
        details: String(err),
      });

      return {
        agentId: this.config.id,
        success: false,
        confidence: 'low' as ConfidenceLevel,
        durationMs,
        error: String(err),
      };
    }
  }

  protected abstract process(input: TInput): Promise<{
    success: boolean;
    confidence: ConfidenceLevel;
    data?: TOutput;
    error?: string;
  }>;
}

// ─── Concrete Agents (simulated, no LLM) ──────────────────────────

class ClassificationAgent extends BaseAgent<Document, { documentType: string; confidence: ConfidenceLevel }> {
  protected async process(input: Document) {
    // Simulate classification based on raw text keywords
    const text = input.rawText.toLowerCase();
    let documentType = 'unknown';
    let confidence: ConfidenceLevel = 'low';

    if (text.includes('invoice') || text.includes('rechnung')) {
      documentType = 'invoice';
      confidence = 'high';
    } else if (text.includes('receipt') || text.includes('quittung')) {
      documentType = 'receipt';
      confidence = 'high';
    } else if (text.includes('statement') || text.includes('kontoauszug')) {
      documentType = 'bank_statement';
      confidence = 'medium';
    }

    return { success: true, confidence, data: { documentType, confidence } };
  }
}

class ExtractionAgent extends BaseAgent<Document, ExtractedData> {
  protected async process(input: Document) {
    // Simulate extraction — in production this would be LLM-powered
    const amountMatch = input.rawText.match(/€?([\d.]+,\d{2})/);
    const hasDate = /\d{2}[./-]\d{2}[./-]\d{4}/.test(input.rawText);
    const hasAmount = !!amountMatch;

    const confidence: ConfidenceLevel = hasAmount && hasDate ? 'high' : hasAmount ? 'medium' : 'low';

    // Parse amount: European format (1.250,00 → 1250.00 or 47,80 → 47.80)
    const firstFind = amountMatch?.[1]
    const parsedAmount = firstFind
      ? parseFloat(firstFind.replace(/\./g, '').replace(',', '.'))
      : undefined;

    const extracted: ExtractedData = {
      documentId: input.id,
      vendor: 'Simulated Vendor GmbH',
      amount: parsedAmount,
      currency: 'EUR',
      date: hasDate ? '2026-03-15' : undefined,
    };

    return { success: true, confidence, data: extracted };
  }
}

class ReconciliationAgent extends BaseAgent<ExtractedData, Reconciliation> {
  private knownTransactions = [
    { id: 'TXN-001', amount: 1250.0, date: '2026-03-15' },
    { id: 'TXN-002', amount: 890.5, date: '2026-03-10' },
  ];

  protected async process(input: ExtractedData) {
    // Simulate reconciliation against known transactions
    const exactMatch = this.knownTransactions.find(
      t => t.amount === input.amount && t.date === input.date,
    );

    if (exactMatch) {
      return {
        success: true,
        confidence: 'high' as ConfidenceLevel,
        data: {
          documentId: input.documentId,
          matchedTransactionId: exactMatch.id,
          matchType: 'exact' as const,
          matchScore: 1.0,
        },
      };
    }

    const fuzzyMatch = this.knownTransactions.find(
      t => input.amount && Math.abs(t.amount - input.amount) < 5,
    );

    if (fuzzyMatch) {
      return {
        success: true,
        confidence: 'medium' as ConfidenceLevel,
        data: {
          documentId: input.documentId,
          matchedTransactionId: fuzzyMatch.id,
          matchType: 'fuzzy' as const,
          matchScore: 0.85,
        },
      };
    }

    return {
      success: true,
      confidence: 'low' as ConfidenceLevel,
      data: {
        documentId: input.documentId,
        matchType: 'unmatched' as const,
        matchScore: 0,
      },
    };
  }
}

class CategorizationAgent extends BaseAgent<
  { extracted: ExtractedData; reconciliation: Reconciliation },
  Categorization
> {
  protected async process(input: { extracted: ExtractedData; reconciliation: Reconciliation }) {
    // Simulate categorization — in production this uses business rules + LLM
    const isReconciled = input.reconciliation.matchType !== 'unmatched';
    const confidence: ConfidenceLevel = isReconciled ? 'high' : 'medium';

    return {
      success: true,
      confidence,
      data: {
        documentId: input.extracted.documentId,
        category: 'Betriebsausgabe', // operating expense
        taxTreatment: 'Vorsteuerabzug', // input tax deduction
        confidence,
      },
    };
  }
}

// ─── Orchestrator ──────────────────────────────────────────────────

type WorkflowOutcome = {
  status: 'completed' | 'escalated' | 'failed';
  reason?: string;
  trace: ReturnType<WorkflowTrace['summary']>;
  results: {
    classification?: unknown;
    extraction?: ExtractedData;
    reconciliation?: Reconciliation;
    categorization?: Categorization;
  };
};

class AccountingPipelineOrchestrator {
  private classificationAgent = new ClassificationAgent({
    id: 'classification',
    confidenceThreshold: 'medium',
    circuitBreakOnUpstreamLow: false,
  });

  private extractionAgent = new ExtractionAgent({
    id: 'extraction',
    confidenceThreshold: 'medium',
    circuitBreakOnUpstreamLow: true,
  });

  private reconciliationAgent = new ReconciliationAgent({
    id: 'reconciliation',
    confidenceThreshold: 'medium',
    circuitBreakOnUpstreamLow: true,
  });

  private categorizationAgent = new CategorizationAgent({
    id: 'categorization',
    confidenceThreshold: 'medium',
    circuitBreakOnUpstreamLow: true,
  });

  async processDocument(doc: Document): Promise<WorkflowOutcome> {
    const trace = new WorkflowTrace(`doc-${doc.id}`);
    const results: WorkflowOutcome['results'] = {};

    // Stage 1: Classification
    const classResult = await this.classificationAgent.execute(doc, trace);
    results.classification = classResult.data;

    if (!classResult.success) {
      return { status: 'failed', reason: 'Classification failed', trace: trace.summary(), results };
    }

    // Stage 2: Extraction
    const extractResult = await this.extractionAgent.execute(doc, trace);
    results.extraction = extractResult.data;

    if (!extractResult.success || extractResult.confidence === 'low') {
      trace.log({ agentId: 'orchestrator', event: 'circuit_break', details: 'Extraction too low confidence' });
      return { status: 'escalated', reason: 'Extraction confidence too low for automated processing', trace: trace.summary(), results };
    }

    // Stage 3: Reconciliation
    const reconResult = await this.reconciliationAgent.execute(extractResult.data!, trace);
    results.reconciliation = reconResult.data;

    // Stage 4: Categorization (even if reconciliation is low, we can still categorize)
    const catResult = await this.categorizationAgent.execute(
      { extracted: extractResult.data!, reconciliation: reconResult.data! },
      trace,
    );
    results.categorization = catResult.data;

    // Determine final workflow outcome based on aggregate confidence
    const confidences = [classResult.confidence, extractResult.confidence, reconResult.confidence, catResult.confidence];
    const hasLow = confidences.includes('low');
    const allHigh = confidences.every(c => c === 'high');

    if (hasLow) {
      return { status: 'escalated', reason: 'One or more stages below confidence threshold', trace: trace.summary(), results };
    }

    return { status: allHigh ? 'completed' : 'completed', trace: trace.summary(), results };
  }
}

// ─── Demo ──────────────────────────────────────────────────────────

async function main() {
  const orchestrator = new AccountingPipelineOrchestrator();

  const testDocs: Document[] = [
    {
      id: 'DOC-001',
      type: 'invoice',
      rawText: 'Rechnung Nr. 2026-0042 — Büromaterial GmbH — Betrag: €1.250,00 — Datum: 15.03.2026',
    },
    {
      id: 'DOC-002',
      type: 'receipt',
      rawText: 'Quittung — Tankstelle — €47,80 — 20.03.2026',
    },
    {
      id: 'DOC-003',
      type: 'invoice',
      rawText: 'Some ambiguous document with no clear amount or date',
    },
  ];

  console.log('=== Accounting MAS Pipeline Demo ===\n');
  console.log(`Processing ${testDocs.length} documents...\n`);

  for (const doc of testDocs) {
    console.log(`--- Document ${doc.id} (${doc.type}) ---`);
    console.log(`  Raw: "${doc.rawText.slice(0, 60)}..."`);

    const outcome = await orchestrator.processDocument(doc);

    console.log(`  Status: ${outcome.status}`);
    if (outcome.reason) console.log(`  Reason: ${outcome.reason}`);
    console.log(`  Agents: ${outcome.trace.agentCount}`);
    console.log(`  Duration: ${outcome.trace.totalDurationMs}ms`);
    console.log(`  Escalated: ${outcome.trace.escalated}`);

    // Show per-agent trace
    for (const entry of outcome.trace.entries) {
      if (entry.event === 'complete') {
        console.log(`    ${entry.agentId}: confidence=${entry.confidence} (${entry.durationMs}ms)`);
      } else if (entry.event === 'escalate') {
        console.log(`    ⚠ ${entry.agentId}: ${entry.details}`);
      } else if (entry.event === 'circuit_break') {
        console.log(`    ✕ ${entry.agentId}: ${entry.details}`);
      }
    }

    if (outcome.results.reconciliation) {
      const r = outcome.results.reconciliation;
      console.log(`  Reconciliation: ${r.matchType} (score=${r.matchScore})`);
    }
    if (outcome.results.categorization) {
      const c = outcome.results.categorization;
      console.log(`  Category: ${c.category} / ${c.taxTreatment} (${c.confidence})`);
    }

    console.log();
  }

  console.log('=== Pipeline Demo Complete ===');
}

main().catch(console.error);
