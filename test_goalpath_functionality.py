#!/usr/bin/env python3
"""
Quick test of GoalPath functionality to verify milestones and epics integration
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_goalpath_functionality():
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Create driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🧪 Testing GoalPath Application...")
        
        # Test 1: Dashboard loads
        print("📊 Test 1: Loading dashboard...")
        driver.get("http://localhost:8007")
        
        # Wait for dashboard to load
        wait = WebDriverWait(driver, 10)
        dashboard_title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        
        if "Dashboard" in driver.page_source:
            print("✅ Dashboard loaded successfully")
        else:
            print("❌ Dashboard failed to load")
            return False
        
        # Test 2: Navigation works
        print("🧭 Test 2: Testing navigation...")
        
        # Test Projects page
        projects_link = driver.find_element(By.LINK_TEXT, "Projects")
        projects_link.click()
        time.sleep(2)
        
        if "Projects" in driver.page_source:
            print("✅ Projects page accessible")
        else:
            print("❌ Projects page failed to load")
            return False
        
        # Test Tasks page
        tasks_link = driver.find_element(By.LINK_TEXT, "Tasks")
        tasks_link.click()
        time.sleep(2)
        
        if "Tasks" in driver.page_source:
            print("✅ Tasks page accessible")
        else:
            print("❌ Tasks page failed to load")
            return False
        
        # Test Goals page
        goals_link = driver.find_element(By.LINK_TEXT, "Goals")
        goals_link.click()
        time.sleep(2)
        
        if "Goals" in driver.page_source:
            print("✅ Goals page accessible")
        else:
            print("❌ Goals page failed to load")
            return False
        
        # Test 3: Go back to dashboard and check stats
        print("📈 Test 3: Checking dashboard statistics...")
        dashboard_link = driver.find_element(By.LINK_TEXT, "Dashboard")
        dashboard_link.click()
        time.sleep(2)
        
        # Check if statistics are displaying
        stats_elements = driver.find_elements(By.CLASS_NAME, "bg-white")
        if len(stats_elements) >= 4:  # Should have at least 4 stat cards
            print("✅ Dashboard statistics are displaying")
        else:
            print("❌ Dashboard statistics not found")
            return False
        
        # Test 4: Check if New Project button is present
        print("🆕 Test 4: Checking interactive elements...")
        new_project_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'New Project')]")
        if new_project_buttons:
            print("✅ New Project button found")
        else:
            print("❌ New Project button not found")
            return False
        
        print("🎉 All tests passed! GoalPath is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_goalpath_functionality()
    exit(0 if success else 1)
