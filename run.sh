#!/bin/bash

# AI Interviewer Bot - Run Script
# Provides easy commands for development and deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Setup function
setup() {
    log_info "Setting up AI Interviewer Bot..."
    
    # Check dependencies
    if ! command_exists python3; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    if ! command_exists pip; then
        log_error "pip is required but not installed"
        exit 1
    fi
    
    # Install Python dependencies
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create environment file if it doesn't exist
    if [ ! -f .env ]; then
        log_info "Creating .env file from template..."
        cp .env.example .env
        log_warning "Please edit .env file with your API keys"
    fi
    
    # Create required directories
    log_info "Creating required directories..."
    mkdir -p sessions completed_sessions logs data/{sessions,completed_sessions,logs}
    
    log_success "Setup completed! Please configure .env file with your API keys."
}

# Test function
test() {
    log_info "Running bot tests..."
    
    if [ ! -f .env ]; then
        log_warning ".env file not found. Some tests may fail."
    fi
    
    python3 test_bot.py
    
    if [ $? -eq 0 ]; then
        log_success "All tests passed!"
    else
        log_error "Some tests failed. Check output above."
        exit 1
    fi
}

# Run basic bot
run_basic() {
    log_info "Starting basic AI Interviewer Bot..."
    
    if [ ! -f .env ]; then
        log_error ".env file not found. Run './run.sh setup' first."
        exit 1
    fi
    
    python3 telegram_bot.py
}

# Run enhanced bot
run_enhanced() {
    log_info "Starting enhanced AI Interviewer Bot..."
    
    if [ ! -f .env ]; then
        log_error ".env file not found. Run './run.sh setup' first."
        exit 1
    fi
    
    python3 bot_enhanced.py
}

# Docker build
docker_build() {
    log_info "Building Docker image..."
    
    if ! command_exists docker; then
        log_error "Docker is required but not installed"
        exit 1
    fi
    
    docker build -t ai-interviewer-bot .
    log_success "Docker image built successfully"
}

# Docker run with compose
docker_run() {
    log_info "Starting bot with Docker Compose..."
    
    if ! command_exists docker-compose; then
        log_error "docker-compose is required but not installed"
        exit 1
    fi
    
    if [ ! -f .env ]; then
        log_error ".env file not found. Run './run.sh setup' first."
        exit 1
    fi
    
    # Create data directories
    mkdir -p data/{sessions,completed_sessions,logs}
    
    docker-compose up -d
    log_success "Bot started with Docker Compose"
    log_info "Use 'docker-compose logs -f' to view logs"
}

# Docker stop
docker_stop() {
    log_info "Stopping Docker containers..."
    docker-compose down
    log_success "Containers stopped"
}

# Docker logs
docker_logs() {
    docker-compose logs -f ai-interviewer-bot
}

# Clean function
clean() {
    log_info "Cleaning up temporary files..."
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Remove test artifacts
    rm -f test_report.json
    
    # Clean sessions (with confirmation)
    if [ -d "sessions" ] && [ "$(ls -A sessions)" ]; then
        read -p "Remove all session files? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf sessions/*
            log_info "Session files removed"
        fi
    fi
    
    log_success "Cleanup completed"
}

# Status function
status() {
    log_info "AI Interviewer Bot Status"
    echo "=========================="
    
    # Check if .env exists
    if [ -f .env ]; then
        log_success ".env file exists"
    else
        log_warning ".env file not found"
    fi
    
    # Check required files
    required_files=("telegram_bot.py" "bot_enhanced.py" "config.py" "requirements.txt")
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "$file exists"
        else
            log_error "$file missing"
        fi
    done
    
    # Check directories
    required_dirs=("sessions" "completed_sessions")
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            log_success "$dir directory exists"
        else
            log_warning "$dir directory missing"
        fi
    done
    
    # Check Docker containers
    if command_exists docker-compose; then
        if docker-compose ps | grep -q "ai-interviewer-bot"; then
            log_success "Docker container is running"
        else
            log_info "Docker container is not running"
        fi
    fi
    
    # Check Python dependencies
    if python3 -c "import telegram, anthropic" 2>/dev/null; then
        log_success "Python dependencies installed"
    else
        log_warning "Some Python dependencies missing"
    fi
}

# Development mode
dev() {
    log_info "Starting development mode with auto-reload..."
    
    if ! command_exists watchdog; then
        log_info "Installing watchdog for file monitoring..."
        pip install watchdog
    fi
    
    # Use watchmedo to auto-reload on file changes
    watchmedo auto-restart --patterns="*.py;*.md" --recursive --signal SIGTERM python3 bot_enhanced.py
}

# Show help
show_help() {
    echo "AI Interviewer Bot - Run Script"
    echo "================================"
    echo ""
    echo "Usage: ./run.sh <command>"
    echo ""
    echo "Commands:"
    echo "  setup           - Initial setup and dependency installation"
    echo "  test            - Run all tests"
    echo "  run-basic       - Run basic bot version"
    echo "  run-enhanced    - Run enhanced bot version"
    echo "  docker-build    - Build Docker image"
    echo "  docker-run      - Run with Docker Compose"
    echo "  docker-stop     - Stop Docker containers"
    echo "  docker-logs     - View Docker logs"
    echo "  dev             - Run in development mode with auto-reload"
    echo "  status          - Check system status"
    echo "  clean           - Clean temporary files"
    echo "  help            - Show this help"
    echo ""
    echo "Examples:"
    echo "  ./run.sh setup              # First-time setup"
    echo "  ./run.sh test               # Run tests"
    echo "  ./run.sh run-enhanced       # Start the bot"
    echo "  ./run.sh docker-run         # Run with Docker"
    echo ""
}

# Main command handler
case "$1" in
    setup)
        setup
        ;;
    test)
        test
        ;;
    run-basic)
        run_basic
        ;;
    run-enhanced)
        run_enhanced
        ;;
    docker-build)
        docker_build
        ;;
    docker-run)
        docker_run
        ;;
    docker-stop)
        docker_stop
        ;;
    docker-logs)
        docker_logs
        ;;
    dev)
        dev
        ;;
    status)
        status
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac