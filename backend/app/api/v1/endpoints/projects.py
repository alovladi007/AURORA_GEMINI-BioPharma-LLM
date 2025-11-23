"""
Project API endpoints.

Provides CRUD operations for managing pharmaceutical research projects.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.project_service import ProjectService
from app.schemas.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectWithCounts,
    ProjectSummary,
)
from app.models.project import ProjectStatus
from app.api.deps import get_current_user_id

router = APIRouter()


@router.get("/", response_model=List[Project])
def list_projects(
    status: ProjectStatus = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    List all projects for the current user.

    **Query Parameters:**
    - **status**: Filter by project status (active, archived, completed)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 100)

    **Returns:**
    - List of projects
    """
    projects = ProjectService.get_projects(
        db=db,
        user_id=user_id,
        status=status,
        skip=skip,
        limit=min(limit, 100),
    )
    return projects


@router.get("/stats")
def get_project_stats(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get project statistics for the current user.

    **Returns:**
    - Project counts by status (total, active, archived, completed)
    """
    stats = ProjectService.get_project_stats(db=db, user_id=user_id)
    return stats


@router.get("/{project_id}", response_model=ProjectWithCounts)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get a specific project by ID with related entity counts.

    **Path Parameters:**
    - **project_id**: Project ID

    **Returns:**
    - Project details with counts of datasets, models, experiments, and jobs

    **Raises:**
    - **404**: Project not found
    - **403**: User does not own this project
    """
    # Check ownership
    if not ProjectService.user_owns_project(db=db, project_id=project_id, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this project"
        )

    project_data = ProjectService.get_project_with_counts(db=db, project_id=project_id)

    if not project_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    # Convert to response schema
    project = project_data["project"]
    return ProjectWithCounts(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        owner_id=project.owner_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        dataset_count=project_data["dataset_count"],
        model_count=project_data["model_count"],
        experiment_count=project_data["experiment_count"],
        job_count=project_data["job_count"],
    )


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create a new project.

    **Request Body:**
    - **name**: Project name (required)
    - **description**: Project description (optional)
    - **status**: Project status (default: active)

    **Returns:**
    - Created project

    **Example:**
    ```json
    {
        "name": "Kinase Inhibitor Discovery",
        "description": "Discovery of novel kinase inhibitors for oncology",
        "status": "active"
    }
    ```
    """
    db_project = ProjectService.create_project(db=db, project=project, user_id=user_id)
    return db_project


@router.put("/{project_id}", response_model=Project)
def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update an existing project.

    **Path Parameters:**
    - **project_id**: Project ID

    **Request Body:**
    - **name**: New project name (optional)
    - **description**: New description (optional)
    - **status**: New status (optional)

    **Returns:**
    - Updated project

    **Raises:**
    - **404**: Project not found
    - **403**: User does not own this project
    """
    # Check ownership
    if not ProjectService.user_owns_project(db=db, project_id=project_id, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this project"
        )

    db_project = ProjectService.update_project(db=db, project_id=project_id, project_update=project)

    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    return db_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete a project.

    **Path Parameters:**
    - **project_id**: Project ID

    **Returns:**
    - 204 No Content on success

    **Raises:**
    - **404**: Project not found
    - **403**: User does not own this project

    **Warning:**
    - This will cascade delete all related datasets, models, experiments, and jobs
    """
    # Check ownership
    if not ProjectService.user_owns_project(db=db, project_id=project_id, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this project"
        )

    deleted = ProjectService.delete_project(db=db, project_id=project_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    return None
