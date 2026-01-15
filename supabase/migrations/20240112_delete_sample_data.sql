-- Delete all sample/mock data from the database
-- Run this in Supabase SQL Editor to clean up

-- Delete sample data from all tables
DELETE FROM public.ai_insights WHERE true;
DELETE FROM public.metrics WHERE true;
DELETE FROM public.logs WHERE true;
DELETE FROM public.alerts WHERE true;
DELETE FROM public.execution_stages WHERE true;
DELETE FROM public.executions WHERE true;
DELETE FROM public.pipeline_stages WHERE true;
DELETE FROM public.pipelines WHERE true;

-- Reset sequences if needed
-- This ensures new records start from 1
ALTER SEQUENCE IF EXISTS logs_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS metrics_id_seq RESTART WITH 1;

-- Verify deletion
SELECT 'Pipelines' as table_name, COUNT(*) as count FROM public.pipelines
UNION ALL
SELECT 'Executions', COUNT(*) FROM public.executions
UNION ALL
SELECT 'Logs', COUNT(*) FROM public.logs
UNION ALL
SELECT 'Alerts', COUNT(*) FROM public.alerts
UNION ALL
SELECT 'AI Insights', COUNT(*) FROM public.ai_insights;
