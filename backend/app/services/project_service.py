"""
Project CRUD service.

Handles database operations for projects.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.project import Project, ProjectStatus
from app.models.dataset import Dataset
from app.models.model import MLModel
from app.models.experiment import Experiment
from app.models.job import Job
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service class for project CRUD operations."""

    @staticmethod
    def get_project(db: Session, project_id: int) -> Optional[Project]:
        """
        Get a single project by ID.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            Project object or None if not found
        """
        return db.query(Project).filter(Project.id == project_id).first()

    @staticmethod
    def get_projects(
        db: Session,
        user_id: Optional[int] = None,
        status: Optional[ProjectStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Project]:
        """
        Get list of projects with optional filtering.

        Args:
            db: Database session
            user_id: Filter by owner user ID
            status: Filter by project status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Project objects
        """
        query = db.query(Project)

        if user_id is not None:
            query = query.filter(Project.owner_id == user_id)

        if status is not None:
            query = query.filter(Project.status == status)

        return query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_project_with_counts(db: Session, project_id: int) -> Optional[dict]:
        """
        Get project with counts of related entities.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            Dictionary with project and counts or None
        """
        project = db.query(Project).filter(Project.id == project_id).first()

        if not project:
            return None

        # Count related entities
        dataset_count = db.query(func.count(Dataset.id)).filter(Dataset.project_id == project_id).scalar()
        model_count = db.query(func.count(MLModel.id)).filter(MLModel.project_id == project_id).scalar()
        experiment_count = db.query(func.count(Experiment.id)).filter(Experiment.project_id == project_id).scalar()
        job_count = db.query(func.count(Job.id)).filter(Job.project_id == project_id).scalar()

        return {
            "project": project,
            "dataset_count": dataset_count,
            "model_count": model_count,
            "experiment_count": experiment_count,
            "job_count": job_count,
        }

    @staticmethod
    def create_project(db: Session, project: ProjectCreate, user_id: int) -> Project:
        """
        Create a new project.

        Args:
            db: Database session
            project: Project creation schema
            user_id: Owner user ID

        Returns:
            Created Project object
        """
        db_project = Project(
            name=project.name,
            description=project.description,
            status=project.status,
            owner_id=user_id,
        )

        db.add(db_project)
        db.commit()
        db.refresh(db_project)

        return db_project

    @staticmethod
    def update_project(
        db: Session,
        project_id: int,
        project_update: ProjectUpdate,
    ) -> Optional[Project]:
        """
        Update an existing project.

        Args:
            db: Database session
            project_id: Project ID
            project_update: Project update schema

        Returns:
            Updated Project object or None if not found
        """
        db_project = db.query(Project).filter(Project.id == project_id).first()

        if not db_project:
            return None

        # Update only provided fields
        update_data = project_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)

        db.commit()
        db.refresh(db_project)

        return db_project

    @staticmethod
    def delete_project(db: Session, project_id: int) -> bool:
        """
        Delete a project.

        Args:
            db: Database session
            project_id: Project ID

        Returns:
            True if deleted, False if not found
        """
        db_project = db.query(Project).filter(Project.id == project_id).first()

        if not db_project:
            return False

        db.delete(db_project)
        db.commit()

        return True

    @staticmethod
    def user_owns_project(db: Session, project_id: int, user_id: int) -> bool:
        """
        Check if a user owns a project.

        Args:
            db: Database session
            project_id: Project ID
            user_id: User ID

        Returns:
            True if user owns the project
        """
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == user_id
        ).first()

        return project is not None

    @staticmethod
    def get_project_stats(db: Session, user_id: Optional[int] = None) -> dict:
        """
        Get project statistics.

        Args:
            db: Database session
            user_id: Optional user ID to filter by

        Returns:
            Dictionary with project statistics
        """
        query = db.query(Project)

        if user_id is not None:
            query = query.filter(Project.owner_id == user_id)

        total_projects = query.count()
        active_projects = query.filter(Project.status == ProjectStatus.ACTIVE).count()
        archived_projects = query.filter(Project.status == ProjectStatus.ARCHIVED).count()
        completed_projects = query.filter(Project.status == ProjectStatus.COMPLETED).count()

        return {
            "total": total_projects,
            "active": active_projects,
            "archived": archived_projects,
            "completed": completed_projects,
        }
