from ai.root_cause_engine import RootCauseAnalysisEngine
from ai.self_healing_engine import SelfHealingEngine
from ai.recommendation_engine import RecommendationEngine


def test_root_cause_engine_detects_connection_issue():
    engine = RootCauseAnalysisEngine()
    result = engine.analyze(
        {
            "stages": [{"name": "extract", "status": "failed"}],
            "logs": ["connection refused from upstream service", "socket timeout"],
            "metrics": {"cpu_percent": 60, "memory_percent": 50, "latency_spike": True},
            "history": {"same_stage_failures_last_7d": 4, "recent_deployment": False},
        }
    )
    assert result.failing_stage == "extract"
    assert result.primary_cause == "connection_issue"
    assert result.confidence >= 0.6


def test_self_healing_engine_requires_approval_for_high_risk():
    engine = SelfHealingEngine()
    plan = engine.decide(
        {
            "risk_score": 0.85,
            "primary_cause": "resource_bottleneck",
            "failing_stage": "transform",
            "retry_count": 1,
            "human_approval_mode": False,
            "parallelizable": True,
        }
    )
    assert plan.risk_level == "high"
    assert plan.requires_human_approval is True
    assert any(action["type"] == "scale_resources" for action in plan.actions)


def test_recommendation_engine_scores_actions():
    engine = RecommendationEngine()
    recommendations = engine.recommend(
        {
            "avg_duration_seconds": 300,
            "retry_frequency": 1.4,
            "avg_cpu_percent": 87,
            "avg_memory_percent": 82,
            "stage_count": 6,
            "parallelizable": True,
        }
    )
    assert len(recommendations) >= 3
    assert all("priority_score" in item for item in recommendations)
