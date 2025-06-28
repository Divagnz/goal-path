#!/usr/bin/env python3
"""
GoalPath MCP Server

Exposes GoalPath functionality through direct database access via service layer.
Provides CRUD operations for projects, goals, epics, milestones, tasks, and issues.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp.server.fastmcp import FastMCP

# Import services
from goalpath.services import GoalService, ProjectService, TaskService, IssueService
from goalpath.database import DatabaseManager
from goalpath.schemas import (
    GoalCreate, GoalUpdate, ProjectCreate, ProjectUpdate, 
    TaskCreate, TaskUpdate, IssueCreate, IssueUpdate
)

# Get database URL from environment or use default SQLite
database_url = os.getenv("GOALPATH_DATABASE_URL", None)

# Initialize database manager
db_manager = DatabaseManager(database_url)

# Create FastMCP server
mcp = FastMCP("GoalPath")

# Project tools
@mcp.tool()
def list_projects(
    status: Optional[str] = None,
    priority: Optional[str] = None, 
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> Dict[str, Any]:
    """List all projects with optional filtering and pagination"""
    with db_manager.SessionLocal() as db:
        with ProjectService(db) as service:
            return service.list_projects_with_statistics(
                status=status, priority=priority, search=search, skip=skip, limit=limit
            )

@mcp.tool()
def get_project(project_id: str) -> Dict[str, Any]:
    """Get a specific project by ID with detailed statistics"""
    with db_manager.SessionLocal() as db:
        with ProjectService(db) as service:
            result = service.get_project_with_statistics(project_id)
            if not result:
                raise ValueError(f"Project with ID {project_id} not found")
            return result

@mcp.tool()
def create_project(
    name: str,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    start_date: Optional[str] = None,
    target_end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new project"""
    with db_manager.SessionLocal() as db:
        with ProjectService(db) as service:
            project_data = ProjectCreate(
                name=name,
                description=description,
                status=status,
                priority=priority,
                start_date=start_date,
                target_end_date=target_end_date
            )
            return service.create_project(project_data)

@mcp.tool()
def update_project(
    project_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    start_date: Optional[str] = None,
    target_end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Update an existing project"""
    with db_manager.SessionLocal() as db:
        with ProjectService(db) as service:
            update_data = ProjectUpdate(
                name=name,
                description=description,
                status=status,
                priority=priority,
                start_date=start_date,
                target_end_date=target_end_date
            )
            return service.update_project(project_id, update_data)

@mcp.tool()
def delete_project(project_id: str) -> Dict[str, str]:
    """Delete a project"""
    with db_manager.SessionLocal() as db:
        with ProjectService(db) as service:
            message = service.delete_project(project_id)
            return {"message": message}

@mcp.tool()
def get_project_statistics(project_id: str) -> Dict[str, Any]:
    """Get comprehensive statistics for a project"""
    with db_manager.SessionLocal() as db:
        with ProjectService(db) as service:
            return service.calculate_project_statistics(project_id)

# Goal tools
@mcp.tool()
def list_goals(
    status: Optional[str] = None,
    goal_type: Optional[str] = None,
    parent_goal_id: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """List goals with optional filtering and pagination"""
    with db_manager.SessionLocal() as db:
        with GoalService(db) as service:
            return service.list_goals_with_progress(
                status=status, goal_type=goal_type, parent_goal_id=parent_goal_id,
                search=search, page=page, size=size
            )

@mcp.tool()
def get_goal(goal_id: str) -> Dict[str, Any]:
    """Get a specific goal by ID with calculated progress"""
    with db_manager.SessionLocal() as db:
        with GoalService(db) as service:
            result = service.get_goal_with_progress(goal_id)
            if not result:
                raise ValueError(f"Goal with ID {goal_id} not found")
            return result

@mcp.tool()
def create_goal(
    title: str,
    description: Optional[str] = None,
    goal_type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    parent_goal_id: Optional[str] = None,
    target_date: Optional[str] = None,
    progress_percentage: Optional[float] = None
) -> Dict[str, Any]:
    """Create a new goal"""
    with db_manager.SessionLocal() as db:
        with GoalService(db) as service:
            goal_data = GoalCreate(
                title=title,
                description=description,
                goal_type=goal_type,
                status=status,
                priority=priority,
                parent_goal_id=parent_goal_id,
                target_date=target_date,
                progress_percentage=progress_percentage
            )
            return service.create_goal(goal_data)

@mcp.tool()
def update_goal(
    goal_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    goal_type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    parent_goal_id: Optional[str] = None,
    target_date: Optional[str] = None,
    progress_percentage: Optional[float] = None
) -> Dict[str, Any]:
    """Update an existing goal"""
    with db_manager.SessionLocal() as db:
        with GoalService(db) as service:
            update_data = GoalUpdate(
                title=title,
                description=description,
                goal_type=goal_type,
                status=status,
                priority=priority,
                parent_goal_id=parent_goal_id,
                target_date=target_date,
                progress_percentage=progress_percentage
            )
            return service.update_goal(goal_id, update_data)

@mcp.tool()
def delete_goal(goal_id: str, cascade: bool = False) -> Dict[str, str]:
    """Delete a goal"""
    with db_manager.SessionLocal() as db:
        with GoalService(db) as service:
            message = service.delete_goal(goal_id, cascade)
            return {"message": message}

@mcp.tool()
def get_goal_hierarchy(goal_id: str) -> Dict[str, Any]:
    """Get complete goal hierarchy (ancestors and descendants)"""
    with db_manager.SessionLocal() as db:
        with GoalService(db) as service:
            return service.get_goal_hierarchy(goal_id)

@mcp.tool()
def link_project_to_goal(goal_id: str, project_id: str, weight: float = 1.0) -> Dict[str, str]:
    """Link a project to a goal with weight for progress calculation"""
    with db_manager.SessionLocal() as db:
        with GoalService(db) as service:
            message = service.link_project_to_goal(goal_id, project_id, weight)
            return {"message": message}

# Task tools
@mcp.tool()
def list_tasks(
    project_id: Optional[str] = None,
    milestone_id: Optional[str] = None,
    epic_id: Optional[str] = None,
    parent_task_id: Optional[str] = None,
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    assigned_to: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """List tasks with extensive filtering and pagination"""
    with db_manager.SessionLocal() as db:
        with TaskService(db) as service:
            return service.list_tasks_with_filters(
                project_id=project_id, milestone_id=milestone_id, epic_id=epic_id,
                parent_task_id=parent_task_id, status=status, task_type=task_type,
                assigned_to=assigned_to, search=search, skip=skip, limit=limit
            )

@mcp.tool()
def get_task(task_id: str) -> Dict[str, Any]:
    """Get a specific task by ID with hierarchy information"""
    with db_manager.SessionLocal() as db:
        with TaskService(db) as service:
            result = service.get_task_with_details(task_id)
            if not result:
                raise ValueError(f"Task with ID {task_id} not found")
            return result

@mcp.tool()
def create_task(
    title: str,
    description: Optional[str] = None,
    project_id: Optional[str] = None,
    milestone_id: Optional[str] = None,
    epic_id: Optional[str] = None,
    parent_task_id: Optional[str] = None,
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    due_date: Optional[str] = None,
    estimated_hours: Optional[float] = None,
    actual_hours: Optional[float] = None
) -> Dict[str, Any]:
    """Create a new task"""
    with db_manager.SessionLocal() as db:
        with TaskService(db) as service:
            task_data = TaskCreate(
                title=title,
                description=description,
                project_id=project_id,
                parent_task_id=parent_task_id,
                epic_id=epic_id,
                milestone_id=milestone_id,
                status=status,
                task_type=task_type,
                priority=priority,
                assigned_to=assigned_to,
                due_date=due_date,
                estimated_hours=estimated_hours,
                actual_hours=actual_hours
            )
            return service.create_task(task_data)

@mcp.tool()
def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    due_date: Optional[str] = None,
    estimated_hours: Optional[float] = None,
    actual_hours: Optional[float] = None
) -> Dict[str, Any]:
    """Update an existing task"""
    with db_manager.SessionLocal() as db:
        with TaskService(db) as service:
            update_data = TaskUpdate(
                title=title,
                description=description,
                status=status,
                task_type=task_type,
                priority=priority,
                assigned_to=assigned_to,
                due_date=due_date,
                estimated_hours=estimated_hours,
                actual_hours=actual_hours
            )
            return service.update_task(task_id, update_data)

@mcp.tool()
def delete_task(task_id: str, handle_subtasks: str = "cascade") -> Dict[str, str]:
    """Delete a task"""
    with db_manager.SessionLocal() as db:
        with TaskService(db) as service:
            message = service.delete_task(task_id, handle_subtasks)
            return {"message": message}

@mcp.tool()
def update_task_status(task_id: str, status: str) -> Dict[str, Any]:
    """Quick status update for a task"""
    with db_manager.SessionLocal() as db:
        with TaskService(db) as service:
            return service.update_task_status(task_id, status)

@mcp.tool()
def get_task_subtasks(task_id: str) -> List[Dict[str, Any]]:
    """Get all subtasks for a specific task"""
    with db_manager.SessionLocal() as db:
        with TaskService(db) as service:
            return service.get_task_subtasks(task_id)

# Issue tools
@mcp.tool()
def list_issues(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    issue_type: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """List issues with optional filtering"""
    with db_manager.SessionLocal() as db:
        with IssueService(db) as service:
            return service.list_issues_with_filters(
                project_id=project_id, status=status, issue_type=issue_type,
                priority=priority, assignee=assignee, skip=skip, limit=limit
            )

@mcp.tool()
def get_issue(issue_id: str) -> Dict[str, Any]:
    """Get a specific issue by ID"""
    with db_manager.SessionLocal() as db:
        with IssueService(db) as service:
            result = service.get_issue_with_details(issue_id)
            if not result:
                raise ValueError(f"Issue with ID {issue_id} not found")
            return result

@mcp.tool()
def create_issue(
    title: str,
    project_id: str,
    description: Optional[str] = None,
    issue_type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    reporter: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new issue"""
    with db_manager.SessionLocal() as db:
        with IssueService(db) as service:
            issue_data = IssueCreate(
                title=title,
                description=description,
                project_id=project_id,
                issue_type=issue_type,
                status=status,
                priority=priority,
                assignee=assignee,
                reporter=reporter or "mcp_user"
            )
            return service.create_issue(issue_data)

@mcp.tool()
def update_issue(
    issue_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    issue_type: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None
) -> Dict[str, Any]:
    """Update an existing issue"""
    with db_manager.SessionLocal() as db:
        with IssueService(db) as service:
            update_data = IssueUpdate(
                title=title,
                description=description,
                issue_type=issue_type,
                status=status,
                priority=priority,
                assignee=assignee
            )
            return service.update_issue(issue_id, update_data)

@mcp.tool()
def delete_issue(issue_id: str) -> Dict[str, str]:
    """Delete an issue"""
    with db_manager.SessionLocal() as db:
        with IssueService(db) as service:
            message = service.delete_issue(issue_id)
            return {"message": message}

@mcp.tool()
def promote_issue_to_task(
    issue_id: str,
    task_title: Optional[str] = None,
    epic_id: Optional[str] = None,
    milestone_id: Optional[str] = None
) -> Dict[str, Any]:
    """Promote an issue to a task with epic/milestone assignment"""
    with db_manager.SessionLocal() as db:
        with IssueService(db) as service:
            return service.promote_issue_to_task(issue_id, task_title, epic_id, milestone_id)

if __name__ == "__main__":
    mcp.run()