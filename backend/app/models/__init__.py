"""
Database models for Pharma AI Platform.

SQLAlchemy ORM models for all entities.
"""

# Import all models here so they're registered with SQLAlchemy Base
# This is required for alembic autogenerate and create_all()

from app.models.user import User, UserRole
from app.models.project import Project, ProjectStatus
from app.models.dataset import Dataset, DatasetType
from app.models.model import MLModel, ModelType, ModelStatus
from app.models.experiment import Experiment
from app.models.job import Job, JobStatus, JobType

__all__ = [
    # Models
    "User",
    "Project",
    "Dataset",
    "MLModel",
    "Experiment",
    "Job",
    # Enums
    "UserRole",
    "ProjectStatus",
    "DatasetType",
    "ModelType",
    "ModelStatus",
    "JobStatus",
    "JobType",
]
