-- FlexiRoaster Initial Database Schema
-- Migration: 20240112_initial_schema

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ============================================================================
-- USER PROFILES
-- ============================================================================
-- Extends Supabase auth.users with additional profile information
CREATE TABLE public.user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    avatar_url TEXT,
    role TEXT DEFAULT 'user' CHECK (role IN ('admin', 'user', 'viewer')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id, full_name, avatar_url)
    VALUES (
        NEW.id,
        NEW.raw_user_meta_data->>'full_name',
        NEW.raw_user_meta_data->>'avatar_url'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================================
-- PIPELINES
-- ============================================================================
CREATE TABLE public.pipelines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES auth.users(id),
    definition JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    schedule_cron TEXT,
    timeout_seconds INTEGER DEFAULT 3600,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_timeout CHECK (timeout_seconds > 0 AND timeout_seconds <= 86400)
);

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_pipelines_updated_at
    BEFORE UPDATE ON public.pipelines
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================================================
-- PIPELINE STAGES
-- ============================================================================
CREATE TABLE public.pipeline_stages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_id UUID REFERENCES public.pipelines(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('input', 'transform', 'validation', 'output')),
    order_index INTEGER NOT NULL,
    config JSONB,
    dependencies TEXT[],
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_order CHECK (order_index >= 0)
);

CREATE INDEX idx_pipeline_stages_pipeline ON public.pipeline_stages(pipeline_id);

-- ============================================================================
-- EXECUTIONS
-- ============================================================================
CREATE TABLE public.executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_id UUID REFERENCES public.pipelines(id),
    status TEXT NOT NULL DEFAULT 'pending' 
        CHECK (status IN ('pending', 'queued', 'running', 'completed', 'failed', 'cancelled')),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    triggered_by UUID REFERENCES auth.users(id),
    trigger_type TEXT DEFAULT 'manual' CHECK (trigger_type IN ('manual', 'scheduled', 'webhook', 'api')),
    error_message TEXT,
    context JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_executions_status ON public.executions(status) WHERE status IN ('running', 'pending', 'queued');
CREATE INDEX idx_executions_pipeline ON public.executions(pipeline_id);
CREATE INDEX idx_executions_created ON public.executions(created_at DESC);
CREATE INDEX idx_executions_triggered_by ON public.executions(triggered_by);

-- ============================================================================
-- EXECUTION STAGES
-- ============================================================================
CREATE TABLE public.execution_stages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID REFERENCES public.executions(id) ON DELETE CASCADE,
    stage_id UUID REFERENCES public.pipeline_stages(id),
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    output JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0
);

CREATE INDEX idx_execution_stages_execution ON public.execution_stages(execution_id);

-- ============================================================================
-- LOGS
-- ============================================================================
CREATE TABLE public.logs (
    id BIGSERIAL PRIMARY KEY,
    level TEXT NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARN', 'ERROR', 'SUCCESS')),
    service TEXT,
    pipeline_id UUID REFERENCES public.pipelines(id),
    execution_id UUID REFERENCES public.executions(id) ON DELETE CASCADE,
    stage_id UUID,
    message TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for log queries
CREATE INDEX idx_logs_execution ON public.logs(execution_id);
CREATE INDEX idx_logs_pipeline ON public.logs(pipeline_id);
CREATE INDEX idx_logs_created ON public.logs(created_at DESC);
CREATE INDEX idx_logs_level ON public.logs(level) WHERE level IN ('ERROR', 'WARN');

-- ============================================================================
-- METRICS
-- ============================================================================
CREATE TABLE public.metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_name TEXT NOT NULL,
    metric_type TEXT NOT NULL CHECK (metric_type IN ('counter', 'gauge', 'histogram')),
    value NUMERIC NOT NULL,
    tags JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for metrics queries
CREATE INDEX idx_metrics_name ON public.metrics(metric_name);
CREATE INDEX idx_metrics_created ON public.metrics(created_at DESC);
CREATE INDEX idx_metrics_name_created ON public.metrics(metric_name, created_at DESC);

-- ============================================================================
-- ALERTS
-- ============================================================================
CREATE TABLE public.alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    source TEXT,
    pipeline_id UUID REFERENCES public.pipelines(id),
    execution_id UUID REFERENCES public.executions(id),
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'acknowledged', 'resolved')),
    acknowledged_by UUID REFERENCES auth.users(id),
    acknowledged_at TIMESTAMPTZ,
    resolved_by UUID REFERENCES auth.users(id),
    resolved_at TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for alert queries
CREATE INDEX idx_alerts_status ON public.alerts(status) WHERE status = 'open';
CREATE INDEX idx_alerts_severity ON public.alerts(severity);
CREATE INDEX idx_alerts_created ON public.alerts(created_at DESC);
CREATE INDEX idx_alerts_pipeline ON public.alerts(pipeline_id);

-- ============================================================================
-- AI INSIGHTS
-- ============================================================================
CREATE TABLE public.ai_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    insight_type TEXT NOT NULL CHECK (insight_type IN ('failure_prediction', 'anomaly', 'optimization', 'cost')),
    pipeline_id UUID REFERENCES public.pipelines(id),
    execution_id UUID REFERENCES public.executions(id),
    severity TEXT CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),
    title TEXT NOT NULL,
    description TEXT,
    recommendation TEXT,
    confidence NUMERIC(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    metadata JSONB,
    is_dismissed BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for AI insights
CREATE INDEX idx_ai_insights_pipeline ON public.ai_insights(pipeline_id);
CREATE INDEX idx_ai_insights_type ON public.ai_insights(insight_type);
CREATE INDEX idx_ai_insights_dismissed ON public.ai_insights(is_dismissed) WHERE is_dismissed = false;

-- ============================================================================
-- ENABLE REALTIME
-- ============================================================================
-- Enable realtime for tables that need live updates
ALTER PUBLICATION supabase_realtime ADD TABLE public.executions;
ALTER PUBLICATION supabase_realtime ADD TABLE public.logs;
ALTER PUBLICATION supabase_realtime ADD TABLE public.metrics;
ALTER PUBLICATION supabase_realtime ADD TABLE public.alerts;
ALTER PUBLICATION supabase_realtime ADD TABLE public.ai_insights;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================
COMMENT ON TABLE public.user_profiles IS 'Extended user profile information';
COMMENT ON TABLE public.pipelines IS 'Pipeline definitions and metadata';
COMMENT ON TABLE public.executions IS 'Pipeline execution records';
COMMENT ON TABLE public.logs IS 'Centralized application and execution logs';
COMMENT ON TABLE public.metrics IS 'Time-series metrics data';
COMMENT ON TABLE public.alerts IS 'System and pipeline alerts';
COMMENT ON TABLE public.ai_insights IS 'AI-generated insights and recommendations';
