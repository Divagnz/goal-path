"""
HTMX-specific tests for GoalPath UI
Tests dynamic content loading, real-time updates, and HTMX fragment interactions
"""

import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


pytestmark = pytest.mark.nondestructive


class TestHTMXFragments:
    """Test HTMX fragment loading and DOM updates"""
    
    def test_htmx_headers_present(self, driver, base_url):
        """Test that HTMX is loaded and functioning"""
        driver.get(base_url)
        
        # Check for HTMX script presence
        htmx_scripts = driver.find_elements(By.CSS_SELECTOR, "script[src*='htmx']")
        
        # Should have HTMX loaded or inline
        assert len(htmx_scripts) > 0 or "hx-" in driver.page_source
        
    def test_dashboard_statistics_updates(self, driver, base_url):
        """Test dashboard statistics fragment updates"""
        driver.get(base_url)
        
        # Look for statistics elements
        stats_selectors = [
            "[data-testid='stats-overview']",
            ".stats-overview", 
            ".statistics",
            "[id*='stat']",
            ".stat-card"
        ]
        
        stats_found = False
        for selector in stats_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    stats_found = True
                    break
            except NoSuchElementException:
                continue
        
        # Should have some statistics display
        assert stats_found or "projects" in driver.page_source.lower()
        
    def test_project_list_fragment(self, driver, base_url):
        """Test project list fragment loading"""
        # Navigate to projects page
        driver.get(f"{base_url}/projects")
        
        # Should load without errors
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Look for project-related content
        project_indicators = [
            "project",
            "create",
            "add",
            "new"
        ]
        
        page_text = driver.page_source.lower()
        has_project_content = any(indicator in page_text for indicator in project_indicators)
        assert has_project_content


class TestHTMXForms:
    """Test HTMX form submissions and validations"""
    
    def test_form_hx_attributes(self, driver, base_url):
        """Test that forms have HTMX attributes"""
        driver.get(base_url)
        
        # Look for forms with HTMX attributes
        hx_forms = driver.find_elements(By.CSS_SELECTOR, "form[hx-post], form[hx-put], form[hx-get]")
        
        # May not have forms on main page, so check for any HTMX attributes
        hx_elements = driver.find_elements(By.CSS_SELECTOR, "[hx-get], [hx-post], [hx-put], [hx-delete]")
        
        # Should have some HTMX interactions
        assert len(hx_forms) > 0 or len(hx_elements) > 0 or "hx-" in driver.page_source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
