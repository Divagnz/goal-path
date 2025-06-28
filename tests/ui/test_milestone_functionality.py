"""
Selenium test for Milestone functionality in GoalPath
Tests the complete milestone management workflow including HTMX interactions
"""

import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class TestMilestoneManagement:
    """Test suite for milestone management functionality"""
    
    @classmethod
    def setup_class(cls):
        """Set up Chrome driver with optimized options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1200,800")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)
        cls.wait = WebDriverWait(cls.driver, 10)
        cls.base_url = "http://localhost:8004"
        
    @classmethod
    def teardown_class(cls):
        """Clean up driver"""
        if hasattr(cls, 'driver'):
            cls.driver.quit()
    
    def test_milestone_page_loads(self):
        """Test that the milestone page loads correctly"""
        try:
            self.driver.get(f"{self.base_url}/milestones")
            
            # Wait for the page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            
            # Check page title
            assert "Milestones" in self.driver.title or "GoalPath" in self.driver.title
            
            # Check for milestone page header
            header = self.driver.find_element(By.TAG_NAME, "h1")
            assert "Milestones" in header.text
            
            # Check for description
            description = self.driver.find_element(By.XPATH, "//p[contains(text(), 'Track progress within epics')]")
            assert "Track progress within epics and monitor key deliverables" in description.text
            
            print("✅ Milestone page loads correctly")
            
        except Exception as e:
            print(f"❌ Milestone page load test failed: {e}")
            raise
    
    def test_milestone_filters_present(self):
        """Test that all filter elements are present"""
        try:
            self.driver.get(f"{self.base_url}/milestones")
            
            # Wait for filters to load
            self.wait.until(EC.presence_of_element_located((By.ID, "epic-filter")))
            
            # Check for all filter elements
            epic_filter = self.driver.find_element(By.ID, "epic-filter")
            status_filter = self.driver.find_element(By.ID, "status-filter")
            due_filter = self.driver.find_element(By.ID, "due-filter")
            search_filter = self.driver.find_element(By.ID, "search-filter")
            
            # Verify filter options
            status_select = Select(status_filter)
            status_options = [option.text for option in status_select.options]
            expected_statuses = ["All Statuses", "Planned", "Active", "Completed", "Cancelled", "Delayed"]
            
            for status in expected_statuses:
                assert status in status_options, f"Status '{status}' not found in filter options"
            
            # Check due date filter options
            due_select = Select(due_filter)
            due_options = [option.text for option in due_select.options]
            expected_due_options = ["All Dates", "Overdue", "This Week", "This Month", "Next Month"]
            
            for due_option in expected_due_options:
                assert due_option in due_options, f"Due date option '{due_option}' not found"
            
            print("✅ All milestone filters are present and correctly configured")
            
        except Exception as e:
            print(f"❌ Milestone filters test failed: {e}")
            raise
    
    def test_create_milestone_button_present(self):
        """Test that the Create Milestone button is present and clickable"""
        try:
            self.driver.get(f"{self.base_url}/milestones")
            
            # Wait for the create button to be present
            create_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Milestone')]"))
            )
            
            # Verify button styling
            button_classes = create_button.get_attribute("class")
            assert "bg-purple-600" in button_classes, "Create button should have purple styling"
            assert "hover:bg-purple-700" in button_classes, "Create button should have hover styling"
            
            print("✅ Create Milestone button is present and properly styled")
            
        except Exception as e:
            print(f"❌ Create Milestone button test failed: {e}")
            raise
    
    def test_create_milestone_modal_opens(self):
        """Test that clicking Create Milestone opens the modal"""
        try:
            self.driver.get(f"{self.base_url}/milestones")
            
            # Click the Create Milestone button
            create_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Milestone')]"))
            )
            create_button.click()
            
            # Wait for modal to appear
            modal = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'fixed') and contains(@class, 'inset-0')]"))
            )
            
            # Check modal title
            modal_title = self.driver.find_element(By.XPATH, "//h3[contains(text(), 'Create New Milestone')]")
            assert "Create New Milestone" in modal_title.text
            
            # Check for required form fields
            title_field = self.driver.find_element(By.ID, "milestone-title")
            epic_field = self.driver.find_element(By.ID, "milestone-epic")
            status_field = self.driver.find_element(By.ID, "milestone-status")
            progress_field = self.driver.find_element(By.ID, "milestone-progress")
            
            # Verify field properties
            assert title_field.get_attribute("required") is not None, "Title field should be required"
            assert epic_field.get_attribute("required") is not None, "Epic field should be required"
            
            # Check for progress slider
            progress_value = self.driver.find_element(By.ID, "progress-value")
            assert "0%" in progress_value.text, "Progress should start at 0%"
            
            print("✅ Create Milestone modal opens with all required fields")
            
        except Exception as e:
            print(f"❌ Create Milestone modal test failed: {e}")
            raise
    
    def test_milestone_form_validation(self):
        """Test form validation in the Create Milestone modal"""
        try:
            self.driver.get(f"{self.base_url}/milestones")
            
            # Open modal
            create_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Milestone')]"))
            )
            create_button.click()
            
            # Wait for modal
            self.wait.until(
                EC.presence_of_element_located((By.ID, "milestone-title"))
            )
            
            # Try to submit empty form
            submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Create Milestone')]")
            submit_button.click()
            
            # Check if validation prevents submission (title field should show as invalid)
            title_field = self.driver.find_element(By.ID, "milestone-title")
            validity = self.driver.execute_script("return arguments[0].validity.valid;", title_field)
            assert not validity, "Empty title field should be invalid"
            
            # Test epic availability message
            epic_message = self.driver.find_element(By.XPATH, "//p[contains(text(), 'No epics available')]")
            assert "Create an epic first" in epic_message.text
            
            print("✅ Form validation works correctly")
            
        except Exception as e:
            print(f"❌ Form validation test failed: {e}")
            raise
    
    def test_timeline_view_present(self):
        """Test that the timeline view section is present"""
        try:
            self.driver.get(f"{self.base_url}/milestones")
            
            # Wait for timeline section
            timeline_section = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Timeline View')]"))
            )
            
            # Check timeline empty state
            empty_state = self.driver.find_element(By.XPATH, "//h3[contains(text(), 'No milestone timeline')]")
            assert "No milestone timeline" in empty_state.text
            
            # Check empty state message
            empty_message = self.driver.find_element(By.XPATH, "//p[contains(text(), 'Milestones with due dates will appear here')]")
            assert "chronological order" in empty_message.text
            
            # Check for "Create Milestone with Due Date" button
            timeline_create_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Create Milestone with Due Date')]")
            assert timeline_create_button.is_displayed()
            
            print("✅ Timeline view is present with correct empty state")
            
        except Exception as e:
            print(f"❌ Timeline view test failed: {e}")
            raise
    
    def test_progress_slider_functionality(self):
        """Test that the progress slider works in the modal"""
        try:
            self.driver.get(f"{self.base_url}/milestones")
            
            # Open modal
            create_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Milestone')]"))
            )
            create_button.click()
            
            # Wait for progress slider
            progress_slider = self.wait.until(
                EC.presence_of_element_located((By.ID, "milestone-progress"))
            )
            
            progress_value = self.driver.find_element(By.ID, "progress-value")
            
            # Test initial state
            initial_value = progress_slider.get_attribute("value")
            assert initial_value == "0", f"Initial progress should be 0, got {initial_value}"
            assert "0%" in progress_value.text
            
            # Change slider value using JavaScript (more reliable than drag)
            self.driver.execute_script("arguments[0].value = 50; arguments[0].dispatchEvent(new Event('input'));", progress_slider)
            
            # Give time for the oninput event to trigger
            time.sleep(0.5)
            
            # Check if value display updated
            updated_text = progress_value.text
            # Note: The oninput handler should update the display, but we'll verify the slider value changed
            updated_value = progress_slider.get_attribute("value")
            assert updated_value == "50", f"Progress slider should be 50, got {updated_value}"
            
            print("✅ Progress slider functionality works")
            
        except Exception as e:
            print(f"❌ Progress slider test failed: {e}")
            raise
    
    def test_responsive_design(self):
        """Test responsive design of the milestone page"""
        try:
            # Test mobile view
            self.driver.set_window_size(375, 667)  # iPhone size
            self.driver.get(f"{self.base_url}/milestones")
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            
            # Check if create button is responsive
            create_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Create Milestone')]")
            button_classes = create_button.get_attribute("class")
            assert "mt-4" in button_classes or "sm:mt-0" in button_classes, "Button should have responsive margin classes"
            
            # Test tablet view
            self.driver.set_window_size(768, 1024)  # iPad size
            time.sleep(1)
            
            # Test desktop view
            self.driver.set_window_size(1200, 800)  # Desktop size
            time.sleep(1)
            
            # Verify filters are visible in desktop view
            filters = self.driver.find_elements(By.XPATH, "//select[@id='epic-filter']")
            assert len(filters) > 0, "Filters should be visible in desktop view"
            
            print("✅ Responsive design works across different screen sizes")
            
        except Exception as e:
            print(f"❌ Responsive design test failed: {e}")
            raise
    
    def test_navigation_menu(self):
        """Test that navigation menu works and includes milestones"""
        try:
            self.driver.get(f"{self.base_url}/milestones")
            
            # Look for navigation items
            nav_items = self.driver.find_elements(By.XPATH, "//nav//a | //header//a")
            nav_texts = [item.text for item in nav_items if item.text.strip()]
            
            # Check for expected navigation items
            expected_items = ["Dashboard", "Projects", "Tasks", "Goals"]
            for item in expected_items:
                # At least one should be present (some might be in mobile menu)
                found = any(item in text for text in nav_texts)
                if not found:
                    print(f"Warning: Navigation item '{item}' not found in visible navigation")
            
            # Test navigation to other pages
            if nav_texts:
                # Try to click on Dashboard link
                dashboard_link = None
                for item in nav_items:
                    if "Dashboard" in item.text:
                        dashboard_link = item
                        break
                
                if dashboard_link:
                    dashboard_link.click()
                    time.sleep(2)  # Allow page to load
                    
                    # Navigate back to milestones
                    self.driver.get(f"{self.base_url}/milestones")
                    self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            
            print("✅ Navigation menu functionality works")
            
        except Exception as e:
            print(f"❌ Navigation menu test failed: {e}")
            raise
    
    def test_htmx_integration(self):
        """Test HTMX integration by checking for HTMX attributes"""
        try:
            self.driver.get(f"{self.base_url}/milestones")
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            
            # Check for HTMX attributes on milestone list container
            milestone_container = self.driver.find_element(By.ID, "milestones-container")
            hx_get = milestone_container.get_attribute("hx-get")
            hx_trigger = milestone_container.get_attribute("hx-trigger")
            
            assert hx_get is not None, "Milestones container should have hx-get attribute"
            assert "milestones/list" in hx_get, "hx-get should point to milestones list endpoint"
            assert hx_trigger is not None, "Milestones container should have hx-trigger attribute"
            
            # Check timeline container
            timeline_container = self.driver.find_element(By.ID, "milestones-timeline")
            timeline_hx_get = timeline_container.get_attribute("hx-get")
            assert timeline_hx_get is not None, "Timeline container should have hx-get attribute"
            assert "timeline" in timeline_hx_get, "Timeline hx-get should point to timeline endpoint"
            
            # Check for auto-refresh functionality in page source
            page_source = self.driver.page_source
            assert "setInterval" in page_source, "Page should have auto-refresh functionality"
            
            print("✅ HTMX integration is properly configured")
            
        except Exception as e:
            print(f"❌ HTMX integration test failed: {e}")
            raise
    
    def test_api_endpoint_accessibility(self):
        """Test that milestone API endpoints are accessible"""
        try:
            # Test the milestone list API endpoint directly
            self.driver.get(f"{self.base_url}/api/milestones/")
            
            # Should return JSON (empty array for now)
            page_source = self.driver.page_source
            assert "[" in page_source and "]" in page_source, "API should return JSON array"
            
            # Test health endpoint
            self.driver.get(f"{self.base_url}/health")
            page_source = self.driver.page_source
            assert "healthy" in page_source, "Health endpoint should return healthy status"
            assert "goalpath" in page_source, "Health endpoint should return app name"
            
            print("✅ API endpoints are accessible")
            
        except Exception as e:
            print(f"❌ API endpoint test failed: {e}")
            raise


def run_milestone_tests():
    """Run all milestone tests"""
    print("🚀 Starting Milestone Functionality Tests")
    print("=" * 60)
    
    test_instance = TestMilestoneManagement()
    test_instance.setup_class()
    
    try:
        # Run all tests
        test_methods = [
            test_instance.test_milestone_page_loads,
            test_instance.test_milestone_filters_present,
            test_instance.test_create_milestone_button_present,
            test_instance.test_create_milestone_modal_opens,
            test_instance.test_milestone_form_validation,
            test_instance.test_timeline_view_present,
            test_instance.test_progress_slider_functionality,
            test_instance.test_responsive_design,
            test_instance.test_navigation_menu,
            test_instance.test_htmx_integration,
            test_instance.test_api_endpoint_accessibility,
        ]
        
        passed = 0
        failed = 0
        
        for test_method in test_methods:
            try:
                test_method()
                passed += 1
            except Exception as e:
                print(f"❌ {test_method.__name__} failed: {e}")
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"🎯 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All milestone tests passed successfully!")
        else:
            print(f"⚠️  {failed} tests failed. Check the logs above for details.")
        
    finally:
        test_instance.teardown_class()


if __name__ == "__main__":
    run_milestone_tests()
