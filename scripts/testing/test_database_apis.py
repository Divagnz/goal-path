#!/usr/bin/env python3
"""
Test script for GoalPath Database APIs
Tests the database-backed endpoints to ensure they work correctly
"""

import sys
import json
import requests
import time
from pathlib import Path


def test_database_apis():
    """Test all database-backed API endpoints"""

    base_url = "http://localhost:8003"  # Use different port to avoid conflicts

    print("🧪 Testing GoalPath Database APIs...")
    print("=" * 60)

    try:
        # Test health check
        print("1. Testing health check...")
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code == 200
        print(f"   ✅ Health check: {response.json()}")

        # Test Projects API with Database
        print("\n2. Testing Projects API (Database)...")

        # List projects (should work even if empty)
        response = requests.get(f"{base_url}/api/projects/")
        assert response.status_code == 200
        existing_projects = response.json()
        print(f"   ✅ Listed {len(existing_projects)} existing projects")

        # Create a new project
        test_project = {
            "name": "Database Test Project",
            "description": "Testing database-backed project creation",
            "status": "active",
            "priority": "high",
            "start_date": "2025-06-04",
        }

        response = requests.post(f"{base_url}/api/projects/", json=test_project)
        assert response.status_code == 201
        created_project = response.json()
        project_id = created_project["id"]
        print(f"   ✅ Created project: {created_project['name']} (ID: {project_id})")

        # Get the created project
        response = requests.get(f"{base_url}/api/projects/{project_id}")
        assert response.status_code == 200
        retrieved_project = response.json()
        assert retrieved_project["name"] == test_project["name"]
        print(f"   ✅ Retrieved project: {retrieved_project['name']}")

        # Update the project
        update_data = {
            "description": "Updated description via database API test",
            "priority": "critical",
        }
        response = requests.put(f"{base_url}/api/projects/{project_id}", json=update_data)
        assert response.status_code == 200
        updated_project = response.json()
        assert updated_project["priority"] == "critical"
        print("   ✅ Updated project successfully")

        # Get project statistics
        response = requests.get(f"{base_url}/api/projects/{project_id}/statistics")
        assert response.status_code == 200
        stats = response.json()
        print(f"   ✅ Retrieved project statistics: {stats['total_tasks']} tasks")

        # Test Tasks API with Database
        print("\n3. Testing Tasks API (Database)...")

        # List tasks (should work even if empty)
        response = requests.get(f"{base_url}/api/tasks/")
        assert response.status_code == 200
        existing_tasks = response.json()
        print(f"   ✅ Listed {len(existing_tasks)} existing tasks")

        # Create a new task
        test_task = {
            "project_id": project_id,
            "title": "Database Test Task",
            "description": "Testing database-backed task creation",
            "task_type": "task",
            "status": "todo",
            "priority": "high",
            "estimated_hours": 8.0,
            "start_date": "2025-06-04",
            "due_date": "2025-06-10",
        }

        response = requests.post(f"{base_url}/api/tasks/", json=test_task)
        assert response.status_code == 201
        created_task = response.json()
        task_id = created_task["id"]
        print(f"   ✅ Created task: {created_task['title']} (ID: {task_id})")

        # Get the created task
        response = requests.get(f"{base_url}/api/tasks/{task_id}")
        assert response.status_code == 200
        retrieved_task = response.json()
        assert retrieved_task["title"] == test_task["title"]
        print(f"   ✅ Retrieved task: {retrieved_task['title']}")

        # Update task status
        response = requests.put(f"{base_url}/api/tasks/{task_id}/status?status=in_progress")
        assert response.status_code == 200
        updated_task = response.json()
        assert updated_task["status"] == "in_progress"
        print("   ✅ Updated task status to 'in_progress'")

        # Create a subtask
        subtask_data = {
            "project_id": project_id,
            "parent_task_id": task_id,
            "title": "Database Test Subtask",
            "description": "Testing hierarchical task creation",
            "task_type": "subtask",
            "status": "todo",
            "priority": "medium",
        }

        response = requests.post(f"{base_url}/api/tasks/", json=subtask_data)
        assert response.status_code == 201
        created_subtask = response.json()
        subtask_id = created_subtask["id"]
        print(f"   ✅ Created subtask: {created_subtask['title']} (ID: {subtask_id})")

        # Get subtasks of the main task
        response = requests.get(f"{base_url}/api/tasks/{task_id}/subtasks")
        assert response.status_code == 200
        subtasks = response.json()
        assert len(subtasks) == 1
        print(f"   ✅ Retrieved {len(subtasks)} subtask(s)")

        # Test Goals API with Database
        print("\n4. Testing Goals API (Database)...")

        # List goals (should work even if empty)
        response = requests.get(f"{base_url}/api/goals/")
        assert response.status_code == 200
        existing_goals = response.json()
        print(f"   ✅ Listed {len(existing_goals)} existing goals")

        # Create a new goal
        test_goal = {
            "title": "Database Test Goal",
            "description": "Testing database-backed goal creation",
            "goal_type": "short_term",
            "status": "active",
            "target_date": "2025-08-01",
        }

        response = requests.post(f"{base_url}/api/goals/", json=test_goal)
        assert response.status_code == 201
        created_goal = response.json()
        goal_id = created_goal["id"]
        print(f"   ✅ Created goal: {created_goal['title']} (ID: {goal_id})")

        # Get the created goal
        response = requests.get(f"{base_url}/api/goals/{goal_id}")
        assert response.status_code == 200
        retrieved_goal = response.json()
        assert retrieved_goal["title"] == test_goal["title"]
        print(f"   ✅ Retrieved goal: {retrieved_goal['title']}")

        # Link project to goal
        response = requests.post(
            f"{base_url}/api/goals/{goal_id}/link-project?project_id={project_id}&weight=1.0"
        )
        assert response.status_code == 200
        print("   ✅ Linked project to goal")

        # Get goal progress (should now calculate from linked project)
        response = requests.get(f"{base_url}/api/goals/{goal_id}/progress")
        assert response.status_code == 200
        progress_data = response.json()
        print(f"   ✅ Retrieved goal progress: {progress_data['current_progress']}%")

        # Update goal progress manually
        response = requests.put(f"{base_url}/api/goals/{goal_id}/progress?progress=45.5")
        assert response.status_code == 200
        updated_goal = response.json()
        assert updated_goal["progress_percentage"] == 45.5
        print("   ✅ Updated goal progress manually")

        # Create a subgoal
        subgoal_data = {
            "parent_goal_id": goal_id,
            "title": "Database Test Subgoal",
            "description": "Testing hierarchical goal creation",
            "goal_type": "milestone",
            "status": "active",
            "target_date": "2025-07-15",
        }

        response = requests.post(f"{base_url}/api/goals/", json=subgoal_data)
        assert response.status_code == 201
        created_subgoal = response.json()
        subgoal_id = created_subgoal["id"]
        print(f"   ✅ Created subgoal: {created_subgoal['title']} (ID: {subgoal_id})")

        # Get subgoals of the main goal
        response = requests.get(f"{base_url}/api/goals/{goal_id}/subgoals")
        assert response.status_code == 200
        subgoals = response.json()
        assert len(subgoals) == 1
        print(f"   ✅ Retrieved {len(subgoals)} subgoal(s)")

        # Get goal hierarchy
        response = requests.get(f"{base_url}/api/goals/{goal_id}/hierarchy")
        assert response.status_code == 200
        hierarchy = response.json()
        print(f"   ✅ Retrieved goal hierarchy: {hierarchy['total_descendants']} descendants")

        # Test filtering and search
        print("\n5. Testing Filtering and Search...")

        # Filter projects by status
        response = requests.get(f"{base_url}/api/projects/?status=active")
        assert response.status_code == 200
        active_projects = response.json()
        print(f"   ✅ Filtered projects by status: {len(active_projects)} active projects")

        # Search projects
        response = requests.get(f"{base_url}/api/projects/?search=Database")
        assert response.status_code == 200
        searched_projects = response.json()
        assert len(searched_projects) >= 1  # Should find our test project
        print(f"   ✅ Searched projects: {len(searched_projects)} results")

        # Filter tasks by project
        response = requests.get(f"{base_url}/api/tasks/?project_id={project_id}")
        assert response.status_code == 200
        project_tasks = response.json()
        assert len(project_tasks) >= 2  # Should have main task + subtask
        print(f"   ✅ Filtered tasks by project: {len(project_tasks)} tasks")

        # Filter tasks by status
        response = requests.get(f"{base_url}/api/tasks/?status=in_progress")
        assert response.status_code == 200
        in_progress_tasks = response.json()
        print(f"   ✅ Filtered tasks by status: {len(in_progress_tasks)} in progress")

        # Test error handling
        print("\n6. Testing Error Handling...")

        # Try to get non-existent project
        response = requests.get(f"{base_url}/api/projects/non-existent-id")
        assert response.status_code == 404
        print("   ✅ 404 error for non-existent project")

        # Try to create task with invalid project
        invalid_task = {
            "project_id": "non-existent-project",
            "title": "Invalid Task",
            "task_type": "task",
        }
        response = requests.post(f"{base_url}/api/tasks/", json=invalid_task)
        assert response.status_code == 404
        print("   ✅ 404 error for invalid project reference")

        # Try to create task with invalid parent
        invalid_parent_task = {
            "project_id": project_id,
            "parent_task_id": "non-existent-parent",
            "title": "Invalid Parent Task",
            "task_type": "subtask",
        }
        response = requests.post(f"{base_url}/api/tasks/", json=invalid_parent_task)
        assert response.status_code == 404
        print("   ✅ 404 error for invalid parent task reference")

        print("\n" + "=" * 60)
        print("🎉 All database API tests passed!")
        print("\n📊 Test Summary:")
        print("   ✅ Projects: Create, Read, Update, Statistics")
        print("   ✅ Tasks: Create, Read, Update, Hierarchy, Status updates")
        print("   ✅ Goals: Create, Read, Update, Progress, Hierarchy, Project linking")
        print("   ✅ Filtering and search functionality")
        print("   ✅ Error handling and validation")
        print("   ✅ Hierarchical relationships (tasks, goals)")
        print("   ✅ Progress calculation from linked projects")
        print("\n🚀 Database implementation is working correctly!")

        return True

    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running:")
        print("   cd /mnt/raid_0_drive/mcp_projs/goal-path")
        print("   /home/diva/.local/bin/uv run uvicorn src.goalpath.main:app --reload --port 8003")
        return False

    except AssertionError as e:
        print(f"❌ API test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🎯 GoalPath Database API Testing Suite")
    print("Testing database-backed endpoints\n")

    success = test_database_apis()
    sys.exit(0 if success else 1)
