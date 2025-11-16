"""
Job model for tracking asynchronous background tasks.

Tracks Celery task execution for ML training, inference, and data processing.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class JobStatus(str, enum.Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, enum.Enum):
    """Job type enumeration."""
    MODEL_TRAINING = "model_training"
    MODEL_INFERENCE = "model_inference"
    DATA_PROCESSING = "data_processing"
    DATASET_UPLOAD = "dataset_upload"
    REPORT_GENERATION = "report_generation"
    GENERIC = "generic"


class Job(Base):
    """
    Job model for tracking asynchronous background tasks.

    Tracks Celery task execution with status, progress, and results.
    Links to Celery task_id for real-time monitoring.

    Attributes:
        id: Primary key
        name: Job name
        description: Job description
        job_type: Type of job
        status: Job status (pending, running, completed, failed, cancelled)
        task_id: Celery task ID for monitoring
        progress: Progress percentage (0-100)
        result: JSON of job result data
        error: Error message if job failed
        logs: Text logs from job execution
        parameters: JSON of job input parameters
        project_id: Foreign key to project
        started_at: Job start timestamp
        completed_at: Job completion timestamp
        created_at: Record creation timestamp
        updated_at: Last update timestamp
        project: Relationship to Project
    """
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    job_type = Column(SQLEnum(JobType), nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)

    # Celery task tracking
    task_id = Column(String(255), unique=True, index=True, nullable=True)
    progress = Column(Integer, default=0, nullable=False)  # 0-100

    # Results and errors
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    logs = Column(Text, nullable=True)

    # Job configuration
    parameters = Column(JSON, nullable=True)

    # Ownership
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="jobs")

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, name='{self.name}', status='{self.status}')>"

    @property
    def duration(self) -> float | None:
        """Calculate job duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def is_terminal(self) -> bool:
        """Check if job is in a terminal state."""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
