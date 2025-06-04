"""
Goals API Router - Mock/Fixed Responses
This module contains fixed responses for testing API structure
TODO: Replace with actual database logic
"""

from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from ..schemas import (
    GoalCreate, GoalUpdate, GoalResponse, GoalFilters,
    MessageResponse, ErrorResponse
)
from ..database import get_db

router = APIRouter(prefix="/api/goals", tags=["goals"])

# Mock data for testing
MOCK_GOALS = [
    {
        "id": "goal-001",
        "parent_goal_id": None,
        "title": "Q2 Product Launch",
        "description": "Launch new product line with mobile app and updated website by end of Q2",
        "goal_type": "short_term",
        "target_date": "2025-06-30",
        "status": "active",
        "progress_percentage": 65.5,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-06-03T10:00:00Z",
        "linked_projects": 2,
        "subgoal_count": 0
    },
    {
        "id": "goal-002",
        "parent_goal_id": None,
        "title": "Market Expansion",
        "description": "Expand to 3 new markets this year with localized products",
        "goal_type": "medium_term",
        "target_date": "2025-12-31",
        "status": "active",
        "progress_percentage": 23.0,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-05-15T14:30:00Z",
        "linked_projects": 1,
        "subgoal_count": 3
    },
    {
        "id": "goal-003",
        "parent_goal_id": "goal-002",
        "title": "European Market Entry",
        "description": "Establish presence in European markets starting with Germany and France",
        "goal_type": "short_term",
        "target_date": "2025-09-30",
        "status": "active",
        "progress_percentage": 40.0,
        "created_at": "2025-02-01T00:00:00Z",
        "updated_at": "2025-06-01T16:45:00Z",
        "linked_projects": 1,
        "subgoal_count": 0
    },
    {
        "id": "goal-004",
        "parent_goal_id": None,
        "title": "Technical Excellence",
        "description": "Modernize infrastructure and improve system reliability",
        "goal_type": "long_term",
        "target_date": "2025-12-31",
        "status": "active",
        "progress_percentage": 78.5,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-06-03T09:15:00Z",
        "linked_projects": 1,
        "subgoal_count": 0
    }
]

@router.get("/", response_model=List[GoalResponse], summary="List all goals")
async def list_goals(
    status: Optional[str] = Query(None, description="Filter by status"),
    goal_type: Optional[str] = Query(None, description="Filter by goal type"),
    parent_goal_id: Optional[str] = Query(None, description="Filter by parent goal"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
) -> List[GoalResponse]:
    """
    Get all goals with optional filtering and pagination.
    
    **Fixed Response**: Returns mock goal data for testing.
    TODO: Implement actual database queries with filtering.
    """
    
    filtered_goals = MOCK_GOALS.copy()
    
    if status:
        filtered_goals = [g for g in filtered_goals if g["status"] == status]
    if goal_type:
        filtered_goals = [g for g in filtered_goals if g["goal_type"] == goal_type]
    if parent_goal_id:
        filtered_goals = [g for g in filtered_goals if g["parent_goal_id"] == parent_goal_id]
    if search:
        search_lower = search.lower()
        filtered_goals = [
            g for g in filtered_goals 
            if search_lower in g["title"].lower() or search_lower in (g["description"] or "").lower()
        ]
    
    # Simulate pagination
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_goals = filtered_goals[start_idx:end_idx]
    
    return [GoalResponse(**goal) for goal in paginated_goals]

@router.get("/{goal_id}", response_model=GoalResponse, summary="Get goal by ID")
async def get_goal(
    goal_id: str,
    db: Session = Depends(get_db)
) -> GoalResponse:
    """
    Get a specific goal by ID.
    
    **Fixed Response**: Returns mock goal data for testing.
    TODO: Implement actual database lookup.
    """
    
    goal = next((g for g in MOCK_GOALS if g["id"] == goal_id), None)
    
    if not goal:
        raise HTTPException(
            status_code=404,
            detail=f"Goal with ID {goal_id} not found"
        )
    
    return GoalResponse(**goal)

@router.post("/", response_model=GoalResponse, status_code=201, summary="Create new goal")
async def create_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db)
) -> GoalResponse:
    """
    Create a new goal.
    
    **Fixed Response**: Returns mock created goal for testing.
    TODO: Implement actual database creation.
    """
    
    new_goal_data = {
        "id": f"goal-{len(MOCK_GOALS) + 1:03d}",
        **goal.dict(),
        "progress_percentage": 0.0,
        "created_at": datetime.now().isoformat() + "Z",
        "updated_at": datetime.now().isoformat() + "Z",
        "linked_projects": 0,
        "subgoal_count": 0
    }
    
    MOCK_GOALS.append(new_goal_data)
    
    return GoalResponse(**new_goal_data)

@router.put("/{goal_id}", response_model=GoalResponse, summary="Update goal")
async def update_goal(
    goal_id: str,
    goal_update: GoalUpdate,
    db: Session = Depends(get_db)
) -> GoalResponse:
    """
    Update an existing goal.
    
    **Fixed Response**: Returns mock updated goal for testing.
    TODO: Implement actual database update with progress recalculation.
    """
    
    goal_idx = next((i for i, g in enumerate(MOCK_GOALS) if g["id"] == goal_id), None)
    
    if goal_idx is None:
        raise HTTPException(
            status_code=404,
            detail=f"Goal with ID {goal_id} not found"
        )
    
    goal_data = MOCK_GOALS[goal_idx].copy()
    update_data = goal_update.dict(exclude_unset=True)
    goal_data.update(update_data)
    goal_data["updated_at"] = datetime.now().isoformat() + "Z"
    
    MOCK_GOALS[goal_idx] = goal_data
    
    return GoalResponse(**goal_data)

@router.delete("/{goal_id}", response_model=MessageResponse, summary="Delete goal")
async def delete_goal(
    goal_id: str,
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Delete a goal.
    
    **Fixed Response**: Returns success message for testing.
    TODO: Implement actual database deletion with subgoal handling.
    """
    
    goal_idx = next((i for i, g in enumerate(MOCK_GOALS) if g["id"] == goal_id), None)
    
    if goal_idx is None:
        raise HTTPException(
            status_code=404,
            detail=f"Goal with ID {goal_id} not found"
        )
    
    removed_goal = MOCK_GOALS.pop(goal_idx)
    
    return MessageResponse(message=f"Goal '{removed_goal['title']}' deleted successfully")

@router.get("/{goal_id}/progress", summary="Get goal progress details")
async def get_goal_progress(
    goal_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get detailed progress information for a goal.
    
    **Fixed Response**: Returns mock progress data for testing.
    TODO: Implement actual progress calculation from linked projects.
    """
    
    goal = next((g for g in MOCK_GOALS if g["id"] == goal_id), None)
    
    if not goal:
        raise HTTPException(
            status_code=404,
            detail=f"Goal with ID {goal_id} not found"
        )
    
    # Mock detailed progress data
    return {
        "goal_id": goal_id,
        "goal_title": goal["title"],
        "current_progress": goal["progress_percentage"],
        "target_date": goal["target_date"],
        "days_remaining": 27,
        "linked_projects": [
            {
                "project_id": "proj-001",
                "project_name": "Website Redesign",
                "weight": 0.6,
                "completion": 53.3,
                "contribution": 31.98
            },
            {
                "project_id": "proj-002",
                "project_name": "Mobile App Development", 
                "weight": 0.4,
                "completion": 17.9,
                "contribution": 7.16
            }
        ],
        "milestones": [
            {
                "title": "MVP Complete",
                "target_date": "2025-06-15",
                "status": "completed",
                "completion_date": "2025-06-14"
            },
            {
                "title": "Beta Release",
                "target_date": "2025-06-25",
                "status": "in_progress"
            }
        ],
        "progress_history": [
            {"date": "2025-05-01", "progress": 45.2},
            {"date": "2025-05-15", "progress": 58.1},
            {"date": "2025-06-01", "progress": 62.8},
            {"date": "2025-06-03", "progress": 65.5}
        ]
    }

@router.get("/{goal_id}/subgoals", response_model=List[GoalResponse], summary="Get subgoals")
async def get_subgoals(
    goal_id: str,
    db: Session = Depends(get_db)
) -> List[GoalResponse]:
    """
    Get all subgoals for a specific goal.
    
    **Fixed Response**: Returns mock subgoal data for testing.
    TODO: Implement actual hierarchical query.
    """
    
    # Check if parent goal exists
    parent_goal = next((g for g in MOCK_GOALS if g["id"] == goal_id), None)
    if not parent_goal:
        raise HTTPException(
            status_code=404,
            detail=f"Goal with ID {goal_id} not found"
        )
    
    # Get subgoals
    subgoals = [g for g in MOCK_GOALS if g["parent_goal_id"] == goal_id]
    
    return [GoalResponse(**goal) for goal in subgoals]

@router.put("/{goal_id}/progress", response_model=GoalResponse, summary="Update goal progress")
async def update_goal_progress(
    goal_id: str,
    progress: float = Query(..., ge=0, le=100, description="Progress percentage (0-100)"),
    db: Session = Depends(get_db)
) -> GoalResponse:
    """
    Manually update goal progress percentage.
    
    **Fixed Response**: Returns mock updated goal for testing.
    TODO: Implement actual progress update with validation.
    """
    
    goal_idx = next((i for i, g in enumerate(MOCK_GOALS) if g["id"] == goal_id), None)
    
    if goal_idx is None:
        raise HTTPException(
            status_code=404,
            detail=f"Goal with ID {goal_id} not found"
        )
    
    goal_data = MOCK_GOALS[goal_idx].copy()
    goal_data["progress_percentage"] = progress
    goal_data["updated_at"] = datetime.now().isoformat() + "Z"
    
    MOCK_GOALS[goal_idx] = goal_data
    
    return GoalResponse(**goal_data)

@router.get("/{goal_id}/hierarchy", summary="Get goal hierarchy")
async def get_goal_hierarchy(
    goal_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get complete goal hierarchy (ancestors and descendants).
    
    **Fixed Response**: Returns mock hierarchy data for testing.
    TODO: Implement actual recursive hierarchy query.
    """
    
    goal = next((g for g in MOCK_GOALS if g["id"] == goal_id), None)
    if not goal:
        raise HTTPException(
            status_code=404,
            detail=f"Goal with ID {goal_id} not found"
        )
    
    # Build mock hierarchy
    def get_ancestors(goal_id):
        ancestors = []
        current_goal = next((g for g in MOCK_GOALS if g["id"] == goal_id), None)
        while current_goal and current_goal["parent_goal_id"]:
            parent = next((g for g in MOCK_GOALS if g["id"] == current_goal["parent_goal_id"]), None)
            if parent:
                ancestors.append({
                    "id": parent["id"],
                    "title": parent["title"],
                    "goal_type": parent["goal_type"],
                    "status": parent["status"],
                    "progress": parent["progress_percentage"]
                })
                current_goal = parent
            else:
                break
        return list(reversed(ancestors))
    
    def get_descendants(goal_id, level=0):
        children = []
        for g in MOCK_GOALS:
            if g["parent_goal_id"] == goal_id:
                child_data = {
                    "id": g["id"],
                    "title": g["title"],
                    "goal_type": g["goal_type"],
                    "status": g["status"],
                    "progress": g["progress_percentage"],
                    "level": level,
                    "children": get_descendants(g["id"], level + 1)
                }
                children.append(child_data)
        return children
    
    return {
        "goal": {
            "id": goal["id"],
            "title": goal["title"],
            "goal_type": goal["goal_type"],
            "status": goal["status"],
            "progress": goal["progress_percentage"]
        },
        "ancestors": get_ancestors(goal_id),
        "descendants": get_descendants(goal_id, 1),
        "depth": len(get_ancestors(goal_id)),
        "total_descendants": len([g for g in MOCK_GOALS if g["parent_goal_id"] and g["parent_goal_id"] == goal_id])
    }
