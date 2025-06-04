# GoalPath 🎯

**A modern, open-source project management system built with FastAPI and HTMX**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![HTMX](https://img.shields.io/badge/HTMX-1.9+-purple.svg)](https://htmx.org)

## Overview

GoalPath is a comprehensive project management system that helps teams and individuals organize, track, and achieve their goals through effective project and task management. Built with modern web technologies, it offers a responsive, real-time interface powered by HTMX and a robust FastAPI backend.

## ✨ Features

### Core Functionality
- **📊 Project Management**: Create, organize, and track projects with detailed metadata
- **📋 Hierarchical Tasks**: Unlimited depth task nesting with parent-child relationships
- **🎯 Goal Tracking**: Set and monitor progress toward short, medium, and long-term goals
- **🏃‍♂️ Sprint Management**: Agile sprint planning and execution
- **🔔 Smart Reminders**: Flexible scheduling with one-time and recurring reminders
- **📈 Progress Tracking**: Real-time progress calculation and reporting

### Advanced Features
- **🔗 Task Dependencies**: Define and visualize task relationships and blocking dependencies
- **📝 Rich Context**: Flexible metadata storage with notes, links, and file attachments
- **🗂️ Issue Management**: Backlog triage and issue-to-task promotion workflows
- **📅 Schedule Integration**: Calendar views and deadline management
- **📊 Analytics Dashboard**: Project statistics and completion metrics

### Technical Features
- **⚡ Real-time UI**: HTMX-powered dynamic updates without page refreshes
- **🎨 Modern Design**: Tailwind CSS for responsive, beautiful interfaces
- **🗄️ Robust Database**: SQLite with PostgreSQL compatibility for scaling
- **🔧 API-First**: Complete REST API with OpenAPI documentation
- **🧪 Well-Tested**: Comprehensive test suite with high coverage

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/goalpath/goalpath.git
   cd goalpath
   ```

2. **Install dependencies**:
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -e .
   ```

3. **Initialize the database**:
   ```bash
   python -m goalpath.database
   ```

4. **Run the application**:
   ```bash
   # Development mode with auto-reload
   uv run dev

   # Or using uvicorn directly
   uvicorn src.goalpath.main:app --reload
   ```

5. **Open your browser**:
   - Application: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

## 📁 Project Structure

```
goalpath/
├── src/goalpath/              # Main application source
│   ├── models/                # SQLAlchemy database models
│   ├── routers/               # FastAPI route handlers
│   ├── templates/             # Jinja2 HTML templates
│   ├── static/                # CSS, JS, and other static files
│   ├── database.py            # Database configuration
│   └── main.py                # FastAPI application entry point
├── database/                  # Database schema and migrations
├── tests/                     # Test suite
├── docs/                      # Documentation
└── pyproject.toml             # Project configuration
```

## 🗄️ Database Schema

GoalPath uses a comprehensive 13-table database schema designed for flexibility and performance:

- **Core Entities**: Projects, Tasks, Goals
- **Relationships**: Task dependencies, Goal-Project links, Sprint assignments  
- **Scheduling**: Reminders, Calendar events
- **Metadata**: Comments, Attachments, Context storage
- **Management**: Issues, Sprint planning

See [database/README.md](database/README.md) for detailed schema documentation.

## 🛠️ Development

### Setting up for Development

1. **Install development dependencies**:
   ```bash
   uv sync --dev
   ```

2. **Run tests**:
   ```bash
   uv run test
   ```

3. **Code formatting and linting**:
   ```bash
   uv run format    # Format code with black and isort
   uv run lint      # Check code with flake8
   uv run type-check # Type checking with mypy
   ```

4. **Database operations**:
   ```bash
   uv run init-db   # Initialize/reset database
   python database/test_schema.py  # Test database schema
   ```

### Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Documentation

- **[API Documentation](http://localhost:8000/api/docs)**: Interactive API docs (when running)
- **[Database Schema](database/README.md)**: Comprehensive database documentation
- **[Implementation Guide](GoalPath-Implementation-Checklist.md)**: Development checklist and progress
- **[Architecture Overview](IMPLEMENTATION_STATUS.md)**: Current implementation status

## 🧪 Testing

```bash
# Run all tests
uv run test

# Run with coverage
uv run test-cov

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
```

## 🚀 Deployment

### Production Deployment

1. **Set up environment variables**:
   ```bash
   export DATABASE_URL="postgresql://user:pass@localhost/goalpath"  # Optional: Use PostgreSQL
   export SECRET_KEY="your-secret-key"
   ```

2. **Install production dependencies**:
   ```bash
   pip install -e .
   ```

3. **Initialize database**:
   ```bash
   python -m goalpath.database --no-sample-data
   ```

4. **Run with production server**:
   ```bash
   python -m goalpath.main
   # Or use gunicorn for better production performance
   gunicorn src.goalpath.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Docker Deployment

```bash
# Build image
docker build -t goalpath .

# Run container
docker run -p 8000:8000 goalpath
```

## 🤝 Community

- **Issues**: [GitHub Issues](https://github.com/goalpath/goalpath/issues)
- **Discussions**: [GitHub Discussions](https://github.com/goalpath/goalpath/discussions)
- **Contributing**: [Contributing Guidelines](CONTRIBUTING.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI**: For the excellent Python web framework
- **HTMX**: For making dynamic HTML interfaces simple and powerful
- **Tailwind CSS**: For beautiful, utility-first CSS
- **SQLAlchemy**: For robust database ORM capabilities

---

**Built with ❤️ by the GoalPath community**

*GoalPath helps you turn your goals into achievable milestones through effective project management.*
