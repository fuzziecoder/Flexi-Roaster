"""
Pipeline management API routes.
Handles CRUD operations for pipelines.
"""
from datetime import datetime
from typing import Dict
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.schemas import (
    PipelineCreate,
    PipelineUpdate,
    PipelineResponse,
    PipelineListResponse,
    SuccessResponse,
)
from backend.api.security import UserPrincipal, get_current_user
from backend.config import settings
from backend.core.pipeline_engine import PipelineEngine
from backend.events import get_event_publisher
from backend.models.pipeline import Pipeline, Stage, StageType

router = APIRouter(prefix="/pipelines", tags=["pipelines"])

# In-memory storage (will be replaced with database in Phase 3)
pipelines_db: Dict[str, Pipeline] = {}


@router.post(
    "",
    response_model=PipelineResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new pipeline"
)
async def create_pipeline(pipeline_data: PipelineCreate, current_user: UserPrincipal = Depends(get_current_user)):
    """Create a new pipeline with stages for the authenticated user."""
    try:
        stages = []
        for stage_data in pipeline_data.stages:
            stages.append(
                Stage(
                    id=stage_data.id or str(uuid.uuid4()),
                    name=stage_data.name,
                    type=StageType(stage_data.type.value),
                    config=stage_data.config,
                    dependencies=stage_data.dependencies,
                )
            )

        pipeline = Pipeline(
            id=str(uuid.uuid4()),
            name=pipeline_data.name,
            description=pipeline_data.description,
            stages=stages,
            user_id=current_user.user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        engine = PipelineEngine()
        is_valid, errors = engine.validate_pipeline(pipeline)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid pipeline: {', '.join(errors)}"
            )

        pipelines_db[pipeline.id] = pipeline

        get_event_publisher().publish(
            topic=settings.TOPIC_PIPELINE_CREATED,
            key=pipeline.id,
            payload={
                "pipeline_id": pipeline.id,
                "name": pipeline.name,
                "description": pipeline.description,
                "stage_count": len(pipeline.stages),
                "user_id": pipeline.user_id,
            },
        )

        return pipeline

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "",
    response_model=PipelineListResponse,
    summary="List all pipelines"
)
async def list_pipelines(
    skip: int = 0,
    limit: int = 100,
    current_user: UserPrincipal = Depends(get_current_user),
):
    """Get pipelines only for the authenticated user."""
    scoped_pipelines = [p for p in pipelines_db.values() if p.user_id == current_user.user_id]
    total = len(scoped_pipelines)
    pipelines = scoped_pipelines[skip: skip + limit]

    return PipelineListResponse(pipelines=pipelines, total=total)


@router.get(
    "/{pipeline_id}",
    response_model=PipelineResponse,
    summary="Get pipeline details"
)
async def get_pipeline(pipeline_id: str, current_user: UserPrincipal = Depends(get_current_user)):
    """Get a specific pipeline if it belongs to authenticated user."""
    pipeline = pipelines_db.get(pipeline_id)
    if pipeline is None or pipeline.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {pipeline_id}"
        )

    return pipeline


@router.put(
    "/{pipeline_id}",
    response_model=PipelineResponse,
    summary="Update a pipeline"
)
async def update_pipeline(
    pipeline_id: str,
    pipeline_data: PipelineUpdate,
    current_user: UserPrincipal = Depends(get_current_user),
):
    """Update a user-owned pipeline."""
    pipeline = pipelines_db.get(pipeline_id)
    if pipeline is None or pipeline.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {pipeline_id}"
        )

    if pipeline_data.name is not None:
        pipeline.name = pipeline_data.name
    if pipeline_data.description is not None:
        pipeline.description = pipeline_data.description
    if pipeline_data.stages is not None:
        stages = []
        for stage_data in pipeline_data.stages:
            stages.append(
                Stage(
                    id=stage_data.id or str(uuid.uuid4()),
                    name=stage_data.name,
                    type=StageType(stage_data.type.value),
                    config=stage_data.config,
                    dependencies=stage_data.dependencies,
                )
            )
        pipeline.stages = stages

    pipeline.updated_at = datetime.now()

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
async def delete_pipeline(pipeline_id: str, current_user: UserPrincipal = Depends(get_current_user)):
    """Delete a user-owned pipeline."""
    pipeline = pipelines_db.get(pipeline_id)
    if pipeline is None or pipeline.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {pipeline_id}"
        )

    del pipelines_db[pipeline_id]

    return SuccessResponse(message=f"Pipeline {pipeline_id} deleted successfully")
