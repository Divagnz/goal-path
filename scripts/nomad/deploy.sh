#!/bin/bash
# Deploy GoalPath to Nomad via API

set -e

NOMAD_URL="http://192.168.0.174:4646"
IMAGE_TAG="${IMAGE_TAG:-latest}"
ENVIRONMENT="${ENVIRONMENT:-staging}"
JOB_NAME="goalpath-${ENVIRONMENT}"

echo "🚀 Deploying $JOB_NAME with image $IMAGE_TAG"

# Set environment-specific values
if [ "$ENVIRONMENT" = "staging" ]; then
    COUNT=2; CPU=256; MEMORY=512
else
    COUNT=3; CPU=512; MEMORY=1024
fi

# Create job JSON for Nomad API
cat > "/tmp/${JOB_NAME}.json" << EOF
{
  "Job": {
    "ID": "${JOB_NAME}",
    "Name": "${JOB_NAME}",
    "Type": "service",
    "Datacenters": ["dc1"],
    "TaskGroups": [{
      "Name": "web",
      "Count": ${COUNT},
      "Networks": [{"ReservedPorts": [{"Label": "http", "Value": 8000}]}],
      "Services": [{
        "Name": "${JOB_NAME}",
        "PortLabel": "http",
        "Tags": ["${ENVIRONMENT}", "web", "goalpath"],
        "Checks": [{"Type": "http", "Path": "/health", "Interval": 10000000000}]
      }],
      "Tasks": [{
        "Name": "goalpath",
        "Driver": "docker",
        "Config": {"image": "${IMAGE_TAG}", "port_map": [{"http": 8000}]},
        "Env": {
          "DATABASE_URL": "${DATABASE_URL:-sqlite:////app/data/${JOB_NAME}.db}",
          "ENVIRONMENT": "${ENVIRONMENT}",
          "PORT": "8000"
        },
        "Resources": {"CPU": ${CPU}, "MemoryMB": ${MEMORY}}
      }]
    }]
  }
}
EOF

# Deploy via Nomad API
curl -X PUT "${NOMAD_URL}/v1/jobs" -H "Content-Type: application/json" -d @/tmp/${JOB_NAME}.json
echo "✅ Deployment complete!"
