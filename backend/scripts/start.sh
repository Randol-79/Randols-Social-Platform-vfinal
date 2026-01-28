#!/bin/bash
#
# Randol's Agentic Marketing Platform - Startup Script
# This script handles environment setup and application startup
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Randol's Marketing Platform Startup${NC}"
echo -e "${GREEN}========================================${NC}"

# Check for .env file
if [ ! -f "$BACKEND_DIR/../.env" ] && [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${YELLOW}Warning: No .env file found${NC}"
    echo "Creating from .env.example..."
    if [ -f "$BACKEND_DIR/../.env.example" ]; then
        cp "$BACKEND_DIR/../.env.example" "$BACKEND_DIR/../.env"
        echo -e "${GREEN}Created .env file - please configure it${NC}"
    fi
fi

# Load environment variables
if [ -f "$BACKEND_DIR/../.env" ]; then
    export $(grep -v '^#' "$BACKEND_DIR/../.env" | xargs)
elif [ -f "$BACKEND_DIR/.env" ]; then
    export $(grep -v '^#' "$BACKEND_DIR/.env" | xargs)
fi

# Set defaults
export FLASK_APP=${FLASK_APP:-"main:app"}
export FLASK_ENV=${FLASK_ENV:-"development"}
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-"5000"}

# Function to check dependencies
check_dependencies() {
    echo -e "\n${YELLOW}Checking dependencies...${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 is required but not installed${NC}"
        exit 1
    fi
    
    # Check pip packages
    cd "$BACKEND_DIR"
    if [ ! -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate venv if not already activated
    if [ -z "$VIRTUAL_ENV" ]; then
        source venv/bin/activate
    fi
    
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    
    echo -e "${GREEN}Dependencies OK${NC}"
}

# Function to check database
check_database() {
    echo -e "\n${YELLOW}Checking database connection...${NC}"
    
    cd "$BACKEND_DIR"
    python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')
from database import db_manager

async def check():
    health = await db_manager.check_health_async()
    if health['status'] != 'healthy':
        print(f'Database: {health}')
        return False
    return True

result = asyncio.run(check())
sys.exit(0 if result else 1)
" && echo -e "${GREEN}Database connection OK${NC}" || {
    echo -e "${RED}Database connection failed${NC}"
    echo "Please check MONGODB_URI in your .env file"
    exit 1
}
}

# Function to initialize database
init_database() {
    echo -e "\n${YELLOW}Initializing database...${NC}"
    cd "$BACKEND_DIR"
    python3 scripts/init_db.py --samples
    echo -e "${GREEN}Database initialized${NC}"
}

# Function to start development server
start_dev() {
    echo -e "\n${GREEN}Starting development server...${NC}"
    echo "Host: $HOST"
    echo "Port: $PORT"
    echo "Debug: true"
    
    cd "$BACKEND_DIR"
    
    # Use Flask's development server with SocketIO
    python3 main.py
}

# Function to start production server
start_prod() {
    echo -e "\n${GREEN}Starting production server...${NC}"
    echo "Host: $HOST"
    echo "Port: $PORT"
    echo "Workers: ${WORKERS:-4}"
    
    cd "$BACKEND_DIR"
    
    # Use Gunicorn with eventlet for production
    gunicorn \
        --worker-class eventlet \
        --workers ${WORKERS:-4} \
        --bind "$HOST:$PORT" \
        --timeout 120 \
        --keep-alive 5 \
        --access-logfile - \
        --error-logfile - \
        --capture-output \
        "main:app"
}

# Function to start worker
start_worker() {
    echo -e "\n${GREEN}Starting scheduler worker...${NC}"
    cd "$BACKEND_DIR"
    python3 workers/scheduler_worker.py
}

# Function to run tests
run_tests() {
    echo -e "\n${YELLOW}Running tests...${NC}"
    cd "$BACKEND_DIR"
    
    # Set test environment
    export FLASK_ENV=testing
    export MOCK_SOCIAL_POSTS=true
    export DEMO_MODE=true
    
    pytest tests/ -v --tb=short
}

# Main command handling
case "${1:-dev}" in
    "dev"|"development")
        check_dependencies
        check_database
        start_dev
        ;;
    "prod"|"production")
        check_dependencies
        check_database
        start_prod
        ;;
    "worker")
        check_dependencies
        check_database
        start_worker
        ;;
    "init")
        check_dependencies
        check_database
        init_database
        ;;
    "test")
        check_dependencies
        run_tests
        ;;
    "check")
        check_dependencies
        check_database
        echo -e "\n${GREEN}All checks passed!${NC}"
        ;;
    *)
        echo "Usage: $0 {dev|prod|worker|init|test|check}"
        echo ""
        echo "Commands:"
        echo "  dev    - Start development server (default)"
        echo "  prod   - Start production server with Gunicorn"
        echo "  worker - Start scheduler background worker"
        echo "  init   - Initialize database with indexes and sample data"
        echo "  test   - Run test suite"
        echo "  check  - Check dependencies and database connection"
        exit 1
        ;;
esac
