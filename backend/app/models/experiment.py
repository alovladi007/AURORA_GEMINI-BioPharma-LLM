"""
Experiment model for tracking ML training runs.

Records detailed information about model training experiments including
parameters, metrics, and results for reproducibility.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class Experiment(Base):
    """
    Experiment model for tracking ML training runs.

    An experiment represents a single training run with specific hyperparameters,
    dataset splits, and evaluation metrics. Enables experiment tracking and
    comparison similar to MLflow or Weights & Biases.

    Attributes:
        id: Primary key
        name: Experiment name
        description: Experiment description
        parameters: JSON of all experiment parameters (hyperparams, seed, etc.)
        metrics: JSON of evaluation metrics over time
        artifacts: JSON of paths to generated artifacts (plots, checkpoints, etc.)
        tags: JSON of experiment tags for filtering
        notes: Free-form notes about the experiment
        model_id: Foreign key to the model being trained
        project_id: Foreign key to project
        started_at: Experiment start timestamp
        completed_at: Experiment completion timestamp
        created_at: Record creation timestamp
        updated_at: Last update timestamp
        model: Relationship to MLModel
        project: Relationship to Project
    """
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Experiment details
    parameters = Column(JSON, nullable=True)  # Hyperparameters, config, etc.
    metrics = Column(JSON, nullable=True)     # Training/validation metrics
    artifacts = Column(JSON, nullable=True)    # Paths to plots, checkpoints, etc.
    tags = Column(JSON, nullable=True)         # Tags for categorization

    notes = Column(Text, nullable=True)        # Free-form notes

    # Relationships
    model_id = Column(Integer, ForeignKey("ml_models.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    model = relationship("MLModel", back_populates="experiments")
    project = relationship("Project", back_populates="experiments")

    def __repr__(self) -> str:
        return f"<Experiment(id={self.id}, name='{self.name}')>"

    @property
    def duration(self) -> float | None:
        """Calculate experiment duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
