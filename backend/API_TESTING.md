# FlexiRoaster API Testing

## Start the API Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python backend/main.py

# Or with uvicorn directly
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at: http://127.0.0.1:8000

## API Documentation

- **Swagger UI**: http://127.0.0.1:8000/api/docs
- **ReDoc**: http://127.0.0.1:8000/api/redoc

## Test Endpoints

### 1. Create a Pipeline

```bash
curl -X POST http://127.0.0.1:8000/api/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Pipeline",
    "description": "A test pipeline",
    "version": "1.0",
    "stages": [
      {
        "id": "input",
        "name": "Read Data",
        "type": "input",
        "config": {"source": "test.csv"},
        "dependencies": []
      },
      {
        "id": "process",
        "name": "Process Data",
        "type": "transform",
        "config": {"operation": "validate"},
        "dependencies": ["input"]
      },
      {
        "id": "output",
        "name": "Write Data",
        "type": "output",
        "config": {"destination": "output.csv"},
        "dependencies": ["process"]
      }
    ],
    "variables": {}
  }'
```

### 2. List Pipelines

```bash
curl http://127.0.0.1:8000/api/pipelines
```

### 3. Execute a Pipeline

```bash
# Replace {pipeline_id} with actual ID from create response
curl -X POST http://127.0.0.1:8000/api/executions \
  -H "Content-Type: application/json" \
  -d '{
    "pipeline_id": "{pipeline_id}"
  }'
```

### 4. Get Execution Status

```bash
# Replace {execution_id} with actual ID from execute response
curl http://127.0.0.1:8000/api/executions/{execution_id}
```

### 5. Get Execution Logs

```bash
curl http://127.0.0.1:8000/api/executions/{execution_id}/logs
```

### 6. Get Metrics

```bash
curl http://127.0.0.1:8000/api/metrics
```

### 7. Get Metrics History

```bash
curl http://127.0.0.1:8000/api/metrics/history?hours=24
```

## Available Endpoints

### Pipelines
- `POST /api/pipelines` - Create pipeline
- `GET /api/pipelines` - List pipelines
- `GET /api/pipelines/{id}` - Get pipeline
- `PUT /api/pipelines/{id}` - Update pipeline
- `DELETE /api/pipelines/{id}` - Delete pipeline
- `POST /api/pipelines/{id}/validate` - Validate pipeline

### Executions
- `POST /api/executions` - Start execution
- `GET /api/executions` - List executions
- `GET /api/executions/{id}` - Get execution status
- `GET /api/executions/{id}/logs` - Get execution logs

### Metrics
- `GET /api/metrics` - Current metrics
- `GET /api/metrics/history` - Historical metrics

## Response Examples

### Pipeline Response
```json
{
  "id": "pipe-abc123",
  "name": "Test Pipeline",
  "description": "A test pipeline",
  "version": "1.0",
  "stages": [...],
  "variables": {}
}
```

### Execution Response
```json
{
  "id": "exec-xyz789",
  "pipeline_id": "pipe-abc123",
  "pipeline_name": "Test Pipeline",
  "status": "running",
  "started_at": "2024-01-10T10:00:00Z",
  "completed_at": null,
  "duration": null,
  "stage_executions": [],
  "error": null
}
```

### Metrics Response
```json
{
  "cpu": 67.5,
  "memory": 54.2,
  "throughput": 12.5,
  "active_executions": 3,
  "total_pipelines": 5,
  "success_rate": 95.5,
  "failure_rate": 4.5,
  "avg_duration": 45.3,
  "timestamp": "2024-01-10T10:00:00Z"
}
```
