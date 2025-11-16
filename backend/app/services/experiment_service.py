"""
Experiment service layer.

Handles experiment tracking CRUD operations.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.experiment import Experiment
from app.schemas.experiment import ExperimentCreate, ExperimentUpdate


class ExperimentService:
    """Service for experiment tracking operations."""

    @staticmethod
    def get_experiment(db: Session, experiment_id: int) -> Optional[Experiment]:
        """Get experiment by ID."""
        return db.query(Experiment).filter(Experiment.id == experiment_id).first()

    @staticmethod
    def get_experiments(
        db: Session,
        project_id: Optional[int] = None,
        model_id: Optional[int] = None,
        dataset_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Experiment]:
        """Get all experiments with optional filtering."""
        query = db.query(Experiment)

        if project_id is not None:
            query = query.filter(Experiment.project_id == project_id)

        if model_id is not None:
            query = query.filter(Experiment.model_id == model_id)

        if dataset_id is not None:
            query = query.filter(Experiment.dataset_id == dataset_id)

        if status is not None:
            query = query.filter(Experiment.status == status)

        return query.order_by(Experiment.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create_experiment(db: Session, experiment: ExperimentCreate) -> Experiment:
        """Create a new experiment."""
        db_experiment = Experiment(
            name=experiment.name,
            description=experiment.description,
            status="pending",
            parameters=experiment.parameters,
            metrics=experiment.metrics,
            artifacts=experiment.artifacts,
            tags=experiment.tags,
            notes=experiment.notes,
            model_id=experiment.model_id,
            dataset_id=experiment.dataset_id,
            project_id=experiment.project_id,
        )
        db.add(db_experiment)
        db.commit()
        db.refresh(db_experiment)
        return db_experiment

    @staticmethod
    def update_experiment(
        db: Session,
        experiment_id: int,
        experiment_update: ExperimentUpdate
    ) -> Optional[Experiment]:
        """Update an existing experiment."""
        db_experiment = ExperimentService.get_experiment(db, experiment_id)
        if not db_experiment:
            return None

        update_data = experiment_update.model_dump(exclude_unset=True)

        # Handle status transitions
        if "status" in update_data:
            new_status = update_data["status"]

            # Set started_at when status changes to running
            if new_status == "running" and db_experiment.status != "running":
                db_experiment.started_at = datetime.utcnow()

            # Set completed_at when status changes to completed or failed
            if new_status in ["completed", "failed"] and db_experiment.status not in ["completed", "failed"]:
                db_experiment.completed_at = datetime.utcnow()

        for field, value in update_data.items():
            setattr(db_experiment, field, value)

        db.commit()
        db.refresh(db_experiment)
        return db_experiment

    @staticmethod
    def delete_experiment(db: Session, experiment_id: int) -> bool:
        """Delete an experiment."""
        db_experiment = ExperimentService.get_experiment(db, experiment_id)
        if not db_experiment:
            return False

        db.delete(db_experiment)
        db.commit()
        return True

    @staticmethod
    def get_experiment_with_duration(db: Session, experiment_id: int) -> Optional[dict]:
        """Get experiment with computed duration."""
        db_experiment = ExperimentService.get_experiment(db, experiment_id)
        if not db_experiment:
            return None

        # Compute duration if applicable
        duration_seconds = None
        if db_experiment.started_at and db_experiment.completed_at:
            duration_seconds = int((db_experiment.completed_at - db_experiment.started_at).total_seconds())

        experiment_dict = {
            "id": db_experiment.id,
            "name": db_experiment.name,
            "description": db_experiment.description,
            "status": db_experiment.status,
            "parameters": db_experiment.parameters,
            "metrics": db_experiment.metrics,
            "artifacts": db_experiment.artifacts,
            "tags": db_experiment.tags,
            "notes": db_experiment.notes,
            "started_at": db_experiment.started_at,
            "completed_at": db_experiment.completed_at,
            "model_id": db_experiment.model_id,
            "dataset_id": db_experiment.dataset_id,
            "project_id": db_experiment.project_id,
            "created_at": db_experiment.created_at,
            "updated_at": db_experiment.updated_at,
            "duration_seconds": duration_seconds,
        }

        return experiment_dict

    @staticmethod
    def get_experiments_summary(
        db: Session,
        project_id: Optional[int] = None
    ) -> List[dict]:
        """Get summary of all experiments."""
        query = db.query(Experiment)

        if project_id is not None:
            query = query.filter(Experiment.project_id == project_id)

        experiments = query.order_by(Experiment.created_at.desc()).all()
        summaries = []

        for exp in experiments:
            summaries.append({
                "id": exp.id,
                "name": exp.name,
                "status": exp.status,
                "model_id": exp.model_id,
                "dataset_id": exp.dataset_id,
                "project_id": exp.project_id,
                "created_at": exp.created_at,
            })

        return summaries
