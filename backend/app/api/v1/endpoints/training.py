"""
Training orchestration endpoints.

Launches real ML training as tracked background Jobs (Celery) and exposes job
status for polling. Phase 1 ships SAR training; later phases add ADMET, KGE, etc.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.core.database import get_db
from app.models.job import Job, JobStatus, JobType

logger = logging.getLogger(__name__)

router = APIRouter()


class SARTrainingRequest(BaseModel):
    """Request to train a SAR model from ChEMBL or an uploaded curated CSV."""

    project_id: int
    target: Optional[str] = Field(
        None, description="ChEMBL target id (e.g. CHEMBL203) to ingest & train on"
    )
    input_csv: Optional[str] = Field(
        None, description="Path to a curated CSV (smiles,label) instead of ChEMBL"
    )
    model_name: str = Field("sar_random_forest", max_length=100)
    max_records: Optional[int] = Field(None, description="Cap ingested records (testing)")
    n_estimators: int = 300
    max_depth: int = 20

    model_config = {
        "json_schema_extra": {
            "example": {"project_id": 1, "target": "CHEMBL203", "model_name": "egfr_sar"}
        }
    }


class JobLaunchResponse(BaseModel):
    job_id: int
    task_id: Optional[str]
    status: str
    message: str


@router.post("/sar", response_model=JobLaunchResponse, status_code=status.HTTP_202_ACCEPTED)
def launch_sar_training(
    request: SARTrainingRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Launch a real SAR training job.

    Provide either `target` (ChEMBL id) or `input_csv`. Returns a job you can
    poll via `GET /api/v1/jobs/{job_id}`.
    """
    if not request.target and not request.input_csv:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either 'target' (ChEMBL id) or 'input_csv'.",
        )

    # 1. Create the tracking Job row (pending).
    job = Job(
        name=f"SAR training: {request.model_name}",
        description=f"Train SAR model from {request.target or request.input_csv}",
        job_type=JobType.MODEL_TRAINING,
        status=JobStatus.PENDING,
        progress=0,
        parameters=request.model_dump(),
        project_id=request.project_id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # 2. Dispatch the Celery task and record its id on the Job.
    try:
        from app.tasks.drug_design_tasks import train_sar_task

        async_result = train_sar_task.delay(
            input_csv=request.input_csv,
            target=request.target,
            model_name=request.model_name,
            project_id=request.project_id,
            max_records=request.max_records,
            n_estimators=request.n_estimators,
            max_depth=request.max_depth,
        )
        job.task_id = async_result.id
        db.commit()
        db.refresh(job)
    except Exception as exc:  # broker unavailable, etc.
        job.status = JobStatus.FAILED
        job.error = f"Failed to enqueue task: {exc}"
        db.commit()
        logger.exception("Failed to enqueue SAR training task")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Task queue unavailable; could not start training.",
        )

    return JobLaunchResponse(
        job_id=job.id,
        task_id=job.task_id,
        status=job.status.value,
        message="SAR training started. Poll GET /api/v1/jobs/{job_id} for progress.",
    )
