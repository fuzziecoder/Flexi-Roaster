# FlexiRoaster AI Backend Architecture (Self-Healing Pipelines)

## 1) Pipeline Monitoring Engine
- **Inputs:** Supabase execution rows, stage/execution logs, infra metrics.
- **Output:** rolling per-pipeline snapshots (`duration`, `failure_rate`, `retries`, `cpu/memory`, `throughput`, `latency`, dominant error signatures).
- **APIs:**
  - `POST /api/monitoring/ingest`
  - `GET /api/monitoring/{pipeline_id}/snapshot`

## 2) Anomaly Detection System
Implemented in `ai/anomaly_detection.py`.

### Targets
- unusual execution time
- abnormal data volume
- sudden failure spikes
- abnormal resource usage
- error-pattern bursts

### Methods
- **Isolation Forest** for unsupervised multivariate anomalies.
- **Z-score + deterministic rules** for explainable threshold breaches.
- **Pattern scoring** for repeated error signatures.

### Online inference flow
1. Event ingested via monitoring API.
2. Feature vector built (`execution_time_s`, `failure_count_1h`, `cpu_percent`, etc.).
3. Hybrid scorer computes anomaly score + reasons.
4. API returns `is_anomaly`, `score`, `reasons`, and recommended guardrail action.

## 3) Failure Prediction Engine
Implemented in `ai/failure_prediction.py`.

### Outputs
- pipeline failure probability
- execution success probability
- stage-level risk scores

### Model strategy
- **Primary:** Gradient Boosting classifier.
- **Fallback:** deterministic heuristic risk model when model artifact/dependencies are unavailable.
- **Rollout:** shadow -> canary -> full.

## 4) Root Cause Analysis Engine
Implemented in `ai/root_cause_engine.py`, exposed via `/api/ai/root-cause/analyze`.

### Detectable causes
- failing stage
- connection/auth issues
- resource bottlenecks
- schema/data inconsistencies
- configuration drift

### Fusion logic
Logs + metrics + historical recurrence are merged into a confidence-scored root cause decision and contributing factors.

## 5) Self-Healing Engine
Implemented in `ai/self_healing_engine.py`, exposed via `/api/ai/self-healing/plan`.

### Automatic actions
- retry failed stage
- restart worker
- increase timeout
- scale worker resources
- switch fallback service
- rollback to known-good config

### Safety policy
- Apply lowest-risk action first.
- Force human approval for high-risk actions.
- Persist pre-change snapshot for deterministic rollback.

## 6) Recommendation Engine
Implemented in `ai/recommendation_engine.py`, exposed via `/api/ai/recommendations`.

### Recommendation classes
- optimize execution time
- increase parallelism
- tune retries/timeouts
- scale workers
- improve resource allocation

Each recommendation includes `confidence`, `impact_score`, and `priority_score`.

## 7) Learning Feedback Loop (Continuous Learning Pipeline)
The system continuously learns from:
- **Past failures:** failure labels, stage-level error signatures, infra saturation windows.
- **Applied fixes:** which remediation action was selected (retry/scale/rollback/etc.).
- **Execution outcomes:** whether the fix improved SLA, reduced retries, and prevented recurrence.

### Closed-loop lifecycle
1. **Collect:** ingest outcome events after each execution (pre-fix and post-fix snapshots).
2. **Label:** produce training labels (`failed`, `recovered`, `false_alarm`, `action_effective`).
3. **Featureize:** join telemetry + pipeline metadata + selected action into feature store records.
4. **Train:** scheduled retraining jobs refresh anomaly, prediction, and recommendation models.
5. **Evaluate:** compare against production baselines (AUC, precision@k, recovery lift, MTTR delta).
6. **Promote:** register best model version and rollout progressively.
7. **Observe:** capture live drift, regressions, and rollback automatically if quality drops.

This creates a true self-improving pipeline where model quality and remediation policies evolve from real execution evidence.

## 8) AI Service Architecture (FastAPI + Supabase + Celery)

### FastAPI service structure
- `main.py`: app lifecycle, middleware, router registration.
- `api/routes/*`: monitoring, prediction, root-cause, self-healing, recommendations.
- `ai/*`: model logic and feature extraction modules.
- `db/*`: persistence layer and Supabase/Postgres adapters.
- `core/*`: orchestration, caching, execution control.

### Model inference APIs
- `POST /api/ai/anomaly/detect`
- `POST /api/ai/prediction/predict`
- `POST /api/ai/root-cause/analyze`
- `POST /api/ai/self-healing/plan`
- `GET /api/ai/recommendations`

### Training pipeline
- Batch data extraction from Supabase telemetry/executions.
- Feature materialization into feature store.
- Scheduled training jobs (daily/weekly) with offline evaluation.
- Model registry with versioned artifacts + metadata.
- Progressive deployment with canary validation.

### Feature store
- **Offline store:** historical feature tables in Supabase/Postgres (for training).
- **Online store/cache:** Redis for low-latency inference feature reads.
- Shared feature definitions between training and serving to prevent skew.

### Background workers (Celery)
- Async tasks for retraining, backfills, drift checks, and notification fan-out.
- Queue-based remediation workflows (retry orchestration, rollback execution).
- Dead-letter queue + retry policy for resilient background processing.

### Supabase integration
- Use Supabase as source of truth for executions, logs, and user-scoped pipeline config.
- Realtime subscriptions trigger event ingestion for near-real-time AI decisions.
- Row-level security preserved for multi-tenant isolation.
- Model outputs (risk score, root cause, action plan, confidence) written back to Supabase for dashboard and auditability.
