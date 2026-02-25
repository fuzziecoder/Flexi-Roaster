# FlexiRoaster Backend - Quick Start

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Install Dependencies

```bash
pip install -r backend/requirements.txt
```

## Running the Backend

### Core API Layer

- **FastAPI** - High-performance Python API framework
- **Uvicorn** - ASGI server for FastAPI
- **Gunicorn** - Production process manager
- **NGINX** - Reverse proxy, load balancing, and rate limiting

### Optional Alternative

- **Django** - Use when a full admin experience and enterprise-grade auth system are required

### Option 1: CLI Testing (Phase 1)

Test pipeline execution from command line:

```bash
# Execute sample pipeline
python -m backend.cli execute --pipeline backend/examples/sample.yaml --verbose

# List available examples
python -m backend.cli list-examples
```

### Option 2: API Server (Phase 2)

Start the FastAPI server:

```bash
# Development mode (with auto-reload)
python -m backend.main

# Or using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs
- **Health**: http://localhost:8000/health

## API Endpoints

### Pipelines
- `POST /api/pipelines` - Create pipeline
- `GET /api/pipelines` - List pipelines
- `GET /api/pipelines/{id}` - Get pipeline
- `PUT /api/pipelines/{id}` - Update pipeline
- `DELETE /api/pipelines/{id}` - Delete pipeline

### Executions
- `POST /api/executions` - Start execution
- `GET /api/executions` - List executions
- `GET /api/executions/{id}` - Get execution details
- `GET /api/executions/{id}/logs` - Get logs
- `DELETE /api/executions/{id}` - Cancel execution

### Metrics
- `GET /api/metrics` - Current metrics
- `GET /api/metrics/history` - Historical data

## Example Usage

### Create a Pipeline

```bash
curl -X POST http://localhost:8000/api/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-pipeline",
    "description": "Test pipeline",
    "stages": [
      {
        "name": "Input Stage",
        "type": "input",
        "config": {"source": "test.csv"}
      }
    ]
  }'
```

### Execute a Pipeline

```bash
curl -X POST http://localhost:8000/api/executions \
  -H "Content-Type: application/json" \
  -d '{"pipeline_id": "your-pipeline-id"}'
```


## Authentication & Security

- JWT authentication endpoint: `POST /api/auth/token`
- RBAC roles: `admin`, `operator`, `viewer`
- Rate limiting: IP-based sliding window using `RATE_LIMIT_PER_MINUTE`
- Secret management abstraction via `SECRET_BACKEND` (`env` or `vault`)
- Optional enterprise IAM metadata endpoint for Keycloak: `GET /api/auth/oidc/keycloak/config`

Example token request:

```bash
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Use token:

```bash
curl http://localhost:8000/api/pipelines \
  -H "Authorization: Bearer <access_token>"
```

## Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp backend/.env.example backend/.env
```

## Event-Driven Architecture (Advanced Setup)

FlexiRoaster supports Kafka-compatible domain events (Apache Kafka or Redpanda) for loose coupling, high scalability, audit-friendly workflows, and real-time analytics.


#### Apache Kafka
- Event-driven triggers
- High-throughput ingestion
- Real-time pipeline activation

#### Redpanda
- Kafka-compatible
- Lower operational complexity

Use this layer when:
- Pipelines should trigger from events
- You need real-time monitoring
- You process millions of records

### Published topics
- `pipeline.created`
- `execution.started`
- `execution.failed`
- `execution.completed`

### Enable streaming publishing
Set the following environment variables in `backend/.env`:

```env
ENABLE_EVENT_STREAMING=true
EVENT_STREAM_BACKEND=kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CLIENT_ID=flexiroaster-backend
TOPIC_PIPELINE_CREATED=pipeline.created
TOPIC_EXECUTION_STARTED=execution.started
TOPIC_EXECUTION_FAILED=execution.failed
TOPIC_EXECUTION_COMPLETED=execution.completed
```

If Kafka/Redpanda is unavailable, the backend falls back to structured application logs for events so local development continues to work.

## Next Steps

1. Install Python and dependencies
2. Test CLI execution
3. Start API server
4. Test endpoints with Postman or curl
5. Integrate with frontend (already running on port 5173)

## Documentation

- Full implementation plan: `implementation_plan.md`
- Task checklist: `task.md`
- Walkthrough: `walkthrough.md`
