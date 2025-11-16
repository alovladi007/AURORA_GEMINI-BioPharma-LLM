"""
ML Model API endpoints.

Provides CRUD operations for ML model registry.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.schemas.model import (
    MLModel,
    MLModelCreate,
    MLModelUpdate,
    MLModelSummary,
    MLModelWithMetrics,
)
from app.services.model_service import MLModelService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[MLModel])
def list_models(
    project_id: Optional[int] = None,
    model_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all ML models with optional filtering.

    **Query Parameters:**
    - **project_id**: Filter by project ID (optional)
    - **model_type**: Filter by model type (optional)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)

    **Returns:**
    - List of ML models matching the filters

    **Example:**
    ```
    GET /api/v1/models?project_id=1&model_type=drug_design_sar
    ```
    """
    if limit > 1000:
        limit = 1000

    models = MLModelService.get_models(
        db=db,
        project_id=project_id,
        model_type=model_type,
        skip=skip,
        limit=limit
    )
    return models


@router.get("/summary", response_model=List[MLModelSummary])
def list_models_summary(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get summary of all ML models.

    **Query Parameters:**
    - **project_id**: Filter by project ID (optional)

    **Returns:**
    - List of model summaries (id, name, type, version, framework, created_at)

    **Example:**
    ```
    GET /api/v1/models/summary?project_id=1
    ```
    """
    summaries = MLModelService.get_models_summary(db=db, project_id=project_id)
    return summaries


@router.post("/", response_model=MLModel, status_code=status.HTTP_201_CREATED)
def create_model(
    model: MLModelCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new ML model in the registry.

    **Request Body:**
    - **name**: Model name (required)
    - **description**: Model description (optional)
    - **model_type**: Type of model (drug_design_sar, safety_admet, etc.) (required)
    - **version**: Model version (required)
    - **framework**: ML framework (pytorch, tensorflow, sklearn, etc.) (optional)
    - **architecture**: Model architecture description (optional)
    - **hyperparameters**: JSON object with hyperparameters (optional)
    - **training_metrics**: JSON object with training metrics (optional)
    - **model_path**: Path to model file (optional)
    - **artifact_path**: Path to model artifacts directory (optional)
    - **metadata**: Additional metadata (optional)
    - **project_id**: Project ID (required)

    **Returns:**
    - Created model object

    **Example:**
    ```json
    {
        "name": "EGFR SAR Predictor v1",
        "description": "Random Forest classifier for EGFR activity prediction",
        "model_type": "drug_design_sar",
        "version": "1.0.0",
        "framework": "sklearn",
        "architecture": "RandomForestClassifier",
        "hyperparameters": {
            "n_estimators": 100,
            "max_depth": 20,
            "min_samples_split": 2
        },
        "training_metrics": {
            "accuracy": 0.87,
            "auroc": 0.92,
            "f1": 0.85
        },
        "project_id": 1
    }
    ```
    """
    try:
        # Validate project exists
        from app.services.project_service import ProjectService
        project = ProjectService.get_project(db, model.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {model.project_id} not found"
            )

        db_model = MLModelService.create_model(db=db, model=model)
        return db_model

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating model: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create model: {str(e)}"
        )


@router.get("/{model_id}", response_model=MLModelWithMetrics)
def get_model(
    model_id: int,
    db: Session = Depends(get_db)
):
    """
    Get ML model by ID with experiment count.

    **Path Parameters:**
    - **model_id**: Model ID

    **Returns:**
    - Model object with experiments_count

    **Example:**
    ```
    GET /api/v1/models/123
    ```
    """
    model = MLModelService.get_model_with_metrics(db=db, model_id=model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with id {model_id} not found"
        )
    return model


@router.put("/{model_id}", response_model=MLModel)
def update_model(
    model_id: int,
    model_update: MLModelUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing ML model.

    **Path Parameters:**
    - **model_id**: Model ID

    **Request Body:**
    - Any model fields to update (all optional)

    **Returns:**
    - Updated model object

    **Example:**
    ```json
    {
        "description": "Updated with better hyperparameters",
        "training_metrics": {
            "accuracy": 0.89,
            "auroc": 0.94,
            "f1": 0.87
        }
    }
    ```
    """
    db_model = MLModelService.update_model(
        db=db,
        model_id=model_id,
        model_update=model_update
    )
    if not db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with id {model_id} not found"
        )
    return db_model


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(
    model_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an ML model.

    **Path Parameters:**
    - **model_id**: Model ID

    **Returns:**
    - 204 No Content on success

    **Note:**
    This will also delete all associated experiments (cascade delete).

    **Example:**
    ```
    DELETE /api/v1/models/123
    ```
    """
    success = MLModelService.delete_model(db=db, model_id=model_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with id {model_id} not found"
        )
    return None
