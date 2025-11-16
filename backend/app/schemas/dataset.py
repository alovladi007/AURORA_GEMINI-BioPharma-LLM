"""
Pydantic schemas for Dataset model.

Request/response schemas for dataset-related API endpoints.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from app.models.dataset import DatasetType


# ============================================
# Base Schemas
# ============================================

class DatasetBase(BaseModel):
    """Base dataset schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    dataset_type: DatasetType


# ============================================
# Request Schemas
# ============================================

class DatasetCreate(DatasetBase):
    """Schema for creating a new dataset."""
    file_format: Optional[str] = Field(None, max_length=50)
    project_id: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Kinase Inhibitor Activity Data",
                "description": "IC50 data for 500 kinase inhibitors",
                "dataset_type": "bioactivity",
                "file_format": "csv",
                "project_id": 1
            }
        }
    )


class DatasetUpdate(BaseModel):
    """Schema for updating dataset information."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    dataset_type: Optional[DatasetType] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Dataset Name",
                "description": "Updated description"
            }
        }
    )


class DatasetUpload(BaseModel):
    """Schema for dataset file upload metadata."""
    dataset_id: int
    file_size: int
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    schema: Optional[Dict[str, Any]] = None


# ============================================
# Response Schemas
# ============================================

class Dataset(DatasetBase):
    """Schema for dataset response."""
    id: int
    file_path: Optional[str]
    file_format: Optional[str]
    schema: Optional[Dict[str, Any]]
    row_count: Optional[int]
    column_count: Optional[int]
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetSummary(BaseModel):
    """Minimal dataset schema for lists."""
    id: int
    name: str
    dataset_type: DatasetType
    row_count: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetWithStats(Dataset):
    """Dataset with usage statistics."""
    used_in_experiments: int = 0

    model_config = ConfigDict(from_attributes=True)
