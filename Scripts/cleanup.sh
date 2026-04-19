#!/bin/bash

echo "Cleaning up Risk Analytics environment..."

cd ../producer-module

# Stop all containers
docker-compose down

# Remove volumes (optional - prompts user)
read -p "Remove data volumes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker volume rm producer-module_timescale_data 2>/dev/null
    echo "✓ Volumes removed"
fi

# Remove orphaned containers
docker container prune -f

echo "✓ Cleanup complete"