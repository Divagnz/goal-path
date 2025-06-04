"""
Pydantic schemas for GoalPath API
Request and response models for validation and documentation
"""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field
from enum import Enum

# Enums for validation
class ProjectStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskType(str, Enum):
    EPIC = "epic"
    STORY = "story"
    TASK = "task"
    SUBTASK = "subtask"
    MILESTONE = "milestone"
    BUG = "bug"

class TaskStatus(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    LOWEST = "lowest"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    HIGHEST = "highest"
    CRITICAL = "critical"

class GoalType(str, Enum):
    LONG_TERM = "long_term"
    MEDIUM_TERM = "medium_term"
    SHORT_TERM = "short_term"
    MILESTONE = "milestone"

# Project Schemas
class ProjectBase(BaseModel):
    name: str = Field(..., max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    status: ProjectStatus = Field(ProjectStatus.ACTIVE, description="Project status")
    priority: Priority = Field(Priority.MEDIUM, description="Project priority")
    start_date: Optional[date] = Field(None, description="Project start date")
    target_end_date: Optional[date] = Field(None, description="Target completion date")

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[Priority] = None
    start_date: Optional[date] = None
    target_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None

class ProjectResponse(ProjectBase):
    id: str = Field(..., description="Project ID")
    actual_end_date: Optional[date] = Field(None, description="Actual completion date")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: str = Field(..., description="Creator identifier")
    
    # Statistics (calculated fields)
    total_tasks: int = Field(0, description="Total number of tasks")
    completed_tasks: int = Field(0, description="Number of completed tasks")
    completion_percentage: float = Field(0.0, description="Completion percentage")

    class Config:
        from_attributes = True

# Task Schemas
class TaskBase(BaseModel):
    title: str = Field(..., max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    task_type: TaskType = Field(TaskType.TASK, description="Task type")
    status: TaskStatus = Field(TaskStatus.BACKLOG, description="Task status")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority")
    story_points: Optional[int] = Field(None, ge=1, description="Story points for estimation")
    estimated_hours: Optional[float] = Field(None, ge=0, description="Estimated hours")
    start_date: Optional[date] = Field(None, description="Task start date")
    due_date: Optional[date] = Field(None, description="Task due date")
    assigned_to: Optional[str] = Field(None, description="Assignee identifier")

class TaskCreate(TaskBase):
    project_id: str = Field(..., description="Parent project ID")
    parent_task_id: Optional[str] = Field(None, description="Parent task ID for hierarchy")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    task_type: Optional[TaskType] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    story_points: Optional[int] = Field(None, ge=1)
    estimated_hours: Optional[float] = Field(None, ge=0)
    actual_hours: Optional[float] = Field(None, ge=0)
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    assigned_to: Optional[str] = None
    parent_task_id: Optional[str] = None

class TaskResponse(TaskBase):
    id: str = Field(..., description="Task ID")
    project_id: str = Field(..., description="Parent project ID")
    parent_task_id: Optional[str] = Field(None, description="Parent task ID")
    actual_hours: Optional[float] = Field(None, description="Actual hours spent")
    completed_date: Optional[datetime] = Field(None, description="Completion timestamp")
    created_by: str = Field(..., description="Creator identifier")
    order_index: int = Field(0, description="Sort order within parent")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Related data
    subtask_count: int = Field(0, description="Number of subtasks")
    dependency_count: int = Field(0, description="Number of dependencies")

    class Config:
        from_attributes = True

# Goal Schemas
class GoalBase(BaseModel):
    title: str = Field(..., max_length=255, description="Goal title")
    description: Optional[str] = Field(None, description="Goal description")
    goal_type: GoalType = Field(GoalType.SHORT_TERM, description="Goal type")
    target_date: Optional[date] = Field(None, description="Target achievement date")
    status: ProjectStatus = Field(ProjectStatus.ACTIVE, description="Goal status")

class GoalCreate(GoalBase):
    parent_goal_id: Optional[str] = Field(None, description="Parent goal ID for hierarchy")

class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    goal_type: Optional[GoalType] = None
    target_date: Optional[date] = None
    status: Optional[ProjectStatus] = None
    parent_goal_id: Optional[str] = None
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)

class GoalResponse(GoalBase):
    id: str = Field(..., description="Goal ID")
    parent_goal_id: Optional[str] = Field(None, description="Parent goal ID")
    progress_percentage: float = Field(0.0, description="Progress percentage (0-100)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Related data
    linked_projects: int = Field(0, description="Number of linked projects")
    subgoal_count: int = Field(0, description="Number of subgoals")

    class Config:
        from_attributes = True

# Common response schemas
class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")

class MessageResponse(BaseModel):
    message: str = Field(..., description="Success message")

class PaginatedResponse(BaseModel):
    items: List[dict] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(1, description="Current page number")
    size: int = Field(20, description="Items per page")
    pages: int = Field(..., description="Total number of pages")

# Query parameter schemas
class ProjectFilters(BaseModel):
    status: Optional[ProjectStatus] = None
    priority: Optional[Priority] = None
    search: Optional[str] = Field(None, max_length=100)

class TaskFilters(BaseModel):
    project_id: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    task_type: Optional[TaskType] = None
    assigned_to: Optional[str] = None
    parent_task_id: Optional[str] = None
    search: Optional[str] = Field(None, max_length=100)

class GoalFilters(BaseModel):
    status: Optional[ProjectStatus] = None
    goal_type: Optional[GoalType] = None
    parent_goal_id: Optional[str] = None
    search: Optional[str] = Field(None, max_length=100)
