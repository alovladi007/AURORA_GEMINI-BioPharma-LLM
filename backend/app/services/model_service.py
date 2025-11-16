"""
ML Model service layer.

Handles ML model registry CRUD operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.model import MLModel
from app.schemas.model import MLModelCreate, MLModelUpdate


class MLModelService:
    """Service for ML model registry operations."""

    @staticmethod
    def get_model(db: Session, model_id: int) -> Optional[MLModel]:
        """Get ML model by ID."""
        return db.query(MLModel).filter(MLModel.id == model_id).first()

    @staticmethod
    def get_models(
        db: Session,
        project_id: Optional[int] = None,
        model_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[MLModel]:
        """Get all models with optional filtering."""
        query = db.query(MLModel)

        if project_id is not None:
            query = query.filter(MLModel.project_id == project_id)

        if model_type is not None:
            query = query.filter(MLModel.model_type == model_type)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_model(db: Session, model: MLModelCreate) -> MLModel:
        """Create a new ML model."""
        db_model = MLModel(
            name=model.name,
            description=model.description,
            model_type=model.model_type,
            version=model.version,
            framework=model.framework,
            architecture=model.architecture,
            hyperparameters=model.hyperparameters,
            training_metrics=model.training_metrics,
            model_path=model.model_path,
            artifact_path=model.artifact_path,
            metadata=model.metadata,
            project_id=model.project_id,
        )
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model

    @staticmethod
    def update_model(
        db: Session,
        model_id: int,
        model_update: MLModelUpdate
    ) -> Optional[MLModel]:
        """Update an existing ML model."""
        db_model = MLModelService.get_model(db, model_id)
        if not db_model:
            return None

        update_data = model_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_model, field, value)

        db.commit()
        db.refresh(db_model)
        return db_model

    @staticmethod
    def delete_model(db: Session, model_id: int) -> bool:
        """Delete an ML model."""
        db_model = MLModelService.get_model(db, model_id)
        if not db_model:
            return False

        db.delete(db_model)
        db.commit()
        return True

    @staticmethod
    def get_model_with_metrics(db: Session, model_id: int) -> Optional[dict]:
        """Get model with experiment count."""
        db_model = MLModelService.get_model(db, model_id)
        if not db_model:
            return None

        # Count experiments using this model
        from app.models.experiment import Experiment
        experiments_count = db.query(func.count(Experiment.id)).filter(
            Experiment.model_id == model_id
        ).scalar()

        model_dict = {
            "id": db_model.id,
            "name": db_model.name,
            "description": db_model.description,
            "model_type": db_model.model_type,
            "version": db_model.version,
            "framework": db_model.framework,
            "architecture": db_model.architecture,
            "hyperparameters": db_model.hyperparameters,
            "training_metrics": db_model.training_metrics,
            "model_path": db_model.model_path,
            "artifact_path": db_model.artifact_path,
            "metadata": db_model.metadata,
            "project_id": db_model.project_id,
            "created_at": db_model.created_at,
            "updated_at": db_model.updated_at,
            "experiments_count": experiments_count,
        }

        return model_dict

    @staticmethod
    def get_models_summary(
        db: Session,
        project_id: Optional[int] = None
    ) -> List[dict]:
        """Get summary of all models."""
        query = db.query(MLModel)

        if project_id is not None:
            query = query.filter(MLModel.project_id == project_id)

        models = query.all()
        summaries = []

        for model in models:
            summaries.append({
                "id": model.id,
                "name": model.name,
                "model_type": model.model_type,
                "version": model.version,
                "framework": model.framework,
                "project_id": model.project_id,
                "created_at": model.created_at,
            })

        return summaries
