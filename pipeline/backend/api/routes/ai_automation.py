"""AI automation endpoints for anomaly detection and failure prediction."""
from typing import Any, Dict, List

from fastapi import APIRouter

from ai.anomaly_detection import anomaly_detection_engine
from ai.failure_prediction import failure_prediction_engine

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
