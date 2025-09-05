# AI Interviewer Telegram Bot MVP

Professional knowledge extraction system with 5 different interview styles, Claude Sonnet-4 integration, and comprehensive session management.

## 🚀 Features

- **5 Interview Styles**: Choose from Master, Telegram-Optimized, Conversational, Stage-Specific, or Conversation Management approaches
- **Claude Sonnet-4 Integration**: Advanced AI-powered interviews with structured JSON responses
- **Session Persistence**: Automatic session saving and restoration
- **Error Recovery**: Robust error handling with retry logic and fallback responses
- **Progress Tracking**: Real-time interview progress and stage completion monitoring
- **Metrics Collection**: Built-in analytics and performance monitoring
- **Docker Support**: Containerized deployment with docker-compose

## 📋 Prerequisites

1. **Telegram Bot Token**: Get from [@BotFather](https://t.me/botfather)
2. **Anthropic API Key**: Get from [Anthropic Console](https://console.anthropic.com/)
3. **Python 3.11+** or **Docker**

## ⚡ Quick Start

### Option 1: Docker Deployment (Recommended)

1. **Clone and setup**:
```bash
git clone <repository>
cd ai-interviewer-telegram-bot
cp .env.example .env
```

2. **Configure environment** (edit `.env`):
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

3. **Run with Docker**:
```bash
# Create data directories
mkdir -p data/{sessions,completed_sessions,logs}

# Start the bot
docker-compose up -d

# Check logs
docker-compose logs -f ai-interviewer-bot
```

### Option 2: Local Python Installation

1. **Setup environment**:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your tokens
```

2. **Run the bot**:
```bash
# Basic version
python telegram_bot.py

# Enhanced version with better error handling
python bot_enhanced.py
```

## 🤖 Bot Usage

### Starting an Interview

1. **Start conversation**: Send `/start` to the bot
2. **Choose style**: Select from 5 interview approaches:
   - 🎯 **Master Interviewer**: Comprehensive and systematic
   - 📱 **Telegram Optimized**: Mobile-friendly, concise messages
   - 💬 **Conversational Balance**: Natural flow with systematic coverage
   - 🎪 **Stage Specific**: Detailed approach for each stage
   - 🧠 **Conversation Management**: Advanced recovery and adaptation

3. **Begin interview**: Click "🚀 Begin Interview" and start responding

### Available Commands

- `/start` - Begin new interview
- `/status` - Check current interview progress
- `/reset` - Reset current session
- `/help` - Show help information
- `/metrics` - View bot statistics (enhanced version only)

### Interview Process

The bot follows a structured 9-stage interview process:

1. **Greeting** (3-5 min) - Building rapport
2. **Profiling** (10 min) - Background and experience
3. **Essence** (15 min) - Role philosophy and purpose
4. **Operations** (20 min) - Daily work processes
5. **Expertise Map** (20 min) - Knowledge hierarchy
6. **Failure Modes** (20 min) - Common mistakes and prevention
7. **Mastery** (15 min) - Expert-level insights
8. **Growth Path** (15 min) - Professional development
9. **Wrap Up** (5 min) - Final validation and completion

**Total Duration**: 90-120 minutes

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | - | Telegram bot token from @BotFather |
| `ANTHROPIC_API_KEY` | ✅ | - | Claude API key from Anthropic Console |
| `BOT_USERNAME` | ❌ | - | Bot username for logging |
| `BOT_NAME` | ❌ | AI Interviewer | Display name for the bot |
| `LOG_LEVEL` | ❌ | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FORMAT` | ❌ | text | Log format (text or json) |
| `SESSION_TIMEOUT_MINUTES` | ❌ | 180 | Session timeout in minutes |
| `MAX_CONVERSATION_HISTORY` | ❌ | 100 | Max messages to keep in history |
| `CLAUDE_MODEL` | ❌ | claude-3-5-sonnet-20241022 | Claude model to use |
| `CLAUDE_MAX_TOKENS` | ❌ | 1000 | Max tokens per response |
| `CLAUDE_TEMPERATURE` | ❌ | 0.7 | Response creativity (0.0-1.0) |

### Interview Prompt Variants

The system includes 5 carefully crafted prompt variants:

1. **prompt_v1_master_interviewer.md** - Most comprehensive, systematic approach
2. **prompt_v2_telegram_optimized.md** - Mobile-friendly, concise messaging
3. **prompt_v3_conversational_balanced.md** - Natural flow with structure
4. **prompt_v4_stage_specific.md** - Detailed stage-by-stage approach
5. **prompt_v5_conversation_management.md** - Advanced error handling

## 📊 Monitoring and Analytics

### Built-in Metrics (Enhanced Version)

- **Sessions**: Started, completed, active
- **Messages**: Processed count
- **API Calls**: Total calls, error rate
- **System**: Error counts, performance

### Session Storage

- **Development**: Local file storage in `sessions/` directory
- **Production**: Redis or PostgreSQL support available

### Logging

- **Structured Logging**: JSON format for production analysis
- **Log Rotation**: Automatic log file management
- **Error Tracking**: Comprehensive error logging with stack traces

## 🐳 Docker Deployment

### Basic Deployment

```bash
# Quick start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Production Deployment

```bash
# Include Redis and PostgreSQL
docker-compose --profile production up -d

# Scale bot instances
docker-compose up -d --scale ai-interviewer-bot=3
```

### Docker Configuration

The Docker setup includes:
- **Resource limits**: Memory and CPU constraints
- **Health checks**: Automatic restart on failure
- **Volume mounts**: Persistent data storage
- **Log rotation**: Automatic log management

## 🔍 Troubleshooting

### Common Issues

1. **Bot not responding**:
   ```bash
   # Check logs
   docker-compose logs ai-interviewer-bot
   
   # Restart bot
   docker-compose restart ai-interviewer-bot
   ```

2. **API errors**:
   - Verify `ANTHROPIC_API_KEY` is correct
   - Check API quota and rate limits
   - Review error logs for specific issues

3. **Session issues**:
   ```bash
   # Clear sessions
   rm -rf data/sessions/*
   
   # Restart with clean state
   docker-compose restart
   ```

### Debug Mode

Enable detailed logging:
```bash
# Set environment variable
LOG_LEVEL=DEBUG

# Or in docker-compose.yml
environment:
  - LOG_LEVEL=DEBUG
```

### Performance Issues

1. **High memory usage**:
   - Reduce `MAX_CONVERSATION_HISTORY`
   - Enable session cleanup
   - Monitor active sessions

2. **Slow responses**:
   - Check internet connection
   - Verify Claude API status
   - Review `CLAUDE_MAX_TOKENS` setting

## 🧪 Development

### Local Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Install development tools
pip install pytest pytest-asyncio black flake8

# Run tests
pytest tests/

# Format code
black *.py

# Lint code
flake8 *.py
```

### Adding New Features

1. **New prompt variant**: Add new `.md` file and update `PromptVariant` enum
2. **Additional commands**: Add handlers in `_setup_handlers()` method
3. **Enhanced analytics**: Extend `MetricsCollector` class
4. **Storage backends**: Implement new session storage in `SessionManager`

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Test specific component
pytest tests/test_session_manager.py
```

## 📖 API Documentation

### Session Data Structure

```python
@dataclass
class InterviewSession:
    user_id: int
    username: str
    prompt_variant: PromptVariant
    current_stage: InterviewStage
    stage_completeness: Dict[str, int]
    conversation_history: List[Dict[str, Any]]
    start_time: datetime
    last_activity: datetime
    question_depth: int = 1
    engagement_level: str = "medium"
    examples_collected: int = 0
    key_insights: List[str] = None
```

### JSON Response Format

```json
{
  "interview_stage": "stage_code",
  "response": "interviewer_message",
  "metadata": {
    "question_depth": 1-4,
    "completeness": 0-100,
    "engagement_level": "high|medium|low"
  },
  "internal_tracking": {
    "key_insights": ["insight1", "insight2"],
    "examples_collected": 3,
    "follow_up_needed": ["area1", "area2"],
    "stage_transition_ready": false
  }
}
```

## 🔐 Security Considerations

1. **API Keys**: Never commit tokens to version control
2. **User Data**: Sessions contain personal professional information
3. **Rate Limiting**: Implement appropriate API call limits
4. **Input Validation**: Sanitize user inputs
5. **Logging**: Avoid logging sensitive information

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📞 Support

For issues and questions:
- Check troubleshooting section above
- Review GitHub issues
- Contact maintainers

---

**Note**: This is an MVP implementation. For production use, consider adding authentication, enhanced security measures, and scalability improvements.