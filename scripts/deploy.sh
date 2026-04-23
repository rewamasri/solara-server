#!/bin/bash

#git pull origin main
#docker compose down
#docker compose up -d --build

# to make executable
# chmod +x scripts/deploy.sh
# to run executable
# ./deploy.sh

# set -e

# echo "Pulling latest code..."
# git pull origin main

# echo "Building and starting containers..."
# docker compose -f infrastructure/compose/docker-compose.yml up -d --build

# echo "Deployment complete."

set -e

echo "Pulling latest code..."
# git pull origin main

echo "Building and starting containers..."
docker compose -f infrastructure/compose/docker-compose.yml up -d --build

echo "Waiting for containers to initialise..."
sleep 5

echo "Running integration tests..."
bash scripts/test_deploy.sh

echo "Running pipeline tests..."
bash scripts/test_pipeline.sh
