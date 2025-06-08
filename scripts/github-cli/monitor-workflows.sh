#!/bin/bash
# Workflow Monitoring and Testing Script
# Usage: ./monitor-workflows.sh

set -e

echo "📊 GoalPath Workflow Monitor & Tester"
echo "======================================"

# Function to show workflow status
show_workflow_status() {
    echo "📋 Workflow Status:"
    gh workflow list --json name,state,url | jq -r '.[] | 
    "• \(.name): \(.state)"'
    echo ""
}

# Function to show recent runs
show_recent_runs() {
    echo "🏃 Recent Workflow Runs (last 10):"
    gh run list --limit 10 --json conclusion,workflowName,createdAt,url | jq -r '.[] |
    "• \(.workflowName): \(.conclusion // "running") (\(.createdAt | split("T")[0]))"'
    echo ""
}

# Function to trigger CI workflow
trigger_ci() {
    echo "🚀 Triggering CI workflow..."
    if gh workflow run ci.yml; then
        echo "✅ CI workflow triggered successfully"
        echo "👀 Watching for completion..."
        sleep 5
        gh run watch $(gh run list --workflow=ci.yml --limit=1 --json databaseId --jq '.[0].databaseId')
    else
        echo "❌ Failed to trigger CI workflow"
    fi
}
# Function to test all workflows
test_workflows() {
    echo "🧪 Testing all workflows..."
    
    # Validate syntax first
    if ./validate-workflows.sh; then
        echo "✅ All workflows have valid syntax"
    else
        echo "❌ Workflow validation failed"
        return 1
    fi
    
    # Show current status
    show_workflow_status
    show_recent_runs
}

# Main menu
case "${1:-menu}" in
    "status")
        show_workflow_status
        ;;
    "runs")
        show_recent_runs
        ;;
    "trigger")
        trigger_ci
        ;;
    "test")
        test_workflows
        ;;
    "watch")
        echo "👀 Watching latest workflow run..."
        gh run watch
        ;;
    "menu"|*)
        echo "🎯 Available commands:"
        echo "  ./monitor-workflows.sh status    # Show workflow status"
        echo "  ./monitor-workflows.sh runs      # Show recent runs"
        echo "  ./monitor-workflows.sh trigger   # Trigger CI workflow"
        echo "  ./monitor-workflows.sh test      # Test all workflows"
        echo "  ./monitor-workflows.sh watch     # Watch latest run"
        echo ""
        echo "📊 Quick Status:"
        show_workflow_status
        ;;
esac