#!/bin/bash
# Monitor Nomad deployments for GoalPath

NOMAD_URL="http://192.168.0.174:4646"

echo "📊 GoalPath Nomad Deployment Status"
echo "Nomad Server: $NOMAD_URL"
echo ""

# Function to check job status
check_job() {
    local job_name="$1"
    local env_name="$2"
    
    echo "🔍 Checking $env_name environment ($job_name)..."
    
    # Get job status
    response=$(curl -s "${NOMAD_URL}/v1/job/${job_name}" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        status=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f\"Status: {data.get('Status', 'Unknown')}\")
    print(f\"Priority: {data.get('Priority', 'Unknown')}\")
    print(f\"Type: {data.get('Type', 'Unknown')}\")
    if 'TaskGroups' in data:
        for tg in data['TaskGroups']:
            print(f\"Task Group: {tg.get('Name', 'Unknown')} - Count: {tg.get('Count', 0)}\")
except:
    print('Failed to parse job data')
")
        echo "$status"
        
        # Get allocations
        allocs=$(curl -s "${NOMAD_URL}/v1/job/${job_name}/allocations" 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$allocs" ]; then
            echo "Allocations:"
            echo "$allocs" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for alloc in data[:3]:  # Show first 3 allocations
        print(f\"  - {alloc.get('ID', 'Unknown')[:8]}... Status: {alloc.get('ClientStatus', 'Unknown')}\")
except:
    print('  Failed to get allocation data')
"
        fi
    else
        echo "❌ Job not found or Nomad unreachable"
    fi
    echo ""
}

# Check both environments
check_job "goalpath-staging" "Staging"
check_job "goalpath-production" "Production"

# Overall Nomad status
echo "🖥️  Overall Nomad Status:"
curl -s "${NOMAD_URL}/v1/status/leader" 2>/dev/null | python3 -c "
import json, sys
try:
    leader = sys.stdin.read().strip('\"')
    print(f'Leader: {leader}')
except:
    print('Could not determine leader')
"
