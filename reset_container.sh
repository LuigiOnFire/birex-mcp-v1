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

# Put some data in
docker compose run -d data_gen_service

# Run app interactively
docker compose run --rm -it app