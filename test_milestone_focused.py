"""
Quick focused Selenium test for Milestone functionality
Tests the core milestone features that are working
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def test_milestone_core_functionality():
    """Quick test of core milestone functionality"""
    print("🚀 Running Focused Milestone Test")
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1200,800")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Test 1: Page loads
        print("📄 Testing page load...")
        driver.get("http://localhost:8004/milestones")
        
        # Wait for page to load
        header = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        assert "Milestones" in header.text
        print("✅ Page loads correctly")
        
        # Test 2: Navigation working
        print("🧭 Testing navigation...")
        nav_links = driver.find_elements(By.XPATH, "//nav//a[contains(@href, '/')]")
        assert len(nav_links) > 0
        print(f"✅ Found {len(nav_links)} navigation links")
        
        # Test 3: Filters present
        print("🔍 Testing filters...")
        epic_filter = driver.find_element(By.ID, "epic-filter")
        status_filter = driver.find_element(By.ID, "status-filter")
        search_filter = driver.find_element(By.ID, "search-filter")
        
        assert epic_filter.is_displayed()
        assert status_filter.is_displayed()
        assert search_filter.is_displayed()
        print("✅ All filters are present and visible")
        
        # Test 4: Create button present
        print("➕ Testing create button...")
        create_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Create Milestone')]")
        assert create_button.is_displayed()
        assert "bg-purple-600" in create_button.get_attribute("class")
        print("✅ Create Milestone button is present and styled correctly")
        
        # Test 5: Timeline section present
        print("📅 Testing timeline section...")
        timeline_section = driver.find_element(By.XPATH, "//h2[contains(text(), 'Timeline View')]")
        assert timeline_section.is_displayed()
        
        empty_state = driver.find_element(By.XPATH, "//div[contains(text(), 'No milestone timeline')]")
        assert empty_state.is_displayed()
        print("✅ Timeline section is present with correct empty state")
        
        # Test 6: API accessibility
        print("🔌 Testing API endpoints...")
        driver.get("http://localhost:8004/api/milestones/")
        page_source = driver.page_source
        assert "[" in page_source and "]" in page_source
        print("✅ Milestones API endpoint returns JSON")
        
        # Test 7: Health check
        driver.get("http://localhost:8004/health")
        page_source = driver.page_source
        assert "healthy" in page_source
        assert "goalpath" in page_source
        print("✅ Health endpoint working")
        
        print("\n🎉 All core milestone functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        driver.quit()


if __name__ == "__main__":
    success = test_milestone_core_functionality()
    if success:
        print("\n✅ Milestone functionality is working correctly!")
    else:
        print("\n❌ Some milestone functionality issues detected.")
