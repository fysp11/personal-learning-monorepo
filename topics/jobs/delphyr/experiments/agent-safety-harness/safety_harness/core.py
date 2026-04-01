"""Core transactional agent framework.

Implements the commit/rollback pattern for agent actions:
- Actions are STAGED before execution (like a database transaction)
- Confidence scoring routes actions: auto-commit / human review / reject
- Full audit trail for every decision
- Cascading rollback capability
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from pydantic import BaseModel, Field


class ActionStatus(str, Enum):
    STAGED = "staged"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    PENDING_REVIEW = "pending_review"
    REJECTED = "rejected"


class ActionSeverity(str, Enum):
    """How critical is this action? Determines routing thresholds."""
    LOW = "low"          # Formatting, display — errors are harmless
    MEDIUM = "medium"    # Data retrieval — errors waste time but don't harm
    HIGH = "high"        # Clinical recommendations — errors could harm patients
    CRITICAL = "critical"  # Treatment suggestions — errors are dangerous


class AuditEntry(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event: str
    details: dict[str, Any] = Field(default_factory=dict)


class StagedAction(BaseModel):
    """An agent action that has been proposed but not yet executed."""
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str
    tool_name: str
    tool_args: dict[str, Any]
    confidence: float = Field(ge=0.0, le=1.0)
    severity: ActionSeverity = ActionSeverity.MEDIUM
    status: ActionStatus = ActionStatus.STAGED
    result: Any | None = None
    error: str | None = None
    audit_trail: list[AuditEntry] = Field(default_factory=list)

    def log(self, event: str, **details: Any) -> None:
        self.audit_trail.append(AuditEntry(event=event, details=details))


class ConfidenceThresholds(BaseModel):
    """Confidence thresholds per severity level.

    Higher severity = stricter thresholds.
    """
    auto_commit: dict[ActionSeverity, float] = Field(default_factory=lambda: {
        ActionSeverity.LOW: 0.80,
        ActionSeverity.MEDIUM: 0.90,
        ActionSeverity.HIGH: 0.95,
        ActionSeverity.CRITICAL: 1.01,  # Never auto-commit critical actions
    })
    review_minimum: dict[ActionSeverity, float] = Field(default_factory=lambda: {
        ActionSeverity.LOW: 0.40,
        ActionSeverity.MEDIUM: 0.60,
        ActionSeverity.HIGH: 0.75,
        ActionSeverity.CRITICAL: 0.80,
    })


class TransactionResult(BaseModel):
    status: str
    action: StagedAction
    reason: str | None = None


class TransactionalAgent:
    """Agent with transactional action execution.

    All actions are staged before execution. Routing is based on
    confidence scores and action severity:

    - Above auto_commit threshold: execute immediately
    - Between review_minimum and auto_commit: queue for human review
    - Below review_minimum: reject automatically
    """

    def __init__(
        self,
        thresholds: ConfidenceThresholds | None = None,
        tool_registry: dict[str, Callable] | None = None,
    ):
        self.thresholds = thresholds or ConfidenceThresholds()
        self.tool_registry = tool_registry or {}
        self.staged_actions: list[StagedAction] = []
        self.committed_actions: list[StagedAction] = []
        self.rejected_actions: list[StagedAction] = []
        self.pending_review: list[StagedAction] = []
        self.global_audit: list[AuditEntry] = []

    def _log(self, event: str, **details: Any) -> None:
        self.global_audit.append(AuditEntry(event=event, details=details))

    def register_tool(self, name: str, func: Callable) -> None:
        """Register a tool that actions can call."""
        self.tool_registry[name] = func

    def stage_action(self, action: StagedAction) -> TransactionResult:
        """Stage an action and route based on confidence + severity."""
        self.staged_actions.append(action)
        action.log("staged", confidence=action.confidence, severity=action.severity)
        self._log("action_staged", action_id=action.action_id, tool=action.tool_name)

        return self._route_action(action)

    def _route_action(self, action: StagedAction) -> TransactionResult:
        """Route an action based on confidence and severity thresholds."""
        auto_threshold = self.thresholds.auto_commit[action.severity]
        review_threshold = self.thresholds.review_minimum[action.severity]

        if action.confidence >= auto_threshold:
            return self.commit(action)
        elif action.confidence >= review_threshold:
            return self.queue_for_review(action)
        else:
            return self.reject(action, reason="confidence_below_minimum")

    def commit(self, action: StagedAction) -> TransactionResult:
        """Execute the staged action."""
        tool_func = self.tool_registry.get(action.tool_name)
        if not tool_func:
            action.status = ActionStatus.REJECTED
            action.error = f"Tool not found: {action.tool_name}"
            action.log("commit_failed", error=action.error)
            self.rejected_actions.append(action)
            return TransactionResult(status="error", action=action, reason=action.error)

        try:
            result = tool_func(**action.tool_args)
            action.status = ActionStatus.COMMITTED
            action.result = result
            action.log("committed", result_preview=str(result)[:200])
            self.committed_actions.append(action)
            self._log("action_committed", action_id=action.action_id)
            return TransactionResult(status="committed", action=action)
        except Exception as e:
            action.status = ActionStatus.ROLLED_BACK
            action.error = str(e)
            action.log("commit_failed_rollback", error=str(e))
            self.rejected_actions.append(action)
            return TransactionResult(status="error", action=action, reason=str(e))

    def queue_for_review(self, action: StagedAction) -> TransactionResult:
        """Queue action for human review."""
        action.status = ActionStatus.PENDING_REVIEW
        action.log("queued_for_review", confidence=action.confidence)
        self.pending_review.append(action)
        self._log("action_pending_review", action_id=action.action_id)
        return TransactionResult(
            status="pending_review",
            action=action,
            reason=f"Confidence {action.confidence:.2f} below auto-commit threshold for {action.severity} severity",
        )

    def reject(self, action: StagedAction, reason: str) -> TransactionResult:
        """Reject an action — confidence too low."""
        action.status = ActionStatus.REJECTED
        action.log("rejected", reason=reason)
        self.rejected_actions.append(action)
        self._log("action_rejected", action_id=action.action_id, reason=reason)
        return TransactionResult(status="rejected", action=action, reason=reason)

    def approve_review(self, action_id: str) -> TransactionResult:
        """Human approves a pending review action."""
        action = self._find_pending(action_id)
        if not action:
            raise ValueError(f"No pending action with id {action_id}")
        self.pending_review.remove(action)
        action.log("human_approved")
        return self.commit(action)

    def deny_review(self, action_id: str, reason: str = "human_denied") -> TransactionResult:
        """Human denies a pending review action."""
        action = self._find_pending(action_id)
        if not action:
            raise ValueError(f"No pending action with id {action_id}")
        self.pending_review.remove(action)
        return self.reject(action, reason=reason)

    def rollback_all(self) -> list[TransactionResult]:
        """Rollback all committed actions in reverse order.

        This is the cascading rollback — if we discover a downstream
        action was wrong, we can undo everything.
        """
        results = []
        for action in reversed(self.committed_actions):
            action.status = ActionStatus.ROLLED_BACK
            action.log("rolled_back_cascade")
            results.append(TransactionResult(
                status="rolled_back",
                action=action,
                reason="cascading_rollback",
            ))
        self._log("cascade_rollback", count=len(self.committed_actions))
        self.committed_actions.clear()
        return results

    def _find_pending(self, action_id: str) -> StagedAction | None:
        return next((a for a in self.pending_review if a.action_id == action_id), None)

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of all actions and their statuses."""
        return {
            "total_staged": len(self.staged_actions),
            "committed": len(self.committed_actions),
            "pending_review": len(self.pending_review),
            "rejected": len(self.rejected_actions),
            "actions": [
                {
                    "id": a.action_id,
                    "tool": a.tool_name,
                    "status": a.status,
                    "confidence": a.confidence,
                    "severity": a.severity,
                }
                for a in self.staged_actions
            ],
        }
