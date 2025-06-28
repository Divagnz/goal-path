"""
HTMX routes for milestone management
Handles milestone interactions and fragment updates
"""

from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import date, datetime, timedelta

from ..database import get_db
from ..models.epics import Milestone, MilestoneStatus, Epic
from ..models import Project
from ..schemas import MilestoneCreate, MilestoneUpdate
from ..htmx_utils import render_template

router = APIRouter(prefix="/htmx/milestones", tags=["htmx-milestones"])


@router.get("/list", response_class=HTMLResponse)
async def list_milestones_htmx(
    request: Request,
    epic_id: Optional[str] = None,
    status: Optional[str] = None,
    due_filter: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Return milestone cards as HTML fragments"""
    query = db.query(Milestone).join(Epic).join(Project)
    
    # Apply filters
    if epic_id:
        query = query.filter(Milestone.epic_id == epic_id)
    if status:
        query = query.filter(Milestone.status == status)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Milestone.title.ilike(search_term),
                Milestone.description.ilike(search_term),
                Epic.title.ilike(search_term)
            )
        )
    
    # Apply due date filter
    today = date.today()
    if due_filter == "overdue":
        query = query.filter(
            and_(
                Milestone.due_date < today,
                Milestone.status != MilestoneStatus.COMPLETED
            )
        )
    elif due_filter == "this-week":
        week_end = today + timedelta(days=7)
        query = query.filter(
            and_(
                Milestone.due_date >= today,
                Milestone.due_date <= week_end
            )
        )
    elif due_filter == "this-month":
        month_end = today + timedelta(days=30)
        query = query.filter(
            and_(
                Milestone.due_date >= today,
                Milestone.due_date <= month_end
            )
        )
    elif due_filter == "next-month":
        month_start = today + timedelta(days=30)
        month_end = today + timedelta(days=60)
        query = query.filter(
            and_(
                Milestone.due_date >= month_start,
                Milestone.due_date <= month_end
            )
        )
    
    # Order by due date and status
    query = query.order_by(
        Milestone.due_date.asc(),
        Milestone.order_index.asc(),
        Milestone.created_at.desc()
    )
    
    milestones = query.all()
    
    return render_template(
        "fragments/milestone_cards.html",
        request=request,
        milestones=milestones,
        today=today
    )


@router.get("/timeline", response_class=HTMLResponse)
async def milestones_timeline_htmx(
    request: Request,
    epic_id: Optional[str] = None,
    project_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Return milestone timeline as HTML fragment"""
    query = db.query(Milestone).join(Epic).join(Project)
    
    # Apply filters
    if epic_id:
        query = query.filter(Milestone.epic_id == epic_id)
    if project_id:
        query = query.filter(Milestone.project_id == project_id)
    
    # Only show milestones with due dates for timeline
    query = query.filter(Milestone.due_date.isnot(None))
    
    # Order by due date
    query = query.order_by(Milestone.due_date.asc())
    
    milestones = query.all()
    
    # Group milestones by month for timeline display
    timeline_months = {}
    for milestone in milestones:
        if milestone.due_date:
            month_key = milestone.due_date.strftime("%Y-%m")
            month_name = milestone.due_date.strftime("%B %Y")
            
            if month_key not in timeline_months:
                timeline_months[month_key] = {
                    "name": month_name,
                    "milestones": []
                }
            timeline_months[month_key]["milestones"].append(milestone)
    
    return render_template(
        "fragments/milestone_timeline.html",
        request=request,
        timeline_months=timeline_months,
        today=date.today()
    )


@router.post("/create", response_class=HTMLResponse)
async def create_milestone_htmx(
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new milestone and return updated list"""
    try:
        form_data = await request.form()
        
        # Extract form data
        epic_id = form_data.get("epic_id")
        if not epic_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Epic ID is required"
            )
        
        # Validate epic exists
        epic = db.query(Epic).filter(Epic.id == epic_id).first()
        if not epic:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Epic not found"
            )
        
        # Create milestone data
        milestone_data = {
            "title": form_data.get("title"),
            "description": form_data.get("description"),
            "epic_id": epic_id,
            "project_id": epic.project_id,  # Set project_id from epic
            "status": form_data.get("status", "planned"),
            "due_date": form_data.get("due_date") if form_data.get("due_date") else None,
            "progress_percentage": float(form_data.get("progress_percentage", 0)),
            "order_index": int(form_data.get("order_index", 0)),
            "created_by": "system"  # TODO: Get from authenticated user
        }
        
        # Remove None values except for explicitly allowed ones
        milestone_data = {k: v for k, v in milestone_data.items() if v is not None or k in ["due_date", "description"]}
        
        # Create milestone
        milestone = Milestone(**milestone_data)
        
        db.add(milestone)
        db.commit()
        db.refresh(milestone)
        
        # Return success fragment
        return render_template(
            "fragments/milestone_success.html",
            request=request,
            milestone=milestone,
            message="Milestone created successfully!"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{milestone_id}/status", response_class=HTMLResponse)
async def update_milestone_status_htmx(
    milestone_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update milestone status and return updated card"""
    form_data = await request.form()
    new_status = form_data.get("status")
    
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    
    # Validate status
    try:
        status_enum = MilestoneStatus(new_status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )
    
    # Update status
    milestone.status = status_enum
    
    # Set completion date if completed
    if status_enum == MilestoneStatus.COMPLETED and not milestone.completed_date:
        milestone.completed_date = datetime.now()
        milestone.progress_percentage = 100.0
    elif status_enum != MilestoneStatus.COMPLETED:
        milestone.completed_date = None
        if milestone.progress_percentage == 100.0:
            milestone.progress_percentage = 90.0  # Reset to near completion
    
    db.commit()
    db.refresh(milestone)
    
    return render_template(
        "fragments/milestone_card.html",
        request=request,
        milestone=milestone,
        today=date.today()
    )


@router.put("/{milestone_id}/progress", response_class=HTMLResponse)
async def update_milestone_progress_htmx(
    milestone_id: str,
    request: Request,
    progress: float,
    db: Session = Depends(get_db)
):
    """Update milestone progress and return updated progress bar"""
    if not 0 <= progress <= 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Progress must be between 0 and 100"
        )
    
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    
    # Update progress
    milestone.progress_percentage = progress
    
    # Auto-complete if 100%
    if progress == 100.0 and milestone.status != MilestoneStatus.COMPLETED:
        milestone.status = MilestoneStatus.COMPLETED
        milestone.completed_date = datetime.now()
    elif progress < 100.0 and milestone.status == MilestoneStatus.COMPLETED:
        milestone.status = MilestoneStatus.ACTIVE
        milestone.completed_date = None
    
    db.commit()
    db.refresh(milestone)
    
    return render_template(
        "fragments/milestone_progress.html",
        request=request,
        milestone=milestone
    )


@router.delete("/{milestone_id}", response_class=HTMLResponse)
async def delete_milestone_htmx(
    milestone_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete milestone and return empty fragment"""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    
    db.delete(milestone)
    db.commit()
    
    # Return empty fragment to remove the card
    return HTMLResponse("")


@router.get("/{milestone_id}/edit", response_class=HTMLResponse)
async def edit_milestone_form_htmx(
    milestone_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Return edit form for milestone"""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    
    # Get available epics for dropdown
    epics = db.query(Epic).filter(Epic.project_id == milestone.project_id).all()
    
    return render_template(
        "fragments/milestone_edit_form.html",
        request=request,
        milestone=milestone,
        epics=epics
    )


@router.put("/{milestone_id}/edit", response_class=HTMLResponse)
async def update_milestone_htmx(
    milestone_id: str,
    request: Request,
    milestone_data: MilestoneUpdate,
    db: Session = Depends(get_db)
):
    """Update milestone and return updated card"""
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
    
    return render_template(
        "fragments/milestone_card.html",
        request=request,
        milestone=milestone,
        today=date.today()
    )


# Modal routes
@router.get("/modals/create", response_class=HTMLResponse)
async def create_milestone_modal_htmx(
    request: Request,
    epic_id: Optional[str] = None,
    project_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Return create milestone modal"""
    # Get available epics
    query = db.query(Epic)
    if project_id:
        query = query.filter(Epic.project_id == project_id)
    epics = query.all()
    
    # Get available projects
    projects = db.query(Project).all()
    
    return render_template(
        "modals/create_milestone.html",
        request=request,
        epics=epics,
        projects=projects,
        selected_epic_id=epic_id,
        selected_project_id=project_id
    )


@router.get("/stats", response_class=HTMLResponse)
async def milestone_stats_htmx(
    request: Request,
    epic_id: Optional[str] = None,
    project_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Return milestone statistics fragment"""
    query = db.query(Milestone)
    
    if epic_id:
        query = query.filter(Milestone.epic_id == epic_id)
    if project_id:
        query = query.filter(Milestone.project_id == project_id)
    
    milestones = query.all()
    
    # Calculate statistics
    total_milestones = len(milestones)
    completed_milestones = len([m for m in milestones if m.status == MilestoneStatus.COMPLETED])
    overdue_milestones = len([
        m for m in milestones 
        if m.due_date and m.due_date < date.today() and m.status != MilestoneStatus.COMPLETED
    ])
    
    avg_progress = 0.0
    if milestones:
        avg_progress = sum(m.progress_percentage for m in milestones) / len(milestones)
    
    return render_template(
        "fragments/milestone_stats.html",
        request=request,
        total_milestones=total_milestones,
        completed_milestones=completed_milestones,
        overdue_milestones=overdue_milestones,
        avg_progress=avg_progress,
        completion_rate=completed_milestones / total_milestones * 100 if total_milestones > 0 else 0
    )
