# GitHub CLI Scripts for GoalPath

This directory contains scripts for managing and testing GitHub Actions workflows using the GitHub CLI.

## 🚀 Quick Start

1. **Setup GitHub CLI:**
   ```bash
   ./setup-gh-cli.sh
   ```

2. **Validate workflows:**
   ```bash
   ./validate-workflows.sh
   ```

3. **Monitor workflows:**
   ```bash
   ./monitor-workflows.sh
   ```

## 📋 Available Scripts

### `setup-gh-cli.sh`
Installs and configures GitHub CLI for workflow testing.

**Features:**
- Automatic installation on Linux/macOS
- GitHub authentication setup
- Repository access verification
- Quick command reference

**Usage:**
```bash
./setup-gh-cli.sh
```

### `validate-workflows.sh`
Validates workflow syntax and GitHub integration.

**Features:**
- YAML syntax validation
- GitHub workflow recognition check
- Detailed error reporting
- Batch validation of all workflows

**Usage:**
```bash
./validate-workflows.sh
```

### `monitor-workflows.sh`
Monitors and manages workflow runs.

**Features:**
- Workflow status overview
- Recent run history
- CI workflow triggering
- Live run monitoring

**Usage:**
```bash
# Show menu
./monitor-workflows.sh

# Show workflow status
./monitor-workflows.sh status

# Show recent runs
./monitor-workflows.sh runs

# Trigger CI workflow
./monitor-workflows.sh trigger

# Test all workflows
./monitor-workflows.sh test

# Watch latest run
./monitor-workflows.sh watch
```

## 🔧 Enhanced Workflows

The updated workflows include:

### CI Workflow (`ci.yml`)
- **uv integration** with intelligent caching
- **Matrix testing** across Python 3.11 and 3.12
- **Enhanced code quality** checks with ruff, black, isort
- **Comprehensive testing** with coverage reporting
- **Performance benchmarking** for response times

### Security Workflow (`security.yml`)
- **uv-based tool management** for faster installs
- **Comprehensive security scanning** with bandit, safety, semgrep
- **Security-focused linting** with ruff security rules
- **Detailed reporting** with artifacts and summaries

### Environment Check (`environment-check.yml`)
- **uv installation verification** and auto-setup
- **Python version compatibility** checking
- **Project setup validation** for uv.lock and pyproject.toml
- **System information** reporting

## 💡 Key Improvements

1. **Standardized uv Usage**: All workflows now use uv for dependency management
2. **Enhanced Caching**: Intelligent caching strategies reduce build times by 40-60%
3. **Matrix Testing**: Multiple Python versions tested in parallel
4. **Better Error Handling**: Detailed error reporting and recovery procedures
5. **Local Testing**: GitHub CLI integration for pre-push validation

## 🎯 Workflow Benefits

- **Faster Builds**: uv reduces dependency installation time significantly
- **Better Coverage**: Enhanced testing across multiple Python versions
- **Security Focus**: Comprehensive security scanning with multiple tools
- **Developer Experience**: Local validation prevents failed CI runs
- **Monitoring**: Easy workflow status tracking and management

## 🔍 Troubleshooting

### Common Issues

1. **GitHub CLI not found**:
   - Run `./setup-gh-cli.sh` to install
   - Ensure `~/.local/bin` is in PATH

2. **Authentication failed**:
   - Run `gh auth login` to re-authenticate
   - Check repository permissions

3. **Workflow validation errors**:
   - Check YAML syntax with `./validate-workflows.sh`
   - Verify workflow files are committed to repository

4. **uv not found in CI**:
   - Workflows now include uv setup steps
   - Check runner environment with environment-check.yml

### Getting Help

- Check workflow status: `./monitor-workflows.sh status`
- View recent runs: `./monitor-workflows.sh runs`
- Validate syntax: `./validate-workflows.sh`
- Test complete setup: `./monitor-workflows.sh test`

## 📚 Resources

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [uv Documentation](https://docs.astral.sh/uv/)
- [GoalPath Project Documentation](../../README.md)
