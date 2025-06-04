"""
Projects API Router - Mock/Fixed Responses
This module contains fixed responses for testing API structure
TODO: Replace with actual database logic
"""

from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from ..schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectFilters,
    MessageResponse, ErrorResponse, PaginatedResponse
)
from ..database import get_db

router = APIRouter(prefix="/api/projects", tags=["projects"])

# Mock data for testing
MOCK_PROJECTS = [
    {
        "id": "proj-001",
        "name": "Website Redesign",
        "description": "Complete overhaul of company website with modern design and improved UX",
        "status": "active",
        "priority": "high",
        "start_date": "2025-01-15",
        "target_end_date": "2025-08-31",
        "actual_end_date": None,
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-06-03T15:30:00Z",
        "created_by": "user_001",
        "total_tasks": 15,
        "completed_tasks": 8,
        "completion_percentage": 53.3
    },
    {
        "id": "proj-002", 
        "name": "Mobile App Development",
        "description": "Native iOS and Android applications for customer portal",
        "status": "active",
        "priority": "critical",
        "start_date": "2025-02-01",
        "target_end_date": "2025-12-15",
        "actual_end_date": None,
        "created_at": "2025-02-01T09:00:00Z",
        "updated_at": "2025-06-03T12:15:00Z",
        "created_by": "user_002",
        "total_tasks": 28,
        "completed_tasks": 5,
        "completion_percentage": 17.9
    },
    {
        "id": "proj-003",
        "name": "Database Migration",
        "description": "Migrate from MySQL to PostgreSQL for better performance",
        "status": "completed",
        "priority": "medium",
        "start_date": "2025-03-01",
        "target_end_date": "2025-06-30",
        "actual_end_date": "2025-05-20",
        "created_at": "2025-03-01T08:00:00Z",
        "updated_at": "2025-05-20T16:45:00Z",
        "created_by": "user_003",
        "total_tasks": 12,
        "completed_tasks": 12,
        "completion_percentage": 100.0
    }
]

@router.get("/", response_model=List[ProjectResponse], summary="List all projects")
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
) -> List[ProjectResponse]:
    """
    Get all projects with optional filtering and pagination.
    
    **Fixed Response**: Returns mock project data for testing.
    TODO: Implement actual database queries with filtering.
    """
    
    # TODO: Replace with actual database query
    # Example of what the real implementation will look like:
    # query = db.query(Project)
    # if status:
    #     query = query.filter(Project.status == status)
    # if priority:
    #     query = query.filter(Project.priority == priority)
    # if search:
    #     query = query.filter(Project.name.contains(search))
    # projects = query.offset((page-1)*size).limit(size).all()
    
    # For now, return filtered mock data
    filtered_projects = MOCK_PROJECTS.copy()
    
    if status:
        filtered_projects = [p for p in filtered_projects if p["status"] == status]
    if priority:
        filtered_projects = [p for p in filtered_projects if p["priority"] == priority]
    if search:
        search_lower = search.lower()
        filtered_projects = [
            p for p in filtered_projects 
            if search_lower in p["name"].lower() or search_lower in (p["description"] or "").lower()
        ]
    
    # Simulate pagination
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_projects = filtered_projects[start_idx:end_idx]
    
    return [ProjectResponse(**project) for project in paginated_projects]

@router.get("/{project_id}", response_model=ProjectResponse, summary="Get project by ID")
async def get_project(
    project_id: str,
    db: Session = Depends(get_db)
) -> ProjectResponse:
    """
    Get a specific project by ID.
    
    **Fixed Response**: Returns mock project data for testing.
    TODO: Implement actual database lookup.
    """
    
    # TODO: Replace with actual database query
    # project = db.query(Project).filter(Project.id == project_id).first()
    # if not project:
    #     raise HTTPException(status_code=404, detail="Project not found")
    # return project
    
    # For now, return mock data
    project = next((p for p in MOCK_PROJECTS if p["id"] == project_id), None)
    
    if not project:
        raise HTTPException(
            status_code=404, 
            detail=f"Project with ID {project_id} not found"
        )
    
    return ProjectResponse(**project)

@router.post("/", response_model=ProjectResponse, status_code=201, summary="Create new project")
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
) -> ProjectResponse:
    """
    Create a new project.
    
    **Fixed Response**: Returns mock created project for testing.
    TODO: Implement actual database creation.
    """
    
    # TODO: Replace with actual database creation
    # new_project = Project(**project.dict())
    # db.add(new_project)
    # db.commit()
    # db.refresh(new_project)
    # return new_project
    
    # For now, return mock created project
    new_project_data = {
        "id": f"proj-{len(MOCK_PROJECTS) + 1:03d}",
        **project.dict(),
        "actual_end_date": None,
        "created_at": datetime.now().isoformat() + "Z",
        "updated_at": datetime.now().isoformat() + "Z",
        "created_by": "current_user",
        "total_tasks": 0,
        "completed_tasks": 0,
        "completion_percentage": 0.0
    }
    
    # Add to mock data for session persistence
    MOCK_PROJECTS.append(new_project_data)
    
    return ProjectResponse(**new_project_data)

@router.put("/{project_id}", response_model=ProjectResponse, summary="Update project")
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db)
) -> ProjectResponse:
    """
    Update an existing project.
    
    **Fixed Response**: Returns mock updated project for testing.
    TODO: Implement actual database update.
    """
    
    # TODO: Replace with actual database update
    # project = db.query(Project).filter(Project.id == project_id).first()
    # if not project:
    #     raise HTTPException(status_code=404, detail="Project not found")
    # 
    # for field, value in project_update.dict(exclude_unset=True).items():
    #     setattr(project, field, value)
    # 
    # db.commit()
    # db.refresh(project)
    # return project
    
    # For now, update mock data
    project_idx = next((i for i, p in enumerate(MOCK_PROJECTS) if p["id"] == project_id), None)
    
    if project_idx is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Project with ID {project_id} not found"
        )
    
    # Update the mock project
    project_data = MOCK_PROJECTS[project_idx].copy()
    update_data = project_update.dict(exclude_unset=True)
    project_data.update(update_data)
    project_data["updated_at"] = datetime.now().isoformat() + "Z"
    
    MOCK_PROJECTS[project_idx] = project_data
    
    return ProjectResponse(**project_data)

@router.delete("/{project_id}", response_model=MessageResponse, summary="Delete project")
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Delete a project.
    
    **Fixed Response**: Returns success message for testing.
    TODO: Implement actual database deletion with cascade.
    """
    
    # TODO: Replace with actual database deletion
    # project = db.query(Project).filter(Project.id == project_id).first()
    # if not project:
    #     raise HTTPException(status_code=404, detail="Project not found")
    # 
    # db.delete(project)
    # db.commit()
    
    # For now, remove from mock data
    project_idx = next((i for i, p in enumerate(MOCK_PROJECTS) if p["id"] == project_id), None)
    
    if project_idx is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Project with ID {project_id} not found"
        )
    
    removed_project = MOCK_PROJECTS.pop(project_idx)
    
    return MessageResponse(message=f"Project '{removed_project['name']}' deleted successfully")

@router.get("/{project_id}/statistics", summary="Get project statistics")
async def get_project_statistics(
    project_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get detailed statistics for a project.
    
    **Fixed Response**: Returns mock statistics for testing.
    TODO: Implement actual database aggregation queries.
    """
    
    # TODO: Replace with actual database aggregation
    # This would involve complex queries joining tasks, calculating progress, etc.
    
    project = next((p for p in MOCK_PROJECTS if p["id"] == project_id), None)
    
    if not project:
        raise HTTPException(
            status_code=404, 
            detail=f"Project with ID {project_id} not found"
        )
    
    # Mock detailed statistics
    return {
        "project_id": project_id,
        "project_name": project["name"],
        "total_tasks": project["total_tasks"],
        "completed_tasks": project["completed_tasks"],
        "in_progress_tasks": 4,
        "blocked_tasks": 1,
        "overdue_tasks": 2,
        "completion_percentage": project["completion_percentage"],
        "estimated_hours": 320.5,
        "actual_hours": 156.75,
        "remaining_hours": 163.75,
        "days_since_start": 139,
        "days_until_deadline": 89,
        "velocity": {
            "tasks_per_week": 1.2,
            "hours_per_week": 8.9
        },
        "recent_activity": [
            {
                "date": "2025-06-03",
                "action": "task_completed",
                "description": "Completed 'User Interface Design'"
            },
            {
                "date": "2025-06-02", 
                "action": "task_created",
                "description": "Created 'Database Integration'"
            }
        ]
    }
