# FlexiRoaster

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> An intelligent, full-stack pipeline automation framework with AI-powered optimization and real-time monitoring

FlexiRoaster is a production-grade automation engine combining a **Python backend** for pipeline execution with a **React dashboard** for visualization and control. Built for reliability, observability, and continuous optimization.

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + TypeScript)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Dashboard   │  │   Pipeline   │  │   Monitoring │        │
│  │    UI        │  │    Builder   │  │    Charts    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│         Tailwind CSS + shadcn/ui + Recharts                    │
└────────────────────────────▲───────────────────────────────────┘
                             │
                   REST API + WebSocket
                             │
┌────────────────────────────┴───────────────────────────────────┐
│                   BACKEND (Python + FastAPI)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   REST API   │  │  WebSocket   │  │     Auth     │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└────────────────────────────▲───────────────────────────────────┘
                             │
┌────────────────────────────┴───────────────────────────────────┐
│              PIPELINE ENGINE (Python Core)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Pipeline  │  │  Stage   │  │   AI     │  │  State   │      │
│  │Executor  │  │ Manager  │  │  Layer   │  │ Manager  │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└────────────────────────────▲───────────────────────────────────┘
                             │
┌────────────────────────────┴───────────────────────────────────┐
│              DATA LAYER (Storage & Queues)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │PostgreSQL│  │  Redis   │  │RabbitMQ  │  │    S3    │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└────────────────────────────────────────────────────────────────┘
```

## 📑 Table of Contents

- [Why Both Frontend and Backend?](#-why-both-frontend-and-backend)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Backend Implementation](#-backend-implementation)
- [Frontend Implementation](#-frontend-implementation)
- [Complete Examples](#-complete-examples)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

## 🤔 Why Both Frontend and Backend?

### **Frontend (React)** - Visualization & Interaction
✅ Real-time dashboard with metrics and charts  
✅ Pipeline status monitoring  
✅ User interactions and controls  
✅ Activity logs and alerts  
✅ Visual pipeline builder  

**BUT** - Frontend cannot:
❌ Execute pipelines  
❌ Run AI models  
❌ Process data  
❌ Manage state persistence  

### **Backend (Python)** - Core Engine
✅ Pipeline execution engine  
✅ AI/ML model inference  
✅ Data processing and validation  
✅ Real-time event streaming  
✅ State management and persistence  

**This separation ensures:**
- ✨ Scalability
- 🔒 Security
- 🎯 Clean architecture
- 📊 Better performance

## 🛠️ Technology Stack

### Backend Stack (Required)

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|----------|
| **Runtime** | Python | 3.8+ | Core execution |
| **API Framework** | FastAPI | 0.104+ | REST + WebSocket |
| **Async** | asyncio | Built-in | Async execution |
| **Task Queue** | Celery | 5.3+ | Background jobs |
| **Message Broker** | RabbitMQ/Redis | Latest | Task distribution |
| **Database** | PostgreSQL | 14+ | Data persistence |
| **Cache** | Redis | 7.0+ | Caching & sessions |
| **ML Framework** | scikit-learn | 1.3+ | AI models |
| **Validation** | Pydantic | 2.0+ | Data validation |

### Frontend Stack (Required)

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|----------|
| **Framework** | React | 18+ | UI library |
| **Language** | TypeScript | 5.0+ | Type safety |
| **Build Tool** | Vite | 5.0+ | Dev & build |
| **Styling** | Tailwind CSS | 3.4+ | Styling |
| **Components** | shadcn/ui | Latest | UI components |
| **Charts** | Recharts | 2.10+ | Visualizations |
| **State** | Zustand | 4.4+ | State management |
| **Data Fetching** | React Query | 5.0+ | API management |
| **Real-time** | Socket.IO Client | 4.6+ | WebSocket |
| **Forms** | React Hook Form | 7.49+ | Form handling |

### Additional Libraries

```python
# Backend Dependencies (requirements.txt)
fastapi==0.104.1
uvicorn[standard]==0.24.0
celery==5.3.4
redis==5.0.1
sqlalchemy==2.0.23
pydantic==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-socketio==5.10.0
pyyaml==6.0.1
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
prometheus-client==0.19.0
```

```json
// Frontend Dependencies (package.json)
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.2.2",
    "@tanstack/react-query": "^5.0.0",
    "zustand": "^4.4.7",
    "socket.io-client": "^4.6.0",
    "recharts": "^2.10.0",
    "react-hook-form": "^7.49.0",
    "axios": "^1.6.2",
    "date-fns": "^3.0.0",
    "lucide-react": "^0.294.0",
    "@radix-ui/react-*": "latest"
  }
}
```

## 📁 Project Structure

```
flexiroaster/
├── backend/                          # Python Backend
│   ├── app/
│   │   ├── main.py                  # FastAPI application
│   │   ├── config.py                # Configuration
│   │   ├── api/                     # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── pipelines.py        # Pipeline APIs
│   │   │   ├── metrics.py          # Metrics APIs
│   │   │   ├── logs.py             # Logs APIs
│   │   │   ├── alerts.py           # Alerts APIs
│   │   │   └── auth.py             # Authentication
│   │   ├── engine/                  # Pipeline Engine
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py         # Pipeline class
│   │   │   ├── executor.py         # Execution engine
│   │   │   ├── stages.py           # Stage implementations
│   │   │   └── context.py          # Execution context
│   │   ├── ai/                      # AI/ML Layer
│   │   │   ├── __init__.py
│   │   │   ├── insights.py         # AI insights
│   │   │   ├── optimizer.py        # Pipeline optimization
│   │   │   └── predictor.py        # Failure prediction
│   │   ├── websocket/               # Real-time events
│   │   │   ├── __init__.py
│   │   │   └── events.py           # WebSocket handlers
│   │   ├── models/                  # Database models
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py
│   │   │   └── execution.py
│   │   └── schemas/                 # Pydantic schemas
│   │       ├── __init__.py
│   │       ├── pipeline.py
│   │       └── response.py
│   ├── tests/                       # Backend tests
│   ├── pipelines/                   # Pipeline definitions
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                         # React Frontend
│   ├── src/
│   │   ├── main.tsx                # Entry point
│   │   ├── App.tsx                 # Root component
│   │   ├── pages/                  # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Pipelines.tsx
│   │   │   ├── Monitoring.tsx
│   │   │   └── Settings.tsx
│   │   ├── components/             # Reusable components
│   │   │   ├── ui/                 # shadcn/ui components
│   │   │   ├── MetricsCard.tsx
│   │   │   ├── PipelineStatus.tsx
│   │   │   ├── ActivityLog.tsx
│   │   │   ├── AlertsPanel.tsx
│   │   │   └── Chart.tsx
│   │   ├── lib/                    # Utilities
│   │   │   ├── api.ts             # API client
│   │   │   ├── socket.ts          # WebSocket client
│   │   │   └── utils.ts
│   │   ├── hooks/                  # Custom hooks
│   │   │   ├── useWebSocket.ts
│   │   │   ├── usePipelines.ts
│   │   │   └── useMetrics.ts
│   │   ├── store/                  # Zustand stores
│   │   │   ├── pipelineStore.ts
│   │   │   └── uiStore.ts
│   │   └── types/                  # TypeScript types
│   │       └── pipeline.ts
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── docker-compose.yml               # Full stack setup
├── .env.example                     # Environment template
└── README.md                        # This file
```

## 📦 Installation

### Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 18+** (for frontend)
- **PostgreSQL 14+**
- **Redis 7.0+**
- **RabbitMQ 3.12+** (optional)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
python -m app.database.init

# Run migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Docker Setup (Recommended)

```bash
# Start entire stack
docker-compose up -d

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# PostgreSQL: localhost:5432
# Redis: localhost:6379
```

## 🚀 Quick Start

### 1. Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Backend runs at:** `http://localhost:8000`  
**API docs:** `http://localhost:8000/docs`

### 2. Start Frontend

```bash
cd frontend
npm run dev
```

**Frontend runs at:** `http://localhost:3000`

### 3. Access Dashboard

Open browser to `http://localhost:3000` and you'll see:
- Real-time metrics dashboard
- Active pipelines list
- Activity logs
- AI insights panel

## 🐍 Backend Implementation

### FastAPI Application (app/main.py)

```python
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.api import pipelines, metrics, logs, alerts
from app.websocket.events import handle_websocket
import socketio

# Initialize FastAPI
app = FastAPI(
    title="FlexiRoaster API",
    version="1.0.0",
    description="Pipeline automation backend"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO for real-time updates
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['http://localhost:3000']
)
socket_app = socketio.ASGIApp(sio, app)

# Include routers
app.include_router(pipelines.router, prefix="/api/pipelines", tags=["Pipelines"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])

@app.get("/")
async def root():
    return {"message": "FlexiRoaster API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# WebSocket connection handler
@sio.on('connect')
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit('connected', {'message': 'Connected to FlexiRoaster'})

@sio.on('disconnect')
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
```

### Pipeline API (app/api/pipelines.py)

```python
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.pipeline import PipelineCreate, PipelineResponse, ExecutionResponse
from app.engine.executor import PipelineExecutor
from app.models.pipeline import Pipeline
from typing import List
import uuid

router = APIRouter()
executor = PipelineExecutor()

@router.get("/", response_model=List[PipelineResponse])
async def list_pipelines():
    """Get all pipelines"""
    pipelines = await Pipeline.get_all()
    return pipelines

@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(pipeline_id: str):
    """Get pipeline by ID"""
    pipeline = await Pipeline.get_by_id(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline

@router.post("/", response_model=PipelineResponse, status_code=201)
async def create_pipeline(pipeline: PipelineCreate):
    """Create new pipeline"""
    new_pipeline = await Pipeline.create(pipeline.dict())
    return new_pipeline

@router.post("/{pipeline_id}/execute", response_model=ExecutionResponse)
async def execute_pipeline(
    pipeline_id: str, 
    background_tasks: BackgroundTasks,
    data: dict = None
):
    """Execute pipeline"""
    pipeline = await Pipeline.get_by_id(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    execution_id = str(uuid.uuid4())
    
    # Run pipeline in background
    background_tasks.add_task(
        executor.execute,
        pipeline=pipeline,
        execution_id=execution_id,
        data=data
    )
    
    return {
        "execution_id": execution_id,
        "pipeline_id": pipeline_id,
        "status": "started",
        "message": "Pipeline execution started"
    }

@router.get("/{pipeline_id}/executions")
async def get_executions(pipeline_id: str, limit: int = 10):
    """Get pipeline execution history"""
    executions = await Pipeline.get_executions(pipeline_id, limit)
    return executions

@router.delete("/{pipeline_id}")
async def delete_pipeline(pipeline_id: str):
    """Delete pipeline"""
    success = await Pipeline.delete(pipeline_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"message": "Pipeline deleted successfully"}
```

### Pipeline Executor (app/engine/executor.py)

```python
import asyncio
from typing import Dict, Any
from app.engine.pipeline import Pipeline
from app.engine.stages import get_stage
from app.websocket.events import emit_event
import logging

logger = logging.getLogger(__name__)

class PipelineExecutor:
    """Core pipeline execution engine"""
    
    async def execute(
        self, 
        pipeline: Pipeline, 
        execution_id: str,
        data: Dict[str, Any] = None
    ):
        """
        Execute pipeline stages sequentially
        """
        context = {
            'execution_id': execution_id,
            'pipeline_id': pipeline.id,
            'data': data or {},
            'results': {}
        }
        
        try:
            # Emit execution started
            await emit_event('execution_started', {
                'execution_id': execution_id,
                'pipeline_id': pipeline.id
            })
            
            # Execute each stage
            for stage_config in pipeline.stages:
                stage = get_stage(stage_config['type'])
                
                # Emit stage started
                await emit_event('stage_started', {
                    'execution_id': execution_id,
                    'stage': stage_config['id']
                })
                
                # Execute stage
                result = await stage.execute(context, stage_config)
                context['results'][stage_config['id']] = result
                
                # Emit stage completed
                await emit_event('stage_completed', {
                    'execution_id': execution_id,
                    'stage': stage_config['id'],
                    'result': result
                })
            
            # Emit execution completed
            await emit_event('execution_completed', {
                'execution_id': execution_id,
                'status': 'success',
                'results': context['results']
            })
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            await emit_event('execution_failed', {
                'execution_id': execution_id,
                'error': str(e)
            })
            raise
```

### Stage Implementation (app/engine/stages.py)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class Stage(ABC):
    """Base stage class"""
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute stage logic"""
        pass

class InputStage(Stage):
    """Input stage for data ingestion"""
    
    async def execute(self, context: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        # Implement input logic
        data = context.get('data', {})
        return {'input_data': data, 'count': len(data)}

class ValidationStage(Stage):
    """Validation stage"""
    
    async def execute(self, context: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        # Implement validation logic
        schema = config.get('schema', {})
        data = context['results'].get('input', {}).get('input_data', {})
        
        # Validate against schema
        is_valid = self.validate(data, schema)
        
        return {'valid': is_valid, 'data': data}
    
    def validate(self, data, schema):
        # Simple validation logic
        return True

class ProcessingStage(Stage):
    """Processing stage"""
    
    async def execute(self, context: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        # Implement processing logic
        operations = config.get('operations', [])
        data = context['results'].get('validation', {}).get('data', {})
        
        processed = self.process(data, operations)
        
        return {'processed_data': processed}
    
    def process(self, data, operations):
        # Processing logic
        return data

def get_stage(stage_type: str) -> Stage:
    """Factory function to get stage by type"""
    stages = {
        'input': InputStage,
        'validation': ValidationStage,
        'processing': ProcessingStage,
    }
    
    stage_class = stages.get(stage_type)
    if not stage_class:
        raise ValueError(f"Unknown stage type: {stage_type}")
    
    return stage_class()
```

### WebSocket Events (app/websocket/events.py)

```python
from app.main import sio

async def emit_event(event_name: str, data: dict):
    """Emit event to all connected clients"""
    await sio.emit(event_name, data)

async def emit_to_room(room: str, event_name: str, data: dict):
    """Emit event to specific room"""
    await sio.emit(event_name, data, room=room)
```

## ⚛️ Frontend Implementation

### API Client (src/lib/api.ts)

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Pipeline APIs
export const pipelinesAPI = {
  getAll: () => api.get('/pipelines'),
  getById: (id: string) => api.get(`/pipelines/${id}`),
  create: (data: any) => api.post('/pipelines', data),
  execute: (id: string, data?: any) => api.post(`/pipelines/${id}/execute`, data),
  delete: (id: string) => api.delete(`/pipelines/${id}`),
  getExecutions: (id: string) => api.get(`/pipelines/${id}/executions`),
};

// Metrics APIs
export const metricsAPI = {
  getCurrent: () => api.get('/metrics'),
  getHistory: (timeRange: string) => api.get(`/metrics/history?range=${timeRange}`),
};

// Logs APIs
export const logsAPI = {
  getRecent: (limit: number = 50) => api.get(`/logs?limit=${limit}`),
  stream: () => api.get('/logs/stream'),
};

// Alerts APIs
export const alertsAPI = {
  getActive: () => api.get('/alerts'),
  acknowledge: (id: string) => api.post(`/alerts/${id}/acknowledge`),
};
```

### WebSocket Hook (src/hooks/useWebSocket.ts)

```typescript
import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

const SOCKET_URL = import.meta.env.VITE_WS_URL || 'http://localhost:8000';

export const useWebSocket = () => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    const socketInstance = io(SOCKET_URL, {
      transports: ['websocket'],
    });

    socketInstance.on('connect', () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    });

    socketInstance.on('disconnect', () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    });

    // Listen to pipeline events
    socketInstance.on('execution_started', (data) => {
      setEvents((prev) => [...prev, { type: 'started', ...data }]);
    });

    socketInstance.on('stage_completed', (data) => {
      setEvents((prev) => [...prev, { type: 'stage_completed', ...data }]);
    });

    socketInstance.on('execution_completed', (data) => {
      setEvents((prev) => [...prev, { type: 'completed', ...data }]);
    });

    socketInstance.on('execution_failed', (data) => {
      setEvents((prev) => [...prev, { type: 'failed', ...data }]);
    });

    setSocket(socketInstance);

    return () => {
      socketInstance.disconnect();
    };
  }, []);

  return { socket, isConnected, events };
};
```

### Dashboard Component (src/pages/Dashboard.tsx)

```typescript
import React, { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { metricsAPI, pipelinesAPI } from '@/lib/api';
import { useWebSocket } from '@/hooks/useWebSocket';
import MetricsCard from '@/components/MetricsCard';
import PipelineStatus from '@/components/PipelineStatus';
import ActivityLog from '@/components/ActivityLog';
import AlertsPanel from '@/components/AlertsPanel';
import { Card } from '@/components/ui/card';

export default function Dashboard() {
  const { isConnected, events } = useWebSocket();
  
  // Fetch metrics
  const { data: metrics, refetch: refetchMetrics } = useQuery({
    queryKey: ['metrics'],
    queryFn: () => metricsAPI.getCurrent(),
    refetchInterval: 5000, // Refetch every 5 seconds
  });

  // Fetch pipelines
  const { data: pipelines } = useQuery({
    queryKey: ['pipelines'],
    queryFn: () => pipelinesAPI.getAll(),
  });

  // Refetch when real-time events come in
  useEffect(() => {
    if (events.length > 0) {
      refetchMetrics();
    }
  }, [events, refetchMetrics]);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="flex items-center gap-2">
          <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-muted-foreground">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricsCard
          title="Total Pipelines"
          value={metrics?.data?.total_pipelines || 0}
          change={+12}
          icon="pipeline"
        />
        <MetricsCard
          title="Active Executions"
          value={metrics?.data?.active_executions || 0}
          change={+5}
          icon="activity"
        />
        <MetricsCard
          title="Success Rate"
          value={`${metrics?.data?.success_rate || 0}%`}
          change={+3.2}
          icon="check"
        />
        <MetricsCard
          title="Avg. Duration"
          value={`${metrics?.data?.avg_duration || 0}s`}
          change={-8}
          icon="clock"
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pipeline Status */}
        <Card className="lg:col-span-2">
          <PipelineStatus pipelines={pipelines?.data || []} />
        </Card>

        {/* Alerts */}
        <Card>
          <AlertsPanel />
        </Card>
      </div>

      {/* Activity Log */}
      <Card>
        <ActivityLog events={events} />
      </Card>
    </div>
  );
}
```

### Metrics Card Component (src/components/MetricsCard.tsx)

```typescript
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface MetricsCardProps {
  title: string;
  value: string | number;
  change: number;
  icon: string;
}

export default function MetricsCard({ title, value, change, icon }: MetricsCardProps) {
  const isPositive = change >= 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground flex items-center
