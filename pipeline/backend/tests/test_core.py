"""
Unit tests for FlexiRoaster Pipeline Automation.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

# Test AI Safety Engine
class TestAISafetyEngine:
    """Tests for AI Safety Engine"""
    
    def test_risk_assessment_low_risk(self):
        """Test risk assessment for a healthy pipeline"""
        from ai.safety_engine import AISafetyEngine, PipelineStats
        
        engine = AISafetyEngine()
        stats = PipelineStats(
            pipeline_id="test-1",
            pipeline_name="Test Pipeline",
            total_executions=100,
            successful_executions=95,
            failed_executions=5,
            avg_duration=30.0,
            last_7_days_failures=1,
            last_7_days_executions=10,
            stage_count=3
        )
        
        assessment = engine.assess_risk(stats)
        
        assert assessment.risk_level == "low"
        assert assessment.should_block == False
        assert 0 <= assessment.risk_score <= 1
        assert len(assessment.factors) > 0
    
    def test_risk_assessment_high_risk(self):
        """Test risk assessment for a problematic pipeline"""
        from ai.safety_engine import AISafetyEngine, PipelineStats
        
        engine = AISafetyEngine()
        stats = PipelineStats(
            pipeline_id="test-2",
            pipeline_name="Failing Pipeline",
            total_executions=10,
            successful_executions=2,
            failed_executions=8,
            avg_duration=200.0,
            last_7_days_failures=5,
            last_7_days_executions=5,
            stage_count=12,
            consecutive_failures=3
        )
        
        assessment = engine.assess_risk(stats)
        
        assert assessment.risk_level == "high"
        assert assessment.risk_score > 0.5
        assert len(assessment.recommendations) > 0
    
    def test_anomaly_detection_time_spike(self):
        """Test anomaly detection for time spikes"""
        from ai.safety_engine import AISafetyEngine
        
        engine = AISafetyEngine()
        result = engine.detect_anomaly(
            current_duration=300.0,
            avg_duration=30.0,
            std_duration=10.0,
            error_count=0
        )
        
        assert result.is_anomaly == True
        assert result.anomaly_type == "time_spike"
    
    def test_anomaly_detection_error_burst(self):
        """Test anomaly detection for error bursts"""
        from ai.safety_engine import AISafetyEngine
        
        engine = AISafetyEngine()
        result = engine.detect_anomaly(
            current_duration=30.0,
            avg_duration=30.0,
            std_duration=5.0,
            error_count=10,
            stage_errors=["Error 1", "Error 2"]
        )
        
        assert result.is_anomaly == True
        assert result.anomaly_type == "error_burst"
    
    def test_safe_action_selection_retry(self):
        """Test safe action selection prefers retry"""
        from ai.safety_engine import AISafetyEngine, SafeAction
        
        engine = AISafetyEngine()
        action, explanation = engine.select_safe_action(
            context={"error": "Connection timeout"},
            is_stage_critical=True,
            retry_count=0,
            max_retries=3
        )
        
        assert action == SafeAction.RETRY_STAGE
    
    def test_safe_action_selection_skip_non_critical(self):
        """Test safe action skips non-critical stages"""
        from ai.safety_engine import AISafetyEngine, SafeAction
        
        engine = AISafetyEngine()
        action, explanation = engine.select_safe_action(
            context={"error": "Stage failed"},
            is_stage_critical=False,
            retry_count=3,
            max_retries=3
        )
        
        assert action == SafeAction.SKIP_STAGE
    
    def test_insight_generation(self):
        """Test insight generation for pipelines"""
        from ai.safety_engine import AISafetyEngine, PipelineStats
        
        engine = AISafetyEngine()
        stats = PipelineStats(
            pipeline_id="test-3",
            pipeline_name="Test Pipeline",
            total_executions=50,
            successful_executions=48,
            failed_executions=2,
            avg_duration=25.0,
            stage_count=4
        )
        
        insights = engine.generate_insights(stats)
        
        # Should have success insight for stable pipeline
        success_insights = [i for i in insights if i['type'] == 'success']
        assert len(success_insights) > 0


# Test Redis State Manager
class TestRedisStateManager:
    """Tests for Redis State Manager (with mocks)"""
    
    @pytest.mark.asyncio
    async def test_fallback_mode_when_redis_unavailable(self):
        """Test fallback to local locks when Redis is unavailable"""
        from core.redis_state import RedisStateManager
        
        manager = RedisStateManager()
        # Don't initialize - simulates Redis being unavailable
        
        assert manager.is_available == False
        assert manager._fallback_mode == False  # Not yet in fallback
    
    @pytest.mark.asyncio
    async def test_health_check_disconnected(self):
        """Test health check when disconnected"""
        from core.redis_state import RedisStateManager
        
        manager = RedisStateManager()
        health = await manager.health_check()
        
        assert health['status'] == 'disconnected'
        assert health['fallback_mode'] == True


# Test Schemas
class TestSchemas:
    """Tests for Pydantic schemas"""
    
    def test_pipeline_create_schema(self):
        """Test pipeline create schema validation"""
        from api.schemas import PipelineCreate, StageCreate, StageTypeEnum
        
        pipeline = PipelineCreate(
            name="Test Pipeline",
            description="Test description",
            stages=[
                StageCreate(
                    id="stage-1",
                    name="Stage 1",
                    type=StageTypeEnum.INPUT,
                    config={"source": "api"}
                )
            ]
        )
        
        assert pipeline.name == "Test Pipeline"
        assert len(pipeline.stages) == 1
        assert pipeline.stages[0].type == StageTypeEnum.INPUT
    
    def test_execution_status_enum(self):
        """Test execution status values"""
        from api.schemas import ExecutionStatusEnum
        
        assert ExecutionStatusEnum.PENDING == "pending"
        assert ExecutionStatusEnum.RUNNING == "running"
        assert ExecutionStatusEnum.COMPLETED == "completed"
        assert ExecutionStatusEnum.FAILED == "failed"
        assert ExecutionStatusEnum.ROLLED_BACK == "rolled_back"


# Test Configuration
class TestConfig:
    """Tests for configuration"""
    
    def test_default_config_values(self):
        """Test default configuration values"""
        from config import Settings
        
        settings = Settings()
        
        assert settings.APP_NAME == "FlexiRoaster"
        assert settings.API_PREFIX == "/api"
        assert settings.EXECUTOR_MAX_RETRIES == 3
        assert settings.AI_RISK_THRESHOLD_HIGH == 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
