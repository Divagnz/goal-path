"""
Issue Service
Contains all business logic for issue management
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .base_service import BaseService
from ..models import Task, Project, TaskDependency
from ..models.epics import Epic, Milestone
from ..models.extended import Issue, IssueStatus
from ..db_utils import TransactionManager
from ..schemas import IssueCreate, IssueUpdate, IssueResponse


class IssueService(BaseService):
    """Service for issue business logic operations"""
    
    def get_issue_with_details(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """Get issue with all related information"""
        issue = self.db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            return None
        
        # Get related entities
        project = self.db.query(Project).filter(Project.id == issue.project_id).first() if issue.project_id else None
        promoted_task = self.db.query(Task).filter(Task.id == issue.promoted_to_task_id).first() if issue.promoted_to_task_id else None
        
        return {
            "id": issue.id,
            "title": issue.title,
            "description": issue.description,
            "issue_type": issue.issue_type,
            "status": issue.status,
            "priority": issue.priority,
            "assignee": issue.assignee,
            "reporter": issue.reporter,
            "project_id": issue.project_id,
            "promoted_to_task_id": issue.promoted_to_task_id,
            "created_at": issue.created_at.isoformat(),
            "updated_at": issue.updated_at.isoformat(),
            "project_name": project.name if project else None,
            "promoted_task_title": promoted_task.title if promoted_task else None,
        }
    
    def list_issues_with_filters(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        issue_type: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List issues with comprehensive filtering"""
        query = self.db.query(Issue)
        
        # Apply filters
        if project_id:
            query = query.filter(Issue.project_id == project_id)
        if status:
            query = query.filter(Issue.status == status)
        if issue_type:
            query = query.filter(Issue.issue_type == issue_type)
        if priority:
            query = query.filter(Issue.priority == priority)
        if assignee:
            query = query.filter(Issue.assignee == assignee)
        
        # Order by priority and creation date
        issues = query.order_by(
            Issue.priority.desc(),
            Issue.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        # Enrich with related data
        result = []
        for issue in issues:
            project = self.db.query(Project).filter(Project.id == issue.project_id).first() if issue.project_id else None
            
            result.append({
                "id": issue.id,
                "title": issue.title,
                "description": issue.description,
                "issue_type": issue.issue_type,
                "status": issue.status,
                "priority": issue.priority,
                "assignee": issue.assignee,
                "reporter": issue.reporter,
                "project_id": issue.project_id,
                "promoted_to_task_id": issue.promoted_to_task_id,
                "created_at": issue.created_at.isoformat(),
                "updated_at": issue.updated_at.isoformat(),
                "project_name": project.name if project else None,
            })
        
        return result
    
    def create_issue(self, issue_data: IssueCreate) -> Dict[str, Any]:
        """Create a new issue with validation"""
        with TransactionManager(self.db) as db_session:
            # Validate project exists if provided
            if issue_data.project_id:
                project = db_session.query(Project).filter(Project.id == issue_data.project_id).first()
                if not project:
                    raise ValueError(f"Project with ID {issue_data.project_id} not found")
            
            # Create issue
            issue_dict = issue_data.model_dump()
            
            new_issue = Issue(**issue_dict)
            db_session.add(new_issue)
            db_session.commit()
            db_session.refresh(new_issue)
            
            return self.get_issue_with_details(new_issue.id)
    
    def update_issue(self, issue_id: str, issue_update: IssueUpdate) -> Dict[str, Any]:
        """Update issue with business logic validation"""
        with TransactionManager(self.db) as db_session:
            issue = db_session.query(Issue).filter(Issue.id == issue_id).first()
            if not issue:
                raise ValueError(f"Issue with ID {issue_id} not found")
            
            # Get update data
            update_data = issue_update.model_dump(exclude_unset=True)
            
            # Business logic: Prevent changing status of promoted issues
            if issue.status == IssueStatus.PROMOTED and "status" in update_data:
                if update_data["status"] != IssueStatus.PROMOTED:
                    raise ValueError("Cannot change status of promoted issue. Update the associated task instead.")
            
            # Validate project change
            if "project_id" in update_data and update_data["project_id"] != issue.project_id:
                if update_data["project_id"]:
                    project = db_session.query(Project).filter(Project.id == update_data["project_id"]).first()
                    if not project:
                        raise ValueError(f"Project with ID {update_data['project_id']} not found")
            
            # Update fields
            for field, value in update_data.items():
                setattr(issue, field, value)
            
            db_session.commit()
            db_session.refresh(issue)
            
            return self.get_issue_with_details(issue_id)
    
    def update_issue_status(self, issue_id: str, new_status: str) -> Dict[str, Any]:
        """Quick status update with business logic"""
        return self.update_issue(issue_id, IssueUpdate(status=new_status))
    
    def delete_issue(self, issue_id: str) -> str:
        """Delete issue with validation"""
        with TransactionManager(self.db) as db_session:
            issue = db_session.query(Issue).filter(Issue.id == issue_id).first()
            if not issue:
                raise ValueError(f"Issue with ID {issue_id} not found")
            
            issue_title = issue.title
            
            # Check if issue has been promoted to a task
            if issue.promoted_to_task_id:
                raise ValueError(f"Cannot delete issue '{issue_title}' - it has been promoted to a task")
            
            # Delete the issue
            db_session.delete(issue)
            db_session.commit()
            
            return f"Issue '{issue_title}' deleted successfully"
    
    def promote_issue_to_task(
        self, 
        issue_id: str, 
        task_title: Optional[str] = None,
        epic_id: Optional[str] = None,
        milestone_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Promote an issue to a task with epic/milestone assignment"""
        with TransactionManager(self.db) as db_session:
            issue = db_session.query(Issue).filter(Issue.id == issue_id).first()
            if not issue:
                raise ValueError(f"Issue with ID {issue_id} not found")
            
            if issue.status == IssueStatus.PROMOTED:
                raise ValueError("Issue has already been promoted to a task")
            
            # Validate epic exists if provided
            if epic_id:
                epic = db_session.query(Epic).filter(Epic.id == epic_id).first()
                if not epic:
                    raise ValueError(f"Epic with ID {epic_id} not found")
            
            # Validate milestone exists if provided
            if milestone_id:
                milestone = db_session.query(Milestone).filter(Milestone.id == milestone_id).first()
                if not milestone:
                    raise ValueError(f"Milestone with ID {milestone_id} not found")
            
            # Create the new task
            task_data = {
                "title": task_title or issue.title,
                "description": issue.description,
                "task_type": "task",
                "status": "backlog",
                "priority": issue.priority,
                "project_id": issue.project_id,
                "assigned_to": issue.assignee,
                "created_by": f"promoted_from_issue_{issue.id}",
            }
            
            # Add epic and milestone if provided
            if epic_id:
                task_data["epic_id"] = epic_id
            if milestone_id:
                task_data["milestone_id"] = milestone_id
            
            # Create the task
            task = Task(**task_data)
            db_session.add(task)
            db_session.flush()  # Get the task ID
            
            # Update the issue to promoted status and link to the task
            issue.status = IssueStatus.PROMOTED
            issue.promoted_to_task_id = task.id
            
            # Create a blocking dependency: the promoted task is blocked by the issue resolution
            # Note: This assumes TaskDependency can handle issue IDs as dependencies
            dependency = TaskDependency(
                task_id=task.id,
                depends_on_task_id=issue.id,  # This might need model adjustment
                dependency_type="blocks"
            )
            db_session.add(dependency)
            
            db_session.commit()
            db_session.refresh(task)
            
            # Return task details
            return {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "task_type": task.task_type,
                "status": task.status,
                "priority": task.priority,
                "project_id": task.project_id,
                "epic_id": task.epic_id,
                "milestone_id": task.milestone_id,
                "assigned_to": task.assigned_to,
                "created_by": task.created_by,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "promoted_from_issue_id": issue_id,
            }
    
    def get_promoted_task(self, issue_id: str) -> Dict[str, Any]:
        """Get the task that was created from promoting this issue"""
        issue = self.db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise ValueError(f"Issue with ID {issue_id} not found")
        
        if not issue.promoted_to_task_id:
            raise ValueError("Issue has not been promoted to a task")
        
        task = self.db.query(Task).filter(Task.id == issue.promoted_to_task_id).first()
        if not task:
            raise ValueError("Promoted task not found")
        
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "task_type": task.task_type,
            "status": task.status,
            "priority": task.priority,
            "project_id": task.project_id,
            "assigned_to": task.assigned_to,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }
    
    def list_promoted_issues(
        self,
        project_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List all promoted issues"""
        query = self.db.query(Issue).filter(Issue.status == IssueStatus.PROMOTED)
        
        if project_id:
            query = query.filter(Issue.project_id == project_id)
        
        issues = query.order_by(Issue.updated_at.desc()).offset(skip).limit(limit).all()
        
        result = []
        for issue in issues:
            project = self.db.query(Project).filter(Project.id == issue.project_id).first() if issue.project_id else None
            promoted_task = self.db.query(Task).filter(Task.id == issue.promoted_to_task_id).first() if issue.promoted_to_task_id else None
            
            result.append({
                "id": issue.id,
                "title": issue.title,
                "description": issue.description,
                "issue_type": issue.issue_type,
                "status": issue.status,
                "priority": issue.priority,
                "assignee": issue.assignee,
                "reporter": issue.reporter,
                "project_id": issue.project_id,
                "promoted_to_task_id": issue.promoted_to_task_id,
                "created_at": issue.created_at.isoformat(),
                "updated_at": issue.updated_at.isoformat(),
                "project_name": project.name if project else None,
                "promoted_task_title": promoted_task.title if promoted_task else None,
                "promoted_task_status": promoted_task.status if promoted_task else None,
            })
        
        return result
    
    def calculate_issue_metrics(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate issue metrics for analysis"""
        query = self.db.query(Issue)
        if project_id:
            query = query.filter(Issue.project_id == project_id)
        
        issues = query.all()
        
        # Calculate basic counts
        total_issues = len(issues)
        status_counts = {}
        type_counts = {}
        priority_counts = {}
        
        for issue in issues:
            # Status breakdown
            status = issue.status
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Type breakdown
            issue_type = issue.issue_type
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
            
            # Priority breakdown
            priority = issue.priority
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Calculate resolution metrics
        resolved_issues = [i for i in issues if i.status in ['resolved', 'closed']]
        promoted_issues = [i for i in issues if i.status == 'promoted']
        
        # Calculate average resolution time (simplified - would need more sophisticated tracking)
        avg_resolution_time = None
        if resolved_issues:
            total_resolution_time = sum(
                (issue.updated_at - issue.created_at).total_seconds() 
                for issue in resolved_issues
            )
            avg_resolution_time = total_resolution_time / len(resolved_issues) / 3600  # hours
        
        return {
            "total_issues": total_issues,
            "status_breakdown": status_counts,
            "type_breakdown": type_counts,
            "priority_breakdown": priority_counts,
            "resolved_count": len(resolved_issues),
            "promoted_count": len(promoted_issues),
            "resolution_rate": (len(resolved_issues) / total_issues * 100) if total_issues > 0 else 0,
            "promotion_rate": (len(promoted_issues) / total_issues * 100) if total_issues > 0 else 0,
            "avg_resolution_time_hours": round(avg_resolution_time, 2) if avg_resolution_time else None,
            "project_id": project_id,
        }
    
    def get_issue_timeline(self, issue_id: str) -> List[Dict[str, Any]]:
        """Get timeline of changes for an issue (simplified version)"""
        issue = self.db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise ValueError(f"Issue with ID {issue_id} not found")
        
        # In a real system, this would query an audit/history table
        # For now, return basic timeline
        timeline = [
            {
                "event": "created",
                "timestamp": issue.created_at.isoformat(),
                "user": issue.reporter,
                "details": f"Issue '{issue.title}' created",
            }
        ]
        
        if issue.status == IssueStatus.PROMOTED and issue.promoted_to_task_id:
            timeline.append({
                "event": "promoted",
                "timestamp": issue.updated_at.isoformat(),
                "user": "system",
                "details": f"Issue promoted to task {issue.promoted_to_task_id}",
            })
        
        return timeline