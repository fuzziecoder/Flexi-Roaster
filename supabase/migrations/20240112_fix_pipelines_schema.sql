-- Fix pipelines table schema
-- Run this in Supabase SQL Editor

-- Step 1: Drop the config column if it exists (it was added but not used)
ALTER TABLE public.pipelines DROP COLUMN IF EXISTS config;

-- Step 2: Make definition column nullable first
ALTER TABLE public.pipelines ALTER COLUMN definition DROP NOT NULL;

-- Step 3: Rename definition to config
ALTER TABLE public.pipelines RENAME COLUMN definition TO config;

-- Step 4: Make config nullable (since we're creating pipelines with empty config initially)
-- Already nullable from step 2

-- Update comment
COMMENT ON COLUMN public.pipelines.config IS 'Pipeline configuration including stages and settings';
