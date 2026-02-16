#!/bin/bash

git pull origin main
docker compose down
docker compose up -d --build

# to make executable
# chmod +x scripts/deploy.sh
# to run executable
# ./deploy.sh