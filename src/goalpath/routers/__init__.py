"""
API Routers for GoalPath
"""

from .projects import router as projects_router
from .tasks import router as tasks_router
from .goals import router as goals_router

__all__ = ["projects_router", "tasks_router", "goals_router"]
