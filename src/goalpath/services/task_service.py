"""
Task Service
Contains all business logic for task management
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .base_service import BaseService
from ..models import Task, Project, TaskDependency
from ..models.epics import Epic, Milestone
from ..db_utils import QueryUtils, TransactionManager
from ..schemas import TaskCreate, TaskUpdate, TaskResponse


class TaskService(BaseService):
    """Service for task business logic operations"""
    
    def get_task_with_details(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task with all related information"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        # Get related entities
        project = self.db.query(Project).filter(Project.id == task.project_id).first() if task.project_id else None
        parent_task = self.db.query(Task).filter(Task.id == task.parent_task_id).first() if task.parent_task_id else None
        
        # Get subtasks
        subtasks = self.db.query(Task).filter(Task.parent_task_id == task_id).all()
        
        # Get dependencies
        dependencies = self.db.query(TaskDependency).filter(TaskDependency.task_id == task_id).all()
        blocking = self.db.query(TaskDependency).filter(TaskDependency.depends_on_task_id == task_id).all()
        
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "task_type": task.task_type,
            "status": task.status,
            "priority": task.priority,
            "story_points": task.story_points,
            "estimated_hours": task.estimated_hours,
            "actual_hours": task.actual_hours,
            "start_date": task.start_date.isoformat() if task.start_date else None,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed_date": task.completed_date.isoformat() if task.completed_date else None,
            "assigned_to": task.assigned_to,
            "project_id": task.project_id,
            "parent_task_id": task.parent_task_id,
            "epic_id": task.epic_id,
            "milestone_id": task.milestone_id,
            "created_by": task.created_by,
            "order_index": task.order_index,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "project_name": project.name if project else None,
            "parent_task_title": parent_task.title if parent_task else None,
            "subtask_count": len(subtasks),
            "dependency_count": len(dependencies),
            "blocking_count": len(blocking),
        }
    
    def list_tasks_with_filters(
        self,
        project_id: Optional[str] = None,
        milestone_id: Optional[str] = None,
        epic_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        assigned_to: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List tasks with comprehensive filtering"""
        query = self.db.query(Task)
        
        # Apply filters
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if milestone_id:
            query = query.filter(Task.milestone_id == milestone_id)
        if epic_id:
            query = query.filter(Task.epic_id == epic_id)
        if parent_task_id:
            query = query.filter(Task.parent_task_id == parent_task_id)
        if status:
            query = query.filter(Task.status == status)
        if task_type:
            query = query.filter(Task.task_type == task_type)
        if assigned_to:
            query = query.filter(Task.assigned_to == assigned_to)
        if search:
            query = query.filter(
                Task.title.contains(search) | Task.description.contains(search)
            )
        
        # Order by priority, then due date, then created date
        tasks = query.order_by(
            Task.priority.desc(),
            Task.due_date.asc().nullslast(),
            Task.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        # Enrich with related data
        result = []
        for task in tasks:
            project = self.db.query(Project).filter(Project.id == task.project_id).first() if task.project_id else None
            subtask_count = self.db.query(Task).filter(Task.parent_task_id == task.id).count()
            
            result.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "task_type": task.task_type,
                "status": task.status,
                "priority": task.priority,
                "story_points": task.story_points,
                "estimated_hours": task.estimated_hours,
                "actual_hours": task.actual_hours,
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "assigned_to": task.assigned_to,
                "project_id": task.project_id,
                "parent_task_id": task.parent_task_id,
                "created_by": task.created_by,
                "order_index": task.order_index,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "project_name": project.name if project else None,
                "subtask_count": subtask_count,
                "dependency_count": 0,  # Could be calculated if needed
            })
        
        return result
    
    def create_task(self, task_data: TaskCreate) -> Dict[str, Any]:
        """Create a new task with validation"""
        with TransactionManager(self.db) as db_session:
            # Validate project exists if provided
            if task_data.project_id:
                project = db_session.query(Project).filter(Project.id == task_data.project_id).first()
                if not project:
                    raise ValueError(f"Project with ID {task_data.project_id} not found")
            
            # Validate parent task exists if provided
            if task_data.parent_task_id:
                parent_task = db_session.query(Task).filter(Task.id == task_data.parent_task_id).first()
                if not parent_task:
                    raise ValueError(f"Parent task with ID {task_data.parent_task_id} not found")
                
                # Inherit project from parent if not specified
                if not task_data.project_id and parent_task.project_id:
                    task_data.project_id = parent_task.project_id
            
            # Validate epic exists if provided
            if task_data.epic_id:
                epic = db_session.query(Epic).filter(Epic.id == task_data.epic_id).first()
                if not epic:
                    raise ValueError(f"Epic with ID {task_data.epic_id} not found")
            
            # Validate milestone exists if provided
            if task_data.milestone_id:
                milestone = db_session.query(Milestone).filter(Milestone.id == task_data.milestone_id).first()
                if not milestone:
                    raise ValueError(f"Milestone with ID {task_data.milestone_id} not found")
            
            # Get next order index for the project
            max_order = db_session.query(Task.order_index).filter(
                Task.project_id == task_data.project_id
            ).order_by(Task.order_index.desc()).first()
            next_order = (max_order[0] + 1) if max_order and max_order[0] else 1
            
            # Create task
            task_dict = task_data.model_dump()
            task_dict["order_index"] = next_order
            
            new_task = Task(**task_dict)
            db_session.add(new_task)
            db_session.commit()
            db_session.refresh(new_task)
            
            return self.get_task_with_details(new_task.id)
    
    def update_task(self, task_id: str, task_update: TaskUpdate) -> Dict[str, Any]:
        """Update task with business logic validation"""
        with TransactionManager(self.db) as db_session:
            task = db_session.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise ValueError(f"Task with ID {task_id} not found")
            
            # Get update data
            update_data = task_update.model_dump(exclude_unset=True)
            
            # Business logic: Set completed_date when status changes to 'done'
            if update_data.get("status") == "done" and task.status != "done":
                update_data["completed_date"] = datetime.now()
            elif update_data.get("status") != "done" and task.status == "done":
                update_data["completed_date"] = None
            
            # Validate project change
            if "project_id" in update_data and update_data["project_id"] != task.project_id:
                if update_data["project_id"]:
                    project = db_session.query(Project).filter(Project.id == update_data["project_id"]).first()
                    if not project:
                        raise ValueError(f"Project with ID {update_data['project_id']} not found")
            
            # Update fields
            for field, value in update_data.items():
                setattr(task, field, value)
            
            db_session.commit()
            db_session.refresh(task)
            
            return self.get_task_with_details(task_id)
    
    def update_task_status(self, task_id: str, new_status: str) -> Dict[str, Any]:
        """Quick status update with business logic"""
        return self.update_task(task_id, TaskUpdate(status=new_status))
    
    def delete_task(self, task_id: str, handle_subtasks: str = "cascade") -> str:
        """Delete task with subtask handling"""
        with TransactionManager(self.db) as db_session:
            task = db_session.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise ValueError(f"Task with ID {task_id} not found")
            
            task_title = task.title
            
            # Handle subtasks
            subtasks = db_session.query(Task).filter(Task.parent_task_id == task_id).all()
            
            if subtasks:
                if handle_subtasks == "cascade":
                    # Delete all subtasks
                    for subtask in subtasks:
                        db_session.delete(subtask)
                elif handle_subtasks == "reassign":
                    # Promote subtasks to same level as current task
                    for subtask in subtasks:
                        subtask.parent_task_id = task.parent_task_id
            
            # Delete task dependencies
            db_session.query(TaskDependency).filter(
                (TaskDependency.task_id == task_id) | (TaskDependency.depends_on_task_id == task_id)
            ).delete()
            
            # Delete the task
            db_session.delete(task)
            db_session.commit()
            
            action_desc = f" and {len(subtasks)} subtasks" if handle_subtasks == "cascade" and subtasks else ""
            return f"Task '{task_title}'{action_desc} deleted successfully"
    
    def get_task_subtasks(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all subtasks for a specific task"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        subtasks = self.db.query(Task).filter(Task.parent_task_id == task_id).order_by(Task.order_index).all()
        
        result = []
        for subtask in subtasks:
            result.append({
                "id": subtask.id,
                "title": subtask.title,
                "description": subtask.description,
                "status": subtask.status,
                "priority": subtask.priority,
                "task_type": subtask.task_type,
                "due_date": subtask.due_date.isoformat() if subtask.due_date else None,
                "assigned_to": subtask.assigned_to,
                "estimated_hours": subtask.estimated_hours,
                "actual_hours": subtask.actual_hours,
                "created_at": subtask.created_at.isoformat(),
                "updated_at": subtask.updated_at.isoformat(),
            })
        
        return result
    
    def calculate_task_completion_time(self, task_id: str) -> Dict[str, Any]:
        """Calculate task completion metrics"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        metrics = {
            "task_id": task_id,
            "task_title": task.title,
            "status": task.status,
            "estimated_hours": task.estimated_hours,
            "actual_hours": task.actual_hours,
            "created_at": task.created_at.isoformat(),
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed_date": task.completed_date.isoformat() if task.completed_date else None,
        }
        
        # Calculate cycle time (creation to completion)
        if task.completed_date:
            cycle_time = (task.completed_date - task.created_at).total_seconds() / 3600  # hours
            metrics["cycle_time_hours"] = round(cycle_time, 2)
        else:
            metrics["cycle_time_hours"] = None
        
        # Calculate lead time (due date performance)
        if task.due_date and task.completed_date:
            lead_time = (task.completed_date.date() - task.due_date).days
            metrics["lead_time_days"] = lead_time
            metrics["on_time"] = lead_time <= 0
        else:
            metrics["lead_time_days"] = None
            metrics["on_time"] = None
        
        # Calculate effort variance
        if task.estimated_hours and task.actual_hours:
            variance = ((task.actual_hours - task.estimated_hours) / task.estimated_hours) * 100
            metrics["effort_variance_percent"] = round(variance, 1)
            metrics["over_estimated"] = variance < -10
            metrics["under_estimated"] = variance > 10
        else:
            metrics["effort_variance_percent"] = None
            metrics["over_estimated"] = None
            metrics["under_estimated"] = None
        
        return metrics
    
    def get_task_dependencies(self, task_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get task dependencies and what this task blocks"""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Tasks this task depends on
        dependencies = self.db.query(TaskDependency).filter(TaskDependency.task_id == task_id).all()
        depends_on = []
        for dep in dependencies:
            dep_task = self.db.query(Task).filter(Task.id == dep.depends_on_task_id).first()
            if dep_task:
                depends_on.append({
                    "id": dep_task.id,
                    "title": dep_task.title,
                    "status": dep_task.status,
                    "dependency_type": dep.dependency_type,
                })
        
        # Tasks that depend on this task
        blocking = self.db.query(TaskDependency).filter(TaskDependency.depends_on_task_id == task_id).all()
        blocks = []
        for dep in blocking:
            blocked_task = self.db.query(Task).filter(Task.id == dep.task_id).first()
            if blocked_task:
                blocks.append({
                    "id": blocked_task.id,
                    "title": blocked_task.title,
                    "status": blocked_task.status,
                    "dependency_type": dep.dependency_type,
                })
        
        return {
            "depends_on": depends_on,
            "blocks": blocks,
        }
    
    def reorder_tasks(self, project_id: str, task_orders: List[Dict[str, Any]]) -> str:
        """Reorder tasks within a project"""
        with TransactionManager(self.db) as db_session:
            # Validate project exists
            project = db_session.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise ValueError(f"Project with ID {project_id} not found")
            
            # Update order indices
            for order_data in task_orders:
                task_id = order_data.get("task_id")
                new_order = order_data.get("order_index")
                
                task = db_session.query(Task).filter(
                    Task.id == task_id, Task.project_id == project_id
                ).first()
                
                if task:
                    task.order_index = new_order
            
            db_session.commit()
            
            return f"Reordered {len(task_orders)} tasks in project '{project.name}'"