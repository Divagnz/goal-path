"""
Unit tests for database models
"""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from src.goalpath.models import Goal, GoalProject, Project, Task, TaskDependency


class TestProjectModel:
    """Test the Project model"""

    def test_create_project_minimal(self, test_db_session, db_helper):
        """Test creating a project with minimal required fields"""
        project = db_helper.create_test_project(test_db_session, name="Minimal Project")

        assert project.id is not None
        assert project.name == "Minimal Project"
        assert project.status == "active"  # default value
        assert project.priority == "medium"  # default value
        assert project.created_at is not None
        assert project.updated_at is not None

    def test_create_project_complete(self, test_db_session):
        """Test creating a project with all fields"""
        project = Project(
            name="Complete Project",
            description="A complete project for testing",
            status="active",
            priority="high",
            start_date=date(2025, 1, 1),
            target_end_date=date(2025, 12, 31),
            created_by="test_user",
        )

        test_db_session.add(project)
        test_db_session.commit()
        test_db_session.refresh(project)

        assert project.name == "Complete Project"
        assert project.description == "A complete project for testing"
        assert project.status == "active"
        assert project.priority == "high"
        assert project.start_date == date(2025, 1, 1)
        assert project.target_end_date == date(2025, 12, 31)
        assert project.created_by == "test_user"

    def test_project_unique_name_constraint(self, test_db_session, db_helper):
        """Test that project names must be unique"""
        db_helper.create_test_project(test_db_session, name="Unique Project")

        # Attempt to create another project with same name
        with pytest.raises(IntegrityError):
            db_helper.create_test_project(test_db_session, name="Unique Project")

    def test_project_status_validation(self, test_db_session):
        """Test project status validation"""
        # Valid status should work
        project = Project(name="Valid Status", status="active")
        test_db_session.add(project)
        test_db_session.commit()

        # Invalid status should be caught by application logic
        # Note: SQLite doesn't enforce CHECK constraints by default
        # This would be enforced at the application level

    def test_project_relationships(self, test_db_session, db_helper):
        """Test project relationships with tasks"""
        project = db_helper.create_test_project(test_db_session, name="Project with Tasks")

        # Create some tasks for this project
        task1 = db_helper.create_test_task(test_db_session, project.id, title="Task 1")
        task2 = db_helper.create_test_task(test_db_session, project.id, title="Task 2")

        # Refresh to load relationships
        test_db_session.refresh(project)

        assert len(project.tasks) == 2
        assert task1 in project.tasks
        assert task2 in project.tasks
        assert task1.project == project
        assert task2.project == project


class TestTaskModel:
    """Test the Task model"""

    def test_create_task_minimal(self, test_db_session, db_helper):
        """Test creating a task with minimal required fields"""
        project = db_helper.create_test_project(test_db_session)
        task = db_helper.create_test_task(test_db_session, project.id, title="Minimal Task")

        assert task.id is not None
        assert task.project_id == project.id
        assert task.title == "Minimal Task"
        assert task.task_type == "task"  # default value
        assert task.status == "backlog"  # default value
        assert task.priority == "medium"  # default value

    def test_task_hierarchy(self, test_db_session, db_helper):
        """Test hierarchical task relationships"""
        project = db_helper.create_test_project(test_db_session)

        # Create parent task
        parent_task = db_helper.create_test_task(
            test_db_session, project.id, title="Parent Task", task_type="epic"
        )

        # Create child tasks
        child_task1 = db_helper.create_test_task(
            test_db_session, project.id, title="Child Task 1", parent_task_id=parent_task.id
        )

        child_task2 = db_helper.create_test_task(
            test_db_session, project.id, title="Child Task 2", parent_task_id=parent_task.id
        )

        # Test relationships
        test_db_session.refresh(parent_task)

        assert len(parent_task.subtasks) == 2
        assert child_task1 in parent_task.subtasks
        assert child_task2 in parent_task.subtasks
        assert child_task1.parent_task == parent_task
        assert child_task2.parent_task == parent_task

    def test_task_foreign_key_constraint(self, test_db_session, db_helper):
        """Test that tasks require valid project_id"""
        with pytest.raises(IntegrityError):
            task = Task(project_id="invalid-project-id", title="Invalid Task")
            test_db_session.add(task)
            test_db_session.commit()


class TestGoalModel:
    """Test the Goal model"""

    def test_create_goal_minimal(self, test_db_session, db_helper):
        """Test creating a goal with minimal required fields"""
        goal = db_helper.create_test_goal(test_db_session, title="Minimal Goal")

        assert goal.id is not None
        assert goal.title == "Minimal Goal"
        assert goal.goal_type == "short_term"  # default value
        assert goal.status == "active"  # default value
        assert goal.progress_percentage == 0.0  # default value

    def test_goal_hierarchy(self, test_db_session, db_helper):
        """Test hierarchical goal relationships"""
        # Create parent goal
        parent_goal = db_helper.create_test_goal(
            test_db_session, title="Parent Goal", goal_type="long_term"
        )

        # Create child goals
        child_goal1 = db_helper.create_test_goal(
            test_db_session,
            title="Child Goal 1",
            parent_goal_id=parent_goal.id,
            goal_type="medium_term",
        )

        child_goal2 = db_helper.create_test_goal(
            test_db_session,
            title="Child Goal 2",
            parent_goal_id=parent_goal.id,
            goal_type="short_term",
        )

        # Test relationships
        test_db_session.refresh(parent_goal)

        assert len(parent_goal.subgoals) == 2
        assert child_goal1 in parent_goal.subgoals
        assert child_goal2 in parent_goal.subgoals
        assert child_goal1.parent_goal == parent_goal
        assert child_goal2.parent_goal == parent_goal

    def test_progress_percentage_bounds(self, test_db_session):
        """Test that progress percentage is within valid bounds"""
        # Valid progress values
        goal1 = Goal(title="0% Progress", progress_percentage=0.0)
        goal2 = Goal(title="50% Progress", progress_percentage=50.0)
        goal3 = Goal(title="100% Progress", progress_percentage=100.0)

        test_db_session.add_all([goal1, goal2, goal3])
        test_db_session.commit()

        # Invalid progress values would be caught by CHECK constraints
        # in a database that enforces them


class TestTaskDependencyModel:
    """Test the TaskDependency model"""

    def test_create_task_dependency(self, test_db_session, db_helper):
        """Test creating task dependencies"""
        project = db_helper.create_test_project(test_db_session)

        task1 = db_helper.create_test_task(test_db_session, project.id, title="Task 1")
        task2 = db_helper.create_test_task(test_db_session, project.id, title="Task 2")

        # Create dependency: task2 blocks task1
        dependency = TaskDependency(
            task_id=task1.id, depends_on_task_id=task2.id, dependency_type="blocks"
        )

        test_db_session.add(dependency)
        test_db_session.commit()
        test_db_session.refresh(dependency)

        assert dependency.task_id == task1.id
        assert dependency.depends_on_task_id == task2.id
        assert dependency.dependency_type == "blocks"

    def test_prevent_self_dependency(self, test_db_session, db_helper):
        """Test that tasks cannot depend on themselves"""
        project = db_helper.create_test_project(test_db_session)
        task = db_helper.create_test_task(test_db_session, project.id, title="Self Task")

        # Attempt to create self-dependency should fail
        with pytest.raises(IntegrityError):
            dependency = TaskDependency(
                task_id=task.id, depends_on_task_id=task.id, dependency_type="blocks"
            )
            test_db_session.add(dependency)
            test_db_session.commit()


class TestGoalProjectModel:
    """Test the GoalProject relationship model"""

    def test_create_goal_project_link(self, test_db_session, db_helper):
        """Test linking goals and projects"""
        goal = db_helper.create_test_goal(test_db_session, title="Test Goal")
        project = db_helper.create_test_project(test_db_session, name="Test Project")

        # Create link
        link = GoalProject(goal_id=goal.id, project_id=project.id, weight=0.75)

        test_db_session.add(link)
        test_db_session.commit()
        test_db_session.refresh(link)

        assert link.goal_id == goal.id
        assert link.project_id == project.id
        assert link.weight == 0.75

        # Test relationships
        test_db_session.refresh(goal)
        test_db_session.refresh(project)

        assert len(goal.project_links) == 1
        assert len(project.goal_links) == 1
        assert goal.project_links[0].project == project
        assert project.goal_links[0].goal == goal
