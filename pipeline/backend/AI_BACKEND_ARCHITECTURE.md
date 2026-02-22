# FlexiRoaster AI Backend Architecture (Self-Healing Pipelines)

## 1) Pipeline Monitoring Engine
- Inputs: Supabase execution rows, execution logs, metrics stream.
- Output: rolling per-pipeline snapshot (`duration`, `failures`, `retries`, `cpu/memory`, `throughput`, `latency`, error patterns).
- API:
  - `POST /api/monitoring/ingest`
  - `GET /api/monitoring/{pipeline_id}/snapshot`

## 2) Anomaly Detection System
Implemented in `ai/anomaly_detection.py`.

### Targets
- unusual execution time
- abnormal data volume
- sudden failure spikes
- abnormal resource usage
- log pattern anomalies

### Algorithms
- **Isolation Forest** for unsupervised multivariate outlier detection.
- **Statistical methods** (z-score against baseline mean/std; threshold rules).
- **Pattern scoring** for log anomaly intensity from unique error signatures.

### Feature extraction
- `execution_time_s`, `data_volume_mb`, `failure_count_1h`, `cpu_percent`, `memory_percent`, `retry_count`, `error_pattern_score`.

### Training flow
1. Build historical telemetry dataset.
2. Normalize feature vectors.
3. Fit baseline stats (mean/std) for statistical checks.
4. Train Isolation Forest.
5. Version model + metadata.

### Online inference
1. Runtime payload to `/api/ai/anomaly/detect`.
2. Compute feature vector.
3. Combine Isolation Forest prediction + z-score/rules.
4. Return anomaly decision with score + reasons.

## 3) Failure Prediction Engine
Implemented in `ai/failure_prediction.py`.

### Predictions
- pipeline failure probability
- execution success probability
- stage-level risk scores

### Inputs
- historical outcomes (`failed` labels)
- recent error count / retry frequency
- pipeline config (`stage_count`, `critical_stage_count`)
- system load (`avg_cpu_percent`, `avg_memory_percent`)

### Model design
- **Primary**: Gradient Boosting Classifier.
- **Fallback**: heuristic weighted risk model if ML model/artifact unavailable.
- **Stage risk**: combines pipeline risk + stage retries + stage failure history + criticality.

### Training strategy
- time-split train/validation
- evaluate ROC-AUC, precision for failure-alert class, calibration
- progressive deployment: shadow -> canary -> full rollout

## 4) Root Cause Analysis Engine
Implemented in `ai/root_cause_engine.py`, exposed via `/api/ai/root-cause/analyze`.

### Detectable causes
- failing stage
- connection issues
- resource bottlenecks
- data inconsistencies
- configuration errors

### Fusion logic (logs + metrics + history)
- **Logs**: keyword/signal extraction for timeout, schema, permission/config, connectivity classes.
- **Metrics**: high CPU/memory and latency spikes as resource/network evidence.
- **History**: recurring stage failures, recent deployments, prior incident patterns.
- Final decision = strongest cause evidence + contributing factors + confidence score.

## 5) Self-Healing Engine (Automatic Fixes)
Implemented in `ai/self_healing_engine.py`, exposed via `/api/ai/self-healing/plan`.

### Safe automatic actions
- retry failed stage
- restart worker
- increase timeout
- scale resources
- switch fallback service
- parallelize pipeline stages (safe mode)

### Decision rules
- Start with lowest-risk action (retry).
- Branch by primary cause:
  - connection -> restart worker + fallback service
  - resource bottleneck -> scale + timeout increase
  - data inconsistency -> conservative timeout/guarded re-run
  - config error -> known-good config fallback
- Parallelization allowed only for low/medium risk and marked parallelizable workloads.

### Risk thresholds
- low `<0.6`
- medium `0.6-<0.8`
- high `>=0.8`

### Rollback strategy
- restore previous timeout/resource config snapshot
- restore baseline worker pool
- revert service routing to primary

### Human approval mode
- enabled explicitly (`human_approval_mode=true`) or forced when risk is high.

## 6) Recommendation Engine
Implemented in `ai/recommendation_engine.py`, exposed via `/api/ai/recommendations`.

### Recommendation types
- optimize execution time
- enable parallel stages
- scale workers
- update configuration
- improve resource allocation

### Scoring and confidence
Each recommendation returns:
- `confidence` (0-1)
- `impact_score` (0-100)
- `priority_score = confidence * impact_score`

This enables deterministic ranking for dashboard + automation policy decisions.
