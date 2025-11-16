"""
Job API endpoints.

Provides CRUD operations for async job tracking.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.schemas.job import (
    Job,
    JobCreate,
    JobUpdate,
    JobSummary,
    JobWithDuration,
)
from app.services.job_service import JobService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[Job])
def list_jobs(
    project_id: Optional[int] = None,
    job_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all jobs with optional filtering.

    **Query Parameters:**
    - **project_id**: Filter by project ID (optional)
    - **job_type**: Filter by job type (optional)
    - **status**: Filter by status (pending, running, completed, failed, cancelled) (optional)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)

    **Returns:**
    - List of jobs matching the filters (sorted by created_at desc)

    **Example:**
    ```
    GET /api/v1/jobs?project_id=1&status=running
    ```
    """
    if limit > 1000:
        limit = 1000

    jobs = JobService.get_jobs(
        db=db,
        project_id=project_id,
        job_type=job_type,
        status=status,
        skip=skip,
        limit=limit
    )
    return jobs


@router.get("/summary", response_model=List[JobSummary])
def list_jobs_summary(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get summary of all jobs.

    **Query Parameters:**
    - **project_id**: Filter by project ID (optional)

    **Returns:**
    - List of job summaries (id, job_type, status, progress, created_at)

    **Example:**
    ```
    GET /api/v1/jobs/summary?project_id=1
    ```
    """
    summaries = JobService.get_jobs_summary(db=db, project_id=project_id)
    return summaries


@router.post("/", response_model=Job, status_code=status.HTTP_201_CREATED)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new job.

    **Request Body:**
    - **job_type**: Type of job (model_training, model_inference, etc.) (required)
    - **parameters**: JSON object with job parameters (optional)
    - **result**: JSON object with job result (optional)
    - **error**: Error message (optional)
    - **logs**: Job logs (optional)
    - **project_id**: Project ID (required)

    **Returns:**
    - Created job object with status="pending" and progress=0

    **Example:**
    ```json
    {
        "job_type": "model_training",
        "parameters": {
            "model_id": 5,
            "dataset_id": 3,
            "epochs": 100,
            "batch_size": 32
        },
        "project_id": 1
    }
    ```
    """
    try:
        # Validate project exists
        from app.services.project_service import ProjectService
        project = ProjectService.get_project(db, job.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {job.project_id} not found"
            )

        db_job = JobService.create_job(db=db, job=job)
        return db_job

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating job: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )


@router.get("/{job_id}", response_model=JobWithDuration)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get job by ID with computed duration.

    **Path Parameters:**
    - **job_id**: Job ID

    **Returns:**
    - Job object with duration_seconds (if completed)

    **Example:**
    ```
    GET /api/v1/jobs/123
    ```
    """
    job = JobService.get_job_with_duration(db=db, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )
    return job


@router.put("/{job_id}", response_model=Job)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing job.

    **Path Parameters:**
    - **job_id**: Job ID

    **Request Body:**
    - Any job fields to update (all optional)

    **Returns:**
    - Updated job object

    **Note:**
    - When status is updated to "running", started_at is automatically set
    - When status is updated to "completed", "failed", or "cancelled", completed_at is automatically set

    **Example:**
    ```json
    {
        "status": "running",
        "progress": 50,
        "logs": "Training epoch 50/100..."
    }
    ```
    """
    db_job = JobService.update_job(
        db=db,
        job_id=job_id,
        job_update=job_update
    )
    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )
    return db_job


@router.post("/{job_id}/cancel", response_model=Job)
def cancel_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Cancel a pending or running job.

    **Path Parameters:**
    - **job_id**: Job ID

    **Returns:**
    - Updated job object with status="cancelled"

    **Note:**
    - Can only cancel jobs with status "pending" or "running"
    - Returns 400 Bad Request if job is already completed/failed/cancelled

    **Example:**
    ```
    POST /api/v1/jobs/123/cancel
    ```
    """
    db_job = JobService.cancel_job(db=db, job_id=job_id)
    if not db_job:
        # Check if job exists
        existing_job = JobService.get_job(db=db, job_id=job_id)
        if not existing_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with id {job_id} not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job with id {job_id} cannot be cancelled (status: {existing_job.status})"
            )
    return db_job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a job.

    **Path Parameters:**
    - **job_id**: Job ID

    **Returns:**
    - 204 No Content on success

    **Example:**
    ```
    DELETE /api/v1/jobs/123
    ```
    """
    success = JobService.delete_job(db=db, job_id=job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )
    return None
