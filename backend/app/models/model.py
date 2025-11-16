"""
ML Model registry for tracking trained models.

Stores metadata about trained models, their versions, and performance metrics.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON, Float
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ModelType(str, enum.Enum):
    """ML model type enumeration."""
    DRUG_DESIGN_GENERATOR = "drug_design_generator"
    DRUG_DESIGN_SAR = "drug_design_sar"
    DRUG_DESIGN_OPTIMIZER = "drug_design_optimizer"
    SAFETY_ADMET = "safety_admet"
    SAFETY_TOXICITY = "safety_toxicity"
    SAFETY_DDI = "safety_ddi"
    CLINICAL_RECRUITMENT = "clinical_recruitment"
    CLINICAL_SURVIVAL = "clinical_survival"
    CLINICAL_SAFETY = "clinical_safety"
    REPURPOSING_LINK_PREDICTION = "repurposing_link_prediction"
    REPURPOSING_MECHANISM = "repurposing_mechanism"
    GENERIC = "generic"


class ModelStatus(str, enum.Enum):
    """Model status enumeration."""
    TRAINING = "training"
    READY = "ready"
    FAILED = "failed"
    DEPRECATED = "deprecated"


class MLModel(Base):
    """
    ML Model registry for tracking trained models.

    Stores metadata about models including type, version, hyperparameters,
    metrics, and file paths to saved model artifacts.

    Attributes:
        id: Primary key
        name: Model name
        description: Model description
        model_type: Type of ML model
        status: Model status (training, ready, failed, deprecated)
        version: Model version string
        file_path: Path to model artifact in object storage
        hyperparameters: JSON of model hyperparameters
        metrics: JSON of evaluation metrics (accuracy, AUC, etc.)
        framework: ML framework used (pytorch, sklearn, etc.)
        project_id: Foreign key to project
        created_at: Model creation timestamp
        updated_at: Last update timestamp
        project: Relationship to Project
        experiments: Relationship to Experiment objects
    """
    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    model_type = Column(SQLEnum(ModelType), nullable=False)
    status = Column(SQLEnum(ModelStatus), default=ModelStatus.TRAINING, nullable=False)
    version = Column(String(50), nullable=False)

    # Model artifacts
    file_path = Column(String(512), nullable=True)
    framework = Column(String(50), nullable=True)  # pytorch, sklearn, tensorflow, etc.

    # Model configuration and results
    hyperparameters = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)

    # Ownership
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="models")
    experiments = relationship("Experiment", back_populates="model")

    def __repr__(self) -> str:
        return f"<MLModel(id={self.id}, name='{self.name}', type='{self.model_type}', status='{self.status}')>"
