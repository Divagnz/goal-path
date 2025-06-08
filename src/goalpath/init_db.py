"""
Database initialization and sample data seeding for GoalPath
"""

from datetime import date, datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from .database import db_manager
from .models import Goal, GoalProject, Project, Task
# Import extended models to ensure they are registered
from .models.extended import Issue, Reminder, TaskComment, TaskAttachment, ProjectContext, ScheduleEvent


class DatabaseInitializer:
    """Database initialization and sample data management"""

    @staticmethod
    def create_sample_projects(session: Session) -> List[Project]:
        """Create sample projects with realistic data"""

        sample_projects = [
            {
                "name": "Website Redesign",
                "description": "Complete overhaul of company website with modern design and improved UX",
                "status": "active",
                "priority": "high",
                "start_date": date(2025, 1, 15),
                "target_end_date": date(2025, 8, 31),
                "created_by": "product_manager",
            },
            {
                "name": "Mobile App Development",
                "description": "Native iOS and Android applications for customer portal",
                "status": "active",
                "priority": "critical",
                "start_date": date(2025, 2, 1),
                "target_end_date": date(2025, 12, 15),
                "created_by": "tech_lead",
            },
            {
                "name": "Database Migration",
                "description": "Migrate from MySQL to PostgreSQL for better performance",
                "status": "completed",
                "priority": "medium",
                "start_date": date(2025, 3, 1),
                "target_end_date": date(2025, 6, 30),
                "actual_end_date": date(2025, 5, 20),
                "created_by": "dev_ops",
            },
            {
                "name": "API Integration Platform",
                "description": "Build unified API platform for third-party integrations",
                "status": "active",
                "priority": "medium",
                "start_date": date(2025, 4, 1),
                "target_end_date": date(2025, 10, 31),
                "created_by": "api_team",
            },
        ]

        projects = []
        for project_data in sample_projects:
            project = Project(**project_data)
            session.add(project)
            projects.append(project)

        session.commit()

        # Refresh to get IDs
        for project in projects:
            session.refresh(project)

        return projects

    @staticmethod
    def create_sample_tasks(session: Session, projects: List[Project]) -> List[Task]:
        """Create sample tasks for the projects"""

        # Find specific projects for task creation
        website_project = next(p for p in projects if p.name == "Website Redesign")
        mobile_project = next(p for p in projects if p.name == "Mobile App Development")
        db_project = next(p for p in projects if p.name == "Database Migration")
        api_project = next(p for p in projects if p.name == "API Integration Platform")

        sample_tasks = [
            # Website Redesign Tasks
            {
                "project_id": website_project.id,
                "title": "Design System Creation",
                "description": "Create comprehensive design system with components, colors, and typography",
                "task_type": "epic",
                "status": "in_progress",
                "priority": "high",
                "estimated_hours": 80.0,
                "actual_hours": 45.0,
                "assigned_to": "design_lead",
                "created_by": "product_manager",
            },
            {
                "project_id": website_project.id,
                "title": "Color Palette Design",
                "description": "Define primary, secondary, and accent colors for the new brand",
                "task_type": "story",
                "status": "done",
                "priority": "medium",
                "estimated_hours": 8.0,
                "actual_hours": 6.5,
                "assigned_to": "ui_designer",
                "created_by": "design_lead",
                "completed_date": datetime(2025, 2, 15, 14, 30),
            },
            {
                "project_id": website_project.id,
                "title": "Typography System",
                "description": "Select and implement typography hierarchy and font combinations",
                "task_type": "story",
                "status": "in_progress",
                "priority": "medium",
                "estimated_hours": 12.0,
                "actual_hours": 8.0,
                "assigned_to": "ui_designer",
                "created_by": "design_lead",
            },
            # Mobile App Tasks
            {
                "project_id": mobile_project.id,
                "title": "User Authentication System",
                "description": "Implement secure authentication with biometric support",
                "task_type": "epic",
                "status": "todo",
                "priority": "highest",
                "estimated_hours": 120.0,
                "assigned_to": "mobile_dev_lead",
                "created_by": "tech_lead",
            },
            {
                "project_id": mobile_project.id,
                "title": "Login Screen Design",
                "description": "Design login screen with social auth options",
                "task_type": "story",
                "status": "done",
                "priority": "high",
                "estimated_hours": 16.0,
                "actual_hours": 14.0,
                "assigned_to": "mobile_designer",
                "created_by": "mobile_dev_lead",
                "completed_date": datetime(2025, 3, 10, 16, 0),
            },
            # Database Migration Tasks
            {
                "project_id": db_project.id,
                "title": "Schema Migration Scripts",
                "description": "Create automated scripts to migrate all table schemas",
                "task_type": "task",
                "status": "done",
                "priority": "critical",
                "estimated_hours": 40.0,
                "actual_hours": 38.5,
                "assigned_to": "database_admin",
                "created_by": "dev_ops",
                "completed_date": datetime(2025, 4, 20, 9, 15),
            },
            {
                "project_id": db_project.id,
                "title": "Data Validation Testing",
                "description": "Comprehensive testing to ensure data integrity after migration",
                "task_type": "task",
                "status": "done",
                "priority": "critical",
                "estimated_hours": 32.0,
                "actual_hours": 35.0,
                "assigned_to": "qa_engineer",
                "created_by": "database_admin",
                "completed_date": datetime(2025, 5, 15, 17, 30),
            },
            # API Platform Tasks
            {
                "project_id": api_project.id,
                "title": "API Gateway Setup",
                "description": "Configure and deploy API gateway with rate limiting and authentication",
                "task_type": "story",
                "status": "in_progress",
                "priority": "high",
                "estimated_hours": 24.0,
                "actual_hours": 12.0,
                "assigned_to": "backend_dev",
                "created_by": "api_team",
            },
        ]

        tasks = []
        for task_data in sample_tasks:
            task = Task(**task_data)
            session.add(task)
            tasks.append(task)

        session.commit()

        # Refresh to get IDs
        for task in tasks:
            session.refresh(task)

        # Create task hierarchy (subtasks)
        design_system_task = next(t for t in tasks if t.title == "Design System Creation")
        color_palette_task = next(t for t in tasks if t.title == "Color Palette Design")
        typography_task = next(t for t in tasks if t.title == "Typography System")

        # Make color palette and typography subtasks of design system
        color_palette_task.parent_task_id = design_system_task.id
        typography_task.parent_task_id = design_system_task.id

        auth_system_task = next(t for t in tasks if t.title == "User Authentication System")
        login_screen_task = next(t for t in tasks if t.title == "Login Screen Design")

        # Make login screen a subtask of auth system
        login_screen_task.parent_task_id = auth_system_task.id

        session.commit()

        return tasks

    @staticmethod
    def create_sample_goals(session: Session, projects: List[Project]) -> List[Goal]:
        """Create sample goals with project links"""

        sample_goals = [
            {
                "title": "Q2 Product Launch",
                "description": "Successfully launch new product features for Q2 targets",
                "goal_type": "short_term",
                "target_date": date(2025, 6, 30),
                "status": "active",
                "progress_percentage": 35.0,
            },
            {
                "title": "Market Expansion",
                "description": "Expand into three new geographic markets by end of year",
                "goal_type": "medium_term",
                "target_date": date(2025, 12, 31),
                "status": "active",
                "progress_percentage": 15.0,
            },
            {
                "title": "Technical Excellence",
                "description": "Achieve technical excellence through infrastructure improvements",
                "goal_type": "long_term",
                "status": "active",
                "progress_percentage": 60.0,
            },
            {
                "title": "Customer Satisfaction",
                "description": "Improve customer satisfaction scores to 4.5+ rating",
                "goal_type": "medium_term",
                "target_date": date(2025, 9, 30),
                "status": "active",
                "progress_percentage": 25.0,
            },
        ]

        goals = []
        for goal_data in sample_goals:
            goal = Goal(**goal_data)
            session.add(goal)
            goals.append(goal)

        session.commit()

        # Refresh to get IDs
        for goal in goals:
            session.refresh(goal)

        return goals

    @staticmethod
    def create_goal_project_links(session: Session, goals: List[Goal], projects: List[Project]):
        """Create relationships between goals and projects"""

        # Find specific goals and projects
        q2_launch = next(g for g in goals if g.title == "Q2 Product Launch")
        market_expansion = next(g for g in goals if g.title == "Market Expansion")
        tech_excellence = next(g for g in goals if g.title == "Technical Excellence")
        customer_satisfaction = next(g for g in goals if g.title == "Customer Satisfaction")

        website_project = next(p for p in projects if p.name == "Website Redesign")
        mobile_project = next(p for p in projects if p.name == "Mobile App Development")
        db_project = next(p for p in projects if p.name == "Database Migration")
        api_project = next(p for p in projects if p.name == "API Integration Platform")

        # Create goal-project links with weights
        links = [
            # Q2 Launch involves website and mobile projects
            GoalProject(goal_id=q2_launch.id, project_id=website_project.id, weight=0.6),
            GoalProject(goal_id=q2_launch.id, project_id=mobile_project.id, weight=0.4),
            # Market Expansion primarily driven by mobile app
            GoalProject(goal_id=market_expansion.id, project_id=mobile_project.id, weight=0.8),
            GoalProject(goal_id=market_expansion.id, project_id=api_project.id, weight=0.2),
            # Technical Excellence includes infrastructure projects
            GoalProject(goal_id=tech_excellence.id, project_id=db_project.id, weight=0.5),
            GoalProject(goal_id=tech_excellence.id, project_id=api_project.id, weight=0.5),
            # Customer Satisfaction enhanced by website and mobile
            GoalProject(
                goal_id=customer_satisfaction.id, project_id=website_project.id, weight=0.4
            ),
            GoalProject(goal_id=customer_satisfaction.id, project_id=mobile_project.id, weight=0.6),
        ]

        for link in links:
            session.add(link)

        session.commit()

    @staticmethod
    def initialize_database(drop_existing: bool = False, create_sample_data: bool = True):
        """Initialize database with tables and optional sample data"""

        print("🔄 Initializing GoalPath database...")

        # Create or recreate tables
        if drop_existing:
            print("  ⚠️  Dropping existing tables...")
            db_manager.drop_tables()

        print("  📊 Creating database tables...")
        db_manager.create_tables()

        if create_sample_data:
            print("  🎭 Creating sample data...")

            with db_manager.get_sync_session() as session:
                try:
                    # Create sample projects
                    print("    📁 Creating sample projects...")
                    projects = DatabaseInitializer.create_sample_projects(session)
                    print(f"    ✅ Created {len(projects)} projects")

                    # Create sample tasks
                    print("    📋 Creating sample tasks...")
                    tasks = DatabaseInitializer.create_sample_tasks(session, projects)
                    print(f"    ✅ Created {len(tasks)} tasks")

                    # Create sample goals
                    print("    🎯 Creating sample goals...")
                    goals = DatabaseInitializer.create_sample_goals(session, projects)
                    print(f"    ✅ Created {len(goals)} goals")

                    # Link goals to projects
                    print("    🔗 Creating goal-project links...")
                    DatabaseInitializer.create_goal_project_links(session, goals, projects)
                    print("    ✅ Created goal-project relationships")

                    print("  🎉 Sample data creation completed!")

                except Exception as e:
                    print(f"  ❌ Error creating sample data: {e}")
                    session.rollback()
                    raise

        print("✅ Database initialization completed successfully!")
        return True

    @staticmethod
    def get_database_stats(session: Session) -> Dict[str, Any]:
        """Get statistics about current database content"""

        stats = {
            "projects": {"total": session.query(Project).count(), "by_status": {}},
            "tasks": {"total": session.query(Task).count(), "by_status": {}, "by_type": {}},
            "goals": {"total": session.query(Goal).count(), "by_status": {}, "by_type": {}},
            "relationships": {"goal_project_links": session.query(GoalProject).count()},
        }

        # Project statistics by status
        from sqlalchemy import func

        project_status_counts = (
            session.query(Project.status, func.count(Project.id)).group_by(Project.status).all()
        )
        stats["projects"]["by_status"] = {status: count for status, count in project_status_counts}

        # Task statistics
        task_status_counts = (
            session.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
        )
        stats["tasks"]["by_status"] = {status: count for status, count in task_status_counts}

        task_type_counts = (
            session.query(Task.task_type, func.count(Task.id)).group_by(Task.task_type).all()
        )
        stats["tasks"]["by_type"] = {task_type: count for task_type, count in task_type_counts}

        # Goal statistics
        goal_status_counts = (
            session.query(Goal.status, func.count(Goal.id)).group_by(Goal.status).all()
        )
        stats["goals"]["by_status"] = {status: count for status, count in goal_status_counts}

        goal_type_counts = (
            session.query(Goal.goal_type, func.count(Goal.id)).group_by(Goal.goal_type).all()
        )
        stats["goals"]["by_type"] = {goal_type: count for goal_type, count in goal_type_counts}

        return stats

    @staticmethod
    def clear_all_data(session: Session):
        """Clear all data from database while keeping schema"""
        print("🗑️  Clearing all data from database...")

        try:
            # Delete in proper order to respect foreign key constraints
            session.query(GoalProject).delete()
            session.query(Task).delete()
            session.query(Goal).delete()
            session.query(Project).delete()

            session.commit()
            print("✅ All data cleared successfully!")

        except Exception as e:
            session.rollback()
            print(f"❌ Error clearing data: {e}")
            raise


def main():
    """Main function for direct script execution"""
    import argparse

    parser = argparse.ArgumentParser(description="GoalPath Database Initialization")
    parser.add_argument(
        "--drop", action="store_true", help="Drop existing tables before creating new ones"
    )
    parser.add_argument("--no-sample-data", action="store_true", help="Skip creating sample data")
    parser.add_argument(
        "--stats", action="store_true", help="Show database statistics after initialization"
    )
    parser.add_argument("--clear", action="store_true", help="Clear all data from database")

    args = parser.parse_args()

    if args.clear:
        with db_manager.get_sync_session() as session:
            DatabaseInitializer.clear_all_data(session)
        return

    # Initialize database
    DatabaseInitializer.initialize_database(
        drop_existing=args.drop, create_sample_data=not args.no_sample_data
    )

    # Show statistics if requested
    if args.stats:
        print("\n📊 Database Statistics:")
        with db_manager.get_sync_session() as session:
            stats = DatabaseInitializer.get_database_stats(session)

            print(f"  Projects: {stats['projects']['total']} total")
            for status, count in stats["projects"]["by_status"].items():
                print(f"    - {status}: {count}")

            print(f"  Tasks: {stats['tasks']['total']} total")
            for status, count in stats["tasks"]["by_status"].items():
                print(f"    - {status}: {count}")

            print(f"  Goals: {stats['goals']['total']} total")
            for status, count in stats["goals"]["by_status"].items():
                print(f"    - {status}: {count}")

            print(f"  Goal-Project Links: {stats['relationships']['goal_project_links']}")


if __name__ == "__main__":
    main()
