#!/usr/bin/env python3
"""
Quick test of GoalPath functionality after fixes
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_navigation_routes():
    """Test that all navigation routes are accessible"""
    routes = [
        "/",
        "/projects", 
        "/epics",
        "/milestones", 
        "/tasks",
        "/goals",
        "/analytics"
    ]
    
    print("🧪 Testing Navigation Routes...")
    for route in routes:
        try:
            response = requests.get(f"{BASE_URL}{route}")
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            print(f"  {route:15} → {status}")
        except Exception as e:
            print(f"  {route:15} → ❌ FAIL (Exception: {str(e)})")
    
    print()

def test_modal_routes():
    """Test modal routes for creating entities"""
    modals = [
        "/modals/create-project",
        "/modals/create-epic",
        "/modals/create-milestone",
        "/modals/create-task", 
        "/modals/create-goal"
    ]
    
    print("🎭 Testing Modal Routes...")
    for modal in modals:
        try:
            response = requests.get(f"{BASE_URL}{modal}")
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            print(f"  {modal:25} → {status}")
        except Exception as e:
            print(f"  {modal:25} → ❌ FAIL (Exception: {str(e)})")
    
    print()

def test_api_endpoints():
    """Test key API endpoints"""
    endpoints = [
        ("/api/projects/", "GET"),
        ("/api/epics/", "GET"),
        ("/api/milestones/", "GET"),
        ("/api/tasks/", "GET"),
        ("/api/goals/", "GET"),
        ("/health", "GET")
    ]
    
    print("🔌 Testing API Endpoints...")
    for endpoint, method in endpoints:
        try:
            response = requests.request(method, f"{BASE_URL}{endpoint}")
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            print(f"  {method} {endpoint:20} → {status}")
        except Exception as e:
            print(f"  {method} {endpoint:20} → ❌ FAIL (Exception: {str(e)})")
    
    print()

def test_htmx_fragments():
    """Test HTMX fragment endpoints"""
    fragments = [
        "/htmx/projects/list",
        "/htmx/epics/list", 
        "/htmx/milestones/list",
        "/htmx/tasks/list",
        "/htmx/goals/list"
    ]
    
    print("🔄 Testing HTMX Fragment Endpoints...")
    headers = {"HX-Request": "true"}  # Simulate HTMX request
    
    for fragment in fragments:
        try:
            response = requests.get(f"{BASE_URL}{fragment}", headers=headers)
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            print(f"  {fragment:25} → {status}")
        except Exception as e:
            print(f"  {fragment:25} → ❌ FAIL (Exception: {str(e)})")
    
    print()

def test_create_project():
    """Test project creation via API"""
    print("📋 Testing Project Creation...")
    
    project_data = {
        "name": "Test Project",
        "description": "A test project for validation",
        "status": "active",
        "priority": "medium"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/projects/", 
                               json=project_data,
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 201:
            project = response.json()
            print(f"  ✅ Project created: {project['name']} (ID: {project['id']})")
            return project['id']
        else:
            print(f"  ❌ Project creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ Project creation exception: {str(e)}")
        return None

def test_create_epic(project_id):
    """Test epic creation via API"""
    print("🚀 Testing Epic Creation...")
    
    if not project_id:
        print("  ⏭️  Skipping epic creation (no project ID)")
        return None
    
    epic_data = {
        "title": "Test Epic",
        "description": "A test epic for validation", 
        "project_id": project_id,
        "status": "planning",
        "priority": "medium"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/epics/",
                               json=epic_data,
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 201:
            epic = response.json()
            print(f"  ✅ Epic created: {epic['title']} (ID: {epic['id']})")
            return epic['id']
        else:
            print(f"  ❌ Epic creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ Epic creation exception: {str(e)}")
        return None

def test_create_milestone(epic_id):
    """Test milestone creation via API"""
    print("🎯 Testing Milestone Creation...")
    
    if not epic_id:
        print("  ⏭️  Skipping milestone creation (no epic ID)")
        return None
    
    milestone_data = {
        "title": "Test Milestone",
        "description": "A test milestone for validation",
        "epic_id": epic_id,
        "status": "planned",
        "progress_percentage": 0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/milestones/",
                               json=milestone_data,
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 201:
            milestone = response.json()
            print(f"  ✅ Milestone created: {milestone['title']} (ID: {milestone['id']})")
            return milestone['id']
        else:
            print(f"  ❌ Milestone creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ Milestone creation exception: {str(e)}")
        return None

def test_create_goal():
    """Test goal creation via API"""
    print("🏆 Testing Goal Creation...")
    
    goal_data = {
        "title": "Test Goal",
        "description": "A test goal for validation",
        "goal_type": "short_term",
        "status": "active"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/goals/",
                               json=goal_data,
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 201:
            goal = response.json()
            print(f"  ✅ Goal created: {goal['title']} (ID: {goal['id']})")
            return goal['id']
        else:
            print(f"  ❌ Goal creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ Goal creation exception: {str(e)}")
        return None

def main():
    """Run all tests"""
    print("🎯 GoalPath Functionality Test Suite")
    print("=" * 50)
    print(f"Testing server at: {BASE_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test basic routes
    test_navigation_routes()
    test_modal_routes() 
    test_api_endpoints()
    test_htmx_fragments()
    
    # Test entity creation
    project_id = test_create_project()
    epic_id = test_create_epic(project_id)
    milestone_id = test_create_milestone(epic_id)
    goal_id = test_create_goal()
    
    print()
    print("📊 Test Summary:")
    print(f"  Project ID: {project_id or 'FAILED'}")
    print(f"  Epic ID: {epic_id or 'FAILED'}")
    print(f"  Milestone ID: {milestone_id or 'FAILED'}")
    print(f"  Goal ID: {goal_id or 'FAILED'}")
    
    print()
    print("🎉 Test suite completed!")
    print(f"🌐 Visit the application at: {BASE_URL}")

if __name__ == "__main__":
    main()
