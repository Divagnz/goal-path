"""
HTMX routes for Epic management
Returns HTML fragments for dynamic page updates
"""

from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.epics import Epic, EpicStatus, EpicPriority
from ..htmx_utils import render_template, is_htmx_request

router = APIRouter(prefix="/htmx/epics", tags=["htmx-epics"])
templates = Jinja2Templates(directory="src/goalpath/templates")


@router.get("/list")
async def epic_list_fragment(
    request: Request,
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Return epic list fragment"""
    query = db.query(Epic)
    
    # Apply filters
    if project_id:
        query = query.filter(Epic.project_id == project_id)
    if status:
        query = query.filter(Epic.status == status)
    if priority:
        query = query.filter(Epic.priority == priority)
    if assigned_to:
        query = query.filter(Epic.assigned_to.ilike(f"%{assigned_to}%"))
    if search:
        query = query.filter(
            Epic.title.ilike(f"%{search}%") | 
            Epic.description.ilike(f"%{search}%")
        )
    
    # Order by priority and creation date
    epics = query.order_by(
        Epic.priority.desc(),
        Epic.created_at.desc()
    ).all()
    
    # Calculate related counts for each epic
    for epic in epics:
        epic.milestone_count = len(epic.milestones)
        epic.task_count = len(epic.tasks)
        
        # Calculate completion percentage based on milestones and tasks
        total_items = epic.milestone_count + epic.task_count
        if total_items > 0:
            completed_milestones = len([m for m in epic.milestones if m.status == 'completed'])
            completed_tasks = len([t for t in epic.tasks if t.status == 'done'])
            epic.completion_percentage = ((completed_milestones + completed_tasks) / total_items) * 100
        else:
            epic.completion_percentage = 0.0
    
    return templates.TemplateResponse(
        "fragments/epic_list.html",
        {"request": request, "epics": epics}
    )


@router.post("/create")
async def create_epic_fragment(
    request: Request,
    db: Session = Depends(get_db)
):
    """Create new epic and return updated list"""
    form_data = await request.form()
    
    epic_data = {
        "title": form_data.get("title"),
        "description": form_data.get("description"),
        "project_id": form_data.get("project_id"),
        "status": form_data.get("status", EpicStatus.PLANNING),
        "priority": form_data.get("priority", EpicPriority.MEDIUM),
        "assigned_to": form_data.get("assigned_to") if form_data.get("assigned_to") else None,
        "story_points": int(form_data.get("story_points")) if form_data.get("story_points") else None,
        "estimated_hours": float(form_data.get("estimated_hours")) if form_data.get("estimated_hours") else None,
        "start_date": form_data.get("start_date") if form_data.get("start_date") else None,
        "target_end_date": form_data.get("target_end_date") if form_data.get("target_end_date") else None,
        "created_by": "system"  # TODO: Get from authenticated user
    }
    
    # Remove None values
    epic_data = {k: v for k, v in epic_data.items() if v is not None}
    
    epic = Epic(**epic_data)
    db.add(epic)
    db.commit()
    db.refresh(epic)
    
    # Calculate related metrics
    epic.milestone_count = 0
    epic.task_count = 0
    epic.completion_percentage = 0.0
    
    # Return success response that triggers list refresh
    response = templates.TemplateResponse(
        "fragments/epic_card.html",
        {"request": request, "epic": epic}
    )
    response.headers["HX-Trigger"] = "epicCreated,closeModal"
    return response


@router.put("/{epic_id}/status")
async def update_epic_status_fragment(
    epic_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update epic status and return updated card"""
    form_data = await request.form()
    new_status = form_data.get("status")
    
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")
    
    epic.status = new_status
    db.commit()
    db.refresh(epic)
    
    # Calculate updated metrics
    epic.milestone_count = len(epic.milestones) if hasattr(epic, 'milestones') else 0
    epic.task_count = len(epic.tasks) if hasattr(epic, 'tasks') else 0
    
    total_items = epic.milestone_count + epic.task_count
    if total_items > 0:
        completed_milestones = len([m for m in epic.milestones if m.status == 'completed']) if hasattr(epic, 'milestones') else 0
        completed_tasks = len([t for t in epic.tasks if t.status == 'done']) if hasattr(epic, 'tasks') else 0
        epic.completion_percentage = ((completed_milestones + completed_tasks) / total_items) * 100
    else:
        epic.completion_percentage = 0.0
    
    response = templates.TemplateResponse(
        "fragments/epic_card.html",
        {"request": request, "epic": epic}
    )
    response.headers["HX-Trigger"] = "epicUpdated"
    return response


@router.delete("/{epic_id}")
async def delete_epic_fragment(
    epic_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete epic and return empty fragment"""
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")
    
    db.delete(epic)
    db.commit()
    
    # Return empty content with trigger to update counters
    response = templates.TemplateResponse(
        "fragments/empty.html",
        {"request": request}
    )
    response.headers["HX-Trigger"] = "epicDeleted"
    return response


@router.get("/{epic_id}")
async def epic_detail_fragment(
    epic_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Return epic detail fragment"""
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")
    
    # Calculate metrics
    epic.milestone_count = len(epic.milestones)
    epic.task_count = len(epic.tasks)
    
    total_items = epic.milestone_count + epic.task_count
    if total_items > 0:
        completed_milestones = len([m for m in epic.milestones if m.status == 'completed'])
        completed_tasks = len([t for t in epic.tasks if t.status == 'done'])
        epic.completion_percentage = ((completed_milestones + completed_tasks) / total_items) * 100
    else:
        epic.completion_percentage = 0.0
    
    return templates.TemplateResponse(
        "fragments/epic_detail.html",
        {"request": request, "epic": epic}
    )


@router.get("/{epic_id}/milestones")
async def epic_milestones_fragment(
    epic_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Return epic milestones fragment"""
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")
    
    milestones = epic.milestones
    
    return templates.TemplateResponse(
        "fragments/milestone_list.html",
        {"request": request, "milestones": milestones, "epic": epic}
    )


@router.get("/{epic_id}/tasks")
async def epic_tasks_fragment(
    epic_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Return epic tasks fragment"""
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")
    
    tasks = epic.tasks
    
    return templates.TemplateResponse(
        "fragments/task_list.html",
        {"request": request, "tasks": tasks, "epic": epic}
    )
