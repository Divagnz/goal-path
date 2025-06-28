"""
Project Service
Contains all business logic for project management
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .base_service import BaseService
from ..models import Project, Task, GoalProject
from ..db_utils import QueryUtils, TransactionManager
from ..schemas import ProjectCreate, ProjectUpdate, ProjectResponse


class ProjectService(BaseService):
    """Service for project business logic operations"""
    
    def calculate_project_statistics(self, project_id: str) -> Dict[str, Any]:
        """Calculate comprehensive project statistics"""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Get all tasks for this project
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()
        
        # Calculate basic statistics
        total_tasks = len(tasks)
        completed_tasks = len([task for task in tasks if task.status == "done"])
        in_progress_tasks = len([task for task in tasks if task.status == "in_progress"])
        todo_tasks = len([task for task in tasks if task.status == "todo"])
        blocked_tasks = len([task for task in tasks if task.status == "blocked"])
        
        # Calculate completion percentage
        completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        
        # Calculate task breakdown by priority
        priority_breakdown = {}
        for task in tasks:
            priority = task.priority
            priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
        
        # Calculate estimated vs actual hours
        total_estimated_hours = sum(task.estimated_hours or 0 for task in tasks)
        total_actual_hours = sum(task.actual_hours or 0 for task in tasks)
        
        # Calculate overdue tasks
        today = date.today()
        overdue_tasks = len([
            task for task in tasks 
            if task.due_date and task.due_date < today and task.status not in ["done", "cancelled"]
        ])
        
        # Get linked goals
        goal_links = self.db.query(GoalProject).filter(GoalProject.project_id == project_id).all()
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "todo_tasks": todo_tasks,
            "blocked_tasks": blocked_tasks,
            "overdue_tasks": overdue_tasks,
            "completion_percentage": round(completion_percentage, 1),
            "priority_breakdown": priority_breakdown,
            "total_estimated_hours": total_estimated_hours,
            "total_actual_hours": total_actual_hours,
            "linked_goals": len(goal_links),
            "status": project.status,
            "priority": project.priority,
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "target_end_date": project.target_end_date.isoformat() if project.target_end_date else None,
            "actual_end_date": project.actual_end_date.isoformat() if project.actual_end_date else None,
        }
    
    def get_project_with_statistics(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project with calculated statistics"""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        
        stats = self.calculate_project_statistics(project_id)
        
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
            "total_tasks": stats["total_tasks"],
            "completed_tasks": stats["completed_tasks"],
            "completion_percentage": stats["completion_percentage"],
        }
    
    def list_projects_with_statistics(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List projects with basic statistics"""
        query = self.db.query(Project)
        
        # Apply filters
        if status:
            query = query.filter(Project.status == status)
        if priority:
            query = query.filter(Project.priority == priority)
        if search:
            query = query.filter(
                Project.name.contains(search) | Project.description.contains(search)
            )
        
        # Order by updated_at desc and apply pagination
        projects = query.order_by(Project.updated_at.desc()).offset(skip).limit(limit).all()
        
        # Add statistics to each project
        result = []
        for project in projects:
            # Get basic task statistics efficiently
            total_tasks = self.db.query(Task).filter(Task.project_id == project.id).count()
            completed_tasks = self.db.query(Task).filter(
                Task.project_id == project.id, Task.status == "done"
            ).count()
            
            completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
            
            result.append({
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
                "completion_percentage": round(completion_percentage, 1),
            })
        
        return result
    
    def create_project(self, project_data: ProjectCreate) -> Dict[str, Any]:
        """Create a new project"""
        with TransactionManager(self.db) as db_session:
            # Create new project instance
            project_dict = project_data.model_dump()
            
            new_project = Project(**project_dict)
            db_session.add(new_project)
            db_session.commit()
            db_session.refresh(new_project)
            
            return {
                "id": new_project.id,
                "name": new_project.name,
                "description": new_project.description,
                "status": new_project.status,
                "priority": new_project.priority,
                "start_date": new_project.start_date.isoformat() if new_project.start_date else None,
                "target_end_date": new_project.target_end_date.isoformat() if new_project.target_end_date else None,
                "actual_end_date": new_project.actual_end_date.isoformat() if new_project.actual_end_date else None,
                "created_at": new_project.created_at.isoformat(),
                "updated_at": new_project.updated_at.isoformat(),
                "created_by": new_project.created_by,
                "total_tasks": 0,
                "completed_tasks": 0,
                "completion_percentage": 0.0,
            }
    
    def update_project(self, project_id: str, project_update: ProjectUpdate) -> Dict[str, Any]:
        """Update project with validation"""
        with TransactionManager(self.db) as db_session:
            project = db_session.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")
            
            # Get update data
            update_data = project_update.model_dump(exclude_unset=True)
            
            # Business logic: If status is being set to "completed", set actual_end_date
            if update_data.get("status") == "completed" and not project.actual_end_date:
                update_data["actual_end_date"] = date.today()
            
            # Update fields
            for field, value in update_data.items():
                setattr(project, field, value)
            
            db_session.commit()
            db_session.refresh(project)
            
            # Get current statistics
            stats = self.calculate_project_statistics(project_id)
            
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
                "total_tasks": stats["total_tasks"],
                "completed_tasks": stats["completed_tasks"],
                "completion_percentage": stats["completion_percentage"],
            }
    
    def delete_project(self, project_id: str) -> str:
        """Delete project with validation"""
        with TransactionManager(self.db) as db_session:
            project = db_session.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")
            
            project_name = project.name
            
            # Check if project has tasks
            task_count = db_session.query(Task).filter(Task.project_id == project_id).count()
            if task_count > 0:
                raise ValueError(f"Cannot delete project '{project_name}' - it has {task_count} associated tasks")
            
            # Check if project is linked to goals
            goal_links = db_session.query(GoalProject).filter(GoalProject.project_id == project_id).all()
            if goal_links:
                raise ValueError(f"Cannot delete project '{project_name}' - it is linked to {len(goal_links)} goals")
            
            # Delete the project
            db_session.delete(project)
            db_session.commit()
            
            return f"Project '{project_name}' deleted successfully"
    
    def archive_project(self, project_id: str) -> Dict[str, Any]:
        """Archive project (soft delete alternative)"""
        return self.update_project(project_id, ProjectUpdate(status="archived"))
    
    def get_project_tasks(self, project_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all tasks for a project with optional status filter"""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
        
        query = self.db.query(Task).filter(Task.project_id == project_id)
        if status:
            query = query.filter(Task.status == status)
        
        tasks = query.order_by(Task.created_at.desc()).all()
        
        result = []
        for task in tasks:
            result.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "task_type": task.task_type,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "estimated_hours": task.estimated_hours,
                "actual_hours": task.actual_hours,
                "assigned_to": task.assigned_to,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            })
        
        return result
    
    def calculate_project_health(self, project_id: str) -> Dict[str, Any]:
        """Calculate project health metrics"""
        stats = self.calculate_project_statistics(project_id)
        project = self.db.query(Project).filter(Project.id == project_id).first()
        
        # Calculate health score based on various factors
        health_score = 100
        health_factors = []
        
        # Factor 1: Overdue tasks
        if stats["overdue_tasks"] > 0:
            overdue_penalty = min(stats["overdue_tasks"] * 10, 30)
            health_score -= overdue_penalty
            health_factors.append(f"{stats['overdue_tasks']} overdue tasks (-{overdue_penalty} points)")
        
        # Factor 2: Blocked tasks
        if stats["blocked_tasks"] > 0:
            blocked_penalty = min(stats["blocked_tasks"] * 15, 25)
            health_score -= blocked_penalty
            health_factors.append(f"{stats['blocked_tasks']} blocked tasks (-{blocked_penalty} points)")
        
        # Factor 3: Progress vs timeline
        if project.target_end_date and project.start_date:
            today = date.today()
            total_duration = (project.target_end_date - project.start_date).days
            elapsed_duration = (today - project.start_date).days
            
            if total_duration > 0:
                expected_progress = (elapsed_duration / total_duration) * 100
                actual_progress = stats["completion_percentage"]
                progress_gap = expected_progress - actual_progress
                
                if progress_gap > 20:  # Behind schedule by more than 20%
                    schedule_penalty = min(progress_gap, 30)
                    health_score -= schedule_penalty
                    health_factors.append(f"Behind schedule by {progress_gap:.1f}% (-{schedule_penalty:.1f} points)")
        
        # Factor 4: Task distribution
        if stats["total_tasks"] > 0:
            in_progress_ratio = stats["in_progress_tasks"] / stats["total_tasks"]
            if in_progress_ratio > 0.7:  # Too many tasks in progress
                multitask_penalty = 10
                health_score -= multitask_penalty
                health_factors.append(f"Too many tasks in progress (-{multitask_penalty} points)")
        
        # Ensure health score is between 0 and 100
        health_score = max(0, min(100, health_score))
        
        # Determine health status
        if health_score >= 80:
            health_status = "Excellent"
        elif health_score >= 60:
            health_status = "Good"
        elif health_score >= 40:
            health_status = "Fair"
        elif health_score >= 20:
            health_status = "Poor"
        else:
            health_status = "Critical"
        
        return {
            "project_id": project_id,
            "health_score": round(health_score, 1),
            "health_status": health_status,
            "health_factors": health_factors,
            "recommendations": self._generate_health_recommendations(stats, health_factors),
        }
    
    def _generate_health_recommendations(self, stats: Dict, health_factors: List[str]) -> List[str]:
        """Generate recommendations based on project health"""
        recommendations = []
        
        if stats["overdue_tasks"] > 0:
            recommendations.append("Review and reschedule overdue tasks")
        
        if stats["blocked_tasks"] > 0:
            recommendations.append("Resolve blocked tasks to improve flow")
        
        if stats["total_tasks"] > 0:
            in_progress_ratio = stats["in_progress_tasks"] / stats["total_tasks"]
            if in_progress_ratio > 0.7:
                recommendations.append("Consider limiting work in progress to improve focus")
        
        if stats["completion_percentage"] < 50 and "Behind schedule" in str(health_factors):
            recommendations.append("Consider adding resources or reducing scope")
        
        if not recommendations:
            recommendations.append("Project is on track - maintain current pace")
        
        return recommendations