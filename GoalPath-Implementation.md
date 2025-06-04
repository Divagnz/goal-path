### Full Stack Overview

* **Package Management**: `uv` (using `pyproject.toml` for dependencies and scripts)
* **Python Runtime**: Python 3.11+ using the `uv` ecosystem
* **Backend Framework**: `FastAPI`
* **Frontend Stack**: `HTMX` for dynamic HTML behavior, `Tailwind CSS` for styling
* **Database**: `SQLite` for local-first storage, pluggable to Postgres later
* **Templating**: `Jinja2`
* **Web Server**: `uvicorn` for async ASGI serving

---

### Phase 1: Core Infrastructure and Project Bootstrapping

* Set up `uv`-based Python environment using `pyproject.toml`
* Define tooling commands: `tool install`, `tool run`, for MCP server and dashboard
* Build SQLite schema and bootstrap logic for project-scoped databases
* Implement FastAPI app with core entity models: projects, tasks, context, and reminders
* Serve an HTMX+Tailwind dashboard locally with routing for core entities

---

### Phase 2: Scheduling and Reminder Subsystem

* Implement recurring and one-time scheduling logic
* Add view-time constraints to reminders (`view_after` timestamp)
* Integrate schedule summaries into dashboard views
* Add MCP command support for `SCHEDULE`, `REMIND`, `GET /schedule`, etc.

---

### Phase 3: Task System Expansion

* Support nested tasks with unlimited depth
* Add task types: Epic, Milestone, Subtask
* Introduce `followers`, `comments`, `attachments`, and `status markers`
* Implement task dependency graph (e.g., blocks/blocked-by)
* Full CRUD for task hierarchy and MCP support for `ASSIGN`, `FOLLOW`, `BLOCKS`, `COMMENT`, `ATTACH`

---

### Phase 4: Sprint Management and State Transitions

* Define sprint structure with date ranges
* Support linking tasks to sprints
* Add sprint dashboards with progress bars and filtered task views
* Extend reminders and schedule visibility scoped to sprints

---

### Phase 5: Issue Box and Triage Logic

* Create issue backlog for each project
* Implement prioritization filters and drag-to-promote flows
* Triage from issue pool to sprints or projects

---

### Phase 6: Goal Framework

* Implement long/medium/short-term goals as wrappers for projects
* Allow goals to contain multiple nested goals and projects
* Track progress as a composite metric of children
* Render global timelines showing goal/project/task alignment

---

### Phase 7: Multi-Project View and Interconnected Visualization

* Design "web view" for all projects: graph of task dependencies, milestones, and status
* Aggregate key metrics: active issues, completion ratios, velocity across entities
* Build navigation to traverse goal → project → task → sprint

---

### Phase 8: Agent + LLM Integration

* Build adapters for OpenAI and Ollama
* Add session state context sharing via MCP
* Route queries through agents with MCP command delegation and compact summaries
* Use LLMs to summarize progress, detect misalignments, and recommend actions

---

### Phase 9: Packaging and Distribution

* Finalize tooling commands via `uv` CLI
* Create installable bundles for MCP server and dashboard
* Add system service support (systemd, PM2) for background operation
* Provide initial documentation for setup, deployment, and self-hosting

---

### 📌 Future Epics Backlog

**Epic: Multi-Tenant Support**
Enable secure context isolation and resource scoping per tenant or user profile.

**Epic: Remote Agent Orchestration**
Allow agents to connect over authenticated channels and execute tasks remotely.

**Epic: LLM Reasoning Feedback Loop**
Introduce mechanisms for agents to receive feedback, self-evaluate, and improve prompt outcomes.

**Epic: Plugin System for Custom Commands**
Support pluggable handlers for user-defined commands and protocol extensions.

**Epic: Webhook and Event Bridge**
Emit MCP events to external systems or subscribe to hooks for state sync.

**Epic: Voice Command Interface**
Integrate Whisper-based voice input and real-time command translation.

**Epic: File and Blob Storage**
Attach structured file input/output pipelines to tasks and context.

**Epic: Distributed Project Sync**
Replicate and sync project state across multiple nodes or devices.

---

### 🔁 P2 Epics Backlog

**Epic: Behavioral Patterns and Context Memory**
Track usage patterns, preferences, and decision trends to offer better suggestions and maintain user-specific context over time.

**Epic: Goal Alignment and Value Tracking**
Introduce weighted scoring for tasks and goals to evaluate alignment with overall mission and user-defined values.

**Epic: Strategy Modeling**
Simulate and evaluate alternative execution paths using dependency graphs and predicted constraints.

**Epic: Forecasting and Retrospective Tools**
Add automatic trend tracking, burndown charts, and predictive task completion forecasts for goals and sprints.

**Epic: Reputation and Trust Scoring**
Establish task and user reputation models based on completion quality, punctuality, and reviewer input.

**Epic: Role-driven Access and Views**
Extend the UI and access control model to support stakeholders, collaborators, reviewers, and read-only observers with tailored permissions and dashboards.

