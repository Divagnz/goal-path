"""
Enhanced Page Objects for GoalPath UI Testing
Extends the existing page objects with comprehensive functionality
"""

import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class TasksPage:
    """Tasks page object with comprehensive task management functionality"""
    
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)
        
    # Locators
    CREATE_TASK_BTN = (By.CSS_SELECTOR, "[data-testid='create-task-btn'], .create-task-btn")
    TASK_ITEMS = (By.CSS_SELECTOR, "[data-testid='task-item'], .task-item, .task-card")
    TASK_CHECKBOXES = (By.CSS_SELECTOR, "input[type='checkbox'][data-task-id], .task-checkbox")
    SEARCH_INPUT = (By.CSS_SELECTOR, "[data-testid='task-search'], input[placeholder*='search']")
    FILTER_DROPDOWN = (By.CSS_SELECTOR, "[data-testid='task-filter'], .filter-dropdown")
    
    def go_to(self, path="/tasks"):
        """Navigate to tasks page"""
        url = f"{self.base_url}{path}"
        self.driver.get(url)
        
    def wait_for_page_load(self):
        """Wait for tasks page to load"""
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
    def get_task_count(self):
        """Get number of task items"""
        try:
            tasks = self.driver.find_elements(*self.TASK_ITEMS)
            return len(tasks)
        except NoSuchElementException:
            return 0
            
    def click_create_task(self):
        """Click create task button"""
        selectors = [
            "[data-testid='create-task-btn']",
            ".create-task-btn",
            "button[class*='create']",
            "a[href*='create']"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if "task" in element.text.lower() or "create" in element.text.lower():
                    element.click()
                    return True
            except NoSuchElementException:
                continue
        return False
        
    def toggle_task_completion(self, task_index=0):
        """Toggle task completion checkbox"""
        try:
            checkboxes = self.driver.find_elements(*self.TASK_CHECKBOXES)
            if checkboxes and task_index < len(checkboxes):
                checkboxes[task_index].click()
                time.sleep(0.5)  # Wait for HTMX update
                return True
        except Exception:
            pass
        return False


class GoalsPage:
    """Goals page object with goal management functionality"""
    
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)
        
    # Locators
    CREATE_GOAL_BTN = (By.CSS_SELECTOR, "[data-testid='create-goal-btn'], .create-goal-btn")
    GOAL_CARDS = (By.CSS_SELECTOR, "[data-testid='goal-card'], .goal-card")
    PROGRESS_BARS = (By.CSS_SELECTOR, ".progress-bar, progress, [class*='progress']")
    
    def go_to(self, path="/goals"):
        """Navigate to goals page"""
        url = f"{self.base_url}{path}"
        self.driver.get(url)
        
    def wait_for_page_load(self):
        """Wait for goals page to load"""
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
    def get_goal_count(self):
        """Get number of goal cards"""
        try:
            goals = self.driver.find_elements(*self.GOAL_CARDS)
            return len(goals)
        except NoSuchElementException:
            return 0
            
    def click_create_goal(self):
        """Click create goal button"""
        selectors = [
            "[data-testid='create-goal-btn']",
            ".create-goal-btn",
            "button[class*='create']"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if "goal" in element.text.lower() or "create" in element.text.lower():
                    element.click()
                    return True
            except NoSuchElementException:
                continue
        return False
