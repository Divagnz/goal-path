"""
HTMX Router for Tasks
Handles HTMX-specific task operations returning HTML fragments
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Form, Depends, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..schemas import TaskCreate, TaskUpdate
from ..database import get_db
from ..models import Task, Project
from ..db_utils import QueryUtils, TransactionManager
from ..htmx_utils import (
    htmx_response,
    htmx_error_response,
    htmx_success_response,
    is_htmx_request,
    htmx_required,
    render_fragment,
)

router = APIRouter(prefix="/htmx/tasks", tags=["htmx-tasks"])


@router.post("/create")
async def create_task_htmx(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("medium"),
    status: str = Form("todo"),
    task_type: str = Form("task"),
    project_id: Optional[str] = Form(None),
    parent_task_id: Optional[str] = Form(None),
    due_date: Optional[str] = Form(None),
    estimated_hours: Optional[float] = Form(None),
    db: Session = Depends(get_db),
    _htmx: bool = Depends(htmx_required),
) -> Any:
    """
    Create a new task via HTMX and return HTML fragment.
    """

    try:
        # Parse due date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            except ValueError:
                return htmx_error_response(
                    error_message="Invalid due date format. Please use YYYY-MM-DD.",
                    request=request,
                    status_code=400,
                )

        # Validate required fields
        if not title.strip():
            return htmx_error_response(
                error_message="Task title is required.",
                request=request,
                status_code=400,
                field_errors={"title": "This field is required"},
            )

        # Validate project exists if provided
        if project_id:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return htmx_error_response(
                    error_message=f"Project with ID {project_id} not found.",
                    request=request,
                    status_code=400,
                    field_errors={"project_id": "Selected project does not exist"},
                )

        # Validate parent task exists if provided
        if parent_task_id:
            parent_task = db.query(Task).filter(Task.id == parent_task_id).first()
            if not parent_task:
                return htmx_error_response(
                    error_message=f"Parent task with ID {parent_task_id} not found.",
                    request=request,
                    status_code=400,
                    field_errors={"parent_task_id": "Selected parent task does not exist"},
                )

        # Validate estimated hours
        if estimated_hours is not None and estimated_hours < 0:
            return htmx_error_response(
                error_message="Estimated hours cannot be negative.",
                request=request,
                status_code=400,
                field_errors={"estimated_hours": "Must be a positive number"},
            )

        # Create task data
        task_data = {
            "title": title.strip(),
            "description": description.strip(),
            "priority": priority,
            "status": status,
            "task_type": task_type,
            "project_id": project_id if project_id else None,
            "parent_task_id": parent_task_id if parent_task_id else None,
            "due_date": parsed_due_date,
            "estimated_hours": estimated_hours,
            "created_by": "system",  # Would come from auth in real app
        }

        # Create task in database
        with TransactionManager(db) as db_session:
            new_task = Task(**task_data)
            db_session.add(new_task)
            db_session.commit()
            db_session.refresh(new_task)

            # Get task with project information
            task_with_project = db_session.query(Task).filter(Task.id == new_task.id).first()

            # Render the task item fragment
            context = {"request": request, "task": task_with_project}

            return htmx_success_response(
                template_name="fragments/task_item.html",
                context=context,
                request=request,
                success_message=f"Task '{task_data['title']}' created successfully!",
            )

    except IntegrityError as e:
        return htmx_error_response(
            error_message=f"Task creation failed due to database constraint: {str(e)}",
            request=request,
            status_code=400,
        )
    except Exception as e:
        return htmx_error_response(
            error_message=f"An unexpected error occurred: {str(e)}",
            request=request,
            status_code=500,
        )


@router.put("/{task_id}/status")
async def update_task_status_htmx(
    task_id: str,
    request: Request,
    status: str = Query(...),
    db: Session = Depends(get_db),
    _htmx: bool = Depends(htmx_required),
) -> Any:
    """
    Update task status via HTMX and return updated HTML fragment.
    """

    try:
        # Validate status
        valid_statuses = ["todo", "in_progress", "done", "blocked", "cancelled"]
        if status not in valid_statuses:
            return htmx_error_response(
                error_message=f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}",
                request=request,
                status_code=400,
            )

        with TransactionManager(db) as db_session:
            task = db_session.query(Task).filter(Task.id == task_id).first()

            if not task:
                return htmx_error_response(
                    error_message=f"Task with ID {task_id} not found.",
                    request=request,
                    status_code=404,
                )

            old_status = task.status
            task.status = status
            task.updated_at = datetime.utcnow()

            # Set completion date if marking as done
            if status == "done" and old_status != "done":
                task.actual_end_date = datetime.utcnow().date()
            elif status != "done" and old_status == "done":
                task.actual_end_date = None

            db_session.commit()
            db_session.refresh(task)

            # Render the updated task item fragment
            context = {"request": request, "task": task}

            status_messages = {
                "todo": "moved to To Do",
                "in_progress": "started",
                "done": "completed",
                "blocked": "marked as blocked",
                "cancelled": "cancelled",
            }

            return htmx_success_response(
                template_name="fragments/task_item.html",
                context=context,
                request=request,
                success_message=f"Task '{task.title}' {status_messages.get(status, 'updated')}!",
                trigger_close_modal=False,  # Don't close modal for status updates
                additional_triggers={"updateDashboardStats": True},  # Trigger dashboard refresh
            )

    except Exception as e:
        return htmx_error_response(
            error_message=f"An error occurred while updating task status: {str(e)}",
            request=request,
            status_code=500,
        )


@router.put("/{task_id}/edit")
async def update_task_htmx(
    task_id: str,
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("medium"),
    status: str = Form("todo"),
    task_type: str = Form("task"),
    project_id: Optional[str] = Form(None),
    parent_task_id: Optional[str] = Form(None),
    due_date: Optional[str] = Form(None),
    estimated_hours: Optional[float] = Form(None),
    db: Session = Depends(get_db),
    _htmx: bool = Depends(htmx_required),
) -> Any:
    """
    Update an existing task via HTMX and return HTML fragment.
    """

    try:
        # Parse due date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            except ValueError:
                return htmx_error_response(
                    error_message="Invalid due date format. Please use YYYY-MM-DD.",
                    request=request,
                    status_code=400,
                )

        # Validate required fields
        if not title.strip():
            return htmx_error_response(
                error_message="Task title is required.",
                request=request,
                status_code=400,
                field_errors={"title": "This field is required"},
            )

        # Validate project exists if provided
        if project_id:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return htmx_error_response(
                    error_message=f"Project with ID {project_id} not found.",
                    request=request,
                    status_code=400,
                    field_errors={"project_id": "Selected project does not exist"},
                )

        # Validate parent task exists if provided and not self-referencing
        if parent_task_id:
            if parent_task_id == task_id:
                return htmx_error_response(
                    error_message="A task cannot be its own parent.",
                    request=request,
                    status_code=400,
                    field_errors={"parent_task_id": "Cannot set task as its own parent"},
                )

            parent_task = db.query(Task).filter(Task.id == parent_task_id).first()
            if not parent_task:
                return htmx_error_response(
                    error_message=f"Parent task with ID {parent_task_id} not found.",
                    request=request,
                    status_code=400,
                    field_errors={"parent_task_id": "Selected parent task does not exist"},
                )

        # Validate estimated hours
        if estimated_hours is not None and estimated_hours < 0:
            return htmx_error_response(
                error_message="Estimated hours cannot be negative.",
                request=request,
                status_code=400,
                field_errors={"estimated_hours": "Must be a positive number"},
            )

        # Update task in database
        with TransactionManager(db) as db_session:
            task = db_session.query(Task).filter(Task.id == task_id).first()

            if not task:
                return htmx_error_response(
                    error_message=f"Task with ID {task_id} not found.",
                    request=request,
                    status_code=404,
                )

            # Update task fields
            task.title = title.strip()
            task.description = description.strip()
            task.priority = priority
            task.status = status
            task.task_type = task_type
            task.project_id = project_id if project_id else None
            task.parent_task_id = parent_task_id if parent_task_id else None
            task.due_date = parsed_due_date
            task.estimated_hours = estimated_hours
            task.updated_at = datetime.utcnow()

            db_session.commit()
            db_session.refresh(task)

            # Render the updated task item fragment
            context = {"request": request, "task": task}

            return htmx_success_response(
                template_name="fragments/task_item.html",
                context=context,
                request=request,
                success_message=f"Task '{task.title}' updated successfully!",
            )

    except Exception as e:
        return htmx_error_response(
            error_message=f"An error occurred while updating the task: {str(e)}",
            request=request,
            status_code=500,
        )


@router.delete("/{task_id}")
async def delete_task_htmx(
    task_id: str,
    request: Request,
    db: Session = Depends(get_db),
    _htmx: bool = Depends(htmx_required),
) -> Any:
    """
    Delete a task via HTMX and return empty response.
    """

    try:
        with TransactionManager(db) as db_session:
            task = db_session.query(Task).filter(Task.id == task_id).first()

            if not task:
                return htmx_error_response(
                    error_message=f"Task with ID {task_id} not found.",
                    request=request,
                    status_code=404,
                )

            task_title = task.title

            # Check if task has subtasks
            subtask_count = db_session.query(Task).filter(Task.parent_task_id == task_id).count()
            if subtask_count > 0:
                return htmx_error_response(
                    error_message=f"Cannot delete task '{task_title}' because it has {subtask_count} subtasks. Please delete or reassign the subtasks first.",
                    request=request,
                    status_code=400,
                )

            # Delete the task
            db_session.delete(task)
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
                        "message": f"Task '{task_title}' deleted successfully!",
                    },
                    "updateDashboardStats": True,
                },
            )

    except Exception as e:
        return htmx_error_response(
            error_message=f"An error occurred while deleting the task: {str(e)}",
            request=request,
            status_code=500,
        )


@router.get("/list")
async def get_tasks_list_htmx(
    request: Request,
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 15,
    db: Session = Depends(get_db),
    _htmx: bool = Depends(htmx_required),
) -> Any:
    """
    Get a list of task items for dashboard updates.
    """

    try:
        # Build query
        query = db.query(Task).order_by(Task.updated_at.desc())

        if project_id:
            query = query.filter(Task.project_id == project_id)
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)

        tasks = query.limit(limit).all()

        context = {"request": request, "tasks": tasks}

        return htmx_response(
            template_name="fragments/tasks_list.html", context=context, request=request
        )

    except Exception as e:
        return htmx_error_response(
            error_message=f"An error occurred while retrieving tasks: {str(e)}",
            request=request,
            status_code=500,
        )
