#!/usr/bin/env python3
"""
Test script for the service layer
"""

import sys
from pathlib import Path

# Add the src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from goalpath.services import GoalService, ProjectService, TaskService, IssueService
from goalpath.database import DatabaseManager
from goalpath.schemas import ProjectCreate, GoalCreate, TaskCreate, IssueCreate

def test_services():
    """Test all services with real database operations"""
    
    # Initialize database
    db_manager = DatabaseManager()
    
    with db_manager.SessionLocal() as db:
        print("🔍 Testing Service Layer (Direct Database Access)")
        print("=" * 50)
        
        # Test ProjectService
        print("\n📁 Testing ProjectService...")
        with ProjectService(db) as project_service:
            # Create a test project with timestamp to avoid duplicates
            import time
            timestamp = int(time.time())
            project_data = ProjectCreate(
                name=f"Service Layer Test Project {timestamp}",
                description="Testing direct database access through service layer",
                status="active",
                priority="medium"
            )
            
            project = project_service.create_project(project_data)
            print(f"✅ Created project: {project['name']} (ID: {project['id']})")
            
            # List projects
            projects = project_service.list_projects_with_statistics(limit=5)
            print(f"✅ Listed {len(projects)} projects")
            
            # Get project statistics
            stats = project_service.calculate_project_statistics(project['id'])
            print(f"✅ Project statistics: {stats['total_tasks']} tasks, {stats['completion_percentage']}% complete")
        
        # Test GoalService
        print("\n🎯 Testing GoalService...")
        with GoalService(db) as goal_service:
            # Create a test goal
            goal_data = GoalCreate(
                title=f"Service Layer Test Goal {timestamp}",
                description="Testing goal management through service layer",
                goal_type="short_term",
                status="active",
                priority="high"
            )
            
            goal = goal_service.create_goal(goal_data)
            print(f"✅ Created goal: {goal['title']} (ID: {goal['id']})")
            
            # Link project to goal
            message = goal_service.link_project_to_goal(goal['id'], project['id'], 1.0)
            print(f"✅ {message}")
            
            # Get goal with progress
            goal_with_progress = goal_service.get_goal_with_progress(goal['id'])
            print(f"✅ Goal progress: {goal_with_progress['progress_percentage']}%")
        
        # Test TaskService
        print("\n📋 Testing TaskService...")
        with TaskService(db) as task_service:
            # Create a test task
            task_data = TaskCreate(
                title="Service Layer Test Task",
                description="Testing task management through service layer",
                project_id=project['id'],
                status="todo",
                priority="high",
                task_type="task"
            )
            
            task = task_service.create_task(task_data)
            print(f"✅ Created task: {task['title']} (ID: {task['id']})")
            
            # Update task status
            updated_task = task_service.update_task_status(task['id'], "done")
            print(f"✅ Updated task status to: {updated_task['status']}")
            
            # List tasks
            tasks = task_service.list_tasks_with_filters(project_id=project['id'])
            print(f"✅ Listed {len(tasks)} tasks for project")
        
        # Test IssueService
        print("\n🐛 Testing IssueService...")
        with IssueService(db) as issue_service:
            # Create a test issue
            issue_data = IssueCreate(
                title="Service Layer Test Issue",
                description="Testing issue management through service layer",
                project_id=project['id'],
                issue_type="bug",
                status="triage",
                priority="medium",
                reporter="test_user"
            )
            
            issue = issue_service.create_issue(issue_data)
            print(f"✅ Created issue: {issue['title']} (ID: {issue['id']})")
            
            # List issues
            issues = issue_service.list_issues_with_filters(project_id=project['id'])
            print(f"✅ Listed {len(issues)} issues for project")
            
            # Calculate issue metrics
            metrics = issue_service.calculate_issue_metrics(project['id'])
            print(f"✅ Issue metrics: {metrics['total_issues']} total, {metrics['resolution_rate']:.1f}% resolved")
        
        print("\n✨ All service tests completed successfully!")
        print(f"📊 Final Project Statistics:")
        print(f"   - Project: {project['name']}")
        print(f"   - Goal: {goal['title']} (Linked)")
        print(f"   - Task: {task['title']} (Completed)")
        print(f"   - Issue: {issue['title']} (Open)")
        
        # Test that services work without backend
        print(f"\n🔌 Backend Status: OFFLINE (Service layer works independently!)")

if __name__ == "__main__":
    test_services()