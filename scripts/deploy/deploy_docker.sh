#!/bin/bash
# AI Interviewer Bot - Docker Deployment Script
# Production-ready Docker deployment with health checks and rollback

set -e

echo "🐳 Starting Docker deployment for AI Interviewer Bot..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ai-interviewer-bot"
DOCKER_COMPOSE_FILE="docker/docker-compose.yml"
BACKUP_SUFFIX=$(date +%Y%m%d_%H%M%S)

# Check if we're in the right directory
if [[ ! -f "$DOCKER_COMPOSE_FILE" ]]; then
    echo -e "${RED}[ERROR]${NC} docker-compose.yml not found at $DOCKER_COMPOSE_FILE"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    echo -e "${YELLOW}[WARNING]${NC} .env file not found"
    if [[ -f ".env.example" ]]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${YELLOW}[IMPORTANT]${NC} Please edit .env with your API keys before continuing"
        echo "Press Enter when ready or Ctrl+C to abort..."
        read
    else
        echo -e "${RED}[ERROR]${NC} No .env.example found. Cannot continue."
        exit 1
    fi
fi

# Function to perform health check
health_check() {
    local container_name="$1"
    local max_attempts=30
    local attempt=1
    
    echo -e "${BLUE}[HEALTH]${NC} Waiting for container to be healthy..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec $container_name python -c "import sys; sys.exit(0)" 2>/dev/null; then
            echo -e "${GREEN}[OK]${NC} Container is healthy!"
            return 0
        fi
        
        echo "Attempt $attempt/$max_attempts failed, waiting 5 seconds..."
        sleep 5
        ((attempt++))
    done
    
    echo -e "${RED}[ERROR]${NC} Container failed health check"
    return 1
}

# Function to backup current deployment
backup_deployment() {
    echo -e "${BLUE}[BACKUP]${NC} Creating backup of current deployment..."
    
    # Backup data volumes
    if docker volume ls | grep -q "${PROJECT_NAME}_sessions"; then
        docker run --rm -v ${PROJECT_NAME}_sessions:/source -v $(pwd)/backups:/backup alpine \
            tar czf /backup/sessions_${BACKUP_SUFFIX}.tar.gz -C /source .
    fi
    
    # Backup environment and configs
    mkdir -p backups
    cp .env backups/.env_${BACKUP_SUFFIX}
    
    echo -e "${GREEN}[OK]${NC} Backup completed with suffix: $BACKUP_SUFFIX"
}

# Function to rollback deployment
rollback() {
    echo -e "${YELLOW}[ROLLBACK]${NC} Rolling back deployment..."
    
    # Stop current containers
    docker-compose -f $DOCKER_COMPOSE_FILE down
    
    # Restore from backup
    if [[ -f "backups/.env_${BACKUP_SUFFIX}" ]]; then
        cp backups/.env_${BACKUP_SUFFIX} .env
        echo -e "${GREEN}[OK]${NC} Environment restored from backup"
    fi
    
    # Restore session data if exists
    if [[ -f "backups/sessions_${BACKUP_SUFFIX}.tar.gz" ]]; then
        docker run --rm -v ${PROJECT_NAME}_sessions:/target -v $(pwd)/backups:/backup alpine \
            sh -c "cd /target && tar xzf /backup/sessions_${BACKUP_SUFFIX}.tar.gz"
        echo -e "${GREEN}[OK]${NC} Session data restored from backup"
    fi
    
    echo -e "${YELLOW}[ROLLBACK]${NC} Rollback completed. Please investigate the issue."
}

# Trap to handle rollback on failure
trap 'rollback' ERR

# Pre-deployment checks
echo -e "${BLUE}[CHECK]${NC} Running pre-deployment checks..."

# Check Docker and docker-compose availability
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} docker-compose is not installed or not in PATH"
    exit 1
fi

# Check required environment variables
required_vars=("TELEGRAM_BOT_TOKEN" "ANTHROPIC_API_KEY")
for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env || grep -q "^${var}=$" .env; then
        echo -e "${RED}[ERROR]${NC} Required environment variable $var is missing or empty in .env"
        exit 1
    fi
done

echo -e "${GREEN}[OK]${NC} Pre-deployment checks passed"

# Create backup
backup_deployment

# Build new images
echo -e "${BLUE}[BUILD]${NC} Building Docker images..."
docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache

# Start deployment with zero-downtime strategy
echo -e "${BLUE}[DEPLOY]${NC} Starting new containers..."

# Stop old containers gracefully
docker-compose -f $DOCKER_COMPOSE_FILE down --timeout 30

# Start new containers
docker-compose -f $DOCKER_COMPOSE_FILE up -d

# Wait for containers to be ready
sleep 10

# Perform health check
if ! health_check "${PROJECT_NAME}"; then
    echo -e "${RED}[ERROR]${NC} Deployment failed health check"
    exit 1
fi

# Cleanup old images (keep last 2)
echo -e "${BLUE}[CLEANUP]${NC} Cleaning up old Docker images..."
docker image prune -f

# Final status check
echo -e "${BLUE}[STATUS]${NC} Deployment status:"
docker-compose -f $DOCKER_COMPOSE_FILE ps

echo -e "${GREEN}[SUCCESS]${NC} Deployment completed successfully!"
echo ""
echo "🎯 Post-deployment:"
echo "• Monitor logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
echo "• Check status: docker-compose -f $DOCKER_COMPOSE_FILE ps"
echo "• Scale up: docker-compose -f $DOCKER_COMPOSE_FILE up --scale ai-interviewer-bot=2"
echo "• Backup location: ./backups/*_${BACKUP_SUFFIX}*"
echo ""
echo "📊 Monitoring commands:"
echo "• Resource usage: docker stats"
echo "• Container logs: docker logs ${PROJECT_NAME} -f"
echo "• Health status: docker inspect --format='{{.State.Health.Status}}' ${PROJECT_NAME}"
echo ""
echo -e "${GREEN}🚀 Bot is now running in production!${NC}"

# Disable trap as deployment succeeded
trap - ERR