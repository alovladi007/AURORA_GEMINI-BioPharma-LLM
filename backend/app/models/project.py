"""
Project model for organizing research work.

Projects group together datasets, models, experiments, and results.
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    """Project status enumeration."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"


class Project(Base):
    """
    Project model for organizing pharmaceutical research.

    A project groups datasets, models, experiments, and jobs for a specific
    research objective (e.g., "Kinase Inhibitor Discovery", "COVID-19 Repurposing").

    Attributes:
        id: Primary key
        name: Project name
        description: Detailed project description
        status: Project status (active, archived, completed)
        owner_id: Foreign key to user who owns the project
        created_at: Project creation timestamp
        updated_at: Last update timestamp
        owner: Relationship to User
        datasets: Relationship to Dataset objects
        models: Relationship to MLModel objects
        experiments: Relationship to Experiment objects
        jobs: Relationship to Job objects
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)

    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="projects")
    datasets = relationship("Dataset", back_populates="project", cascade="all, delete-orphan")
    models = relationship("MLModel", back_populates="project", cascade="all, delete-orphan")
    experiments = relationship("Experiment", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"
