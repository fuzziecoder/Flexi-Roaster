"""
Pipeline API Routes for FlexiRoaster.
Handles pipeline CRUD operations.
"""
import uuid
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List

from api.schemas import (
    PipelineCreate, PipelineUpdate, PipelineResponse, PipelineDetailResponse,
    PipelineListResponse, SuccessResponse, StageResponse
)
from db import (
    get_db_session, PipelineCRUD, PipelineDB, PipelineStageDB
)
from core.redis_state import redis_state_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


def _pipeline_to_response(pipeline: PipelineDB) -> PipelineResponse:
    """Convert database model to response schema"""
    return PipelineResponse(
        id=pipeline.id,
        name=pipeline.name,
        description=pipeline.description,
        version=pipeline.version,
        is_active=pipeline.is_active,
        schedule=pipeline.schedule,
        stage_count=len(pipeline.stages) if pipeline.stages else 0,
        created_at=pipeline.created_at,
        updated_at=pipeline.updated_at
    )


def _pipeline_to_detail_response(pipeline: PipelineDB) -> PipelineDetailResponse:
    """Convert database model to detailed response schema"""
    stages = [
        StageResponse(
            id=s.stage_id,
            name=s.name,
            type=s.stage_type,
            description=s.description,
            config=s.config or {},
            dependencies=s.dependencies or [],
            timeout=s.timeout,
            max_retries=s.max_retries,
            retry_delay=s.retry_delay,
            is_critical=s.is_critical,
            order=s.order
        )
        for s in (pipeline.stages or [])
    ]
    
    return PipelineDetailResponse(
        id=pipeline.id,
        name=pipeline.name,
        description=pipeline.description,
        version=pipeline.version,
        is_active=pipeline.is_active,
        schedule=pipeline.schedule,
        stage_count=len(stages),
        created_at=pipeline.created_at,
        updated_at=pipeline.updated_at,
        stages=stages,
        config=pipeline.config or {}
    )


@router.post(
    "",
    response_model=PipelineDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new pipeline"
)
async def create_pipeline(
    pipeline_data: PipelineCreate,
    db: Session = Depends(get_db_session)
):
    """
    Create a new pipeline with stages.
    
    - **name**: Pipeline name
    - **description**: Optional description
    - **stages**: List of stage definitions
    - **config**: Optional pipeline configuration
    - **schedule**: Optional cron schedule
    """
    pipeline_id = f"pipeline-{uuid.uuid4().hex[:12]}"
    
    try:
        # Create pipeline
        pipeline = PipelineCRUD.create(
            db=db,
            id=pipeline_id,
            name=pipeline_data.name,
            description=pipeline_data.description,
            version=pipeline_data.version,
            definition={"stages": [s.model_dump() for s in pipeline_data.stages]},
            config=pipeline_data.config,
            schedule=pipeline_data.schedule
        )
        
        # Create stages
        for order, stage_data in enumerate(pipeline_data.stages):
            stage = PipelineStageDB(
                stage_id=stage_data.id,
                pipeline_id=pipeline_id,
                name=stage_data.name,
                description=stage_data.description,
                stage_type=stage_data.type.value,
                config=stage_data.config,
                dependencies=stage_data.dependencies,
                timeout=stage_data.timeout,
                max_retries=stage_data.max_retries,
                retry_delay=stage_data.retry_delay,
                is_critical=stage_data.is_critical,
                order=order
            )
            db.add(stage)
        
        db.commit()
        db.refresh(pipeline)
        
        logger.info(f"Created pipeline: {pipeline_id}")
        
        # Invalidate cache
        await redis_state_manager.invalidate_cache(pipeline_id)
        
        return _pipeline_to_detail_response(pipeline)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pipeline: {str(e)}"
        )


@router.get(
    "",
    response_model=PipelineListResponse,
    summary="List all pipelines"
)
async def list_pipelines(
    is_active: bool = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """
    Get a list of all pipelines.
    
    - **is_active**: Filter by active status
    - **skip**: Number of pipelines to skip (pagination)
    - **limit**: Maximum number of pipelines to return
    """
    pipelines = PipelineCRUD.get_all(db, is_active=is_active, skip=skip, limit=limit)
    total = PipelineCRUD.count(db, is_active=is_active)
    
    return PipelineListResponse(
        pipelines=[_pipeline_to_response(p) for p in pipelines],
        total=total
    )


@router.get(
    "/{pipeline_id}",
    response_model=PipelineDetailResponse,
    summary="Get pipeline details"
)
async def get_pipeline(
    pipeline_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Get detailed information about a specific pipeline.
    
    - **pipeline_id**: Unique pipeline identifier
    """
    # Try cache first
    cached = await redis_state_manager.get_cached_pipeline(pipeline_id)
    if cached:
        return PipelineDetailResponse(**cached)
    
    pipeline = PipelineCRUD.get_by_id(db, pipeline_id)
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {pipeline_id}"
        )
    
    response = _pipeline_to_detail_response(pipeline)
    
    # Cache the response
    await redis_state_manager.cache_pipeline(pipeline_id, response.model_dump())
    
    return response


@router.put(
    "/{pipeline_id}",
    response_model=PipelineDetailResponse,
    summary="Update a pipeline"
)
async def update_pipeline(
    pipeline_id: str,
    pipeline_data: PipelineUpdate,
    db: Session = Depends(get_db_session)
):
    """
    Update an existing pipeline.
    
    - **pipeline_id**: Unique pipeline identifier
    """
    pipeline = PipelineCRUD.get_by_id(db, pipeline_id)
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {pipeline_id}"
        )
    
    try:
        # Update pipeline fields
        update_data = pipeline_data.model_dump(exclude_unset=True)
        
        if "stages" in update_data:
            # Delete existing stages
            for stage in pipeline.stages:
                db.delete(stage)
            
            # Create new stages
            for order, stage_data in enumerate(pipeline_data.stages):
                stage = PipelineStageDB(
                    stage_id=stage_data.id,
                    pipeline_id=pipeline_id,
                    name=stage_data.name,
                    description=stage_data.description,
                    stage_type=stage_data.type.value,
                    config=stage_data.config,
                    dependencies=stage_data.dependencies,
                    timeout=stage_data.timeout,
                    max_retries=stage_data.max_retries,
                    retry_delay=stage_data.retry_delay,
                    is_critical=stage_data.is_critical,
                    order=order
                )
                db.add(stage)
            
            del update_data["stages"]
        
        # Update other fields
        for key, value in update_data.items():
            if hasattr(pipeline, key):
                setattr(pipeline, key, value)
        
        db.commit()
        db.refresh(pipeline)
        
        # Invalidate cache
        await redis_state_manager.invalidate_cache(pipeline_id)
        
        return _pipeline_to_detail_response(pipeline)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update pipeline: {str(e)}"
        )


@router.delete(
    "/{pipeline_id}",
    response_model=SuccessResponse,
    summary="Delete a pipeline"
)
async def delete_pipeline(
    pipeline_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Delete a pipeline.
    
    - **pipeline_id**: Unique pipeline identifier
    """
    success = PipelineCRUD.delete(db, pipeline_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {pipeline_id}"
        )
    
    db.commit()
    
    # Invalidate cache
    await redis_state_manager.invalidate_cache(pipeline_id)
    
    return SuccessResponse(message=f"Pipeline {pipeline_id} deleted successfully")


@router.post(
    "/{pipeline_id}/activate",
    response_model=SuccessResponse,
    summary="Activate a pipeline"
)
async def activate_pipeline(
    pipeline_id: str,
    db: Session = Depends(get_db_session)
):
    """Activate a pipeline for execution"""
    pipeline = PipelineCRUD.update(db, pipeline_id, is_active=True)
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {pipeline_id}"
        )
    
    db.commit()
    await redis_state_manager.invalidate_cache(pipeline_id)
    
    return SuccessResponse(message=f"Pipeline {pipeline_id} activated")


@router.post(
    "/{pipeline_id}/deactivate",
    response_model=SuccessResponse,
    summary="Deactivate a pipeline"
)
async def deactivate_pipeline(
    pipeline_id: str,
    db: Session = Depends(get_db_session)
):
    """Deactivate a pipeline"""
    pipeline = PipelineCRUD.update(db, pipeline_id, is_active=False)
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {pipeline_id}"
        )
    
    db.commit()
    await redis_state_manager.invalidate_cache(pipeline_id)
    
    return SuccessResponse(message=f"Pipeline {pipeline_id} deactivated")
