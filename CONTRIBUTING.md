# Contributing to GoalPath

We love your input! We want to make contributing to GoalPath as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Pull Requests

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

### Development Setup

1. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/goalpath.git
   cd goalpath
   ```

2. **Set up development environment**:
   ```bash
   uv sync --dev
   ```

3. **Run tests to verify setup**:
   ```bash
   uv run test
   ```

4. **Start the development server**:
   ```bash
   uv run dev
   ```

### Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting  
- **flake8**: Linting
- **mypy**: Type checking

Run all checks with:
```bash
uv run format     # Format code
uv run lint       # Check linting
uv run type-check # Type checking
```

### Testing

- Write tests for any new functionality
- Ensure all tests pass before submitting PR
- Aim for high test coverage on new code
- Use meaningful test names and descriptions

```bash
uv run test           # Run all tests
uv run test-cov       # Run with coverage report
pytest tests/test_models.py  # Run specific test file
```

## Issues and Feature Requests

We use GitHub issues to track public bugs and feature requests.

### Bug Reports

Great bug reports include:

- A quick summary and/or background
- Steps to reproduce (be specific!)
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening)

### Feature Requests

We welcome feature requests! Please provide:

- Clear description of the feature
- Use case and motivation
- Any implementation ideas (optional)
- Examples of similar features in other tools (optional)

## Architecture Guidelines

### Database Changes

- All schema changes must include migrations
- Update both SQLAlchemy models and raw SQL schema
- Include sample data for new entities
- Document relationships and constraints

### API Design

- Follow RESTful conventions
- Use appropriate HTTP status codes
- Include comprehensive OpenAPI documentation
- Implement proper error handling

### Frontend Development

- Use HTMX for dynamic interactions
- Follow Tailwind CSS conventions
- Ensure responsive design
- Maintain accessibility standards

### Code Organization

- Keep functions and classes focused and small
- Use type hints throughout
- Follow Python naming conventions
- Write clear docstrings

## Project Structure Guidelines

### Adding New Features

1. **Models**: Add SQLAlchemy models in `src/goalpath/models/`
2. **API**: Create routers in `src/goalpath/routers/`
3. **Templates**: Add HTML templates in `src/goalpath/templates/`
4. **Tests**: Add tests in `tests/` mirroring the source structure

### Database Migrations

1. Update SQLAlchemy models
2. Create Alembic migration: `alembic revision --autogenerate -m "Description"`
3. Review and test migration
4. Update sample data if needed

## Release Process

We follow semantic versioning (SemVer):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

## Community Guidelines

### Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code.

### Communication

- Be respectful and inclusive
- Use clear and concise language
- Provide context for your contributions
- Be patient with new contributors

## Getting Help

- Check existing issues and documentation first
- Ask questions in GitHub Discussions
- Join our community chat (link TBD)
- Reach out to maintainers for guidance

## Recognition

Contributors will be recognized in:

- The project README
- Release notes for significant contributions
- Annual contributor acknowledgments

Thank you for contributing to GoalPath! 🎯
