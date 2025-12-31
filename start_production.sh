#!/bin/bash

# Production startup script for ML Learner Flask application
# This script starts the Flask app using Gunicorn in production mode

# Exit on any error
set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

# Change to backend directory
cd "$BACKEND_DIR"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Set production environment variables
export FLASK_ENV=production
export SECRET_KEY=${SECRET_KEY:-"change-this-in-production-to-a-secure-random-key"}

# Database configuration
export USE_SQLITE=false
export DATABASE_USER=${DATABASE_USER:-"ml_user"}
export DATABASE_PASSWORD=${DATABASE_PASSWORD:-"your_secure_password"}
export DATABASE_HOST=${DATABASE_HOST:-"localhost"}
export DATABASE_PORT=${DATABASE_PORT:-"3306"}
export DATABASE_NAME=${DATABASE_NAME:-"ml_learner"}

# Server configuration
export PORT=${PORT:-8000}
export HOST=${HOST:-"0.0.0.0"}

# Number of workers (recommended: 2 * CPU cores + 1)
WORKERS=${WORKERS:-3}

echo "Starting ML Learner Flask application in production mode..."
echo "Workers: $WORKERS"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Database: $DATABASE_NAME@$DATABASE_HOST:$DATABASE_PORT"

# Start Gunicorn with production settings
exec gunicorn \
    --bind "$HOST:$PORT" \
    --workers $WORKERS \
    --worker-class sync \
    --worker-timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance \
    app:create_app()

# Note: This script should be run by systemd or a process manager
# Do not run directly unless for testing purposes
