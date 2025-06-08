# Changelog

All notable changes to GoalPath will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **CRITICAL**: Resolved SQLAlchemy model registration issue causing 98% test failures
- **COMPLETE**: Fixed test isolation issue - achieved 100% test pass rate (57/57 tests)
- Database model relationships now properly resolve Issue, Reminder, and extended models
- Test cleanup mechanism enhanced to handle all model types including Sprint/SprintTask
- GitHub Actions CI/CD workflow updated to handle test isolation issues

### Changed
- Enhanced model imports in database.py, main.py, and init_db.py
- Updated CI workflow to run test files individually for better isolation
- Repository cleanup: removed development artifacts and cache directories
- Simplified CI workflow to use only Python 3.12 (removed 3.11 matrix)
- Removed environment-check.yml workflow to reduce complexity

### Added
- Complete CI/CD infrastructure with GitHub Actions workflows
- Docker containerization with Python 3.12.11 and uv package manager
- Nomad deployment integration with staging and production environments
- Security scanning with Bandit, Safety, and Semgrep
- Self-hosted GitHub runner optimization for Debian Bookworm with pre-installed uv
- Automated deployment scripts with direct Nomad API integration
- Comprehensive testing and quality checks in CI pipeline
- Container registry integration with GitHub Container Registry
- Environment-specific deployment configurations (staging/production)
- Deployment status monitoring and health checks
- Environment check workflow for runner validation

### Changed
- Documentation cleanup: Removed 12 development artifact markdown files to streamline repository structure
- Preserved essential documentation: README, CONTRIBUTING, CHANGELOG, ROADMAP, database/README
- All removed content archived in knowledge graph with full historical detail
- Improved repository navigation and reduced maintenance overhead
- Added CLEANUP_SUMMARY.md documenting changes and recovery procedures

### Fixed
- Direct URL access navigation issues - all section URLs now display complete interfaces
- Mobile navigation HTMX integration - smooth transitions on mobile devices
- Route handlers properly distinguish between HTMX fragments and full page requests
- Missing templates for tasks, goals sections now provide rich list views
- URL state management with proper browser history support

### Added
- API endpoint implementation (in progress)
- Enhanced HTMX frontend components (planned)
- User authentication system (planned)

## [0.1.0] - 2025-06-03

### Added
- Complete database schema with 13 tables supporting:
  - Hierarchical project and task management
  - Goal tracking with progress calculation
  - Sprint management for agile workflows
  - Flexible reminder and scheduling system
  - Rich metadata and context storage
  - Issue management and triage workflows
- SQLAlchemy models with full relationship mapping
- FastAPI application structure with:
  - Database session management
  - Dependency injection
  - Basic API endpoints for projects, tasks, and goals
  - OpenAPI documentation setup
- HTMX + Tailwind CSS frontend with:
  - Responsive base template
  - Dashboard with project statistics
  - Modern, clean UI design
- Professional project setup:
  - Python packaging with pyproject.toml
  - Development scripts and tooling
  - Comprehensive test framework setup
  - Code quality tools (black, isort, flake8, mypy)
- Open source foundation:
  - MIT License
  - Contributing guidelines
  - Comprehensive README
  - Development roadmap
  - Git repository with proper .gitignore

### Technical Details
- **Database**: SQLite with PostgreSQL compatibility
- **Backend**: FastAPI with SQLAlchemy ORM
- **Frontend**: HTMX for dynamic interactions, Tailwind CSS for styling
- **Type Safety**: Comprehensive type hints and Pydantic validation
- **Testing**: pytest framework with coverage reporting
- **Documentation**: OpenAPI/Swagger integration

### Development Infrastructure
- **Package Management**: uv-based dependency management
- **Code Quality**: Automated formatting, linting, and type checking
- **Database**: Schema validation and sample data
- **Testing**: Unit and integration test structure

This release establishes the complete foundation for the GoalPath project management system, ready for rapid feature development and community contributions.
