#!/bin/bash

#git pull origin main
#docker compose down
#docker compose up -d --build

# to make executable
# chmod +x scripts/deploy.sh
# to run executable
# ./deploy.sh

set -e

echo "Pulling latest code..."
#git pull origin main

echo "Building and starting containers..."
docker compose -f infrastructure/compose/docker-compose.yml up -d --build

echo "Deployment complete."
