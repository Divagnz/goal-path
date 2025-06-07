#!/bin/bash
# GitHub Self-Hosted Runner Setup for GoalPath

set -e

# Configuration
RUNNER_NAME="${RUNNER_NAME:-goalpath-runner-$(hostname)}"
RUNNER_LABELS="${RUNNER_LABELS:-self-hosted,goalpath-runner,linux,x64}"
GITHUB_REPO="${GITHUB_REPO:-Divagnz/goal-path}"
RUNNER_VERSION="2.314.1"

echo "🚀 Setting up GitHub Self-Hosted Runner for GoalPath"
echo "Repository: $GITHUB_REPO"
echo "Runner Name: $RUNNER_NAME"
echo "Labels: $RUNNER_LABELS"

# Create runner user
if ! id "runner" &>/dev/null; then
    echo "Creating runner user..."
    sudo useradd -m -s /bin/bash runner
    sudo usermod -aG docker runner
fi

# Create runner directory
RUNNER_DIR="/home/runner/actions-runner"
sudo mkdir -p $RUNNER_DIR
sudo chown runner:runner $RUNNER_DIR

# Download and setup runner
cd $RUNNER_DIR
if [ ! -f "run.sh" ]; then
    echo "Downloading GitHub Actions Runner..."
    sudo -u runner curl -o actions-runner-linux-x64-$RUNNER_VERSION.tar.gz \
        -L https://github.com/actions/runner/releases/download/v$RUNNER_VERSION/actions-runner-linux-x64-$RUNNER_VERSION.tar.gz
    
    sudo -u runner tar xzf actions-runner-linux-x64-$RUNNER_VERSION.tar.gz
    sudo -u runner rm actions-runner-linux-x64-$RUNNER_VERSION.tar.gz
fi

echo "✅ Runner setup complete!"
echo ""
echo "Next steps:"
echo "1. Get a registration token from GitHub:"
echo "   Settings > Actions > Runners > New self-hosted runner"
echo "2. Run the configuration:"
echo "   sudo -u runner ./config.sh --url https://github.com/$GITHUB_REPO --token YOUR_TOKEN --name $RUNNER_NAME --labels $RUNNER_LABELS"
echo "3. Install as service:"
echo "   sudo ./svc.sh install runner"
echo "   sudo ./svc.sh start"
