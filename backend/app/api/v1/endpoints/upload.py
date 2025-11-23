"""
File upload endpoints for datasets and model artifacts.
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from pathlib import Path

from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_user_id
from app.models.dataset import Dataset
from app.services.dataset_service import DatasetService

router = APIRouter()

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    ".csv", ".tsv", ".xlsx", ".xls",
    ".sdf", ".mol", ".pdb",
    ".json", ".xml",
    ".txt", ".parquet"
}

MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB


@router.post("/dataset", status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    project_id: int = None,
    name: str = None,
    description: str = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Upload a dataset file.

    Supports CSV, Excel, SDF, JSON, and other common formats.

    **Form Data:**
    - **file**: Dataset file to upload
    - **project_id**: Optional project ID to associate with
    - **name**: Optional dataset name (defaults to filename)
    - **description**: Optional description

    **Returns:**
    - Dataset metadata

    **Raises:**
    - 400: Invalid file type or size
    - 413: File too large
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file content to check size
    contents = await file.read()
    file_size = len(contents)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({file_size} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE} bytes)"
        )

    # Create storage directory if it doesn't exist
    storage_path = Path(settings.STORAGE_LOCAL_PATH) / "datasets" / str(user_id)
    storage_path.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    import uuid
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = storage_path / unique_filename

    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Create dataset record
    dataset_service = DatasetService(db)

    # Count records if CSV
    num_records = None
    if file_ext in [".csv", ".tsv"]:
        try:
            import pandas as pd
            df = pd.read_csv(file_path, sep="," if file_ext == ".csv" else "\t")
            num_records = len(df)
        except:
            pass

    dataset_name = name or file.filename
    dataset = dataset_service.create_dataset({
        "name": dataset_name,
        "description": description,
        "file_path": str(file_path),
        "file_size": file_size,
        "num_records": num_records,
        "project_id": project_id,
    })

    return {
        "id": dataset.id,
        "name": dataset.name,
        "filename": file.filename,
        "size": file_size,
        "num_records": num_records,
        "file_path": str(file_path),
        "message": "Dataset uploaded successfully"
    }


@router.post("/datasets/batch", status_code=status.HTTP_201_CREATED)
async def upload_multiple_datasets(
    files: List[UploadFile] = File(...),
    project_id: int = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Upload multiple dataset files.

    **Form Data:**
    - **files**: List of files to upload
    - **project_id**: Optional project ID

    **Returns:**
    - List of uploaded dataset metadata
    """
    results = []
    errors = []

    for file in files:
        try:
            result = await upload_dataset(
                file=file,
                project_id=project_id,
                db=db,
                user_id=user_id,
            )
            results.append(result)
        except HTTPException as e:
            errors.append({
                "filename": file.filename,
                "error": e.detail
            })

    return {
        "uploaded": results,
        "failed": errors,
        "total": len(files),
        "successful": len(results),
        "failed_count": len(errors),
    }


@router.delete("/dataset/{dataset_id}")
async def delete_dataset_file(
    dataset_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete a dataset and its associated file.

    **Path Parameters:**
    - **dataset_id**: Dataset ID

    **Returns:**
    - Success message
    """
    dataset_service = DatasetService(db)
    dataset = dataset_service.get_dataset_by_id(dataset_id)

    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )

    # Delete file from storage
    if dataset.file_path and os.path.exists(dataset.file_path):
        try:
            os.remove(dataset.file_path)
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Failed to delete file {dataset.file_path}: {e}")

    # Delete from database
    dataset_service.delete_dataset(dataset_id)

    return {"message": "Dataset deleted successfully"}
