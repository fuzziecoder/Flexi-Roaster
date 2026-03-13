"""
Prometheus Metrics Definitions for Pipeline Monitoring
"""
import os
from prometheus_client import Counter, Histogram, Gauge, REGISTRY

# Disable the default process/platform metrics for cleaner app-specific dashboards if desired
# from prometheus_client import process_collector, platform_collector, gc_collector
# REGISTRY.unregister(process_collector.ProcessCollector())
# REGISTRY.unregister(platform_collector.PlatformCollector())
# REGISTRY.unregister(gc_collector.GCCollector())

# --- Counters ---
# Tracks the total number of pipeline executions, labeled by pipeline_id and final status
pipeline_executions_total = Counter(
    'pipeline_executions_total',
    'Total number of pipeline executions',
    ['pipeline_id', 'status']
)

# Tracks the total number of explicit failures, labeled by pipeline_id
pipeline_failures_total = Counter(
    'pipeline_failures_total',
    'Total number of failed pipeline executions',
    ['pipeline_id']
)

# --- Histograms ---
# Tracks the distribution of total end-to-end execution duration for a pipeline
# Buckets: 1s, 5s, 15s, 30s, 1m, 2m, 5m, 10m, 15m, 30m, 1h, +Inf
pipeline_execution_duration_seconds = Histogram(
    'pipeline_execution_duration_seconds',
    'Pipeline execution duration in seconds',
    ['pipeline_id'],
    buckets=(1.0, 5.0, 15.0, 30.0, 60.0, 120.0, 300.0, 600.0, 900.0, 1800.0, 3600.0, float('inf'))
)

# Tracks the duration of individual stages within a pipeline
stage_execution_duration_seconds = Histogram(
    'stage_execution_duration_seconds',
    'Stage execution duration in seconds',
    ['pipeline_id', 'stage_name', 'status'],
    buckets=(0.1, 0.5, 1.0, 5.0, 15.0, 30.0, 60.0, 120.0, 300.0, float('inf'))
)

# --- Gauges ---
# Tracks the current number of concurrently running pipelines
pipeline_active_executions = Gauge(
    'pipeline_active_executions',
    'Number of currently running pipeline executions',
    ['pipeline_id']
)
