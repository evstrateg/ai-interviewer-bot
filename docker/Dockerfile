# AI Interviewer Telegram Bot - Multi-stage Dockerfile
# Optimized for new package structure with src/ directories

# Build stage - install dependencies and build package
FROM python:3.11-slim as builder

# Set working directory for build
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy package configuration first for better caching
COPY setup.py .
COPY config/requirements.txt ./config/

# Copy source code
COPY src/ ./src/

# Create wheel for installation
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels .

# Install dependencies to get all wheels
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels -r config/requirements.txt

# Runtime stage - minimal image for running
FROM python:3.11-slim as runtime

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    # Only essential runtime dependencies
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user early
RUN useradd --create-home --shell /bin/bash --uid 1000 botuser

# Copy wheels from builder stage
COPY --from=builder /build/wheels /tmp/wheels

# Install packages from wheels (faster and smaller)
RUN pip install --no-cache-dir --find-links /tmp/wheels telegram-interview-bot \
    && rm -rf /tmp/wheels /root/.cache

# Copy configuration and data directories
COPY config/ ./config/
COPY data/ ./data/
COPY .env.example ./

# Create necessary directories with proper permissions
RUN mkdir -p sessions completed_sessions logs data/sessions data/completed_sessions data/logs \
    && chown -R botuser:botuser /app

# Copy any additional runtime files
COPY prompts/ ./prompts/
COPY docs/ ./docs/

# Switch to non-root user
USER botuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check using the installed package
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Expose port for health checks (optional)
EXPOSE 8080

# Use the entry point from setup.py
CMD ["interview-bot-enhanced"]