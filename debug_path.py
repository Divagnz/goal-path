#!/usr/bin/env python3
"""
Debug database path resolution
"""
from pathlib import Path

# Simulate the database.py path calculation
database_py_file = Path("/mnt/raid_0_drive/mcp_projs/goal-path/src/goalpath/database.py")
print(f"Database.py file: {database_py_file}")
print(f"Parent: {database_py_file.parent}")
print(f"Parent.parent: {database_py_file.parent.parent}")
print(f"Parent.parent.parent: {database_py_file.parent.parent.parent}")
print(f"Parent.parent.parent.parent: {database_py_file.parent.parent.parent.parent}")

# Calculate the db path
db_path = database_py_file.parent.parent.parent.parent / "goalpath.db"
print(f"Calculated DB path: {db_path}")
print(f"Resolved DB path: {db_path.resolve()}")

# Check if files exist
print(f"DB at calculated path exists: {db_path.exists()}")

correct_path = Path("/mnt/raid_0_drive/mcp_projs/goal-path/goalpath.db")
print(f"DB at correct path exists: {correct_path.exists()}")

# Check current working directory context
import os
print(f"Current working directory: {os.getcwd()}")
