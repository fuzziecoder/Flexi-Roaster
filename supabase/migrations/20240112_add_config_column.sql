-- Add missing config column to pipelines table
-- Run this in Supabase SQL Editor

ALTER TABLE public.pipelines 
ADD COLUMN IF NOT EXISTS config JSONB DEFAULT '{}'::jsonb;

-- Add comment
COMMENT ON COLUMN public.pipelines.config IS 'Pipeline configuration including stages and settings';
