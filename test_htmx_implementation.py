#!/usr/bin/env python3
"""
Test HTMX endpoints functionality
"""

import requests
import json

BASE_URL = "http://localhost:8004"

def test_htmx_project_creation():
    """Test creating a project via HTMX endpoint"""
    
    # Test data
    project_data = {
        "name": "Test HTMX Project",
        "description": "A test project created via HTMX",
        "priority": "medium",
        "status": "active"
    }
    
    # HTMX headers
    htmx_headers = {
        "HX-Request": "true",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    print("🧪 Testing HTMX project creation...")
    print(f"📝 Project data: {project_data}")
    
    # Make request to HTMX endpoint
    response = requests.post(
        f"{BASE_URL}/htmx/projects/create",
        data=project_data,
        headers=htmx_headers
    )
    
    print(f"📊 Response status: {response.status_code}")
    print(f"📋 Response headers: {dict(response.headers)}")
    print(f"📄 Response content preview: {response.text[:500]}...")
    
    if response.status_code == 200:
        print("✅ HTMX project creation successful!")
        # Check if response contains HTML (not JSON)
        if "<!DOCTYPE html>" in response.text or "<div" in response.text:
            print("✅ Response is HTML (as expected for HTMX)")
        else:
            print("❌ Response is not HTML")
    else:
        print(f"❌ HTMX project creation failed with status {response.status_code}")
        print(f"Error details: {response.text}")

def test_regular_api_still_works():
    """Test that regular API endpoints still work"""
    
    print("\n🧪 Testing regular API still works...")
    
    response = requests.get(f"{BASE_URL}/api/projects/")
    
    print(f"📊 API Response status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"✅ API returns JSON with {len(data)} projects")
        except json.JSONDecodeError:
            print("❌ API response is not valid JSON")
    else:
        print(f"❌ API request failed with status {response.status_code}")

def test_htmx_without_headers():
    """Test HTMX endpoint without proper headers (should fail)"""
    
    print("\n🧪 Testing HTMX endpoint without HTMX headers (should fail)...")
    
    project_data = {
        "name": "Test Project Without Headers",
        "description": "This should fail",
        "priority": "medium",
        "status": "active"
    }
    
    # Regular headers (no HX-Request)
    regular_headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(
        f"{BASE_URL}/htmx/projects/create",
        data=project_data,
        headers=regular_headers
    )
    
    print(f"📊 Response status: {response.status_code}")
    
    if response.status_code == 400:
        print("✅ HTMX endpoint correctly rejects non-HTMX requests")
    else:
        print(f"❌ HTMX endpoint should have rejected request, got {response.status_code}")

if __name__ == "__main__":
    print("🚀 Testing GoalPath HTMX Implementation\n")
    
    try:
        test_htmx_project_creation()
        test_regular_api_still_works()
        test_htmx_without_headers()
        
        print("\n🎉 HTMX testing completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on port 8004.")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
