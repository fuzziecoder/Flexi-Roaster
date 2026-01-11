"""
Pipeline management API routes.
Handles CRUD operations for pipelines.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
import uuid
from datetime import datetime

from backend.api.schemas import (
    PipelineCreate,
    PipelineUpdate,
    PipelineResponse,
    PipelineListResponse,
    SuccessResponse,
    ErrorResponse,
    StageResponse
)
from backend.models.pipeline import Pipeline, Stage, StageType
from backend.core.pipeline_engine import PipelineEngine

router = APIRouter(prefix="/pipelines", tags=["pipelines"])

# In-memory storage (will be replaced with database in Phase 3)
pipelines_db: Dict[str, Pipeline] = {}


@router.post(
    "",
    response_model=PipelineResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new pipeline"
)
async def create_pipeline(pipeline_data: PipelineCreate):
    """
    Create a new pipeline with stages.
    
    - **name**: Pipeline name
    - **description**: Pipeline description
    - **stages**: List of pipeline stages
    """
    try:
        # Create stages
        stages = []
        for stage_data in pipeline_data.stages:
            stage = Stage(
                id=stage_data.id or str(uuid.uuid4()),
                name=stage_data.name,
                type=StageType(stage_data.type.value),
                config=stage_data.config,
                dependencies=stage_data.dependencies
            )
            stages.append(stage)
        
        # Create pipeline
        pipeline = Pipeline(
            id=str(uuid.uuid4()),
            name=pipeline_data.name,
            description=pipeline_data.description,
            stages=stages,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Validate pipeline
        engine = PipelineEngine()
        is_valid, errors = engine.validate_pipeline(pipeline)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid pipeline: {', '.join(errors)}"
            )
        
        # Store pipeline
        pipelines_db[pipeline.id] = pipeline
        
        return pipeline
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=PipelineListResponse,
    summary="List all pipelines"
)
async def list_pipelines(skip: int = 0, limit: int = 100):
    """
    Get a list of all pipelines.
    
    - **skip**: Number of pipelines to skip (pagination)
    - **limit**: Maximum number of pipelines to return
    """
    all_pipelines = list(pipelines_db.values())
    total = len(all_pipelines)
    pipelines = all_pipelines[skip : skip + limit]
    
    return PipelineListResponse(
        pipelines=pipelines,
        total=total
    )


@router.get(
    "/{pipeline_id}",
    response_model=PipelineResponse,
    summary="Get pipeline details"
)
async def get_pipeline(pipeline_id: str):
    """
    Get details of a specific pipeline.
    
    - **pipeline_id**: Unique pipeline identifier
    """
    if pipeline_id not in pipelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {pipeline_id}"
        )
    
    return pipelines_db[pipeline_id]


@router.put(
    "/{pipeline_id}",
    response_model=PipelineResponse,
    summary="Update a pipeline"
)
async def update_pipeline(pipeline_id: str, pipeline_data: PipelineUpdate):
    """
    Update an existing pipeline.
    
    - **pipeline_id**: Unique pipeline identifier
    - **name**: New pipeline name (optional)
    - **description**: New pipeline description (optional)
    - **stages**: New stages list (optional)
    """
    if pipeline_id not in pipelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {pipeline_id}"
        )
    
    pipeline = pipelines_db[pipeline_id]
    
    # Update fields
    if pipeline_data.name is not None:
        pipeline.name = pipeline_data.name
    if pipeline_data.description is not None:
        pipeline.description = pipeline_data.description
    if pipeline_data.stages is not None:
        stages = []
        for stage_data in pipeline_data.stages:
            stage = Stage(
                id=stage_data.id or str(uuid.uuid4()),
                name=stage_data.name,
                type=StageType(stage_data.type.value),
                config=stage_data.config,
                dependencies=stage_data.dependencies
            )
            stages.append(stage)
        pipeline.stages = stages
    
    pipeline.updated_at = datetime.now()
    
    # Validate updated pipeline
    engine = PipelineEngine()
    is_valid, errors = engine.validate_pipeline(pipeline)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid pipeline: {', '.join(errors)}"
        )
    
    pipelines_db[pipeline_id] = pipeline
    
    return pipeline


@router.delete(
    "/{pipeline_id}",
    response_model=SuccessResponse,
    summary="Delete a pipeline"
)
async def delete_pipeline(pipeline_id: str):
    """
    Delete a pipeline.
    
    - **pipeline_id**: Unique pipeline identifier
    """
    if pipeline_id not in pipelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {pipeline_id}"
        )
    
    del pipelines_db[pipeline_id]
    
    return SuccessResponse(
        message=f"Pipeline {pipeline_id} deleted successfully"
    )
