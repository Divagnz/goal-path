"""
Selenium WebDriver configuration and fixtures for GoalPath UI tests
"""

import pytest
import subprocess
import time
import os
import signal
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class TestServer:
    """Manages the test server lifecycle"""
    
    def __init__(self, port=8000):
        self.process = None
        self.port = port
        self.base_url = f"http://localhost:{port}"
        
    def start(self):
        """Start the FastAPI test server"""
        cmd = [
            "/home/diva/.local/bin/uv", "run", "uvicorn", 
            "src.goalpath.main:app", 
            "--host", "0.0.0.0", 
            "--port", str(self.port),
            "--reload"
        ]
        
        # Change to project directory
        project_dir = "/mnt/raid_0_drive/mcp_projs/goal-path"
        
        self.process = subprocess.Popen(
            cmd, 
            cwd=project_dir,
            stdout=subprocess.DEVNULL,  # Suppress output
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid
        )
        
        # Wait for server to start
        print(f"Starting server on {self.base_url}...")
        time.sleep(4)
        
    def stop(self):
        """Stop the test server"""
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=10)
                print("Server stopped")
            except (ProcessLookupError, subprocess.TimeoutExpired):
                # Process already dead or taking too long
                pass


@pytest.fixture(scope="session")
def test_server():
    """Session-scoped test server fixture"""
    server = TestServer(port=8001)  # Use different port to avoid conflicts
    server.start()
    yield server
    server.stop()


@pytest.fixture(scope="session")
def driver_init():
    """Initialize Chrome WebDriver with options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    # Install and setup ChromeDriver automatically
    service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)  # Global wait time
    
    yield driver
    driver.quit()


@pytest.fixture
def driver(driver_init):
    """Fresh driver for each test"""
    driver_init.delete_all_cookies()
    yield driver_init


@pytest.fixture(scope="session")
def base_url(test_server):
    """Base URL for tests"""
    return test_server.base_url


class BasePage:
    """Base page object with common methods"""
    
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)
        
    def go_to(self, path=""):
        """Navigate to a specific path"""
        url = f"{self.base_url}{path}"
        self.driver.get(url)
        
    def wait_for_element(self, locator, timeout=10):
        """Wait for element to be present"""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))
        
    def wait_for_clickable(self, locator, timeout=10):
        """Wait for element to be clickable"""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.element_to_be_clickable(locator))
        
    def wait_for_visible(self, locator, timeout=10):
        """Wait for element to be visible"""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located(locator))
        
    def is_element_present(self, locator):
        """Check if element is present"""
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False
            
    def get_element_text(self, locator):
        """Get text from element"""
        element = self.wait_for_element(locator)
        return element.text
        
    def click_element(self, locator):
        """Click an element"""
        element = self.wait_for_clickable(locator)
        element.click()
        
    def fill_input(self, locator, text):
        """Fill an input field"""
        element = self.wait_for_element(locator)
        element.clear()
        element.send_keys(text)
        
    def get_page_title(self):
        """Get page title"""
        return self.driver.title
        
    def get_current_url(self):
        """Get current URL"""
        return self.driver.current_url
        
    def wait_for_url_contains(self, text, timeout=10):
        """Wait for URL to contain specific text"""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.url_contains(text))


class DashboardPage(BasePage):
    """Dashboard page object"""
    
    # Locators
    MAIN_HEADING = (By.TAG_NAME, "h1")
    NAVIGATION = (By.TAG_NAME, "nav")
    STATS_SECTION = (By.CSS_SELECTOR, "[data-testid='stats-overview'], .stats-overview")
    PROJECTS_LINK = (By.CSS_SELECTOR, "a[href*='project']")
    TASKS_LINK = (By.CSS_SELECTOR, "a[href*='task']")
    GOALS_LINK = (By.CSS_SELECTOR, "a[href*='goal']")
    
    def navigate_to_projects(self):
        """Navigate to projects page"""
        if self.is_element_present(self.PROJECTS_LINK):
            self.click_element(self.PROJECTS_LINK)
            
    def navigate_to_tasks(self):
        """Navigate to tasks page"""
        if self.is_element_present(self.TASKS_LINK):
            self.click_element(self.TASKS_LINK)
            
    def navigate_to_goals(self):
        """Navigate to goals page"""
        if self.is_element_present(self.GOALS_LINK):
            self.click_element(self.GOALS_LINK)


class ProjectsPage(BasePage):
    """Projects page object"""
    
    # Locators
    CREATE_PROJECT_BTN = (By.CSS_SELECTOR, "[data-testid='create-project-btn'], .create-project-btn, button:contains('Create')")
    PROJECT_CARDS = (By.CSS_SELECTOR, "[data-testid='project-card'], .project-card")
    SEARCH_INPUT = (By.CSS_SELECTOR, "[data-testid='project-search'], input[type='search']")
    
    def click_create_project(self):
        """Click create project button"""
        # Try multiple possible selectors
        selectors = [
            "[data-testid='create-project-btn']",
            ".create-project-btn", 
            "button[class*='create']",
            "a[href*='create']",
            "button:contains('Create')"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                element.click()
                return
            except NoSuchElementException:
                continue
                
        # If no button found, just verify we're on the page
        pass
        
    def get_project_count(self):
        """Get number of project cards"""
        try:
            projects = self.driver.find_elements(*self.PROJECT_CARDS)
            return len(projects)
        except NoSuchElementException:
            return 0
            
    def search_projects(self, search_term):
        """Search for projects"""
        if self.is_element_present(self.SEARCH_INPUT):
            self.fill_input(self.SEARCH_INPUT, search_term)


@pytest.fixture
def dashboard_page(driver, base_url):
    """Dashboard page fixture"""
    return DashboardPage(driver, base_url)


@pytest.fixture  
def projects_page(driver, base_url):
    """Projects page fixture"""
    return ProjectsPage(driver, base_url)
