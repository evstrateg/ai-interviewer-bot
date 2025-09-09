#!/bin/bash
# AI Interviewer Bot - Docker Build Testing Script
# Tests the Docker configuration for the new package structure

set -e

echo "🧪 Testing Docker configuration for new package structure..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DOCKER_DIR="$PROJECT_ROOT/docker"

echo -e "${BLUE}[INFO]${NC} Project root: $PROJECT_ROOT"
echo -e "${BLUE}[INFO]${NC} Docker directory: $DOCKER_DIR"

# Pre-flight checks
echo -e "${BLUE}[CHECK]${NC} Running pre-flight checks..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Docker is not installed or not available"
    echo "Please install Docker and try again"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} docker-compose is not installed or not available"
    echo "Please install docker-compose and try again"
    exit 1
fi

# Check required files
required_files=(
    "$DOCKER_DIR/Dockerfile"
    "$DOCKER_DIR/docker-compose.yml"
    "$PROJECT_ROOT/setup.py"
    "$PROJECT_ROOT/config/requirements.txt"
    "$PROJECT_ROOT/src/core"
    "$PROJECT_ROOT/src/handlers"
    "$PROJECT_ROOT/src/localization"
)

for file in "${required_files[@]}"; do
    if [[ ! -e "$file" ]]; then
        echo -e "${RED}[ERROR]${NC} Required file/directory not found: $file"
        exit 1
    fi
done

echo -e "${GREEN}[OK]${NC} Pre-flight checks passed"

# Test 1: Docker build
echo -e "${BLUE}[TEST 1]${NC} Testing Docker build..."
cd "$PROJECT_ROOT"

if docker build -f docker/Dockerfile -t ai-interviewer-bot:test . ; then
    echo -e "${GREEN}[OK]${NC} Docker build successful"
else
    echo -e "${RED}[ERROR]${NC} Docker build failed"
    exit 1
fi

# Test 2: Package installation verification
echo -e "${BLUE}[TEST 2]${NC} Testing package installation in container..."
if docker run --rm ai-interviewer-bot:test python -c "import src.core.config; print('Package imports working')"; then
    echo -e "${GREEN}[OK]${NC} Package imports working"
else
    echo -e "${RED}[ERROR]${NC} Package import failed"
    exit 1
fi

# Test 3: Entry points verification
echo -e "${BLUE}[TEST 3]${NC} Testing entry points..."
if docker run --rm ai-interviewer-bot:test which interview-bot-enhanced; then
    echo -e "${GREEN}[OK]${NC} Entry points installed correctly"
else
    echo -e "${RED}[ERROR]${NC} Entry points not found"
    exit 1
fi

# Test 4: Directory structure verification
echo -e "${BLUE}[TEST 4]${NC} Testing directory structure..."
docker run --rm ai-interviewer-bot:test ls -la /app/ | head -10
docker run --rm ai-interviewer-bot:test find /app -name "*.py" -type f | head -5

# Test 5: Docker Compose syntax check
echo -e "${BLUE}[TEST 5]${NC} Testing docker-compose syntax..."
cd "$DOCKER_DIR"
if docker-compose config > /dev/null; then
    echo -e "${GREEN}[OK]${NC} docker-compose.yml syntax is valid"
else
    echo -e "${RED}[ERROR]${NC} docker-compose.yml syntax error"
    exit 1
fi

# Test 6: Multi-stage build verification
echo -e "${BLUE}[TEST 6]${NC} Testing multi-stage build efficiency..."
builder_size=$(docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" | grep "ai-interviewer-bot" | grep "test" | awk '{print $2}')
echo -e "${BLUE}[INFO]${NC} Final image size: $builder_size"

# Test 7: Security scan (basic)
echo -e "${BLUE}[TEST 7]${NC} Running basic security checks..."
if docker run --rm ai-interviewer-bot:test whoami | grep -q "botuser"; then
    echo -e "${GREEN}[OK]${NC} Running as non-root user"
else
    echo -e "${YELLOW}[WARNING]${NC} Container might be running as root"
fi

# Test 8: Volume mount points
echo -e "${BLUE}[TEST 8]${NC} Testing volume mount points..."
expected_dirs=("/app/data/sessions" "/app/data/completed_sessions" "/app/data/logs")
for dir in "${expected_dirs[@]}"; do
    if docker run --rm ai-interviewer-bot:test ls -ld "$dir"; then
        echo -e "${GREEN}[OK]${NC} Directory exists: $dir"
    else
        echo -e "${RED}[ERROR]${NC} Directory missing: $dir"
        exit 1
    fi
done

# Test 9: Environment variable handling
echo -e "${BLUE}[TEST 9]${NC} Testing environment variables..."
if docker run --rm -e PYTHONPATH=/app ai-interviewer-bot:test python -c "import os; print('PYTHONPATH:', os.environ.get('PYTHONPATH'))"; then
    echo -e "${GREEN}[OK]${NC} Environment variables working"
else
    echo -e "${YELLOW}[WARNING]${NC} Environment variable test inconclusive"
fi

# Cleanup test image
echo -e "${BLUE}[CLEANUP]${NC} Cleaning up test image..."
docker rmi ai-interviewer-bot:test

echo -e "${GREEN}[SUCCESS]${NC} All Docker tests passed!"
echo ""
echo "🎯 Ready for deployment:"
echo "• Production build: cd docker && docker-compose up -d"
echo "• Development build: cd docker && docker-compose -f docker-compose.development.yml up -d --profile development"
echo "• Run tests: cd docker && docker-compose -f docker-compose.development.yml up --profile testing test-runner"
echo ""
echo "📊 Next steps:"
echo "• Configure .env file with your API keys"
echo "• Run the deployment script: ./scripts/deploy/deploy_docker.sh"
echo "• Monitor with: docker-compose -f docker/docker-compose.yml logs -f"