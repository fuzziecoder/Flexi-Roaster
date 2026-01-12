-- FlexiRoaster Row Level Security Policies
-- Migration: 20240112_rls_policies

-- ============================================================================
-- ENABLE RLS ON ALL TABLES
-- ============================================================================
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pipelines ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pipeline_stages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.execution_stages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_insights ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- USER PROFILES POLICIES
-- ============================================================================
-- Everyone can view all profiles
CREATE POLICY "Users can view all profiles"
    ON public.user_profiles
    FOR SELECT
    USING (true);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
    ON public.user_profiles
    FOR UPDATE
    USING (auth.uid() = id);

-- ============================================================================
-- PIPELINES POLICIES
-- ============================================================================
-- Everyone can view active pipelines
CREATE POLICY "Users can view pipelines"
    ON public.pipelines
    FOR SELECT
    USING (is_active = true OR owner_id = auth.uid());

-- Authenticated users can create pipelines
CREATE POLICY "Authenticated users can create pipelines"
    ON public.pipelines
    FOR INSERT
    WITH CHECK (auth.uid() IS NOT NULL AND owner_id = auth.uid());

-- Owners and admins can update pipelines
CREATE POLICY "Owners can update their pipelines"
    ON public.pipelines
    FOR UPDATE
    USING (
        owner_id = auth.uid() OR
        EXISTS (
            SELECT 1 FROM public.user_profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Only admins can delete pipelines
CREATE POLICY "Admins can delete pipelines"
    ON public.pipelines
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.user_profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- ============================================================================
-- PIPELINE STAGES POLICIES
-- ============================================================================
-- Users can view stages of pipelines they can see
CREATE POLICY "Users can view pipeline stages"
    ON public.pipeline_stages
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.pipelines
            WHERE id = pipeline_id AND (is_active = true OR owner_id = auth.uid())
        )
    );

-- Pipeline owners can manage stages
CREATE POLICY "Pipeline owners can manage stages"
    ON public.pipeline_stages
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.pipelines
            WHERE id = pipeline_id AND owner_id = auth.uid()
        )
    );

-- ============================================================================
-- EXECUTIONS POLICIES
-- ============================================================================
-- Users can view all executions
CREATE POLICY "Users can view executions"
    ON public.executions
    FOR SELECT
    USING (auth.uid() IS NOT NULL);

-- Authenticated users can create executions
CREATE POLICY "Authenticated users can create executions"
    ON public.executions
    FOR INSERT
    WITH CHECK (auth.uid() IS NOT NULL AND triggered_by = auth.uid());

-- Users can update executions they triggered
CREATE POLICY "Users can update their executions"
    ON public.executions
    FOR UPDATE
    USING (triggered_by = auth.uid());

-- ============================================================================
-- EXECUTION STAGES POLICIES
-- ============================================================================
-- Users can view execution stages
CREATE POLICY "Users can view execution stages"
    ON public.execution_stages
    FOR SELECT
    USING (auth.uid() IS NOT NULL);

-- System can manage execution stages (via service role)
-- No user-level insert/update/delete policies - managed by backend

-- ============================================================================
-- LOGS POLICIES
-- ============================================================================
-- Authenticated users can view logs
CREATE POLICY "Users can view logs"
    ON public.logs
    FOR SELECT
    USING (auth.uid() IS NOT NULL);

-- Only service role can insert logs (no user policy)

-- ============================================================================
-- METRICS POLICIES
-- ============================================================================
-- Authenticated users can view metrics
CREATE POLICY "Users can view metrics"
    ON public.metrics
    FOR SELECT
    USING (auth.uid() IS NOT NULL);

-- Only service role can insert metrics (no user policy)

-- ============================================================================
-- ALERTS POLICIES
-- ============================================================================
-- Users can view all alerts
CREATE POLICY "Users can view alerts"
    ON public.alerts
    FOR SELECT
    USING (auth.uid() IS NOT NULL);

-- Users can acknowledge and resolve alerts
CREATE POLICY "Users can acknowledge alerts"
    ON public.alerts
    FOR UPDATE
    USING (auth.uid() IS NOT NULL)
    WITH CHECK (
        (status = 'acknowledged' AND acknowledged_by = auth.uid()) OR
        (status = 'resolved' AND resolved_by = auth.uid())
    );

-- ============================================================================
-- AI INSIGHTS POLICIES
-- ============================================================================
-- Users can view AI insights
CREATE POLICY "Users can view AI insights"
    ON public.ai_insights
    FOR SELECT
    USING (auth.uid() IS NOT NULL);

-- Users can dismiss insights
CREATE POLICY "Users can dismiss insights"
    ON public.ai_insights
    FOR UPDATE
    USING (auth.uid() IS NOT NULL)
    WITH CHECK (is_dismissed = true);

-- ============================================================================
-- HELPER FUNCTIONS FOR RLS
-- ============================================================================
-- Check if user is admin
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE id = auth.uid() AND role = 'admin'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Check if user owns pipeline
CREATE OR REPLACE FUNCTION public.owns_pipeline(pipeline_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.pipelines
        WHERE id = pipeline_uuid AND owner_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
