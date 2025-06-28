"""
Milestone management routes for GoalPath
Handles milestone tracking within epics
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..database import get_db
from ..models.epics import Epic, Milestone, MilestoneStatus
from ..schemas import MilestoneCreate, MilestoneUpdate, MilestoneResponse

router = APIRouter(prefix="/api/milestones", tags=["milestones"])


@router.get("/", response_model=List[MilestoneResponse])
async def list_milestones(
    project_id: Optional[str] = None,
    epic_id: Optional[str] = None,
    status: Optional[MilestoneStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List milestones with optional filtering"""
    query = db.query(Milestone)
    
    # Apply filters
    if project_id:
        query = query.filter(Milestone.project_id == project_id)
    if epic_id:
        query = query.filter(Milestone.epic_id == epic_id)
    if status:
        query = query.filter(Milestone.status == status)
    
    # Order by due date and creation date
    query = query.order_by(
        Milestone.due_date.asc(),
        Milestone.order_index.asc(),
        Milestone.created_at.desc()
    )
    
    milestones = query.offset(skip).limit(limit).all()
    return milestones


@router.get("/{milestone_id}", response_model=MilestoneResponse)
async def get_milestone(milestone_id: str, db: Session = Depends(get_db)):
    """Get a specific milestone by ID"""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    return milestone


@router.post("/", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_milestone(milestone_data: MilestoneCreate, db: Session = Depends(get_db)):
    """Create a new milestone with automatic project_id derivation from epic"""
    # First, lookup the epic to get the project_id
    epic = db.query(Epic).filter(Epic.id == milestone_data.epic_id).first()
    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Epic not found with id: {milestone_data.epic_id}"
        )
    
    # Create milestone data with project_id derived from epic
    milestone_dict = milestone_data.dict()
    
    # If project_id was provided, validate it matches the epic's project
    if milestone_data.project_id is not None:
        if milestone_data.project_id != epic.project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project ID mismatch: epic belongs to project {epic.project_id}, but {milestone_data.project_id} was provided"
            )
    
    # Always use the epic's project_id to ensure consistency
    milestone_dict["project_id"] = epic.project_id
    
    milestone = Milestone(**milestone_dict)
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


@router.put("/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: str, 
    milestone_data: MilestoneUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing milestone"""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    
    # Update fields
    update_data = milestone_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(milestone, field, value)
    
    db.commit()
    db.refresh(milestone)
    return milestone


@router.delete("/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_milestone(milestone_id: str, db: Session = Depends(get_db)):
    """Delete a milestone"""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    
    db.delete(milestone)
    db.commit()


@router.get("/{milestone_id}/tasks")
async def get_milestone_tasks(milestone_id: str, db: Session = Depends(get_db)):
    """Get all tasks for a specific milestone"""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    
    return milestone.tasks


@router.put("/{milestone_id}/status", response_model=MilestoneResponse)
async def update_milestone_status(
    milestone_id: str,
    status: MilestoneStatus,
    db: Session = Depends(get_db)
):
    """Update milestone status"""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    
    milestone.status = status
    db.commit()
    db.refresh(milestone)
    return milestone


@router.put("/{milestone_id}/progress", response_model=MilestoneResponse)
async def update_milestone_progress(
    milestone_id: str,
    progress_percentage: float,
    db: Session = Depends(get_db)
):
    """Update milestone progress"""
    if not 0 <= progress_percentage <= 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Progress percentage must be between 0 and 100"
        )
        
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    
    milestone.progress_percentage = progress_percentage
    db.commit()
    db.refresh(milestone)
    return milestone
