"""
Tasks API Router - Mock/Fixed Responses
This module contains fixed responses for testing API structure
TODO: Replace with actual database logic
"""

from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from ..schemas import (
    TaskCreate, TaskUpdate, TaskResponse, TaskFilters,
    MessageResponse, ErrorResponse
)
from ..database import get_db

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# Mock data for testing
MOCK_TASKS = [
    {
        "id": "task-001",
        "project_id": "proj-001",
        "parent_task_id": None,
        "title": "Design System Creation",
        "description": "Create comprehensive design system with components and guidelines",
        "task_type": "epic",
        "status": "in_progress",
        "priority": "high",
        "story_points": 13,
        "estimated_hours": 80.0,
        "actual_hours": 45.5,
        "start_date": "2025-01-20",
        "due_date": "2025-07-15",
        "assigned_to": "designer_001",
        "completed_date": None,
        "created_by": "user_001",
        "order_index": 1,
        "created_at": "2025-01-20T09:00:00Z",
        "updated_at": "2025-06-03T14:30:00Z",
        "subtask_count": 3,
        "dependency_count": 0
    },
    {
        "id": "task-002",
        "project_id": "proj-001",
        "parent_task_id": "task-001",
        "title": "Color Palette Design",
        "description": "Define primary, secondary, and accent colors",
        "task_type": "subtask",
        "status": "done",
        "priority": "medium",
        "story_points": None,
        "estimated_hours": 8.0,
        "actual_hours": 6.5,
        "start_date": "2025-01-20",
        "due_date": "2025-02-01",
        "assigned_to": "designer_001",
        "completed_date": "2025-01-28T16:00:00Z",
        "created_by": "user_001",
        "order_index": 1,
        "created_at": "2025-01-20T09:30:00Z",
        "updated_at": "2025-01-28T16:00:00Z",
        "subtask_count": 0,
        "dependency_count": 0
    }
]

@router.get("/", response_model=List[TaskResponse], summary="List tasks")
async def list_tasks(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
) -> List[TaskResponse]:
    """List all tasks with filtering and pagination"""
    
    filtered_tasks = MOCK_TASKS.copy()
    
    if project_id:
        filtered_tasks = [t for t in filtered_tasks if t["project_id"] == project_id]
    if status:
        filtered_tasks = [t for t in filtered_tasks if t["status"] == status]
    
    # Simulate pagination
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_tasks = filtered_tasks[start_idx:end_idx]
    
    return [TaskResponse(**task) for task in paginated_tasks]

@router.get("/{task_id}", response_model=TaskResponse, summary="Get task by ID")
async def get_task(
    task_id: str,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """Get a specific task by ID"""
    
    task = next((t for t in MOCK_TASKS if t["id"] == task_id), None)
    
    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID {task_id} not found"
        )
    
    return TaskResponse(**task)

@router.post("/", response_model=TaskResponse, status_code=201, summary="Create new task")
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """Create a new task"""
    
    new_task_data = {
        "id": f"task-{len(MOCK_TASKS) + 1:03d}",
        **task.dict(),
        "actual_hours": None,
        "completed_date": None,
        "created_by": "current_user",
        "order_index": len(MOCK_TASKS) + 1,
        "created_at": datetime.now().isoformat() + "Z",
        "updated_at": datetime.now().isoformat() + "Z",
        "subtask_count": 0,
        "dependency_count": 0
    }
    
    MOCK_TASKS.append(new_task_data)
    
    return TaskResponse(**new_task_data)

@router.put("/{task_id}", response_model=TaskResponse, summary="Update task")
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """Update an existing task"""
    
    task_idx = next((i for i, t in enumerate(MOCK_TASKS) if t["id"] == task_id), None)
    
    if task_idx is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID {task_id} not found"
        )
    
    task_data = MOCK_TASKS[task_idx].copy()
    update_data = task_update.dict(exclude_unset=True)
    
    # Handle status transitions
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == "done" and task_data["status"] != "done":
            update_data["completed_date"] = datetime.now().isoformat() + "Z"
        elif new_status != "done" and task_data["status"] == "done":
            update_data["completed_date"] = None
    
    task_data.update(update_data)
    task_data["updated_at"] = datetime.now().isoformat() + "Z"
    
    MOCK_TASKS[task_idx] = task_data
    
    return TaskResponse(**task_data)

@router.delete("/{task_id}", response_model=MessageResponse, summary="Delete task")
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db)
) -> MessageResponse:
    """Delete a task"""
    
    task_idx = next((i for i, t in enumerate(MOCK_TASKS) if t["id"] == task_id), None)
    
    if task_idx is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID {task_id} not found"
        )
    
    removed_task = MOCK_TASKS.pop(task_idx)
    
    return MessageResponse(message=f"Task '{removed_task['title']}' deleted successfully")
