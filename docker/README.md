# Docker Configuration for AI Interviewer Bot

This directory contains the Docker configuration for deploying the AI Interviewer Bot with the new package-based structure.

## 📁 File Structure

```
docker/
├── Dockerfile                      # Multi-stage production Dockerfile
├── docker-compose.yml              # Production Docker Compose
├── docker-compose.development.yml  # Development Docker Compose
└── README.md                       # This file
```

## 🚀 Quick Start

### Production Deployment

1. **Configure environment variables:**
   ```bash
   # Copy and edit environment file
   cp .env.example .env
   nano .env  # Add your API keys
   ```

2. **Deploy using the automated script:**
   ```bash
   ./scripts/deploy/deploy_docker.sh
   ```

3. **Or deploy manually:**
   ```bash
   cd docker
   docker-compose up -d
   ```

### Development Setup

1. **Start development environment:**
   ```bash
   cd docker
   docker-compose -f docker-compose.development.yml up -d --profile development
   ```

2. **Run tests:**
   ```bash
   docker-compose -f docker-compose.development.yml up --profile testing test-runner
   ```

## 🏗️ Multi-Stage Dockerfile

The Dockerfile uses a multi-stage build for optimal production images:

- **Builder Stage**: Compiles dependencies and creates Python wheels
- **Runtime Stage**: Minimal production image with only runtime dependencies

### Key Features:

- ✅ **Package-based installation** using setup.py
- ✅ **Non-root user** for security
- ✅ **Multi-stage build** for smaller images
- ✅ **Health checks** for container monitoring
- ✅ **Proper Python environment** configuration
- ✅ **Volume mounts** for persistent data

## 📦 Package Structure Integration

The Docker configuration is optimized for the new package structure:

```
src/
├── core/          # Core bot functionality
├── handlers/      # Message and voice handlers
└── localization/  # Multi-language support

config/
├── requirements.txt           # Production dependencies
├── requirements_minimal.txt   # Minimal dependencies
└── requirements_new_features.txt  # Extended features

docker/
├── Dockerfile                # Production container
└── docker-compose.yml        # Orchestration
```

### Entry Points

The bot can be started using the package entry points defined in setup.py:

- `interview-bot-enhanced`: Main enhanced bot
- `interview-bot`: Basic bot
- `run-tests`: Test runner

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Telegram bot token |
| `ANTHROPIC_API_KEY` | Yes | - | Claude API key |
| `ASSEMBLYAI_API_KEY` | No | - | Voice processing API key |
| `LOG_LEVEL` | No | INFO | Logging level |
| `CLAUDE_MODEL` | No | claude-3-5-sonnet-20241022 | Claude model to use |

### Volume Mounts

The following directories are mounted for persistence:

- `/app/data/sessions` - Active interview sessions
- `/app/data/completed_sessions` - Completed interviews
- `/app/data/logs` - Application logs

## 📊 Monitoring and Maintenance

### Container Health

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f ai-interviewer-bot

# Check health status
docker inspect --format='{{.State.Health.Status}}' ai-interviewer-bot
```

### Resource Usage

```bash
# Monitor resource usage
docker stats ai-interviewer-bot

# View container metrics
docker exec ai-interviewer-bot cat /proc/meminfo
```

### Scaling

```bash
# Scale horizontally (if load balancer configured)
docker-compose up --scale ai-interviewer-bot=3

# Update configuration
docker-compose up -d --force-recreate
```

## 🧪 Testing

### Build Testing

Run comprehensive build tests:

```bash
./scripts/deploy/test_docker_build.sh
```

### Development Testing

```bash
# Run all tests in container
cd docker
docker-compose -f docker-compose.development.yml up --profile testing test-runner

# Interactive development
docker-compose -f docker-compose.development.yml up -d --profile development
docker exec -it ai-interviewer-bot-dev bash
```

## 🔒 Security

### Security Features:

- ✅ **Non-root execution** - Bot runs as `botuser`
- ✅ **Multi-stage build** - No build tools in production image
- ✅ **Minimal base image** - Python slim image
- ✅ **Read-only mounts** - Source code mounted read-only
- ✅ **Resource limits** - CPU and memory constraints
- ✅ **Health checks** - Container health monitoring

### Security Scanning

```bash
# Scan image for vulnerabilities (requires docker scan)
docker scan ai-interviewer-bot:latest

# Check for non-root execution
docker run --rm ai-interviewer-bot:latest whoami
```

## 🚨 Troubleshooting

### Common Issues

1. **Build fails with "setup.py not found"**
   ```bash
   # Ensure you're in the project root directory
   cd /path/to/project
   docker build -f docker/Dockerfile .
   ```

2. **Package imports fail**
   ```bash
   # Check PYTHONPATH is set correctly
   docker run --rm ai-interviewer-bot:latest python -c "import sys; print(sys.path)"
   ```

3. **Permission errors**
   ```bash
   # Check volume permissions
   docker run --rm -v $(pwd)/data:/app/data ai-interviewer-bot:latest ls -la /app/data
   ```

4. **Container exits immediately**
   ```bash
   # Check logs for startup errors
   docker-compose logs ai-interviewer-bot
   ```

### Debug Mode

For debugging, use the development compose file:

```bash
cd docker
docker-compose -f docker-compose.development.yml up --profile development

# Attach debugger (if configured)
docker exec -it ai-interviewer-bot-dev python -m debugpy --listen 0.0.0.0:5678 -m src.core.bot_enhanced
```

## 🔄 Updates and Rollbacks

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and redeploy
./scripts/deploy/deploy_docker.sh
```

### Rollback Procedure

The deployment script automatically creates backups. To rollback manually:

```bash
# Stop current deployment
docker-compose down

# Restore from backup (created by deploy script)
cp backups/.env_YYYYMMDD_HHMMSS .env

# Start previous version
docker-compose up -d
```

## 📈 Performance Optimization

### Resource Tuning

Edit `docker-compose.yml` to adjust resource limits:

```yaml
deploy:
  resources:
    limits:
      memory: 1G      # Increase for high usage
      cpus: '1.0'     # Adjust based on load
    reservations:
      memory: 512M
      cpus: '0.5'
```

### Image Optimization

- Multi-stage build reduces final image size
- Python wheels cached for faster rebuilds  
- Minimal runtime dependencies
- Build cache optimization with layer ordering

---

For more information, see the main project documentation or contact the development team.