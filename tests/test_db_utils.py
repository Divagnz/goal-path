"""
Tests for database utilities and query helpers
"""

import pytest
from datetime import date, datetime

from src.goalpath.db_utils import QueryUtils, TransactionManager
from src.goalpath.models import Project, Task, Goal, GoalProject


class TestQueryUtils:
    """Test the QueryUtils class"""

    def test_get_projects_with_stats(self, test_db_session, db_helper):
        """Test getting projects with calculated statistics"""
        # Create test data
        project1 = db_helper.create_test_project(test_db_session, name="Project 1")
        project2 = db_helper.create_test_project(test_db_session, name="Project 2")

        # Create tasks for project1
        db_helper.create_test_task(test_db_session, project1.id, title="Task 1", status="done")
        db_helper.create_test_task(
            test_db_session, project1.id, title="Task 2", status="in_progress"
        )
        db_helper.create_test_task(test_db_session, project1.id, title="Task 3", status="todo")

        # Create tasks for project2
        db_helper.create_test_task(test_db_session, project2.id, title="Task 4", status="done")
        db_helper.create_test_task(test_db_session, project2.id, title="Task 5", status="done")

        # Test query
        results = QueryUtils.get_projects_with_stats(test_db_session)

        assert len(results) == 2

        # Find project1 in results
        project1_result = next((r for r in results if "Project 1" in r["name"]), None)
        assert project1_result is not None
        assert project1_result["total_tasks"] == 3
        assert project1_result["completed_tasks"] == 1
        assert project1_result["completion_percentage"] == 33.3

        # Find project2 in results
        project2_result = next((r for r in results if "Project 2" in r["name"]), None)
        assert project2_result is not None
        assert project2_result["total_tasks"] == 2
        assert project2_result["completed_tasks"] == 2
        assert project2_result["completion_percentage"] == 100.0

    def test_get_projects_with_filters(self, test_db_session, db_helper):
        """Test filtering projects by status, priority, and search"""
        # Create test projects
        db_helper.create_test_project(
            test_db_session, name="Active High Priority", status="active", priority="high"
        )
        db_helper.create_test_project(
            test_db_session, name="Completed Medium Priority", status="completed", priority="medium"
        )
        db_helper.create_test_project(
            test_db_session, name="Active Low Priority", status="active", priority="low"
        )

        # Test status filter
        active_projects = QueryUtils.get_projects_with_stats(test_db_session, status="active")
        assert len(active_projects) == 2

        # Test priority filter
        high_priority_projects = QueryUtils.get_projects_with_stats(
            test_db_session, priority="high"
        )
        assert len(high_priority_projects) == 1
        assert high_priority_projects[0]["name"] == "Active High Priority"

        # Test search filter
        search_results = QueryUtils.get_projects_with_stats(test_db_session, search="completed")
        assert len(search_results) == 1
        assert search_results[0]["name"] == "Completed Medium Priority"

    def test_get_project_with_stats(self, test_db_session, db_helper):
        """Test getting a single project with detailed statistics"""
        project = db_helper.create_test_project(test_db_session, name="Test Project")

        # Create tasks with various statuses
        db_helper.create_test_task(test_db_session, project.id, status="done")
        db_helper.create_test_task(test_db_session, project.id, status="done")
        db_helper.create_test_task(test_db_session, project.id, status="in_progress")
        db_helper.create_test_task(test_db_session, project.id, status="blocked")
        db_helper.create_test_task(test_db_session, project.id, status="todo")

        result = QueryUtils.get_project_with_stats(test_db_session, project.id)

        assert result is not None
        assert result["name"] == "Test Project"
        assert result["total_tasks"] == 5
        assert result["completed_tasks"] == 2
        assert result["in_progress_tasks"] == 1
        assert result["blocked_tasks"] == 1
        assert result["completion_percentage"] == 40.0

    def test_get_tasks_with_hierarchy(self, test_db_session, db_helper):
        """Test getting tasks with hierarchy information"""
        project = db_helper.create_test_project(test_db_session)

        # Create parent task
        parent_task = db_helper.create_test_task(
            test_db_session, project.id, title="Parent Task", task_type="epic"
        )

        # Create child tasks
        child_task1 = db_helper.create_test_task(
            test_db_session, project.id, title="Child 1", parent_task_id=parent_task.id
        )
        child_task2 = db_helper.create_test_task(
            test_db_session, project.id, title="Child 2", parent_task_id=parent_task.id
        )

        # Test getting all tasks
        all_tasks = QueryUtils.get_tasks_with_hierarchy(test_db_session, project_id=project.id)
        assert len(all_tasks) == 3

        # Test getting only parent tasks (no parent_task_id)
        parent_tasks = QueryUtils.get_tasks_with_hierarchy(
            test_db_session, project_id=project.id, parent_task_id=None
        )
        # Note: This would need a specific query for tasks with NULL parent_task_id

        # Find parent task in results
        parent_result = next(t for t in all_tasks if t["title"] == "Parent Task")
        assert parent_result["subtask_count"] == 2
        assert parent_result["task_type"] == "epic"

    def test_get_goals_with_progress(self, test_db_session, db_helper):
        """Test getting goals with calculated progress"""
        # Create test goal
        goal = db_helper.create_test_goal(test_db_session, title="Test Goal")

        # Create projects
        project1 = db_helper.create_test_project(test_db_session, name="Project 1")
        project2 = db_helper.create_test_project(test_db_session, name="Project 2")

        # Create tasks for projects (to calculate completion)
        # Project 1: 50% complete (1 of 2 tasks done)
        db_helper.create_test_task(test_db_session, project1.id, status="done")
        db_helper.create_test_task(test_db_session, project1.id, status="todo")

        # Project 2: 100% complete (2 of 2 tasks done)
        db_helper.create_test_task(test_db_session, project2.id, status="done")
        db_helper.create_test_task(test_db_session, project2.id, status="done")

        # Link projects to goal with weights
        link1 = GoalProject(goal_id=goal.id, project_id=project1.id, weight=0.4)
        link2 = GoalProject(goal_id=goal.id, project_id=project2.id, weight=0.6)
        test_db_session.add_all([link1, link2])
        test_db_session.commit()

        # Test query
        results = QueryUtils.get_goals_with_progress(test_db_session)

        assert len(results) == 1
        goal_result = results[0]

        # Expected: (50% * 0.4) + (100% * 0.6) = 20% + 60% = 80%
        assert goal_result["progress_percentage"] == 80.0
        assert goal_result["linked_projects"] == 2

    def test_validate_task_hierarchy(self, test_db_session, db_helper):
        """Test task hierarchy validation"""
        project = db_helper.create_test_project(test_db_session)

        # Create a chain of tasks: task1 -> task2 -> task3
        task1 = db_helper.create_test_task(test_db_session, project.id, title="Task 1")
        task2 = db_helper.create_test_task(
            test_db_session, project.id, title="Task 2", parent_task_id=task1.id
        )
        task3 = db_helper.create_test_task(
            test_db_session, project.id, title="Task 3", parent_task_id=task2.id
        )

        # Test valid hierarchy (task4 can be child of task3)
        task4 = db_helper.create_test_task(test_db_session, project.id, title="Task 4")
        assert QueryUtils.validate_task_hierarchy(test_db_session, task4.id, task3.id) is True

        # Test self-reference (invalid)
        assert QueryUtils.validate_task_hierarchy(test_db_session, task1.id, task1.id) is False

        # Test cycle creation (task1 cannot be child of task3, would create cycle)
        assert QueryUtils.validate_task_hierarchy(test_db_session, task1.id, task3.id) is False


class TestTransactionManager:
    """Test the TransactionManager context manager"""

    def test_successful_transaction(self, test_db_session, db_helper):
        """Test successful transaction with automatic commit"""
        project_count_before = test_db_session.query(Project).count()

        with TransactionManager(test_db_session) as db:
            project = Project(
                name="Transaction Test Project",
                description="Testing transaction manager",
                status="active",
                priority="medium",
            )
            db.add(project)

        # Transaction should be committed automatically
        project_count_after = test_db_session.query(Project).count()
        assert project_count_after == project_count_before + 1

        # Verify project was saved
        saved_project = (
            test_db_session.query(Project)
            .filter(Project.name == "Transaction Test Project")
            .first()
        )
        assert saved_project is not None

    def test_failed_transaction_rollback(self, test_db_session, db_helper):
        """Test transaction rollback on exception"""
        project_count_before = test_db_session.query(Project).count()

        try:
            with TransactionManager(test_db_session) as db:
                # Create a valid project
                project = Project(
                    name="Valid Project",
                    description="This should be rolled back",
                    status="active",
                    priority="medium",
                )
                db.add(project)

                # Raise an exception to trigger rollback
                raise ValueError("Simulated error")

        except ValueError:
            pass  # Expected exception

        # Transaction should be rolled back
        project_count_after = test_db_session.query(Project).count()
        assert project_count_after == project_count_before

        # Verify project was not saved
        saved_project = (
            test_db_session.query(Project).filter(Project.name == "Valid Project").first()
        )
        assert saved_project is None

    def test_manual_commit(self, test_db_session, db_helper):
        """Test manual commit within transaction"""
        project_count_before = test_db_session.query(Project).count()

        with TransactionManager(test_db_session) as db:
            project = Project(
                name="Manual Commit Project",
                description="Testing manual commit",
                status="active",
                priority="medium",
            )
            db.add(project)

            # Manually commit
            transaction_manager = TransactionManager(db)
            transaction_manager.commit()

        # Verify project was saved
        project_count_after = test_db_session.query(Project).count()
        assert project_count_after == project_count_before + 1

        saved_project = (
            test_db_session.query(Project).filter(Project.name == "Manual Commit Project").first()
        )
        assert saved_project is not None

    def test_manual_rollback(self, test_db_session, db_helper):
        """Test manual rollback within transaction"""
        project_count_before = test_db_session.query(Project).count()

        with TransactionManager(test_db_session) as db:
            project = Project(
                name="Manual Rollback Project",
                description="Testing manual rollback",
                status="active",
                priority="medium",
            )
            db.add(project)

            # Manually rollback
            transaction_manager = TransactionManager(db)
            transaction_manager.rollback()

        # Verify project was not saved
        project_count_after = test_db_session.query(Project).count()
        assert project_count_after == project_count_before

        saved_project = (
            test_db_session.query(Project).filter(Project.name == "Manual Rollback Project").first()
        )
        assert saved_project is None
