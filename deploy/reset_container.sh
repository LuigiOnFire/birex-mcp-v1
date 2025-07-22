#!/bin/bash

# Clean existing containers, volumes, etc.
# May be necessary to resolve issues with stale containers or volumes
# echo "Cleaning old containers and volumes..."
# docker compose down --volumes --remove-orphans
# docker system prune -a --volumes -f

# Define the desired names and tags
APP_NAME="birex-mcp-v1-app"
APP_TAG="latest"
DB_NAME="birex-mcp-v1-db"
DB_TAG="latest"

# Load app image
echo "Loading app image..."
APP_OUTPUT=$(docker load -i birex-mcp-v1-app.tar)
echo "$APP_OUTPUT"
APP_ID=$(echo "$APP_OUTPUT" | grep -oP '(?<=Loaded image ID: )\S+')
docker tag "$APP_ID" "$APP_NAME:$APP_TAG"
echo "Tagged $APP_ID as $APP_NAME:$APP_TAG"

# Load db image
echo "Loading db image..."
DB_OUTPUT=$(docker load -i birex-mcp-v1-db.tar)
echo "$DB_OUTPUT"
DB_ID=$(echo "$DB_OUTPUT" | grep -oP '(?<=Loaded image ID: )\S+')
docker tag "$DB_ID" "$DB_NAME:$DB_TAG"
echo "Tagged $DB_ID as $DB_NAME:$DB_TAG"

# Show final image list, for debugging
docker images | grep -E "$APP_NAME|$DB_NAME"
read -p "Press any key to continue"

# Start database in background
echo "Starting database container..."
docker compose up -d db

# Wait briefly for DB to be ready
echo "Waiting for database to initialize..."
sleep 10

# Run the app in interactive mode
echo "Running app..."
docker compose run --rm -it app
