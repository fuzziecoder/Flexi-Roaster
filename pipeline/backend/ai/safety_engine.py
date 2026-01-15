"""
AI Safety Module for FlexiRoaster Pipeline Automation.
Provides deterministic, explainable AI for failure prediction and anomaly handling.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from statistics import mean, stdev

from config import settings

logger = logging.getLogger(__name__)


# ===================
# Data Classes
# ===================

@dataclass
class PipelineStats:
    """Statistics for a pipeline used in risk assessment"""
    pipeline_id: str
    pipeline_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    avg_duration: float = 0.0
    std_duration: float = 0.0
    last_7_days_failures: int = 0
    last_7_days_executions: int = 0
    stage_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    consecutive_failures: int = 0
    
    @property
    def failure_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.failed_executions / self.total_executions
    
    @property
    def success_rate(self) -> float:
        return 1.0 - self.failure_rate


@dataclass
class StageStats:
    """Statistics for a stage"""
    stage_id: str
    stage_name: str
    total_executions: int = 0
    failed_executions: int = 0
    avg_duration: float = 0.0
    std_duration: float = 0.0
    is_critical: bool = True


@dataclass
class RiskAssessment:
    """Result of pre-execution risk assessment"""
    risk_score: float
    risk_level: str  # low, medium, high, critical
    should_block: bool
    factors: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    explanation: str = ""


@dataclass
class AnomalyDetection:
    """Result of runtime anomaly detection"""
    is_anomaly: bool
    anomaly_type: Optional[str] = None  # time_spike, error_burst, resource_spike
    severity: str = "low"  # low, medium, high, critical
    details: Dict[str, Any] = field(default_factory=dict)
    recommended_action: Optional[str] = None
    explanation: str = ""


class SafeAction(str, Enum):
    """Safe actions in priority order (lowest risk first)"""
    CONTINUE = "continue"
    RETRY_STAGE = "retry_stage"
    SKIP_STAGE = "skip_stage"
    PAUSE_PIPELINE = "pause_pipeline"
    ROLLBACK = "rollback"
    TERMINATE = "terminate"


# ===================
# AI Safety Engine
# ===================

class AISafetyEngine:
    """
    Deterministic, explainable AI safety engine.
    Provides pre-execution risk assessment and runtime anomaly detection.
    """
    
    def __init__(self):
        self.risk_thresholds = {
            "low": settings.AI_RISK_THRESHOLD_LOW,
            "medium": settings.AI_RISK_THRESHOLD_MEDIUM,
            "high": settings.AI_RISK_THRESHOLD_HIGH,
            "critical": 0.9
        }
        
        # Weights for risk factors
        self.risk_weights = {
            "historical_failure_rate": 0.30,
            "recent_failures": 0.25,
            "consecutive_failures": 0.15,
            "duration_anomaly": 0.10,
            "stage_complexity": 0.10,
            "time_since_success": 0.10
        }
        
        # Action priority order (safest first)
        self.action_priority = [
            SafeAction.CONTINUE,
            SafeAction.RETRY_STAGE,
            SafeAction.SKIP_STAGE,
            SafeAction.PAUSE_PIPELINE,
            SafeAction.ROLLBACK,
            SafeAction.TERMINATE
        ]
    
    # ==================
    # Pre-Execution Assessment
    # ==================
    
    def assess_risk(self, stats: PipelineStats) -> RiskAssessment:
        """
        Assess failure risk before execution starts.
        Returns a deterministic risk score with explanation.
        """
        factors = []
        recommendations = []
        
        # Factor 1: Historical failure rate (30%)
        failure_rate_score = min(stats.failure_rate * 1.5, 1.0)
        factors.append({
            "name": "historical_failure_rate",
            "value": round(stats.failure_rate * 100, 1),
            "score": round(failure_rate_score, 3),
            "weight": self.risk_weights["historical_failure_rate"],
            "description": f"Historical failure rate: {stats.failure_rate*100:.1f}%"
        })
        
        if stats.failure_rate > 0.3:
            recommendations.append("Review pipeline configuration and error handling")
        
        # Factor 2: Recent failures (25%)
        recent_rate = (stats.last_7_days_failures / stats.last_7_days_executions 
                       if stats.last_7_days_executions > 0 else 0)
        recent_score = min(recent_rate * 2, 1.0)
        factors.append({
            "name": "recent_failures",
            "value": stats.last_7_days_failures,
            "score": round(recent_score, 3),
            "weight": self.risk_weights["recent_failures"],
            "description": f"{stats.last_7_days_failures} failures in last 7 days"
        })
        
        if stats.last_7_days_failures >= 3:
            recommendations.append("Investigate recent failure patterns")
        
        # Factor 3: Consecutive failures (15%)
        consecutive_score = min(stats.consecutive_failures / 3, 1.0)
        factors.append({
            "name": "consecutive_failures",
            "value": stats.consecutive_failures,
            "score": round(consecutive_score, 3),
            "weight": self.risk_weights["consecutive_failures"],
            "description": f"{stats.consecutive_failures} consecutive failures"
        })
        
        if stats.consecutive_failures >= 2:
            recommendations.append("Consider running a test execution first")
        
        # Factor 4: Duration anomaly (10%)
        duration_score = 0.0
        if stats.avg_duration > 0:
            if stats.avg_duration > settings.EXECUTOR_DEFAULT_TIMEOUT * 0.8:
                duration_score = 0.8
            elif stats.avg_duration > 120:
                duration_score = min(stats.avg_duration / 300, 0.6)
        factors.append({
            "name": "duration_anomaly",
            "value": round(stats.avg_duration, 1),
            "score": round(duration_score, 3),
            "weight": self.risk_weights["duration_anomaly"],
            "description": f"Average duration: {stats.avg_duration:.1f}s"
        })
        
        if duration_score > 0.5:
            recommendations.append("Consider optimizing slow stages")
        
        # Factor 5: Stage complexity (10%)
        complexity_score = min(stats.stage_count / 15, 1.0)
        factors.append({
            "name": "stage_complexity",
            "value": stats.stage_count,
            "score": round(complexity_score, 3),
            "weight": self.risk_weights["stage_complexity"],
            "description": f"{stats.stage_count} stages in pipeline"
        })
        
        if stats.stage_count > 10:
            recommendations.append("Consider breaking pipeline into smaller units")
        
        # Factor 6: Time since last success (10%)
        time_score = 0.0
        if stats.last_success_time:
            days_since = (datetime.now() - stats.last_success_time).days
            time_score = min(days_since / 7, 1.0)
            factors.append({
                "name": "time_since_success",
                "value": days_since,
                "score": round(time_score, 3),
                "weight": self.risk_weights["time_since_success"],
                "description": f"{days_since} days since last success"
            })
        
        # Calculate weighted risk score
        risk_score = sum(
            factor["score"] * factor["weight"]
            for factor in factors
        )
        risk_score = round(min(risk_score, 1.0), 3)
        
        # Determine risk level
        risk_level = self._get_risk_level(risk_score)
        
        # Determine if should block
        should_block = (
            settings.AI_BLOCK_HIGH_RISK and 
            risk_level in ["high", "critical"]
        )
        
        # Generate explanation
        explanation = self._generate_risk_explanation(
            stats, risk_score, risk_level, factors
        )
        
        return RiskAssessment(
            risk_score=risk_score,
            risk_level=risk_level,
            should_block=should_block,
            factors=factors,
            recommendations=recommendations,
            explanation=explanation
        )
    
    def _get_risk_level(self, score: float) -> str:
        """Determine risk level from score"""
        if score >= self.risk_thresholds["critical"]:
            return "critical"
        elif score >= self.risk_thresholds["high"]:
            return "high"
        elif score >= self.risk_thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    def _generate_risk_explanation(
        self,
        stats: PipelineStats,
        risk_score: float,
        risk_level: str,
        factors: List[Dict]
    ) -> str:
        """Generate human-readable explanation of risk assessment"""
        lines = [
            f"Risk Assessment for pipeline '{stats.pipeline_name}':",
            f"Overall Risk Score: {risk_score:.1%} ({risk_level.upper()})",
            "",
            "Contributing Factors:"
        ]
        
        # Sort factors by contribution (score * weight)
        sorted_factors = sorted(
            factors,
            key=lambda f: f["score"] * f["weight"],
            reverse=True
        )
        
        for factor in sorted_factors:
            contribution = factor["score"] * factor["weight"] * 100
            lines.append(f"  - {factor['description']} (contribution: {contribution:.1f}%)")
        
        return "\n".join(lines)
    
    # ==================
    # Runtime Anomaly Detection
    # ==================
    
    def detect_anomaly(
        self,
        current_duration: float,
        avg_duration: float,
        std_duration: float,
        error_count: int,
        stage_errors: List[str] = None
    ) -> AnomalyDetection:
        """
        Detect anomalies during execution.
        Uses statistical analysis for deterministic detection.
        """
        anomalies_detected = []
        
        # Time spike detection
        if avg_duration > 0 and std_duration > 0:
            z_score = (current_duration - avg_duration) / std_duration if std_duration > 0 else 0
            if z_score > settings.AI_ANOMALY_TIME_MULTIPLIER:
                anomalies_detected.append({
                    "type": "time_spike",
                    "severity": "high" if z_score > 5 else "medium",
                    "z_score": round(z_score, 2),
                    "expected": round(avg_duration, 1),
                    "actual": round(current_duration, 1)
                })
        elif current_duration > avg_duration * settings.AI_ANOMALY_TIME_MULTIPLIER:
            anomalies_detected.append({
                "type": "time_spike",
                "severity": "medium",
                "multiplier": round(current_duration / avg_duration, 2) if avg_duration > 0 else 0,
                "expected": round(avg_duration, 1),
                "actual": round(current_duration, 1)
            })
        
        # Error burst detection
        if error_count >= settings.AI_ANOMALY_ERROR_THRESHOLD:
            anomalies_detected.append({
                "type": "error_burst",
                "severity": "high" if error_count > 10 else "medium",
                "error_count": error_count,
                "errors": stage_errors[:5] if stage_errors else []
            })
        
        if not anomalies_detected:
            return AnomalyDetection(is_anomaly=False)
        
        # Get most severe anomaly
        severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        main_anomaly = max(
            anomalies_detected,
            key=lambda a: severity_order.get(a["severity"], 0)
        )
        
        # Recommend action based on anomaly
        recommended_action = self._recommend_action_for_anomaly(main_anomaly)
        
        # Generate explanation
        explanation = self._generate_anomaly_explanation(main_anomaly)
        
        return AnomalyDetection(
            is_anomaly=True,
            anomaly_type=main_anomaly["type"],
            severity=main_anomaly["severity"],
            details=main_anomaly,
            recommended_action=recommended_action,
            explanation=explanation
        )
    
    def _recommend_action_for_anomaly(self, anomaly: Dict) -> str:
        """Recommend safest action for an anomaly"""
        anomaly_type = anomaly["type"]
        severity = anomaly["severity"]
        
        if anomaly_type == "time_spike":
            if severity == "high":
                return SafeAction.PAUSE_PIPELINE.value
            return SafeAction.CONTINUE.value
        
        if anomaly_type == "error_burst":
            if severity == "high":
                return SafeAction.ROLLBACK.value
            elif severity == "medium":
                return SafeAction.PAUSE_PIPELINE.value
            return SafeAction.RETRY_STAGE.value
        
        return SafeAction.CONTINUE.value
    
    def _generate_anomaly_explanation(self, anomaly: Dict) -> str:
        """Generate explanation for detected anomaly"""
        if anomaly["type"] == "time_spike":
            return (
                f"Execution time anomaly detected. "
                f"Current duration ({anomaly.get('actual', 0):.1f}s) significantly exceeds "
                f"expected duration ({anomaly.get('expected', 0):.1f}s)."
            )
        elif anomaly["type"] == "error_burst":
            return (
                f"Error burst detected. "
                f"{anomaly.get('error_count', 0)} errors occurred, "
                f"exceeding the threshold of {settings.AI_ANOMALY_ERROR_THRESHOLD}."
            )
        return "Anomaly detected in pipeline execution."
    
    # ==================
    # Safe Action Selection
    # ==================
    
    def select_safe_action(
        self,
        context: Dict[str, Any],
        is_stage_critical: bool = True,
        retry_count: int = 0,
        max_retries: int = 3
    ) -> Tuple[SafeAction, str]:
        """
        Select the safest action based on context.
        Always chooses the lowest-risk option that can handle the situation.
        
        Returns: (action, explanation)
        """
        error = context.get("error")
        anomaly = context.get("anomaly")
        risk_level = context.get("risk_level", "low")
        
        # No error or anomaly - continue
        if not error and not anomaly:
            return SafeAction.CONTINUE, "No issues detected, continuing execution."
        
        # Check if retry is viable
        if retry_count < max_retries:
            if error and not anomaly:
                return (
                    SafeAction.RETRY_STAGE,
                    f"Stage failed with error. Attempting retry {retry_count + 1}/{max_retries}."
                )
        
        # Non-critical stage can be skipped
        if not is_stage_critical:
            return (
                SafeAction.SKIP_STAGE,
                "Non-critical stage failed. Skipping to continue pipeline execution."
            )
        
        # High risk or persistent failures - pause
        if risk_level in ["high", "critical"] or retry_count >= max_retries:
            if anomaly and anomaly.get("type") == "error_burst":
                return (
                    SafeAction.ROLLBACK,
                    f"Error burst detected after {retry_count} retries. "
                    "Rolling back to prevent cascading failures."
                )
            return (
                SafeAction.PAUSE_PIPELINE,
                f"Pipeline paused after {retry_count} failed retries. "
                "Awaiting manual intervention."
            )
        
        # Default to pause for safety
        return SafeAction.PAUSE_PIPELINE, "Pausing pipeline for safety review."
    
    # ==================
    # Insight Generation
    # ==================
    
    def generate_insights(
        self,
        stats: PipelineStats,
        risk_assessment: Optional[RiskAssessment] = None
    ) -> List[Dict[str, Any]]:
        """Generate actionable insights for a pipeline"""
        insights = []
        
        if risk_assessment is None:
            risk_assessment = self.assess_risk(stats)
        
        # Risk-based insight
        if risk_assessment.risk_level in ["high", "critical"]:
            insights.append({
                "type": "prediction",
                "severity": risk_assessment.risk_level,
                "title": f"{risk_assessment.risk_level.title()} Failure Risk Detected",
                "message": (
                    f"Pipeline has a {risk_assessment.risk_score:.0%} risk of failure "
                    f"based on historical data."
                ),
                "recommendation": risk_assessment.recommendations[0] if risk_assessment.recommendations else None,
                "confidence": risk_assessment.risk_score,
                "factors": risk_assessment.factors,
                "explanation": risk_assessment.explanation
            })
        elif risk_assessment.risk_level == "medium":
            insights.append({
                "type": "prediction",
                "severity": "medium",
                "title": "Moderate Risk Detected",
                "message": f"Recent execution history shows {stats.last_7_days_failures} failures.",
                "recommendation": "Monitor execution logs for patterns",
                "confidence": risk_assessment.risk_score,
                "factors": risk_assessment.factors[:3],
                "explanation": risk_assessment.explanation
            })
        
        # Performance insight
        if stats.avg_duration > 120:
            insights.append({
                "type": "performance",
                "severity": "medium" if stats.avg_duration > 180 else "low",
                "title": "Long Execution Time",
                "message": f"Average execution duration is {stats.avg_duration:.1f}s",
                "recommendation": "Consider optimizing slow stages or adding parallel execution",
                "confidence": 0.85,
                "factors": [],
                "explanation": f"Executions taking longer than 2 minutes may impact throughput."
            })
        
        # Complexity insight
        if stats.stage_count > 10:
            insights.append({
                "type": "optimization",
                "severity": "low",
                "title": "High Stage Complexity",
                "message": f"Pipeline has {stats.stage_count} stages",
                "recommendation": "Consider breaking into smaller, reusable pipelines",
                "confidence": 0.75,
                "factors": [],
                "explanation": "Complex pipelines are harder to debug and maintain."
            })
        
        # Success pattern insight
        if stats.success_rate > 0.95 and stats.total_executions > 20:
            insights.append({
                "type": "success",
                "severity": "low",
                "title": "Stable Pipeline",
                "message": f"Excellent {stats.success_rate:.1%} success rate over {stats.total_executions} executions",
                "recommendation": "Use as template for other pipelines",
                "confidence": 0.95,
                "factors": [],
                "explanation": "This pipeline demonstrates reliable, consistent execution."
            })
        
        # Consecutive failures warning
        if stats.consecutive_failures >= 3:
            insights.append({
                "type": "anomaly",
                "severity": "high",
                "title": "Consecutive Failures Detected",
                "message": f"{stats.consecutive_failures} consecutive failures",
                "recommendation": "Investigate root cause before next execution",
                "confidence": 0.9,
                "factors": [],
                "explanation": "Multiple consecutive failures often indicate a systemic issue."
            })
        
        return insights


# Singleton instance
ai_safety_engine = AISafetyEngine()
