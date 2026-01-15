#!/usr/bin/env python3
"""
Example script demonstrating FlexiRoaster Pipeline API usage.
Run this after starting the services to create sample pipelines.
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api"


def pretty_print(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2, default=str))


def create_sample_pipeline():
    """Create a sample data processing pipeline"""
    print("\n" + "="*60)
    print("Creating Sample Pipeline")
    print("="*60)
    
    pipeline = {
        "name": "Sample Data Processing Pipeline",
        "description": "Demonstrates a complete ETL workflow with multiple stages",
        "version": "1.0.0",
        "stages": [
            {
                "id": "extract",
                "name": "Extract Data",
                "type": "input",
                "description": "Load data from source",
                "config": {
                    "source": "api",
                    "endpoint": "/data/users",
                    "data": [
                        {"id": 1, "name": "Alice", "age": 30},
                        {"id": 2, "name": "Bob", "age": 25},
                        {"id": 3, "name": "Charlie", "age": 35}
                    ]
                },
                "dependencies": [],
                "timeout": 60,
                "max_retries": 3,
                "is_critical": True
            },
            {
                "id": "validate",
                "name": "Validate Data",
                "type": "validation",
                "description": "Validate data against schema",
                "config": {
                    "schema": {
                        "id": "integer",
                        "name": "string",
                        "age": "integer"
                    }
                },
                "dependencies": ["extract"],
                "timeout": 30,
                "max_retries": 2,
                "is_critical": True
            },
            {
                "id": "transform",
                "name": "Transform Data",
                "type": "transform",
                "description": "Apply transformations",
                "config": {
                    "operation": "normalize",
                    "fields": ["name", "age"]
                },
                "dependencies": ["validate"],
                "timeout": 120,
                "max_retries": 3,
                "is_critical": True
            },
            {
                "id": "load",
                "name": "Load to Database",
                "type": "output",
                "description": "Save processed data",
                "config": {
                    "destination": "database",
                    "table": "processed_users"
                },
                "dependencies": ["transform"],
                "timeout": 60,
                "max_retries": 3,
                "is_critical": True
            }
        ],
        "config": {
            "notify_on_completion": True,
            "notify_on_failure": True
        }
    }
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/pipelines",
        json=pipeline
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✓ Created pipeline: {result['id']}")
        pretty_print(result)
        return result['id']
    else:
        print(f"✗ Failed to create pipeline: {response.status_code}")
        print(response.text)
        return None


def list_pipelines():
    """List all pipelines"""
    print("\n" + "="*60)
    print("Listing All Pipelines")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}{API_PREFIX}/pipelines")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Found {result['total']} pipeline(s)")
        for p in result['pipelines']:
            print(f"  - {p['id']}: {p['name']} (active: {p['is_active']}, stages: {p['stage_count']})")
        return result
    else:
        print(f"✗ Failed to list pipelines: {response.status_code}")
        return None


def execute_pipeline(pipeline_id):
    """Execute a pipeline"""
    print("\n" + "="*60)
    print(f"Executing Pipeline: {pipeline_id}")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/executions/{pipeline_id}/execute",
        params={"triggered_by": "example_script"}
    )
    
    if response.status_code == 202:
        result = response.json()
        print(f"✓ Execution started")
        pretty_print(result)
        return result
    else:
        print(f"✗ Failed to execute pipeline: {response.status_code}")
        print(response.text)
        return None


def get_execution_status(execution_id):
    """Get execution status"""
    print("\n" + "="*60)
    print(f"Execution Status: {execution_id}")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}{API_PREFIX}/executions/{execution_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result['status']}")
        print(f"Progress: {result['progress']}%")
        print(f"Completed Stages: {result['completed_stages']}/{result['total_stages']}")
        if result.get('error'):
            print(f"Error: {result['error']}")
        return result
    else:
        print(f"✗ Failed to get execution: {response.status_code}")
        return None


def check_health():
    """Check service health"""
    print("\n" + "="*60)
    print("Service Health Check")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result['status']}")
        print(f"App: {result['app']} v{result['version']}")
        for service, health in result.get('services', {}).items():
            print(f"  - {service}: {health['status']}")
        return result
    else:
        print(f"✗ Health check failed: {response.status_code}")
        return None


def get_metrics():
    """Get dashboard metrics"""
    print("\n" + "="*60)
    print("Dashboard Metrics")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/metrics")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total Pipelines: {result['total_pipelines']}")
        print(f"Active Pipelines: {result['active_pipelines']}")
        print(f"Total Executions: {result['total_executions']}")
        print(f"Success Rate: {result['success_rate']}%")
        print(f"Avg Duration: {result['avg_duration']}s")
        return result
    else:
        print(f"✗ Failed to get metrics: {response.status_code}")
        return None


def get_insights():
    """Get AI insights"""
    print("\n" + "="*60)
    print("AI Insights")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/insights")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Found {result['total']} insight(s)")
        for i in result['insights']:
            print(f"  [{i['severity'].upper()}] {i['title']}")
            print(f"    {i['message']}")
            if i.get('recommendation'):
                print(f"    → {i['recommendation']}")
        return result
    else:
        print(f"✗ Failed to get insights: {response.status_code}")
        return None


def main():
    """Main demo function"""
    print("\n" + "#"*60)
    print("# FlexiRoaster Pipeline Automation Demo")
    print("#"*60)
    
    # Check health first
    health = check_health()
    if not health or health['status'] != 'healthy':
        print("\n⚠ Backend is not healthy. Please start the services first.")
        print("Run: docker-compose up -d")
        return
    
    # Create a sample pipeline
    pipeline_id = create_sample_pipeline()
    if not pipeline_id:
        return
    
    # List all pipelines
    list_pipelines()
    
    # Execute the pipeline
    execution = execute_pipeline(pipeline_id)
    
    # Wait a bit and check status
    if execution and execution.get('success'):
        print("\nWaiting for execution to complete...")
        time.sleep(3)
        # Note: In async mode, we can't get execution_id from the response
        # You would need to list executions to get the ID
    
    # Get metrics
    get_metrics()
    
    # Get insights
    get_insights()
    
    print("\n" + "#"*60)
    print("# Demo Complete!")
    print("#"*60)
    print("\nNext steps:")
    print("  1. Open API docs: http://localhost:8000/api/docs")
    print("  2. Open Airflow UI: http://localhost:8080")
    print("  3. Trigger DAGs via Airflow for scheduled execution")


if __name__ == "__main__":
    main()
