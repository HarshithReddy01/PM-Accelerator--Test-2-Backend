#!/bin/bash

# Production startup script for Weather App Backend

echo "Starting Weather App Backend in production mode..."

# Load environment variables
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found. Make sure environment variables are set."
fi

# Check if required environment variables are set
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL environment variable is not set"
    exit 1
fi

if [ -z "$GOOGLE_MAPS_API_KEY" ] || [ -z "$GOOGLE_PLACES_API_KEY" ]; then
    echo "Error: Google API keys are not set"
    exit 1
fi

# Initialize database
echo "Initializing database..."
python init_db.py

# Start Gunicorn server
echo "Starting Gunicorn server..."
gunicorn --config gunicorn.conf.py wsgi:app
