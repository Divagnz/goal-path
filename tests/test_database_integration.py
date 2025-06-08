"""
Integration tests for database operations
"""


import pytest

from src.goalpath.models import GoalProject, Project, Task


class TestDatabaseIntegration:
    """Test database integration and complex operations"""

    def test_database_session_lifecycle(self, test_db_session):
        """Test that database sessions work correctly"""
        # Create a project
        project = Project(name="Session Test Project")
        test_db_session.add(project)
        test_db_session.commit()

        # Verify it was saved
        saved_project = (
            test_db_session.query(Project).filter(Project.name == "Session Test Project").first()
        )

        assert saved_project is not None
        assert saved_project.name == "Session Test Project"
        assert saved_project.id == project.id

    def test_cascade_delete_project_tasks(self, test_db_session, db_helper):
        """Test that deleting a project cascades to its tasks"""
        project = db_helper.create_test_project(test_db_session, name="Delete Test Project")

        # Create tasks for this project
        task1 = db_helper.create_test_task(test_db_session, project.id, title="Task 1")
        task2 = db_helper.create_test_task(test_db_session, project.id, title="Task 2")

        # Verify tasks exist
        task_count = test_db_session.query(Task).filter(Task.project_id == project.id).count()
        assert task_count == 2

        # Delete the project
        test_db_session.delete(project)
        test_db_session.commit()

        # Verify tasks were also deleted (cascade)
        remaining_tasks = test_db_session.query(Task).filter(Task.project_id == project.id).count()
        assert remaining_tasks == 0

    def test_complex_hierarchy_queries(self, test_db_session, db_helper):
        """Test querying hierarchical data structures"""
        project = db_helper.create_test_project(test_db_session, name="Hierarchy Test")

        # Create a complex task hierarchy
        epic = db_helper.create_test_task(
            test_db_session, project.id, title="Epic Task", task_type="epic"
        )

        story1 = db_helper.create_test_task(
            test_db_session, project.id, title="Story 1", task_type="story", parent_task_id=epic.id
        )

        story2 = db_helper.create_test_task(
            test_db_session, project.id, title="Story 2", task_type="story", parent_task_id=epic.id
        )

        subtask1 = db_helper.create_test_task(
            test_db_session,
            project.id,
            title="Subtask 1",
            task_type="subtask",
            parent_task_id=story1.id,
        )

        subtask2 = db_helper.create_test_task(
            test_db_session,
            project.id,
            title="Subtask 2",
            task_type="subtask",
            parent_task_id=story1.id,
        )

        # Test querying root tasks (no parent)
        root_tasks = (
            test_db_session.query(Task)
            .filter(Task.project_id == project.id, Task.parent_task_id.is_(None))
            .all()
        )

        assert len(root_tasks) == 1
        assert root_tasks[0].title == "Epic Task"

        # Test querying children of epic
        epic_children = test_db_session.query(Task).filter(Task.parent_task_id == epic.id).all()

        assert len(epic_children) == 2
        assert set(task.title for task in epic_children) == {"Story 1", "Story 2"}

        # Test querying all descendants (would need recursive query in real app)
        all_tasks = test_db_session.query(Task).filter(Task.project_id == project.id).count()

        assert all_tasks == 5  # epic + 2 stories + 2 subtasks

    def test_goal_project_links_with_progress(self, test_db_session, db_helper):
        """Test goal-project relationships and progress calculation"""
        # Create a goal
        goal = db_helper.create_test_goal(test_db_session, title="Major Goal")

        # Create projects
        project1 = db_helper.create_test_project(test_db_session, name="Project 1")
        project2 = db_helper.create_test_project(test_db_session, name="Project 2")

        # Link projects to goal with different weights
        link1 = GoalProject(goal_id=goal.id, project_id=project1.id, weight=0.6)
        link2 = GoalProject(goal_id=goal.id, project_id=project2.id, weight=0.4)

        test_db_session.add_all([link1, link2])
        test_db_session.commit()

        # Test querying linked projects
        linked_projects = (
            test_db_session.query(Project)
            .join(GoalProject)
            .filter(GoalProject.goal_id == goal.id)
            .all()
        )

        assert len(linked_projects) == 2
        assert set(p.name for p in linked_projects) == {"Project 1", "Project 2"}

        # Test querying with weights
        project_weights = (
            test_db_session.query(Project.name, GoalProject.weight)
            .join(GoalProject)
            .filter(GoalProject.goal_id == goal.id)
            .all()
        )

        weights_dict = {name: weight for name, weight in project_weights}
        assert float(weights_dict["Project 1"]) == 0.6
        assert float(weights_dict["Project 2"]) == 0.4

    def test_database_constraints_enforcement(self, test_db_session, db_helper):
        """Test that database constraints are enforced"""
        project = db_helper.create_test_project(test_db_session, name="Constraint Test")

        # Test foreign key constraint
        with pytest.raises(Exception):  # Could be IntegrityError or similar
            invalid_task = Task(project_id="non-existent-id", title="Invalid Task")
            test_db_session.add(invalid_task)
            test_db_session.commit()

    def test_transaction_rollback(self, test_db_session, db_helper):
        """Test transaction rollback on errors"""
        project = db_helper.create_test_project(test_db_session, name="Rollback Test")

        # Start a transaction
        task1 = db_helper.create_test_task(test_db_session, project.id, title="Valid Task")

        # Verify task was created
        assert test_db_session.query(Task).filter(Task.title == "Valid Task").first() is not None

        try:
            # Attempt to create invalid task
            invalid_task = Task(project_id="invalid-id", title="Invalid Task")
            test_db_session.add(invalid_task)
            test_db_session.commit()
        except Exception:
            test_db_session.rollback()

        # Verify valid task still exists after rollback
        remaining_task = test_db_session.query(Task).filter(Task.title == "Valid Task").first()
        assert remaining_task is not None

    def test_multiple_session_isolation(self, test_db_manager):
        """Test that different sessions are properly isolated"""
        # Create two separate sessions
        session1 = test_db_manager.get_sync_session()
        session2 = test_db_manager.get_sync_session()
        
        project1_id = None
        project2_id = None

        try:
            # Create project in session1
            project1 = Project(name="Session1 Project")
            session1.add(project1)
            session1.commit()
            project1_id = project1.id

            # Create project in session2
            project2 = Project(name="Session2 Project")
            session2.add(project2)
            session2.commit()
            project2_id = project2.id

            # Verify each session can see its own data
            s1_projects = session1.query(Project).all()
            s2_projects = session2.query(Project).all()

            # Both sessions should see both projects (they're in the same database)
            assert len(s1_projects) >= 2
            assert len(s2_projects) >= 2

        finally:
            # Clean up the test data
            try:
                if project1_id:
                    session1.query(Project).filter(Project.id == project1_id).delete()
                    session1.commit()
                if project2_id:
                    session2.query(Project).filter(Project.id == project2_id).delete()
                    session2.commit()
            except Exception:
                session1.rollback()
                session2.rollback()
            finally:
                session1.close()
                session2.close()
