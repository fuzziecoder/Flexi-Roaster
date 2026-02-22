"""Root cause analysis engine for pipeline failures."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class RootCauseResult:
    failing_stage: str
    primary_cause: str
    confidence: float
    evidence: List[str]
    contributing_factors: List[str]


class RootCauseAnalysisEngine:
    """Combines logs, metrics, and historical patterns to infer root cause."""

    def analyze(self, payload: Dict[str, Any]) -> RootCauseResult:
        stages = payload.get("stages", [])
        failing_stage = self._find_failing_stage(stages)
        logs = payload.get("logs", [])
        metrics = payload.get("metrics", {})
        history = payload.get("history", {})

        evidence: List[str] = []
        factors: List[str] = []

        cause = "unknown"

        log_text = " ".join(str(item).lower() for item in logs)

        if any(token in log_text for token in ["timeout", "connection refused", "dns", "socket"]):
            cause = "connection_issue"
            evidence.append("Connection-related errors detected in logs")
        elif metrics.get("cpu_percent", 0) > 90 or metrics.get("memory_percent", 0) > 90:
            cause = "resource_bottleneck"
            evidence.append("High resource utilization detected")
        elif any(token in log_text for token in ["schema", "null", "type mismatch", "constraint"]):
            cause = "data_inconsistency"
            evidence.append("Data validation/schema anomalies found in logs")
        elif any(token in log_text for token in ["config", "invalid parameter", "missing env", "permission"]):
            cause = "configuration_error"
            evidence.append("Configuration-related errors found in logs")

        if history.get("same_stage_failures_last_7d", 0) >= 3:
            factors.append("Repeated failure pattern in same stage")
        if history.get("recent_deployment", False):
            factors.append("Recent deployment may have introduced regression")
        if metrics.get("latency_spike", False):
            factors.append("Upstream/downstream latency spike observed")

        confidence = self._confidence(cause, evidence, factors)
        return RootCauseResult(
            failing_stage=failing_stage,
            primary_cause=cause,
            confidence=confidence,
            evidence=evidence or ["Insufficient evidence; defaulted to unknown"],
            contributing_factors=factors,
        )

    def _find_failing_stage(self, stages: List[Dict[str, Any]]) -> str:
        for stage in stages:
            if str(stage.get("status", "")).lower() in {"failed", "error"}:
                return str(stage.get("name") or stage.get("id") or "unknown")
        return "unknown"

    def _confidence(self, cause: str, evidence: List[str], factors: List[str]) -> float:
        base = 0.3 if cause == "unknown" else 0.6
        return round(min(0.98, base + 0.1 * len(evidence) + 0.05 * len(factors)), 3)


root_cause_engine = RootCauseAnalysisEngine()
