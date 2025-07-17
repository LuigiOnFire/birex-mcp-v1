 #!/bin/bash
# Clean everything
docker compose down --volumes --remove-orphans
docker system prune -a --volumes -f

# Rebuild fresh
docker compose build --no-cache

# Start database
docker compose up -d db

# Wait briefly for DB to be ready
sleep 10

# Run app interactively
docker compose run --rm -it app