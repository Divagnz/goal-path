"""
GoalPath FastAPI Application
Main application entry point with routing and configuration
"""

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import uvicorn
from pathlib import Path

from .database import get_db, init_database
from .models import Project, Task, Goal
from .routers import projects_router, tasks_router, goals_router

# Create FastAPI application
app = FastAPI(
    title="GoalPath",
    description="Project Management System with FastAPI and HTMX",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
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

# CORS middleware for development
from fastapi.middleware.cors import CORSMiddleware

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

# Root route - Dashboard
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard view"""
    
    # Get dashboard data
    projects = db.query(Project).limit(5).all()
    recent_tasks = db.query(Task).order_by(Task.updated_at.desc()).limit(10).all()
    active_goals = db.query(Goal).filter(Goal.status == "active").limit(5).all()
    
    # Calculate statistics
    total_projects = db.query(Project).count()
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.status == "done").count()
    
    context = {
        "request": request,
        "projects": projects,
        "recent_tasks": recent_tasks,
        "active_goals": active_goals,
        "stats": {
            "total_projects": total_projects,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
        }
    }
    
    return templates.TemplateResponse("dashboard.html", context)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "app": "goalpath"}

# API Routes (will be expanded)
@app.get("/api/projects")
async def list_projects(db: Session = Depends(get_db)):
    """List all projects"""
    projects = db.query(Project).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "status": p.status,
            "priority": p.priority,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in projects
    ]

@app.get("/api/tasks")
async def list_tasks(project_id: str = None, db: Session = Depends(get_db)):
    """List tasks, optionally filtered by project"""
    query = db.query(Task)
    if project_id:
        query = query.filter(Task.project_id == project_id)
    
    tasks = query.all()
    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "project_id": t.project_id,
            "parent_task_id": t.parent_task_id,
            "due_date": t.due_date.isoformat() if t.due_date else None
        }
        for t in tasks
    ]

@app.get("/api/goals")
async def list_goals(db: Session = Depends(get_db)):
    """List all goals"""
    goals = db.query(Goal).all()
    return [
        {
            "id": g.id,
            "title": g.title,
            "description": g.description,
            "status": g.status,
            "goal_type": g.goal_type,
            "progress_percentage": float(g.progress_percentage) if g.progress_percentage else 0.0,
            "target_date": g.target_date.isoformat() if g.target_date else None
        }
        for g in goals
    ]

def main():
    """Main entry point for production"""
    uvicorn.run(
        "goalpath.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

def dev():
    """Development entry point with auto-reload"""
    uvicorn.run(
        "goalpath.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )

if __name__ == "__main__":
    dev()
