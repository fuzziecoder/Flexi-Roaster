from ai.anomaly_detection import AnomalyDetectionEngine
from ai.failure_prediction import FailurePredictionEngine


def test_anomaly_engine_training_and_detection():
    engine = AnomalyDetectionEngine()
    historical = [
        {
            "duration_seconds": 25 + i,
            "data_volume_mb": 200 + i,
            "failure_count_1h": 0,
            "cpu_percent": 45 + i,
            "memory_percent": 40 + i,
            "retry_count": 0,
            "stage_errors": [],
        }
        for i in range(10)
    ]
    result = engine.train(historical)
    assert result["trained_samples"] == 10

    anomaly = engine.detect(
        {
            "duration_seconds": 200,
            "data_volume_mb": 1200,
            "failure_count_1h": 6,
            "cpu_percent": 97,
            "memory_percent": 96,
            "retry_count": 4,
            "stage_errors": ["timeout", "oom", "timeout"],
        }
    )
    assert anomaly.is_anomaly is True
    assert anomaly.score >= 0.5


def test_failure_prediction_engine_predicts_probabilities():
    engine = FailurePredictionEngine()
    samples = [
        {
            "historical_failure_rate": 0.05,
            "recent_error_count": 1,
            "stage_count": 4,
            "critical_stage_count": 2,
            "avg_cpu_percent": 40,
            "avg_memory_percent": 35,
            "retry_frequency": 0.2,
            "failed": False,
        },
        {
            "historical_failure_rate": 0.6,
            "recent_error_count": 8,
            "stage_count": 10,
            "critical_stage_count": 8,
            "avg_cpu_percent": 90,
            "avg_memory_percent": 92,
            "retry_frequency": 2.0,
            "failed": True,
        },
    ]
    train_result = engine.train(samples)
    assert train_result["trained_samples"] == 2

    prediction = engine.predict(
        {
            "historical_failure_rate": 0.55,
            "recent_error_count": 7,
            "stage_count": 8,
            "critical_stage_count": 6,
            "avg_cpu_percent": 88,
            "avg_memory_percent": 87,
            "retry_frequency": 1.8,
            "stages": [
                {"name": "extract", "retry_count": 2, "historical_failure_rate": 0.4, "is_critical": True},
                {"name": "validate", "retry_count": 1, "historical_failure_rate": 0.2, "is_critical": False},
            ],
        }
    )

    assert 0 <= prediction.failure_probability <= 1
    assert 0 <= prediction.success_probability <= 1
    assert set(prediction.stage_risk_scores.keys()) == {"extract", "validate"}
