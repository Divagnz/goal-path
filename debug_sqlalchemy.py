#!/usr/bin/env python3
"""
Debug SQLAlchemy database connection and schema
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from goalpath.database import db_manager
from goalpath.models import Task
from sqlalchemy import text

def debug_database():
    # Get the database URL
    print(f"Database URL: {db_manager.database_url}")
    
    # Get a raw connection and check the schema
    with db_manager.engine.connect() as conn:
        print("\n=== RAW SQL CHECK ===")
        result = conn.execute(text("PRAGMA table_info(tasks)"))
        columns = result.fetchall()
        print("Columns in tasks table (raw SQL):")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
    
    # Try SQLAlchemy query
    print("\n=== SQLALCHEMY CHECK ===")
    try:
        with db_manager.get_sync_session() as session:
            # Just try to count tasks
            count = session.query(Task).count()
            print(f"Task count: {count}")
            
            # Try to get first task
            first_task = session.query(Task).first()
            if first_task:
                print(f"First task: {first_task.title}")
                print(f"Epic ID: {first_task.epic_id}")
                print(f"Milestone ID: {first_task.milestone_id}")
            else:
                print("No tasks found")
                
    except Exception as e:
        print(f"SQLAlchemy error: {e}")
        
        # Try to see what SQL is being generated
        print("\n=== SQL GENERATION DEBUG ===")
        try:
            query = session.query(Task)
            print(f"Generated SQL: {query}")
        except Exception as sql_e:
            print(f"SQL generation error: {sql_e}")

if __name__ == "__main__":
    debug_database()
