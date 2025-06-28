"""
Epic and Milestone models for GoalPath
Separate models for higher-level planning entities
"""

from enum import Enum
from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base, generate_uuid


class EpicStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class EpicPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MilestoneStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"


class Epic(Base):
    """Epic model for high-level feature development"""

    __tablename__ = "epics"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), nullable=False, default=EpicStatus.PLANNING)
    priority = Column(String(20), nullable=False, default=EpicPriority.MEDIUM)
    story_points = Column(Integer)
    estimated_hours = Column(Numeric(7, 2))
    actual_hours = Column(Numeric(7, 2))
    start_date = Column(Date)
    target_end_date = Column(Date)
    actual_end_date = Column(Date)
    assigned_to = Column(String(100))
    created_by = Column(String(100), nullable=False, default="system")
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="epics")
    milestones = relationship("Milestone", back_populates="epic", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="epic")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('planning', 'active', 'in_progress', 'completed', 'cancelled', 'on_hold')",
            name="chk_epic_status",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high', 'critical')",
            name="chk_epic_priority",
        ),
        CheckConstraint(
            "target_end_date IS NULL OR start_date IS NULL OR target_end_date >= start_date",
            name="chk_epic_dates",
        ),
        CheckConstraint(
            "actual_end_date IS NULL OR start_date IS NULL OR actual_end_date >= start_date",
            name="chk_epic_actual_end_date",
        ),
        CheckConstraint("story_points IS NULL OR story_points > 0", name="chk_epic_story_points"),
        CheckConstraint(
            "estimated_hours IS NULL OR estimated_hours >= 0", name="chk_epic_estimated_hours"
        ),
        CheckConstraint("actual_hours IS NULL OR actual_hours >= 0", name="chk_epic_actual_hours"),
    )


class Milestone(Base):
    """Milestone model for epic composition and tracking"""

    __tablename__ = "milestones"

    id = Column(String, primary_key=True, default=generate_uuid)
    epic_id = Column(String, ForeignKey("epics.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), nullable=False, default=MilestoneStatus.PLANNED)
    due_date = Column(Date)
    completed_date = Column(DateTime)
    progress_percentage = Column(Numeric(5, 2), nullable=False, default=0.00)
    order_index = Column(Integer, default=0)
    created_by = Column(String(100), nullable=False, default="system")
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    epic = relationship("Epic", back_populates="milestones")
    project = relationship("Project", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('planned', 'active', 'completed', 'cancelled', 'delayed')",
            name="chk_milestone_status",
        ),
        CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="chk_milestone_progress",
        ),
    )


# Export all models
__all__ = [
    "Epic",
    "Milestone", 
    "EpicStatus",
    "EpicPriority",
    "MilestoneStatus",
]
