-- GoalPath Useful Queries
-- Common queries for testing and development

-- =============================================================================
-- PROJECT QUERIES
-- =============================================================================

-- Get all projects with task statistics
SELECT 
    p.name,
    p.status,
    p.priority,
    COUNT(t.id) as total_tasks,
    COUNT(CASE WHEN t.status = 'done' THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN t.status IN ('todo', 'in_progress', 'in_review') THEN 1 END) as active_tasks,
    ROUND(
        CASE 
            WHEN COUNT(t.id) > 0 THEN 
                (COUNT(CASE WHEN t.status = 'done' THEN 1 END) * 100.0) / COUNT(t.id)
            ELSE 0 
        END, 2
    ) as completion_percentage
FROM projects p
LEFT JOIN tasks t ON p.id = t.project_id
GROUP BY p.id, p.name, p.status, p.priority
ORDER BY p.created_at;

-- =============================================================================
-- TASK HIERARCHY QUERIES
-- =============================================================================

-- Get complete task hierarchy for a specific project
WITH RECURSIVE task_tree AS (
    -- Root tasks (no parent)
    SELECT 
        id, project_id, parent_task_id, title, status, priority, task_type,
        0 as level, 
        title as path,
        id as root_id
    FROM tasks 
    WHERE parent_task_id IS NULL 
      AND project_id = (SELECT id FROM projects WHERE name = 'Website Redesign' LIMIT 1)
    
    UNION ALL
    
    -- Child tasks
    SELECT 
        t.id, t.project_id, t.parent_task_id, t.title, t.status, t.priority, t.task_type,
        tt.level + 1, 
        tt.path || ' > ' || t.title,
        tt.root_id
    FROM tasks t
    INNER JOIN task_tree tt ON t.parent_task_id = tt.id
    WHERE tt.level < 10  -- Prevent infinite recursion
)
SELECT 
    PRINTF('%*s%s', level * 2, '', title) as indented_title,
    status,
    priority,
    task_type,
    level
FROM task_tree 
ORDER BY root_id, level, title;

-- =============================================================================
-- UPCOMING DEADLINES
-- =============================================================================

-- Tasks due in the next 30 days
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

-- =============================================================================
-- GOAL PROGRESS TRACKING
-- =============================================================================

-- Goal progress based on linked projects
SELECT 
    g.title as goal_title,
    g.goal_type,
    g.target_date,
    g.status,
    COUNT(DISTINCT gp.project_id) as linked_projects,
    AVG(
        CASE 
            WHEN p.status = 'completed' THEN 100.0
            WHEN p.status = 'active' THEN 
                COALESCE(
                    (SELECT AVG(CASE WHEN t.status = 'done' THEN 100.0 ELSE 0.0 END)
                     FROM tasks t WHERE t.project_id = p.id), 0.0
                )
            ELSE 0.0
        END * gp.weight
    ) as calculated_progress
FROM goals g
LEFT JOIN goal_projects gp ON g.id = gp.goal_id
LEFT JOIN projects p ON gp.project_id = p.id
GROUP BY g.id, g.title, g.goal_type, g.target_date, g.status
ORDER BY g.target_date;