"""
Dataset model for storing uploaded research data.

Handles molecular datasets, clinical trial data, and other inputs for ML models.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class DatasetType(str, enum.Enum):
    """Dataset type enumeration."""
    MOLECULAR = "molecular"  # SMILES, molecular properties
    CLINICAL = "clinical"    # Clinical trial data
    BIOACTIVITY = "bioactivity"  # Activity data (IC50, Ki, etc.)
    TOXICITY = "toxicity"    # Toxicity endpoints
    KNOWLEDGE_GRAPH = "knowledge_graph"  # Graph data for repurposing
    GENERIC = "generic"      # Other data types


class Dataset(Base):
    """
    Dataset model for uploaded research data.

    Stores metadata about datasets used in ML training and inference.
    Actual data is stored in object storage or database tables.

    Attributes:
        id: Primary key
        name: Dataset name
        description: Dataset description
        dataset_type: Type of dataset
        file_path: Path to dataset file in object storage
        file_format: File format (csv, parquet, json, etc.)
        schema: JSON schema describing dataset columns/structure
        row_count: Number of rows/records
        column_count: Number of columns/features
        project_id: Foreign key to project
        created_at: Upload timestamp
        updated_at: Last update timestamp
        project: Relationship to Project
    """
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    dataset_type = Column(SQLEnum(DatasetType), nullable=False)

    # File information
    file_path = Column(String(512), nullable=True)
    file_format = Column(String(50), nullable=True)  # csv, parquet, json, etc.

    # Metadata
    schema = Column(JSON, nullable=True)  # Column names and types
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)

    # Ownership
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="datasets")

    def __repr__(self) -> str:
        return f"<Dataset(id={self.id}, name='{self.name}', type='{self.dataset_type}')>"
