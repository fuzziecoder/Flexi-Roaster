"""Self-healing decision engine with safeguards and rollback strategy."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class SelfHealingPlan:
    actions: List[Dict[str, Any]]
    risk_level: str
    requires_human_approval: bool
    rollback_plan: List[str]
    reason: str


class SelfHealingEngine:
    def __init__(self):
        self.thresholds = {"low": 0.3, "medium": 0.6, "high": 0.8}

    def decide(self, payload: Dict[str, Any]) -> SelfHealingPlan:
        risk = float(payload.get("risk_score", 0.0) or 0.0)
        cause = str(payload.get("primary_cause", "unknown"))
        stage = str(payload.get("failing_stage", "unknown"))
        retry_count = int(payload.get("retry_count", 0) or 0)
        approval_mode = bool(payload.get("human_approval_mode", False))

        actions: List[Dict[str, Any]] = []
        rollback = [
            "Revert timeout/scaling config to previous snapshot",
            "Restore worker pool size baseline",
            "Resume prior service routing",
        ]

        if retry_count < 3:
            actions.append({"type": "retry_failed_stage", "stage": stage, "max_attempts": 3})

        if cause == "connection_issue":
            actions.append({"type": "restart_worker", "target": "pipeline-worker"})
            actions.append({"type": "switch_fallback_service", "target": "secondary-endpoint"})
        elif cause == "resource_bottleneck":
            actions.append({"type": "scale_resources", "cpu": "+2", "memory": "+4Gi"})
            actions.append({"type": "increase_timeout", "stage": stage, "multiplier": 1.5})
        elif cause == "data_inconsistency":
            actions.append({"type": "increase_timeout", "stage": stage, "multiplier": 1.2})
        elif cause == "configuration_error":
            actions.append({"type": "switch_fallback_service", "target": "known-good-config-profile"})

        if payload.get("parallelizable", False) and risk <= self.thresholds["medium"]:
            actions.append({"type": "parallelize_pipeline_stages", "mode": "safe_non_critical_only"})

        risk_level = self._risk_level(risk)
        requires_approval = approval_mode or risk_level == "high"

        return SelfHealingPlan(
            actions=actions,
            risk_level=risk_level,
            requires_human_approval=requires_approval,
            rollback_plan=rollback,
            reason=f"Selected actions for cause={cause}, risk={risk:.2f}, retries={retry_count}",
        )

    def _risk_level(self, risk: float) -> str:
        if risk >= self.thresholds["high"]:
            return "high"
        if risk >= self.thresholds["medium"]:
            return "medium"
        return "low"


self_healing_engine = SelfHealingEngine()
