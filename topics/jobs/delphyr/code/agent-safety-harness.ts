/**
 * Agent Safety Harness with Commit/Rollback
 *
 * Demonstrates transactional agent patterns for clinical AI workflows:
 * - Staged actions (propose before executing)
 * - Per-action confidence scoring and routing
 * - Commit/rollback semantics with compensating actions
 * - Full audit trail for compliance
 * - Escalation paths for low-confidence actions
 *
 * This is the "highest signal" experiment for Delphyr interviews:
 * "In clinical workflows, you need both action-level confidence routing
 *  AND the ability to rollback an entire workflow if a downstream action
 *  reveals the upstream was wrong."
 */

import { z } from 'zod';

// ── Types ──────────────────────────────────────────────────────

const ActionStatus = z.enum(['staged', 'committed', 'rolled_back', 'failed', 'needs_review']);
type ActionStatus = z.infer<typeof ActionStatus>;

const ConfidenceLevel = z.enum(['high', 'medium', 'low']);
type ConfidenceLevel = z.infer<typeof ConfidenceLevel>;

interface StagedAction<T = unknown> {
  actionId: string;
  description: string;
  toolName: string;
  toolArgs: Record<string, unknown>;
  confidence: number;
  confidenceLevel: ConfidenceLevel;
  status: ActionStatus;
  result?: T;
  error?: string;
  stagedAt: Date;
  resolvedAt?: Date;
  compensatingAction?: () => Promise<void>;
}

interface WorkflowTrace {
  workflowId: string;
  patientId: string;
  startedAt: Date;
  completedAt?: Date;
  actions: StagedAction[];
  outcome: 'completed' | 'rolled_back' | 'escalated' | 'in_progress';
  escalationReason?: string;
  auditLog: AuditEntry[];
}

interface AuditEntry {
  timestamp: Date;
  actionId: string;
  event: 'staged' | 'committed' | 'rolled_back' | 'escalated' | 'reviewed';
  detail: string;
  actor: 'system' | 'human';
}

interface ConfidenceThresholds {
  autoCommit: number;  // >= this → auto-commit
  review: number;      // >= this → needs human review
  // < review → auto-reject/rollback
}

interface RoutingDecision {
  action: StagedAction;
  decision: 'auto_commit' | 'needs_review' | 'rejected';
  reason: string;
}

// ── Safety Harness ─────────────────────────────────────────────

class AgentSafetyHarness {
  private thresholds: ConfidenceThresholds;
  private workflow: WorkflowTrace;

  constructor(
    workflowId: string,
    patientId: string,
    thresholds: ConfidenceThresholds = { autoCommit: 0.9, review: 0.6 }
  ) {
    this.thresholds = thresholds;
    this.workflow = {
      workflowId,
      patientId,
      startedAt: new Date(),
      actions: [],
      outcome: 'in_progress',
      auditLog: [],
    };
  }

  /**
   * Stage an action without executing it.
   * Returns a routing decision based on confidence.
   */
  stage(params: {
    description: string;
    toolName: string;
    toolArgs: Record<string, unknown>;
    confidence: number;
    compensatingAction?: () => Promise<void>;
  }): RoutingDecision {
    const confidenceLevel = this.classifyConfidence(params.confidence);
    const action: StagedAction = {
      actionId: `action-${this.workflow.actions.length + 1}`,
      description: params.description,
      toolName: params.toolName,
      toolArgs: params.toolArgs,
      confidence: params.confidence,
      confidenceLevel,
      status: 'staged',
      stagedAt: new Date(),
      compensatingAction: params.compensatingAction,
    };

    this.workflow.actions.push(action);
    this.audit(action.actionId, 'staged', `Staged: ${params.description} (confidence: ${params.confidence.toFixed(2)})`);

    return this.route(action);
  }

  /**
   * Route a staged action based on confidence thresholds.
   */
  private route(action: StagedAction): RoutingDecision {
    if (action.confidence >= this.thresholds.autoCommit) {
      return {
        action,
        decision: 'auto_commit',
        reason: `Confidence ${action.confidence.toFixed(2)} >= auto-commit threshold ${this.thresholds.autoCommit}`,
      };
    }

    if (action.confidence >= this.thresholds.review) {
      action.status = 'needs_review';
      this.audit(action.actionId, 'escalated', `Needs review: confidence ${action.confidence.toFixed(2)} in review range [${this.thresholds.review}, ${this.thresholds.autoCommit})`);
      return {
        action,
        decision: 'needs_review',
        reason: `Confidence ${action.confidence.toFixed(2)} in review range`,
      };
    }

    // Below review threshold → reject
    action.status = 'rolled_back';
    action.resolvedAt = new Date();
    this.audit(action.actionId, 'rolled_back', `Rejected: confidence ${action.confidence.toFixed(2)} below review threshold ${this.thresholds.review}`);
    return {
      action,
      decision: 'rejected',
      reason: `Confidence ${action.confidence.toFixed(2)} below minimum threshold ${this.thresholds.review}`,
    };
  }

  /**
   * Commit a staged action (execute it).
   */
  commit<T>(actionId: string, result: T): StagedAction<T> {
    const action = this.findAction(actionId);
    if (action.status !== 'staged' && action.status !== 'needs_review') {
      throw new Error(`Cannot commit action ${actionId} in status ${action.status}`);
    }

    action.status = 'committed';
    action.result = result;
    action.resolvedAt = new Date();
    this.audit(actionId, 'committed', `Committed: ${action.description}`);
    return action as StagedAction<T>;
  }

  /**
   * Approve a needs_review action (human-in-the-loop).
   */
  approve(actionId: string): RoutingDecision {
    const action = this.findAction(actionId);
    if (action.status !== 'needs_review') {
      throw new Error(`Cannot approve action ${actionId} in status ${action.status}`);
    }

    this.audit(actionId, 'reviewed', `Human approved: ${action.description}`, 'human');
    action.status = 'staged'; // Reset to staged so it can be committed
    return {
      action,
      decision: 'auto_commit',
      reason: 'Human approved',
    };
  }

  /**
   * Rollback a single committed action using its compensating action.
   */
  async rollback(actionId: string, reason: string): Promise<void> {
    const action = this.findAction(actionId);
    if (action.status !== 'committed') {
      throw new Error(`Cannot rollback action ${actionId} in status ${action.status}`);
    }

    if (action.compensatingAction) {
      await action.compensatingAction();
    }

    action.status = 'rolled_back';
    action.resolvedAt = new Date();
    this.audit(actionId, 'rolled_back', `Rolled back: ${reason}`);
  }

  /**
   * Rollback ALL committed actions in reverse order.
   * Used when a downstream action reveals upstream was wrong.
   */
  async rollbackAll(reason: string): Promise<void> {
    const committed = this.workflow.actions
      .filter(a => a.status === 'committed')
      .reverse();

    for (const action of committed) {
      await this.rollback(action.actionId, reason);
    }

    this.workflow.outcome = 'rolled_back';
    this.workflow.completedAt = new Date();
  }

  /**
   * Escalate the entire workflow to a human.
   */
  escalate(reason: string): void {
    this.workflow.outcome = 'escalated';
    this.workflow.escalationReason = reason;
    this.workflow.completedAt = new Date();
    this.audit('workflow', 'escalated', `Workflow escalated: ${reason}`);
  }

  /**
   * Complete the workflow successfully.
   */
  complete(): WorkflowTrace {
    this.workflow.outcome = 'completed';
    this.workflow.completedAt = new Date();
    return this.workflow;
  }

  /**
   * Get the full audit trail for compliance.
   */
  getAuditTrail(): AuditEntry[] {
    return [...this.workflow.auditLog];
  }

  /**
   * Get workflow summary for reporting.
   */
  getSummary(): {
    workflowId: string;
    patientId: string;
    outcome: string;
    totalActions: number;
    committed: number;
    rolledBack: number;
    needsReview: number;
    avgConfidence: number;
    minConfidence: number;
  } {
    const actions = this.workflow.actions;
    const confidences = actions.map(a => a.confidence);
    return {
      workflowId: this.workflow.workflowId,
      patientId: this.workflow.patientId,
      outcome: this.workflow.outcome,
      totalActions: actions.length,
      committed: actions.filter(a => a.status === 'committed').length,
      rolledBack: actions.filter(a => a.status === 'rolled_back').length,
      needsReview: actions.filter(a => a.status === 'needs_review').length,
      avgConfidence: confidences.length > 0 ? confidences.reduce((a, b) => a + b, 0) / confidences.length : 0,
      minConfidence: confidences.length > 0 ? Math.min(...confidences) : 0,
    };
  }

  private classifyConfidence(score: number): ConfidenceLevel {
    if (score >= this.thresholds.autoCommit) return 'high';
    if (score >= this.thresholds.review) return 'medium';
    return 'low';
  }

  private findAction(actionId: string): StagedAction {
    const action = this.workflow.actions.find(a => a.actionId === actionId);
    if (!action) throw new Error(`Action ${actionId} not found`);
    return action;
  }

  private audit(actionId: string, event: AuditEntry['event'], detail: string, actor: 'system' | 'human' = 'system'): void {
    this.workflow.auditLog.push({
      timestamp: new Date(),
      actionId,
      event,
      detail,
      actor,
    });
  }
}

// ── Clinical MDT Preparation Demo ──────────────────────────────

/**
 * Simulates a clinical MDT preparation workflow using the safety harness.
 * Each step is staged, confidence-scored, and routed.
 */
async function runMDTPrepWorkflow(): Promise<void> {
  console.log('═══════════════════════════════════════════════════');
  console.log('  Agent Safety Harness — MDT Preparation Demo');
  console.log('═══════════════════════════════════════════════════\n');

  const harness = new AgentSafetyHarness(
    'mdt-prep-2026-04-08',
    'patient-12345',
    { autoCommit: 0.9, review: 0.6 }
  );

  // ── Step 1: Retrieve patient timeline (high confidence) ──

  console.log('Step 1: Retrieve patient timeline');
  const timelineDecision = harness.stage({
    description: 'Retrieve patient clinical timeline (last 90 days)',
    toolName: 'retrieve_patient_timeline',
    toolArgs: { patientId: 'patient-12345', lookbackDays: 90 },
    confidence: 0.98,
    compensatingAction: async () => {
      console.log('  [Compensating] Clearing cached timeline data');
    },
  });
  console.log(`  Decision: ${timelineDecision.decision} (${timelineDecision.reason})`);

  if (timelineDecision.decision === 'auto_commit') {
    harness.commit(timelineDecision.action.actionId, {
      events: [
        { date: '2026-03-15', type: 'lab', detail: 'Creatinine 1.8 mg/dL (elevated)' },
        { date: '2026-03-18', type: 'imaging', detail: 'CT Abdomen — 2.3cm lesion, stable' },
        { date: '2026-03-22', type: 'consult', detail: 'Nephrology — recommends monitoring' },
        { date: '2026-04-01', type: 'lab', detail: 'Creatinine 2.1 mg/dL (rising)' },
      ],
    });
    console.log('  ✓ Committed\n');
  }

  // ── Step 2: Extract clinical question (medium confidence) ──

  console.log('Step 2: Identify clinical question');
  const questionDecision = harness.stage({
    description: 'Extract clinical question from referral and trajectory',
    toolName: 'extract_clinical_question',
    toolArgs: { patientId: 'patient-12345', context: 'rising creatinine, stable lesion' },
    confidence: 0.72,
    compensatingAction: async () => {
      console.log('  [Compensating] Removing extracted clinical question');
    },
  });
  console.log(`  Decision: ${questionDecision.decision} (${questionDecision.reason})`);

  if (questionDecision.decision === 'needs_review') {
    console.log('  ⏸ Awaiting human review...');
    // Simulate human approval
    const approved = harness.approve(questionDecision.action.actionId);
    console.log('  ✓ Human approved');
    harness.commit(approved.action.actionId, {
      question: 'Should treatment plan be adjusted given renal trajectory (creatinine 1.8→2.1 over 2 weeks)?',
      priorMDT: 'Continue current protocol, reassess in 6 weeks (2026-02-10)',
    });
    console.log('  ✓ Committed\n');
  }

  // ── Step 3: Match clinical guidelines (high confidence) ──

  console.log('Step 3: Match clinical guidelines');
  const guidelineDecision = harness.stage({
    description: 'Retrieve relevant clinical guideline sections',
    toolName: 'match_guidelines',
    toolArgs: { diagnosis: 'renal cell carcinoma', query: 'nephrotoxicity management' },
    confidence: 0.94,
  });
  console.log(`  Decision: ${guidelineDecision.decision} (${guidelineDecision.reason})`);

  if (guidelineDecision.decision === 'auto_commit') {
    harness.commit(guidelineDecision.action.actionId, {
      guidelines: [
        { source: 'ESMO RCC 2024, §5.3', recommendation: 'Monitor renal function every 2 weeks during treatment', evidence: 'IIA' },
        { source: 'NVvH Nefrotoxiciteit, §3.1', recommendation: 'Creatinine rise >30% warrants nephrology consultation', evidence: 'III' },
      ],
    });
    console.log('  ✓ Committed\n');
  }

  // ── Step 4: Detect information gaps (low confidence → rejected) ──

  console.log('Step 4: Detect information gaps');
  const gapDecision = harness.stage({
    description: 'Detect missing information for MDT discussion',
    toolName: 'detect_gaps',
    toolArgs: { patientId: 'patient-12345', mdtType: 'oncology' },
    confidence: 0.45, // Low: gap detection rules are uncertain
  });
  console.log(`  Decision: ${gapDecision.decision} (${gapDecision.reason})`);
  console.log('  ⚠ Action rejected due to low confidence');
  console.log('  → Gap detection will be performed manually by the clinician\n');

  // ── Step 5: Generate MDT brief (medium confidence) ──

  console.log('Step 5: Generate MDT brief');
  const briefDecision = harness.stage({
    description: 'Assemble structured MDT case brief',
    toolName: 'generate_mdt_brief',
    toolArgs: { patientId: 'patient-12345', includeGaps: false },
    confidence: 0.85,
  });
  console.log(`  Decision: ${briefDecision.decision} (${briefDecision.reason})`);

  if (briefDecision.decision === 'needs_review') {
    console.log('  ⏸ Awaiting human review...');
    const approved = harness.approve(briefDecision.action.actionId);
    console.log('  ✓ Human approved');
    harness.commit(approved.action.actionId, {
      brief: 'Patient with rising creatinine under oncology treatment. MDT question: adjust treatment plan?',
      sources: ['Lab #4521', 'Lab #4587', 'Radiology #892', 'Consult #1203'],
      confidenceNote: 'Gap detection was below threshold — manual review of completeness recommended',
    });
    console.log('  ✓ Committed\n');
  }

  // ── Complete workflow ──

  const trace = harness.complete();

  // ── Print summary ──

  console.log('═══════════════════════════════════════════════════');
  console.log('  Workflow Summary');
  console.log('═══════════════════════════════════════════════════\n');

  const summary = harness.getSummary();
  console.log(`  Workflow: ${summary.workflowId}`);
  console.log(`  Patient: ${summary.patientId}`);
  console.log(`  Outcome: ${summary.outcome}`);
  console.log(`  Total actions: ${summary.totalActions}`);
  console.log(`  Committed: ${summary.committed}`);
  console.log(`  Rolled back: ${summary.rolledBack}`);
  console.log(`  Needs review: ${summary.needsReview}`);
  console.log(`  Avg confidence: ${summary.avgConfidence.toFixed(2)}`);
  console.log(`  Min confidence: ${summary.minConfidence.toFixed(2)}`);
  console.log();

  // ── Audit trail ──

  console.log('═══════════════════════════════════════════════════');
  console.log('  Audit Trail (Compliance)');
  console.log('═══════════════════════════════════════════════════\n');

  for (const entry of harness.getAuditTrail()) {
    const time = entry.timestamp.toISOString().slice(11, 23);
    const actor = entry.actor === 'human' ? '[HUMAN]' : '[SYSTEM]';
    console.log(`  ${time} ${actor} ${entry.detail}`);
  }
  console.log();

  // ── Demonstrate rollback scenario ──

  console.log('═══════════════════════════════════════════════════');
  console.log('  Rollback Demo — Downstream Invalidation');
  console.log('═══════════════════════════════════════════════════\n');

  const rollbackHarness = new AgentSafetyHarness(
    'mdt-prep-rollback-demo',
    'patient-67890',
    { autoCommit: 0.9, review: 0.6 }
  );

  // Step 1: High confidence extraction
  console.log('Step 1: Extract medication list (high confidence)');
  const medDecision = rollbackHarness.stage({
    description: 'Extract current medication list',
    toolName: 'extract_medications',
    toolArgs: { patientId: 'patient-67890' },
    confidence: 0.95,
    compensatingAction: async () => {
      console.log('  [Compensating] Removing extracted medication list from brief');
    },
  });
  rollbackHarness.commit(medDecision.action.actionId, {
    medications: ['Metformin 500mg BID', 'Lisinopril 10mg QD'],
  });
  console.log('  ✓ Committed: Metformin 500mg BID, Lisinopril 10mg QD\n');

  // Step 2: Check interactions — discovers the extraction missed an allergy
  console.log('Step 2: Check drug interactions (finds conflict!)');
  const interactionDecision = rollbackHarness.stage({
    description: 'Check drug-drug interactions against patient allergies',
    toolName: 'check_interactions',
    toolArgs: { medications: ['Metformin', 'Lisinopril'], patientId: 'patient-67890' },
    confidence: 0.92,
  });
  rollbackHarness.commit(interactionDecision.action.actionId, {
    conflict: true,
    detail: 'Patient has documented ACE inhibitor sensitivity — Lisinopril flagged',
    source: 'Allergy record from 2025-11-03',
  });
  console.log('  ⚠ Conflict detected: ACE inhibitor sensitivity vs. Lisinopril');
  console.log('  → Downstream action invalidates upstream medication list\n');

  // Rollback ALL — the medication extraction was incomplete (missed allergy context)
  console.log('Rolling back entire workflow...');
  await rollbackHarness.rollbackAll(
    'Downstream interaction check revealed missed allergy — medication list extraction was incomplete'
  );
  rollbackHarness.escalate('Medication-allergy conflict requires clinician review');
  console.log('  ✓ All actions rolled back');
  console.log('  ✓ Workflow escalated to clinician\n');

  const rollbackSummary = rollbackHarness.getSummary();
  console.log(`  Outcome: ${rollbackSummary.outcome}`);
  console.log(`  Committed: ${rollbackSummary.committed}`);
  console.log(`  Rolled back: ${rollbackSummary.rolledBack}`);
  console.log();

  console.log('═══════════════════════════════════════════════════');
  console.log('  Key Takeaways');
  console.log('═══════════════════════════════════════════════════\n');
  console.log('  1. Every action is staged before execution — no silent side effects');
  console.log('  2. Confidence-based routing: auto-commit, human review, or reject');
  console.log('  3. Compensating actions enable rollback of committed work');
  console.log('  4. Full audit trail for MDR/compliance requirements');
  console.log('  5. Downstream findings can invalidate upstream — rollback-all is essential');
  console.log('  6. Escalation path ensures the system never silently proceeds when uncertain');
  console.log();
}

// ── Run ────────────────────────────────────────────────────────

runMDTPrepWorkflow().catch(console.error);
