# FlexiRoaster

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-19+-61dafb.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Apertre'26](https://img.shields.io/badge/Apertre'26-Participating-orange.svg)](https://apertre.org)

> Full-stack pipeline orchestration platform with a React dashboard, FastAPI backend, execution engine, and AI insights.

---

## Table of Contents

- [Overview](#overview)
- [Current Architecture](#current-architecture)
- [Technology Stack](#technology-stack)
- [Repository Layout](#repository-layout)
- [End-to-End Workflows](#end-to-end-workflows)
- [API Surface](#api-surface)
- [Database and Persistence](#database-and-persistence)
- [Run Locally](#run-locally)
- [Deployment Strategy](#deployment-strategy)
- [Safety & Production Requirements](#safety--production-requirements)
- [Testing & Quality](#testing--quality)
- [Contributing](#contributing)

---

## Overview

FlexiRoaster combines:

1. **Frontend SPA (`src/`)** for dashboards, pipelines, schedules, logs, alerts, AI insights, and settings.
2. **Backend API (`backend/`)** using FastAPI for pipeline CRUD, execution lifecycle, metrics, and Airflow callbacks.
3. **Pipeline execution core (`backend/core/`)** to parse, validate, and execute staged pipelines.
4. **Persistence layer** split across:
   - SQLAlchemy-backed backend database models (`backend/db/`)
   - Supabase-powered frontend data model (`src/lib/supabase.ts`, `supabase/migrations/`)
5. **AI features (`backend/ai/`)** for predictive insights and recommendations.

---

## Current Architecture

### Runtime Architecture (Text Diagram)

```text
┌──────────────────────────────────────────────────────────────────┐
│                         Frontend (Vite + React)                 │
│  Pages: Dashboard, Pipelines, Executions, Schedules, AI, Logs   │
│  Hooks: usePipelines, useExecutions, useAlerts, useLogs, etc.   │
└──────────────────────────────┬───────────────────────────────────┘
                               │ HTTP / JSON
                    ┌──────────▼──────────┐
                    │     FastAPI API      │
                    │  /api/v1/* + /health │
                    └───────┬──────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
┌────────▼─────────┐ ┌──────▼───────────┐ ┌────▼───────────────────┐
│ Pipeline Routes  │ │ Execution Routes │ │ Metrics / Airflow      │
│ CRUD + validate  │ │ run + monitor    │ │ callbacks + telemetry  │
└────────┬─────────┘ └──────┬───────────┘ └────┬───────────────────┘
         │                  │                  │
         └───────────┬──────┴──────────────┬───┘
                     │                     │
             ┌───────▼────────┐    ┌──────▼────────────┐
             │ Core Engine     │    │ DB / CRUD Layer   │
             │ parse+validate  │    │ SQLAlchemy models │
             │ execute stages  │    │ executions/logs   │
             └─────────────────┘    └───────────────────┘
```

### Product Capability Map

- **Pipeline Management**: Create, update, delete, and validate staged pipelines.
- **Execution Management**: Trigger, monitor, and inspect run outcomes.
- **Scheduling UI**: Configure schedule triggers from frontend experience.
- **AI Insights**: Generate risk, optimization, and anomaly recommendations.
- **Observability**: Metrics, logs, alerts, and health checks.

---

## Technology Stack

### Frontend

- **React 19** + **TypeScript**
- **Vite 7** build tooling
- **Tailwind CSS** styling
- **React Router** routing
- **TanStack Query** data fetching/caching
- **Zustand** local state stores
- **Supabase JS** frontend data/auth integration
- **Recharts** dashboard charts
- **Lucide React** icon set

### Backend

- **FastAPI** (REST API)
- **Uvicorn** (ASGI runtime)
- **Pydantic / pydantic-settings** (configuration and schema validation)
- **SQLAlchemy** (ORM models + DB sessions)
- **PyYAML** (pipeline definition parsing)
- **NumPy / Pandas / Scikit-learn** (AI feature support)
- **Pytest** (backend tests)

### Platform / Infra (as represented in repo)

- **Supabase migrations** for DB evolution (`supabase/migrations/`)
- **Vercel config** for frontend deployment (`vercel.json`)
- **Airflow integration hooks** (`backend/api/routes/airflow.py`, `pipeline/airflow/`)

---

## Repository Layout

```text
Flexi-Roaster/
├── src/                         # React frontend app
│   ├── pages/                   # Route pages (Dashboard, Schedules, etc.)
│   ├── components/              # Shared UI and feature components
│   ├── hooks/                   # Data hooks (pipelines, logs, executions...)
│   ├── lib/                     # API/Supabase clients and helpers
│   ├── store/                   # Zustand stores
│   └── types/                   # TS type definitions
├── backend/                     # FastAPI backend + core engine
│   ├── api/routes/              # REST route modules
│   ├── core/                    # Pipeline engine / executor
│   ├── models/                  # Domain models
│   ├── db/                      # SQLAlchemy models, CRUD, sessions
│   ├── ai/                      # AI predictor + insight logic
│   └── tests/                   # Backend tests
├── supabase/                    # Supabase functions + SQL migrations
├── pipeline/                    # Airflow + sample pipeline integration assets
├── public/                      # Static frontend assets
└── README.md                    # This file
```

---

## End-to-End Workflows

### 1) Pipeline Creation → Validation → Storage

```text
User (UI) -> Frontend Form -> API POST /api/v1/pipelines
          -> FastAPI route builds Pipeline + Stages
          -> Core validator checks schema/dependencies/cycles
          -> Valid pipeline persisted in route storage / DB layer
          -> Response returned to UI list/detail views
```

### 2) Pipeline Execution Workflow

```text
User clicks Execute
  -> Frontend sends execution request
  -> Backend creates execution context
  -> Core executor resolves stage order and runs stage handlers
  -> Logs + status updates emitted during execution
  -> Final execution status/duration persisted
  -> Frontend refreshes execution status and metrics
```

### 3) Schedule Workflow (Frontend Experience)

```text
User creates schedule (type + expression + pipeline)
  -> Schedule stored in frontend state/persistence
  -> Next run time computed (cron/interval)
  -> User can pause/resume or trigger run-now
  -> Schedule card updates last/next run state in UI
```

### 4) AI Insight Workflow

```text
Executions table/history
  -> Aggregate per-pipeline failure + duration statistics
  -> AI predictor generates insights with confidence
  -> API returns recommendations + severity + messages
  -> Frontend AI pages/widgets render prioritized insights
```

### 5) Airflow Callback Workflow

```text
Airflow DAG callback
  -> POST /api/v1/airflow/callback
  -> Backend validates callback secret/payload
  -> Execution status transitioned (running/success/failure/etc.)
  -> Execution logs/context updated
  -> Success response returned to orchestrator
```

---

## API Surface

### Core FastAPI Endpoints

- `GET /health`
- `GET /`
- `POST /api/v1/pipelines`
- `GET /api/v1/pipelines`
- `GET /api/v1/pipelines/{pipeline_id}`
- `PUT /api/v1/pipelines/{pipeline_id}`
- `DELETE /api/v1/pipelines/{pipeline_id}`
- `POST /api/v1/executions`
- `GET /api/v1/executions`
- `GET /api/v1/executions/{execution_id}`
- `POST /api/v1/executions/{execution_id}/cancel`
- `GET /api/v1/metrics/system`
- `GET /api/v1/metrics/pipelines/{pipeline_id}`
- Airflow integration endpoints under `/api/v1/airflow/*`

> See `backend/API_TESTING.md` for concrete request/response examples.

---

## Database and Persistence

This repo currently demonstrates **two persistence planes**:

1. **Backend SQLAlchemy models** (`backend/db/models.py`)
   - `PipelineDB`
   - `ExecutionDB`
   - `StageExecutionDB`
   - `LogDB`
   - `MetricDB`

2. **Supabase schema & generated TS types**
   - SQL migrations in `supabase/migrations/`
   - Typed frontend contracts in `src/types/database.ts`

### Persistence Strategy Notes

- Frontend and backend can be run independently for development.
- Production deployments should align on a single source of truth for execution and schedule state.
- Keep schema migrations versioned and backward compatible.

---

## Run Locally

### Prerequisites

- Node.js 20+
- npm 10+
- Python 3.8+

### Frontend

```bash
npm install
npm run dev
```

Build production bundle:

```bash
npm run build
npm run preview
```

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m backend.main
```

or:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Optional Supabase Setup

- Apply SQL in `supabase/migrations/`
- Configure frontend env variables for Supabase URL/key
- See `SUPABASE_SETUP.md`

---

## Deployment Strategy

### Recommended Path

1. **Frontend**: Vite build deployed via Vercel/static hosting.
2. **Backend**: Containerized FastAPI app behind reverse proxy.
3. **Database**: Managed Postgres + backups + migration pipeline.
4. **Workers/Orchestration**: Split execution workers from API for scale.
5. **Observability**: Central logs + metrics dashboards + alerting.

### Environment Promotion

- `dev` → `staging` → `production`
- Promote with immutable build artifacts and schema migration gates.
- Use smoke tests and rollback plans per release.

---

## Safety & Production Requirements

A complete production safety blueprint is available in:

- [`SAFETY_PRODUCTION_REQUIREMENTS.md`](SAFETY_PRODUCTION_REQUIREMENTS.md)

It includes:

- Confidence threshold policy design
- Human override flow
- Audit log architecture
- Explainability requirements
- Failure recovery strategy
- Architecture/service/API/schema/model/deployment sections

---

## Testing & Quality

### Frontend

```bash
npm run lint
npm run build
```

### Backend

```bash
cd backend
pytest
```

### API Manual Validation

Use examples in:

- `backend/API_TESTING.md`

---

## Contributing

- Read [CONTRIBUTING.md](CONTRIBUTING.md)
- Prefer small, focused PRs
- Include validation steps in your PR description
- Keep docs in sync when adding routes, schemas, or workflows

---

## License

MIT License.
