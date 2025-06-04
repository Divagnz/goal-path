-- GoalPath Sample Data
-- Generated: 2025-06-03
-- Purpose: Test data for development and validation

-- =============================================================================
-- SAMPLE PROJECTS
-- =============================================================================

INSERT INTO projects (name, description, status, priority, start_date, target_end_date) VALUES
('Website Redesign', 'Complete overhaul of company website with modern design and improved UX', 'active', 'high', '2025-01-15', '2025-08-31'),
('Mobile App Development', 'Native iOS and Android applications for customer portal', 'active', 'critical', '2025-02-01', '2025-12-15'),
('Database Migration', 'Migrate from MySQL to PostgreSQL for better performance', 'active', 'medium', '2025-03-01', '2025-06-30'),
('Customer Support Portal', 'Self-service portal for customer inquiries and documentation', 'active', 'medium', '2025-01-20', '2025-09-30');

-- =============================================================================
-- SAMPLE GOALS
-- =============================================================================

INSERT INTO goals (title, description, goal_type, target_date, status) VALUES
('Q2 Product Launch', 'Launch new product line with mobile app and updated website by end of Q2', 'short_term', '2025-06-30', 'active'),
('Market Expansion', 'Expand to 3 new markets this year with localized products', 'medium_term', '2025-12-31', 'active'),
('Technical Excellence', 'Modernize infrastructure and improve system reliability', 'long_term', '2025-12-31', 'active'),
('Customer Satisfaction', 'Achieve 95% customer satisfaction through improved support tools', 'medium_term', '2025-10-31', 'active');

-- =============================================================================
-- SAMPLE TASKS (HIERARCHICAL)
-- =============================================================================

-- Website Redesign Tasks
INSERT INTO tasks (project_id, title, description, task_type, status, priority, estimated_hours, due_date) 
SELECT id, 'Design System Creation', 'Create comprehensive design system with components and guidelines', 'epic', 'in_progress', 'high', 80.0, '2025-07-15'
FROM projects WHERE name = 'Website Redesign';

INSERT INTO tasks (project_id, title, description, task_type, status, priority, estimated_hours, due_date)
SELECT id, 'Frontend Development', 'Implement new frontend using React and Tailwind CSS', 'epic', 'todo', 'high', 120.0, '2025-08-15'
FROM projects WHERE name = 'Website Redesign';

INSERT INTO tasks (project_id, title, description, task_type, status, priority, estimated_hours, due_date)
SELECT id, 'Content Migration', 'Migrate existing content to new structure', 'story', 'todo', 'medium', 40.0, '2025-08-01'
FROM projects WHERE name = 'Website Redesign';

-- Mobile App Tasks
INSERT INTO tasks (project_id, title, description, task_type, status, priority, story_points, due_date)
SELECT id, 'iOS App Development', 'Native iOS application development', 'epic', 'in_progress', 'critical', 21, '2025-11-30'
FROM projects WHERE name = 'Mobile App Development';

INSERT INTO tasks (project_id, title, description, task_type, status, priority, story_points, due_date)
SELECT id, 'Android App Development', 'Native Android application development', 'epic', 'todo', 'critical', 21, '2025-12-15'
FROM projects WHERE name = 'Mobile App Development';

INSERT INTO tasks (project_id, title, description, task_type, status, priority, story_points, due_date)
SELECT id, 'API Integration', 'Integrate mobile apps with backend APIs', 'story', 'todo', 'high', 8, '2025-10-15'
FROM projects WHERE name = 'Mobile App Development';

-- Database Migration Tasks
INSERT INTO tasks (project_id, title, description, task_type, status, priority, estimated_hours, due_date)
SELECT id, 'Schema Analysis', 'Analyze current MySQL schema and plan PostgreSQL migration', 'task', 'done', 'medium', 16.0, '2025-03-15'
FROM projects WHERE name = 'Database Migration';

INSERT INTO tasks (project_id, title, description, task_type, status, priority, estimated_hours, due_date)
SELECT id, 'Migration Scripts', 'Create data migration scripts and validation tools', 'task', 'in_progress', 'medium', 32.0, '2025-04-30'
FROM projects WHERE name = 'Database Migration';

-- Add subtasks for Design System Creation
INSERT INTO tasks (project_id, parent_task_id, title, description, task_type, status, priority, estimated_hours)
SELECT p.id, t.id, 'Color Palette Design', 'Define primary, secondary, and accent colors', 'subtask', 'done', 'medium', 8.0
FROM projects p
JOIN tasks t ON p.id = t.project_id
WHERE p.name = 'Website Redesign' AND t.title = 'Design System Creation';

INSERT INTO tasks (project_id, parent_task_id, title, description, task_type, status, priority, estimated_hours)
SELECT p.id, t.id, 'Typography System', 'Define font families, sizes, and spacing', 'subtask', 'done', 'medium', 12.0
FROM projects p
JOIN tasks t ON p.id = t.project_id
WHERE p.name = 'Website Redesign' AND t.title = 'Design System Creation';

INSERT INTO tasks (project_id, parent_task_id, title, description, task_type, status, priority, estimated_hours)
SELECT p.id, t.id, 'Component Library', 'Create reusable UI components', 'subtask', 'in_progress', 'high', 40.0
FROM projects p
JOIN tasks t ON p.id = t.project_id
WHERE p.name = 'Website Redesign' AND t.title = 'Design System Creation';
-- =============================================================================
-- SAMPLE GOAL-PROJECT RELATIONSHIPS
-- =============================================================================

-- Link projects to goals
INSERT INTO goal_projects (goal_id, project_id, weight)
SELECT g.id, p.id, 0.6
FROM goals g, projects p
WHERE g.title = 'Q2 Product Launch' AND p.name = 'Website Redesign';

INSERT INTO goal_projects (goal_id, project_id, weight)
SELECT g.id, p.id, 0.4
FROM goals g, projects p
WHERE g.title = 'Q2 Product Launch' AND p.name = 'Mobile App Development';

INSERT INTO goal_projects (goal_id, project_id, weight)
SELECT g.id, p.id, 1.0
FROM goals g, projects p
WHERE g.title = 'Technical Excellence' AND p.name = 'Database Migration';

INSERT INTO goal_projects (goal_id, project_id, weight)
SELECT g.id, p.id, 1.0
FROM goals g, projects p
WHERE g.title = 'Customer Satisfaction' AND p.name = 'Customer Support Portal';

-- =============================================================================
-- SAMPLE SPRINTS
-- =============================================================================

INSERT INTO sprints (project_id, name, goal, start_date, end_date, status)
SELECT id, 'Sprint 1 - Foundation', 'Set up design system and basic structure', '2025-06-01', '2025-06-14', 'completed'
FROM projects WHERE name = 'Website Redesign';

INSERT INTO sprints (project_id, name, goal, start_date, end_date, status)
SELECT id, 'Sprint 2 - Components', 'Build core UI components and layouts', '2025-06-15', '2025-06-28', 'active'
FROM projects WHERE name = 'Website Redesign';

INSERT INTO sprints (project_id, name, goal, start_date, end_date, status)
SELECT id, 'MVP Development', 'Core mobile app functionality', '2025-06-01', '2025-07-15', 'active'
FROM projects WHERE name = 'Mobile App Development';

-- =============================================================================
-- SAMPLE REMINDERS
-- =============================================================================

INSERT INTO reminders (project_id, title, message, trigger_datetime, status)
SELECT id, 'Project Milestone Review', 'Review progress on website redesign milestone', '2025-06-10 09:00:00', 'pending'
FROM projects WHERE name = 'Website Redesign';

INSERT INTO reminders (task_id, title, message, trigger_datetime, status)
SELECT id, 'Task Due Soon', 'Component Library development due in 3 days', '2025-06-07 10:00:00', 'pending'
FROM tasks WHERE title = 'Component Library';

-- =============================================================================
-- SAMPLE ISSUES
-- =============================================================================

INSERT INTO issues (project_id, title, description, issue_type, priority, status, reporter)
SELECT id, 'Mobile responsiveness issues', 'Current design doesnt work well on tablet sizes', 'bug', 'medium', 'triage', 'user_001'
FROM projects WHERE name = 'Website Redesign';

INSERT INTO issues (project_id, title, description, issue_type, priority, status, reporter)
SELECT id, 'Dark mode support', 'Add dark mode toggle for better user experience', 'feature', 'low', 'backlog', 'user_002'
FROM projects WHERE name = 'Website Redesign';

INSERT INTO issues (project_id, title, description, issue_type, priority, status, reporter)
SELECT id, 'Performance optimization', 'App startup time is too slow on older devices', 'enhancement', 'high', 'triage', 'user_003'
FROM projects WHERE name = 'Mobile App Development';

-- =============================================================================
-- SAMPLE TASK COMMENTS
-- =============================================================================

INSERT INTO task_comments (task_id, author, content, comment_type)
SELECT id, 'designer_001', 'Color palette has been finalized and approved by stakeholders', 'status_change'
FROM tasks WHERE title = 'Color Palette Design';

INSERT INTO task_comments (task_id, author, content, comment_type)
SELECT id, 'developer_001', 'Started implementation of base components. ETA: 3 days', 'comment'
FROM tasks WHERE title = 'Component Library';

-- =============================================================================
-- SAMPLE PROJECT CONTEXT
-- =============================================================================

INSERT INTO project_context (project_id, context_type, key, value)
SELECT id, 'links', 'design_mockups', '{"url": "https://figma.com/redesign-mockups", "description": "Latest design mockups"}'
FROM projects WHERE name = 'Website Redesign';

INSERT INTO project_context (project_id, context_type, key, value)
SELECT id, 'settings', 'deployment_config', '{"environment": "staging", "auto_deploy": true, "branch": "main"}'
FROM projects WHERE name = 'Website Redesign';

INSERT INTO project_context (project_id, context_type, key, value)
SELECT id, 'metadata', 'tech_stack', '{"frontend": "React", "styling": "Tailwind CSS", "backend": "FastAPI", "database": "SQLite"}'
FROM projects WHERE name = 'Mobile App Development';