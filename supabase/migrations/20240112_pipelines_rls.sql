-- Add RLS policy for pipelines so users only see their own pipelines
-- Run this in Supabase SQL Editor

-- Drop existing policy if it exists
DROP POLICY IF EXISTS "Users can view all pipelines" ON public.pipelines;

-- Create new policy: Users can only view their own pipelines
CREATE POLICY "Users can view own pipelines"
ON public.pipelines
FOR SELECT
TO authenticated
USING (auth.uid() = owner_id);

-- Users can insert their own pipelines (already handled by usePipelines hook)
CREATE POLICY "Users can insert own pipelines"
ON public.pipelines
FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = owner_id);

-- Users can update their own pipelines
CREATE POLICY "Users can update own pipelines"
ON public.pipelines
FOR UPDATE
TO authenticated
USING (auth.uid() = owner_id)
WITH CHECK (auth.uid() = owner_id);

-- Users can delete their own pipelines
CREATE POLICY "Users can delete own pipelines"
ON public.pipelines
FOR DELETE
TO authenticated
USING (auth.uid() = owner_id);

-- Service role has full access
CREATE POLICY "Service role has full access to pipelines"
ON public.pipelines
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);
