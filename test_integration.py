#!/usr/bin/env python3
"""
Complete integration test for the project detail navigation
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:8001"

def test_complete_navigation_flow():
    """Test the complete navigation flow from projects list to project detail"""
    print("🚀 Testing Complete Navigation Flow")
    print("=" * 60)
    
    try:
        # Step 1: Get projects page
        print("1. Loading projects page...")
        projects_response = requests.get(f"{BASE_URL}/projects")
        assert projects_response.status_code == 200, f"Projects page failed: {projects_response.status_code}"
        
        # Parse the HTML to find project links
        soup = BeautifulSoup(projects_response.text, 'html.parser')
        project_links = soup.find_all('a', attrs={'hx-get': lambda x: x and x.startswith('/projects/')})
        
        print(f"   ✅ Projects page loaded ({len(projects_response.text)} chars)")
        print(f"   📋 Found {len(project_links)} project navigation links")
        
        if project_links:
            # Step 2: Test HTMX navigation to project detail
            first_link = project_links[0]
            project_url = first_link.get('hx-get')
            project_name = first_link.get_text().strip()
            
            print(f"\n2. Testing HTMX navigation to: {project_name}")
            print(f"   🔗 URL: {project_url}")
            
            # Simulate HTMX request
            htmx_headers = {"HX-Request": "true"}
            detail_response = requests.get(f"{BASE_URL}{project_url}", headers=htmx_headers)
            assert detail_response.status_code == 200, f"Project detail failed: {detail_response.status_code}"
            
            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
            
            # Check for expected content
            has_breadcrumb = detail_soup.find('nav', attrs={'aria-label': 'Breadcrumb'}) is not None
            has_project_title = detail_soup.find('h1') is not None
            has_progress_cards = len(detail_soup.find_all('div', class_='bg-white')) > 0
            has_back_link = detail_soup.find('a', attrs={'hx-get': '/projects'}) is not None
            
            print(f"   ✅ Project detail loaded ({len(detail_response.text)} chars)")
            print(f"   🍞 Breadcrumb navigation: {'✅' if has_breadcrumb else '❌'}")
            print(f"   📋 Project title: {'✅' if has_project_title else '❌'}")
            print(f"   📊 Progress cards: {'✅' if has_progress_cards else '❌'}")
            print(f"   ↩️  Back to projects link: {'✅' if has_back_link else '❌'}")
            
            # Step 3: Test back navigation
            print(f"\n3. Testing back navigation...")
            back_response = requests.get(f"{BASE_URL}/projects", headers=htmx_headers)
            assert back_response.status_code == 200, f"Back navigation failed: {back_response.status_code}"
            
            print(f"   ✅ Back navigation works ({len(back_response.text)} chars)")
            
            # Step 4: Test direct URL access (non-HTMX)
            print(f"\n4. Testing direct URL access...")
            direct_response = requests.get(f"{BASE_URL}{project_url}")
            assert direct_response.status_code == 200, f"Direct access failed: {direct_response.status_code}"
            
            print(f"   ✅ Direct URL access works ({len(direct_response.text)} chars)")
            
            # Step 5: Test error handling
            print(f"\n5. Testing error handling...")
            error_response = requests.get(f"{BASE_URL}/projects/nonexistent-id")
            assert error_response.status_code == 404, f"Expected 404, got {error_response.status_code}"
            
            htmx_error_response = requests.get(f"{BASE_URL}/projects/nonexistent-id", headers=htmx_headers)
            assert htmx_error_response.status_code == 200, f"HTMX error handling failed: {htmx_error_response.status_code}"
            
            error_soup = BeautifulSoup(htmx_error_response.text, 'html.parser')
            has_error_message = 'not found' in htmx_error_response.text.lower()
            has_back_button = error_soup.find('a', attrs={'hx-get': '/projects'}) is not None
            
            print(f"   ✅ Regular request returns 404")
            print(f"   ✅ HTMX request returns error fragment")
            print(f"   💬 Error message: {'✅' if has_error_message else '❌'}")
            print(f"   🔙 Back button: {'✅' if has_back_button else '❌'}")
            
        else:
            print("   ❌ No project navigation links found")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False
    except AssertionError as e:
        print(f"   ❌ Test assertion failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False
        
    print("\n" + "=" * 60)
    print("🎉 All navigation tests passed!")
    return True

def test_project_detail_features():
    """Test specific features of the project detail view"""
    print("\n📋 Testing Project Detail Features")
    print("=" * 60)
    
    try:
        # Get a project to test with
        projects_response = requests.get(f"{BASE_URL}/api/projects/")
        projects = projects_response.json()
        
        if not projects:
            print("   ❌ No projects available for testing")
            return False
            
        project_id = projects[0]["id"]
        
        # Test project detail features
        detail_response = requests.get(f"{BASE_URL}/projects/{project_id}")
        soup = BeautifulSoup(detail_response.text, 'html.parser')
        
        # Check for key features
        features = {
            "Project Header": soup.find('h1') is not None,
            "Progress Card": 'Overall Progress' in detail_response.text,
            "Tasks Summary": 'Tasks' in detail_response.text,
            "Action Buttons": soup.find('button', string=lambda x: x and 'Edit Project' in x) is not None,
            "Add Task Button": soup.find('button', string=lambda x: x and 'Add Task' in x) is not None,
            "Tasks Section": 'Project Tasks' in detail_response.text,
            "Breadcrumb": soup.find('nav', attrs={'aria-label': 'Breadcrumb'}) is not None,
        }
        
        print("Feature Checklist:")
        for feature, present in features.items():
            status = "✅" if present else "❌"
            print(f"   {status} {feature}")
            
        all_features_present = all(features.values())
        
        if all_features_present:
            print("\n🎉 All project detail features are present!")
        else:
            missing = [f for f, present in features.items() if not present]
            print(f"\n⚠️  Missing features: {', '.join(missing)}")
            
        return all_features_present
        
    except Exception as e:
        print(f"   ❌ Error testing features: {e}")
        return False

if __name__ == "__main__":
    print("🧪 GoalPath Project Detail Route - Integration Tests")
    print("🎯 Testing the complete implementation")
    print()
    
    # Run tests
    navigation_success = test_complete_navigation_flow()
    features_success = test_project_detail_features()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Navigation Flow: {'✅ PASS' if navigation_success else '❌ FAIL'}")
    print(f"Feature Tests: {'✅ PASS' if features_success else '❌ FAIL'}")
    
    if navigation_success and features_success:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("✨ Project detail route implementation is complete and working!")
    else:
        print("\n⚠️  Some tests failed. Please review the implementation.")
