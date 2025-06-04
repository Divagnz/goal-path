# GoalPath Database Schema Design

## 🎯 Overview
This document defines the complete database schema for the GoalPath project management system, focusing on supporting hierarchical tasks, project management, goal tracking, and scheduling features.

---

## 📊 Core Business Rules

### Entity Relationships
1. **Projects** contain multiple **Tasks** in a hierarchical structure
2. **Tasks** can have parent-child relationships (unlimited depth)
3. **Goals** can contain multiple **Projects** and track progress
4. **Sprints** organize **Tasks** within time-boxed iterations
5. **Reminders** can be associated with **Tasks** or **Projects**
6. **Issues** represent backlog items that can be promoted to **Tasks**

### Key Constraints
- Tasks cannot create circular dependencies
- Sprint dates must be valid (end_date > start_date)
- Goal progress is calculated from linked project completion
- Reminders must have either task_id OR project_id (not both)
- Status transitions follow defined business rules

---

## 📋 Database Schema Summary

### Core Tables (8 tables)
1. **projects** - Main project entities
2. **tasks** - Hierarchical task management  
3. **task_dependencies** - Task relationship mapping
4. **goals** - Goal hierarchy and tracking
5. **goal_projects** - Many-to-many goal-project links
6. **sprints** - Time-boxed iterations
7. **sprint_tasks** - Many-to-many sprint-task assignments
8. **reminders** - Scheduling and notification system

### Supporting Tables (5 tables)
9. **schedule_events** - Calendar events and deadlines
10. **project_context** - Flexible project metadata
11. **task_comments** - Task discussion and audit trail
12. **task_attachments** - File storage references
13. **issues** - Backlog and triage management

**Total: 13 tables with comprehensive relationships and constraints**

---

## 🔧 Key Features

### Hierarchical Task Support
- Self-referencing parent_task_id with cycle prevention
- Recursive queries for task trees
- Order management within task groups

### Goal Progress Tracking
- Weighted project contributions to goals
- Automatic progress calculation
- Hierarchical goal structures

### Sprint Management
- Date-bounded iterations
- Task assignment and tracking
- Status and progress monitoring

### Flexible Scheduling
- One-time and recurring reminders
- JSON-based recurrence patterns
- View constraints and acknowledgment tracking

### Rich Context Storage
- JSON-based metadata storage
- Type-categorized context data
- Versioned updates with timestamps

---

This schema provides a robust foundation supporting all GoalPath requirements while maintaining data integrity and performance optimization.