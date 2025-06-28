#!/usr/bin/env python3
"""
Debug database path resolution
"""
from pathlib import Path
import os

# Simulate the path calculation from database.py
current_file = Path(__file__)
print(f"Current file: {current_file}")
print(f"Current file parent: {current_file.parent}")

# database.py location simulation
database_py_path = Path("src/goalpath/database.py")
print(f"Database.py path: {database_py_path}")
print(f"Database.py parent: {database_py_path.parent}")
print(f"Database.py parent.parent: {database_py_path.parent.parent}")
print(f"Database.py parent.parent.parent: {database_py_path.parent.parent.parent}")
print(f"Database.py parent.parent.parent.parent: {database_py_path.parent.parent.parent.parent}")

# Calculate expected db path
expected_db_path = database_py_path.parent.parent.parent.parent / "goalpath.db"
print(f"Expected DB path: {expected_db_path}")
print(f"Expected DB path resolved: {expected_db_path.resolve()}")

# Current working directory
print(f"Current working directory: {os.getcwd()}")

# Check actual database file
db_file = Path("goalpath.db")
print(f"Actual DB file exists: {db_file.exists()}")
print(f"Actual DB file path: {db_file.resolve()}")
