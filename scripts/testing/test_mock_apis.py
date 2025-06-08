#!/usr/bin/env python3
"""
Test script for GoalPath Mock APIs
Tests the fixed response endpoints before implementing database logic
"""

import sys
from pathlib import Path

import requests

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_api_endpoints():
    """Test all API endpoints with mock data"""

    base_url = "http://localhost:8000"

    # Test data for creating resources
    test_project = {
        "name": "Test API Project",
        "description": "Testing the API endpoints",
        "status": "active",
        "priority": "medium",
    }

    test_task = {
        "project_id": "proj-001",  # Use existing mock project
        "title": "Test API Task",
        "description": "Testing task creation",
        "task_type": "task",
        "status": "todo",
        "priority": "medium",
    }

    test_goal = {
        "title": "Test API Goal",
        "description": "Testing goal creation",
        "goal_type": "short_term",
        "status": "active",
    }

    print("🧪 Testing GoalPath Mock APIs...")
    print("=" * 50)

    try:
        # Test health check
        print("1. Testing health check...")
        response = requests.get(f"{base_url}/health")
        assert response.status_code == 200
        print(f"   ✅ Health check: {response.json()}")

        # Test dashboard
        print("2. Testing dashboard...")
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        print("   ✅ Dashboard loaded successfully")

        # Test API documentation
        print("3. Testing API docs...")
        response = requests.get(f"{base_url}/api/docs")
        assert response.status_code == 200
        print("   ✅ API documentation accessible")

        # Test Projects API
        print("4. Testing Projects API...")

        # List projects
        response = requests.get(f"{base_url}/api/projects/")
        assert response.status_code == 200
        projects = response.json()
        print(f"   ✅ Listed {len(projects)} projects")

        # Get specific project
        if projects:
            project_id = projects[0]["id"]
            response = requests.get(f"{base_url}/api/projects/{project_id}")
            assert response.status_code == 200
            print(f"   ✅ Retrieved project: {response.json()['name']}")

            # Get project statistics
            response = requests.get(f"{base_url}/api/projects/{project_id}/statistics")
            assert response.status_code == 200
            print("   ✅ Retrieved project statistics")

        # Create project
        response = requests.post(f"{base_url}/api/projects/", json=test_project)
        assert response.status_code == 201
        created_project = response.json()
        print(f"   ✅ Created project: {created_project['name']}")

        # Update project
        update_data = {"description": "Updated description via API test"}
        response = requests.put(
            f"{base_url}/api/projects/{created_project['id']}", json=update_data
        )
        assert response.status_code == 200
        print("   ✅ Updated project successfully")

        # Test Tasks API
        print("5. Testing Tasks API...")

        # List tasks
        response = requests.get(f"{base_url}/api/tasks/")
        assert response.status_code == 200
        tasks = response.json()
        print(f"   ✅ Listed {len(tasks)} tasks")

        # Filter tasks by project
        response = requests.get(f"{base_url}/api/tasks/?project_id=proj-001")
        assert response.status_code == 200
        filtered_tasks = response.json()
        print(f"   ✅ Filtered tasks by project: {len(filtered_tasks)} tasks")

        # Get specific task
        if tasks:
            task_id = tasks[0]["id"]
            response = requests.get(f"{base_url}/api/tasks/{task_id}")
            assert response.status_code == 200
            print(f"   ✅ Retrieved task: {response.json()['title']}")

            # Get task hierarchy
            response = requests.get(f"{base_url}/api/tasks/{task_id}/hierarchy")
            assert response.status_code == 200
            print("   ✅ Retrieved task hierarchy")

            # Update task status
            response = requests.put(f"{base_url}/api/tasks/{task_id}/status?status=in_progress")
            assert response.status_code == 200
            print("   ✅ Updated task status")

        # Create task
        response = requests.post(f"{base_url}/api/tasks/", json=test_task)
        assert response.status_code == 201
        created_task = response.json()
        print(f"   ✅ Created task: {created_task['title']}")

        # Test Goals API
        print("6. Testing Goals API...")

        # List goals
        response = requests.get(f"{base_url}/api/goals/")
        assert response.status_code == 200
        goals = response.json()
        print(f"   ✅ Listed {len(goals)} goals")

        # Get specific goal
        if goals:
            goal_id = goals[0]["id"]
            response = requests.get(f"{base_url}/api/goals/{goal_id}")
            assert response.status_code == 200
            print(f"   ✅ Retrieved goal: {response.json()['title']}")

            # Get goal progress
            response = requests.get(f"{base_url}/api/goals/{goal_id}/progress")
            assert response.status_code == 200
            print("   ✅ Retrieved goal progress details")

            # Update goal progress
            response = requests.put(f"{base_url}/api/goals/{goal_id}/progress?progress=75.5")
            assert response.status_code == 200
            print("   ✅ Updated goal progress")

        # Create goal
        response = requests.post(f"{base_url}/api/goals/", json=test_goal)
        assert response.status_code == 201
        created_goal = response.json()
        print(f"   ✅ Created goal: {created_goal['title']}")

        # Test filtering and search
        print("7. Testing filtering and search...")

        # Filter projects by status
        response = requests.get(f"{base_url}/api/projects/?status=active")
        assert response.status_code == 200
        print("   ✅ Filtered projects by status")

        # Search tasks
        response = requests.get(f"{base_url}/api/tasks/?search=design")
        assert response.status_code == 200
        print("   ✅ Searched tasks")

        # Filter goals by type
        response = requests.get(f"{base_url}/api/goals/?goal_type=short_term")
        assert response.status_code == 200
        print("   ✅ Filtered goals by type")

        print("\n" + "=" * 50)
        print("🎉 All API tests passed! Mock endpoints are working correctly.")
        print("\n📊 Test Summary:")
        print("   ✅ Health check and dashboard")
        print("   ✅ API documentation accessibility")
        print("   ✅ Projects CRUD operations")
        print("   ✅ Tasks CRUD operations and hierarchy")
        print("   ✅ Goals CRUD operations and progress")
        print("   ✅ Filtering and search functionality")
        print("\n🚀 Ready to implement real database logic!")

        return True

    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running:")
        print("   python -m src.goalpath.main")
        print("   or: uvicorn src.goalpath.main:app --reload")
        return False

    except AssertionError as e:
        print(f"❌ API test failed: {e}")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def start_server_and_test():
    """Start the FastAPI server and run tests"""

    print("🚀 Starting FastAPI server...")

    # Try to start the server
    try:
        import threading
        import time

        import uvicorn

        # Start server in a separate thread
        def run_server():
            uvicorn.run(
                "src.goalpath.main:app",
                host="127.0.0.1",
                port=8000,
                log_level="warning",  # Reduce log noise during testing
            )

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # Wait for server to start
        time.sleep(3)

        # Run tests
        success = test_api_endpoints()

        return success

    except ImportError:
        print("❌ uvicorn not installed. Please install dependencies:")
        print("   pip install -e .")
        return False
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False


if __name__ == "__main__":
    print("🎯 GoalPath API Testing Suite")
    print("Testing mock endpoints before database implementation\n")

    # Check if server is already running
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ Server already running, proceeding with tests...")
            success = test_api_endpoints()
        else:
            print("⚠️  Server responding but unhealthy, starting new instance...")
            success = start_server_and_test()
    except requests.exceptions.ConnectionError:
        print("🚀 Starting server and running tests...")
        success = start_server_and_test()

    sys.exit(0 if success else 1)
