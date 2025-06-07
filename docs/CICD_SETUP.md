# CI/CD Infrastructure Setup

## Overview
Complete CI/CD infrastructure for GoalPath using GitHub Actions, self-hosted runners, and Nomad deployment.

## Infrastructure Components

### GitHub Actions Workflows
- **`.github/workflows/ci.yml`** - Continuous Integration with testing and quality checks
- **`.github/workflows/cd.yml`** - Continuous Deployment with Docker build and Nomad deployment  
- **`.github/workflows/security.yml`** - Security scanning with Bandit, Safety, and Semgrep

### Nomad Deployment
- **Nomad Server**: `http://192.168.0.174:4646`
- **Staging Environment**: `goalpath-staging` (2 instances, 256 CPU, 512MB RAM)
- **Production Environment**: `goalpath-production` (3 instances, 512 CPU, 1024MB RAM)
- **Health Checks**: HTTP health checks on `/health` endpoint

### Docker Infrastructure
- **Base Image**: Python 3.12.11 slim with uv package manager (pre-installed on runner)
- **Container Registry**: GitHub Container Registry (ghcr.io)
- **Health Checks**: Built-in container health monitoring

### Scripts and Automation
- **`scripts/nomad/deploy.sh`** - Direct Nomad API deployment script
- **`scripts/nomad/status.sh`** - Deployment status monitoring
- **`scripts/testing/`** - Moved test scripts for better organization
- **`scripts/deployment/`** - Deployment utilities

## Workflow Overview

### CI Pipeline (Triggered on PR/Push)
1. **Code Quality**: Ruff linting, Black formatting, MyPy type checking
2. **Testing**: pytest with coverage reporting
3. **Security**: Bandit, Safety, Semgrep security scans
4. **Artifacts**: Coverage reports, security scan results

### CD Pipeline (Triggered on main branch)
1. **Build**: Docker image build and push to GHCR
2. **Deploy Staging**: Automatic deployment to staging environment
3. **Deploy Production**: Manual approval required for production deployment

## Environment Configuration

### Required Secrets
- `GITHUB_TOKEN` - For container registry access (automatically provided)
- `DATABASE_URL` - Production database connection string
- `SECRET_KEY` - Production application secret key

### Environment Variables
- `NOMAD_ADDR` - Nomad server URL (configured as `http://192.168.0.174:4646`)
- `REGISTRY` - Container registry URL (configured as `ghcr.io`)

## Manual Deployment Commands

```bash
# Deploy to staging
IMAGE_TAG=latest ENVIRONMENT=staging ./scripts/nomad/deploy.sh

# Deploy to production  
IMAGE_TAG=latest ENVIRONMENT=production ./scripts/nomad/deploy.sh

# Check deployment status
./scripts/nomad/status.sh
```


## Self-Hosted Runner Configuration
- **Runner Labels**: `[self-hosted, linux]`
- **OS**: Debian Bookworm
- **Python**: 3.12.11 (exact version match)
- **Required Tools**: Docker, uv (pre-installed), curl, git
- **Network Access**: Must reach Nomad server at 192.168.0.174:4646

## Optimizations for Your Environment
- **uv Pre-installed**: No need to install uv in workflows, already available on runner
- **Python 3.12**: Updated all workflows to use latest Python version
- **Direct Nomad API**: Custom deployment scripts using your specific Nomad server
- **Efficient Workflows**: Reduced setup time by leveraging pre-installed tools

This setup provides a complete CI/CD pipeline optimized for your existing infrastructure.
