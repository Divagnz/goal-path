#!/bin/bash
# GitHub CLI Setup and Workflow Testing Script
# Usage: ./setup-gh-cli.sh

set -e

echo "🚀 Setting up GitHub CLI for GoalPath workflow testing..."

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "📦 Installing GitHub CLI..."
    
    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        if command -v apt &> /dev/null; then
            curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
            sudo apt update && sudo apt install gh
        # RHEL/CentOS
        elif command -v yum &> /dev/null; then
            sudo dnf install -y gh
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install gh
        fi
    fi
else
    echo "✅ GitHub CLI already installed: $(gh --version | head -1)"
fi
# Check authentication
echo "🔐 Checking GitHub authentication..."
if gh auth status &> /dev/null; then
    echo "✅ Already authenticated with GitHub"
    gh auth status
else
    echo "🔑 Please authenticate with GitHub..."
    echo "Choose your preferred authentication method:"
    echo "1. Browser (recommended)"
    echo "2. Token"
    read -p "Enter choice (1 or 2): " auth_choice
    
    if [ "$auth_choice" = "1" ]; then
        gh auth login --web
    else
        gh auth login
    fi
fi

# Verify repository access
echo "📂 Verifying repository access..."
if gh repo view &> /dev/null; then
    echo "✅ Repository access confirmed"
    REPO_INFO=$(gh repo view --json name,owner,url)
    echo "Repository: $(echo $REPO_INFO | jq -r '.owner.login')/$(echo $REPO_INFO | jq -r '.name')"
else
    echo "❌ Cannot access repository. Please check permissions."
    exit 1
fi

# List current workflows
echo "📋 Available workflows:"
gh workflow list

echo "✅ GitHub CLI setup complete!"
echo ""
echo "🎯 Quick commands to get started:"
echo "  gh workflow list                    # List all workflows"
echo "  gh run list                         # List recent workflow runs"
echo "  gh workflow run ci.yml              # Trigger CI workflow"
echo "  gh run watch                        # Watch latest run"
echo "  ./validate-workflows.sh             # Validate workflow syntax"
