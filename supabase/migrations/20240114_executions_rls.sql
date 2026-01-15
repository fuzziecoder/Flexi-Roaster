-- ============================================================================
-- RLS POLICIES FOR EXECUTIONS TABLE
-- Run this SQL in your Supabase SQL Editor to fix execution permissions
-- ============================================================================

-- Enable RLS on executions table
ALTER TABLE public.executions ENABLE ROW LEVEL SECURITY;

-- Allow users to view executions for pipelines they own
CREATE POLICY "Users can view executions for their pipelines" ON public.executions
FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM public.pipelines 
        WHERE pipelines.id = executions.pipeline_id 
        AND pipelines.owner_id = auth.uid()
    )
);

-- Allow users to insert executions for pipelines they own
CREATE POLICY "Users can create executions for their pipelines" ON public.executions
FOR INSERT WITH CHECK (
    EXISTS (
        SELECT 1 FROM public.pipelines 
        WHERE pipelines.id = executions.pipeline_id 
        AND pipelines.owner_id = auth.uid()
    )
    AND triggered_by = auth.uid()
);

-- Allow users to update their own executions
CREATE POLICY "Users can update their own executions" ON public.executions
FOR UPDATE USING (triggered_by = auth.uid());

-- Allow users to delete their own executions
CREATE POLICY "Users can delete their own executions" ON public.executions
FOR DELETE USING (triggered_by = auth.uid());
