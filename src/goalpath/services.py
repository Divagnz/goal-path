"""
Database service layer for GoalPath
Centralized database operations for all entities
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, desc, asc, func
from datetime import date, datetime

from .models import Project, Task, Goal, GoalProject, TaskDependency
from .db_utils import QueryUtils, TransactionManager


class ProjectService:
    """Service layer for Project operations"""

    @staticmethod
    def get_all(
        db: Session,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get all projects with optional filtering and pagination"""
        return QueryUtils.get_projects_with_stats(
            db=db, status=status, priority=priority, search=search, page=page, size=size
        )

    @staticmethod
    def get_by_id(db: Session, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID with statistics"""
        return QueryUtils.get_project_with_stats(db, project_id)

    @staticmethod
    def create(db: Session, project_data: dict) -> Dict[str, Any]:
        """Create new project"""
        with TransactionManager(db) as db_session:
            # Add created_by if not provided
            if "created_by" not in project_data or not project_data["created_by"]:
                project_data["created_by"] = "system"

            new_project = Project(**project_data)
            db_session.add(new_project)
            db_session.commit()
            db_session.refresh(new_project)

            return QueryUtils.get_project_with_stats(db_session, new_project.id)

    @staticmethod
    def update(db: Session, project_id: str, update_data: dict) -> Optional[Dict[str, Any]]:
        """Update existing project"""
        with TransactionManager(db) as db_session:
            project = db_session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return None

            for field, value in update_data.items():
                setattr(project, field, value)

            db_session.commit()
            db_session.refresh(project)

            return QueryUtils.get_project_with_stats(db_session, project.id)

    @staticmethod
    def delete(db: Session, project_id: str) -> Optional[str]:
        """Delete project and return its name"""
        with TransactionManager(db) as db_session:
            project = db_session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return None

            project_name = project.name
            db_session.delete(project)
            db_session.commit()

            return project_name

    @staticmethod
    def get_statistics(db: Session, project_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed project statistics"""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None

        project_stats = QueryUtils.get_project_with_stats(db, project_id)

        # Calculate additional statistics
        task_stats = (
            db.query(
                Task.status,
                func.count(Task.id).label("count"),
                func.coalesce(func.sum(Task.estimated_hours), 0).label("estimated_hours"),
                func.coalesce(func.sum(Task.actual_hours), 0).label("actual_hours"),
            )
            .filter(Task.project_id == project_id)
            .group_by(Task.status)
            .all()
        )

        total_estimated_hours = sum(float(stat.estimated_hours or 0) for stat in task_stats)
        total_actual_hours = sum(float(stat.actual_hours or 0) for stat in task_stats)

        # Calculate timeline
        days_since_start = None
        days_until_deadline = None

        if project.start_date:
            days_since_start = (date.today() - project.start_date).days

        if project.target_end_date:
            days_until_deadline = (project.target_end_date - date.today()).days

        return {
            "project_id": project_id,
            "project_name": project.name,
            "total_tasks": project_stats["total_tasks"],
            "completed_tasks": project_stats["completed_tasks"],
            "in_progress_tasks": project_stats["in_progress_tasks"],
            "blocked_tasks": project_stats["blocked_tasks"],
            "completion_percentage": project_stats["completion_percentage"],
            "estimated_hours": total_estimated_hours,
            "actual_hours": total_actual_hours,
            "remaining_hours": max(0, total_estimated_hours - total_actual_hours),
            "days_since_start": days_since_start,
            "days_until_deadline": days_until_deadline,
            "velocity": {
                "tasks_per_week": round(
                    project_stats["completed_tasks"] / max(1, (days_since_start or 1) / 7), 1
                ),
                "hours_per_week": round(
                    total_actual_hours / max(1, (days_since_start or 1) / 7), 1
                ),
            },
            "timeline": {
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "target_end_date": (
                    project.target_end_date.isoformat() if project.target_end_date else None
                ),
                "actual_end_date": (
                    project.actual_end_date.isoformat() if project.actual_end_date else None
                ),
                "is_overdue": (
                    (
                        project.target_end_date
                        and date.today() > project.target_end_date
                        and project.status != "completed"
                    )
                    if project.target_end_date
                    else False
                ),
            },
            "task_breakdown": {
                stat.status: {
                    "count": stat.count,
                    "estimated_hours": float(stat.estimated_hours or 0),
                    "actual_hours": float(stat.actual_hours or 0),
                }
                for stat in task_stats
            },
        }


class TaskService:
    """Service layer for Task operations"""

    @staticmethod
    def get_all(
        db: Session,
        project_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        assigned_to: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get all tasks with filtering and hierarchy information"""
        return QueryUtils.get_tasks_with_hierarchy(
            db=db,
            project_id=project_id,
            parent_task_id=parent_task_id,
            status=status,
            task_type=task_type,
            assigned_to=assigned_to,
            page=page,
            size=size,
        )

    @staticmethod
    def get_by_id(db: Session, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID with hierarchy information"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None

        # Get subtask count
        subtask_count = db.query(Task).filter(Task.parent_task_id == task_id).count()

        # Get dependency count
        dependency_count = (
            db.query(TaskDependency).filter(TaskDependency.task_id == task_id).count()
        )

        return {
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
            "subtask_count": subtask_count,
            "dependency_count": dependency_count,
        }

    @staticmethod
    def create(db: Session, task_data: dict) -> Dict[str, Any]:
        """Create new task with hierarchy validation"""
        with TransactionManager(db) as db_session:
            # Add created_by if not provided
            if "created_by" not in task_data or not task_data["created_by"]:
                task_data["created_by"] = "system"

            # Validate hierarchy if parent_task_id is provided
            if task_data.get("parent_task_id"):
                if not QueryUtils.validate_task_hierarchy(
                    db_session, "new", task_data["parent_task_id"]
                ):
                    raise ValueError("Invalid task hierarchy - would create cycle")

            # Set order_index if not provided
            if "order_index" not in task_data:
                max_order = (
                    db_session.query(func.coalesce(func.max(Task.order_index), 0))
                    .filter(Task.project_id == task_data["project_id"])
                    .scalar()
                )
                task_data["order_index"] = (max_order or 0) + 1

            new_task = Task(**task_data)
            db_session.add(new_task)
            db_session.commit()
            db_session.refresh(new_task)

            return TaskService.get_by_id(db_session, new_task.id)

    @staticmethod
    def update(db: Session, task_id: str, update_data: dict) -> Optional[Dict[str, Any]]:
        """Update existing task with status transition handling"""
        with TransactionManager(db) as db_session:
            task = db_session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return None

            # Handle status transitions
            if "status" in update_data:
                new_status = update_data["status"]
                if new_status == "done" and task.status != "done":
                    update_data["completed_date"] = datetime.now()
                elif new_status != "done" and task.status == "done":
                    update_data["completed_date"] = None

            # Validate hierarchy changes
            if "parent_task_id" in update_data and update_data["parent_task_id"]:
                if not QueryUtils.validate_task_hierarchy(
                    db_session, task_id, update_data["parent_task_id"]
                ):
                    raise ValueError("Invalid task hierarchy - would create cycle")

            for field, value in update_data.items():
                setattr(task, field, value)

            db_session.commit()
            db_session.refresh(task)

            return TaskService.get_by_id(db_session, task.id)

    @staticmethod
    def delete(db: Session, task_id: str) -> Optional[str]:
        """Delete task and return its title"""
        with TransactionManager(db) as db_session:
            task = db_session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return None

            task_title = task.title

            # Handle subtasks - either reassign to parent or delete cascade
            subtasks = db_session.query(Task).filter(Task.parent_task_id == task_id).all()
            for subtask in subtasks:
                subtask.parent_task_id = task.parent_task_id  # Move to grandparent

            db_session.delete(task)
            db_session.commit()

            return task_title

    @staticmethod
    def update_status(db: Session, task_id: str, status: str) -> Optional[Dict[str, Any]]:
        """Quick status update for a task"""
        return TaskService.update(db, task_id, {"status": status})


class GoalService:
    """Service layer for Goal operations"""

    @staticmethod
    def get_all(
        db: Session,
        parent_goal_id: Optional[str] = None,
        goal_type: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get all goals with calculated progress"""
        return QueryUtils.get_goals_with_progress(
            db=db,
            parent_goal_id=parent_goal_id,
            goal_type=goal_type,
            status=status,
            search=search,
            page=page,
            size=size,
        )

    @staticmethod
    def get_by_id(db: Session, goal_id: str) -> Optional[Dict[str, Any]]:
        """Get goal by ID with calculated progress"""
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return None

        # Get linked projects and their weights
        project_links = db.query(GoalProject).filter(GoalProject.goal_id == goal_id).all()

        if project_links:
            # Calculate weighted progress
            total_weight = sum(float(link.weight) for link in project_links)
            weighted_progress = 0.0

            for link in project_links:
                project_progress = QueryUtils.get_project_completion_percentage(db, link.project_id)
                weighted_progress += project_progress * float(link.weight)

            calculated_progress = weighted_progress / total_weight if total_weight > 0 else 0.0
        else:
            calculated_progress = float(goal.progress_percentage)

        subgoal_count = db.query(Goal).filter(Goal.parent_goal_id == goal_id).count()

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

    @staticmethod
    def create(db: Session, goal_data: dict) -> Dict[str, Any]:
        """Create new goal with hierarchy validation"""
        with TransactionManager(db) as db_session:
            # Validate hierarchy if parent_goal_id is provided
            if goal_data.get("parent_goal_id"):
                parent = (
                    db_session.query(Goal).filter(Goal.id == goal_data["parent_goal_id"]).first()
                )
                if not parent:
                    raise ValueError("Parent goal not found")

            new_goal = Goal(**goal_data)
            db_session.add(new_goal)
            db_session.commit()
            db_session.refresh(new_goal)

            return GoalService.get_by_id(db_session, new_goal.id)

    @staticmethod
    def update(db: Session, goal_id: str, update_data: dict) -> Optional[Dict[str, Any]]:
        """Update existing goal with progress recalculation"""
        with TransactionManager(db) as db_session:
            goal = db_session.query(Goal).filter(Goal.id == goal_id).first()
            if not goal:
                return None

            # Validate hierarchy changes
            if "parent_goal_id" in update_data and update_data["parent_goal_id"]:
                parent = (
                    db_session.query(Goal).filter(Goal.id == update_data["parent_goal_id"]).first()
                )
                if not parent:
                    raise ValueError("Parent goal not found")
                # TODO: Add cycle detection for goals

            for field, value in update_data.items():
                setattr(goal, field, value)

            db_session.commit()
            db_session.refresh(goal)

            return GoalService.get_by_id(db_session, goal.id)

    @staticmethod
    def delete(db: Session, goal_id: str) -> Optional[str]:
        """Delete goal and return its title"""
        with TransactionManager(db) as db_session:
            goal = db_session.query(Goal).filter(Goal.id == goal_id).first()
            if not goal:
                return None

            goal_title = goal.title

            # Handle subgoals - move to parent or orphan
            subgoals = db_session.query(Goal).filter(Goal.parent_goal_id == goal_id).all()
            for subgoal in subgoals:
                subgoal.parent_goal_id = goal.parent_goal_id

            # Remove goal-project links
            db_session.query(GoalProject).filter(GoalProject.goal_id == goal_id).delete()

            db_session.delete(goal)
            db_session.commit()

            return goal_title

    @staticmethod
    def get_progress_details(db: Session, goal_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed progress information for a goal"""
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return None

        # Get linked projects with their contributions
        project_links = (
            db.query(GoalProject).join(Project).filter(GoalProject.goal_id == goal_id).all()
        )

        linked_projects = []
        for link in project_links:
            project_completion = QueryUtils.get_project_completion_percentage(db, link.project_id)
            contribution = project_completion * float(link.weight)

            linked_projects.append(
                {
                    "project_id": link.project_id,
                    "project_name": link.project.name,
                    "weight": float(link.weight),
                    "completion": project_completion,
                    "contribution": round(contribution, 2),
                }
            )

        # Calculate days remaining
        days_remaining = None
        if goal.target_date:
            days_remaining = (goal.target_date - date.today()).days

        return {
            "goal_id": goal_id,
            "goal_title": goal.title,
            "current_progress": float(goal.progress_percentage),
            "target_date": goal.target_date.isoformat() if goal.target_date else None,
            "days_remaining": days_remaining,
            "linked_projects": linked_projects,
            "milestones": [],  # TODO: Implement milestones
            "progress_history": [],  # TODO: Implement progress history
        }

    @staticmethod
    def get_subgoals(db: Session, goal_id: str) -> List[Dict[str, Any]]:
        """Get all subgoals for a specific goal"""
        # Verify parent goal exists
        parent_goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not parent_goal:
            return None

        return GoalService.get_all(db, parent_goal_id=goal_id)

    @staticmethod
    def update_progress(db: Session, goal_id: str, progress: float) -> Optional[Dict[str, Any]]:
        """Manually update goal progress percentage"""
        return GoalService.update(db, goal_id, {"progress_percentage": progress})

    @staticmethod
    def get_hierarchy(db: Session, goal_id: str) -> Optional[Dict[str, Any]]:
        """Get complete goal hierarchy (ancestors and descendants)"""
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return None

        def get_ancestors(goal_id: str) -> List[Dict[str, Any]]:
            ancestors = []
            current_goal = db.query(Goal).filter(Goal.id == goal_id).first()

            while current_goal and current_goal.parent_goal_id:
                parent = db.query(Goal).filter(Goal.id == current_goal.parent_goal_id).first()
                if parent:
                    ancestors.append(
                        {
                            "id": parent.id,
                            "title": parent.title,
                            "goal_type": parent.goal_type,
                            "status": parent.status,
                            "progress": float(parent.progress_percentage),
                        }
                    )
                    current_goal = parent
                else:
                    break

            return list(reversed(ancestors))

        def get_descendants(goal_id: str, level: int = 0) -> List[Dict[str, Any]]:
            children = []
            subgoals = db.query(Goal).filter(Goal.parent_goal_id == goal_id).all()

            for subgoal in subgoals:
                child_data = {
                    "id": subgoal.id,
                    "title": subgoal.title,
                    "goal_type": subgoal.goal_type,
                    "status": subgoal.status,
                    "progress": float(subgoal.progress_percentage),
                    "level": level,
                    "children": get_descendants(subgoal.id, level + 1),
                }
                children.append(child_data)

            return children

        ancestors = get_ancestors(goal_id)
        descendants = get_descendants(goal_id, 1)

        return {
            "goal": {
                "id": goal.id,
                "title": goal.title,
                "goal_type": goal.goal_type,
                "status": goal.status,
                "progress": float(goal.progress_percentage),
            },
            "ancestors": ancestors,
            "descendants": descendants,
            "depth": len(ancestors),
            "total_descendants": len(descendants),
        }
