-- Sample Data for Testing
-- Migration: 20240112_sample_data

-- Note: Run this AFTER creating a test user through Supabase Auth

-- Sample Pipelines
INSERT INTO public.pipelines (id, name, description, owner_id, definition, tags) VALUES
(
    '550e8400-e29b-41d4-a716-446655440001',
    'Customer Data Validation',
    'Validate and clean customer data from CSV source',
    auth.uid(), -- Will use the authenticated user
    '{
        "stages": [
            {
                "id": "input",
                "name": "Read CSV",
                "type": "input",
                "config": {"source": "data/customers.csv"}
            },
            {
                "id": "validate",
                "name": "Validate Schema",
                "type": "validation",
                "config": {"schema": {"email": "email", "age": "integer"}},
                "dependencies": ["input"]
            },
            {
                "id": "output",
                "name": "Write to Database",
                "type": "output",
                "config": {"table": "customers"},
                "dependencies": ["validate"]
            }
        ]
    }'::jsonb,
    ARRAY['data-quality', 'validation']
),
(
    '550e8400-e29b-41d4-a716-446655440002',
    'ML Model Training',
    'Train fraud detection model on transaction data',
    auth.uid(),
    '{
        "stages": [
            {
                "id": "extract",
                "name": "Extract Features",
                "type": "transform",
                "config": {"features": ["amount", "location", "time"]}
            },
            {
                "id": "train",
                "name": "Train Model",
                "type": "transform",
                "config": {"algorithm": "random_forest"},
                "dependencies": ["extract"]
            },
            {
                "id": "evaluate",
                "name": "Evaluate Model",
                "type": "validation",
                "config": {"metrics": ["accuracy", "precision", "recall"]},
                "dependencies": ["train"]
            }
        ]
    }'::jsonb,
    ARRAY['ml', 'fraud-detection']
);

-- Sample Execution
INSERT INTO public.executions (id, pipeline_id, status, triggered_by, trigger_type) VALUES
(
    '660e8400-e29b-41d4-a716-446655440001',
    '550e8400-e29b-41d4-a716-446655440001',
    'completed',
    auth.uid(),
    'manual'
);

-- Sample Logs
INSERT INTO public.logs (level, execution_id, message) VALUES
('INFO', '660e8400-e29b-41d4-a716-446655440001', 'Pipeline execution started'),
('INFO', '660e8400-e29b-41d4-a716-446655440001', 'Stage: Read CSV - Processing 1000 records'),
('SUCCESS', '660e8400-e29b-41d4-a716-446655440001', 'Pipeline completed successfully');

-- Sample Metrics
INSERT INTO public.metrics (metric_name, metric_type, value, tags) VALUES
('execution_duration', 'histogram', 45.2, '{"pipeline": "customer-validation"}'::jsonb),
('success_rate', 'gauge', 0.95, '{}'::jsonb),
('throughput', 'counter', 1200, '{"unit": "records/min"}'::jsonb);

-- Sample Alert
INSERT INTO public.alerts (severity, title, message, pipeline_id, status) VALUES
(
    'medium',
    'Pipeline Execution Slow',
    'Customer Data Validation pipeline took 2x longer than average',
    '550e8400-e29b-41d4-a716-446655440001',
    'open'
);

-- Sample AI Insight
INSERT INTO public.ai_insights (insight_type, pipeline_id, severity, title, description, recommendation, confidence) VALUES
(
    'optimization',
    '550e8400-e29b-41d4-a716-446655440001',
    'medium',
    'Parallel Processing Opportunity',
    'Validation stage can be parallelized to improve performance',
    'Consider splitting validation into multiple workers',
    0.85
);
