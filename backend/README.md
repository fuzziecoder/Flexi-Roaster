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

## Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp backend/.env.example backend/.env
```

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
