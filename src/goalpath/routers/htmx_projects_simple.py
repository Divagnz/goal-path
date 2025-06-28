"""
HTMX Router for Projects - Simplified Version
Handles HTMX-specific project operations returning HTML fragments
"""

from typing import Optional
from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Project, Task

router = APIRouter(prefix="/htmx/projects", tags=["htmx-projects"])
templates = Jinja2Templates(directory="src/goalpath/templates")


@router.get("/list")
async def get_projects_list_htmx(
    request: Request,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get a list of project cards for dashboard updates."""
    
    try:
        # Build query
        query = db.query(Project)
        
        # Apply filters
        if status:
            query = query.filter(Project.status == status)
        if priority:
            query = query.filter(Project.priority == priority)
        if search:
            query = query.filter(
                Project.name.ilike(f"%{search}%") | 
                Project.description.ilike(f"%{search}%")
            )
        
        # Get projects
        projects = query.order_by(Project.updated_at.desc()).limit(limit).all()
        
        # Calculate statistics for each project
        for project in projects:
            total_tasks = db.query(Task).filter(Task.project_id == project.id).count()
            completed_tasks = (
                db.query(Task).filter(Task.project_id == project.id, Task.status == "done").count()
            )
            project.total_tasks = total_tasks
            project.completed_tasks = completed_tasks
            project.completion_percentage = (
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
            )

        context = {"request": request, "projects": projects}
        return templates.TemplateResponse("fragments/projects_list.html", context)

    except Exception as e:
        # Return error template
        context = {"request": request, "error": f"Error retrieving projects: {str(e)}"}
        return templates.TemplateResponse("fragments/error.html", context)


@router.post("/create")
async def create_project_htmx(
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new project via HTMX and return HTML fragment."""
    
    try:
        form_data = await request.form()
        
        # Create project data
        project_data = {
            "name": form_data.get("name", "").strip(),
            "description": form_data.get("description", "").strip(),
            "priority": form_data.get("priority", "medium"),
            "status": form_data.get("status", "active"),
            "start_date": form_data.get("start_date") if form_data.get("start_date") else None,
            "target_end_date": form_data.get("target_end_date") if form_data.get("target_end_date") else None,
            "created_by": "system"
        }

        # Validate required fields
        if not project_data["name"]:
            context = {"request": request, "error": "Project name is required"}
            return templates.TemplateResponse("fragments/error.html", context)

        # Create project in database
        new_project = Project(**{k: v for k, v in project_data.items() if v is not None})
        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        # Add statistics
        new_project.total_tasks = 0
        new_project.completed_tasks = 0
        new_project.completion_percentage = 0.0

        # Return success response
        response = templates.TemplateResponse(
            "fragments/project_card.html",
            {"request": request, "project": new_project}
        )
        response.headers["HX-Trigger"] = "projectCreated,closeModal"
        return response

    except Exception as e:
        context = {"request": request, "error": f"Error creating project: {str(e)}"}
        return templates.TemplateResponse("fragments/error.html", context)


@router.put("/{project_id}/status")
async def update_project_status_htmx(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update project status and return updated card."""
    
    try:
        form_data = await request.form()
        new_status = form_data.get("status")
        
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            context = {"request": request, "error": "Project not found"}
            return templates.TemplateResponse("fragments/error.html", context)
        
        project.status = new_status
        db.commit()
        db.refresh(project)
        
        # Calculate statistics
        total_tasks = db.query(Task).filter(Task.project_id == project.id).count()
        completed_tasks = (
            db.query(Task).filter(Task.project_id == project.id, Task.status == "done").count()
        )
        project.total_tasks = total_tasks
        project.completed_tasks = completed_tasks
        project.completion_percentage = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        )
        
        response = templates.TemplateResponse(
            "fragments/project_card.html",
            {"request": request, "project": project}
        )
        response.headers["HX-Trigger"] = "projectUpdated"
        return response

    except Exception as e:
        context = {"request": request, "error": f"Error updating project: {str(e)}"}
        return templates.TemplateResponse("fragments/error.html", context)


@router.delete("/{project_id}")
async def delete_project_htmx(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a project via HTMX and return empty response."""
    
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            context = {"request": request, "error": "Project not found"}
            return templates.TemplateResponse("fragments/error.html", context)

        project_name = project.name

        # Check if project has tasks
        task_count = db.query(Task).filter(Task.project_id == project_id).count()
        if task_count > 0:
            context = {
                "request": request, 
                "error": f"Cannot delete project '{project_name}' because it has {task_count} associated tasks."
            }
            return templates.TemplateResponse("fragments/error.html", context)

        # Delete the project
        db.delete(project)
        db.commit()

        # Return empty content to remove the element
        response = templates.TemplateResponse(
            "fragments/empty.html",
            {"request": request}
        )
        response.headers["HX-Trigger"] = "projectDeleted"
        return response

    except Exception as e:
        context = {"request": request, "error": f"Error deleting project: {str(e)}"}
        return templates.TemplateResponse("fragments/error.html", context)
