#!/usr/bin/env python3
"""
GoalPath Database Initialization Script
Combines schema and sample data creation for development setup
"""

import os
import sqlite3
from pathlib import Path


def init_database(db_path: str = "goalpath.db", with_sample_data: bool = True):
    """
    Initialize the GoalPath database with schema and optional sample data

    Args:
        db_path: Path to SQLite database file
        with_sample_data: Whether to include sample data for development
    """

    # Get the directory containing this script
    script_dir = Path(__file__).parent

    # Define SQL file paths
    schema_files = [
        script_dir / "schema_complete.sql",
    ]
    sample_data_file = script_dir / "sample_data.sql"

    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")

    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("Creating database schema...")

        # Execute schema files
        for schema_file in schema_files:
            if schema_file.exists():
                with open(schema_file, "r") as f:
                    schema_sql = f.read()
                    # Execute each statement separately to handle SQLite limitations
                    statements = schema_sql.split(";")
                    for statement in statements:
                        statement = statement.strip()
                        if statement:
                            cursor.execute(statement)
                print(f"Executed: {schema_file.name}")
            else:
                print(f"Warning: Schema file not found: {schema_file}")

        # Insert sample data if requested
        if with_sample_data and sample_data_file.exists():
            print("Inserting sample data...")
            with open(sample_data_file, "r") as f:
                sample_sql = f.read()
                statements = sample_sql.split(";")
                for statement in statements:
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)
            print("Sample data inserted successfully")

        # Commit all changes
        conn.commit()

        print(f"Database initialized successfully: {db_path}")

        # Display some statistics
        cursor.execute("SELECT COUNT(*) FROM projects")
        project_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM goals")
        goal_count = cursor.fetchone()[0]

        print("Database contains:")
        print(f"  - {project_count} projects")
        print(f"  - {task_count} tasks")
        print(f"  - {goal_count} goals")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        raise

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()


def verify_schema(db_path: str = "goalpath.db"):
    """
    Verify that all expected tables exist in the database
    """
    expected_tables = [
        "projects",
        "tasks",
        "task_dependencies",
        "goals",
        "goal_projects",
        "sprints",
        "sprint_tasks",
        "reminders",
        "schedule_events",
        "project_context",
        "task_comments",
        "task_attachments",
        "issues",
    ]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]

        print("Schema verification:")
        missing_tables = []
        for table in expected_tables:
            if table in existing_tables:
                print(f"  ✓ {table}")
            else:
                print(f"  ✗ {table} (MISSING)")
                missing_tables.append(table)

        if missing_tables:
            print(f"Warning: {len(missing_tables)} tables are missing!")
            return False
        else:
            print("All expected tables are present!")
            return True

    except sqlite3.Error as e:
        print(f"Verification error: {e}")
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize GoalPath database")
    parser.add_argument("--db-path", default="goalpath.db", help="Database file path")
    parser.add_argument("--no-sample-data", action="store_true", help="Skip sample data insertion")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing schema")

    args = parser.parse_args()

    if args.verify_only:
        verify_schema(args.db_path)
    else:
        init_database(args.db_path, not args.no_sample_data)
        verify_schema(args.db_path)
