#!/bin/bash
# Local CI Workflow Simulation
# Simulates the enhanced CI workflow to identify potential issues

set -e

echo "🧪 GoalPath CI Workflow Simulation"
echo "=================================="
echo "Simulating the enhanced CI workflow locally..."
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Not in GoalPath project directory"
    exit 1
fi

echo "📂 Project directory: $(pwd)"
echo ""

# Simulate uv setup check
echo "🔧 Step 1: Checking uv setup..."
if command -v uv &> /dev/null; then
    echo "✅ uv found: $(uv --version)"
else
    echo "❌ uv not found in PATH"
    if [ -f "/home/diva/.local/bin/uv" ]; then
        echo "✅ Found uv at /home/diva/.local/bin/uv"
        UV_CMD="/home/diva/.local/bin/uv"
    else
        echo "❌ uv not found - workflow would fail here"
        exit 1
    fi
fi

# Use UV_CMD if set, otherwise use uv from PATH
UV=${UV_CMD:-uv}

echo ""

# Simulate Python setup
echo "🐍 Step 2: Checking Python versions..."
for version in "3.11" "3.12"; do
    if command -v python$version &> /dev/null; then
        echo "✅ Python $version: $(python$version --version)"
    else
        echo "⚠️  Python $version not found - matrix job would fail"
    fi
done
echo ""

# Simulate dependency installation
echo "📦 Step 3: Installing dependencies..."
echo "Running: $UV sync --dev --frozen"
if $UV sync --dev --frozen; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Dependency installation failed"
    exit 1
fi
echo ""

# Simulate code quality checks
echo "🔍 Step 4: Running code quality checks..."

# Check if ruff is available
echo "Checking ruff..."
if $UV run ruff --version &> /dev/null; then
    echo "✅ ruff available: $($UV run ruff --version)"
    echo "Running ruff check..."
    $UV run ruff check . --output-format=text || echo "⚠️  ruff found issues"
else
    echo "❌ ruff not available - workflow would fail"
fi

# Check black
echo "Checking black..."
if $UV run black --version &> /dev/null; then
    echo "✅ black available: $($UV run black --version)"
    echo "Running black check..."
    $UV run black --check . --diff || echo "⚠️  black found formatting issues"
else
    echo "❌ black not available"
fi

# Check isort
echo "Checking isort..."
if $UV run isort --version &> /dev/null; then
    echo "✅ isort available: $($UV run isort --version)"
    echo "Running isort check..."
    $UV run isort --check-only --diff . || echo "⚠️  isort found import order issues"
else
    echo "❌ isort not available"
fi

# Check mypy
echo "Checking mypy..."
if $UV run mypy --version &> /dev/null; then
    echo "✅ mypy available: $($UV run mypy --version)"
    echo "Running mypy check..."
    $UV run mypy src/goalpath --show-error-codes || echo "⚠️  mypy found type issues"
else
    echo "❌ mypy not available"
fi
echo ""

# Simulate database initialization
echo "🗄️  Step 5: Testing database initialization..."
echo "Testing database setup..."
if $UV run python -c "
from src.goalpath.database import DatabaseManager
db = DatabaseManager('sqlite:///test_simulation.db')
db.create_tables()
print('✅ Test database initialized successfully')
import os
os.remove('test_simulation.db')
print('✅ Test database cleaned up')
" 2>/dev/null; then
    echo "✅ Database initialization works"
else
    echo "❌ Database initialization failed"
fi
echo ""

# Simulate test execution
echo "🧪 Step 6: Running tests..."
echo "Looking for test files..."

test_dirs=("tests" "scripts/testing")
test_found=false

for test_dir in "${test_dirs[@]}"; do
    if [ -d "$test_dir" ]; then
        echo "✅ Found test directory: $test_dir"
        test_found=true
        
        # Count test files
        test_files=$(find "$test_dir" -name "*.py" | wc -l)
        echo "   Test files found: $test_files"
    fi
done

if [ "$test_found" = true ]; then
    echo "Running pytest simulation..."
    if $UV run python -c "import pytest; print('✅ pytest available')" 2>/dev/null; then
        echo "✅ pytest is available"
        # Run a simple test to check if the framework works
        echo "Testing pytest execution..."
        $UV run pytest --version || echo "⚠️  pytest version check failed"
    else
        echo "❌ pytest not available"
    fi
else
    echo "⚠️  No test directories found"
fi
echo ""

# Simulate performance benchmark
echo "🚀 Step 7: Performance benchmark simulation..."
echo "Testing FastAPI import and basic functionality..."
if $UV run python -c "
from src.goalpath.main import app
from fastapi.testclient import TestClient
import time

print('✅ FastAPI app imported successfully')
client = TestClient(app)

# Simple performance test
start = time.time()
try:
    response = client.get('/')
    end = time.time()
    print(f'✅ Root endpoint responded in {(end-start)*1000:.2f}ms')
    print(f'   Status code: {response.status_code}')
except Exception as e:
    print(f'⚠️  Performance test failed: {e}')
" 2>/dev/null; then
    echo "✅ Performance benchmark simulation passed"
else
    echo "❌ Performance benchmark failed"
fi
echo ""

# Summary
echo "📊 Simulation Summary"
echo "===================="
echo "This simulation tested the key components of our enhanced CI workflow:"
echo "✅ uv setup and dependency management"
echo "✅ Code quality tools availability and basic functionality"
echo "✅ Database initialization and cleanup"
echo "✅ Test framework availability"
echo "✅ FastAPI application basic functionality"
echo ""
echo "🎯 Next Steps:"
echo "1. Address any ❌ errors shown above"
echo "2. Install missing dependencies if needed"
echo "3. Fix any code quality issues reported"
echo "4. Ensure all tests pass before pushing"
echo ""
echo "🚀 To run the actual CI workflow:"
echo "   git push origin feature/cicd-nomad-setup"
echo "   # Then monitor with: ./scripts/github-cli/monitor-workflows.sh"