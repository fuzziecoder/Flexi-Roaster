-- Complete RLS setup for all tables
-- Run this in Supabase SQL Editor

-- ============================================================================
-- ENABLE RLS ON ALL TABLES
-- ============================================================================
ALTER TABLE public.pipelines ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pipeline_stages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.execution_stages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_insights ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- PIPELINES - Users see only their own
-- ============================================================================
DROP POLICY IF EXISTS "Users can view all pipelines" ON public.pipelines;
DROP POLICY IF EXISTS "Users can view own pipelines" ON public.pipelines;
DROP POLICY IF EXISTS "Users can insert own pipelines" ON public.pipelines;
DROP POLICY IF EXISTS "Users can update own pipelines" ON public.pipelines;
DROP POLICY IF EXISTS "Users can delete own pipelines" ON public.pipelines;
DROP POLICY IF EXISTS "Service role has full access to pipelines" ON public.pipelines;

CREATE POLICY "Users can view own pipelines"
ON public.pipelines FOR SELECT
TO authenticated
USING (auth.uid() = owner_id);

CREATE POLICY "Users can insert own pipelines"
ON public.pipelines FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "Users can update own pipelines"
ON public.pipelines FOR UPDATE
TO authenticated
USING (auth.uid() = owner_id)
WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "Users can delete own pipelines"
ON public.pipelines FOR DELETE
TO authenticated
USING (auth.uid() = owner_id);

-- ============================================================================
-- PIPELINE STAGES - Inherit from pipeline ownership
-- ============================================================================
DROP POLICY IF EXISTS "Users can view pipeline stages" ON public.pipeline_stages;
DROP POLICY IF EXISTS "Users can manage pipeline stages" ON public.pipeline_stages;

CREATE POLICY "Users can view pipeline stages"
ON public.pipeline_stages FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM public.pipelines
        WHERE pipelines.id = pipeline_stages.pipeline_id
        AND pipelines.owner_id = auth.uid()
    )
);

CREATE POLICY "Users can manage pipeline stages"
ON public.pipeline_stages FOR ALL
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM public.pipelines
        WHERE pipelines.id = pipeline_stages.pipeline_id
        AND pipelines.owner_id = auth.uid()
    )
)
WITH CHECK (
    EXISTS (
        SELECT 1 FROM public.pipelines
        WHERE pipelines.id = pipeline_stages.pipeline_id
        AND pipelines.owner_id = auth.uid()
    )
);

-- ============================================================================
-- EXECUTIONS - Users see executions of their pipelines
-- ============================================================================
DROP POLICY IF EXISTS "Users can view executions" ON public.executions;
DROP POLICY IF EXISTS "Users can create executions" ON public.executions;

CREATE POLICY "Users can view executions"
ON public.executions FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM public.pipelines
        WHERE pipelines.id = executions.pipeline_id
        AND pipelines.owner_id = auth.uid()
    )
);

CREATE POLICY "Users can create executions"
ON public.executions FOR INSERT
TO authenticated
WITH CHECK (
    EXISTS (
        SELECT 1 FROM public.pipelines
        WHERE pipelines.id = executions.pipeline_id
        AND pipelines.owner_id = auth.uid()
    )
);

-- ============================================================================
-- EXECUTION STAGES - Inherit from execution/pipeline ownership
-- ============================================================================
DROP POLICY IF EXISTS "Users can view execution stages" ON public.execution_stages;

CREATE POLICY "Users can view execution stages"
ON public.execution_stages FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM public.executions e
        JOIN public.pipelines p ON p.id = e.pipeline_id
        WHERE e.id = execution_stages.execution_id
        AND p.owner_id = auth.uid()
    )
);

-- ============================================================================
-- LOGS - Users see logs from their executions
-- ============================================================================
DROP POLICY IF EXISTS "Users can view logs" ON public.logs;

CREATE POLICY "Users can view logs"
ON public.logs FOR SELECT
TO authenticated
USING (
    execution_id IS NULL OR
    EXISTS (
        SELECT 1 FROM public.executions e
        JOIN public.pipelines p ON p.id = e.pipeline_id
        WHERE e.id = logs.execution_id
        AND p.owner_id = auth.uid()
    )
);

-- ============================================================================
-- ALERTS - Users see alerts from their pipelines
-- ============================================================================
DROP POLICY IF EXISTS "Users can view alerts" ON public.alerts;
DROP POLICY IF EXISTS "Users can update alerts" ON public.alerts;

CREATE POLICY "Users can view alerts"
ON public.alerts FOR SELECT
TO authenticated
USING (
    execution_id IS NULL OR
    EXISTS (
        SELECT 1 FROM public.executions e
        JOIN public.pipelines p ON p.id = e.pipeline_id
        WHERE e.id = alerts.execution_id
        AND p.owner_id = auth.uid()
    )
);

CREATE POLICY "Users can update alerts"
ON public.alerts FOR UPDATE
TO authenticated
USING (
    execution_id IS NULL OR
    EXISTS (
        SELECT 1 FROM public.executions e
        JOIN public.pipelines p ON p.id = e.pipeline_id
        WHERE e.id = alerts.execution_id
        AND p.owner_id = auth.uid()
    )
);

-- ============================================================================
-- METRICS - Users see metrics from their executions
-- ============================================================================
DROP POLICY IF EXISTS "Users can view metrics" ON public.metrics;

CREATE POLICY "Users can view metrics"
ON public.metrics FOR SELECT
TO authenticated
USING (
    execution_id IS NULL OR
    EXISTS (
        SELECT 1 FROM public.executions e
        JOIN public.pipelines p ON p.id = e.pipeline_id
        WHERE e.id = metrics.execution_id
        AND p.owner_id = auth.uid()
    )
);

-- ============================================================================
-- AI INSIGHTS - Users see insights from their pipelines
-- ============================================================================
DROP POLICY IF EXISTS "Users can view ai insights" ON public.ai_insights;

CREATE POLICY "Users can view ai insights"
ON public.ai_insights FOR SELECT
TO authenticated
USING (
    execution_id IS NULL OR
    EXISTS (
        SELECT 1 FROM public.executions e
        JOIN public.pipelines p ON p.id = e.pipeline_id
        WHERE e.id = ai_insights.execution_id
        AND p.owner_id = auth.uid()
    )
);
