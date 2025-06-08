"""
SQLAlchemy models for GoalPath project management system
Based on the approved database schema
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Integer,
    Date,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Numeric,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid

Base = declarative_base()


# Enums for type safety
class ProjectStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskType(str, Enum):
    EPIC = "epic"
    STORY = "story"
    TASK = "task"
    SUBTASK = "subtask"
    MILESTONE = "milestone"
    BUG = "bug"


class TaskStatus(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOWEST = "lowest"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    HIGHEST = "highest"
    CRITICAL = "critical"


def generate_uuid():
    """Generate UUID for primary keys"""
    return str(uuid.uuid4())


class Project(Base):
    """Project model representing main project entities"""

    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    status = Column(String(20), nullable=False, default=ProjectStatus.ACTIVE)
    priority = Column(String(20), nullable=False, default=Priority.MEDIUM)
    start_date = Column(Date)
    target_end_date = Column(Date)
    actual_end_date = Column(Date)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    created_by = Column(String(100), nullable=False, default="system")

    # Relationships
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    sprints = relationship("Sprint", back_populates="project", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="project", cascade="all, delete-orphan")
    context = relationship("ProjectContext", back_populates="project", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="project")
    goal_links = relationship("GoalProject", back_populates="project")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'paused', 'completed', 'archived')", name="chk_project_status"
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'critical')", name="chk_project_priority"
        ),
        CheckConstraint(
            "target_end_date IS NULL OR start_date IS NULL OR target_end_date >= start_date",
            name="chk_project_dates",
        ),
        CheckConstraint(
            "actual_end_date IS NULL OR start_date IS NULL OR actual_end_date >= start_date",
            name="chk_actual_end_date",
        ),
    )


class Task(Base):
    """Task model with hierarchical support"""

    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    parent_task_id = Column(String, ForeignKey("tasks.id", ondelete="SET NULL"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    task_type = Column(String(20), nullable=False, default=TaskType.TASK)
    status = Column(String(20), nullable=False, default=TaskStatus.BACKLOG)
    priority = Column(String(20), nullable=False, default=TaskPriority.MEDIUM)
    story_points = Column(Integer)
    estimated_hours = Column(Numeric(7, 2))
    actual_hours = Column(Numeric(7, 2))
    start_date = Column(Date)
    due_date = Column(Date)
    completed_date = Column(DateTime)
    assigned_to = Column(String(100))
    created_by = Column(String(100), nullable=False, default="system")
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="tasks")
    parent_task = relationship("Task", remote_side=[id], back_populates="subtasks")
    subtasks = relationship("Task", back_populates="parent_task", cascade="all, delete-orphan")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship(
        "TaskAttachment", back_populates="task", cascade="all, delete-orphan"
    )
    reminders = relationship("Reminder", back_populates="task")
    dependencies_as_task = relationship(
        "TaskDependency", foreign_keys="TaskDependency.task_id", back_populates="task"
    )
    dependencies_as_dependency = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.depends_on_task_id",
        back_populates="depends_on_task",
    )
    sprint_links = relationship("SprintTask", back_populates="task")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "task_type IN ('epic', 'story', 'task', 'subtask', 'milestone', 'bug')",
            name="chk_task_type",
        ),
        CheckConstraint(
            "status IN ('backlog', 'todo', 'in_progress', 'in_review', 'done', 'blocked', 'cancelled')",
            name="chk_task_status",
        ),
        CheckConstraint(
            "priority IN ('lowest', 'low', 'medium', 'high', 'highest', 'critical')",
            name="chk_task_priority",
        ),
        CheckConstraint(
            "due_date IS NULL OR start_date IS NULL OR due_date >= start_date",
            name="chk_task_dates",
        ),
        CheckConstraint("story_points IS NULL OR story_points > 0", name="chk_story_points"),
        CheckConstraint(
            "estimated_hours IS NULL OR estimated_hours >= 0", name="chk_estimated_hours"
        ),
        CheckConstraint("actual_hours IS NULL OR actual_hours >= 0", name="chk_actual_hours"),
    )


class TaskDependency(Base):
    """Task dependency relationships"""

    __tablename__ = "task_dependencies"

    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    depends_on_task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    dependency_type = Column(String(20), nullable=False, default="blocks")
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    task = relationship("Task", foreign_keys=[task_id], back_populates="dependencies_as_task")
    depends_on_task = relationship(
        "Task", foreign_keys=[depends_on_task_id], back_populates="dependencies_as_dependency"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "dependency_type IN ('blocks', 'subtask_of', 'related_to')", name="chk_dependency_type"
        ),
        CheckConstraint("task_id != depends_on_task_id", name="chk_no_self_dependency"),
        UniqueConstraint("task_id", "depends_on_task_id", name="uq_task_dependency"),
    )


class Goal(Base):
    """Goal model with hierarchical support"""

    __tablename__ = "goals"

    id = Column(String, primary_key=True, default=generate_uuid)
    parent_goal_id = Column(String, ForeignKey("goals.id", ondelete="SET NULL"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    goal_type = Column(String(20), nullable=False, default="short_term")
    target_date = Column(Date)
    status = Column(String(20), nullable=False, default="active")
    progress_percentage = Column(Numeric(5, 2), nullable=False, default=0.00)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    parent_goal = relationship("Goal", remote_side=[id], back_populates="subgoals")
    subgoals = relationship("Goal", back_populates="parent_goal", cascade="all, delete-orphan")
    project_links = relationship("GoalProject", back_populates="goal")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "goal_type IN ('long_term', 'medium_term', 'short_term', 'milestone')",
            name="chk_goal_type",
        ),
        CheckConstraint(
            "status IN ('active', 'paused', 'completed', 'cancelled')", name="chk_goal_status"
        ),
        CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="chk_progress_percentage",
        ),
    )


class GoalProject(Base):
    """Many-to-many relationship between goals and projects"""

    __tablename__ = "goal_projects"

    goal_id = Column(String, ForeignKey("goals.id", ondelete="CASCADE"), primary_key=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    weight = Column(Numeric(3, 2), nullable=False, default=1.00)

    # Relationships
    goal = relationship("Goal", back_populates="project_links")
    project = relationship("Project", back_populates="goal_links")

    # Constraints
    __table_args__ = (CheckConstraint("weight > 0 AND weight <= 1", name="chk_weight_range"),)


class Sprint(Base):
    """Sprint model for agile development"""

    __tablename__ = "sprints"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    goal = Column(Text)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="planning")
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="sprints")
    task_links = relationship("SprintTask", back_populates="sprint")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('planning', 'active', 'completed', 'cancelled')", name="chk_sprint_status"
        ),
        CheckConstraint("end_date > start_date", name="chk_sprint_dates"),
    )


class SprintTask(Base):
    """Many-to-many relationship between sprints and tasks"""

    __tablename__ = "sprint_tasks"

    sprint_id = Column(String, ForeignKey("sprints.id", ondelete="CASCADE"), primary_key=True)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
    added_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    sprint = relationship("Sprint", back_populates="task_links")
    task = relationship("Task", back_populates="sprint_links")
