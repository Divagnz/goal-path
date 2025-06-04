-- GoalPath Database Schema
-- Generated: 2025-06-03
-- Version: 1.0
-- Database: SQLite (PostgreSQL compatible)

-- Enable foreign key constraints in SQLite
PRAGMA foreign_keys = ON;

-- =============================================================================
-- CORE TABLES
-- =============================================================================

-- Projects Table
CREATE TABLE projects (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    status VARCHAR(20) CHECK (status IN ('active', 'paused', 'completed', 'archived')) DEFAULT 'active',
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'critical')) DEFAULT 'medium',
    start_date DATE,
    target_end_date DATE,
    actual_end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    
    CONSTRAINT chk_project_dates CHECK (
        target_end_date IS NULL OR start_date IS NULL OR target_end_date >= start_date
    ),
    CONSTRAINT chk_actual_end_date CHECK (
        actual_end_date IS NULL OR start_date IS NULL OR actual_end_date >= start_date
    )
);

-- Projects Indexes
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_priority ON projects(priority);
CREATE INDEX idx_projects_created_at ON projects(created_at);
CREATE INDEX idx_projects_target_end_date ON projects(target_end_date);

-- Tasks Table  
CREATE TABLE tasks (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    parent_task_id TEXT REFERENCES tasks(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    task_type VARCHAR(20) CHECK (task_type IN ('epic', 'story', 'task', 'subtask', 'milestone', 'bug')) DEFAULT 'task',
    status VARCHAR(20) CHECK (status IN ('backlog', 'todo', 'in_progress', 'in_review', 'done', 'blocked', 'cancelled')) DEFAULT 'backlog',
    priority VARCHAR(20) CHECK (priority IN ('lowest', 'low', 'medium', 'high', 'highest', 'critical')) DEFAULT 'medium',
    story_points INTEGER CHECK (story_points > 0),
    estimated_hours DECIMAL(7,2) CHECK (estimated_hours >= 0),
    actual_hours DECIMAL(7,2) CHECK (actual_hours >= 0),
    start_date DATE,
    due_date DATE,
    completed_date TIMESTAMP,
    assigned_to VARCHAR(100),
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_task_dates CHECK (
        due_date IS NULL OR start_date IS NULL OR due_date >= start_date
    ),
    CONSTRAINT chk_completed_status CHECK (
        (status = 'done' AND completed_date IS NOT NULL) OR 
        (status != 'done' AND completed_date IS NULL)
    )
);
-- Tasks Indexes
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_parent_task_id ON tasks(parent_task_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_type_status ON tasks(task_type, status);

-- Task Dependencies Table
CREATE TABLE task_dependencies (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    depends_on_task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    dependency_type VARCHAR(20) CHECK (dependency_type IN ('blocks', 'subtask_of', 'related_to')) DEFAULT 'blocks',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_no_self_dependency CHECK (task_id != depends_on_task_id),
    CONSTRAINT uq_task_dependency UNIQUE (task_id, depends_on_task_id)
);

CREATE INDEX idx_task_dependencies_task_id ON task_dependencies(task_id);
CREATE INDEX idx_task_dependencies_depends_on ON task_dependencies(depends_on_task_id);

-- Goals Table
CREATE TABLE goals (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    parent_goal_id TEXT REFERENCES goals(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    goal_type VARCHAR(20) CHECK (goal_type IN ('long_term', 'medium_term', 'short_term', 'milestone')) DEFAULT 'short_term',
    target_date DATE,
    status VARCHAR(20) CHECK (status IN ('active', 'paused', 'completed', 'cancelled')) DEFAULT 'active',
    progress_percentage DECIMAL(5,2) CHECK (progress_percentage >= 0 AND progress_percentage <= 100) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_goals_parent_goal_id ON goals(parent_goal_id);
CREATE INDEX idx_goals_status ON goals(status);
CREATE INDEX idx_goals_target_date ON goals(target_date);
CREATE INDEX idx_goals_type ON goals(goal_type);

-- Goal Projects Table (Many-to-Many)
CREATE TABLE goal_projects (
    goal_id TEXT NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    weight DECIMAL(3,2) CHECK (weight > 0 AND weight <= 1) DEFAULT 1.00,
    PRIMARY KEY (goal_id, project_id)
);

-- Sprints Table
CREATE TABLE sprints (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    goal TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) CHECK (status IN ('planning', 'active', 'completed', 'cancelled')) DEFAULT 'planning',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_sprint_dates CHECK (end_date > start_date)
);

CREATE INDEX idx_sprints_project_id ON sprints(project_id);
CREATE INDEX idx_sprints_status ON sprints(status);
CREATE INDEX idx_sprints_dates ON sprints(start_date, end_date);