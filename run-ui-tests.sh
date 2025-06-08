#!/bin/bash

# GoalPath UI Test Runner
# Runs Selenium-based UI tests for the GoalPath application

set -e

echo "🚀 Starting GoalPath UI Tests with Selenium..."

# Create reports directory
mkdir -p reports

# Check if Chrome is available
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo "⚠️  Chrome not found. Installing chromium..."
    sudo apt-get update && sudo apt-get install -y chromium-browser
fi

echo "📋 Running UI smoke tests..."
uv run pytest tests/ui/test_smoke.py -v --tb=short

echo "🔍 Running comprehensive UI tests..."
uv run pytest tests/ui/ -v --tb=short --html=reports/ui-tests-report.html --self-contained-html

echo "✅ UI tests completed!"
echo "📊 Test report available at: reports/ui-tests-report.html"
