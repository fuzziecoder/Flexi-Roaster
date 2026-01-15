# FlexiRoaster Pipeline Automation System

A production-ready pipeline automation system built with:

- **Apache Airflow** - Orchestration & scheduling
- **FastAPI** - Pipeline execution engine
- **Redis** - State management, locks, caching
- **PostgreSQL** - Persistence
- **AI Safety Module** - Failure prediction & anomaly handling

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Apache Airflow                          │
│         (DAGs, Scheduling, Retries, Monitoring)             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌─────────────┐  ┌────────────────┐  ┌─────────────────┐   │
│  │  Pipeline   │  │   AI Safety    │  │  Redis State    │   │
│  │  Executor   │  │    Engine      │  │    Manager      │   │
│  └─────────────┘  └────────────────┘  └─────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌─────────┐    ┌──────────┐    ┌──────────┐
    │ Redis   │    │PostgreSQL│    │  Logs    │
    │ Cache   │    │   DB     │    │ Metrics  │
    └─────────┘    └──────────┘    └──────────┘
```

## Features

### Pipeline Orchestration
- DAG-based workflow management
- Stage dependencies and ordering
- Automatic retries with exponential backoff
- Timeout handling per stage

### AI Safety Module
- **Pre-execution Risk Assessment**: Predicts failure probability
- **Runtime Anomaly Detection**: Detects time spikes and error bursts
- **Safe Action Selection**: Chooses safest action (retry → skip → pause → rollback → terminate)
- **Explainable AI**: All decisions include explanations

### State Management (Redis)
- Distributed execution locks
- Duplicate run prevention
- Stage retry counters
- Heartbeat monitoring
- Execution state caching
- Automatic fallback to DB if Redis unavailable

### Execution States
- `pending` - Waiting to start
- `running` - Currently executing
- `paused` - Temporarily paused
- `completed` - Successfully finished
- `failed` - Execution failed
- `rolled_back` - Rolled back after failure
- `cancelled` - Manually cancelled

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### 1. Clone and Setup

```bash
cd pipeline
cp .env.example .env
cp backend/.env.example backend/.env
```

### 2. Start All Services

```bash
# Create Airflow directories with correct permissions
mkdir -p airflow/logs airflow/plugins
chmod -R 777 airflow

# Start services
docker-compose up -d
```

### 3. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Airflow UI | http://localhost:8080 | admin / admin |
| FastAPI Docs | http://localhost:8000/api/docs | - |
| PostgreSQL | localhost:5432 | airflow / airflow |
| Redis | localhost:6379 | - |

### 4. Create Your First Pipeline

```bash
curl -X POST http://localhost:8000/api/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Pipeline",
    "description": "A simple data pipeline",
    "stages": [
      {
        "id": "load-data",
        "name": "Load Data",
        "type": "input",
        "config": {"source": "api"},
        "dependencies": []
      },
      {
        "id": "transform",
        "name": "Transform Data",
        "type": "transform",
        "config": {"operation": "normalize"},
        "dependencies": ["load-data"]
      },
      {
        "id": "save-data",
        "name": "Save Results",
        "type": "output",
        "config": {"destination": "database"},
        "dependencies": ["transform"]
      }
    ]
  }'
```

### 5. Execute the Pipeline

```bash
# Via API
curl -X POST http://localhost:8000/api/executions/pipeline-xxx/execute

# Or via Airflow
# Go to Airflow UI and trigger the flexiroaster_pipeline DAG
```

## API Reference

### Pipelines

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/pipelines` | Create pipeline |
| GET | `/api/pipelines` | List pipelines |
| GET | `/api/pipelines/{id}` | Get pipeline details |
| PUT | `/api/pipelines/{id}` | Update pipeline |
| DELETE | `/api/pipelines/{id}` | Delete pipeline |

### Executions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/executions` | Start execution |
| POST | `/api/executions/{pipeline_id}/execute` | Execute specific pipeline |
| GET | `/api/executions` | List executions |
| GET | `/api/executions/{id}` | Get execution details |
| POST | `/api/executions/{id}/stop` | Stop execution |
| POST | `/api/executions/{id}/pause` | Pause execution |
| POST | `/api/executions/{id}/resume` | Resume execution |
| GET | `/api/executions/{id}/logs` | Get execution logs |

### Health & Metrics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/metrics` | Dashboard metrics |
| GET | `/insights` | AI insights |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | - | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `EXECUTOR_MAX_RETRIES` | `3` | Max retries per stage |
| `EXECUTOR_STAGE_TIMEOUT` | `120` | Stage timeout in seconds |
| `AI_BLOCK_HIGH_RISK` | `false` | Block high-risk executions |
| `AI_RISK_THRESHOLD_HIGH` | `0.7` | High risk threshold |

### Airflow Variables

Set in Airflow UI or via `airflow variables set`:

| Variable | Description |
|----------|-------------|
| `flexiroaster_backend_url` | Backend API URL |
| `flexiroaster_pipeline_id` | Default pipeline to execute |
| `flexiroaster_schedule` | Cron schedule |

## Project Structure

```
pipeline/
├── docker-compose.yml       # Docker services config
├── .env.example             # Environment template
├── airflow/
│   ├── dags/
│   │   └── flexiroaster_pipeline_dag.py
│   ├── logs/
│   └── plugins/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── api/
│   │   ├── schemas.py       # Pydantic models
│   │   └── routes/
│   │       ├── pipelines.py
│   │       ├── executions.py
│   │       └── health.py
│   ├── core/
│   │   ├── executor.py      # Pipeline executor
│   │   └── redis_state.py   # Redis state manager
│   ├── ai/
│   │   └── safety_engine.py # AI safety module
│   └── db/
│       ├── models.py        # SQLAlchemy models
│       ├── database.py      # DB connection
│       └── crud.py          # CRUD operations
└── init-db/
    └── 01-create-databases.sql
```

## Design Principles

### Separation of Concerns

| Component | Responsibility |
|-----------|----------------|
| **Airflow** | Scheduling, retries, dependencies |
| **FastAPI** | Business logic, execution, AI safety |
| **Redis** | Locks, caching, real-time state |
| **PostgreSQL** | History, definitions, logs |

### Fail-Safe Design

1. **Redis unavailable** → Falls back to database locks
2. **Stage fails** → AI determines safest action
3. **Execution timeout** → Graceful shutdown and cleanup
4. **High risk detected** → Can block or warn before execution

## AI Safety Module

### Risk Assessment Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| Historical failure rate | 30% | Past failure percentage |
| Recent failures | 25% | Failures in last 7 days |
| Consecutive failures | 15% | Streak of failures |
| Duration anomaly | 10% | Unusually long executions |
| Stage complexity | 10% | Number of stages |
| Time since success | 10% | Days since last success |

### Safe Actions (Priority Order)

1. **Continue** - No action needed
2. **Retry Stage** - Retry the failed stage
3. **Skip Stage** - Skip non-critical stage
4. **Pause Pipeline** - Wait for manual intervention
5. **Rollback** - Undo completed stages
6. **Terminate** - Stop immediately

## Monitoring

### Logs
- Structured JSON logging
- Per-stage log entries
- Traceback on errors

### Metrics
- Execution duration by stage
- Stage success/failure rates
- AI risk scores over time

### Health Checks
- Database connectivity
- Redis availability
- Active execution count

## Development

### Running Locally (Without Docker)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql+psycopg2://user:pass@localhost/flexiroaster
export REDIS_URL=redis://localhost:6379/0

# Run the server
python main.py
```

### Running Tests

```bash
cd backend
pytest tests/ -v
```

## License

MIT License
