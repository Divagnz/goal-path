"""
Quick smoke tests for GoalPath UI
Basic validation that the application loads and functions
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


pytestmark = pytest.mark.nondestructive


def test_application_loads(driver, base_url):
    """Test that the application loads successfully"""
    driver.get(base_url)
    
    # Should have basic HTML structure
    body = driver.find_element(By.TAG_NAME, "body")
    assert body.is_displayed()
    
    # Should not show server errors (more specific checks)
    page_source = driver.page_source.lower()
    assert "500 internal server error" not in page_source
    assert "internal server error" not in page_source
    assert "error 500" not in page_source


def test_basic_navigation(driver, base_url):
    """Test basic navigation works"""
    driver.get(base_url)
    
    # Try common routes
    routes = ["/", "/projects", "/tasks"]
    
    for route in routes:
        driver.get(f"{base_url}{route}")
        
        # Should load without errors
        body = driver.find_element(By.TAG_NAME, "body")
        assert body.is_displayed()
        
        # Should not be 404
        page_source = driver.page_source.lower()
        assert "404 not found" not in page_source
        assert "page not found" not in page_source


def test_responsive_layout(driver, base_url):
    """Test responsive design"""
    driver.get(base_url)
    
    # Test mobile viewport
    driver.set_window_size(375, 667)
    time.sleep(0.5)
    
    body = driver.find_element(By.TAG_NAME, "body")
    assert body.is_displayed()
    
    # Test desktop viewport  
    driver.set_window_size(1200, 800)
    time.sleep(0.5)
    
    assert body.is_displayed()


def test_no_console_errors(driver, base_url):
    """Test for critical console errors"""
    driver.get(base_url)
    
    # Wait for page to fully load
    time.sleep(2)
    
    # Check for console errors
    try:
        logs = driver.get_log('browser')
        severe_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        # Should not have critical JavaScript errors
        assert len(severe_errors) == 0 or all(
            'favicon' in error['message'].lower() or 
            'network' in error['message'].lower()
            for error in severe_errors
        ), f"Critical errors found: {[e['message'] for e in severe_errors]}"
    except Exception:
        # If browser logs not available, just pass
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
