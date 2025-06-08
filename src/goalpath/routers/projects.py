"""
Projects API Router - Database Implementation
Full CRUD operations for projects with statistics and filtering
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..db_utils import QueryUtils, TransactionManager
from ..models import Project
from ..schemas import (
    MessageResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectResponse], summary="List all projects")
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
) -> List[ProjectResponse]:
    """
    Get all projects with optional filtering and pagination.

    **Database Implementation**: Queries projects with calculated statistics.
    """

    try:
        # Use QueryUtils for database operations with statistics
        projects_data = QueryUtils.get_projects_with_stats(
            db=db, status=status, priority=priority, search=search, page=page, size=size
        )

        return [ProjectResponse(**project) for project in projects_data]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving projects: {str(e)}")


@router.get("/{project_id}", response_model=ProjectResponse, summary="Get project by ID")
async def get_project(project_id: str, db: Session = Depends(get_db)) -> ProjectResponse:
    """
    Get a specific project by ID with detailed statistics.

    **Database Implementation**: Retrieves project with calculated stats.
    """

    try:
        project_data = QueryUtils.get_project_with_stats(db, project_id)

        if not project_data:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

        return ProjectResponse(**project_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving project: {str(e)}")


@router.post("/", response_model=ProjectResponse, status_code=201, summary="Create new project")
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)) -> ProjectResponse:
    """
    Create a new project.

    **Database Implementation**: Creates project in database with validation.
    """

    try:
        with TransactionManager(db) as db_session:
            # Create new project instance
            project_data = project.model_dump()

            # Add created_by if not provided (would come from auth in real app)
            if "created_by" not in project_data or not project_data["created_by"]:
                project_data["created_by"] = "system"

            new_project = Project(**project_data)
            db_session.add(new_project)
            db_session.commit()
            db_session.refresh(new_project)

            # Get project with statistics
            project_with_stats = QueryUtils.get_project_with_stats(db_session, new_project.id)

            return ProjectResponse(**project_with_stats)

    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Project creation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")


@router.put("/{project_id}", response_model=ProjectResponse, summary="Update project")
async def update_project(
    project_id: str, project_update: ProjectUpdate, db: Session = Depends(get_db)
) -> ProjectResponse:
    """
    Update an existing project.

    **Database Implementation**: Updates project in database with validation.
    """

    try:
        with TransactionManager(db) as db_session:
            # Find existing project
            project = db_session.query(Project).filter(Project.id == project_id).first()

            if not project:
                raise HTTPException(
                    status_code=404, detail=f"Project with ID {project_id} not found"
                )

            # Update fields from request
            update_data = project_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(project, field, value)

            db_session.commit()
            db_session.refresh(project)

            # Get project with updated statistics
            project_with_stats = QueryUtils.get_project_with_stats(db_session, project.id)

            return ProjectResponse(**project_with_stats)

    except HTTPException:
        raise
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Project update failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")


@router.delete("/{project_id}", response_model=MessageResponse, summary="Delete project")
async def delete_project(project_id: str, db: Session = Depends(get_db)) -> MessageResponse:
    """
    Delete a project.

    **Database Implementation**: Deletes project with cascade handling.
    """

    try:
        with TransactionManager(db) as db_session:
            # Find existing project
            project = db_session.query(Project).filter(Project.id == project_id).first()

            if not project:
                raise HTTPException(
                    status_code=404, detail=f"Project with ID {project_id} not found"
                )

            project_name = project.name

            # Delete project (cascade will handle related entities)
            db_session.delete(project)
            db_session.commit()

            return MessageResponse(message=f"Project '{project_name}' deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting project: {str(e)}")


@router.get("/{project_id}/statistics", summary="Get project statistics")
async def get_project_statistics(project_id: str, db: Session = Depends(get_db)) -> dict:
    """
    Get detailed statistics for a project.

    **Database Implementation**: Calculates real statistics from database.
    """

    try:
        # First verify project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

        # Get detailed project statistics
        project_stats = QueryUtils.get_project_with_stats(db, project_id)

        # Calculate additional statistics
        from sqlalchemy import func

        from ..models import Task

        # Get task statistics by status
        task_stats = (
            db.query(
                Task.status,
                func.count(Task.id).label("count"),
                func.coalesce(func.sum(Task.estimated_hours), 0).label("estimated_hours"),
                func.coalesce(func.sum(Task.actual_hours), 0).label("actual_hours"),
            )
            .filter(Task.project_id == project_id)
            .group_by(Task.status)
            .all()
        )

        # Calculate time-based statistics
        total_estimated_hours = sum(float(stat.estimated_hours or 0) for stat in task_stats)
        total_actual_hours = sum(float(stat.actual_hours or 0) for stat in task_stats)

        # Calculate project timeline
        days_since_start = None
        days_until_deadline = None

        if project.start_date:
            days_since_start = (date.today() - project.start_date).days

        if project.target_end_date:
            days_until_deadline = (project.target_end_date - date.today()).days

        # Build comprehensive statistics response
        statistics = {
            "project_id": project_id,
            "project_name": project.name,
            "total_tasks": project_stats["total_tasks"],
            "completed_tasks": project_stats["completed_tasks"],
            "in_progress_tasks": project_stats["in_progress_tasks"],
            "blocked_tasks": project_stats["blocked_tasks"],
            "completion_percentage": project_stats["completion_percentage"],
            "estimated_hours": total_estimated_hours,
            "actual_hours": total_actual_hours,
            "remaining_hours": max(0, total_estimated_hours - total_actual_hours),
            "days_since_start": days_since_start,
            "days_until_deadline": days_until_deadline,
            "velocity": {
                "tasks_per_week": round(
                    project_stats["completed_tasks"] / max(1, (days_since_start or 1) / 7), 1
                ),
                "hours_per_week": round(
                    total_actual_hours / max(1, (days_since_start or 1) / 7), 1
                ),
            },
            "timeline": {
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "target_end_date": (
                    project.target_end_date.isoformat() if project.target_end_date else None
                ),
                "actual_end_date": (
                    project.actual_end_date.isoformat() if project.actual_end_date else None
                ),
                "is_overdue": (
                    (
                        project.target_end_date
                        and date.today() > project.target_end_date
                        and project.status != "completed"
                    )
                    if project.target_end_date
                    else False
                ),
            },
            "task_breakdown": {
                stat.status: {
                    "count": stat.count,
                    "estimated_hours": float(stat.estimated_hours or 0),
                    "actual_hours": float(stat.actual_hours or 0),
                }
                for stat in task_stats
            },
        }

        return statistics

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error calculating project statistics: {str(e)}"
        )
