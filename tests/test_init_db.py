"""
Tests for database initialization and sample data creation
"""

import pytest
from src.goalpath.init_db import DatabaseInitializer
from src.goalpath.models import Project, Task, Goal, GoalProject


class TestDatabaseInitializer:
    """Test the DatabaseInitializer class"""

    def test_create_sample_projects(self, test_db_session):
        """Test creating sample projects"""
        projects = DatabaseInitializer.create_sample_projects(test_db_session)

        assert len(projects) == 4

        # Check specific projects exist
        project_names = [p.name for p in projects]
        assert "Website Redesign" in project_names
        assert "Mobile App Development" in project_names
        assert "Database Migration" in project_names
        assert "API Integration Platform" in project_names

        # Check project properties
        website_project = next(p for p in projects if p.name == "Website Redesign")
        assert website_project.status == "active"
        assert website_project.priority == "high"
        assert website_project.created_by == "product_manager"

        db_project = next(p for p in projects if p.name == "Database Migration")
        assert db_project.status == "completed"
        assert db_project.actual_end_date is not None

    def test_create_sample_tasks(self, test_db_session):
        """Test creating sample tasks with hierarchy"""
        # First create projects
        projects = DatabaseInitializer.create_sample_projects(test_db_session)

        # Then create tasks
        tasks = DatabaseInitializer.create_sample_tasks(test_db_session, projects)

        assert len(tasks) >= 8  # Should have at least 8 tasks

        # Check specific tasks exist
        task_titles = [t.title for t in tasks]
        assert "Design System Creation" in task_titles
        assert "Color Palette Design" in task_titles
        assert "User Authentication System" in task_titles

        # Check task hierarchy
        design_system = next(t for t in tasks if t.title == "Design System Creation")
        color_palette = next(t for t in tasks if t.title == "Color Palette Design")

        assert color_palette.parent_task_id == design_system.id

        # Check task properties
        assert design_system.task_type == "epic"
        assert color_palette.status == "done"
        assert color_palette.completed_date is not None

    def test_create_sample_goals(self, test_db_session):
        """Test creating sample goals"""
        # Create projects first (needed for goal-project links later)
        projects = DatabaseInitializer.create_sample_projects(test_db_session)

        # Create goals
        goals = DatabaseInitializer.create_sample_goals(test_db_session, projects)

        assert len(goals) == 4

        # Check specific goals exist
        goal_titles = [g.title for g in goals]
        assert "Q2 Product Launch" in goal_titles
        assert "Market Expansion" in goal_titles
        assert "Technical Excellence" in goal_titles
        assert "Customer Satisfaction" in goal_titles

        # Check goal properties
        q2_launch = next(g for g in goals if g.title == "Q2 Product Launch")
        assert q2_launch.goal_type == "short_term"
        assert q2_launch.status == "active"
        assert q2_launch.progress_percentage == 35.0

        tech_excellence = next(g for g in goals if g.title == "Technical Excellence")
        assert tech_excellence.goal_type == "long_term"
        assert tech_excellence.target_date is None  # Long-term goals may not have specific dates

    def test_create_goal_project_links(self, test_db_session):
        """Test creating relationships between goals and projects"""
        # Create projects and goals
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        goals = DatabaseInitializer.create_sample_goals(test_db_session, projects)

        # Create links
        DatabaseInitializer.create_goal_project_links(test_db_session, goals, projects)

        # Check that links were created
        links = test_db_session.query(GoalProject).all()
        assert len(links) >= 8  # Should have multiple goal-project relationships

        # Check specific links
        q2_launch = next(g for g in goals if g.title == "Q2 Product Launch")
        q2_links = (
            test_db_session.query(GoalProject).filter(GoalProject.goal_id == q2_launch.id).all()
        )

        assert len(q2_links) == 2  # Q2 launch should link to 2 projects

        # Check weights
        weights = [float(link.weight) for link in q2_links]
        assert 0.6 in weights
        assert 0.4 in weights

        # Verify total weight
        total_weight = sum(float(link.weight) for link in q2_links)
        assert total_weight == 1.0

    def test_get_database_stats(self, test_db_session):
        """Test getting database statistics"""
        # Create sample data
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        tasks = DatabaseInitializer.create_sample_tasks(test_db_session, projects)
        goals = DatabaseInitializer.create_sample_goals(test_db_session, projects)
        DatabaseInitializer.create_goal_project_links(test_db_session, goals, projects)

        # Get statistics
        stats = DatabaseInitializer.get_database_stats(test_db_session)

        # Check structure
        assert "projects" in stats
        assert "tasks" in stats
        assert "goals" in stats
        assert "relationships" in stats

        # Check project stats
        assert stats["projects"]["total"] == 4
        assert "by_status" in stats["projects"]
        assert stats["projects"]["by_status"]["active"] >= 2
        assert stats["projects"]["by_status"]["completed"] >= 1

        # Check task stats
        assert stats["tasks"]["total"] >= 8
        assert "by_status" in stats["tasks"]
        assert "by_type" in stats["tasks"]
        assert stats["tasks"]["by_status"]["done"] >= 2
        assert stats["tasks"]["by_type"]["epic"] >= 1

        # Check goal stats
        assert stats["goals"]["total"] == 4
        assert "by_status" in stats["goals"]
        assert "by_type" in stats["goals"]
        assert stats["goals"]["by_status"]["active"] == 4

        # Check relationships
        assert stats["relationships"]["goal_project_links"] >= 8

    def test_clear_all_data(self, test_db_session):
        """Test clearing all data from database"""
        # Create sample data
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        tasks = DatabaseInitializer.create_sample_tasks(test_db_session, projects)
        goals = DatabaseInitializer.create_sample_goals(test_db_session, projects)
        DatabaseInitializer.create_goal_project_links(test_db_session, goals, projects)

        # Verify data exists
        assert test_db_session.query(Project).count() > 0
        assert test_db_session.query(Task).count() > 0
        assert test_db_session.query(Goal).count() > 0
        assert test_db_session.query(GoalProject).count() > 0

        # Clear all data
        DatabaseInitializer.clear_all_data(test_db_session)

        # Verify data is gone
        assert test_db_session.query(Project).count() == 0
        assert test_db_session.query(Task).count() == 0
        assert test_db_session.query(Goal).count() == 0
        assert test_db_session.query(GoalProject).count() == 0

    def test_task_hierarchy_integrity(self, test_db_session):
        """Test that task hierarchy is properly established"""
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        tasks = DatabaseInitializer.create_sample_tasks(test_db_session, projects)

        # Find parent and child tasks
        design_system = next(t for t in tasks if t.title == "Design System Creation")
        color_palette = next(t for t in tasks if t.title == "Color Palette Design")
        typography = next(t for t in tasks if t.title == "Typography System")

        # Verify hierarchy
        assert color_palette.parent_task_id == design_system.id
        assert typography.parent_task_id == design_system.id

        # Verify parent task has children through relationships
        test_db_session.refresh(design_system)
        child_tasks = (
            test_db_session.query(Task).filter(Task.parent_task_id == design_system.id).all()
        )

        assert len(child_tasks) >= 2
        child_titles = [t.title for t in child_tasks]
        assert "Color Palette Design" in child_titles
        assert "Typography System" in child_titles

    def test_project_task_relationships(self, test_db_session):
        """Test that tasks are properly linked to projects"""
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        tasks = DatabaseInitializer.create_sample_tasks(test_db_session, projects)

        # Find specific project and its tasks
        website_project = next(p for p in projects if p.name == "Website Redesign")
        website_tasks = [t for t in tasks if t.project_id == website_project.id]

        assert len(website_tasks) >= 3  # Should have multiple tasks for website project

        # Verify task titles belong to website project
        website_task_titles = [t.title for t in website_tasks]
        assert "Design System Creation" in website_task_titles
        assert "Color Palette Design" in website_task_titles

        # Verify all tasks have valid project IDs
        for task in tasks:
            assert task.project_id is not None
            # Verify project exists
            project = test_db_session.query(Project).filter(Project.id == task.project_id).first()
            assert project is not None

    def test_goal_progress_values(self, test_db_session):
        """Test that goals have realistic progress values"""
        projects = DatabaseInitializer.create_sample_projects(test_db_session)
        goals = DatabaseInitializer.create_sample_goals(test_db_session, projects)

        for goal in goals:
            # Progress should be between 0 and 100
            assert 0.0 <= goal.progress_percentage <= 100.0

            # Active goals should have some progress variation
            if goal.status == "active":
                assert goal.progress_percentage >= 0.0

        # Check specific goal progress values are realistic
        tech_excellence = next(g for g in goals if g.title == "Technical Excellence")
        assert tech_excellence.progress_percentage == 60.0  # Should be well progressed

        market_expansion = next(g for g in goals if g.title == "Market Expansion")
        assert market_expansion.progress_percentage == 15.0  # Should be early stage
