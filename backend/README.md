# FlexiRoaster Backend

Python backend for FlexiRoaster pipeline automation platform.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt
```

## CLI Usage

### Execute a pipeline
```bash
python -m backend.cli execute --pipeline backend/examples/sample_pipeline.yaml
```

### Validate a pipeline
```bash
python -m backend.cli validate --pipeline backend/examples/sample_pipeline.yaml
```

### List loaded pipelines
```bash
python -m backend.cli list
```

## Project Structure

```
backend/
├── core/           # Core pipeline engine
├── models/         # Pydantic models
├── db/             # Database layer
├── api/            # FastAPI routes
├── ai/             # AI/ML features
├── examples/       # Sample pipelines
└── cli.py          # CLI tool
```

## Pipeline Definition

Pipelines are defined in YAML or JSON format:

```yaml
name: "My Pipeline"
description: "Pipeline description"
version: "1.0"

stages:
  - id: "stage1"
    name: "Stage Name"
    type: "input"  # input, transform, output
    config:
      key: "value"
    dependencies: []
```

## Stage Types

- **input**: Read data from source
- **transform**: Process/transform data
- **output**: Write data to destination
