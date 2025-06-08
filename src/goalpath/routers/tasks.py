"""
Tasks API Router - Database Implementation
Full CRUD operations for tasks with hierarchical support
"""

from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskFilters,
    MessageResponse,
    ErrorResponse,
)
from ..database import get_db
from ..models import Task, Project
from ..db_utils import QueryUtils, TransactionManager

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/", response_model=List[TaskResponse], summary="List tasks")
async def list_tasks(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    parent_task_id: Optional[str] = Query(None, description="Filter by parent task ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    assigned_to: Optional[str] = Query(None, description="Filter by assignee"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
) -> List[TaskResponse]:
    """
    List all tasks with filtering and pagination.

    **Database Implementation**: Queries tasks with hierarchy information.
    """

    try:
        # Use QueryUtils for database operations with hierarchy
        tasks_data = QueryUtils.get_tasks_with_hierarchy(
            db=db,
            project_id=project_id,
            parent_task_id=parent_task_id,
            status=status,
            task_type=task_type,
            assigned_to=assigned_to,
            page=page,
            size=size,
        )

        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            tasks_data = [
                task
                for task in tasks_data
                if search_lower in task["title"].lower()
                or search_lower in (task["description"] or "").lower()
            ]

        # Add dependency count for each task
        for task_data in tasks_data:
            from ..models import TaskDependency

            dependency_count = (
                db.query(TaskDependency).filter(TaskDependency.task_id == task_data["id"]).count()
            )
            task_data["dependency_count"] = dependency_count

        return [TaskResponse(**task) for task in tasks_data]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tasks: {str(e)}")


@router.get("/{task_id}", response_model=TaskResponse, summary="Get task by ID")
async def get_task(task_id: str, db: Session = Depends(get_db)) -> TaskResponse:
    """
    Get a specific task by ID with hierarchy information.

    **Database Implementation**: Retrieves task with calculated stats.
    """

    try:
        # Get task from database
        task = db.query(Task).filter(Task.id == task_id).first()

        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        # Calculate subtask count
        subtask_count = db.query(Task).filter(Task.parent_task_id == task_id).count()

        # Calculate dependency count
        from ..models import TaskDependency

        dependency_count = (
            db.query(TaskDependency).filter(TaskDependency.task_id == task_id).count()
        )

        # Build response data
        task_data = {
            "id": task.id,
            "project_id": task.project_id,
            "parent_task_id": task.parent_task_id,
            "title": task.title,
            "description": task.description,
            "task_type": task.task_type,
            "status": task.status,
            "priority": task.priority,
            "story_points": task.story_points,
            "estimated_hours": float(task.estimated_hours) if task.estimated_hours else None,
            "actual_hours": float(task.actual_hours) if task.actual_hours else None,
            "start_date": task.start_date.isoformat() if task.start_date else None,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed_date": task.completed_date.isoformat() if task.completed_date else None,
            "assigned_to": task.assigned_to,
            "created_by": task.created_by,
            "order_index": task.order_index,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "subtask_count": subtask_count,
            "dependency_count": dependency_count,
        }

        return TaskResponse(**task_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task: {str(e)}")


@router.post("/", response_model=TaskResponse, status_code=201, summary="Create new task")
async def create_task(task: TaskCreate, db: Session = Depends(get_db)) -> TaskResponse:
    """
    Create a new task.

    **Database Implementation**: Creates task in database with validation.
    """

    try:
        with TransactionManager(db) as db_session:
            # Validate that the project exists
            project = db_session.query(Project).filter(Project.id == task.project_id).first()
            if not project:
                raise HTTPException(
                    status_code=404, detail=f"Project with ID {task.project_id} not found"
                )

            # Validate parent task if provided
            if task.parent_task_id:
                parent_task = db_session.query(Task).filter(Task.id == task.parent_task_id).first()
                if not parent_task:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Parent task with ID {task.parent_task_id} not found",
                    )

                # Ensure parent task is in the same project
                if parent_task.project_id != task.project_id:
                    raise HTTPException(
                        status_code=400, detail="Parent task must be in the same project"
                    )

                # Validate hierarchy (prevent cycles)
                if not QueryUtils.validate_task_hierarchy(
                    db_session, "new_task", task.parent_task_id
                ):
                    raise HTTPException(
                        status_code=400, detail="Invalid task hierarchy - would create a cycle"
                    )

            # Create new task instance
            task_data = task.model_dump()

            # Add created_by if not provided (would come from auth in real app)
            if "created_by" not in task_data or not task_data["created_by"]:
                task_data["created_by"] = "system"

            # Calculate order index if not provided
            if "order_index" not in task_data:
                max_order = (
                    db_session.query(Task.order_index)
                    .filter(
                        Task.project_id == task.project_id,
                        Task.parent_task_id == task.parent_task_id,
                    )
                    .order_by(Task.order_index.desc())
                    .first()
                )
                task_data["order_index"] = (max_order[0] + 1) if max_order and max_order[0] else 1

            new_task = Task(**task_data)
            db_session.add(new_task)
            db_session.commit()
            db_session.refresh(new_task)

            # Build response with calculated fields
            task_response_data = {
                "id": new_task.id,
                "project_id": new_task.project_id,
                "parent_task_id": new_task.parent_task_id,
                "title": new_task.title,
                "description": new_task.description,
                "task_type": new_task.task_type,
                "status": new_task.status,
                "priority": new_task.priority,
                "story_points": new_task.story_points,
                "estimated_hours": (
                    float(new_task.estimated_hours) if new_task.estimated_hours else None
                ),
                "actual_hours": float(new_task.actual_hours) if new_task.actual_hours else None,
                "start_date": new_task.start_date.isoformat() if new_task.start_date else None,
                "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
                "completed_date": (
                    new_task.completed_date.isoformat() if new_task.completed_date else None
                ),
                "assigned_to": new_task.assigned_to,
                "created_by": new_task.created_by,
                "order_index": new_task.order_index,
                "created_at": new_task.created_at.isoformat(),
                "updated_at": new_task.updated_at.isoformat(),
                "subtask_count": 0,  # New task has no subtasks
                "dependency_count": 0,  # New task has no dependencies
            }

            return TaskResponse(**task_response_data)

    except HTTPException:
        raise
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Task creation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")


@router.put("/{task_id}", response_model=TaskResponse, summary="Update task")
async def update_task(
    task_id: str, task_update: TaskUpdate, db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Update an existing task.

    **Database Implementation**: Updates task in database with validation.
    """

    try:
        with TransactionManager(db) as db_session:
            # Find existing task
            task = db_session.query(Task).filter(Task.id == task_id).first()

            if not task:
                raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

            # Get update data
            update_data = task_update.model_dump(exclude_unset=True)

            # Validate parent task hierarchy if being changed
            if "parent_task_id" in update_data:
                new_parent_id = update_data["parent_task_id"]
                if new_parent_id:
                    parent_task = db_session.query(Task).filter(Task.id == new_parent_id).first()
                    if not parent_task:
                        raise HTTPException(
                            status_code=404, detail=f"Parent task with ID {new_parent_id} not found"
                        )

                    # Ensure parent task is in the same project
                    if parent_task.project_id != task.project_id:
                        raise HTTPException(
                            status_code=400, detail="Parent task must be in the same project"
                        )

                    # Validate hierarchy (prevent cycles)
                    if not QueryUtils.validate_task_hierarchy(db_session, task_id, new_parent_id):
                        raise HTTPException(
                            status_code=400, detail="Invalid task hierarchy - would create a cycle"
                        )

            # Handle status transitions
            if "status" in update_data:
                new_status = update_data["status"]
                if new_status == "done" and task.status != "done":
                    update_data["completed_date"] = datetime.now()
                elif new_status != "done" and task.status == "done":
                    update_data["completed_date"] = None

            # Update fields from request
            for field, value in update_data.items():
                setattr(task, field, value)

            db_session.commit()
            db_session.refresh(task)

            # Calculate related data
            subtask_count = db_session.query(Task).filter(Task.parent_task_id == task_id).count()

            from ..models import TaskDependency

            dependency_count = (
                db_session.query(TaskDependency).filter(TaskDependency.task_id == task_id).count()
            )

            # Build response data
            task_response_data = {
                "id": task.id,
                "project_id": task.project_id,
                "parent_task_id": task.parent_task_id,
                "title": task.title,
                "description": task.description,
                "task_type": task.task_type,
                "status": task.status,
                "priority": task.priority,
                "story_points": task.story_points,
                "estimated_hours": float(task.estimated_hours) if task.estimated_hours else None,
                "actual_hours": float(task.actual_hours) if task.actual_hours else None,
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed_date": task.completed_date.isoformat() if task.completed_date else None,
                "assigned_to": task.assigned_to,
                "created_by": task.created_by,
                "order_index": task.order_index,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "subtask_count": subtask_count,
                "dependency_count": dependency_count,
            }

            return TaskResponse(**task_response_data)

    except HTTPException:
        raise
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Task update failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")


@router.delete("/{task_id}", response_model=MessageResponse, summary="Delete task")
async def delete_task(
    task_id: str,
    cascade: bool = Query(
        False, description="Delete subtasks (true) or reassign to parent (false)"
    ),
    db: Session = Depends(get_db),
) -> MessageResponse:
    """
    Delete a task.

    **Database Implementation**: Deletes task with subtask handling options.
    """

    try:
        with TransactionManager(db) as db_session:
            # Find existing task
            task = db_session.query(Task).filter(Task.id == task_id).first()

            if not task:
                raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

            task_title = task.title

            # Handle subtasks
            subtasks = db_session.query(Task).filter(Task.parent_task_id == task_id).all()

            if subtasks:
                if cascade:
                    # Delete all subtasks (will cascade to their subtasks)
                    for subtask in subtasks:
                        db_session.delete(subtask)
                else:
                    # Reassign subtasks to this task's parent
                    for subtask in subtasks:
                        subtask.parent_task_id = task.parent_task_id

            # Delete the task (dependencies will be handled by CASCADE)
            db_session.delete(task)
            db_session.commit()

            action_desc = "and all subtasks " if cascade and subtasks else ""
            return MessageResponse(message=f"Task '{task_title}' {action_desc}deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")


@router.put("/{task_id}/status", response_model=TaskResponse, summary="Update task status")
async def update_task_status(
    task_id: str,
    status: str = Query(..., description="New task status"),
    db: Session = Depends(get_db),
) -> TaskResponse:
    """
    Quick status update for a task.

    **Database Implementation**: Updates task status with automatic timestamp handling.
    """

    try:
        with TransactionManager(db) as db_session:
            # Find existing task
            task = db_session.query(Task).filter(Task.id == task_id).first()

            if not task:
                raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

            # Validate status value
            from ..models import TaskStatus

            try:
                TaskStatus(status)  # This will raise ValueError if invalid
            except ValueError:
                valid_statuses = [status.value for status in TaskStatus]
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status '{status}'. Valid values: {valid_statuses}",
                )

            # Handle status transitions
            old_status = task.status
            if status == "done" and old_status != "done":
                task.completed_date = datetime.now()
            elif status != "done" and old_status == "done":
                task.completed_date = None

            task.status = status
            db_session.commit()
            db_session.refresh(task)

            # Calculate related data
            subtask_count = db_session.query(Task).filter(Task.parent_task_id == task_id).count()

            from ..models import TaskDependency

            dependency_count = (
                db_session.query(TaskDependency).filter(TaskDependency.task_id == task_id).count()
            )

            # Build response data
            task_response_data = {
                "id": task.id,
                "project_id": task.project_id,
                "parent_task_id": task.parent_task_id,
                "title": task.title,
                "description": task.description,
                "task_type": task.task_type,
                "status": task.status,
                "priority": task.priority,
                "story_points": task.story_points,
                "estimated_hours": float(task.estimated_hours) if task.estimated_hours else None,
                "actual_hours": float(task.actual_hours) if task.actual_hours else None,
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed_date": task.completed_date.isoformat() if task.completed_date else None,
                "assigned_to": task.assigned_to,
                "created_by": task.created_by,
                "order_index": task.order_index,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "subtask_count": subtask_count,
                "dependency_count": dependency_count,
            }

            return TaskResponse(**task_response_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task status: {str(e)}")


@router.get("/{task_id}/subtasks", response_model=List[TaskResponse], summary="Get task subtasks")
async def get_task_subtasks(
    task_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
) -> List[TaskResponse]:
    """
    Get all subtasks for a specific task.

    **Database Implementation**: Retrieves subtasks with hierarchy.
    """

    try:
        # Verify parent task exists
        parent_task = db.query(Task).filter(Task.id == task_id).first()
        if not parent_task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        # Get subtasks using QueryUtils
        subtasks_data = QueryUtils.get_tasks_with_hierarchy(
            db=db, parent_task_id=task_id, page=page, size=size
        )

        # Add dependency count for each subtask
        for task_data in subtasks_data:
            from ..models import TaskDependency

            dependency_count = (
                db.query(TaskDependency).filter(TaskDependency.task_id == task_data["id"]).count()
            )
            task_data["dependency_count"] = dependency_count

        return [TaskResponse(**task) for task in subtasks_data]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving subtasks: {str(e)}")


@router.get("/{task_id}/dependencies", summary="Get task dependencies")
async def get_task_dependencies(task_id: str, db: Session = Depends(get_db)) -> dict:
    """
    Get all dependencies for a task.

    **Database Implementation**: Retrieves task dependency relationships.
    """

    try:
        # Verify task exists
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        from ..models import TaskDependency

        # Get dependencies (tasks this task depends on)
        depends_on = (
            db.query(TaskDependency, Task)
            .join(Task, TaskDependency.depends_on_task_id == Task.id)
            .filter(TaskDependency.task_id == task_id)
            .all()
        )

        # Get dependents (tasks that depend on this task)
        dependents = (
            db.query(TaskDependency, Task)
            .join(Task, TaskDependency.task_id == Task.id)
            .filter(TaskDependency.depends_on_task_id == task_id)
            .all()
        )

        # Format response
        dependencies = {
            "task_id": task_id,
            "task_title": task.title,
            "depends_on": [
                {
                    "dependency_id": dep.id,
                    "task_id": dep_task.id,
                    "task_title": dep_task.title,
                    "task_status": dep_task.status,
                    "dependency_type": dep.dependency_type,
                    "created_at": dep.created_at.isoformat(),
                }
                for dep, dep_task in depends_on
            ],
            "dependents": [
                {
                    "dependency_id": dep.id,
                    "task_id": dep_task.id,
                    "task_title": dep_task.title,
                    "task_status": dep_task.status,
                    "dependency_type": dep.dependency_type,
                    "created_at": dep.created_at.isoformat(),
                }
                for dep, dep_task in dependents
            ],
        }

        return dependencies

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task dependencies: {str(e)}")
