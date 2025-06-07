"""
Tests for database-backed Projects API endpoints
"""

import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient

from src.goalpath.init_db import DatabaseInitializer


class TestProjectsAPI:
    """Test the database-backed Projects API"""
    
    def test_list_projects_empty(self, test_client):
        """Test listing projects when database is empty"""
        response = test_client.get("/api/projects/")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_projects_with_data(self, test_client, test_db_session):
        """Test listing projects with sample data"""
        # Create sample data
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        DatabaseInitializer.create_sample_tasks(test_db_session, projects)
        
        response = test_client.get("/api/projects/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        
        # Check project structure
        project = data[0]
        assert "id" in project
        assert "name" in project
        assert "description" in project
        assert "status" in project
        assert "priority" in project
        assert "total_tasks" in project
        assert "completed_tasks" in project
        assert "completion_percentage" in project
        
        # Check specific projects exist
        project_names = [p["name"] for p in data]
        assert "Website Redesign" in project_names
        assert "Mobile App Development" in project_names
    
    def test_list_projects_with_filters(self, test_client, test_db_session):
        """Test listing projects with filters"""
        # Create sample data
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        DatabaseInitializer.create_sample_tasks(test_db_session, projects)
        
        # Test status filter
        response = test_client.get("/api/projects/?status=active")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # 3 active projects
        for project in data:
            assert project["status"] == "active"
        
        # Test priority filter
        response = test_client.get("/api/projects/?priority=high")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1  # 1 high priority project
        assert data[0]["priority"] == "high"
        
        # Test search filter
        response = test_client.get("/api/projects/?search=website")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Website" in data[0]["name"]
        
        # Test combined filters
        response = test_client.get("/api/projects/?status=active&priority=critical")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "active"
        assert data[0]["priority"] == "critical"
    
    def test_list_projects_pagination(self, test_client, test_db_session):
        """Test project listing with pagination"""
        # Create sample data
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        
        # Test page size
        response = test_client.get("/api/projects/?size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Test page 2
        response = test_client.get("/api/projects/?page=2&size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Test page beyond data
        response = test_client.get("/api/projects/?page=10&size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_get_project_success(self, test_client, test_db_session):
        """Test getting a specific project"""
        # Create sample data
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        DatabaseInitializer.create_sample_tasks(test_db_session, projects)
        
        project_id = projects[0].id
        
        response = test_client.get(f"/api/projects/{project_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == projects[0].name
        assert "total_tasks" in data
        assert "completion_percentage" in data
    
    def test_get_project_not_found(self, test_client):
        """Test getting a non-existent project"""
        response = test_client.get("/api/projects/non-existent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_create_project_success(self, test_client):
        """Test creating a new project"""
        project_data = {
            "name": "New Test Project",
            "description": "A test project created via API",
            "status": "active",
            "priority": "medium",
            "start_date": "2025-01-01",
            "target_end_date": "2025-12-31"
        }
        
        response = test_client.post("/api/projects/", json=project_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == project_data["name"]
        assert data["description"] == project_data["description"]
        assert data["status"] == project_data["status"]
        assert data["priority"] == project_data["priority"]
        assert "id" in data
        assert data["total_tasks"] == 0
        assert data["completion_percentage"] == 0.0
    
    def test_create_project_validation_error(self, test_client):
        """Test creating a project with invalid data"""
        # Missing required fields
        project_data = {
            "description": "Missing name field"
        }
        
        response = test_client.post("/api/projects/", json=project_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_project_duplicate_name(self, test_client, test_db_session):
        """Test creating a project with duplicate name"""
        # Create initial project
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        existing_name = projects[0].name
        
        # Try to create project with same name
        project_data = {
            "name": existing_name,
            "description": "Duplicate name test",
            "status": "active",
            "priority": "medium"
        }
        
        response = test_client.post("/api/projects/", json=project_data)
        
        assert response.status_code == 400  # Integrity error
        assert "failed" in response.json()["detail"].lower()
    
    def test_update_project_success(self, test_client, test_db_session):
        """Test updating an existing project"""
        # Create sample data
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        project_id = projects[0].id
        
        update_data = {
            "name": "Updated Project Name",
            "priority": "critical",
            "status": "paused"
        }
        
        response = test_client.put(f"/api/projects/{project_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == update_data["name"]
        assert data["priority"] == update_data["priority"]
        assert data["status"] == update_data["status"]
        # Description should remain unchanged
        assert data["description"] == projects[0].description
    
    def test_update_project_not_found(self, test_client):
        """Test updating a non-existent project"""
        update_data = {
            "name": "Updated Name"
        }
        
        response = test_client.put("/api/projects/non-existent-id", json=update_data)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_project_partial(self, test_client, test_db_session):
        """Test partial project update"""
        # Create sample data
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        project_id = projects[0].id
        original_name = projects[0].name
        
        # Update only priority
        update_data = {
            "priority": "low"
        }
        
        response = test_client.put(f"/api/projects/{project_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "low"
        assert data["name"] == original_name  # Should remain unchanged
    
    def test_delete_project_success(self, test_client, test_db_session):
        """Test deleting a project"""
        # Create sample data
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        project_id = projects[0].id
        project_name = projects[0].name
        
        response = test_client.delete(f"/api/projects/{project_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]
        assert project_name in data["message"]
        
        # Verify project is actually deleted
        get_response = test_client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 404
    
    def test_delete_project_not_found(self, test_client):
        """Test deleting a non-existent project"""
        response = test_client.delete("/api/projects/non-existent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_project_statistics_success(self, test_client, test_db_session):
        """Test getting project statistics"""
        # Create sample data
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        DatabaseInitializer.create_sample_tasks(test_db_session, projects)
        
        project_id = projects[0].id
        
        response = test_client.get(f"/api/projects/{project_id}/statistics")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert data["project_id"] == project_id
        assert "project_name" in data
        assert "total_tasks" in data
        assert "completed_tasks" in data
        assert "completion_percentage" in data
        assert "estimated_hours" in data
        assert "actual_hours" in data
        assert "velocity" in data
        assert "timeline" in data
        assert "task_breakdown" in data
        
        # Check velocity structure
        assert "tasks_per_week" in data["velocity"]
        assert "hours_per_week" in data["velocity"]
        
        # Check timeline structure
        timeline = data["timeline"]
        assert "start_date" in timeline
        assert "target_end_date" in timeline
        assert "is_overdue" in timeline
    
    def test_project_statistics_not_found(self, test_client):
        """Test getting statistics for non-existent project"""
        response = test_client.get("/api/projects/non-existent-id/statistics")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_project_with_tasks_completion_calculation(self, test_client, test_db_session):
        """Test that project completion percentage is calculated correctly"""
        # Create a project
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        DatabaseInitializer.create_sample_tasks(test_db_session, projects)
        
        # Find a project with tasks
        website_project = next(p for p in projects if p.name == "Website Redesign")
        
        response = test_client.get(f"/api/projects/{website_project.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have tasks and realistic completion percentage
        assert data["total_tasks"] > 0
        assert 0 <= data["completion_percentage"] <= 100
        
        # If there are completed tasks, completion should be > 0
        if data["completed_tasks"] > 0:
            assert data["completion_percentage"] > 0
