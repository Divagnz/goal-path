"""
Epic management routes for GoalPath
Handles high-level feature development tracking
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..database import get_db
from ..models.epics import Epic, EpicStatus, EpicPriority
from ..schemas import EpicCreate, EpicUpdate, EpicResponse, EpicListResponse

router = APIRouter(prefix="/api/epics", tags=["epics"])


@router.get("/", response_model=List[EpicResponse])
async def list_epics(
    project_id: Optional[str] = None,
    status: Optional[EpicStatus] = None,
    priority: Optional[EpicPriority] = None,
    assigned_to: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List epics with optional filtering"""
    query = db.query(Epic)
    
    # Apply filters
    if project_id:
        query = query.filter(Epic.project_id == project_id)
    if status:
        query = query.filter(Epic.status == status)
    if priority:
        query = query.filter(Epic.priority == priority)
    if assigned_to:
        query = query.filter(Epic.assigned_to == assigned_to)
    
    # Order by priority and creation date
    query = query.order_by(
        Epic.priority.desc(),
        Epic.created_at.desc()
    )
    
    epics = query.offset(skip).limit(limit).all()
    return epics


@router.get("/{epic_id}", response_model=EpicResponse)
async def get_epic(epic_id: str, db: Session = Depends(get_db)):
    """Get a specific epic by ID"""
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Epic not found"
        )
    return epic


@router.post("/", response_model=EpicResponse, status_code=status.HTTP_201_CREATED)
async def create_epic(epic_data: EpicCreate, db: Session = Depends(get_db)):
    """Create a new epic"""
    epic = Epic(**epic_data.dict())
    db.add(epic)
    db.commit()
    db.refresh(epic)
    return epic


@router.put("/{epic_id}", response_model=EpicResponse)
async def update_epic(
    epic_id: str, 
    epic_data: EpicUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing epic"""
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Epic not found"
        )
    
    # Update fields
    update_data = epic_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(epic, field, value)
    
    db.commit()
    db.refresh(epic)
    return epic


@router.delete("/{epic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_epic(epic_id: str, db: Session = Depends(get_db)):
    """Delete an epic"""
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Epic not found"
        )
    
    db.delete(epic)
    db.commit()


@router.get("/{epic_id}/milestones")
async def get_epic_milestones(epic_id: str, db: Session = Depends(get_db)):
    """Get all milestones for a specific epic"""
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Epic not found"
        )
    
    return epic.milestones


@router.get("/{epic_id}/tasks")
async def get_epic_tasks(epic_id: str, db: Session = Depends(get_db)):
    """Get all tasks for a specific epic"""
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Epic not found"
        )
    
    return epic.tasks


@router.put("/{epic_id}/status", response_model=EpicResponse)
async def update_epic_status(
    epic_id: str,
    status: EpicStatus,
    db: Session = Depends(get_db)
):
    """Update epic status"""
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Epic not found"
        )
    
    epic.status = status
    db.commit()
    db.refresh(epic)
    return epic
