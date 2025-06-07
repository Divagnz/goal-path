#!/usr/bin/env python3
"""
Test SQLAlchemy models and database setup
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from goalpath.database import DatabaseManager, init_database
from goalpath.models import Project, Task, Goal

def test_sqlalchemy_setup():
    """Test SQLAlchemy models and database operations"""
    
    print("🧪 Testing SQLAlchemy setup...")
    
    try:
        # Initialize database
        db_manager = DatabaseManager("sqlite:///test_sqlalchemy.db")
        
        # Create tables
        print("Creating database tables...")
        db_manager.create_tables()
        
        # Test basic operations
        with db_manager.get_sync_session() as session:
            
            # Create a project
            project = Project(
                name="Test SQLAlchemy Project",
                description="Testing SQLAlchemy models",
                status="active",
                priority="medium"
            )
            session.add(project)
            session.commit()
            session.refresh(project)
            
            print(f"✅ Created project: {project.name} (ID: {project.id})")
            
            # Create a task
            task = Task(
                project_id=project.id,
                title="Test Task",
                description="Testing task creation",
                task_type="task",
                status="todo",
                priority="medium"
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            
            print(f"✅ Created task: {task.title} (ID: {task.id})")
            
            # Create a goal
            goal = Goal(
                title="Test Goal",
                description="Testing goal creation",
                goal_type="short_term",
                status="active"
            )
            session.add(goal)
            session.commit()
            session.refresh(goal)
            
            print(f"✅ Created goal: {goal.title} (ID: {goal.id})")
            
            # Test relationships
            project_tasks = session.query(Task).filter(Task.project_id == project.id).all()
            print(f"✅ Project has {len(project_tasks)} tasks")
            
            # Test querying
            all_projects = session.query(Project).all()
            print(f"✅ Database contains {len(all_projects)} projects")
            
        print("✅ All SQLAlchemy tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test database
        import os
        if os.path.exists("test_sqlalchemy.db"):
            os.remove("test_sqlalchemy.db")
            print("🧹 Cleaned up test database")

if __name__ == "__main__":
    success = test_sqlalchemy_setup()
    sys.exit(0 if success else 1)
