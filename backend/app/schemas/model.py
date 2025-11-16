"""
Pydantic schemas for MLModel.

Request/response schemas for model registry operations.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from app.models.model import ModelType, ModelStatus


# ============================================
# Base Schemas
# ============================================

class MLModelBase(BaseModel):
    """Base ML model schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    model_type: ModelType
    version: str = Field(..., max_length=50)


# ============================================
# Request Schemas
# ============================================

class MLModelCreate(MLModelBase):
    """Schema for creating a new ML model."""
    framework: Optional[str] = Field(None, max_length=50)
    hyperparameters: Optional[Dict[str, Any]] = None
    project_id: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "SAR RandomForest Model",
                "description": "Random forest classifier for activity prediction",
                "model_type": "drug_design_sar",
                "version": "1.0.0",
                "framework": "sklearn",
                "hyperparameters": {"n_estimators": 100, "max_depth": 20},
                "project_id": 1
            }
        }
    )


class MLModelUpdate(BaseModel):
    """Schema for updating ML model information."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ModelStatus] = None
    metrics: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ready",
                "metrics": {"accuracy": 0.92, "auc": 0.95}
            }
        }
    )


# ============================================
# Response Schemas
# ============================================

class MLModel(MLModelBase):
    """Schema for ML model response."""
    id: int
    status: ModelStatus
    file_path: Optional[str]
    framework: Optional[str]
    hyperparameters: Optional[Dict[str, Any]]
    metrics: Optional[Dict[str, Any]]
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MLModelSummary(BaseModel):
    """Minimal ML model schema for lists."""
    id: int
    name: str
    model_type: ModelType
    version: str
    status: ModelStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MLModelWithMetrics(MLModel):
    """ML model with detailed metrics."""
    experiment_count: int = 0

    model_config = ConfigDict(from_attributes=True)
