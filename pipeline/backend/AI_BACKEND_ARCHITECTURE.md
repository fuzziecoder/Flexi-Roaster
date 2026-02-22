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
   - Extracts error signatures (timeout, auth failure, schema mismatch, dependency error).
   - Emits error-pattern features and stage errors to monitoring/anomaly services.

3. **Metrics Stream Adapter**
   - Consumes CPU, memory, throughput, and latency metrics.
   - Correlates by `pipeline_id` + `execution_id` + `stage_id`.

4. **Monitoring Engine (`ai/monitoring_engine.py`)**
   - Maintains sliding-window telemetry state per pipeline.
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

---

## 2) Anomaly Detection System

### What is detected
- unusual execution time
- abnormal data volume
- sudden failure spikes
- abnormal CPU/memory usage
- log pattern anomalies

### Algorithms
The backend uses a **hybrid approach** in `ai/anomaly_detection.py`:
1. **Isolation Forest (unsupervised)**
   - Finds rare/outlier points in multivariate telemetry without labels.
   - Ideal for unknown/novel anomalies.
2. **Statistical detection (z-score / threshold rules)**
   - Detects strong deviations from baseline (`|z| >= 3`).
   - Enforces deterministic safety checks for retry bursts and log anomalies.
3. **Pattern scoring**
   - Error-log signature diversity converted into `error_pattern_score`.

### Feature extraction
Per event, extract:
- `execution_time_s`
- `data_volume_mb`
- `failure_count_1h`
- `cpu_percent`
- `memory_percent`
- `retry_count`
- `error_pattern_score` (derived from unique stage error signatures)

### Training flow
1. Pull historical telemetry from Supabase + metrics store.
2. Normalize to event schema.
3. Build baseline mean/std stats for key metrics.
4. Train Isolation Forest on feature matrix.
5. Persist model artifacts + metadata (version, training window, contamination).

### Online inference pipeline
1. Runtime event enters `/api/ai/anomaly/detect`.
2. Feature extractor builds vector.
3. Inference executes:
   - Isolation Forest score/prediction
   - z-score checks vs baseline
   - rule checks for retry burst/log-pattern anomalies
4. Return `is_anomaly`, `score`, `reasons`, `algorithm`.
5. Orchestrator consumes result and executes remediation runbook (retry, scale, pause, rollback).

---

## 3) Failure Prediction Engine

### Predictions produced
- pipeline-level failure probability
- execution success probability
- stage-level risk scores

### Inputs
- historical execution outcomes
- past error counts/signatures
- pipeline topology/config (`stage_count`, `critical_stage_count`)
- system load (`avg_cpu_percent`, `avg_memory_percent`)
- retry behavior (`retry_frequency`)

### Model design
Implemented in `ai/failure_prediction.py`:
1. **Primary supervised model: Gradient Boosting Classifier**
   - Learns nonlinear feature interactions.
   - Outputs failure probability through `predict_proba`.
2. **Heuristic fallback model**
   - Weighted risk formula when model artifact/dependency unavailable.
   - Keeps prediction service operational in degraded environments.
3. **Stage risk decomposition**
   - Pipeline probability + stage-specific multipliers:
     - stage historical failure rate
     - stage retry count
     - critical-stage bonus

### Training strategy
1. Build labeled dataset (`failed` boolean target).
2. Time-split training/validation to avoid leakage.
3. Calibrate probability thresholds for alerting and auto-remediation.
4. Track metrics:
   - ROC-AUC
   - Precision@K for failure alerts
   - Brier score for probability calibration
5. Register model version and rollout gradually (shadow -> canary -> full).

### Inference flow
1. Trigger execution request or periodic preflight check.
2. Call `/api/ai/prediction/predict` with execution context.
3. Return:
   - `failure_probability`
   - `success_probability`
   - `stage_risk_scores`
   - `top_risk_factors`
4. Policy engine decides whether to continue, gate, or apply preventive actions.

---

## 4) Self-Healing Control Loop
1. Monitor telemetry continuously.
2. Detect anomalies and predict near-term failures.
3. Choose safe actions (retry, skip non-critical, pause, rollback, terminate).
4. Verify outcome and feed execution data back to training sets.
5. Improve model quality with periodic retraining.

This architecture enables production-grade, AI-assisted, automated pipeline operations.
### Automation Hook
The monitoring snapshot can be polled by an orchestration worker that applies runbooks:
- high failure rate + repeated pattern -> retry/backoff + ticket
- latency spike + high CPU -> scale worker pool
- throughput drop + retry burst -> pause non-critical stages

This creates the foundation for fully automated, self-healing pipeline operations.
