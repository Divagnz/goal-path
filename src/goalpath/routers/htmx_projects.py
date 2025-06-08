"""
HTMX Router for Projects
Handles HTMX-specific project operations returning HTML fragments
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..db_utils import QueryUtils, TransactionManager
from ..htmx_utils import (
    htmx_error_response,
    htmx_required,
    htmx_response,
    htmx_success_response,
)
from ..models import Project, Task

router = APIRouter(prefix="/htmx/projects", tags=["htmx-projects"])


@router.post("/create")
async def create_project_htmx(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    priority: str = Form("medium"),
    status: str = Form("active"),
    start_date: Optional[str] = Form(None),
    target_end_date: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    _htmx: bool = Depends(htmx_required),
) -> Any:
    """
    Create a new project via HTMX and return HTML fragment.
    """

    try:
        # Parse dates if provided
        parsed_start_date = None
        parsed_target_end_date = None

        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError:
                return htmx_error_response(
                    error_message="Invalid start date format. Please use YYYY-MM-DD.",
                    request=request,
                    status_code=400,
                )

        if target_end_date:
            try:
                parsed_target_end_date = datetime.strptime(target_end_date, "%Y-%m-%d").date()
            except ValueError:
                return htmx_error_response(
                    error_message="Invalid target end date format. Please use YYYY-MM-DD.",
                    request=request,
                    status_code=400,
                )

        # Validate business rules
        if (
            parsed_start_date
            and parsed_target_end_date
            and parsed_start_date > parsed_target_end_date
        ):
            return htmx_error_response(
                error_message="Start date cannot be after target end date.",
                request=request,
                status_code=400,
            )

        # Create project data
        project_data = {
            "name": name.strip(),
            "description": description.strip(),
            "priority": priority,
            "status": status,
            "start_date": parsed_start_date,
            "target_end_date": parsed_target_end_date,
            "created_by": "system",  # Would come from auth in real app
        }

        # Validate required fields
        if not project_data["name"]:
            return htmx_error_response(
                error_message="Project name is required.",
                request=request,
                status_code=400,
                field_errors={"name": "This field is required"},
            )

        # Create project in database
        with TransactionManager(db) as db_session:
            new_project = Project(**project_data)
            db_session.add(new_project)
            db_session.commit()
            db_session.refresh(new_project)

            # Get project with statistics
            project_with_stats = QueryUtils.get_project_with_stats(db_session, new_project.id)

            # Render the project card fragment
            context = {"request": request, "project": project_with_stats}

            return htmx_success_response(
                template_name="fragments/project_card.html",
                context=context,
                request=request,
                success_message=f"Project '{project_data['name']}' created successfully!",
            )

    except IntegrityError as e:
        return htmx_error_response(
            error_message=f"Project creation failed due to database constraint: {str(e)}",
            request=request,
            status_code=400,
        )
    except Exception as e:
        return htmx_error_response(
            error_message=f"An unexpected error occurred: {str(e)}",
            request=request,
            status_code=500,
        )


@router.put("/{project_id}/edit")
async def update_project_htmx(
    project_id: str,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    priority: str = Form("medium"),
    status: str = Form("active"),
    start_date: Optional[str] = Form(None),
    target_end_date: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    _htmx: bool = Depends(htmx_required),
) -> Any:
    """
    Update an existing project via HTMX and return HTML fragment.
    """

    try:
        # Parse dates if provided
        parsed_start_date = None
        parsed_target_end_date = None

        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError:
                return htmx_error_response(
                    error_message="Invalid start date format. Please use YYYY-MM-DD.",
                    request=request,
                    status_code=400,
                )

        if target_end_date:
            try:
                parsed_target_end_date = datetime.strptime(target_end_date, "%Y-%m-%d").date()
            except ValueError:
                return htmx_error_response(
                    error_message="Invalid target end date format. Please use YYYY-MM-DD.",
                    request=request,
                    status_code=400,
                )

        # Validate business rules
        if (
            parsed_start_date
            and parsed_target_end_date
            and parsed_start_date > parsed_target_end_date
        ):
            return htmx_error_response(
                error_message="Start date cannot be after target end date.",
                request=request,
                status_code=400,
            )

        # Validate required fields
        if not name.strip():
            return htmx_error_response(
                error_message="Project name is required.",
                request=request,
                status_code=400,
                field_errors={"name": "This field is required"},
            )

        # Update project in database
        with TransactionManager(db) as db_session:
            project = db_session.query(Project).filter(Project.id == project_id).first()

            if not project:
                return htmx_error_response(
                    error_message=f"Project with ID {project_id} not found.",
                    request=request,
                    status_code=404,
                )

            # Update project fields
            project.name = name.strip()
            project.description = description.strip()
            project.priority = priority
            project.status = status
            project.start_date = parsed_start_date
            project.target_end_date = parsed_target_end_date
            project.updated_at = datetime.utcnow()

            db_session.commit()
            db_session.refresh(project)

            # Get updated project with statistics
            project_with_stats = QueryUtils.get_project_with_stats(db_session, project.id)

            # Render the updated project card fragment
            context = {"request": request, "project": project_with_stats}

            return htmx_success_response(
                template_name="fragments/project_card.html",
                context=context,
                request=request,
                success_message=f"Project '{project.name}' updated successfully!",
            )

    except Exception as e:
        return htmx_error_response(
            error_message=f"An error occurred while updating the project: {str(e)}",
            request=request,
            status_code=500,
        )


@router.delete("/{project_id}")
async def delete_project_htmx(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _htmx: bool = Depends(htmx_required),
) -> Any:
    """
    Delete a project via HTMX and return empty response.
    """

    try:
        with TransactionManager(db) as db_session:
            project = db_session.query(Project).filter(Project.id == project_id).first()

            if not project:
                return htmx_error_response(
                    error_message=f"Project with ID {project_id} not found.",
                    request=request,
                    status_code=404,
                )

            project_name = project.name

            # Check if project has tasks
            task_count = db_session.query(Task).filter(Task.project_id == project_id).count()
            if task_count > 0:
                return htmx_error_response(
                    error_message=f"Cannot delete project '{project_name}' because it has {task_count} associated tasks. Please delete or reassign the tasks first.",
                    request=request,
                    status_code=400,
                )

            # Delete the project
            db_session.delete(project)
            db_session.commit()

            # Return empty content to remove the element
            return htmx_response(
                template_name="fragments/empty.html",
                context={"request": request},
                request=request,
                trigger={
                    "showNotification": {
                        "type": "success",
                        "title": "Success",
                        "message": f"Project '{project_name}' deleted successfully!",
                    }
                },
            )

    except Exception as e:
        return htmx_error_response(
            error_message=f"An error occurred while deleting the project: {str(e)}",
            request=request,
            status_code=500,
        )


@router.get("/{project_id}/card")
async def get_project_card_htmx(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _htmx: bool = Depends(htmx_required),
) -> Any:
    """
    Get a single project card fragment for updates.
    """

    try:
        project_with_stats = QueryUtils.get_project_with_stats(db, project_id)

        if not project_with_stats:
            return htmx_error_response(
                error_message=f"Project with ID {project_id} not found.",
                request=request,
                status_code=404,
            )

        context = {"request": request, "project": project_with_stats}

        return htmx_response(
            template_name="fragments/project_card.html", context=context, request=request
        )

    except Exception as e:
        return htmx_error_response(
            error_message=f"An error occurred while retrieving the project: {str(e)}",
            request=request,
            status_code=500,
        )


@router.get("/list")
async def get_projects_list_htmx(
    request: Request,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    _htmx: bool = Depends(htmx_required),
) -> Any:
    """
    Get a list of project cards for dashboard updates.
    """

    try:
        projects_data = QueryUtils.get_projects_with_stats(
            db=db, status=status, priority=priority, search=search, page=1, size=limit
        )

        context = {"request": request, "projects": projects_data}

        return htmx_response(
            template_name="fragments/projects_list.html", context=context, request=request
        )

    except Exception as e:
        return htmx_error_response(
            error_message=f"An error occurred while retrieving projects: {str(e)}",
            request=request,
            status_code=500,
        )
