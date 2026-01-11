import type { Pipeline, PipelineExecution } from '@/types/pipeline';
import type { MetricsData, MetricsHistory } from '@/types/metrics';
import type { LogEntry, Alert, AIInsight, Notification } from '@/types/common';

// Mock Pipelines
export const mockPipelines: Pipeline[] = [
    {
        id: 'pl-001',
        name: 'Customer Data ETL',
        description: 'Extract, transform, and load customer data from multiple sources',
        status: 'running',
        progress: 67,
        lastExecution: new Date(Date.now() - 300000).toISOString(),
        stages: [
            { id: 's1', name: 'Extract', type: 'input', status: 'completed' },
            { id: 's2', name: 'Validate', type: 'validation', status: 'completed' },
            { id: 's3', name: 'Transform', type: 'processing', status: 'running' },
            { id: 's4', name: 'Load', type: 'storage', status: 'pending' },
        ],
        createdAt: new Date(Date.now() - 86400000 * 30).toISOString(),
        updatedAt: new Date(Date.now() - 300000).toISOString(),
    },
    {
        id: 'pl-002',
        name: 'ML Model Training',
        description: 'Train and deploy machine learning models',
        status: 'completed',
        progress: 100,
        lastExecution: new Date(Date.now() - 3600000).toISOString(),
        stages: [
            { id: 's1', name: 'Data Load', type: 'input', status: 'completed' },
            { id: 's2', name: 'Feature Engineering', type: 'processing', status: 'completed' },
            { id: 's3', name: 'Training', type: 'processing', status: 'completed' },
            { id: 's4', name: 'Evaluation', type: 'validation', status: 'completed' },
            { id: 's5', name: 'Deploy', type: 'notification', status: 'completed' },
        ],
        createdAt: new Date(Date.now() - 86400000 * 15).toISOString(),
        updatedAt: new Date(Date.now() - 3600000).toISOString(),
    },
    {
        id: 'pl-003',
        name: 'Real-time Log Processor',
        description: 'Process and analyze application logs in real-time',
        status: 'running',
        progress: 100,
        lastExecution: new Date().toISOString(),
        stages: [
            { id: 's1', name: 'Stream Input', type: 'input', status: 'running' },
            { id: 's2', name: 'Parse', type: 'processing', status: 'running' },
            { id: 's3', name: 'Analyze', type: 'processing', status: 'running' },
            { id: 's4', name: 'Store', type: 'storage', status: 'running' },
        ],
        createdAt: new Date(Date.now() - 86400000 * 60).toISOString(),
        updatedAt: new Date().toISOString(),
    },
    {
        id: 'pl-004',
        name: 'Fraud Detection',
        description: 'Detect and flag potentially fraudulent transactions',
        status: 'failed',
        progress: 45,
        lastExecution: new Date(Date.now() - 7200000).toISOString(),
        stages: [
            { id: 's1', name: 'Ingest', type: 'input', status: 'completed' },
            { id: 's2', name: 'Enrich', type: 'processing', status: 'completed', error: 'Connection timeout' },
            { id: 's3', name: 'Score', type: 'processing', status: 'failed' },
            { id: 's4', name: 'Alert', type: 'notification', status: 'pending' },
        ],
        createdAt: new Date(Date.now() - 86400000 * 45).toISOString(),
        updatedAt: new Date(Date.now() - 7200000).toISOString(),
    },
    {
        id: 'pl-005',
        name: 'Report Generator',
        description: 'Generate daily business reports',
        status: 'pending',
        progress: 0,
        lastExecution: new Date(Date.now() - 86400000).toISOString(),
        nextExecution: new Date(Date.now() + 3600000).toISOString(),
        stages: [
            { id: 's1', name: 'Query', type: 'input', status: 'pending' },
            { id: 's2', name: 'Aggregate', type: 'processing', status: 'pending' },
            { id: 's3', name: 'Format', type: 'processing', status: 'pending' },
            { id: 's4', name: 'Send', type: 'notification', status: 'pending' },
        ],
        createdAt: new Date(Date.now() - 86400000 * 90).toISOString(),
        updatedAt: new Date(Date.now() - 86400000).toISOString(),
    },
];

// Mock Recent Executions
export const mockExecutions: PipelineExecution[] = [
    {
        id: 'ex-001',
        pipelineId: 'pl-001',
        pipelineName: 'Customer Data ETL',
        status: 'running',
        startTime: new Date(Date.now() - 300000).toISOString(),
        stagesCompleted: 2,
        totalStages: 4,
    },
    {
        id: 'ex-002',
        pipelineId: 'pl-002',
        pipelineName: 'ML Model Training',
        status: 'completed',
        startTime: new Date(Date.now() - 7200000).toISOString(),
        endTime: new Date(Date.now() - 3600000).toISOString(),
        duration: 3600000,
        stagesCompleted: 5,
        totalStages: 5,
    },
    {
        id: 'ex-003',
        pipelineId: 'pl-004',
        pipelineName: 'Fraud Detection',
        status: 'failed',
        startTime: new Date(Date.now() - 9000000).toISOString(),
        endTime: new Date(Date.now() - 7200000).toISOString(),
        duration: 1800000,
        stagesCompleted: 2,
        totalStages: 4,
        error: 'Connection timeout to enrichment service',
    },
];

// Mock Metrics
export const mockMetrics: MetricsData = {
    cpu: 67,
    memory: 54,
    throughput: 1247,
    activeExecutions: 3,
    failureRate: 2.4,
    avgDuration: 45000,
    totalPipelines: 24,
    successRate: 97.6,
};

// Mock Metrics History (last 24 hours)
export const mockMetricsHistory: MetricsHistory = {
    cpu: Array.from({ length: 24 }, (_, i) => ({
        timestamp: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
        value: 50 + Math.random() * 30,
    })),
    memory: Array.from({ length: 24 }, (_, i) => ({
        timestamp: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
        value: 40 + Math.random() * 25,
    })),
    throughput: Array.from({ length: 24 }, (_, i) => ({
        timestamp: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
        value: 800 + Math.random() * 600,
    })),
    executionTime: Array.from({ length: 24 }, (_, i) => ({
        timestamp: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
        value: 30000 + Math.random() * 40000,
    })),
};

// Mock Logs
export const mockLogs: LogEntry[] = [
    { id: 'log-001', timestamp: new Date(Date.now() - 5000).toISOString(), level: 'info', service: 'pipeline-executor', message: 'Stage "Transform" started for pipeline pl-001' },
    { id: 'log-002', timestamp: new Date(Date.now() - 15000).toISOString(), level: 'success', service: 'ml-service', message: 'Model training completed with 94.2% accuracy' },
    { id: 'log-003', timestamp: new Date(Date.now() - 30000).toISOString(), level: 'warn', service: 'data-ingestion', message: 'High latency detected in data stream, current: 450ms' },
    { id: 'log-004', timestamp: new Date(Date.now() - 45000).toISOString(), level: 'error', service: 'fraud-detector', message: 'Connection timeout to enrichment service after 30s' },
    { id: 'log-005', timestamp: new Date(Date.now() - 60000).toISOString(), level: 'info', service: 'scheduler', message: 'Scheduled pipeline "Report Generator" for 09:00 UTC' },
    { id: 'log-006', timestamp: new Date(Date.now() - 120000).toISOString(), level: 'debug', service: 'cache-manager', message: 'Cache hit ratio: 87.3%, evictions: 124' },
    { id: 'log-007', timestamp: new Date(Date.now() - 180000).toISOString(), level: 'info', service: 'api-gateway', message: 'Processed 1,247 requests in the last minute' },
    { id: 'log-008', timestamp: new Date(Date.now() - 240000).toISOString(), level: 'success', service: 'deployment', message: 'New model version v2.3.1 deployed successfully' },
];

// Mock Alerts
export const mockAlerts: Alert[] = [
    {
        id: 'alert-001',
        title: 'Pipeline Failure',
        message: 'Fraud Detection pipeline failed due to connection timeout',
        severity: 'critical',
        source: 'pl-004',
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        acknowledged: false,
    },
    {
        id: 'alert-002',
        title: 'High Memory Usage',
        message: 'Memory usage exceeded 80% threshold on worker-node-3',
        severity: 'high',
        source: 'worker-node-3',
        timestamp: new Date(Date.now() - 1800000).toISOString(),
        acknowledged: false,
    },
    {
        id: 'alert-003',
        title: 'Slow Query Detected',
        message: 'Query execution time exceeded 10s threshold',
        severity: 'medium',
        source: 'database',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        acknowledged: true,
    },
];

// Mock AI Insights
export const mockAIInsights: AIInsight[] = [
    {
        id: 'ai-001',
        type: 'prediction',
        title: 'Predicted Failure Risk',
        description: 'Pipeline "Fraud Detection" has 78% probability of failure in the next execution due to recurring connection issues.',
        confidence: 0.78,
        impact: 'high',
        timestamp: new Date(Date.now() - 300000).toISOString(),
        actionable: true,
        action: 'Review and update connection pool settings',
    },
    {
        id: 'ai-002',
        type: 'optimization',
        title: 'Performance Optimization',
        description: 'Parallelizing stages 2-3 in "Customer Data ETL" could reduce execution time by ~35%.',
        confidence: 0.92,
        impact: 'medium',
        timestamp: new Date(Date.now() - 600000).toISOString(),
        actionable: true,
        action: 'Enable parallel execution',
    },
    {
        id: 'ai-003',
        type: 'anomaly',
        title: 'Anomaly Detected',
        description: 'Unusual spike in data volume for "Real-time Log Processor" - 3x normal throughput.',
        confidence: 0.85,
        impact: 'medium',
        timestamp: new Date(Date.now() - 900000).toISOString(),
        actionable: false,
    },
    {
        id: 'ai-004',
        type: 'recommendation',
        title: 'Resource Allocation',
        description: 'Based on usage patterns, consider scaling down worker nodes during 02:00-06:00 UTC to reduce costs by ~18%.',
        confidence: 0.88,
        impact: 'low',
        timestamp: new Date(Date.now() - 1200000).toISOString(),
        actionable: true,
        action: 'Configure auto-scaling schedule',
    },
];

// Mock Notifications
export const mockNotifications: Notification[] = [
    { id: 'notif-001', title: 'Pipeline Completed', message: 'ML Model Training finished successfully', type: 'success', read: false, timestamp: new Date(Date.now() - 3600000).toISOString() },
    { id: 'notif-002', title: 'Alert Triggered', message: 'Fraud Detection pipeline failed', type: 'error', read: false, timestamp: new Date(Date.now() - 7200000).toISOString() },
    { id: 'notif-003', title: 'New AI Insight', message: 'Performance optimization suggestion available', type: 'info', read: true, timestamp: new Date(Date.now() - 10800000).toISOString() },
];
