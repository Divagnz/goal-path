# GoalPath Database Schema

This directory contains the complete database schema and related files for the GoalPath project management system.

## Files Overview

### Core Schema Files
- **`schema.sql`** - Main database schema with core tables (projects, tasks, goals, etc.)
- **`schema_part2.sql`** - Additional schema components (context, metadata, triggers, views)
- **`sample_data.sql`** - Sample data for development and testing
- **`useful_queries.sql`** - Common queries for development and debugging

### Scripts
- **`init_db.py`** - Database initialization script (executable)
- **`test_schema.py`** - Schema validation and testing script

## Database Structure

### Core Tables (13 total)
1. **projects** - Main project entities
2. **tasks** - Hierarchical task management with parent-child relationships
3. **task_dependencies** - Task dependency mapping (blocks, relates to, etc.)
4. **goals** - Goal hierarchy and progress tracking
5. **goal_projects** - Many-to-many relationships between goals and projects
6. **sprints** - Time-boxed iterations for agile development
7. **sprint_tasks** - Many-to-many sprint-task assignments
8. **reminders** - Scheduling and notification system
9. **schedule_events** - Calendar events and deadlines
10. **project_context** - Flexible project metadata storage (JSON)
11. **task_comments** - Task discussion and audit trail
12. **task_attachments** - File attachment references
13. **issues** - Backlog and triage management

### Key Features
- **Hierarchical Tasks**: Unlimited depth task nesting with cycle prevention
- **Goal Progress Tracking**: Weighted project contributions to goals
- **Sprint Management**: Agile sprint planning and execution
- **Flexible Scheduling**: One-time and recurring reminders with JSON patterns
- **Rich Context Storage**: JSON-based metadata for extensibility
- **Data Integrity**: Comprehensive constraints and validation

## Quick Start

### Initialize Database
```bash
# Initialize with sample data (development)
python database/init_db.py

# Initialize without sample data (production)
python database/init_db.py --no-sample-data

# Custom database path
python database/init_db.py --db-path my_goalpath.db
```

### Test Schema
```bash
# Run schema validation tests
python database/test_schema.py

# Verify existing database
python database/init_db.py --verify-only
```

### Common Operations
```bash
# View all projects with statistics
sqlite3 goalpath.db < database/useful_queries.sql

# Manual database inspection
sqlite3 goalpath.db
.tables
.schema projects
```

## Schema Validation

The database includes several validation mechanisms:

### Constraints
- Foreign key relationships with CASCADE/RESTRICT rules
- Check constraints for enum values and business logic
- Unique constraints for preventing duplicates
- Date validation (end_date > start_date)

### Triggers
- Automatic timestamp updates on record modification
- Task hierarchy validation to prevent circular references

### Views
- **project_stats** - Project completion statistics
- **task_hierarchy** - Recursive task tree structure
- **upcoming_deadlines** - Tasks due in next 30 days

## Performance Considerations

### Indexing Strategy
- Primary and foreign key indexes for join performance
- Composite indexes for common filter patterns
- Temporal indexes for date-based queries

### Query Optimization
- Recursive CTEs with depth limits for hierarchy queries
- Efficient goal progress calculation with weighted averages
- Optimized deadline and reminder queries

## Migration Strategy

### Version Control
- Schema changes tracked via numbered migration files
- Rollback procedures for safe schema updates
- Alembic integration for production migrations

### Compatibility
- SQLite for development and small deployments
- PostgreSQL-compatible syntax for production scaling
- UUID primary keys for distributed system support

## Example Queries

### Get Project Statistics
```sql
SELECT * FROM project_stats WHERE status = 'active';
```

### Task Hierarchy for Project
```sql
WITH RECURSIVE task_tree AS (
    SELECT id, title, parent_task_id, 0 as level
    FROM tasks 
    WHERE project_id = ? AND parent_task_id IS NULL
    UNION ALL
    SELECT t.id, t.title, t.parent_task_id, tt.level + 1
    FROM tasks t
    INNER JOIN task_tree tt ON t.parent_task_id = tt.id
    WHERE tt.level < 10
)
SELECT * FROM task_tree ORDER BY level;
```

### Upcoming Deadlines
```sql
SELECT * FROM upcoming_deadlines WHERE urgency IN ('urgent', 'overdue');
```

## Development Notes

- Use `init_db.py` for clean database setup during development
- Run `test_schema.py` after schema changes to validate integrity
- Check `useful_queries.sql` for common query patterns
- Sample data provides realistic test scenarios for development

For questions or issues with the database schema, refer to the main project documentation or create an issue in the project repository.
