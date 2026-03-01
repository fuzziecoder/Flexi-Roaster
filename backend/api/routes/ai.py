"""
AI Insights API Routes
"""
from typing import List, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.api.schemas import SuccessResponse
from backend.db.database import get_db
from backend.db import crud
from backend.db.models import ExecutionDB
from backend.ai.predictor import predictor, PipelineStats
from backend.ai.forecasting import PipelineForecaster
from pydantic import BaseModel

router = APIRouter(prefix="/api/ai", tags=["ai"])

# Initialize the forecaster
forecaster = PipelineForecaster()


class AIInsight(BaseModel):
    """AI Insight schema"""
    type: str
    severity: str
    title: str
    message: str
    recommendation: str
    confidence: float
    pipeline_id: str = None
    timestamp: datetime = None


class AIInsightsResponse(BaseModel):
    """AI Insights response"""
    insights: List[AIInsight]
    total_count: int
    generated_at: datetime


class ForecastPrediction(BaseModel):
    date: str
    failure_probability: float
    confidence_interval: Dict[str, float]


class AnomalyAlert(BaseModel):
    timestamp: datetime
    duration: float
    z_score: float
    is_unusually_high: bool


class ForecastResponse(BaseModel):
    pipeline_id: str
    forecast_days: int
    predictions: List[ForecastPrediction]
    anomalies: List[AnomalyAlert]
    generated_at: datetime


@router.get("/insights", response_model=AIInsightsResponse)
async def get_ai_insights(db: Session = Depends(get_db)):
    """Get AI-generated insights for all pipelines"""
    
    # Get all pipelines
    db_pipelines = crud.get_pipelines(db)
    
    # Calculate statistics for each pipeline
    pipeline_stats = []
    
    for pipeline in db_pipelines:
        # Get executions for this pipeline
        all_executions = db.query(ExecutionDB).filter(
            ExecutionDB.pipeline_id == pipeline.id
        ).all()
        
        if not all_executions:
            continue
        
        # Calculate stats
        total = len(all_executions)
        failed = sum(1 for e in all_executions if e.status == 'failed')
        
        # Calculate average duration
        completed = [e for e in all_executions if e.duration is not None]
        avg_duration = sum(e.duration for e in completed) / len(completed) if completed else 0
        
        # Count recent failures (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_failures = sum(
            1 for e in all_executions 
            if e.status == 'failed' and e.started_at >= seven_days_ago
        )
        
        # Get stage count
        stage_count = len(pipeline.definition.get('stages', []))
        
        # Create stats object
        stats = PipelineStats(
            pipeline_id=pipeline.id,
            total_executions=total,
            failed_executions=failed,
            avg_duration=avg_duration,
            last_7_days_failures=recent_failures,
            stage_count=stage_count
        )
        
        pipeline_stats.append(stats)
    
    # Generate insights using AI predictor
    insights = predictor.predict_all(pipeline_stats)
    
    # Add timestamps
    for insight in insights:
        insight['timestamp'] = datetime.utcnow()
    
    return AIInsightsResponse(
        insights=[AIInsight(**insight) for insight in insights],
        total_count=len(insights),
        generated_at=datetime.utcnow()
    )


@router.get("/insights/{pipeline_id}", response_model=AIInsightsResponse)
async def get_pipeline_insights(pipeline_id: str, db: Session = Depends(get_db)):
    """Get AI insights for a specific pipeline"""
    
    # Get pipeline
    pipeline = crud.get_pipeline(db, pipeline_id)
    if not pipeline:
        return AIInsightsResponse(insights=[], total_count=0, generated_at=datetime.utcnow())
    
    # Get executions
    all_executions = db.query(ExecutionDB).filter(
        ExecutionDB.pipeline_id == pipeline_id
    ).all()
    
    if not all_executions:
        return AIInsightsResponse(insights=[], total_count=0, generated_at=datetime.utcnow())
    
    # Calculate stats
    total = len(all_executions)
    failed = sum(1 for e in all_executions if e.status == 'failed')
    completed = [e for e in all_executions if e.duration is not None]
    avg_duration = sum(e.duration for e in completed) / len(completed) if completed else 0
    
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_failures = sum(
        1 for e in all_executions 
        if e.status == 'failed' and e.started_at >= seven_days_ago
    )
    
    stage_count = len(pipeline.definition.get('stages', []))
    
    stats = PipelineStats(
        pipeline_id=pipeline_id,
        total_executions=total,
        failed_executions=failed,
        avg_duration=avg_duration,
        last_7_days_failures=recent_failures,
        stage_count=stage_count
    )
    
    # Generate insights
    insights = predictor.generate_insights(stats)
    
    for insight in insights:
        insight['timestamp'] = datetime.utcnow()
    
    return AIInsightsResponse(
        insights=[AIInsight(**insight) for insight in insights],
        total_count=len(insights),
        generated_at=datetime.utcnow()
    )


@router.get("/forecast/{pipeline_id}", response_model=ForecastResponse)
async def get_pipeline_forecast(
    pipeline_id: str, 
    periods: int = 7, 
    db: Session = Depends(get_db)
):
    """
    Get machine-learning time-series failure forecasts and duration anomalies
    for a specific pipeline.
    """
    # 1. Verify pipeline exists
    pipeline = crud.get_pipeline(db, pipeline_id)
    if not pipeline:
        return ForecastResponse(
            pipeline_id=pipeline_id,
            forecast_days=periods,
            predictions=[],
            anomalies=[],
            generated_at=datetime.utcnow()
        )
        
    # 2. Get historical executions for data preparation
    # We order by started_at so it is proper time-series data
    history = db.query(ExecutionDB).filter(
        ExecutionDB.pipeline_id == pipeline_id,
        ExecutionDB.status != 'pending',  # Only completed/failed runs count toward anomalies/training
        ExecutionDB.started_at.isnot(None)
    ).order_by(ExecutionDB.started_at.asc()).all()
    
    if not history:
        return ForecastResponse(
            pipeline_id=pipeline_id,
            forecast_days=periods,
            predictions=[],
            anomalies=[],
            generated_at=datetime.utcnow()
        )
        
    # Step 3/4 integration: Train the model
    # (In a real massive app, training happens in a background worker, but for our API we do it on demand)
    model = forecaster.train(history, pipeline_id)
    
    # Run the prediction map for the next X days
    predictions = forecaster.forecast(model, periods=periods)
    
    # Step 5 integration: Anomaly Detection
    # Get the raw prepared DataFrame
    df = forecaster.prepare_data(history, pipeline_id)
    # Scan it for standard deviation duration anomalies
    anomalies = forecaster.detect_anomalies(df)
    
    return ForecastResponse(
        pipeline_id=pipeline_id,
        forecast_days=periods,
        predictions=predictions,
        anomalies=anomalies,
        generated_at=datetime.utcnow()
    )

