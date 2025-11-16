"""
Pydantic schemas for Project model.

Request/response schemas for project-related API endpoints.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.project import ProjectStatus


# ============================================
# Base Schemas
# ============================================

class ProjectBase(BaseModel):
    """Base project schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.ACTIVE


# ============================================
# Request Schemas
# ============================================

class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Kinase Inhibitor Discovery",
                "description": "Discovery of novel kinase inhibitors for oncology targets",
                "status": "active"
            }
        }
    )


class ProjectUpdate(BaseModel):
    """Schema for updating project information."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Kinase Inhibitor Discovery - Phase 2",
                "status": "active"
            }
        }
    )


# ============================================
# Response Schemas
# ============================================

class Project(ProjectBase):
    """Schema for project response."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectWithCounts(Project):
    """Schema for project response with related entity counts."""
    dataset_count: int = 0
    model_count: int = 0
    experiment_count: int = 0
    job_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ProjectSummary(BaseModel):
    """Minimal project schema for lists."""
    id: int
    name: str
    status: ProjectStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
