"""
Pydantic schemas for Experiment model.

Request/response schemas for experiment tracking operations.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


# ============================================
# Base Schemas
# ============================================

class ExperimentBase(BaseModel):
    """Base experiment schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


# ============================================
# Request Schemas
# ============================================

class ExperimentCreate(ExperimentBase):
    """Schema for creating a new experiment."""
    parameters: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    model_id: Optional[int] = None
    project_id: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "SAR Training Run #1",
                "description": "Initial training with default hyperparameters",
                "parameters": {
                    "learning_rate": 0.001,
                    "batch_size": 32,
                    "epochs": 100
                },
                "tags": ["baseline", "sar", "kinase"],
                "model_id": 1,
                "project_id": 1
            }
        }
    )


class ExperimentUpdate(BaseModel):
    """Schema for updating experiment information."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    artifacts: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "metrics": {"train_loss": 0.15, "val_accuracy": 0.89},
                "notes": "Good performance, consider reducing learning rate"
            }
        }
    )


# ============================================
# Response Schemas
# ============================================

class Experiment(ExperimentBase):
    """Schema for experiment response."""
    id: int
    parameters: Optional[Dict[str, Any]]
    metrics: Optional[Dict[str, Any]]
    artifacts: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    notes: Optional[str]
    model_id: Optional[int]
    project_id: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExperimentSummary(BaseModel):
    """Minimal experiment schema for lists."""
    id: int
    name: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExperimentWithDuration(Experiment):
    """Experiment with computed duration."""
    duration_seconds: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
