"""
Job service layer.

Handles async job tracking CRUD operations.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


class JobService:
    """Service for async job tracking operations."""

    @staticmethod
    def get_job(db: Session, job_id: int) -> Optional[Job]:
        """Get job by ID."""
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    def get_jobs(
        db: Session,
        project_id: Optional[int] = None,
        job_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Job]:
        """Get all jobs with optional filtering."""
        query = db.query(Job)

        if project_id is not None:
            query = query.filter(Job.project_id == project_id)

        if job_type is not None:
            query = query.filter(Job.job_type == job_type)

        if status is not None:
            query = query.filter(Job.status == status)

        return query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create_job(db: Session, job: JobCreate) -> Job:
        """Create a new job."""
        db_job = Job(
            job_type=job.job_type,
            status="pending",
            progress=0,
            parameters=job.parameters,
            result=job.result,
            error=job.error,
            logs=job.logs,
            project_id=job.project_id,
        )
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return db_job

    @staticmethod
    def update_job(
        db: Session,
        job_id: int,
        job_update: JobUpdate
    ) -> Optional[Job]:
        """Update an existing job."""
        db_job = JobService.get_job(db, job_id)
        if not db_job:
            return None

        update_data = job_update.model_dump(exclude_unset=True)

        # Handle status transitions
        if "status" in update_data:
            new_status = update_data["status"]

            # Set started_at when status changes to running
            if new_status == "running" and db_job.status != "running":
                db_job.started_at = datetime.utcnow()

            # Set completed_at when status changes to completed, failed, or cancelled
            if new_status in ["completed", "failed", "cancelled"] and db_job.status not in ["completed", "failed", "cancelled"]:
                db_job.completed_at = datetime.utcnow()

        for field, value in update_data.items():
            setattr(db_job, field, value)

        db.commit()
        db.refresh(db_job)
        return db_job

    @staticmethod
    def delete_job(db: Session, job_id: int) -> bool:
        """Delete a job."""
        db_job = JobService.get_job(db, job_id)
        if not db_job:
            return False

        db.delete(db_job)
        db.commit()
        return True

    @staticmethod
    def get_job_with_duration(db: Session, job_id: int) -> Optional[dict]:
        """Get job with computed duration."""
        db_job = JobService.get_job(db, job_id)
        if not db_job:
            return None

        # Compute duration if applicable
        duration_seconds = None
        if db_job.started_at and db_job.completed_at:
            duration_seconds = int((db_job.completed_at - db_job.started_at).total_seconds())

        job_dict = {
            "id": db_job.id,
            "job_type": db_job.job_type,
            "status": db_job.status,
            "progress": db_job.progress,
            "parameters": db_job.parameters,
            "result": db_job.result,
            "error": db_job.error,
            "logs": db_job.logs,
            "started_at": db_job.started_at,
            "completed_at": db_job.completed_at,
            "project_id": db_job.project_id,
            "created_at": db_job.created_at,
            "updated_at": db_job.updated_at,
            "duration_seconds": duration_seconds,
        }

        return job_dict

    @staticmethod
    def get_jobs_summary(
        db: Session,
        project_id: Optional[int] = None
    ) -> List[dict]:
        """Get summary of all jobs."""
        query = db.query(Job)

        if project_id is not None:
            query = query.filter(Job.project_id == project_id)

        jobs = query.order_by(Job.created_at.desc()).all()
        summaries = []

        for job in jobs:
            summaries.append({
                "id": job.id,
                "job_type": job.job_type,
                "status": job.status,
                "progress": job.progress,
                "project_id": job.project_id,
                "created_at": job.created_at,
            })

        return summaries

    @staticmethod
    def cancel_job(db: Session, job_id: int) -> Optional[Job]:
        """Cancel a pending or running job."""
        db_job = JobService.get_job(db, job_id)
        if not db_job:
            return None

        # Can only cancel pending or running jobs
        if db_job.status not in ["pending", "running"]:
            return None

        db_job.status = "cancelled"
        db_job.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(db_job)
        return db_job
