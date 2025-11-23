"""
Celery tasks for drug design module.

Handles asynchronous molecule generation, SAR prediction, and optimization.
"""

from celery import Task
from typing import List, Dict, Any

from app.celery_app import celery_app
from app.ml.drug_design.inference import (
    generate_molecules,
    predict_sar,
    optimize_leads,
)
from app.core.database import SessionLocal
from app.models.job import Job, JobStatus


class CallbackTask(Task):
    """Base task with database session and progress tracking."""

    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)

    def on_success(self, retval, task_id, args, kwargs):
        """Update job status on success."""
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.celery_task_id == task_id).first()
            if job:
                job.status = JobStatus.COMPLETED
                job.result = retval
                job.progress = 100
                db.commit()
        finally:
            db.close()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Update job status on failure."""
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.celery_task_id == task_id).first()
            if job:
                job.status = JobStatus.FAILED
                job.error_message = str(exc)
                db.commit()
        finally:
            db.close()


@celery_app.task(base=CallbackTask, bind=True, name="drug_design.generate_molecules")
def generate_molecules_task(
    self,
    smiles: str,
    num_molecules: int = 10,
    similarity_threshold: float = 0.7,
    job_id: int = None,
) -> Dict[str, Any]:
    """
    Generate similar molecules asynchronously.

    Args:
        smiles: Input SMILES string
        num_molecules: Number of molecules to generate
        similarity_threshold: Minimum similarity to input
        job_id: Database job ID for tracking

    Returns:
        Dict with generated molecules and metadata
    """
    # Update job to running
    if job_id:
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = JobStatus.RUNNING
                job.progress = 0
                db.commit()
        finally:
            db.close()

    # Generate molecules
    result = generate_molecules(smiles, num_molecules, similarity_threshold)

    # Update progress
    self.update_state(state="PROGRESS", meta={"progress": 100})

    return result


@celery_app.task(base=CallbackTask, bind=True, name="drug_design.predict_sar")
def predict_sar_task(
    self,
    smiles_list: List[str],
    job_id: int = None,
) -> Dict[str, Any]:
    """
    Predict SAR for molecules asynchronously.

    Args:
        smiles_list: List of SMILES strings
        job_id: Database job ID for tracking

    Returns:
        Dict with SAR predictions
    """
    if job_id:
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = JobStatus.RUNNING
                job.progress = 0
                db.commit()
        finally:
            db.close()

    # Predict SAR with progress updates
    total = len(smiles_list)
    predictions = []

    for i, smiles in enumerate(smiles_list):
        prediction = predict_sar(smiles)
        predictions.append(prediction)

        # Update progress
        progress = int((i + 1) / total * 100)
        self.update_state(state="PROGRESS", meta={"progress": progress})

        if job_id:
            db = SessionLocal()
            try:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    job.progress = progress
                    db.commit()
            finally:
                db.close()

    return {"predictions": predictions}


@celery_app.task(base=CallbackTask, bind=True, name="drug_design.optimize_leads")
def optimize_leads_task(
    self,
    smiles: str,
    target_property: str,
    num_iterations: int = 10,
    job_id: int = None,
) -> Dict[str, Any]:
    """
    Optimize lead compounds asynchronously.

    Args:
        smiles: Input SMILES string
        target_property: Property to optimize
        num_iterations: Number of optimization iterations
        job_id: Database job ID for tracking

    Returns:
        Dict with optimized molecules
    """
    if job_id:
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = JobStatus.RUNNING
                job.progress = 0
                db.commit()
        finally:
            db.close()

    # Optimize leads
    result = optimize_leads(smiles, target_property, num_iterations)

    # Update progress
    self.update_state(state="PROGRESS", meta={"progress": 100})

    return result
