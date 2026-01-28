#!/bin/bash
# ===========================================
# Randol's Marketing Platform - One-Click Setup
# Cross-platform setup script (macOS/Linux)
# ===========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emoji support
CHECKMARK="✓"
CROSS="✗"
ARROW="→"
ROCKET="🚀"
GEAR="⚙️"
KEY="🔑"
DATABASE="🗄️"
PACKAGE="📦"

# Print banner
print_banner() {
    echo ""
    echo -e "${RED}"
    echo "  ██████╗  █████╗ ███╗   ██╗██████╗  ██████╗ ██╗     ███████╗"
    echo "  ██╔══██╗██╔══██╗████╗  ██║██╔══██╗██╔═══██╗██║     ██╔════╝"
    echo "  ██████╔╝███████║██╔██╗ ██║██║  ██║██║   ██║██║     ███████╗"
    echo "  ██╔══██╗██╔══██║██║╚██╗██║██║  ██║██║   ██║██║     ╚════██║"
    echo "  ██║  ██║██║  ██║██║ ╚████║██████╔╝╚██████╔╝███████╗███████║"
    echo "  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚══════╝╚══════╝"
    echo -e "${NC}"
    echo -e "${CYAN}  Agentic Social Media Marketing Platform${NC}"
    echo -e "${YELLOW}  One-Click Setup Wizard${NC}"
    echo ""
}

# Print step
print_step() {
    echo -e "${BLUE}${ARROW} $1${NC}"
}

# Print success
print_success() {
    echo -e "${GREEN}${CHECKMARK} $1${NC}"
}

# Print warning
print_warning() {
    echo -e "${YELLOW}! $1${NC}"
}

# Print error
print_error() {
    echo -e "${RED}${CROSS} $1${NC}"
}

# Check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."

    local missing=()

    if ! command_exists python3; then
        missing+=("Python 3.11+")
    else
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [[ $(echo "$PYTHON_VERSION < 3.9" | bc -l) -eq 1 ]]; then
            missing+=("Python 3.11+ (found $PYTHON_VERSION)")
        fi
    fi

    if ! command_exists node; then
        missing+=("Node.js 18+")
    else
        NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
        if [[ $NODE_VERSION -lt 18 ]]; then
            missing+=("Node.js 18+ (found v$NODE_VERSION)")
        fi
    fi

    if ! command_exists npm; then
        missing+=("npm")
    fi

    if ! command_exists git; then
        missing+=("Git")
    fi

    if [ ${#missing[@]} -gt 0 ]; then
        print_error "Missing prerequisites:"
        for item in "${missing[@]}"; do
            echo "  - $item"
        done
        echo ""
        echo "Please install the missing prerequisites and try again."
        exit 1
    fi

    print_success "All prerequisites satisfied"
}

# Create .env file
create_env_file() {
    print_step "Setting up environment variables..."

    if [ -f .env ]; then
        read -p "  .env file exists. Overwrite? (y/N): " overwrite
        if [[ ! $overwrite =~ ^[Yy]$ ]]; then
            print_warning "Keeping existing .env file"
            return
        fi
    fi

    cp .env.example .env

    echo ""
    echo -e "${KEY} ${CYAN}API Key Configuration${NC}"
    echo "  Enter your API keys (press Enter to skip and configure later)"
    echo ""

    # OpenAI
    read -p "  OpenAI API Key (required for AI features): " openai_key
    if [ -n "$openai_key" ]; then
        sed -i.bak "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$openai_key|" .env
    fi

    # MongoDB
    read -p "  MongoDB URI (or press Enter for local): " mongodb_uri
    if [ -n "$mongodb_uri" ]; then
        sed -i.bak "s|MONGODB_URI=.*|MONGODB_URI=$mongodb_uri|" .env
    else
        sed -i.bak "s|MONGODB_URI=.*|MONGODB_URI=mongodb://localhost:27017/randols_marketing|" .env
    fi

    # Generate secrets
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")

    sed -i.bak "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
    sed -i.bak "s|JWT_SECRET_KEY=.*|JWT_SECRET_KEY=$JWT_SECRET|" .env

    rm -f .env.bak

    print_success "Environment file configured"
}

# Setup backend
setup_backend() {
    print_step "${PACKAGE} Setting up backend..."

    cd backend

    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi

    # Activate and install dependencies
    source venv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt -q

    # Download NLTK data
    python3 -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)" 2>/dev/null || true

    deactivate
    cd ..

    print_success "Backend setup complete"
}

# Setup frontend
setup_frontend() {
    print_step "${PACKAGE} Setting up frontend..."

    cd frontend
    npm install --silent
    cd ..

    print_success "Frontend setup complete"
}

# Setup Docker (optional)
setup_docker() {
    if command_exists docker && command_exists docker-compose; then
        read -p "  Docker detected. Setup with Docker? (y/N): " use_docker
        if [[ $use_docker =~ ^[Yy]$ ]]; then
            print_step "Starting Docker services..."
            docker-compose up -d mongodb redis
            print_success "Docker services started"
            return 0
        fi
    fi
    return 1
}

# Initialize database
init_database() {
    print_step "${DATABASE} Initializing database..."

    cd backend
    source venv/bin/activate

    if python3 -c "from pymongo import MongoClient; MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000).admin.command('ismaster')" 2>/dev/null; then
        python3 scripts/init_db.py --samples 2>/dev/null || print_warning "Database init skipped (run manually if needed)"
        print_success "Database initialized"
    else
        print_warning "MongoDB not running. Database initialization skipped."
        echo "  Start MongoDB and run: cd backend && source venv/bin/activate && python scripts/init_db.py"
    fi

    deactivate
    cd ..
}

# Print completion message
print_completion() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${ROCKET} ${GREEN}Setup Complete!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${CYAN}Quick Start Commands:${NC}"
    echo ""
    echo "  ${YELLOW}Start Development Servers:${NC}"
    echo "    make dev"
    echo ""
    echo "  ${YELLOW}Or start separately:${NC}"
    echo "    Backend:  cd backend && source venv/bin/activate && python main.py"
    echo "    Frontend: cd frontend && npm run dev"
    echo ""
    echo "  ${YELLOW}With Docker:${NC}"
    echo "    docker-compose up"
    echo ""
    echo -e "${CYAN}Access Points:${NC}"
    echo "  Frontend:  http://localhost:3000"
    echo "  Backend:   http://localhost:5000"
    echo "  API Docs:  http://localhost:5000/api/v1/docs"
    echo ""
    echo -e "${CYAN}Next Steps:${NC}"
    echo "  1. Configure your social media API keys in .env"
    echo "  2. Set up MongoDB (local or Atlas)"
    echo "  3. Run: make dev"
    echo ""
    echo -e "${PURPLE}Documentation: https://github.com/randols/platform#readme${NC}"
    echo ""
}

# Main execution
main() {
    print_banner

    check_prerequisites
    echo ""

    create_env_file
    echo ""

    setup_backend
    setup_frontend
    echo ""

    setup_docker
    init_database

    print_completion
}

# Run main function
main "$@"
