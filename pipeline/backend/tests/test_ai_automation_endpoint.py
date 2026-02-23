import importlib.util
from pathlib import Path

import asyncio


MODULE_PATH = Path(__file__).resolve().parents[1] / "api" / "routes" / "ai_automation.py"
SPEC = importlib.util.spec_from_file_location("ai_automation_route_module", MODULE_PATH)
ai_automation = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(ai_automation)
automate_pipeline_remediation = ai_automation.automate_pipeline_remediation


def test_auto_remediation_returns_auto_executable_for_low_risk_payload():
    payload = {
        "telemetry": {
            "duration_seconds": 35,
            "data_volume_mb": 180,
            "failure_count_1h": 0,
            "cpu_percent": 42,
            "memory_percent": 44,
            "retry_count": 0,
            "stage_errors": [],
        },
        "risk_features": {
            "historical_failure_rate": 0.02,
            "recent_error_count": 0,
            "stage_count": 4,
            "critical_stage_count": 1,
            "avg_cpu_percent": 42,
            "avg_memory_percent": 44,
            "retry_frequency": 0.2,
            "parallelizable": True,
            "stages": [{"name": "extract", "retry_count": 0, "historical_failure_rate": 0.01}],
        },
        "diagnostics": {
            "stages": [{"name": "extract", "status": "failed"}],
            "logs": ["schema mismatch in transform"],
            "metrics": {"cpu_percent": 35, "memory_percent": 38, "latency_spike": False},
            "history": {"same_stage_failures_last_7d": 0, "recent_deployment": False},
        },
        "human_approval_mode": False,
    }

    result = asyncio.run(automate_pipeline_remediation(payload))

    assert result["automation_status"] == "auto_executable"
    assert "self_healing_plan" in result
    assert "recommendations" in result
    assert 0 <= result["prediction"]["failure_probability"] <= 1


def test_auto_remediation_requires_approval_for_high_risk_payload():
    payload = {
        "telemetry": {
            "duration_seconds": 390,
            "data_volume_mb": 1200,
            "failure_count_1h": 7,
            "cpu_percent": 95,
            "memory_percent": 96,
            "retry_count": 3,
            "stage_errors": ["timeout", "connection refused", "socket"],
        },
        "risk_features": {
            "historical_failure_rate": 0.75,
            "recent_error_count": 10,
            "stage_count": 8,
            "critical_stage_count": 7,
            "avg_cpu_percent": 94,
            "avg_memory_percent": 93,
            "retry_frequency": 2.1,
            "parallelizable": False,
            "stages": [{"name": "transform", "retry_count": 3, "historical_failure_rate": 0.7, "is_critical": True}],
        },
        "diagnostics": {
            "stages": [{"name": "transform", "status": "failed"}],
            "logs": ["connection refused from upstream", "socket timeout"],
            "metrics": {"cpu_percent": 95, "memory_percent": 96, "latency_spike": True},
            "history": {"same_stage_failures_last_7d": 5, "recent_deployment": True},
        },
        "human_approval_mode": False,
    }

    result = asyncio.run(automate_pipeline_remediation(payload))

    assert result["automation_status"] == "approval_required"
    assert result["self_healing_plan"]["requires_human_approval"] is True
    assert result["prediction"]["failure_probability"] >= 0.7
