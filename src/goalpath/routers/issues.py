"""
Enhanced Issue management routes for GoalPath
Handles issue tracking with promotion to tasks functionality
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..database import get_db
from ..models.extended import Issue, IssueStatus
from ..models import Task, TaskDependency, TaskStatus, TaskType
from ..schemas import (
    IssueCreate, IssueUpdate, IssueResponse, IssuePromoteRequest,
    TaskCreate, TaskResponse
)

router = APIRouter(prefix="/api/issues", tags=["issues"])


@router.get("/", response_model=List[IssueResponse])
async def list_issues(
    project_id: Optional[str] = None,
    status: Optional[IssueStatus] = None,
    issue_type: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List issues with optional filtering"""
    query = db.query(Issue)
    
    # Apply filters
    if project_id:
        query = query.filter(Issue.project_id == project_id)
    if status:
        query = query.filter(Issue.status == status)
    if issue_type:
        query = query.filter(Issue.issue_type == issue_type)
    if priority:
        query = query.filter(Issue.priority == priority)
    if assignee:
        query = query.filter(Issue.assignee == assignee)
    
    # Order by priority and creation date
    query = query.order_by(
        Issue.priority.desc(),
        Issue.created_at.desc()
    )
    
    issues = query.offset(skip).limit(limit).all()
    return issues


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(issue_id: str, db: Session = Depends(get_db)):
    """Get a specific issue by ID"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    return issue


@router.post("/", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(issue_data: IssueCreate, db: Session = Depends(get_db)):
    """Create a new issue"""
    issue = Issue(**issue_data.dict())
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@router.put("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: str, 
    issue_data: IssueUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing issue"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Update fields
    update_data = issue_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(issue, field, value)
    
    db.commit()
    db.refresh(issue)
    return issue


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_issue(issue_id: str, db: Session = Depends(get_db)):
    """Delete an issue"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    db.delete(issue)
    db.commit()


@router.post("/{issue_id}/promote", response_model=TaskResponse)
async def promote_issue_to_task(
    issue_id: str,
    promote_data: IssuePromoteRequest,
    db: Session = Depends(get_db)
):
    """
    Promote an issue to a task
    When promoted, the task gets blocked by the original issue tracking task
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    if issue.status == IssueStatus.PROMOTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Issue has already been promoted to a task"
        )
    
    # Create the new task
    task_title = promote_data.task_title or issue.title
    task_data = {
        "title": task_title,
        "description": issue.description,
        "task_type": TaskType.TASK,
        "status": TaskStatus.BACKLOG,
        "priority": issue.priority,
        "project_id": issue.project_id,
        "assigned_to": issue.assignee,
        "created_by": f"promoted_from_issue_{issue.id}",
    }
    
    # Add epic and milestone if provided
    if promote_data.epic_id:
        task_data["epic_id"] = promote_data.epic_id
    if promote_data.milestone_id:
        task_data["milestone_id"] = promote_data.milestone_id
    
    # Create the task
    task = Task(**task_data)
    db.add(task)
    db.flush()  # Get the task ID
    
    # Update the issue to promoted status and link to the task
    issue.status = IssueStatus.PROMOTED
    issue.promoted_to_task_id = task.id
    
    # Create a blocking dependency: the promoted task is blocked by the issue resolution
    # This means the task cannot be completed until the issue is resolved
    dependency = TaskDependency(
        task_id=task.id,
        depends_on_task_id=issue.id,  # This will need adjustment in your model
        dependency_type="blocks"
    )
    db.add(dependency)
    
    db.commit()
    db.refresh(task)
    
    return task


@router.get("/{issue_id}/promoted-task")
async def get_promoted_task(issue_id: str, db: Session = Depends(get_db)):
    """Get the task that was created from promoting this issue"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    if not issue.promoted_to_task_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue has not been promoted to a task"
        )
    
    task = db.query(Task).filter(Task.id == issue.promoted_to_task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promoted task not found"
        )
    
    return task


@router.put("/{issue_id}/status", response_model=IssueResponse)
async def update_issue_status(
    issue_id: str,
    new_status: IssueStatus,
    db: Session = Depends(get_db)
):
    """Update issue status"""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Prevent changing status of promoted issues
    if issue.status == IssueStatus.PROMOTED and new_status != IssueStatus.PROMOTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change status of promoted issue. Update the associated task instead."
        )
    
    issue.status = new_status
    db.commit()
    db.refresh(issue)
    return issue


@router.get("/promoted", response_model=List[IssueResponse])
async def list_promoted_issues(
    project_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all promoted issues"""
    query = db.query(Issue).filter(Issue.status == IssueStatus.PROMOTED)
    
    if project_id:
        query = query.filter(Issue.project_id == project_id)
    
    query = query.order_by(Issue.updated_at.desc())
    
    issues = query.offset(skip).limit(limit).all()
    return issues
