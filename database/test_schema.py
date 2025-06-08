#!/usr/bin/env python3
"""
Quick test script to validate the database schema
"""

import os
import sqlite3
import sys
from pathlib import Path


def test_database_schema():
    """Test basic database operations"""
    db_path = "test_goalpath.db"

    try:
        # Initialize database
        print("Testing database initialization...")

        # Import and run the init script
        sys.path.append(str(Path(__file__).parent))
        from init_db import init_database, verify_schema

        # Remove test database if exists
        if os.path.exists(db_path):
            os.remove(db_path)

        # Initialize with sample data
        init_database(db_path, with_sample_data=True)

        # Verify schema
        if not verify_schema(db_path):
            raise Exception("Schema verification failed")

        # Test basic queries
        print("\nTesting basic queries...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Test project query
        cursor.execute("SELECT COUNT(*) FROM projects")
        project_count = cursor.fetchone()[0]
        print(f"Projects: {project_count}")

        # Test task hierarchy query
        cursor.execute(
            """
            WITH RECURSIVE task_tree AS (
                SELECT id, title, parent_task_id, 0 as level
                FROM tasks 
                WHERE parent_task_id IS NULL
                UNION ALL
                SELECT t.id, t.title, t.parent_task_id, tt.level + 1
                FROM tasks t
                INNER JOIN task_tree tt ON t.parent_task_id = tt.id
                WHERE tt.level < 5
            )
            SELECT COUNT(*) FROM task_tree
        """
        )
        hierarchy_count = cursor.fetchone()[0]
        print(f"Task hierarchy nodes: {hierarchy_count}")

        # Test project stats view
        cursor.execute("SELECT * FROM project_stats LIMIT 3")
        stats = cursor.fetchall()
        print(f"Project stats retrieved: {len(stats)} rows")

        # Test goal progress calculation
        cursor.execute(
            """
            SELECT g.title, COUNT(gp.project_id) as linked_projects
            FROM goals g
            LEFT JOIN goal_projects gp ON g.id = gp.goal_id
            GROUP BY g.id, g.title
        """
        )
        goals = cursor.fetchall()
        print(f"Goals with project links: {len(goals)}")

        conn.close()

        print("\n✅ All database tests passed!")
        print(f"Test database created: {db_path}")

        # Clean up test database
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Test database cleaned up")

        return True

    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_database_schema()
    sys.exit(0 if success else 1)
