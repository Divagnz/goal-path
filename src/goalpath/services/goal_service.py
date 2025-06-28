"""
Goal Service
Contains all business logic for goal management
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .base_service import BaseService
from ..models import Goal, GoalProject, Project
from ..db_utils import QueryUtils, TransactionManager
from ..schemas import GoalCreate, GoalUpdate, GoalResponse


class GoalService(BaseService):
    """Service for goal business logic operations"""
    
    def calculate_goal_progress(self, goal_id: str) -> float:
        """Calculate goal progress from linked projects"""
        project_links = self.db.query(GoalProject).filter(GoalProject.goal_id == goal_id).all()
        
        if not project_links:
            # No linked projects, use manual progress
            goal = self.db.query(Goal).filter(Goal.id == goal_id).first()
            return float(goal.progress_percentage) if goal else 0.0
        
        # Calculate weighted progress from linked projects
        total_weight = sum(float(link.weight) for link in project_links)
        weighted_progress = 0.0
        
        for link in project_links:
            project_progress = QueryUtils.get_project_completion_percentage(self.db, link.project_id)
            weighted_progress += project_progress * float(link.weight)
        
        return weighted_progress / total_weight if total_weight > 0 else 0.0
    
    def get_goal_with_progress(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """Get goal with calculated progress and metadata"""
        goal = self.db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return None
        
        # Calculate progress
        calculated_progress = self.calculate_goal_progress(goal_id)
        
        # Count subgoals and linked projects
        subgoal_count = self.db.query(Goal).filter(Goal.parent_goal_id == goal_id).count()
        project_links = self.db.query(GoalProject).filter(GoalProject.goal_id == goal_id).all()
        
        return {
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
            "linked_projects": len(project_links),
        }
    
    def list_goals_with_progress(
        self,
        parent_goal_id: Optional[str] = None,
        goal_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> List[Dict[str, Any]]:
        """List goals with calculated progress"""
        goals_data = QueryUtils.get_goals_with_progress(
            db=self.db,
            parent_goal_id=parent_goal_id,
            goal_type=goal_type,
            status=status,
            search=search,
            page=page,
            size=size,
        )
        return goals_data
    
    def create_goal(self, goal_data: GoalCreate) -> Dict[str, Any]:
        """Create a new goal with validation"""
        with TransactionManager(self.db) as db_session:
            # Validate parent goal if provided
            if goal_data.parent_goal_id:
                parent_goal = db_session.query(Goal).filter(Goal.id == goal_data.parent_goal_id).first()
                if not parent_goal:
                    raise ValueError(f"Parent goal with ID {goal_data.parent_goal_id} not found")
            
            # Create new goal instance
            goal_dict = goal_data.model_dump()
            goal_dict["progress_percentage"] = 0.0  # Initialize progress to 0
            
            new_goal = Goal(**goal_dict)
            db_session.add(new_goal)
            db_session.commit()
            db_session.refresh(new_goal)
            
            # Return goal data
            return {
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
                "subgoal_count": 0,
                "linked_projects": 0,
            }
    
    def update_goal(self, goal_id: str, goal_update: GoalUpdate) -> Dict[str, Any]:
        """Update goal with business logic validation"""
        with TransactionManager(self.db) as db_session:
            goal = db_session.query(Goal).filter(Goal.id == goal_id).first()
            if not goal:
                raise ValueError(f"Goal with ID {goal_id} not found")
            
            # Get update data
            update_data = goal_update.model_dump(exclude_unset=True)
            
            # Validate parent goal hierarchy if being changed
            if "parent_goal_id" in update_data:
                new_parent_id = update_data["parent_goal_id"]
                if new_parent_id:
                    parent_goal = db_session.query(Goal).filter(Goal.id == new_parent_id).first()
                    if not parent_goal:
                        raise ValueError(f"Parent goal with ID {new_parent_id} not found")
                    
                    # Prevent cycles
                    if new_parent_id == goal_id:
                        raise ValueError("Goal cannot be its own parent")
                    
                    # Check for cycles in goal hierarchy
                    if self._would_create_cycle(db_session, goal_id, new_parent_id):
                        raise ValueError("Invalid goal hierarchy - would create a cycle")
            
            # Update fields
            for field, value in update_data.items():
                setattr(goal, field, value)
            
            db_session.commit()
            db_session.refresh(goal)
            
            # Recalculate progress if not manually set
            if "progress_percentage" not in update_data:
                calculated_progress = self.calculate_goal_progress(goal_id)
            else:
                calculated_progress = float(goal.progress_percentage)
            
            # Count related items
            subgoal_count = db_session.query(Goal).filter(Goal.parent_goal_id == goal_id).count()
            project_links = db_session.query(GoalProject).filter(GoalProject.goal_id == goal_id).all()
            
            return {
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
                "linked_projects": len(project_links),
            }
    
    def delete_goal(self, goal_id: str, cascade: bool = False) -> str:
        """Delete goal with subgoal handling"""
        with TransactionManager(self.db) as db_session:
            goal = db_session.query(Goal).filter(Goal.id == goal_id).first()
            if not goal:
                raise ValueError(f"Goal with ID {goal_id} not found")
            
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
            
            # Delete goal-project links
            db_session.query(GoalProject).filter(GoalProject.goal_id == goal_id).delete()
            
            # Delete the goal
            db_session.delete(goal)
            db_session.commit()
            
            action_desc = "and all subgoals " if cascade and subgoals else ""
            return f"Goal '{goal_title}' {action_desc}deleted successfully"
    
    def link_project_to_goal(self, goal_id: str, project_id: str, weight: float = 1.0) -> str:
        """Link project to goal with weight validation"""
        with TransactionManager(self.db) as db_session:
            # Verify goal exists
            goal = db_session.query(Goal).filter(Goal.id == goal_id).first()
            if not goal:
                raise ValueError(f"Goal with ID {goal_id} not found")
            
            # Verify project exists
            project = db_session.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")
            
            # Check if link already exists
            existing_link = (
                db_session.query(GoalProject)
                .filter(GoalProject.goal_id == goal_id, GoalProject.project_id == project_id)
                .first()
            )
            
            if existing_link:
                raise ValueError(f"Project '{project.name}' is already linked to goal '{goal.title}'")
            
            # Create link
            goal_project_link = GoalProject(goal_id=goal_id, project_id=project_id, weight=weight)
            db_session.add(goal_project_link)
            db_session.commit()
            
            return f"Project '{project.name}' linked to goal '{goal.title}' with weight {weight}"
    
    def unlink_project_from_goal(self, goal_id: str, project_id: str) -> str:
        """Remove project link from goal"""
        with TransactionManager(self.db) as db_session:
            # Find the link
            link = (
                db_session.query(GoalProject)
                .filter(GoalProject.goal_id == goal_id, GoalProject.project_id == project_id)
                .first()
            )
            
            if not link:
                raise ValueError(f"No link found between goal {goal_id} and project {project_id}")
            
            # Get names for response
            goal = db_session.query(Goal).filter(Goal.id == goal_id).first()
            project = db_session.query(Project).filter(Project.id == project_id).first()
            
            # Remove link
            db_session.delete(link)
            db_session.commit()
            
            goal_name = goal.title if goal else goal_id
            project_name = project.name if project else project_id
            
            return f"Project '{project_name}' unlinked from goal '{goal_name}'"
    
    def get_goal_hierarchy(self, goal_id: str) -> Dict[str, Any]:
        """Get complete goal hierarchy (ancestors and descendants)"""
        goal = self.db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            raise ValueError(f"Goal with ID {goal_id} not found")
        
        def get_ancestors(current_goal_id: str) -> List[Dict]:
            """Recursively get goal ancestors"""
            ancestors = []
            current_goal = self.db.query(Goal).filter(Goal.id == current_goal_id).first()
            
            while current_goal and current_goal.parent_goal_id:
                parent = self.db.query(Goal).filter(Goal.id == current_goal.parent_goal_id).first()
                if parent:
                    calculated_progress = self.calculate_goal_progress(parent.id)
                    ancestors.append({
                        "id": parent.id,
                        "title": parent.title,
                        "goal_type": parent.goal_type,
                        "status": parent.status,
                        "progress": round(calculated_progress, 1),
                    })
                    current_goal = parent
                else:
                    break
            
            return list(reversed(ancestors))
        
        def get_descendants(current_goal_id: str, level: int = 0) -> List[Dict]:
            """Recursively get goal descendants"""
            children = []
            subgoals = self.db.query(Goal).filter(Goal.parent_goal_id == current_goal_id).all()
            
            for subgoal in subgoals:
                calculated_progress = self.calculate_goal_progress(subgoal.id)
                child_data = {
                    "id": subgoal.id,
                    "title": subgoal.title,
                    "goal_type": subgoal.goal_type,
                    "status": subgoal.status,
                    "progress": round(calculated_progress, 1),
                    "level": level,
                    "children": get_descendants(subgoal.id, level + 1),
                }
                children.append(child_data)
            
            return children
        
        # Calculate progress for current goal
        calculated_progress = self.calculate_goal_progress(goal_id)
        
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
                "progress": round(calculated_progress, 1),
            },
            "ancestors": ancestors,
            "descendants": descendants,
            "depth": len(ancestors),
            "total_descendants": count_descendants(descendants),
        }
    
    def _would_create_cycle(self, db_session: Session, goal_id: str, new_parent_id: str) -> bool:
        """Check if setting new_parent_id as parent would create a cycle"""
        current_id = new_parent_id
        visited = set()
        
        while current_id and current_id not in visited:
            visited.add(current_id)
            parent = db_session.query(Goal).filter(Goal.id == current_id).first()
            if not parent:
                break
            if parent.parent_goal_id == goal_id:
                return True
            current_id = parent.parent_goal_id
        
        return False