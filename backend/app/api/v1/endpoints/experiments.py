"""
Experiment API endpoints.

Provides CRUD operations for experiment tracking.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.schemas.experiment import (
    Experiment,
    ExperimentCreate,
    ExperimentUpdate,
    ExperimentSummary,
    ExperimentWithDuration,
)
from app.services.experiment_service import ExperimentService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[Experiment])
def list_experiments(
    project_id: Optional[int] = None,
    model_id: Optional[int] = None,
    dataset_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all experiments with optional filtering.

    **Query Parameters:**
    - **project_id**: Filter by project ID (optional)
    - **model_id**: Filter by model ID (optional)
    - **dataset_id**: Filter by dataset ID (optional)
    - **status**: Filter by status (pending, running, completed, failed) (optional)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)

    **Returns:**
    - List of experiments matching the filters (sorted by created_at desc)

    **Example:**
    ```
    GET /api/v1/experiments?project_id=1&status=completed
    ```
    """
    if limit > 1000:
        limit = 1000

    experiments = ExperimentService.get_experiments(
        db=db,
        project_id=project_id,
        model_id=model_id,
        dataset_id=dataset_id,
        status=status,
        skip=skip,
        limit=limit
    )
    return experiments


@router.get("/summary", response_model=List[ExperimentSummary])
def list_experiments_summary(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get summary of all experiments.

    **Query Parameters:**
    - **project_id**: Filter by project ID (optional)

    **Returns:**
    - List of experiment summaries (id, name, status, model_id, dataset_id, created_at)

    **Example:**
    ```
    GET /api/v1/experiments/summary?project_id=1
    ```
    """
    summaries = ExperimentService.get_experiments_summary(db=db, project_id=project_id)
    return summaries


@router.post("/", response_model=Experiment, status_code=status.HTTP_201_CREATED)
def create_experiment(
    experiment: ExperimentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new experiment.

    **Request Body:**
    - **name**: Experiment name (required)
    - **description**: Experiment description (optional)
    - **parameters**: JSON object with experiment parameters (optional)
    - **metrics**: JSON object with experiment metrics (optional)
    - **artifacts**: JSON object with artifact paths (optional)
    - **tags**: List of tags (optional)
    - **notes**: Additional notes (optional)
    - **model_id**: Model ID (optional)
    - **dataset_id**: Dataset ID (optional)
    - **project_id**: Project ID (required)

    **Returns:**
    - Created experiment object with status="pending"

    **Example:**
    ```json
    {
        "name": "EGFR SAR Training Run #5",
        "description": "Training with increased max_depth",
        "parameters": {
            "n_estimators": 100,
            "max_depth": 30,
            "learning_rate": 0.01
        },
        "tags": ["baseline", "hyperparameter-tuning"],
        "model_id": 5,
        "dataset_id": 3,
        "project_id": 1
    }
    ```
    """
    try:
        # Validate project exists
        from app.services.project_service import ProjectService
        project = ProjectService.get_project(db, experiment.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {experiment.project_id} not found"
            )

        # Validate model exists if provided
        if experiment.model_id:
            from app.services.model_service import MLModelService
            model = MLModelService.get_model(db, experiment.model_id)
            if not model:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Model with id {experiment.model_id} not found"
                )

        # Validate dataset exists if provided
        if experiment.dataset_id:
            from app.services.dataset_service import DatasetService
            dataset = DatasetService.get_dataset(db, experiment.dataset_id)
            if not dataset:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dataset with id {experiment.dataset_id} not found"
                )

        db_experiment = ExperimentService.create_experiment(db=db, experiment=experiment)
        return db_experiment

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating experiment: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create experiment: {str(e)}"
        )


@router.get("/{experiment_id}", response_model=ExperimentWithDuration)
def get_experiment(
    experiment_id: int,
    db: Session = Depends(get_db)
):
    """
    Get experiment by ID with computed duration.

    **Path Parameters:**
    - **experiment_id**: Experiment ID

    **Returns:**
    - Experiment object with duration_seconds (if completed)

    **Example:**
    ```
    GET /api/v1/experiments/123
    ```
    """
    experiment = ExperimentService.get_experiment_with_duration(db=db, experiment_id=experiment_id)
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with id {experiment_id} not found"
        )
    return experiment


@router.put("/{experiment_id}", response_model=Experiment)
def update_experiment(
    experiment_id: int,
    experiment_update: ExperimentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing experiment.

    **Path Parameters:**
    - **experiment_id**: Experiment ID

    **Request Body:**
    - Any experiment fields to update (all optional)

    **Returns:**
    - Updated experiment object

    **Note:**
    - When status is updated to "running", started_at is automatically set
    - When status is updated to "completed" or "failed", completed_at is automatically set

    **Example:**
    ```json
    {
        "status": "running",
        "metrics": {
            "epoch": 10,
            "loss": 0.35,
            "accuracy": 0.88
        }
    }
    ```
    """
    db_experiment = ExperimentService.update_experiment(
        db=db,
        experiment_id=experiment_id,
        experiment_update=experiment_update
    )
    if not db_experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with id {experiment_id} not found"
        )
    return db_experiment


@router.delete("/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experiment(
    experiment_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an experiment.

    **Path Parameters:**
    - **experiment_id**: Experiment ID

    **Returns:**
    - 204 No Content on success

    **Example:**
    ```
    DELETE /api/v1/experiments/123
    ```
    """
    success = ExperimentService.delete_experiment(db=db, experiment_id=experiment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with id {experiment_id} not found"
        )
    return None
