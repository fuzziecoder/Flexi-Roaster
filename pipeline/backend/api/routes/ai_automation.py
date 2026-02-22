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
