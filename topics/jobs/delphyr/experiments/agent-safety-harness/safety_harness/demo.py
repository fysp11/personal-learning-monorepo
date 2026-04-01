"""Demo: MDT Meeting Preparation Agent.

Simulates a clinical agent preparing a digital case for a Multi-Disciplinary
Team meeting. Demonstrates the safety harness with realistic clinical actions.
"""

from .core import (
    TransactionalAgent,
    StagedAction,
    ActionSeverity,
    ConfidenceThresholds,
)

# ── Mock Clinical Tools ──────────────────────────────────────────────

MOCK_PATIENT = {
    "id": "P-2024-0731",
    "name": "[REDACTED]",  # pseudonymized
    "age": 62,
    "condition": "Non-small cell lung cancer, Stage IIIA",
    "recent_labs": {
        "date": "2026-03-28",
        "hemoglobin": 12.1,
        "wbc": 7.2,
        "platelets": 245,
        "creatinine": 0.9,
    },
    "imaging": {
        "date": "2026-03-25",
        "type": "CT thorax",
        "finding": "4.2cm mass in right upper lobe, mediastinal lymphadenopathy",
    },
    "medications": ["metformin 500mg BID", "lisinopril 10mg QD"],
}

MOCK_GUIDELINES = {
    "ESMO_NSCLC_2024": {
        "condition": "NSCLC Stage IIIA",
        "recommendation": "Consider concurrent chemoradiotherapy or surgery + adjuvant chemotherapy",
        "evidence_level": "1A",
        "decision_point": "Resectability assessment — MDT discussion required",
    },
}


def retrieve_patient_history(**kwargs) -> dict:
    """Mock: Retrieve patient history from EHR."""
    return {
        "patient": MOCK_PATIENT,
        "source": "EHR/Epic",
        "retrieved_at": "2026-04-01T10:00:00Z",
    }


def retrieve_lab_results(**kwargs) -> dict:
    """Mock: Retrieve recent lab results."""
    return {
        "labs": MOCK_PATIENT["recent_labs"],
        "source": "LIS",
        "retrieved_at": "2026-04-01T10:00:01Z",
    }


def retrieve_imaging(**kwargs) -> dict:
    """Mock: Retrieve imaging reports."""
    return {
        "imaging": MOCK_PATIENT["imaging"],
        "source": "PACS",
        "retrieved_at": "2026-04-01T10:00:02Z",
    }


def match_clinical_guideline(**kwargs) -> dict:
    """Mock: Match patient condition to clinical guideline."""
    condition = kwargs.get("condition", "")
    if "lung" in condition.lower() and "stage iii" in condition.lower():
        return MOCK_GUIDELINES["ESMO_NSCLC_2024"]
    return {"recommendation": "No specific guideline match", "evidence_level": "N/A"}


def generate_case_summary(**kwargs) -> dict:
    """Mock: Generate structured case summary for MDT."""
    return {
        "summary": (
            f"Patient {kwargs.get('patient_id', 'unknown')}, {MOCK_PATIENT['age']}yo. "
            f"Dx: {MOCK_PATIENT['condition']}. "
            f"CT ({MOCK_PATIENT['imaging']['date']}): {MOCK_PATIENT['imaging']['finding']}. "
            f"Labs WNL. On metformin + lisinopril. "
            f"Guideline: {MOCK_GUIDELINES['ESMO_NSCLC_2024']['recommendation']}. "
            f"Decision: {MOCK_GUIDELINES['ESMO_NSCLC_2024']['decision_point']}."
        ),
        "citations": ["EHR/P-2024-0731", "PACS/CT-2026-03-25", "ESMO NSCLC Guidelines 2024"],
        "generated_at": "2026-04-01T10:00:05Z",
    }


def suggest_treatment(**kwargs) -> dict:
    """Mock: Suggest treatment options (CRITICAL — always needs review)."""
    return {
        "options": [
            {"treatment": "Concurrent chemoradiotherapy", "evidence": "1A", "notes": "Standard for unresectable IIIA"},
            {"treatment": "Surgery + adjuvant chemo", "evidence": "1A", "notes": "If MDT deems resectable"},
        ],
        "warning": "CRITICAL: Treatment suggestion requires MDT review and oncologist approval",
    }


# ── Demo Runner ──────────────────────────────────────────────────────

def run_demo():
    """Run the MDT preparation demo."""
    print("=" * 70)
    print("  AGENT SAFETY HARNESS — MDT Meeting Preparation Demo")
    print("=" * 70)
    print()

    # Create agent with clinical thresholds
    agent = TransactionalAgent(
        thresholds=ConfidenceThresholds(),
    )

    # Register mock tools
    agent.register_tool("retrieve_patient_history", retrieve_patient_history)
    agent.register_tool("retrieve_lab_results", retrieve_lab_results)
    agent.register_tool("retrieve_imaging", retrieve_imaging)
    agent.register_tool("match_clinical_guideline", match_clinical_guideline)
    agent.register_tool("generate_case_summary", generate_case_summary)
    agent.register_tool("suggest_treatment", suggest_treatment)

    # ── Step 1: Retrieve patient data (MEDIUM severity, high confidence) ──
    print("[Step 1] Retrieving patient history...")
    r1 = agent.stage_action(StagedAction(
        description="Retrieve patient history for MDT case preparation",
        tool_name="retrieve_patient_history",
        tool_args={"patient_id": "P-2024-0731"},
        confidence=0.98,
        severity=ActionSeverity.MEDIUM,
    ))
    print(f"  -> {r1.status} (confidence: {r1.action.confidence})")

    # ── Step 2: Retrieve labs (MEDIUM severity, high confidence) ──
    print("[Step 2] Retrieving lab results...")
    r2 = agent.stage_action(StagedAction(
        description="Retrieve recent lab results",
        tool_name="retrieve_lab_results",
        tool_args={"patient_id": "P-2024-0731"},
        confidence=0.97,
        severity=ActionSeverity.MEDIUM,
    ))
    print(f"  -> {r2.status} (confidence: {r2.action.confidence})")

    # ── Step 3: Retrieve imaging (MEDIUM severity, high confidence) ──
    print("[Step 3] Retrieving imaging reports...")
    r3 = agent.stage_action(StagedAction(
        description="Retrieve CT thorax imaging report",
        tool_name="retrieve_imaging",
        tool_args={"patient_id": "P-2024-0731"},
        confidence=0.96,
        severity=ActionSeverity.MEDIUM,
    ))
    print(f"  -> {r3.status} (confidence: {r3.action.confidence})")

    # ── Step 4: Match guideline (HIGH severity, medium confidence) ──
    print("[Step 4] Matching clinical guideline...")
    r4 = agent.stage_action(StagedAction(
        description="Match patient condition to ESMO guidelines",
        tool_name="match_clinical_guideline",
        tool_args={"condition": "Non-small cell lung cancer, Stage IIIA"},
        confidence=0.82,
        severity=ActionSeverity.HIGH,
    ))
    print(f"  -> {r4.status} (confidence: {r4.action.confidence})")
    if r4.status == "pending_review":
        print(f"     Reason: {r4.reason}")

    # ── Step 5: Generate case summary (HIGH severity, medium confidence) ──
    print("[Step 5] Generating MDT case summary...")
    r5 = agent.stage_action(StagedAction(
        description="Generate structured case summary for MDT presentation",
        tool_name="generate_case_summary",
        tool_args={"patient_id": "P-2024-0731"},
        confidence=0.78,
        severity=ActionSeverity.HIGH,
    ))
    print(f"  -> {r5.status} (confidence: {r5.action.confidence})")
    if r5.status == "pending_review":
        print(f"     Reason: {r5.reason}")

    # ── Step 6: Suggest treatment (CRITICAL — always needs review) ──
    print("[Step 6] Suggesting treatment options...")
    r6 = agent.stage_action(StagedAction(
        description="Suggest treatment options based on guidelines",
        tool_name="suggest_treatment",
        tool_args={"condition": "NSCLC Stage IIIA", "patient_id": "P-2024-0731"},
        confidence=0.88,
        severity=ActionSeverity.CRITICAL,
    ))
    print(f"  -> {r6.status} (confidence: {r6.action.confidence})")
    if r6.status == "pending_review":
        print(f"     Reason: {r6.reason}")

    # ── Summary ──
    print()
    print("-" * 70)
    summary = agent.get_summary()
    print(f"Total actions staged: {summary['total_staged']}")
    print(f"Auto-committed: {summary['committed']}")
    print(f"Pending human review: {summary['pending_review']}")
    print(f"Rejected: {summary['rejected']}")
    print()

    print("Actions by status:")
    for a in summary["actions"]:
        icon = {"committed": "V", "pending_review": "?", "rejected": "X"}.get(a["status"].value if hasattr(a["status"], "value") else a["status"], "-")
        sev = a["severity"].value if hasattr(a["severity"], "value") else a["severity"]
        status = a["status"].value if hasattr(a["status"], "value") else a["status"]
        print(f"  [{icon}] {a['tool']:<30} conf={a['confidence']:.2f}  sev={sev:<10} -> {status}")

    print()
    print("Key insight: Patient data retrieval (MEDIUM severity) was auto-committed,")
    print("but guideline matching and case summary (HIGH severity) need human review,")
    print("and treatment suggestions (CRITICAL) ALWAYS need human review regardless")
    print("of confidence — because the consequences of an error are too high.")

    # ── Simulate human review ──
    print()
    print("-" * 70)
    print("Simulating human review of pending actions...")
    for action in list(agent.pending_review):
        print(f"  Approving: {action.tool_name} (id: {action.action_id})")
        result = agent.approve_review(action.action_id)
        print(f"    -> {result.status}")

    final = agent.get_summary()
    print()
    print(f"After review: {final['committed']} committed, {final['pending_review']} pending, {final['rejected']} rejected")


if __name__ == "__main__":
    run_demo()
