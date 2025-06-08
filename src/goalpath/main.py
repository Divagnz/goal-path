"""
GoalPath FastAPI Application
Enhanced main application with HTMX frontend support
"""

from datetime import date, datetime
from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import get_db, init_database
from .models import Goal, GoalProject, Project, Task
# Import extended models to ensure they are registered
from .models.extended import Issue, Reminder, TaskComment, TaskAttachment, ProjectContext, ScheduleEvent
from .routers import goals_router, projects_router, tasks_router
from .routers.htmx_projects import router as htmx_projects_router
from .routers.htmx_tasks import router as htmx_tasks_router

# Create FastAPI application
app = FastAPI(
    title="GoalPath",
    description="Enhanced Project Management System with FastAPI and HTMX",
    version="0.2.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Setup static files and templates
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

# Create directories if they don't exist
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Include API routers
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(goals_router)

# Include HTMX routers
app.include_router(htmx_projects_router)
app.include_router(htmx_tasks_router)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")


# Helper function to detect HTMX requests
def is_htmx_request(request: Request) -> bool:
    """Check if request is from HTMX"""
    return request.headers.get("HX-Request") == "true"


# Root route - Enhanced Dashboard
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Enhanced dashboard view with real-time stats"""

    # Get dashboard data
    projects = db.query(Project).order_by(Project.updated_at.desc()).limit(10).all()
    recent_tasks = db.query(Task).order_by(Task.updated_at.desc()).limit(15).all()
    active_goals = db.query(Goal).filter(Goal.status == "active").limit(6).all()

    # Calculate enhanced statistics
    total_projects = db.query(Project).count()
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.status == "done").count()

    # Calculate this week's completed tasks
    from datetime import timedelta

    week_start = date.today() - timedelta(days=date.today().weekday())
    tasks_completed_this_week = (
        db.query(Task)
        .filter(Task.status == "done", func.date(Task.updated_at) >= week_start)
        .count()
    )

    # Get today's tasks (tasks due today or overdue)
    today = date.today()
    todays_tasks = (
        db.query(Task)
        .filter(Task.due_date <= today, Task.status.in_(["todo", "in_progress"]))
        .limit(5)
        .all()
    )

    context = {
        "request": request,
        "projects": projects,
        "recent_tasks": recent_tasks,
        "active_goals": active_goals,
        "todays_tasks": todays_tasks,
        "stats": {
            "total_projects": total_projects,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round(
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1
            ),
            "tasks_completed_this_week": tasks_completed_this_week,
        },
    }

    # Return content fragment for HTMX requests, full page otherwise
    if is_htmx_request(request):
        return templates.TemplateResponse("fragments/dashboard_content.html", context)
    else:
        return templates.TemplateResponse("dashboard.html", context)


# Modal Routes for HTMX
@app.get("/modals/create-project", response_class=HTMLResponse)
async def create_project_modal(request: Request, db: Session = Depends(get_db)):
    """Create project modal"""
    context = {"request": request}
    return templates.TemplateResponse("modals/create_project.html", context)


@app.get("/modals/create-task", response_class=HTMLResponse)
async def create_task_modal(
    request: Request,
    project_id: str = None,
    parent_task_id: str = None,
    db: Session = Depends(get_db),
):
    """Create task modal with optional project and parent task pre-selection"""
    projects = db.query(Project).filter(Project.status == "active").all()
    parent_task = (
        db.query(Task).filter(Task.id == parent_task_id).first() if parent_task_id else None
    )

    # If parent task exists, auto-select its project
    if parent_task and not project_id:
        project_id = parent_task.project_id

    context = {
        "request": request,
        "projects": projects,
        "selected_project_id": project_id,
        "parent_task": parent_task,
        "parent_task_id": parent_task_id,
    }
    return templates.TemplateResponse("modals/create_task.html", context)


@app.get("/modals/create-goal", response_class=HTMLResponse)
async def create_goal_modal(request: Request, db: Session = Depends(get_db)):
    """Create goal modal"""
    projects = db.query(Project).filter(Project.status == "active").all()
    goals = db.query(Goal).filter(Goal.status == "active").all()
    context = {"request": request, "projects": projects, "goals": goals}
    return templates.TemplateResponse("modals/create_goal.html", context)


@app.get("/modals/edit-task/{task_id}", response_class=HTMLResponse)
async def edit_task_modal(task_id: str, request: Request, db: Session = Depends(get_db)):
    """Edit task modal"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    projects = db.query(Project).filter(Project.status == "active").all()
    context = {"request": request, "task": task, "projects": projects}
    return templates.TemplateResponse("modals/edit_task.html", context)


# Enhanced API endpoints for dashboard
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(request: Request, db: Session = Depends(get_db)):
    """Get real-time dashboard statistics"""

    # Calculate current stats
    total_projects = db.query(Project).count()
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.status == "done").count()

    # Calculate this week's stats
    from datetime import timedelta

    week_start = date.today() - timedelta(days=date.today().weekday())
    tasks_completed_this_week = (
        db.query(Task)
        .filter(Task.status == "done", func.date(Task.updated_at) >= week_start)
        .count()
    )

    # Get active goals for progress calculation
    active_goals = db.query(Goal).filter(Goal.status == "active").all()

    context = {
        "request": request,
        "active_goals": active_goals,
        "stats": {
            "total_projects": total_projects,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round(
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1
            ),
            "tasks_completed_this_week": tasks_completed_this_week,
        },
    }

    # Return HTML fragment for HTMX requests, JSON for API calls
    if is_htmx_request(request):
        return templates.TemplateResponse("fragments/dashboard_stats.html", context)
    else:
        return {
            "total_projects": total_projects,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round(
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1
            ),
            "tasks_completed_this_week": tasks_completed_this_week,
            "updated_at": datetime.now().isoformat(),
        }


# Projects page
@app.get("/projects", response_class=HTMLResponse)
async def projects_page(request: Request, db: Session = Depends(get_db)):
    """Projects management page"""
    projects = db.query(Project).order_by(Project.updated_at.desc()).all()

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

    # Return content fragment for HTMX requests, full page otherwise
    if is_htmx_request(request):
        return templates.TemplateResponse("fragments/projects_content.html", context)
    else:
        return templates.TemplateResponse("projects.html", context)


# Single project view
@app.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail(project_id: str, request: Request, db: Session = Depends(get_db)):
    """Single project detail view"""
    # Get the project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        # Handle project not found
        if is_htmx_request(request):
            context = {"request": request, "error": "Project not found"}
            return templates.TemplateResponse("fragments/error.html", context)
        else:
            raise HTTPException(status_code=404, detail="Project not found")

    # Get project tasks
    tasks = (
        db.query(Task).filter(Task.project_id == project_id).order_by(Task.created_at.desc()).all()
    )

    # Calculate project statistics
    total_tasks = len(tasks)
    completed_tasks = len([task for task in tasks if task.status == "done"])
    in_progress_tasks = len([task for task in tasks if task.status == "in_progress"])
    todo_tasks = len([task for task in tasks if task.status == "todo"])

    # Calculate progress percentage
    completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

    # Get linked goals
    goal_links = db.query(GoalProject).filter(GoalProject.project_id == project_id).all()
    linked_goals = []
    for link in goal_links:
        goal = db.query(Goal).filter(Goal.id == link.goal_id).first()
        if goal:
            goal.weight = link.weight
            linked_goals.append(goal)

    # Calculate task breakdown by status
    task_breakdown = {"todo": todo_tasks, "in_progress": in_progress_tasks, "done": completed_tasks}

    # Calculate task breakdown by priority
    priority_breakdown = {}
    for task in tasks:
        priority = task.priority
        priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1

    context = {
        "request": request,
        "project": project,
        "tasks": tasks,
        "project_tasks": tasks,  # For compatibility with project_detail.html template
        "linked_goals": linked_goals,
        "stats": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "todo_tasks": todo_tasks,
            "completion_percentage": round(completion_percentage, 1),
            "task_breakdown": task_breakdown,
            "priority_breakdown": priority_breakdown,
        },
    }

    # Return appropriate response type
    if is_htmx_request(request):
        return templates.TemplateResponse("fragments/project_detail_content.html", context)
    else:
        return templates.TemplateResponse("project_detail.html", context)


# Single task view
@app.get("/tasks/{task_id}", response_class=HTMLResponse)
async def task_detail(task_id: str, request: Request, db: Session = Depends(get_db)):
    """Single task detail view"""
    # Get the task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        # Handle task not found
        if is_htmx_request(request):
            context = {"request": request, "error": "Task not found"}
            return templates.TemplateResponse("fragments/error.html", context)
        else:
            raise HTTPException(status_code=404, detail="Task not found")

    # Get related project
    project = (
        db.query(Project).filter(Project.id == task.project_id).first() if task.project_id else None
    )

    # Get subtasks if this is a parent task
    subtasks = (
        db.query(Task).filter(Task.parent_task_id == task_id).order_by(Task.created_at.desc()).all()
    )

    # Get parent task if this is a subtask
    parent_task = (
        db.query(Task).filter(Task.id == task.parent_task_id).first()
        if task.parent_task_id
        else None
    )

    # Get related tasks in same project (excluding current task and subtasks)
    related_tasks = []
    if project:
        related_tasks = (
            db.query(Task)
            .filter(
                Task.project_id == project.id, Task.id != task_id, Task.parent_task_id != task_id
            )
            .limit(5)
            .all()
        )

    context = {
        "request": request,
        "task": task,
        "project": project,
        "subtasks": subtasks,
        "parent_task": parent_task,
        "related_tasks": related_tasks,
        "subtask_count": len(subtasks),
        "completion_stats": {
            "total_subtasks": len(subtasks),
            "completed_subtasks": len([st for st in subtasks if st.status == "done"]),
            "completion_percentage": (
                (len([st for st in subtasks if st.status == "done"]) / len(subtasks) * 100)
                if subtasks
                else 0
            ),
        },
    }

    # Return appropriate response type
    if is_htmx_request(request):
        return templates.TemplateResponse("fragments/task_detail_content.html", context)
    else:
        return templates.TemplateResponse("task_detail.html", context)


# Tasks page
@app.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request, db: Session = Depends(get_db)):
    """Tasks management page"""
    tasks = db.query(Task).order_by(Task.updated_at.desc()).all()
    projects = db.query(Project).all()

    context = {"request": request, "tasks": tasks, "projects": projects}

    # Return content fragment for HTMX requests, full page otherwise
    if is_htmx_request(request):
        return templates.TemplateResponse("fragments/tasks_content.html", context)
    else:
        return templates.TemplateResponse("tasks.html", context)


# Goals page
@app.get("/goals", response_class=HTMLResponse)
async def goals_page(request: Request, db: Session = Depends(get_db)):
    """Goals management page"""
    goals = db.query(Goal).order_by(Goal.updated_at.desc()).all()

    # Calculate progress for each goal
    for goal in goals:
        project_links = db.query(GoalProject).filter(GoalProject.goal_id == goal.id).all()
        if project_links:
            total_weight = sum(float(link.weight) for link in project_links)
            weighted_progress = 0.0
            for link in project_links:
                # Calculate project completion
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

    context = {"request": request, "goals": goals}

    # Return content fragment for HTMX requests, full page otherwise
    if is_htmx_request(request):
        return templates.TemplateResponse("fragments/goals_content.html", context)
    else:
        return templates.TemplateResponse("goals.html", context)


# Analytics page
@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request, db: Session = Depends(get_db)):
    """Analytics and reporting page"""
    # Get analytics data
    projects = db.query(Project).all()
    tasks = db.query(Task).all()
    goals = db.query(Goal).all()

    # Calculate analytics
    project_status_counts = {}
    task_status_counts = {}
    task_priority_counts = {}

    for project in projects:
        status = project.status
        project_status_counts[status] = project_status_counts.get(status, 0) + 1

    for task in tasks:
        status = task.status
        priority = task.priority
        task_status_counts[status] = task_status_counts.get(status, 0) + 1
        task_priority_counts[priority] = task_priority_counts.get(priority, 0) + 1

    context = {
        "request": request,
        "analytics": {
            "project_status_counts": project_status_counts,
            "task_status_counts": task_status_counts,
            "task_priority_counts": task_priority_counts,
            "total_projects": len(projects),
            "total_tasks": len(tasks),
            "total_goals": len(goals),
        },
    }

    # Return content fragment for HTMX requests, full page otherwise
    if is_htmx_request(request):
        return templates.TemplateResponse("fragments/analytics_content.html", context)
    else:
        return templates.TemplateResponse("analytics.html", context)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "app": "goalpath", "version": "0.2.0"}


# Quick task endpoint for dashboard
@app.post("/api/quick-task")
async def create_quick_task(request: Request, db: Session = Depends(get_db)):
    """Create a quick task from dashboard"""
    form_data = await request.form()

    task_data = {
        "title": form_data.get("title"),
        "priority": form_data.get("priority", "medium"),
        "project_id": form_data.get("project_id") if form_data.get("project_id") else None,
        "task_type": "task",
        "status": "todo",
        "created_by": "system",
    }

    # Remove None values
    task_data = {k: v for k, v in task_data.items() if v is not None}

    new_task = Task(**task_data)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {"message": "Task created successfully", "task_id": new_task.id}


def main():
    """Main entry point for production"""
    uvicorn.run("goalpath.main:app", host="0.0.0.0", port=8000, log_level="info")


def dev():
    """Development entry point with auto-reload"""
    uvicorn.run("goalpath.main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")


if __name__ == "__main__":
    dev()
