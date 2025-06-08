"""
Additional SQLAlchemy models for GoalPath - Part 2
Reminders, Issues, Comments, Context, and other supporting entities
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Integer,
    BigInteger,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Numeric,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base, generate_uuid


class Reminder(Base):
    """Reminder and scheduling system"""

    __tablename__ = "reminders"

    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    message = Column(Text)
    reminder_type = Column(String(20), nullable=False, default="one_time")
    trigger_datetime = Column(DateTime, nullable=False)
    view_after = Column(DateTime)
    recurrence_pattern = Column(Text)  # JSON string for SQLite compatibility
    status = Column(String(20), nullable=False, default="pending")
    acknowledged_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    task = relationship("Task", back_populates="reminders")
    project = relationship("Project", back_populates="reminders")

    # Constraints
    __table_args__ = (
        CheckConstraint("reminder_type IN ('one_time', 'recurring')", name="chk_reminder_type"),
        CheckConstraint(
            "status IN ('pending', 'acknowledged', 'snoozed', 'cancelled')",
            name="chk_reminder_status",
        ),
        CheckConstraint(
            "(task_id IS NOT NULL AND project_id IS NULL) OR (task_id IS NULL AND project_id IS NOT NULL)",
            name="chk_reminder_relation",
        ),
    )


class Issue(Base):
    """Issue tracking and backlog management"""

    __tablename__ = "issues"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    issue_type = Column(String(20), nullable=False, default="feature")
    priority = Column(String(20), nullable=False, default="medium")
    status = Column(String(20), nullable=False, default="triage")
    reporter = Column(String(100), nullable=False)
    assignee = Column(String(100))
    promoted_to_task_id = Column(String, ForeignKey("tasks.id", ondelete="SET NULL"))
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="issues")
    promoted_task = relationship("Task", foreign_keys=[promoted_to_task_id])

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "issue_type IN ('bug', 'feature', 'enhancement', 'question')", name="chk_issue_type"
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'critical')", name="chk_issue_priority"
        ),
        CheckConstraint(
            "status IN ('triage', 'backlog', 'in_progress', 'resolved', 'closed')",
            name="chk_issue_status",
        ),
    )


class TaskComment(Base):
    """Task comments and activity tracking"""

    __tablename__ = "task_comments"

    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    author = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    comment_type = Column(String(20), nullable=False, default="comment")
    comment_metadata = Column(Text)  # JSON string for SQLite compatibility
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    task = relationship("Task", back_populates="comments")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "comment_type IN ('comment', 'status_change', 'assignment', 'attachment')",
            name="chk_comment_type",
        ),
    )


class TaskAttachment(Base):
    """Task file attachments"""

    __tablename__ = "task_attachments"

    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    uploaded_by = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    task = relationship("Task", back_populates="attachments")

    # Constraints
    __table_args__ = (CheckConstraint("file_size > 0", name="chk_file_size"),)


class ProjectContext(Base):
    """Flexible project metadata and context storage"""

    __tablename__ = "project_context"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    context_type = Column(String(20), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)  # JSON string for SQLite compatibility
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="context")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "context_type IN ('notes', 'links', 'files', 'settings', 'metadata')",
            name="chk_context_type",
        ),
        UniqueConstraint("project_id", "context_type", "key", name="uq_project_context"),
    )


class ScheduleEvent(Base):
    """Calendar events and deadlines"""

    __tablename__ = "schedule_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"))
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"))
    event_type = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime)
    location = Column(String(255))
    created_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    project = relationship("Project")
    task = relationship("Task")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('deadline', 'meeting', 'milestone', 'reminder')", name="chk_event_type"
        ),
        CheckConstraint(
            "end_datetime IS NULL OR end_datetime > start_datetime", name="chk_event_dates"
        ),
    )


# Export all models
__all__ = [
    "Base",
    "Project",
    "Task",
    "TaskDependency",
    "Goal",
    "GoalProject",
    "Sprint",
    "SprintTask",
    "Reminder",
    "Issue",
    "TaskComment",
    "TaskAttachment",
    "ProjectContext",
    "ScheduleEvent",
]
