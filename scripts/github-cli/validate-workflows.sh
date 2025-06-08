#!/bin/bash
# Workflow Validation and Testing Script
# Usage: ./validate-workflows.sh

set -e

echo "🔍 Validating GitHub Actions workflows..."

WORKFLOW_DIR=".github/workflows"

if [ ! -d "$WORKFLOW_DIR" ]; then
    echo "❌ Workflow directory not found: $WORKFLOW_DIR"
    exit 1
fi

# Function to validate YAML syntax
validate_yaml() {
    local file="$1"
    echo "📄 Validating $file..."
    
    # Check YAML syntax using python
    if python3 -c "
import yaml
import sys
try:
    with open('$file', 'r') as f:
        yaml.safe_load(f)
    print('✅ YAML syntax valid')
except yaml.YAMLError as e:
    print(f'❌ YAML syntax error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error reading file: {e}')
    sys.exit(1)
" 2>/dev/null; then
        echo "✅ $file: YAML syntax valid"
    else
        echo "❌ $file: YAML syntax invalid"
        return 1
    fi
}
# Function to check workflow with GitHub CLI
check_workflow_github() {
    local file="$1"
    local workflow_name=$(basename "$file" .yml)
    
    echo "🔍 Checking $workflow_name with GitHub CLI..."
    
    # Try to get workflow info
    if gh workflow view "$workflow_name" &> /dev/null; then
        echo "✅ $workflow_name: GitHub recognizes workflow"
        
        # Show basic info
        gh workflow view "$workflow_name" --json name,state,url | jq -r '
        "Name: " + .name,
        "State: " + .state,
        "URL: " + .url
        ' 2>/dev/null || echo "ℹ️  Workflow info available"
    else
        echo "⚠️  $workflow_name: Not found on GitHub (may be new)"
    fi
}

# Validate all workflow files
VALIDATION_FAILED=0

echo "📂 Found workflows in $WORKFLOW_DIR:"
ls -la "$WORKFLOW_DIR"/*.yml 2>/dev/null || {
    echo "❌ No workflow files found"
    exit 1
}

echo ""

for workflow in "$WORKFLOW_DIR"/*.yml; do
    if [ -f "$workflow" ]; then
        echo "=================================="
        if ! validate_yaml "$workflow"; then
            VALIDATION_FAILED=1
        fi
        
        check_workflow_github "$workflow"
        echo ""
    fi
done

# Final validation result
if [ $VALIDATION_FAILED -eq 0 ]; then
    echo "✅ All workflows passed validation!"
    exit 0
else
    echo "❌ Some workflows failed validation"
    exit 1
fi
# Function to check workflow with GitHub CLI
check_workflow_github() {
    local file="$1"
    local workflow_name=$(basename "$file" .yml)
    
    echo "🔍 Checking $workflow_name with GitHub CLI..."
    
    # Try to get workflow info
    if gh workflow view "$workflow_name" &> /dev/null; then
        echo "✅ $workflow_name: GitHub recognizes workflow"
        
        # Show basic info
        gh workflow view "$workflow_name" --json name,state,url | jq -r '
        "Name: " + .name,
        "State: " + .state,
        "URL: " + .url
        ' 2>/dev/null || echo "ℹ️  Workflow info available"
    else
        echo "⚠️  $workflow_name: Not found on GitHub (may be new)"
    fi
}

# Validate all workflow files
VALIDATION_FAILED=0

echo "📂 Found workflows in $WORKFLOW_DIR:"
ls -la "$WORKFLOW_DIR"/*.yml 2>/dev/null || {
    echo "❌ No workflow files found"
    exit 1
}

echo ""

for workflow in "$WORKFLOW_DIR"/*.yml; do
    if [ -f "$workflow" ]; then
        echo "=================================="
        if ! validate_yaml "$workflow"; then
            VALIDATION_FAILED=1
        fi
        
        check_workflow_github "$workflow"
        echo ""
    fi
done
# Final validation result
if [ $VALIDATION_FAILED -eq 0 ]; then
    echo "✅ All workflows passed validation!"
    exit 0
else
    echo "❌ Some workflows failed validation"
    exit 1
fi