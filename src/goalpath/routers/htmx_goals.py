"""
HTMX routes for Goal management
Returns HTML fragments for dynamic page updates
"""

from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Goal, GoalProject, Project
from ..htmx_utils import render_template, is_htmx_request

router = APIRouter(prefix="/htmx/goals", tags=["htmx-goals"])
templates = Jinja2Templates(directory="src/goalpath/templates")


@router.get("/list")
async def goal_list_fragment(
    request: Request,
    status: Optional[str] = None,
    goal_type: Optional[str] = None,
    parent_goal_id: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Return goal list fragment"""
    query = db.query(Goal)
    
    # Apply filters
    if status:
        query = query.filter(Goal.status == status)
    if goal_type:
        query = query.filter(Goal.goal_type == goal_type)
    if parent_goal_id:
        query = query.filter(Goal.parent_goal_id == parent_goal_id)
    if search:
        query = query.filter(
            Goal.title.ilike(f"%{search}%") | 
            Goal.description.ilike(f"%{search}%")
        )
    
    # Order by creation date
    goals = query.order_by(Goal.created_at.desc()).all()
    
    # Calculate progress for each goal
    for goal in goals:
        project_links = db.query(GoalProject).filter(GoalProject.goal_id == goal.id).all()
        if project_links:
            total_weight = sum(float(link.weight) for link in project_links)
            weighted_progress = 0.0
            for link in project_links:
                # Calculate project completion
                from ..models import Task
                total_tasks = db.query(Task).filter(Task.project_id == link.project_id).count()
                completed_tasks = (
                    db.query(Task)
                    .filter(Task.project_id == link.project_id, Task.status == "done")
                    .count()
                )
                project_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
                weighted_progress += project_progress * float(link.weight)

            goal.calculated_progress = weighted_progress / total_weight if total_weight > 0 else 0.0
        else:
            goal.calculated_progress = float(goal.progress_percentage)

        goal.linked_projects = len(project_links)
    
    return templates.TemplateResponse(
        "fragments/goal_list.html",
        {"request": request, "goals": goals}
    )


@router.post("/create")
async def create_goal_fragment(
    request: Request,
    db: Session = Depends(get_db)
):
    """Create new goal and return updated list"""
    form_data = await request.form()
    
    goal_data = {
        "title": form_data.get("title"),
        "description": form_data.get("description"),
        "goal_type": form_data.get("goal_type", "short_term"),
        "status": form_data.get("status", "active"),
        "target_date": form_data.get("target_date") if form_data.get("target_date") else None,
        "parent_goal_id": form_data.get("parent_goal_id") if form_data.get("parent_goal_id") else None,
        "progress_percentage": 0.0
    }
    
    # Remove None values
    goal_data = {k: v for k, v in goal_data.items() if v is not None}
    
    goal = Goal(**goal_data)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    # Add calculated fields
    goal.calculated_progress = 0.0
    goal.linked_projects = 0
    
    # Return success response with HX-Trigger to refresh the list
    response = templates.TemplateResponse(
        "fragments/goal_card.html",
        {"request": request, "goal": goal}
    )
    response.headers["HX-Trigger"] = "goalCreated,closeModal"
    return response


@router.put("/{goal_id}/status")
async def update_goal_status_fragment(
    goal_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update goal status and return updated card"""
    form_data = await request.form()
    new_status = form_data.get("status")
    
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    goal.status = new_status
    db.commit()
    db.refresh(goal)
    
    # Calculate progress
    project_links = db.query(GoalProject).filter(GoalProject.goal_id == goal_id).all()
    if project_links:
        total_weight = sum(float(link.weight) for link in project_links)
        weighted_progress = 0.0
        for link in project_links:
            from ..models import Task
            total_tasks = db.query(Task).filter(Task.project_id == link.project_id).count()
            completed_tasks = (
                db.query(Task)
                .filter(Task.project_id == link.project_id, Task.status == "done")
                .count()
            )
            project_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
            weighted_progress += project_progress * float(link.weight)

        goal.calculated_progress = weighted_progress / total_weight if total_weight > 0 else 0.0
    else:
        goal.calculated_progress = float(goal.progress_percentage)

    goal.linked_projects = len(project_links)
    
    response = templates.TemplateResponse(
        "fragments/goal_card.html",
        {"request": request, "goal": goal}
    )
    response.headers["HX-Trigger"] = "goalUpdated"
    return response


@router.delete("/{goal_id}")
async def delete_goal_fragment(
    goal_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete goal and return empty fragment"""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    db.delete(goal)
    db.commit()
    
    # Return empty content with trigger to update counters
    response = templates.TemplateResponse(
        "fragments/empty.html",
        {"request": request}
    )
    response.headers["HX-Trigger"] = "goalDeleted"
    return response


@router.get("/{goal_id}")
async def goal_detail_fragment(
    goal_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Return goal detail fragment"""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Calculate progress
    project_links = db.query(GoalProject).filter(GoalProject.goal_id == goal_id).all()
    if project_links:
        total_weight = sum(float(link.weight) for link in project_links)
        weighted_progress = 0.0
        for link in project_links:
            from ..models import Task
            total_tasks = db.query(Task).filter(Task.project_id == link.project_id).count()
            completed_tasks = (
                db.query(Task)
                .filter(Task.project_id == link.project_id, Task.status == "done")
                .count()
            )
            project_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
            weighted_progress += project_progress * float(link.weight)

        goal.calculated_progress = weighted_progress / total_weight if total_weight > 0 else 0.0
    else:
        goal.calculated_progress = float(goal.progress_percentage)

    goal.linked_projects = len(project_links)
    
    return templates.TemplateResponse(
        "fragments/goal_detail.html",
        {"request": request, "goal": goal}
    )
