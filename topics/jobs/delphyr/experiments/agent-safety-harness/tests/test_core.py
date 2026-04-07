"""Tests for the transactional agent safety harness."""

import pytest
from safety_harness.core import (
    TransactionalAgent,
    StagedAction,
    ActionSeverity,
    ActionStatus,
    ConfidenceThresholds,
)


def dummy_tool(**kwargs):
    return {"status": "ok", "args": kwargs}


def failing_tool(**kwargs):
    raise RuntimeError("Tool execution failed")


@pytest.fixture
def agent():
    a = TransactionalAgent()
    a.register_tool("dummy", dummy_tool)
    a.register_tool("failing", failing_tool)
    return a


class TestAutoCommit:
    """Test that high-confidence actions are auto-committed."""

    def test_low_severity_auto_commits(self, agent):
        result = agent.stage_action(StagedAction(
            description="Format report",
            tool_name="dummy",
            tool_args={"key": "value"},
            confidence=0.85,
            severity=ActionSeverity.LOW,
        ))
        assert result.status == "committed"
        assert result.action.status == ActionStatus.COMMITTED

    def test_medium_severity_auto_commits_high_confidence(self, agent):
        result = agent.stage_action(StagedAction(
            description="Retrieve data",
            tool_name="dummy",
            tool_args={},
            confidence=0.95,
            severity=ActionSeverity.MEDIUM,
        ))
        assert result.status == "committed"

    def test_high_severity_auto_commits_very_high_confidence(self, agent):
        result = agent.stage_action(StagedAction(
            description="Match guideline",
            tool_name="dummy",
            tool_args={},
            confidence=0.96,
            severity=ActionSeverity.HIGH,
        ))
        assert result.status == "committed"


class TestPendingReview:
    """Test that medium-confidence actions are queued for review."""

    def test_medium_severity_queued(self, agent):
        result = agent.stage_action(StagedAction(
            description="Classify document",
            tool_name="dummy",
            tool_args={},
            confidence=0.75,
            severity=ActionSeverity.MEDIUM,
        ))
        assert result.status == "pending_review"
        assert len(agent.pending_review) == 1

    def test_high_severity_queued(self, agent):
        result = agent.stage_action(StagedAction(
            description="Match clinical guideline",
            tool_name="dummy",
            tool_args={},
            confidence=0.85,
            severity=ActionSeverity.HIGH,
        ))
        assert result.status == "pending_review"

    def test_critical_always_queued(self, agent):
        """CRITICAL actions should always go to review, even at 0.99 confidence."""
        result = agent.stage_action(StagedAction(
            description="Suggest treatment",
            tool_name="dummy",
            tool_args={},
            confidence=0.99,
            severity=ActionSeverity.CRITICAL,
        ))
        assert result.status == "pending_review"


class TestRejection:
    """Test that low-confidence actions are rejected."""

    def test_low_confidence_rejected(self, agent):
        result = agent.stage_action(StagedAction(
            description="Uncertain classification",
            tool_name="dummy",
            tool_args={},
            confidence=0.30,
            severity=ActionSeverity.MEDIUM,
        ))
        assert result.status == "rejected"

    def test_high_severity_low_confidence_rejected(self, agent):
        result = agent.stage_action(StagedAction(
            description="Uncertain guideline match",
            tool_name="dummy",
            tool_args={},
            confidence=0.60,
            severity=ActionSeverity.HIGH,
        ))
        assert result.status == "rejected"


class TestHumanReview:
    """Test the human review approval/denial flow."""

    def test_approve_executes_action(self, agent):
        # Stage a medium-confidence action
        result = agent.stage_action(StagedAction(
            description="Needs review",
            tool_name="dummy",
            tool_args={"patient_id": "P-001"},
            confidence=0.75,
            severity=ActionSeverity.MEDIUM,
        ))
        assert result.status == "pending_review"

        # Human approves
        approved = agent.approve_review(result.action.action_id)
        assert approved.status == "committed"
        assert approved.action.result is not None

    def test_deny_rejects_action(self, agent):
        result = agent.stage_action(StagedAction(
            description="Needs review",
            tool_name="dummy",
            tool_args={},
            confidence=0.75,
            severity=ActionSeverity.MEDIUM,
        ))
        denied = agent.deny_review(result.action.action_id, reason="Doctor disagrees")
        assert denied.status == "rejected"
        assert denied.reason == "Doctor disagrees"

    def test_approve_nonexistent_raises(self, agent):
        with pytest.raises(ValueError, match="No pending action"):
            agent.approve_review("nonexistent-id")


class TestRollback:
    """Test cascading rollback of committed actions."""

    def test_rollback_all(self, agent):
        # Commit multiple actions
        for i in range(3):
            agent.stage_action(StagedAction(
                description=f"Action {i}",
                tool_name="dummy",
                tool_args={},
                confidence=0.95,
                severity=ActionSeverity.MEDIUM,
            ))
        assert len(agent.committed_actions) == 3

        results = agent.rollback_all()
        assert len(results) == 3
        assert all(r.status == "rolled_back" for r in results)
        assert len(agent.committed_actions) == 0

    def test_rollback_preserves_audit_trail(self, agent):
        result = agent.stage_action(StagedAction(
            description="Will be rolled back",
            tool_name="dummy",
            tool_args={},
            confidence=0.95,
            severity=ActionSeverity.MEDIUM,
        ))
        agent.rollback_all()
        # Audit trail should have: staged, committed, rolled_back
        events = [e.event for e in result.action.audit_trail]
        assert "staged" in events
        assert "committed" in events
        assert "rolled_back_cascade" in events


class TestToolFailure:
    """Test handling of tool execution failures."""

    def test_failing_tool_rolls_back(self, agent):
        result = agent.stage_action(StagedAction(
            description="Will fail",
            tool_name="failing",
            tool_args={},
            confidence=0.95,
            severity=ActionSeverity.MEDIUM,
        ))
        assert result.status == "error"
        assert result.action.status == ActionStatus.ROLLED_BACK

    def test_unknown_tool_rejected(self, agent):
        result = agent.stage_action(StagedAction(
            description="No such tool",
            tool_name="nonexistent_tool",
            tool_args={},
            confidence=0.95,
            severity=ActionSeverity.LOW,
        ))
        assert result.status == "error"
        assert "not found" in result.reason


class TestAuditTrail:
    """Test that audit trail captures all events."""

    def test_committed_action_has_full_trail(self, agent):
        result = agent.stage_action(StagedAction(
            description="Tracked action",
            tool_name="dummy",
            tool_args={},
            confidence=0.95,
            severity=ActionSeverity.MEDIUM,
        ))
        events = [e.event for e in result.action.audit_trail]
        assert "staged" in events
        assert "committed" in events

    def test_global_audit_tracks_all(self, agent):
        agent.stage_action(StagedAction(
            description="Action 1",
            tool_name="dummy",
            tool_args={},
            confidence=0.95,
            severity=ActionSeverity.MEDIUM,
        ))
        agent.stage_action(StagedAction(
            description="Action 2",
            tool_name="dummy",
            tool_args={},
            confidence=0.30,
            severity=ActionSeverity.MEDIUM,
        ))
        assert len(agent.global_audit) >= 2
