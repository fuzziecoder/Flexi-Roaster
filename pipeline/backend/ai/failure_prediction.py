"""Failure prediction engine for pipeline execution risk scoring."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    from sklearn.ensemble import GradientBoostingClassifier
except Exception:  # pragma: no cover
    GradientBoostingClassifier = None


@dataclass
class PredictionResult:
    failure_probability: float
    success_probability: float
    stage_risk_scores: Dict[str, float]
    model_type: str
    top_risk_factors: List[str]


class FailurePredictionEngine:
    """Supervised predictor for pipeline and stage-level failure probability."""

    def __init__(self):
        self._model: Optional[Any] = None
        self._feature_order = [
            "historical_failure_rate",
            "recent_error_count",
            "stage_count",
            "critical_stage_count",
            "avg_cpu_percent",
            "avg_memory_percent",
            "retry_frequency",
        ]

    def extract_features(self, sample: Dict[str, Any]) -> List[float]:
        return [
            float(sample.get("historical_failure_rate", 0.0) or 0.0),
            float(sample.get("recent_error_count", 0.0) or 0.0),
            float(sample.get("stage_count", 0.0) or 0.0),
            float(sample.get("critical_stage_count", 0.0) or 0.0),
            float(sample.get("avg_cpu_percent", 0.0) or 0.0),
            float(sample.get("avg_memory_percent", 0.0) or 0.0),
            float(sample.get("retry_frequency", 0.0) or 0.0),
        ]

    def train(self, historical_samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        x_values = [self.extract_features(sample) for sample in historical_samples]
        y_values = [int(sample.get("failed", False)) for sample in historical_samples]

        if x_values and GradientBoostingClassifier is not None:
            self._model = GradientBoostingClassifier(random_state=42)
            self._model.fit(x_values, y_values)
            model_type = "gradient_boosting"
        else:
            model_type = "heuristic"

        return {
            "trained_samples": len(historical_samples),
            "model_type": model_type,
            "features": self._feature_order,
        }

    def predict(self, sample: Dict[str, Any]) -> PredictionResult:
        features = self.extract_features(sample)

        if self._model is not None:
            probability = float(self._model.predict_proba([features])[0][1])
            model_type = "gradient_boosting"
        else:
            probability = self._heuristic_probability(sample)
            model_type = "heuristic"

        stage_risks = self._stage_risks(sample, probability)
        risk_factors = self._top_risk_factors(sample)
        probability = max(0.0, min(probability, 1.0))

        return PredictionResult(
            failure_probability=round(probability, 3),
            success_probability=round(1 - probability, 3),
            stage_risk_scores=stage_risks,
            model_type=model_type,
            top_risk_factors=risk_factors,
        )

    def _heuristic_probability(self, sample: Dict[str, Any]) -> float:
        return min(
            1.0,
            (
                float(sample.get("historical_failure_rate", 0.0)) * 0.35
                + float(sample.get("recent_error_count", 0.0)) * 0.05
                + float(sample.get("retry_frequency", 0.0)) * 0.25
                + float(sample.get("avg_cpu_percent", 0.0)) / 100.0 * 0.15
                + float(sample.get("avg_memory_percent", 0.0)) / 100.0 * 0.10
                + float(sample.get("critical_stage_count", 0.0)) / max(float(sample.get("stage_count", 1.0)), 1.0) * 0.10
            ),
        )

    def _stage_risks(self, sample: Dict[str, Any], pipeline_probability: float) -> Dict[str, float]:
        stages = sample.get("stages", [])
        if not stages:
            return {}

        risks: Dict[str, float] = {}
        for stage in stages:
            name = stage.get("name") or stage.get("id") or "unknown"
            retry_weight = min(float(stage.get("retry_count", 0.0)) / 3.0, 1.0)
            failure_weight = min(float(stage.get("historical_failure_rate", 0.0)), 1.0)
            critical_bonus = 0.15 if stage.get("is_critical", True) else -0.1
            score = max(0.0, min(1.0, pipeline_probability * 0.5 + retry_weight * 0.25 + failure_weight * 0.25 + critical_bonus))
            risks[name] = round(score, 3)
        return risks

    def _top_risk_factors(self, sample: Dict[str, Any]) -> List[str]:
        factors: List[str] = []
        if float(sample.get("historical_failure_rate", 0.0)) > 0.3:
            factors.append("High historical failure rate")
        if float(sample.get("recent_error_count", 0.0)) >= 5:
            factors.append("Recent error spike")
        if float(sample.get("avg_cpu_percent", 0.0)) > 85:
            factors.append("CPU saturation")
        if float(sample.get("avg_memory_percent", 0.0)) > 85:
            factors.append("Memory pressure")
        if float(sample.get("retry_frequency", 0.0)) > 1.5:
            factors.append("High retry frequency")
        return factors[:3] or ["No major risk factors detected"]


failure_prediction_engine = FailurePredictionEngine()
