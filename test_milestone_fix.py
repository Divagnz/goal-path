#!/usr/bin/env python3
"""
Test script to verify milestone creation fix
Tests both the issue and the solution
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8007"

def test_milestone_creation():
    """Test milestone creation with epic lookup"""
    
    print("🎯 Testing Milestone Creation Fix\n")
    
    # Step 1: Get existing epics
    print("1. Fetching existing epics...")
    response = requests.get(f"{BASE_URL}/api/epics/")
    if response.status_code != 200:
        print(f"❌ Failed to fetch epics: {response.status_code}")
        return False
        
    epics = response.json()
    if not epics:
        print("❌ No epics found. Please create epics first.")
        return False
    
    epic = epics[0]  # Use first epic
    epic_id = epic["id"]
    project_id = epic["project_id"]
    
    print(f"✓ Found epic: {epic['title']}")
    print(f"  Epic ID: {epic_id}")
    print(f"  Project ID: {project_id}")
    
    # Step 2: Test milestone creation (should now work)
    print("\n2. Creating milestone...")
    milestone_data = {
        "epic_id": epic_id,
        # Note: No project_id - should be derived automatically
        "title": "Test Milestone - Auto Project ID",
        "description": "Testing automatic project_id derivation from epic",
        "status": "planned"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/milestones/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(milestone_data)
    )
    
    if response.status_code == 201:
        milestone = response.json()
        print("✓ Milestone created successfully!")
        print(f"  Milestone ID: {milestone['id']}")
        print(f"  Title: {milestone['title']}")
        print(f"  Epic ID: {milestone['epic_id']}")
        print(f"  Project ID: {milestone['project_id']}")
        
        # Verify project_id matches epic's project_id
        if milestone['project_id'] == project_id:
            print("✅ Project ID correctly derived from epic!")
            return True
        else:
            print(f"❌ Project ID mismatch! Expected: {project_id}, Got: {milestone['project_id']}")
            return False
    else:
        print(f"❌ Failed to create milestone: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_milestone_validation():
    """Test milestone creation with invalid epic_id"""
    
    print("\n3. Testing validation with invalid epic_id...")
    milestone_data = {
        "epic_id": "non-existent-epic-id",
        "title": "Should Fail",
        "description": "This should fail validation",
        "status": "planned"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/milestones/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(milestone_data)
    )
    
    if response.status_code == 404:
        print("✓ Correctly rejected invalid epic_id with 404")
        return True
    elif response.status_code == 400:
        print("✓ Correctly rejected invalid epic_id with 400")
        return True
    else:
        print(f"❌ Unexpected response for invalid epic: {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    success = True
    
    try:
        success &= test_milestone_creation()
        success &= test_milestone_validation()
        
        if success:
            print("\n🎉 All tests passed! Milestone creation fix is working.")
        else:
            print("\n💥 Some tests failed. Fix needs more work.")
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        success = False
    
    exit(0 if success else 1)
