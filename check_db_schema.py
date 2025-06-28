#!/usr/bin/env python3
"""
Check database schema to understand the current state
"""
import sqlite3

def check_database_schema():
    try:
        # Connect to the database
        conn = sqlite3.connect('goalpath.db')
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("=== EXISTING TABLES ===")
        for table in tables:
            print(f"- {table[0]}")
        
        print("\n=== TASKS TABLE SCHEMA ===")
        cursor.execute("PRAGMA table_info(tasks);")
        columns = cursor.fetchall()
        
        if columns:
            print("Columns in tasks table:")
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        else:
            print("Tasks table does not exist")
            
        print("\n=== CHECK FOR EPICS AND MILESTONES TABLES ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='epics' OR name='milestones');")
        epic_tables = cursor.fetchall()
        
        if epic_tables:
            for table in epic_tables:
                print(f"\n{table[0]} table exists:")
                cursor.execute(f"PRAGMA table_info({table[0]});")
                cols = cursor.fetchall()
                for col in cols:
                    print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        else:
            print("No epics or milestones tables found")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database_schema()
