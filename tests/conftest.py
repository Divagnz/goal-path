"""
Test configuration and fixtures for GoalPath
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from src.goalpath.database import DatabaseManager, get_db
from src.goalpath.main import app


@pytest.fixture(scope="session")
def test_db_manager():
    """Create a test database manager with in-memory SQLite"""
    # Use in-memory SQLite for tests
    test_db_url = "sqlite:///:memory:"
    db_manager = DatabaseManager(test_db_url)

    # Create all tables
    db_manager.create_tables()

    yield db_manager

    # Cleanup is automatic with in-memory database


@pytest.fixture(scope="function")
def test_db_session(test_db_manager):
    """Create a test database session with automatic rollback"""
    session = test_db_manager.get_sync_session()

    yield session

    # Clean up by removing all data
    try:
        # Import only the models we know exist
        from src.goalpath.models import Goal, GoalProject, Project, Task, TaskDependency

        # Try to import extended models if they exist
        try:
            from src.goalpath.models.extended import (
                Issue,
                ProjectContext,
                Reminder,
                ScheduleEvent,
                TaskAttachment,
                TaskComment,
            )
            from src.goalpath.models import Sprint, SprintTask

            extended_models_available = True
        except ImportError:
            extended_models_available = False

        # Delete relationship tables first
        session.query(GoalProject).delete()
        session.query(TaskDependency).delete()
        if extended_models_available:
            session.query(SprintTask).delete()

        # Delete extended model data if available
        if extended_models_available:
            session.query(TaskComment).delete()
            session.query(TaskAttachment).delete()
            session.query(Reminder).delete()
            session.query(Issue).delete()
            session.query(ProjectContext).delete()
            session.query(ScheduleEvent).delete()
            session.query(Sprint).delete()

        # Delete main tables
        session.query(Task).delete()
        session.query(Goal).delete()
        session.query(Project).delete()

        # Force commit all deletions
        session.commit()
        
        # Verify cleanup worked
        remaining_projects = session.query(Project).count()
        if remaining_projects > 0:
            print(f"Warning: {remaining_projects} projects still exist after cleanup")
            
    except Exception as e:
        print(f"Cleanup error: {e}")
        session.rollback()
        # Force delete all projects as fallback
        try:
            session.query(Project).delete()
            session.commit()
        except Exception:
            session.rollback()
    finally:
        session.close()


@pytest.fixture(scope="function")
def test_client(test_db_session):
    """Create a test client with database dependency override"""

    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass  # Session cleanup handled by test_db_session fixture

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    # Clean up the override
    app.dependency_overrides.clear()


@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return {
        "name": "Test Project",
        "description": "A test project for unit testing",
        "status": "active",
        "priority": "medium",
        "start_date": "2025-01-01",
        "target_end_date": "2025-12-31",
    }


@pytest.fixture
def sample_task_data():
    """Sample task data for testing"""
    return {
        "title": "Test Task",
        "description": "A test task for unit testing",
        "task_type": "task",
        "status": "backlog",
        "priority": "medium",
        "estimated_hours": 8.0,
    }


@pytest.fixture
def sample_goal_data():
    """Sample goal data for testing"""
    return {
        "title": "Test Goal",
        "description": "A test goal for unit testing",
        "goal_type": "short_term",
        "status": "active",
        "progress_percentage": 0.0,
    }


class DatabaseTestHelper:
    """Helper class for database testing operations"""

    @staticmethod
    def create_test_project(session, **kwargs):
        """Create a test project with default or provided data"""
        from src.goalpath.models import Project

        # Generate unique name if not provided
        if "name" not in kwargs:
            unique_suffix = str(uuid.uuid4())[:8]
            kwargs["name"] = f"Test Project {unique_suffix}"

        default_data = {"description": "Test Description", "status": "active", "priority": "medium"}
        default_data.update(kwargs)

        project = Project(**default_data)
        session.add(project)
        session.commit()
        session.refresh(project)
        return project

    @staticmethod
    def create_test_task(session, project_id, **kwargs):
        """Create a test task with default or provided data"""
        from src.goalpath.models import Task

        # Generate unique title if not provided
        if "title" not in kwargs:
            unique_suffix = str(uuid.uuid4())[:8]
            kwargs["title"] = f"Test Task {unique_suffix}"

        default_data = {
            "project_id": project_id,
            "description": "Test Description",
            "task_type": "task",
            "status": "backlog",
            "priority": "medium",
        }
        default_data.update(kwargs)

        task = Task(**default_data)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def create_test_goal(session, **kwargs):
        """Create a test goal with default or provided data"""
        from src.goalpath.models import Goal

        # Generate unique title if not provided
        if "title" not in kwargs:
            unique_suffix = str(uuid.uuid4())[:8]
            kwargs["title"] = f"Test Goal {unique_suffix}"

        default_data = {
            "description": "Test Description",
            "goal_type": "short_term",
            "status": "active",
            "progress_percentage": 0.0,
        }
        default_data.update(kwargs)

        goal = Goal(**default_data)
        session.add(goal)
        session.commit()
        session.refresh(goal)
        return goal


# Make the helper available as a fixture
@pytest.fixture
def db_helper():
    """Database test helper fixture"""
    return DatabaseTestHelper
