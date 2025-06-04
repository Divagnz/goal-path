-- GoalPath Complete Database Schema
PRAGMA foreign_keys = ON;

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
    created_by VARCHAR(100) NOT NULL DEFAULT 'system'
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_priority ON projects(priority);

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
    story_points INTEGER,
    estimated_hours DECIMAL(7,2),
    actual_hours DECIMAL(7,2),
    start_date DATE,
    due_date DATE,
    completed_date TIMESTAMP,
    assigned_to VARCHAR(100),
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_parent_task_id ON tasks(parent_task_id);
CREATE INDEX idx_tasks_status ON tasks(status);

-- Goals Table
CREATE TABLE goals (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    parent_goal_id TEXT REFERENCES goals(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    goal_type VARCHAR(20) CHECK (goal_type IN ('long_term', 'medium_term', 'short_term', 'milestone')) DEFAULT 'short_term',
    target_date DATE,
    status VARCHAR(20) CHECK (status IN ('active', 'paused', 'completed', 'cancelled')) DEFAULT 'active',
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Views for common queries
CREATE VIEW project_stats AS
SELECT 
    p.id,
    p.name,
    p.status,
    COUNT(t.id) as total_tasks,
    COUNT(CASE WHEN t.status = 'done' THEN 1 END) as completed_tasks,
    ROUND(
        CASE 
            WHEN COUNT(t.id) > 0 THEN 
                (COUNT(CASE WHEN t.status = 'done' THEN 1 END) * 100.0) / COUNT(t.id)
            ELSE 0 
        END, 2
    ) as completion_percentage
FROM projects p
LEFT JOIN tasks t ON p.id = t.project_id
GROUP BY p.id, p.name, p.status;-- Add missing tables to complete schema

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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reminders Table
CREATE TABLE reminders (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    task_id TEXT REFERENCES tasks(id) ON DELETE CASCADE,
    project_id TEXT REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    reminder_type VARCHAR(20) CHECK (reminder_type IN ('one_time', 'recurring')) DEFAULT 'one_time',
    trigger_datetime TIMESTAMP NOT NULL,
    status VARCHAR(20) CHECK (status IN ('pending', 'acknowledged', 'snoozed', 'cancelled')) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Issues Table
CREATE TABLE issues (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    issue_type VARCHAR(20) CHECK (issue_type IN ('bug', 'feature', 'enhancement', 'question')) DEFAULT 'feature',
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'critical')) DEFAULT 'medium',
    status VARCHAR(20) CHECK (status IN ('triage', 'backlog', 'in_progress', 'resolved', 'closed')) DEFAULT 'triage',
    reporter VARCHAR(100) NOT NULL,
    assignee VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task Comments Table
CREATE TABLE task_comments (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    author VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    comment_type VARCHAR(20) CHECK (comment_type IN ('comment', 'status_change', 'assignment', 'attachment')) DEFAULT 'comment',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project Context Table
CREATE TABLE project_context (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    context_type VARCHAR(20) CHECK (context_type IN ('notes', 'links', 'files', 'settings', 'metadata')) NOT NULL,
    key VARCHAR(100) NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);