# FlexiRoaster AI Backend Architecture (Self-Healing Pipelines)

## 1) Pipeline Monitoring Engine

### Goal
Continuously monitor and normalize pipeline signals so downstream AI services can predict failures, detect anomalies, and trigger remediation actions.

### Components
1. **Supabase Change Consumer**
   - Pulls pipeline execution rows (status, duration, retries, stage failures).
   - Sends normalized events to Monitoring API (`/api/monitoring/ingest`).

2. **Log Pattern Extractor**
   - Parses execution/stage logs.
   - Extracts error signatures (e.g., timeout, auth failure, schema mismatch).
   - Emits error pattern payloads into the same ingest endpoint.

3. **Metrics Stream Adapter**
   - Consumes CPU, memory, throughput, and latency metrics.
   - Correlates by `pipeline_id` + `execution_id`.

4. **Monitoring Engine (`ai/monitoring_engine.py`)**
   - Maintains sliding window telemetry state per pipeline.
   - Computes health KPIs:
     - execution duration trend
     - failure rate + stage failures
     - retry frequency
     - avg CPU/memory
     - throughput changes
     - latency spikes
     - dominant error patterns

5. **Snapshot API (`/api/monitoring/{pipeline_id}/snapshot`)**
   - Returns pre-aggregated metrics/signals for dashboard + automation workflows.

### Data Flow
```text
Supabase executions ─┐
Execution logs ──────┼──> Normalizer/Adapters ──> Monitoring ingest API
Metrics stream ──────┘                                │
                                                       v
                                           Sliding-window Monitoring Engine
                                                       │
                            ┌──────────────────────────┴────────────────────────┐
                            v                                                   v
                     Dashboard AI insights                            Auto-remediation planner
```

### Automation Hook
The monitoring snapshot can be polled by an orchestration worker that applies runbooks:
- high failure rate + repeated pattern -> retry/backoff + ticket
- latency spike + high CPU -> scale worker pool
- throughput drop + retry burst -> pause non-critical stages

This creates the foundation for fully automated, self-healing pipeline operations.
