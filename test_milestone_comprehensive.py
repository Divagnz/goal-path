#!/usr/bin/env python3
"""
Comprehensive test for milestone creation with various scenarios
"""

import requests
import json

BASE_URL = "http://localhost:8007"

def test_milestone_creation_comprehensive():
    """Test milestone creation with comprehensive scenarios"""
    
    print("🎯 Comprehensive Milestone Creation Test\n")
    
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
    
    # Test 2: Create milestone without project_id (auto-derive)
    print("\n2. Creating milestone without project_id (auto-derive)...")
    milestone_data = {
        "epic_id": epic_id,
        "title": "Auto-derived Project ID",
        "description": "Testing automatic project_id derivation",
        "status": "planned"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/milestones/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(milestone_data)
    )
    
    if response.status_code == 201:
        milestone = response.json()
        print("✅ Milestone created successfully with auto-derived project_id!")
        print(f"  Project ID: {milestone['project_id']} (should match epic's project_id)")
        assert milestone['project_id'] == project_id, "Project ID should match epic's project"
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    # Test 3: Create milestone with correct project_id (validation)
    print("\n3. Creating milestone with correct project_id...")
    milestone_data = {
        "epic_id": epic_id,
        "project_id": project_id,  # Explicitly provide correct project_id
        "title": "Validated Project ID",
        "description": "Testing project_id validation",
        "status": "planned"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/milestones/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(milestone_data)
    )
    
    if response.status_code == 201:
        milestone = response.json()
        print("✅ Milestone created successfully with validated project_id!")
        assert milestone['project_id'] == project_id, "Project ID should match"
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    # Test 4: Try to create milestone with wrong project_id (should fail)
    print("\n4. Creating milestone with incorrect project_id (should fail)...")
    milestone_data = {
        "epic_id": epic_id,
        "project_id": "wrong-project-id",  # Wrong project_id
        "title": "Should Fail",
        "description": "This should fail validation",
        "status": "planned"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/milestones/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(milestone_data)
    )
    
    if response.status_code == 400:
        print("✅ Correctly rejected wrong project_id!")
        error_detail = response.json().get("detail", "")
        print(f"  Error: {error_detail}")
    else:
        print(f"❌ Should have failed with 400, got: {response.status_code}")
        return False
    
    # Test 5: Try with non-existent epic_id
    print("\n5. Creating milestone with non-existent epic_id (should fail)...")
    milestone_data = {
        "epic_id": "non-existent-epic",
        "title": "Should Fail",
        "description": "Epic doesn't exist",
        "status": "planned"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/milestones/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(milestone_data)
    )
    
    if response.status_code == 404:
        print("✅ Correctly rejected non-existent epic_id!")
        error_detail = response.json().get("detail", "")
        print(f"  Error: {error_detail}")
    else:
        print(f"❌ Should have failed with 404, got: {response.status_code}")
        return False
    
    print("\n🎉 All comprehensive tests passed!")
    return True

def test_milestone_listing():
    """Test milestone listing and filtering"""
    print("\n6. Testing milestone listing...")
    
    # Get all milestones
    response = requests.get(f"{BASE_URL}/api/milestones/")
    if response.status_code == 200:
        milestones = response.json()
        print(f"✅ Found {len(milestones)} milestones")
        
        if milestones:
            milestone = milestones[0]
            print(f"  Sample milestone: {milestone['title']}")
            print(f"  Epic ID: {milestone['epic_id']}")
            print(f"  Project ID: {milestone['project_id']}")
        
        return True
    else:
        print(f"❌ Failed to list milestones: {response.status_code}")
        return False

if __name__ == "__main__":
    success = True
    
    try:
        success &= test_milestone_creation_comprehensive()
        success &= test_milestone_listing()
        
        if success:
            print("\n🎉 All comprehensive tests passed! Milestone API is working perfectly.")
        else:
            print("\n💥 Some tests failed.")
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        success = False
    
    exit(0 if success else 1)
