# Safety & Production Requirements Blueprint

## Architecture Diagram (Text)

```text
┌──────────────────────┐
│   Web UI (React)     │
│ Schedules, Pipelines │
└──────────┬───────────┘
           │ HTTPS
┌──────────▼───────────┐
│ API Gateway / BFF    │
│ AuthN/AuthZ + RBAC   │
└──────┬───────┬───────┘
       │       │
       │       ├──────────────────────────────────┐
       │                                          │
┌──────▼────────────┐                     ┌───────▼──────────────┐
│ Pipeline Service  │                     │ AI Decision Service   │
│ CRUD + Scheduling │                     │ scoring + policy eval │
└──────┬────────────┘                     └───────┬──────────────┘
       │                                          │
┌──────▼───────────┐                      ┌───────▼──────────────┐
│ Scheduler Worker │                      │ Explainability Engine │
│ cron/interval    │                      │ reasons + feature imp │
└──────┬───────────┘                      └───────┬──────────────┘
       │                                          │
┌──────▼────────────┐                    ┌────────▼──────────────┐
│ Execution Queue   │                    │ Audit Log Service      │
│ retry + DLQ       │                    │ immutable trace        │
└──────┬────────────┘                    └────────┬──────────────┘
       │                                          │
┌──────▼────────────┐                    ┌────────▼──────────────┐
│ PostgreSQL        │                    │ Object Store / SIEM    │
│ pipelines/schedules│                   │ long-term logs         │
└───────────────────┘                    └────────────────────────┘
```

## Service Components

- **Frontend UI**: Pipeline and schedule management, confidence display, human approval inbox.
- **Auth Service**: SSO, RBAC, scoped API tokens.
- **Pipeline Service**: Pipeline + schedule CRUD, trigger orchestration.
- **Scheduler Service**: Cron/interval/event evaluation with timezone awareness.
- **AI Decision Service**: Model inference, threshold checks, fallback routing.
- **Policy Service**: Confidence thresholds and human-override policy evaluation.
- **Audit Service**: Immutable event logging for all user/system/model actions.
- **Recovery Worker**: Retry engine, dead-letter queue processing, replay tooling.

## API Endpoints

- `POST /api/v1/pipelines` – create pipeline
- `GET /api/v1/pipelines` – list pipelines
- `PATCH /api/v1/pipelines/{id}` – update pipeline
- `POST /api/v1/schedules` – create schedule
- `GET /api/v1/schedules` – list schedules
- `PATCH /api/v1/schedules/{id}` – pause/resume/update
- `POST /api/v1/schedules/{id}/run` – trigger immediate run
- `POST /api/v1/ai/evaluate` – score request and return confidence + explanation
- `POST /api/v1/approvals` – create human-approval request
- `PATCH /api/v1/approvals/{id}` – approve/reject override
- `GET /api/v1/audit-logs` – retrieve filtered audit timeline
- `POST /api/v1/recovery/replay` – replay failed jobs from DLQ

## Database Schema (Core)

- `pipelines(id, name, owner_id, config_json, is_active, created_at, updated_at)`
- `schedules(id, pipeline_id, type, expression, timezone, is_active, last_run_at, next_run_at, created_by, created_at)`
- `executions(id, pipeline_id, schedule_id, status, started_at, finished_at, error_code, error_message)`
- `ai_decisions(id, execution_id, model_version, confidence, threshold, decision, explanation_json, created_at)`
- `approvals(id, execution_id, required_role, status, reviewer_id, reviewer_notes, created_at, decided_at)`
- `audit_logs(id, actor_type, actor_id, action, resource_type, resource_id, before_json, after_json, trace_id, created_at)`
- `recovery_events(id, execution_id, strategy, retry_count, dlq_reason, replayed_at, outcome)`

## Model Pipeline

1. **Input validation** (schema + PII checks)
2. **Feature extraction**
3. **Inference**
4. **Confidence calibration** (e.g., temperature scaling)
5. **Policy gate**:
   - confidence >= high threshold -> auto-allow
   - between medium/high -> human review required
   - below medium -> block/fallback
6. **Explanation generation** (top contributing features + reason code)
7. **Audit write** (inputs hash, model version, decision, reviewer if any)

## Safety Requirements

- **Confidence thresholds**: configurable by pipeline and environment (`dev`, `staging`, `prod`).
- **Human override**: mandatory approval path for low/ambiguous confidence decisions.
- **Audit logs**: immutable, append-only, traceable by `trace_id`.
- **Explainability**: return reason codes and feature-level contribution summary.
- **Failure recovery**: retries with backoff + DLQ + replay tooling with approvals.

## Deployment Strategy

- Use **blue/green** or **canary** deployment for API and model-serving workloads.
- Keep model artifacts versioned and promote with staged validation gates.
- Use managed Postgres + automated backups + PITR.
- Separate worker pools for scheduler, inference, and replay tasks.
- Enforce infra-as-code, policy-as-code, and environment parity.

## Production Best Practices

- Strict RBAC + least privilege on all services.
- Idempotent schedule triggers and execution APIs.
- End-to-end tracing (OpenTelemetry) across UI/API/workers.
- SLA/SLO dashboards for latency, failure rate, and approval turnaround.
- Alerting on threshold drifts, spike in overrides, and DLQ growth.
- Chaos drills for scheduler outage and model-service degradation.
- Periodic model bias and drift reviews with rollback playbooks.
