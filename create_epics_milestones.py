#!/usr/bin/env python3
"""
Create epics and milestones for the GoalPath project
"""
import requests
import json
from datetime import datetime, date

# Server URL
BASE_URL = "http://localhost:8007"

def create_epic(project_id, title, description, priority="medium", status="planning"):
    """Create a new epic"""
    epic_data = {
        "project_id": project_id,
        "title": title,
        "description": description,
        "priority": priority,
        "status": status,
        "estimated_hours": 40.0,
        "created_by": "system"
    }
    
    response = requests.post(f"{BASE_URL}/api/epics/", json=epic_data)
    if response.status_code == 201:
        epic = response.json()
        print(f"✅ Created epic: {epic['title']} (ID: {epic['id']})")
        return epic
    else:
        print(f"❌ Failed to create epic: {response.status_code} - {response.text}")
        return None

def create_milestone(epic_id, project_id, title, description, due_date=None):
    """Create a new milestone"""
    milestone_data = {
        "epic_id": epic_id,
        "project_id": project_id,
        "title": title,
        "description": description,
        "status": "planned",
        "created_by": "system"
    }
    
    if due_date:
        milestone_data["due_date"] = due_date
    
    response = requests.post(f"{BASE_URL}/api/milestones/", json=milestone_data)
    if response.status_code == 201:
        milestone = response.json()
        print(f"✅ Created milestone: {milestone['title']} (ID: {milestone['id']})")
        return milestone
    else:
        print(f"❌ Failed to create milestone: {response.status_code} - {response.text}")
        return None

def get_projects():
    """Get all projects"""
    response = requests.get(f"{BASE_URL}/api/projects/")
    if response.status_code == 200:
        projects = response.json()
        print(f"📋 Found {len(projects)} projects")
        return projects
    else:
        print(f"❌ Failed to get projects: {response.status_code}")
        return []

def main():
    print("🏗️ Creating Epics and Milestones for GoalPath...")
    
    # Get existing projects
    projects = get_projects()
    if not projects:
        print("❌ No projects found!")
        return
    
    # Use the first project for our epics
    project = projects[0]
    project_id = project["id"]
    print(f"🎯 Using project: {project['name']} (ID: {project_id})")
    
    # Create Epic 1: User Authentication System
    print("\n📦 Creating Epic 1: User Authentication System")
    auth_epic = create_epic(
        project_id=project_id,
        title="User Authentication System",
        description="Implement comprehensive user authentication with login, registration, password reset, and role-based access control",
        priority="high",
        status="active"
    )
    
    if auth_epic:
        # Create milestones for auth epic
        auth_milestones = [
            {
                "title": "User Registration",
                "description": "Implement user registration with email verification",
                "due_date": "2025-07-15"
            },
            {
                "title": "Login System", 
                "description": "Implement secure login with session management",
                "due_date": "2025-07-20"
            },
            {
                "title": "Password Reset",
                "description": "Implement password reset functionality via email",
                "due_date": "2025-07-25"
            },
            {
                "title": "Role Management",
                "description": "Implement role-based access control system",
                "due_date": "2025-07-30"
            }
        ]
        
        auth_milestone_ids = []
        for milestone_data in auth_milestones:
            milestone = create_milestone(
                epic_id=auth_epic["id"],
                project_id=project_id,
                title=milestone_data["title"],
                description=milestone_data["description"],
                due_date=milestone_data["due_date"]
            )
            if milestone:
                auth_milestone_ids.append(milestone["id"])
    
    # Create Epic 2: Dashboard & Analytics
    print("\n📊 Creating Epic 2: Dashboard & Analytics")
    dashboard_epic = create_epic(
        project_id=project_id,
        title="Dashboard & Analytics",
        description="Build comprehensive dashboard with real-time analytics, reporting, and data visualization features",
        priority="medium",
        status="planning"
    )
    
    if dashboard_epic:
        # Create milestones for dashboard epic
        dashboard_milestones = [
            {
                "title": "Real-time Dashboard",
                "description": "Implement live dashboard with key metrics and widgets",
                "due_date": "2025-08-05"
            },
            {
                "title": "Data Visualization",
                "description": "Add charts, graphs, and visual analytics components",
                "due_date": "2025-08-10"
            },
            {
                "title": "Reporting System",
                "description": "Implement PDF/Excel export and scheduled reports",
                "due_date": "2025-08-15"
            },
            {
                "title": "Performance Metrics",
                "description": "Add performance tracking and optimization metrics",
                "due_date": "2025-08-20"
            }
        ]
        
        dashboard_milestone_ids = []
        for milestone_data in dashboard_milestones:
            milestone = create_milestone(
                epic_id=dashboard_epic["id"],
                project_id=project_id,
                title=milestone_data["title"],
                description=milestone_data["description"],
                due_date=milestone_data["due_date"]
            )
            if milestone:
                dashboard_milestone_ids.append(milestone["id"])
    
    # Create Epic 3: Mobile Application
    print("\n📱 Creating Epic 3: Mobile Application")
    mobile_epic = create_epic(
        project_id=project_id,
        title="Mobile Application",
        description="Develop cross-platform mobile application with offline support and push notifications",
        priority="medium",
        status="planning"
    )
    
    if mobile_epic:
        # Create milestones for mobile epic
        mobile_milestones = [
            {
                "title": "Mobile UI Framework",
                "description": "Setup React Native/Flutter framework and basic UI components",
                "due_date": "2025-09-01"
            },
            {
                "title": "API Integration",
                "description": "Integrate mobile app with backend API endpoints",
                "due_date": "2025-09-10"
            },
            {
                "title": "Offline Support",
                "description": "Implement offline data synchronization and caching",
                "due_date": "2025-09-20"
            },
            {
                "title": "Push Notifications",
                "description": "Add push notification system for alerts and updates",
                "due_date": "2025-09-30"
            }
        ]
        
        mobile_milestone_ids = []
        for milestone_data in mobile_milestones:
            milestone = create_milestone(
                epic_id=mobile_epic["id"],
                project_id=project_id,
                title=milestone_data["title"],
                description=milestone_data["description"],
                due_date=milestone_data["due_date"]
            )
            if milestone:
                mobile_milestone_ids.append(milestone["id"])
    
    print("\n🎉 Epic and Milestone creation completed!")
    print("📈 Summary:")
    print(f"   • Created 3 epics with comprehensive feature sets")
    print(f"   • Created 12 milestones with specific deliverables")
    print(f"   • All linked to project: {project['name']}")

if __name__ == "__main__":
    main()
