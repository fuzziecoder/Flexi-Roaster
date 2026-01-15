-- Rename definition column to config in pipelines table
-- Run this in Supabase SQL Editor

-- Rename the column
ALTER TABLE public.pipelines 
RENAME COLUMN definition TO config;

-- Update comment
COMMENT ON COLUMN public.pipelines.config IS 'Pipeline configuration including stages and settings (renamed from definition)';
