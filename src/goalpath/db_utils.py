"""
Database utilities and query helpers for GoalPath
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.sql import func

from .models import Project, Task, Goal, TaskDependency, GoalProject


class QueryUtils:
    """Utility class for common database queries"""
    
    @staticmethod
    def get_projects_with_stats(
        db: Session,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> List[Dict[str, Any]]:
        """Get projects with calculated statistics"""
        
        # Base query
        query = db.query(Project)
        
        # Apply filters
        if status:
            query = query.filter(Project.status == status)
        if priority:
            query = query.filter(Project.priority == priority)
        if search:
            search_filter = or_(
                Project.name.ilike(f"%{search}%"),
                Project.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Apply pagination
        offset = (page - 1) * size
        projects = query.offset(offset).limit(size).all()
        
        # Calculate statistics for each project
        result = []
        for project in projects:
            # Count tasks by status
            total_tasks = db.query(Task).filter(Task.project_id == project.id).count()
            completed_tasks = db.query(Task).filter(
                Task.project_id == project.id,
                Task.status == "done"
            ).count()
            
            # Calculate completion percentage
            completion_percentage = (
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
            )
            
            project_dict = {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "priority": project.priority,
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "target_end_date": project.target_end_date.isoformat() if project.target_end_date else None,
                "actual_end_date": project.actual_end_date.isoformat() if project.actual_end_date else None,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
                "created_by": project.created_by,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_percentage": round(completion_percentage, 1)
            }
            result.append(project_dict)
        
        return result
    
    @staticmethod
    def get_project_with_stats(db: Session, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a single project with detailed statistics"""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        
        # Calculate detailed statistics
        task_stats = db.query(
            Task.status,
            func.count(Task.id).label('count')
        ).filter(Task.project_id == project_id).group_by(Task.status).all()
        
        # Convert to dict
        status_counts = {status: count for status, count in task_stats}
        total_tasks = sum(status_counts.values())
        completed_tasks = status_counts.get("done", 0)
        in_progress_tasks = status_counts.get("in_progress", 0)
        blocked_tasks = status_counts.get("blocked", 0)
        
        completion_percentage = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        )
        
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "priority": project.priority,
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "target_end_date": project.target_end_date.isoformat() if project.target_end_date else None,
            "actual_end_date": project.actual_end_date.isoformat() if project.actual_end_date else None,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
            "created_by": project.created_by,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "blocked_tasks": blocked_tasks,
            "completion_percentage": round(completion_percentage, 1)
        }
    
    @staticmethod
    def get_tasks_with_hierarchy(
        db: Session,
        project_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        assigned_to: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> List[Dict[str, Any]]:
        """Get tasks with hierarchy information"""
        
        # Base query
        query = db.query(Task)
        
        # Apply filters
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if parent_task_id:
            query = query.filter(Task.parent_task_id == parent_task_id)
        if status:
            query = query.filter(Task.status == status)
        if task_type:
            query = query.filter(Task.task_type == task_type)
        if assigned_to:
            query = query.filter(Task.assigned_to == assigned_to)
        
        # Apply pagination
        offset = (page - 1) * size
        tasks = query.offset(offset).limit(size).all()
        
        # Calculate subtask counts
        result = []
        for task in tasks:
            subtask_count = db.query(Task).filter(Task.parent_task_id == task.id).count()
            
            task_dict = {
                "id": task.id,
                "project_id": task.project_id,
                "parent_task_id": task.parent_task_id,
                "title": task.title,
                "description": task.description,
                "task_type": task.task_type,
                "status": task.status,
                "priority": task.priority,
                "story_points": task.story_points,
                "estimated_hours": float(task.estimated_hours) if task.estimated_hours else None,
                "actual_hours": float(task.actual_hours) if task.actual_hours else None,
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed_date": task.completed_date.isoformat() if task.completed_date else None,
                "assigned_to": task.assigned_to,
                "created_by": task.created_by,
                "order_index": task.order_index,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "subtask_count": subtask_count
            }
            result.append(task_dict)
        
        return result
    
    @staticmethod
    def get_goals_with_progress(
        db: Session,
        parent_goal_id: Optional[str] = None,
        goal_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> List[Dict[str, Any]]:
        """Get goals with calculated progress from linked projects"""
        
        # Base query
        query = db.query(Goal)
        
        # Apply filters
        if parent_goal_id:
            query = query.filter(Goal.parent_goal_id == parent_goal_id)
        if goal_type:
            query = query.filter(Goal.goal_type == goal_type)
        if status:
            query = query.filter(Goal.status == status)
        if search:
            search_filter = or_(
                Goal.title.ilike(f"%{search}%"),
                Goal.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Apply pagination
        offset = (page - 1) * size
        goals = query.offset(offset).limit(size).all()
        
        # Calculate progress from linked projects
        result = []
        for goal in goals:
            # Get linked projects and their weights
            project_links = db.query(GoalProject).filter(
                GoalProject.goal_id == goal.id
            ).all()
            
            if project_links:
                # Calculate weighted progress
                total_weight = sum(link.weight for link in project_links)
                weighted_progress = 0.0
                
                for link in project_links:
                    project_progress = QueryUtils.get_project_completion_percentage(
                        db, link.project_id
                    )
                    weighted_progress += project_progress * float(link.weight)
                
                calculated_progress = weighted_progress / float(total_weight) if total_weight > 0 else 0.0
            else:
                calculated_progress = float(goal.progress_percentage)
            
            subgoal_count = db.query(Goal).filter(Goal.parent_goal_id == goal.id).count()
            
            goal_dict = {
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
            result.append(goal_dict)
        
        return result
    
    @staticmethod
    def get_project_completion_percentage(db: Session, project_id: str) -> float:
        """Calculate project completion percentage"""
        total_tasks = db.query(Task).filter(Task.project_id == project_id).count()
        if total_tasks == 0:
            return 0.0
        
        completed_tasks = db.query(Task).filter(
            Task.project_id == project_id,
            Task.status == "done"
        ).count()
        
        return (completed_tasks / total_tasks) * 100
    
    @staticmethod
    def validate_task_hierarchy(db: Session, task_id: str, parent_task_id: str) -> bool:
        """Validate that setting parent_task_id doesn't create a cycle"""
        if task_id == parent_task_id:
            return False
        
        # Check if parent_task_id is a descendant of task_id
        current_id = parent_task_id
        visited = set()
        
        while current_id and current_id not in visited:
            visited.add(current_id)
            task = db.query(Task).filter(Task.id == current_id).first()
            if not task:
                break
            if task.parent_task_id == task_id:
                return False  # Would create a cycle
            current_id = task.parent_task_id
        
        return True


class TransactionManager:
    """Context manager for database transactions"""
    
    def __init__(self, db: Session):
        self.db = db
        self.committed = False
    
    def __enter__(self):
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and not self.committed:
            self.db.commit()
            self.committed = True
        elif exc_type is not None:
            self.db.rollback()
    
    def commit(self):
        """Manually commit the transaction"""
        if not self.committed:
            self.db.commit()
            self.committed = True
    
    def rollback(self):
        """Manually rollback the transaction"""
        self.db.rollback()
