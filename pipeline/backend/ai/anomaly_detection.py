"""Anomaly detection engine for pipeline self-healing."""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Any, Dict, List, Optional

try:
    from sklearn.ensemble import IsolationForest
except Exception:  # pragma: no cover - fallback when sklearn unavailable
    IsolationForest = None


@dataclass
class FeatureVector:
    execution_time_s: float
    data_volume_mb: float
    failure_count_1h: float
    cpu_percent: float
    memory_percent: float
    retry_count: float
    error_pattern_score: float


@dataclass
class AnomalyDecision:
    is_anomaly: bool
    score: float
    reasons: List[str]
    algorithm: str


class AnomalyDetectionEngine:
    """Hybrid anomaly detector using Isolation Forest + statistical rules."""

    def __init__(self):
        self._model: Optional[Any] = None
        self._baseline: Dict[str, Dict[str, float]] = {}

    def extract_features(self, event: Dict[str, Any]) -> FeatureVector:
        """Extracts model features from monitoring event payload."""
        errors = event.get("stage_errors") or []
        error_pattern_score = min(len(set(errors)) / 5.0, 1.0)
        return FeatureVector(
            execution_time_s=float(event.get("duration_seconds", 0.0) or 0.0),
            data_volume_mb=float(event.get("data_volume_mb", 0.0) or 0.0),
            failure_count_1h=float(event.get("failure_count_1h", 0.0) or 0.0),
            cpu_percent=float(event.get("cpu_percent", 0.0) or 0.0),
            memory_percent=float(event.get("memory_percent", 0.0) or 0.0),
            retry_count=float(event.get("retry_count", 0.0) or 0.0),
            error_pattern_score=error_pattern_score,
        )

    def train(self, historical_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train unsupervised baseline and optional Isolation Forest model."""
        features = [self.extract_features(event) for event in historical_events]
        matrix = [
            [
                feature.execution_time_s,
                feature.data_volume_mb,
                feature.failure_count_1h,
                feature.cpu_percent,
                feature.memory_percent,
                feature.retry_count,
                feature.error_pattern_score,
            ]
            for feature in features
        ]

        if matrix and IsolationForest is not None:
            self._model = IsolationForest(contamination=0.05, random_state=42)
            self._model.fit(matrix)

        self._baseline = self._build_baseline(features)
        return {
            "trained_samples": len(features),
            "algorithm": "isolation_forest+zscore" if self._model is not None else "zscore_only",
        }

    def detect(self, event: Dict[str, Any]) -> AnomalyDecision:
        feature = self.extract_features(event)
        reasons = self._statistical_anomaly_reasons(feature)

        score = min(len(reasons) / 4.0, 1.0)
        algorithm = "zscore_rules"

        if self._model is not None:
            values = [[
                feature.execution_time_s,
                feature.data_volume_mb,
                feature.failure_count_1h,
                feature.cpu_percent,
                feature.memory_percent,
                feature.retry_count,
                feature.error_pattern_score,
            ]]
            prediction = int(self._model.predict(values)[0])
            if prediction == -1:
                reasons.insert(0, "IsolationForest flagged point as outlier")
                score = min(score + 0.4, 1.0)
            algorithm = "isolation_forest+zscore"

        return AnomalyDecision(
            is_anomaly=(score >= 0.5),
            score=round(score, 3),
            reasons=reasons or ["No significant anomalies detected"],
            algorithm=algorithm,
        )

    def _build_baseline(self, features: List[FeatureVector]) -> Dict[str, Dict[str, float]]:
        if not features:
            return {}

        columns = {
            "execution_time_s": [f.execution_time_s for f in features],
            "data_volume_mb": [f.data_volume_mb for f in features],
            "failure_count_1h": [f.failure_count_1h for f in features],
            "cpu_percent": [f.cpu_percent for f in features],
            "memory_percent": [f.memory_percent for f in features],
        }
        baseline: Dict[str, Dict[str, float]] = {}
        for key, values in columns.items():
            baseline[key] = {"mean": mean(values), "std": pstdev(values) if len(values) > 1 else 1.0}
        return baseline

    def _statistical_anomaly_reasons(self, feature: FeatureVector) -> List[str]:
        reasons: List[str] = []
        if not self._baseline:
            if feature.execution_time_s > 0:
                return ["No baseline available; anomaly model not trained yet"]
            return []

        for name, value in {
            "execution_time_s": feature.execution_time_s,
            "data_volume_mb": feature.data_volume_mb,
            "failure_count_1h": feature.failure_count_1h,
            "cpu_percent": feature.cpu_percent,
            "memory_percent": feature.memory_percent,
        }.items():
            baseline = self._baseline[name]
            std = baseline["std"] if baseline["std"] > 0 else 1.0
            z_score = abs((value - baseline["mean"]) / std)
            if z_score >= 3:
                reasons.append(f"{name} z-score {z_score:.2f} (>3)")

        if feature.retry_count >= 3:
            reasons.append("Retry burst detected")
        if feature.error_pattern_score >= 0.6:
            reasons.append("Log pattern anomaly detected")

        return reasons


anomaly_detection_engine = AnomalyDetectionEngine()
