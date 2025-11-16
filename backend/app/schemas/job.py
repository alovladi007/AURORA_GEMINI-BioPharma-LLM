"""
Pydantic schemas for Job model.

Request/response schemas for async job tracking operations.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from app.models.job import JobType, JobStatus


# ============================================
# Base Schemas
# ============================================

class JobBase(BaseModel):
    """Base job schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    job_type: JobType


# ============================================
# Request Schemas
# ============================================

class JobCreate(JobBase):
    """Schema for creating a new job."""
    parameters: Optional[Dict[str, Any]] = None
    project_id: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Train SAR Model",
                "description": "Training random forest on kinase data",
                "job_type": "model_training",
                "parameters": {"dataset_id": 1, "model_id": 1},
                "project_id": 1
            }
        }
    )


class JobUpdate(BaseModel):
    """Schema for updating job information."""
    status: Optional[JobStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    logs: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "completed",
                "progress": 100,
                "result": {"accuracy": 0.92, "training_time": 120.5}
            }
        }
    )


# ============================================
# Response Schemas
# ============================================

class Job(JobBase):
    """Schema for job response."""
    id: int
    status: JobStatus
    task_id: Optional[str]
    progress: int
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    logs: Optional[str]
    parameters: Optional[Dict[str, Any]]
    project_id: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobSummary(BaseModel):
    """Minimal job schema for lists."""
    id: int
    name: str
    job_type: JobType
    status: JobStatus
    progress: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobWithDuration(Job):
    """Job with computed duration."""
    duration_seconds: Optional[float] = None
    is_terminal: bool = False

    model_config = ConfigDict(from_attributes=True)
