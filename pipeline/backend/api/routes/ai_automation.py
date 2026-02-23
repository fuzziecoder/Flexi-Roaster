"""AI automation endpoints for anomaly detection and failure prediction."""
from typing import Any, Dict, List

from fastapi import APIRouter

from ai.anomaly_detection import anomaly_detection_engine
from ai.failure_prediction import failure_prediction_engine

from ai.root_cause_engine import root_cause_engine
from ai.self_healing_engine import self_healing_engine
from ai.recommendation_engine import recommendation_engine

router = APIRouter(prefix="/ai", tags=["ai-automation"])


@router.post("/anomaly/train", response_model=Dict[str, Any])
async def train_anomaly_model(historical_events: List[Dict[str, Any]]):
    """Train anomaly detector with historical telemetry features."""
    return anomaly_detection_engine.train(historical_events)


@router.post("/anomaly/detect", response_model=Dict[str, Any])
async def detect_anomaly(event: Dict[str, Any]):
    """Run online anomaly inference for a single execution event."""
    decision = anomaly_detection_engine.detect(event)
    return {
        "is_anomaly": decision.is_anomaly,
        "score": decision.score,
        "reasons": decision.reasons,
        "algorithm": decision.algorithm,
    }


@router.post("/prediction/train", response_model=Dict[str, Any])
async def train_failure_predictor(historical_samples: List[Dict[str, Any]]):
    """Train failure prediction model with historical execution outcomes."""
    return failure_prediction_engine.train(historical_samples)


@router.post("/prediction/predict", response_model=Dict[str, Any])
async def predict_failure(sample: Dict[str, Any]):
    """Predict execution failure probability and stage-level risk scores."""
    prediction = failure_prediction_engine.predict(sample)
    return {
        "failure_probability": prediction.failure_probability,
        "success_probability": prediction.success_probability,
        "stage_risk_scores": prediction.stage_risk_scores,
        "model_type": prediction.model_type,
        "top_risk_factors": prediction.top_risk_factors,
    }


@router.post("/root-cause/analyze", response_model=Dict[str, Any])
async def analyze_root_cause(payload: Dict[str, Any]):
    """Analyze failing stage and infer probable root causes from logs/metrics/history."""
    result = root_cause_engine.analyze(payload)
    return {
        "failing_stage": result.failing_stage,
        "primary_cause": result.primary_cause,
        "confidence": result.confidence,
        "evidence": result.evidence,
        "contributing_factors": result.contributing_factors,
    }


@router.post("/self-healing/plan", response_model=Dict[str, Any])
async def generate_self_healing_plan(payload: Dict[str, Any]):
    """Generate safe automatic actions with approval/rollback strategy."""
    plan = self_healing_engine.decide(payload)
    return {
        "actions": plan.actions,
        "risk_level": plan.risk_level,
        "requires_human_approval": plan.requires_human_approval,
        "rollback_plan": plan.rollback_plan,
        "reason": plan.reason,
    }


@router.post("/recommendations", response_model=Dict[str, Any])
async def generate_recommendations(payload: Dict[str, Any]):
    """Generate optimization recommendations with confidence and priority scoring."""
    recommendations = recommendation_engine.recommend(payload)
    return {"recommendations": recommendations}


@router.post("/pipelines/auto-remediate", response_model=Dict[str, Any])
async def automate_pipeline_remediation(payload: Dict[str, Any]):
    """Run end-to-end automation: detect anomaly, predict risk, infer cause, and plan remediation."""
    telemetry = payload.get("telemetry", {})
    risk_features = payload.get("risk_features", {})
    diagnostics = payload.get("diagnostics", {})

    anomaly = anomaly_detection_engine.detect(telemetry)
    prediction = failure_prediction_engine.predict(risk_features)

    merged_diagnostics = {
        "stages": diagnostics.get("stages", risk_features.get("stages", [])),
        "logs": diagnostics.get("logs", []),
        "metrics": diagnostics.get(
            "metrics",
            {
                "cpu_percent": telemetry.get("cpu_percent", risk_features.get("avg_cpu_percent", 0)),
                "memory_percent": telemetry.get("memory_percent", risk_features.get("avg_memory_percent", 0)),
                "latency_spike": telemetry.get("duration_seconds", 0) > 180,
            },
        ),
        "history": diagnostics.get(
            "history",
            {
                "same_stage_failures_last_7d": risk_features.get("recent_error_count", 0),
                "recent_deployment": bool(payload.get("recent_deployment", False)),
            },
        ),
    }

    root_cause = root_cause_engine.analyze(merged_diagnostics)

    remediation_input = {
        "risk_score": max(anomaly.score, prediction.failure_probability),
        "primary_cause": root_cause.primary_cause,
        "failing_stage": root_cause.failing_stage,
        "retry_count": telemetry.get("retry_count", 0),
        "human_approval_mode": bool(payload.get("human_approval_mode", False)),
        "parallelizable": bool(risk_features.get("parallelizable", False)),
    }
    self_healing = self_healing_engine.decide(remediation_input)

    recommendations = recommendation_engine.recommend(
        {
            "avg_duration_seconds": telemetry.get("duration_seconds", 0),
            "retry_frequency": risk_features.get("retry_frequency", 0),
            "avg_cpu_percent": telemetry.get("cpu_percent", risk_features.get("avg_cpu_percent", 0)),
            "avg_memory_percent": telemetry.get("memory_percent", risk_features.get("avg_memory_percent", 0)),
            "stage_count": risk_features.get("stage_count", 0),
            "parallelizable": risk_features.get("parallelizable", False),
        }
    )

    return {
        "automation_status": "approval_required"
        if self_healing.requires_human_approval
        else "auto_executable",
        "anomaly": {
            "is_anomaly": anomaly.is_anomaly,
            "score": anomaly.score,
            "reasons": anomaly.reasons,
            "algorithm": anomaly.algorithm,
        },
        "prediction": {
            "failure_probability": prediction.failure_probability,
            "success_probability": prediction.success_probability,
            "stage_risk_scores": prediction.stage_risk_scores,
            "model_type": prediction.model_type,
            "top_risk_factors": prediction.top_risk_factors,
        },
        "root_cause": {
            "failing_stage": root_cause.failing_stage,
            "primary_cause": root_cause.primary_cause,
            "confidence": root_cause.confidence,
            "evidence": root_cause.evidence,
            "contributing_factors": root_cause.contributing_factors,
        },
        "self_healing_plan": {
            "actions": self_healing.actions,
            "risk_level": self_healing.risk_level,
            "requires_human_approval": self_healing.requires_human_approval,
            "rollback_plan": self_healing.rollback_plan,
            "reason": self_healing.reason,
        },
        "recommendations": recommendations,
    }
