-- GoalPath Database Schema (Part 2)
-- Context, Metadata, and Additional Components

-- =============================================================================
-- CONTEXT AND METADATA TABLES
-- =============================================================================

-- Project Context Table
CREATE TABLE project_context (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    context_type VARCHAR(20) CHECK (context_type IN ('notes', 'links', 'files', 'settings', 'metadata')) NOT NULL,
    key VARCHAR(100) NOT NULL,
    value TEXT NOT NULL, -- JSON string for SQLite compatibility
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uq_project_context UNIQUE (project_id, context_type, key)
);

-- Project Context Indexes
CREATE INDEX idx_project_context_project_id ON project_context(project_id);
CREATE INDEX idx_project_context_type ON project_context(context_type);

-- Task Comments Table
CREATE TABLE task_comments (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    author VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    comment_type VARCHAR(20) CHECK (comment_type IN ('comment', 'status_change', 'assignment', 'attachment')) DEFAULT 'comment',
    metadata TEXT, -- JSON string for SQLite compatibility
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task Comments Indexes
CREATE INDEX idx_task_comments_task_id ON task_comments(task_id);
CREATE INDEX idx_task_comments_created_at ON task_comments(created_at);
CREATE INDEX idx_task_comments_type ON task_comments(comment_type);

-- Task Attachments Table
CREATE TABLE task_attachments (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL CHECK (file_size > 0),
    mime_type VARCHAR(100) NOT NULL,
    uploaded_by VARCHAR(100) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task Attachments Indexes
CREATE INDEX idx_task_attachments_task_id ON task_attachments(task_id);
CREATE INDEX idx_task_attachments_uploaded_at ON task_attachments(uploaded_at);

-- =============================================================================
-- ISSUE MANAGEMENT TABLES
-- =============================================================================

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
    promoted_to_task_id TEXT REFERENCES tasks(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Issues Indexes
CREATE INDEX idx_issues_project_id ON issues(project_id);
CREATE INDEX idx_issues_status ON issues(status);
CREATE INDEX idx_issues_priority ON issues(priority);
CREATE INDEX idx_issues_assignee ON issues(assignee);
CREATE INDEX idx_issues_promoted_task ON issues(promoted_to_task_id);

-- =============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =============================================================================

-- Update timestamp triggers for SQLite
CREATE TRIGGER update_projects_updated_at 
    AFTER UPDATE ON projects
    FOR EACH ROW
    BEGIN
        UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_tasks_updated_at 
    AFTER UPDATE ON tasks
    FOR EACH ROW
    BEGIN
        UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_goals_updated_at 
    AFTER UPDATE ON goals
    FOR EACH ROW
    BEGIN
        UPDATE goals SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_sprints_updated_at 
    AFTER UPDATE ON sprints
    FOR EACH ROW
    BEGIN
        UPDATE sprints SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_project_context_updated_at 
    AFTER UPDATE ON project_context
    FOR EACH ROW
    BEGIN
        UPDATE project_context SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER update_issues_updated_at 
    AFTER UPDATE ON issues
    FOR EACH ROW
    BEGIN
        UPDATE issues SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Task Hierarchy View
CREATE VIEW task_hierarchy AS
WITH RECURSIVE task_tree AS (
    -- Root tasks (no parent)
    SELECT 
        id, project_id, parent_task_id, title, status, priority,
        0 as level, title as path
    FROM tasks 
    WHERE parent_task_id IS NULL
    
    UNION ALL
    
    -- Child tasks
    SELECT 
        t.id, t.project_id, t.parent_task_id, t.title, t.status, t.priority,
        tt.level + 1, tt.path || ' > ' || t.title
    FROM tasks t
    INNER JOIN task_tree tt ON t.parent_task_id = tt.id
    WHERE tt.level < 10  -- Prevent infinite recursion
)
SELECT * FROM task_tree;

-- Project Statistics View
CREATE VIEW project_stats AS
SELECT 
    p.id,
    p.name,
    p.status,
    COUNT(t.id) as total_tasks,
    COUNT(CASE WHEN t.status = 'done' THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN t.status IN ('todo', 'in_progress', 'in_review') THEN 1 END) as active_tasks,
    COUNT(CASE WHEN t.status = 'blocked' THEN 1 END) as blocked_tasks,
    ROUND(
        CASE 
            WHEN COUNT(t.id) > 0 THEN 
                (COUNT(CASE WHEN t.status = 'done' THEN 1 END) * 100.0) / COUNT(t.id)
            ELSE 0 
        END, 2
    ) as completion_percentage
FROM projects p
LEFT JOIN tasks t ON p.id = t.project_id
GROUP BY p.id, p.name, p.status;

-- Upcoming Deadlines View
CREATE VIEW upcoming_deadlines AS
SELECT 
    p.name as project_name,
    t.title as task_title,
    t.due_date,
    t.priority,
    t.status,
    CASE 
        WHEN t.due_date < DATE('now') THEN 'overdue'
        WHEN t.due_date <= DATE('now', '+3 days') THEN 'urgent'
        WHEN t.due_date <= DATE('now', '+7 days') THEN 'soon'
        ELSE 'upcoming'
    END as urgency,
    JULIANDAY(t.due_date) - JULIANDAY('now') as days_remaining
FROM tasks t
JOIN projects p ON t.project_id = p.id
WHERE t.due_date IS NOT NULL 
  AND t.status NOT IN ('done', 'cancelled')
  AND t.due_date <= DATE('now', '+30 days')
ORDER BY t.due_date ASC;