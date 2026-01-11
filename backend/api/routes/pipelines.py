"""
Updated Pipeline API Routes with Database Integration
"""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from backend.api.schemas import (
    PipelineCreate,
    PipelineUpdate,
    PipelineResponse,
    MessageResponse
)
from backend.core.pipeline_engine import PipelineEngine
from backend.db.database import get_db
from backend.db import crud

router = APIRouter(prefix="/api/pipelines", tags=["pipelines"])

# Global pipeline engine instance
engine = PipelineEngine()


@router.post("", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(pipeline_data: PipelineCreate, db: Session = Depends(get_db)):
    """Create a new pipeline"""
    try:
        # Convert to dict and load into engine
        data = pipeline_data.model_dump()
        pipeline = engine.load_from_dict(data)
        
        # Save to database
        db_pipeline = crud.create_pipeline(db, pipeline)
        
        return PipelineResponse(
            id=db_pipeline.id,
            name=db_pipeline.name,
            description=db_pipeline.description,
            version=db_pipeline.version,
            stages=db_pipeline.definition.get("stages", []),
            variables=db_pipeline.definition.get("variables", {}),
            created_at=db_pipeline.created_at,
            updated_at=db_pipeline.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create pipeline: {str(e)}"
        )


@router.get("", response_model=List[PipelineResponse])
async def list_pipelines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all pipelines"""
    db_pipelines = crud.get_pipelines(db, skip=skip, limit=limit)
    
    # Also load into engine
    for db_pipeline in db_pipelines:
        if db_pipeline.id not in engine.pipelines:
            data = {
                "id": db_pipeline.id,
                "name": db_pipeline.name,
                "description": db_pipeline.description,
                "version": db_pipeline.version,
                "stages": db_pipeline.definition.get("stages", []),
                "variables": db_pipeline.definition.get("variables", {})
            }
            engine.load_from_dict(data)
    
    return [
        PipelineResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            version=p.version,
            stages=p.definition.get("stages", []),
            variables=p.definition.get("variables", {}),
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        for p in db_pipelines
    ]


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(pipeline_id: str, db: Session = Depends(get_db)):
    """Get a specific pipeline"""
    db_pipeline = crud.get_pipeline(db, pipeline_id)
    
    if not db_pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {pipeline_id}"
        )
    
    # Load into engine if not already loaded
    if pipeline_id not in engine.pipelines:
        data = {
            "id": db_pipeline.id,
            "name": db_pipeline.name,
            "description": db_pipeline.description,
            "version": db_pipeline.version,
            "stages": db_pipeline.definition.get("stages", []),
            "variables": db_pipeline.definition.get("variables", {})
        }
        engine.load_from_dict(data)
    
    return PipelineResponse(
        id=db_pipeline.id,
        name=db_pipeline.name,
        description=db_pipeline.description,
        version=db_pipeline.version,
        stages=db_pipeline.definition.get("stages", []),
        variables=db_pipeline.definition.get("variables", {}),
        created_at=db_pipeline.created_at,
        updated_at=db_pipeline.updated_at
    )


@router.delete("/{pipeline_id}", response_model=MessageResponse)
async def delete_pipeline(pipeline_id: str, db: Session = Depends(get_db)):
    """Delete a pipeline"""
    success = crud.delete_pipeline(db, pipeline_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {pipeline_id}"
        )
    
    # Remove from engine
    if pipeline_id in engine.pipelines:
        del engine.pipelines[pipeline_id]
    
    return MessageResponse(message=f"Pipeline {pipeline_id} deleted successfully")
