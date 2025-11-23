"""
Integration tests for projects API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.models.user import User
from app.models.project import Project


class TestProjectsAPI:
    """Tests for /api/v1/projects endpoints."""

    def test_create_project(self, client: TestClient, auth_headers: dict):
        """Test creating a new project."""
        response = client.post(
            "/api/v1/projects/",
            json={
                "name": "New Test Project",
                "description": "A project created via API",
                "status": "active",
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Test Project"
        assert data["description"] == "A project created via API"
        assert data["status"] == "active"
        assert "id" in data

    def test_create_project_no_auth(self, client: TestClient):
        """Test creating project without authentication."""
        response = client.post(
            "/api/v1/projects/",
            json={
                "name": "Unauthorized Project",
                "status": "active",
            }
        )

        assert response.status_code == 403

    def test_list_projects(
        self,
        client: TestClient,
        auth_headers: dict,
        multiple_projects: list[Project]
    ):
        """Test listing user's projects."""
        response = client.get("/api/v1/projects/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == len(multiple_projects)

    def test_list_projects_filtered_by_status(
        self,
        client: TestClient,
        auth_headers: dict,
        multiple_projects: list[Project]
    ):
        """Test listing projects filtered by status."""
        response = client.get(
            "/api/v1/projects/?status=active",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(p["status"] == "active" for p in data)

    def test_get_project(
        self,
        client: TestClient,
        auth_headers: dict,
        test_project: Project
    ):
        """Test getting a specific project."""
        response = client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_project.id
        assert data["name"] == test_project.name

    def test_get_nonexistent_project(self, client: TestClient, auth_headers: dict):
        """Test getting a project that doesn't exist."""
        response = client.get("/api/v1/projects/99999", headers=auth_headers)

        assert response.status_code == 404

    def test_update_project(
        self,
        client: TestClient,
        auth_headers: dict,
        test_project: Project
    ):
        """Test updating a project."""
        response = client.put(
            f"/api/v1/projects/{test_project.id}",
            json={
                "name": "Updated Project Name",
                "status": "completed",
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Project Name"
        assert data["status"] == "completed"

    def test_delete_project(
        self,
        client: TestClient,
        auth_headers: dict,
        test_project: Project
    ):
        """Test deleting a project."""
        response = client.delete(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify project is deleted
        get_response = client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_get_project_stats(self, client: TestClient, auth_headers: dict):
        """Test getting project statistics."""
        response = client.get("/api/v1/projects/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_projects" in data
        assert "active_projects" in data
        assert "completed_projects" in data
        assert isinstance(data["total_projects"], int)
