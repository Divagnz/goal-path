# GoalPath MCP Server

This directory contains a Model Context Protocol (MCP) server that exposes GoalPath functionality through direct database access for LLM usage.

## Overview

The MCP server provides comprehensive access to GoalPath's project management functionality through a standardized interface that LLMs can use to:

- Create, read, update, and delete projects, goals, epics, milestones, tasks, and issues
- Query project statistics and progress information
- Manage hierarchical relationships (goals, tasks)
- Handle project-goal linking and task dependencies
- Promote issues to tasks

## Features

### Core Entities
- **Projects**: Full CRUD + statistics
- **Goals**: Full CRUD + hierarchy + progress + project linking  
- **Epics**: Full CRUD + milestone/task relationships
- **Milestones**: Full CRUD + progress tracking
- **Tasks**: Full CRUD + hierarchy + dependencies + status management
- **Issues**: Full CRUD + promotion to tasks

### Key Capabilities
- Hierarchical data management (parent-child relationships)
- Progress tracking and calculation
- Status transitions with automatic timestamps
- Comprehensive filtering and pagination
- Project statistics and analytics
- Dependency management
- Issue promotion workflows

## Installation

1. Install MCP dependencies:
   ```bash
   pip install -r requirements-mcp.txt
   ```

2. The MCP server accesses the database directly and does not require the backend to be running

3. The MCP server is already configured in `.mcp.json` and will be available to Claude Code

## Usage

The MCP server exposes 30+ tools covering all major GoalPath operations:

### Project Management
- `list_projects` - List all projects with filtering
- `get_project` - Get specific project details
- `create_project` - Create new project
- `update_project` - Update existing project
- `delete_project` - Delete project
- `get_project_statistics` - Get project analytics

### Goal Management
- `list_goals` - List goals with filtering
- `get_goal` - Get specific goal details
- `create_goal` - Create new goal
- `update_goal` - Update existing goal
- `delete_goal` - Delete goal (with subgoal handling)
- `get_goal_hierarchy` - Get complete goal tree
- `link_project_to_goal` - Link projects to goals

### Epic Management
- `list_epics` - List epics with filtering
- `get_epic` - Get specific epic details
- `create_epic` - Create new epic
- `update_epic` - Update existing epic
- `delete_epic` - Delete epic

### Milestone Management
- `list_milestones` - List milestones with filtering
- `get_milestone` - Get specific milestone details
- `create_milestone` - Create new milestone (auto-derives project_id)
- `update_milestone` - Update existing milestone
- `delete_milestone` - Delete milestone

### Task Management
- `list_tasks` - List tasks with extensive filtering
- `get_task` - Get specific task details
- `create_task` - Create new task
- `update_task` - Update existing task
- `delete_task` - Delete task (with subtask handling)
- `update_task_status` - Quick status updates
- `get_task_subtasks` - Get task hierarchy

### Issue Management
- `list_issues` - List issues with filtering
- `get_issue` - Get specific issue details
- `create_issue` - Create new issue
- `update_issue` - Update existing issue
- `delete_issue` - Delete issue
- `promote_issue_to_task` - Convert issues to tasks

## Configuration

### Environment Variables
- `GOALPATH_DATABASE_URL`: Optional database URL (defaults to SQLite in the project directory)

### MCP Configuration
The server is automatically configured in `.mcp.json`:
```json
{
  "goalpath-mcp": {
    "command": "/path/to/.venv/bin/python",
    "args": ["/path/to/mcp_server.py"]
  }
}
```

## Data Models

All tools use the same data structures as the GoalPath service layer:

### Projects
```json
{
  "name": "string",
  "description": "string", 
  "status": "string",
  "priority": "string",
  "start_date": "YYYY-MM-DD",
  "target_end_date": "YYYY-MM-DD"
}
```

### Goals
```json
{
  "title": "string",
  "description": "string",
  "goal_type": "string",
  "status": "string",
  "priority": "string",
  "parent_goal_id": "integer",
  "target_date": "YYYY-MM-DD",
  "progress_percentage": "number"
}
```

### Tasks
```json
{
  "title": "string",
  "description": "string",
  "project_id": "integer",
  "milestone_id": "integer",
  "epic_id": "integer", 
  "parent_task_id": "integer",
  "status": "string",
  "task_type": "string",
  "priority": "string",
  "assigned_to": "string",
  "due_date": "YYYY-MM-DD",
  "estimated_hours": "number",
  "actual_hours": "number"
}
```

## Error Handling

The MCP server provides comprehensive error handling:
- Database errors are captured and formatted
- Invalid parameters are validated before service calls
- Business logic validation through service layer
- All errors include descriptive messages

## Testing

To test the MCP server:

1. The MCP server will be automatically available in Claude Code (no backend startup required)

2. Test basic functionality:
   - Create a project: `create_project(name="Test Project")`
   - List projects: `list_projects()`
   - Get project details: `get_project(project_id="project-uuid")`

## Architecture

The MCP server uses FastMCP and follows these patterns:
- FastMCP framework for simplified tool definition
- Direct database access through service layer
- Decorator-based tool registration (@mcp.tool())
- Automatic parameter validation and JSON schema generation
- Clean function-based tool implementations
- Proper database session management with context managers

## Future Enhancements

Potential improvements:
- Authentication integration
- Bulk operations
- Export/import functionality
- Advanced analytics tools
- Custom field support
- Caching layer for improved performance