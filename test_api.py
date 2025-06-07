#!/usr/bin/env python3
"""
Quick API test script to verify database-backed endpoints
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_api():
    print("🧪 Testing GoalPath Database-Backed API")
    print("=" * 50)
    
    # Test 1: List all projects
    print("\n1. Testing GET /api/projects/")
    response = requests.get(f"{BASE_URL}/api/projects/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        projects = response.json()
        print(f"Found {len(projects)} projects")
        if projects:
            print(f"First project: {projects[0]['name']} ({projects[0]['status']})")
            project_id = projects[0]['id']
        else:
            print("No projects found")
            return
    else:
        print(f"Error: {response.text}")
        return
    
    # Test 2: Get specific project
    print(f"\n2. Testing GET /api/projects/{project_id}")
    response = requests.get(f"{BASE_URL}/api/projects/{project_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        project = response.json()
        print(f"Project: {project['name']}")
        print(f"Tasks: {project['total_tasks']} total, {project['completed_tasks']} completed")
        print(f"Completion: {project['completion_percentage']}%")
    else:
        print(f"Error: {response.text}")
    
    # Test 3: Get project statistics
    print(f"\n3. Testing GET /api/projects/{project_id}/statistics")
    response = requests.get(f"{BASE_URL}/api/projects/{project_id}/statistics")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"Project: {stats['project_name']}")
        print(f"Timeline: {stats['timeline']['start_date']} → {stats['timeline']['target_end_date']}")
        print(f"Velocity: {stats['velocity']['tasks_per_week']} tasks/week")
        print(f"Hours: {stats['estimated_hours']} estimated, {stats['actual_hours']} actual")
    else:
        print(f"Error: {response.text}")
    
    # Test 4: Filter projects
    print(f"\n4. Testing GET /api/projects/?status=active")
    response = requests.get(f"{BASE_URL}/api/projects/?status=active")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        projects = response.json()
        print(f"Found {len(projects)} active projects")
        for project in projects:
            print(f"  - {project['name']} ({project['priority']} priority)")
    else:
        print(f"Error: {response.text}")
    
    # Test 5: Create new project
    print(f"\n5. Testing POST /api/projects/")
    new_project = {
        "name": "API Test Project",
        "description": "Created via API test script",
        "status": "active",
        "priority": "low",
        "start_date": "2025-06-04"
    }
    response = requests.post(f"{BASE_URL}/api/projects/", json=new_project)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        created_project = response.json()
        print(f"Created project: {created_project['name']} (ID: {created_project['id']})")
        new_project_id = created_project['id']
    else:
        print(f"Error: {response.text}")
        return
    
    # Test 6: Update project
    print(f"\n6. Testing PUT /api/projects/{new_project_id}")
    update_data = {
        "priority": "medium",
        "description": "Updated description via API test"
    }
    response = requests.put(f"{BASE_URL}/api/projects/{new_project_id}", json=update_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        updated_project = response.json()
        print(f"Updated project priority to: {updated_project['priority']}")
        print(f"Updated description: {updated_project['description']}")
    else:
        print(f"Error: {response.text}")
    
    # Test 7: Delete project
    print(f"\n7. Testing DELETE /api/projects/{new_project_id}")
    response = requests.delete(f"{BASE_URL}/api/projects/{new_project_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Delete result: {result['message']}")
    else:
        print(f"Error: {response.text}")
    
    # Test 8: Verify deletion
    print(f"\n8. Testing GET /api/projects/{new_project_id} (should be 404)")
    response = requests.get(f"{BASE_URL}/api/projects/{new_project_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 404:
        print("✅ Project successfully deleted")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server.")
        print("Make sure the server is running on http://127.0.0.1:8001")
    except Exception as e:
        print(f"❌ Error during testing: {e}")
