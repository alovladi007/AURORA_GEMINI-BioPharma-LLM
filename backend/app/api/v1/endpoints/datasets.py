"""
Dataset API endpoints.

Provides CRUD operations for datasets.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.schemas.dataset import (
    Dataset,
    DatasetCreate,
    DatasetUpdate,
    DatasetSummary,
    DatasetWithStats,
)
from app.services.dataset_service import DatasetService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[Dataset])
def list_datasets(
    project_id: Optional[int] = None,
    dataset_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all datasets with optional filtering.

    **Query Parameters:**
    - **project_id**: Filter by project ID (optional)
    - **dataset_type**: Filter by dataset type (optional)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)

    **Returns:**
    - List of datasets matching the filters

    **Example:**
    ```
    GET /api/v1/datasets?project_id=1&dataset_type=molecular
    ```
    """
    if limit > 1000:
        limit = 1000

    datasets = DatasetService.get_datasets(
        db=db,
        project_id=project_id,
        dataset_type=dataset_type,
        skip=skip,
        limit=limit
    )
    return datasets


@router.get("/summary", response_model=List[DatasetSummary])
def list_datasets_summary(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get summary of all datasets.

    **Query Parameters:**
    - **project_id**: Filter by project ID (optional)

    **Returns:**
    - List of dataset summaries (id, name, type, size, created_at)

    **Example:**
    ```
    GET /api/v1/datasets/summary?project_id=1
    ```
    """
    summaries = DatasetService.get_datasets_summary(db=db, project_id=project_id)
    return summaries


@router.post("/", response_model=Dataset, status_code=status.HTTP_201_CREATED)
def create_dataset(
    dataset: DatasetCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new dataset.

    **Request Body:**
    - **name**: Dataset name (required)
    - **description**: Dataset description (optional)
    - **dataset_type**: Type of dataset (molecular, clinical, bioactivity, etc.) (required)
    - **file_path**: Path to dataset file (optional)
    - **file_format**: File format (csv, sdf, xlsx, etc.) (optional)
    - **file_size_bytes**: File size in bytes (optional)
    - **num_rows**: Number of rows (optional)
    - **num_columns**: Number of columns (optional)
    - **schema_info**: JSON schema information (optional)
    - **metadata**: Additional metadata (optional)
    - **project_id**: Project ID (required)

    **Returns:**
    - Created dataset object

    **Example:**
    ```json
    {
        "name": "Kinase Inhibitor Dataset",
        "description": "Bioactivity data for kinase inhibitors",
        "dataset_type": "bioactivity",
        "file_format": "csv",
        "num_rows": 15000,
        "num_columns": 25,
        "project_id": 1
    }
    ```
    """
    try:
        # Validate project exists
        from app.services.project_service import ProjectService
        project = ProjectService.get_project(db, dataset.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {dataset.project_id} not found"
            )

        db_dataset = DatasetService.create_dataset(db=db, dataset=dataset)
        return db_dataset

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating dataset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create dataset: {str(e)}"
        )


@router.get("/{dataset_id}", response_model=DatasetWithStats)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    """
    Get dataset by ID with usage statistics.

    **Path Parameters:**
    - **dataset_id**: Dataset ID

    **Returns:**
    - Dataset object with experiments_count

    **Example:**
    ```
    GET /api/v1/datasets/123
    ```
    """
    dataset = DatasetService.get_dataset_with_stats(db=db, dataset_id=dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with id {dataset_id} not found"
        )
    return dataset


@router.put("/{dataset_id}", response_model=Dataset)
def update_dataset(
    dataset_id: int,
    dataset_update: DatasetUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing dataset.

    **Path Parameters:**
    - **dataset_id**: Dataset ID

    **Request Body:**
    - Any dataset fields to update (all optional)

    **Returns:**
    - Updated dataset object

    **Example:**
    ```json
    {
        "description": "Updated description",
        "metadata": {"source": "ChEMBL 30"}
    }
    ```
    """
    db_dataset = DatasetService.update_dataset(
        db=db,
        dataset_id=dataset_id,
        dataset_update=dataset_update
    )
    if not db_dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with id {dataset_id} not found"
        )
    return db_dataset


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a dataset.

    **Path Parameters:**
    - **dataset_id**: Dataset ID

    **Returns:**
    - 204 No Content on success

    **Note:**
    This will also delete all associated experiments (cascade delete).

    **Example:**
    ```
    DELETE /api/v1/datasets/123
    ```
    """
    success = DatasetService.delete_dataset(db=db, dataset_id=dataset_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with id {dataset_id} not found"
        )
    return None
