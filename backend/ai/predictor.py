"""
AI Failure Prediction Model
Simple rule-based predictor with ML capabilities
"""
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class PipelineStats:
    """Pipeline statistics for prediction"""
    pipeline_id: str
    total_executions: int
    failed_executions: int
    avg_duration: float
    last_7_days_failures: int
    stage_count: int
    last_failure_time: str = None


class FailurePredictor:
    """AI-powered failure prediction"""
    
    def __init__(self):
        self.risk_thresholds = {
            'high': 0.7,
            'medium': 0.4,
            'low': 0.2
        }
    
    def calculate_failure_rate(self, stats: PipelineStats) -> float:
        """Calculate failure rate"""
        if stats.total_executions == 0:
            return 0.0
        return stats.failed_executions / stats.total_executions
    
    def calculate_risk_score(self, stats: PipelineStats) -> float:
        """
        Calculate risk score (0-1) based on multiple factors
        
        Factors:
        - Historical failure rate (40%)
        - Recent failures (30%)
        - Average duration anomaly (20%)
        - Stage complexity (10%)
        """
        # Historical failure rate
        failure_rate = self.calculate_failure_rate(stats)
        historical_score = min(failure_rate * 2, 1.0)  # Cap at 1.0
        
        # Recent failures (last 7 days)
        recent_score = min(stats.last_7_days_failures / 5, 1.0)  # 5+ failures = max risk
        
        # Duration anomaly (if avg > 120s, consider risky)
        duration_score = min(stats.avg_duration / 240, 1.0)  # 240s = max risk
        
        # Stage complexity (more stages = more risk)
        complexity_score = min(stats.stage_count / 10, 1.0)  # 10+ stages = max risk
        
        # Weighted average
        risk_score = (
            historical_score * 0.4 +
            recent_score * 0.3 +
            duration_score * 0.2 +
            complexity_score * 0.1
        )
        
        return round(risk_score, 3)
    
    def get_risk_level(self, risk_score: float) -> str:
        """Get risk level from score"""
        if risk_score >= self.risk_thresholds['high']:
            return 'high'
        elif risk_score >= self.risk_thresholds['medium']:
            return 'medium'
        else:
            return 'low'
    
    def generate_insights(self, stats: PipelineStats) -> List[Dict[str, Any]]:
        """Generate AI insights for a pipeline"""
        insights = []
        
        risk_score = self.calculate_risk_score(stats)
        risk_level = self.get_risk_level(risk_score)
        failure_rate = self.calculate_failure_rate(stats)
        
        # Main prediction insight
        if risk_level == 'high':
            insights.append({
                'type': 'prediction',
                'severity': 'high',
                'title': 'High Failure Risk Detected',
                'message': f'Pipeline has {failure_rate*100:.1f}% failure rate with {stats.last_7_days_failures} failures in last 7 days',
                'recommendation': 'Review pipeline configuration and add error handling',
                'confidence': risk_score,
                'pipeline_id': stats.pipeline_id
            })
        elif risk_level == 'medium':
            insights.append({
                'type': 'prediction',
                'severity': 'medium',
                'title': 'Moderate Risk Detected',
                'message': f'Pipeline shows {stats.last_7_days_failures} recent failures',
                'recommendation': 'Monitor execution logs for patterns',
                'confidence': risk_score,
                'pipeline_id': stats.pipeline_id
            })
        
        # Duration anomaly
        if stats.avg_duration > 120:
            insights.append({
                'type': 'performance',
                'severity': 'medium',
                'title': 'Long Execution Time',
                'message': f'Average duration is {stats.avg_duration:.1f}s',
                'recommendation': 'Optimize stage processing or add parallel execution',
                'confidence': 0.85,
                'pipeline_id': stats.pipeline_id
            })
        
        # Complexity warning
        if stats.stage_count > 7:
            insights.append({
                'type': 'optimization',
                'severity': 'low',
                'title': 'High Stage Complexity',
                'message': f'Pipeline has {stats.stage_count} stages',
                'recommendation': 'Consider breaking into smaller pipelines',
                'confidence': 0.75,
                'pipeline_id': stats.pipeline_id
            })
        
        # Success pattern
        if failure_rate < 0.05 and stats.total_executions > 10:
            insights.append({
                'type': 'success',
                'severity': 'low',
                'title': 'Stable Pipeline',
                'message': f'Excellent {(1-failure_rate)*100:.1f}% success rate',
                'recommendation': 'Use as template for other pipelines',
                'confidence': 0.95,
                'pipeline_id': stats.pipeline_id
            })
        
        return insights
    
    def predict_all(self, pipelines_stats: List[PipelineStats]) -> List[Dict[str, Any]]:
        """Generate insights for all pipelines"""
        all_insights = []
        
        for stats in pipelines_stats:
            insights = self.generate_insights(stats)
            all_insights.extend(insights)
        
        # Sort by severity and confidence
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        all_insights.sort(
            key=lambda x: (severity_order.get(x['severity'], 3), -x['confidence'])
        )
        
        return all_insights


# Singleton instance
predictor = FailurePredictor()
