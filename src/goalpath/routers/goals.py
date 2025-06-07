"""
Goals API Router - Database Implementation
Full CRUD operations for goals with hierarchical support and progress calculation
"""

from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from ..schemas import (
    GoalCreate, GoalUpdate, GoalResponse, GoalFilters,
    MessageResponse, ErrorResponse
)
from ..database import get_db
from ..models import Goal, GoalProject, Project, Task
from ..db_utils import QueryUtils, TransactionManager

router = APIRouter(prefix="/api/goals", tags=["goals"])


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
    
    **Database Implementation**: Queries goals with calculated progress from linked projects.
    """
    
    try:
        # Use QueryUtils for database operations with progress calculation
        goals_data = QueryUtils.get_goals_with_progress(
            db=db,
            parent_goal_id=parent_goal_id,
            goal_type=goal_type,
            status=status,
            search=search,
            page=page,
            size=size
        )
        
        return [GoalResponse(**goal) for goal in goals_data]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving goals: {str(e)}"
        )


@router.get("/{goal_id}", response_model=GoalResponse, summary="Get goal by ID")
async def get_goal(
    goal_id: str,
    db: Session = Depends(get_db)
) -> GoalResponse:
    """
    Get a specific goal by ID with calculated progress.
    
    **Database Implementation**: Retrieves goal with progress from linked projects.
    """
    
    try:
        # Get goal from database
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        
        if not goal:
            raise HTTPException(
                status_code=404,
                detail=f"Goal with ID {goal_id} not found"
            )
        
        # Calculate progress from linked projects
        project_links = db.query(GoalProject).filter(GoalProject.goal_id == goal_id).all()
        
        if project_links:
            # Calculate weighted progress
            total_weight = sum(float(link.weight) for link in project_links)
            weighted_progress = 0.0
            
            for link in project_links:
                project_progress = QueryUtils.get_project_completion_percentage(
                    db, link.project_id
                )
                weighted_progress += project_progress * float(link.weight)
            
            calculated_progress = weighted_progress / total_weight if total_weight > 0 else 0.0
        else:
            calculated_progress = float(goal.progress_percentage)
        
        # Count subgoals
        subgoal_count = db.query(Goal).filter(Goal.parent_goal_id == goal_id).count()
        
        # Build response data
        goal_data = {
            "id": goal.id,
            "parent_goal_id": goal.parent_goal_id,
            "title": goal.title,
            "description": goal.description,
            "goal_type": goal.goal_type,
            "target_date": goal.target_date.isoformat() if goal.target_date else None,
            "status": goal.status,
            "progress_percentage": round(calculated_progress, 1),
            "created_at": goal.created_at.isoformat(),
            "updated_at": goal.updated_at.isoformat(),
            "subgoal_count": subgoal_count,
            "linked_projects": len(project_links)
        }
        
        return GoalResponse(**goal_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving goal: {str(e)}"
        )


@router.post("/", response_model=GoalResponse, status_code=201, summary="Create new goal")
async def create_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db)
) -> GoalResponse:
    """
    Create a new goal.
    
    **Database Implementation**: Creates goal in database with hierarchy validation.
    """
    
    try:
        with TransactionManager(db) as db_session:
            # Validate parent goal if provided
            if goal.parent_goal_id:
                parent_goal = db_session.query(Goal).filter(Goal.id == goal.parent_goal_id).first()
                if not parent_goal:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Parent goal with ID {goal.parent_goal_id} not found"
                    )
            
            # Create new goal instance
            goal_data = goal.model_dump()
            goal_data["progress_percentage"] = 0.0  # Initialize progress to 0
            
            new_goal = Goal(**goal_data)
            db_session.add(new_goal)
            db_session.commit()
            db_session.refresh(new_goal)
            
            # Build response data
            goal_response_data = {
                "id": new_goal.id,
                "parent_goal_id": new_goal.parent_goal_id,
                "title": new_goal.title,
                "description": new_goal.description,
                "goal_type": new_goal.goal_type,
                "target_date": new_goal.target_date.isoformat() if new_goal.target_date else None,
                "status": new_goal.status,
                "progress_percentage": 0.0,
                "created_at": new_goal.created_at.isoformat(),
                "updated_at": new_goal.updated_at.isoformat(),
                "subgoal_count": 0,  # New goal has no subgoals
                "linked_projects": 0  # New goal has no linked projects
            }
            
            return GoalResponse(**goal_response_data)
            
    except HTTPException:
        raise
    except IntegrityError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Goal creation failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating goal: {str(e)}"
        )


@router.put("/{goal_id}", response_model=GoalResponse, summary="Update goal")
async def update_goal(
    goal_id: str,
    goal_update: GoalUpdate,
    db: Session = Depends(get_db)
) -> GoalResponse:
    """
    Update an existing goal.
    
    **Database Implementation**: Updates goal with progress recalculation.
    """
    
    try:
        with TransactionManager(db) as db_session:
            # Find existing goal
            goal = db_session.query(Goal).filter(Goal.id == goal_id).first()
            
            if not goal:
                raise HTTPException(
                    status_code=404,
                    detail=f"Goal with ID {goal_id} not found"
                )
            
            # Get update data
            update_data = goal_update.model_dump(exclude_unset=True)
            
            # Validate parent goal hierarchy if being changed
            if "parent_goal_id" in update_data:
                new_parent_id = update_data["parent_goal_id"]
                if new_parent_id:
                    parent_goal = db_session.query(Goal).filter(Goal.id == new_parent_id).first()
                    if not parent_goal:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Parent goal with ID {new_parent_id} not found"
                        )
                    
                    # Validate hierarchy (prevent cycles)
                    if new_parent_id == goal_id:
                        raise HTTPException(
                            status_code=400,
                            detail="Goal cannot be its own parent"
                        )
                    
                    # Check for cycles in goal hierarchy
                    current_id = new_parent_id
                    visited = set()
                    while current_id and current_id not in visited:
                        visited.add(current_id)
                        parent = db_session.query(Goal).filter(Goal.id == current_id).first()
                        if not parent:
                            break
                        if parent.parent_goal_id == goal_id:
                            raise HTTPException(
                                status_code=400,
                                detail="Invalid goal hierarchy - would create a cycle"
                            )
                        current_id = parent.parent_goal_id
            
            # Update fields from request
            for field, value in update_data.items():
                setattr(goal, field, value)
            
            db_session.commit()
            db_session.refresh(goal)
            
            # Recalculate progress from linked projects
            project_links = db_session.query(GoalProject).filter(GoalProject.goal_id == goal_id).all()
            
            if project_links and "progress_percentage" not in update_data:
                # Only auto-calculate if progress wasn't manually set
                total_weight = sum(float(link.weight) for link in project_links)
                weighted_progress = 0.0
                
                for link in project_links:
                    project_progress = QueryUtils.get_project_completion_percentage(
                        db_session, link.project_id
                    )
                    weighted_progress += project_progress * float(link.weight)
                
                calculated_progress = weighted_progress / total_weight if total_weight > 0 else 0.0
            else:
                calculated_progress = float(goal.progress_percentage)
            
            # Count subgoals
            subgoal_count = db_session.query(Goal).filter(Goal.parent_goal_id == goal_id).count()
            
            # Build response data
            goal_response_data = {
                "id": goal.id,
                "parent_goal_id": goal.parent_goal_id,
                "title": goal.title,
                "description": goal.description,
                "goal_type": goal.goal_type,
                "target_date": goal.target_date.isoformat() if goal.target_date else None,
                "status": goal.status,
                "progress_percentage": round(calculated_progress, 1),
                "created_at": goal.created_at.isoformat(),
                "updated_at": goal.updated_at.isoformat(),
                "subgoal_count": subgoal_count,
                "linked_projects": len(project_links)
            }
            
            return GoalResponse(**goal_response_data)
            
    except HTTPException:
        raise
    except IntegrityError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Goal update failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating goal: {str(e)}"
        )


@router.delete("/{goal_id}", response_model=MessageResponse, summary="Delete goal")
async def delete_goal(
    goal_id: str,
    cascade: bool = Query(False, description="Delete subgoals (true) or promote to parent (false)"),
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Delete a goal.
    
    **Database Implementation**: Deletes goal with subgoal handling and project link cleanup.
    """
    
    try:
        with TransactionManager(db) as db_session:
            # Find existing goal
            goal = db_session.query(Goal).filter(Goal.id == goal_id).first()
            
            if not goal:
                raise HTTPException(
                    status_code=404,
                    detail=f"Goal with ID {goal_id} not found"
                )
            
            goal_title = goal.title
            
            # Handle subgoals
            subgoals = db_session.query(Goal).filter(Goal.parent_goal_id == goal_id).all()
            
            if subgoals:
                if cascade:
                    # Delete all subgoals (will cascade to their subgoals)
                    for subgoal in subgoals:
                        db_session.delete(subgoal)
                else:
                    # Promote subgoals to this goal's parent level
                    for subgoal in subgoals:
                        subgoal.parent_goal_id = goal.parent_goal_id
            
            # Delete goal-project links (will be handled by CASCADE in schema)
            # But we'll do it explicitly for clarity
            db_session.query(GoalProject).filter(GoalProject.goal_id == goal_id).delete()
            
            # Delete the goal
            db_session.delete(goal)
            db_session.commit()
            
            action_desc = "and all subgoals " if cascade and subgoals else ""
            return MessageResponse(
                message=f"Goal '{goal_title}' {action_desc}deleted successfully"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting goal: {str(e)}"
        )


@router.get("/{goal_id}/progress", summary="Get goal progress details")
async def get_goal_progress(
    goal_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get detailed progress information for a goal.
    
    **Database Implementation**: Calculates progress from linked projects with detailed breakdown.
    """
    
    try:
        # Verify goal exists
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        
        if not goal:
            raise HTTPException(
                status_code=404,
                detail=f"Goal with ID {goal_id} not found"
            )
        
        # Get linked projects with weights
        project_links = db.query(GoalProject, Project).join(
            Project, GoalProject.project_id == Project.id
        ).filter(GoalProject.goal_id == goal_id).all()
        
        # Calculate days remaining
        days_remaining = None
        if goal.target_date:
            days_remaining = (goal.target_date - date.today()).days
        
        # Build linked projects data with contributions
        linked_projects_data = []
        total_weight = sum(float(link.weight) for link, _ in project_links)
        current_progress = 0.0
        
        for link, project in project_links:
            project_completion = QueryUtils.get_project_completion_percentage(db, project.id)
            weight = float(link.weight)
            contribution = project_completion * weight
            current_progress += contribution
            
            linked_projects_data.append({
                "project_id": project.id,
                "project_name": project.name,
                "weight": weight,
                "completion": round(project_completion, 1),
                "contribution": round(contribution, 2)
            })
        
        # Calculate final progress percentage
        final_progress = current_progress / total_weight if total_weight > 0 else float(goal.progress_percentage)
        
        # Get goal history (simplified - in real app would track changes)
        progress_history = [
            {
                "date": goal.created_at.date().isoformat(),
                "progress": 0.0
            },
            {
                "date": date.today().isoformat(),
                "progress": round(final_progress, 1)
            }
        ]
        
        # Calculate milestones (simplified - in real app would have milestone tracking)
        milestones = []
        if goal.target_date:
            # Create sample milestone based on progress
            if final_progress >= 50:
                milestones.append({
                    "title": "Halfway Point",
                    "target_date": (goal.created_at.date() + (goal.target_date - goal.created_at.date()) / 2).isoformat(),
                    "status": "completed" if final_progress >= 50 else "in_progress"
                })
            
            milestones.append({
                "title": "Goal Completion",
                "target_date": goal.target_date.isoformat(),
                "status": "completed" if final_progress >= 100 else "in_progress"
            })
        
        return {
            "goal_id": goal_id,
            "goal_title": goal.title,
            "current_progress": round(final_progress, 1),
            "target_date": goal.target_date.isoformat() if goal.target_date else None,
            "days_remaining": days_remaining,
            "linked_projects": linked_projects_data,
            "milestones": milestones,
            "progress_history": progress_history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating goal progress: {str(e)}"
        )


@router.get("/{goal_id}/subgoals", response_model=List[GoalResponse], summary="Get subgoals")
async def get_subgoals(
    goal_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
) -> List[GoalResponse]:
    """
    Get all subgoals for a specific goal.
    
    **Database Implementation**: Retrieves subgoals with calculated progress.
    """
    
    try:
        # Check if parent goal exists
        parent_goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not parent_goal:
            raise HTTPException(
                status_code=404,
                detail=f"Goal with ID {goal_id} not found"
            )
        
        # Get subgoals with progress calculation
        subgoals_data = QueryUtils.get_goals_with_progress(
            db=db,
            parent_goal_id=goal_id,
            page=page,
            size=size
        )
        
        return [GoalResponse(**goal) for goal in subgoals_data]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving subgoals: {str(e)}"
        )


@router.put("/{goal_id}/progress", response_model=GoalResponse, summary="Update goal progress")
async def update_goal_progress(
    goal_id: str,
    progress: float = Query(..., ge=0, le=100, description="Progress percentage (0-100)"),
    db: Session = Depends(get_db)
) -> GoalResponse:
    """
    Manually update goal progress percentage.
    
    **Database Implementation**: Updates progress with validation and audit.
    """
    
    try:
        with TransactionManager(db) as db_session:
            # Find existing goal
            goal = db_session.query(Goal).filter(Goal.id == goal_id).first()
            
            if not goal:
                raise HTTPException(
                    status_code=404,
                    detail=f"Goal with ID {goal_id} not found"
                )
            
            # Update progress
            goal.progress_percentage = progress
            db_session.commit()
            db_session.refresh(goal)
            
            # Get related data
            project_links = db_session.query(GoalProject).filter(GoalProject.goal_id == goal_id).all()
            subgoal_count = db_session.query(Goal).filter(Goal.parent_goal_id == goal_id).count()
            
            # Build response data
            goal_response_data = {
                "id": goal.id,
                "parent_goal_id": goal.parent_goal_id,
                "title": goal.title,
                "description": goal.description,
                "goal_type": goal.goal_type,
                "target_date": goal.target_date.isoformat() if goal.target_date else None,
                "status": goal.status,
                "progress_percentage": round(float(goal.progress_percentage), 1),
                "created_at": goal.created_at.isoformat(),
                "updated_at": goal.updated_at.isoformat(),
                "subgoal_count": subgoal_count,
                "linked_projects": len(project_links)
            }
            
            return GoalResponse(**goal_response_data)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating goal progress: {str(e)}"
        )


@router.get("/{goal_id}/hierarchy", summary="Get goal hierarchy")
async def get_goal_hierarchy(
    goal_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get complete goal hierarchy (ancestors and descendants).
    
    **Database Implementation**: Builds hierarchy tree from database relationships.
    """
    
    try:
        # Verify goal exists
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            raise HTTPException(
                status_code=404,
                detail=f"Goal with ID {goal_id} not found"
            )
        
        def get_ancestors(goal_id: str) -> List[dict]:
            """Recursively get goal ancestors"""
            ancestors = []
            current_goal = db.query(Goal).filter(Goal.id == goal_id).first()
            
            while current_goal and current_goal.parent_goal_id:
                parent = db.query(Goal).filter(Goal.id == current_goal.parent_goal_id).first()
                if parent:
                    # Calculate progress for parent
                    project_links = db.query(GoalProject).filter(GoalProject.goal_id == parent.id).all()
                    if project_links:
                        total_weight = sum(float(link.weight) for link in project_links)
                        weighted_progress = 0.0
                        for link in project_links:
                            project_progress = QueryUtils.get_project_completion_percentage(db, link.project_id)
                            weighted_progress += project_progress * float(link.weight)
                        calculated_progress = weighted_progress / total_weight if total_weight > 0 else 0.0
                    else:
                        calculated_progress = float(parent.progress_percentage)
                    
                    ancestors.append({
                        "id": parent.id,
                        "title": parent.title,
                        "goal_type": parent.goal_type,
                        "status": parent.status,
                        "progress": round(calculated_progress, 1)
                    })
                    current_goal = parent
                else:
                    break
            
            return list(reversed(ancestors))
        
        def get_descendants(goal_id: str, level: int = 0) -> List[dict]:
            """Recursively get goal descendants"""
            children = []
            subgoals = db.query(Goal).filter(Goal.parent_goal_id == goal_id).all()
            
            for subgoal in subgoals:
                # Calculate progress for subgoal
                project_links = db.query(GoalProject).filter(GoalProject.goal_id == subgoal.id).all()
                if project_links:
                    total_weight = sum(float(link.weight) for link in project_links)
                    weighted_progress = 0.0
                    for link in project_links:
                        project_progress = QueryUtils.get_project_completion_percentage(db, link.project_id)
                        weighted_progress += project_progress * float(link.weight)
                    calculated_progress = weighted_progress / total_weight if total_weight > 0 else 0.0
                else:
                    calculated_progress = float(subgoal.progress_percentage)
                
                child_data = {
                    "id": subgoal.id,
                    "title": subgoal.title,
                    "goal_type": subgoal.goal_type,
                    "status": subgoal.status,
                    "progress": round(calculated_progress, 1),
                    "level": level,
                    "children": get_descendants(subgoal.id, level + 1)
                }
                children.append(child_data)
            
            return children
        
        # Calculate progress for current goal
        project_links = db.query(GoalProject).filter(GoalProject.goal_id == goal_id).all()
        if project_links:
            total_weight = sum(float(link.weight) for link in project_links)
            weighted_progress = 0.0
            for link in project_links:
                project_progress = QueryUtils.get_project_completion_percentage(db, link.project_id)
                weighted_progress += project_progress * float(link.weight)
            calculated_progress = weighted_progress / total_weight if total_weight > 0 else 0.0
        else:
            calculated_progress = float(goal.progress_percentage)
        
        # Build hierarchy response
        ancestors = get_ancestors(goal_id)
        descendants = get_descendants(goal_id, 1)
        
        # Count total descendants
        def count_descendants(children):
            count = len(children)
            for child in children:
                count += count_descendants(child.get("children", []))
            return count
        
        return {
            "goal": {
                "id": goal.id,
                "title": goal.title,
                "goal_type": goal.goal_type,
                "status": goal.status,
                "progress": round(calculated_progress, 1)
            },
            "ancestors": ancestors,
            "descendants": descendants,
            "depth": len(ancestors),
            "total_descendants": count_descendants(descendants)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving goal hierarchy: {str(e)}"
        )


@router.post("/{goal_id}/link-project", summary="Link project to goal")
async def link_project_to_goal(
    goal_id: str,
    project_id: str = Query(..., description="Project ID to link"),
    weight: float = Query(1.0, ge=0.01, le=1.0, description="Weight for progress calculation (0.01-1.0)"),
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Link a project to a goal with a weight for progress calculation.
    
    **Database Implementation**: Creates goal-project relationship.
    """
    
    try:
        with TransactionManager(db) as db_session:
            # Verify goal exists
            goal = db_session.query(Goal).filter(Goal.id == goal_id).first()
            if not goal:
                raise HTTPException(
                    status_code=404,
                    detail=f"Goal with ID {goal_id} not found"
                )
            
            # Verify project exists
            project = db_session.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise HTTPException(
                    status_code=404,
                    detail=f"Project with ID {project_id} not found"
                )
            
            # Check if link already exists
            existing_link = db_session.query(GoalProject).filter(
                GoalProject.goal_id == goal_id,
                GoalProject.project_id == project_id
            ).first()
            
            if existing_link:
                raise HTTPException(
                    status_code=400,
                    detail=f"Project '{project.name}' is already linked to goal '{goal.title}'"
                )
            
            # Create link
            goal_project_link = GoalProject(
                goal_id=goal_id,
                project_id=project_id,
                weight=weight
            )
            
            db_session.add(goal_project_link)
            db_session.commit()
            
            return MessageResponse(
                message=f"Project '{project.name}' linked to goal '{goal.title}' with weight {weight}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error linking project to goal: {str(e)}"
        )


@router.delete("/{goal_id}/unlink-project", summary="Unlink project from goal")
async def unlink_project_from_goal(
    goal_id: str,
    project_id: str = Query(..., description="Project ID to unlink"),
    db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Remove project link from a goal.
    
    **Database Implementation**: Removes goal-project relationship.
    """
    
    try:
        with TransactionManager(db) as db_session:
            # Find the link
            link = db_session.query(GoalProject).filter(
                GoalProject.goal_id == goal_id,
                GoalProject.project_id == project_id
            ).first()
            
            if not link:
                raise HTTPException(
                    status_code=404,
                    detail=f"No link found between goal {goal_id} and project {project_id}"
                )
            
            # Get names for response
            goal = db_session.query(Goal).filter(Goal.id == goal_id).first()
            project = db_session.query(Project).filter(Project.id == project_id).first()
            
            # Remove link
            db_session.delete(link)
            db_session.commit()
            
            goal_name = goal.title if goal else goal_id
            project_name = project.name if project else project_id
            
            return MessageResponse(
                message=f"Project '{project_name}' unlinked from goal '{goal_name}'"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error unlinking project from goal: {str(e)}"
        )
