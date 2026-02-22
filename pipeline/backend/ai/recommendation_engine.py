"""Recommendation engine for optimization guidance with confidence scoring."""
from __future__ import annotations

from typing import Any, Dict, List


class RecommendationEngine:
    def recommend(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        recommendations: List[Dict[str, Any]] = []

        avg_duration = float(payload.get("avg_duration_seconds", 0) or 0)
        retry_frequency = float(payload.get("retry_frequency", 0) or 0)
        cpu = float(payload.get("avg_cpu_percent", 0) or 0)
        mem = float(payload.get("avg_memory_percent", 0) or 0)
        stage_count = float(payload.get("stage_count", 0) or 0)
        parallelizable = bool(payload.get("parallelizable", False))

        if avg_duration > 180:
            recommendations.append(self._entry("optimize_execution_time", 0.82, 88))
        if parallelizable and stage_count >= 4:
            recommendations.append(self._entry("enable_parallel_stages", 0.76, 81))
        if cpu > 80 or mem > 80:
            recommendations.append(self._entry("scale_workers", 0.84, 90))
            recommendations.append(self._entry("improve_resource_allocation", 0.79, 86))
        if retry_frequency > 1.0:
            recommendations.append(self._entry("update_configuration", 0.74, 80))

        return recommendations or [self._entry("no_action_needed", 0.93, 95)]

    def _entry(self, recommendation: str, confidence: float, impact_score: int) -> Dict[str, Any]:
        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "impact_score": impact_score,
            "priority_score": round(confidence * impact_score, 2),
        }


recommendation_engine = RecommendationEngine()
