#!/usr/bin/env python3
"""
Test script for the new project detail route
"""


import requests

# Test the new project detail route
BASE_URL = "http://localhost:8001"


def test_project_detail_route():
    """Test the project detail route functionality"""
    print("🧪 Testing Project Detail Route Implementation")
    print("=" * 50)

    # First, get the list of projects to find a valid project ID
    print("1. Getting projects list...")
    try:
        response = requests.get(f"{BASE_URL}/api/projects/")
        if response.status_code == 200:
            projects = response.json()
            print(f"   ✅ Found {len(projects)} projects")

            if projects:
                project_id = projects[0]["id"]
                project_name = projects[0]["name"]
                print(f"   📋 Testing with project: {project_name} (ID: {project_id})")

                # Test the project detail route
                print("\n2. Testing project detail route...")

                # Test regular HTTP request (should return HTML)
                detail_response = requests.get(f"{BASE_URL}/projects/{project_id}")
                print(f"   Regular request status: {detail_response.status_code}")

                if detail_response.status_code == 200:
                    content = detail_response.text
                    if "project.name" in content or project_name in content:
                        print("   ✅ Project detail route returns HTML content")
                        print(f"   📄 Content length: {len(content)} characters")
                    else:
                        print("   ⚠️  HTML content might not contain project data")
                else:
                    print(f"   ❌ Failed to get project detail: {detail_response.status_code}")

                # Test HTMX request (should return fragment)
                print("\n3. Testing HTMX fragment request...")
                htmx_headers = {"HX-Request": "true"}
                htmx_response = requests.get(
                    f"{BASE_URL}/projects/{project_id}", headers=htmx_headers
                )
                print(f"   HTMX request status: {htmx_response.status_code}")

                if htmx_response.status_code == 200:
                    htmx_content = htmx_response.text
                    if "project.name" in htmx_content or project_name in htmx_content:
                        print("   ✅ HTMX request returns fragment content")
                        print(f"   📄 Fragment length: {len(htmx_content)} characters")
                    else:
                        print("   ⚠️  Fragment might not contain project data")
                else:
                    print(f"   ❌ Failed to get HTMX fragment: {htmx_response.status_code}")

                # Test error handling with invalid project ID
                print("\n4. Testing error handling...")
                error_response = requests.get(f"{BASE_URL}/projects/invalid-id")
                print(f"   Invalid ID request status: {error_response.status_code}")

                if error_response.status_code == 404:
                    print("   ✅ Correctly returns 404 for invalid project ID")
                else:
                    print(
                        f"   ⚠️  Unexpected status code for invalid ID: {error_response.status_code}"
                    )

                # Test HTMX error handling
                htmx_error_response = requests.get(
                    f"{BASE_URL}/projects/invalid-id", headers=htmx_headers
                )
                print(f"   HTMX invalid ID status: {htmx_error_response.status_code}")

                if htmx_error_response.status_code == 200:
                    error_content = htmx_error_response.text
                    if "not found" in error_content.lower() or "error" in error_content.lower():
                        print("   ✅ HTMX error handling returns error fragment")
                    else:
                        print("   ⚠️  HTMX error response might not contain error message")

            else:
                print("   ❌ No projects found to test with")

        else:
            print(f"   ❌ Failed to get projects: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")

    print("\n" + "=" * 50)
    print("🏁 Test completed!")


def test_projects_page_navigation():
    """Test that the projects page has links to project details"""
    print("\n🔗 Testing Projects Page Navigation Links")
    print("=" * 50)

    try:
        # Test projects page
        response = requests.get(f"{BASE_URL}/projects")
        if response.status_code == 200:
            content = response.text

            # Check for HTMX attributes in project links
            if 'hx-get="/projects/' in content:
                print("   ✅ Projects page contains HTMX navigation links")
            else:
                print("   ⚠️  Projects page might not have HTMX links")

            # Check for proper HTMX targeting
            if 'hx-target="#main-content"' in content:
                print("   ✅ HTMX links target main-content correctly")
            else:
                print("   ⚠️  HTMX links might not target correctly")

            # Check for URL pushing
            if 'hx-push-url="true"' in content:
                print("   ✅ HTMX links include URL pushing")
            else:
                print("   ⚠️  HTMX links might not push URLs")

        else:
            print(f"   ❌ Failed to get projects page: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")


if __name__ == "__main__":
    test_project_detail_route()
    test_projects_page_navigation()
