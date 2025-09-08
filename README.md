# 🎯 AI Interviewer Telegram Bot

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](docker-compose.yml)
[![Claude AI](https://img.shields.io/badge/Claude-Sonnet--4-orange.svg)](https://anthropic.com)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot%20API-blue.svg)](https://core.telegram.org/bots)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-black.svg)](https://github.com/psf/black)

> **Professional knowledge extraction system** with multiple AI interviewer personalities, advanced session management, and comprehensive analytics. Conduct structured 90-120 minute interviews through Telegram using Claude AI.

## 🌟 Key Highlights

- **🎭 5 AI Interviewer Personalities**: From systematic to conversational approaches
- **🧠 Claude Sonnet-4 Integration**: Advanced AI with structured JSON responses  
- **💾 Intelligent Session Management**: Persistent sessions with automatic recovery
- **📊 Real-time Analytics**: Progress tracking and performance monitoring
- **🌐 Multilingual Support**: Full English and Russian localization
- **🎤 Voice Message Processing**: AssemblyAI speech-to-text integration
- **🐳 Production Ready**: Docker deployment with scaling support
- **🔒 Enterprise Security**: Comprehensive error handling and data protection
- **⚡ High Performance**: Optimized for concurrent users and fast responses

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Architecture Overview](#-architecture-overview)
- [Interview Process](#-interview-process)
- [Deployment Options](#-deployment-options)
- [Configuration](#-configuration)
- [API Usage & Integration](#-api-usage--integration)
- [Performance & Monitoring](#-performance--monitoring)
- [Security Considerations](#-security-considerations)
- [Troubleshooting](#-troubleshooting)
- [Development Guide](#-development-guide)
- [Contributing](#-contributing)
- [Documentation Suite](#-documentation-suite)

## ✨ Features

### 🎭 Multiple AI Interviewer Personalities

Choose from 5 carefully crafted interviewer styles, each optimized for different use cases:

| Style | Best For | Characteristics |
|-------|----------|----------------|
| **🎯 Master Interviewer** | Comprehensive knowledge extraction | Systematic, thorough, structured approach |
| **📱 Telegram Optimized** | Mobile-first interactions | Concise messages, quick responses, chat-friendly |
| **💬 Conversational Balance** | Natural interview flow | Engaging dialogue with systematic coverage |
| **🎪 Stage Specific** | Detailed stage progression | Focused approach for each interview phase |
| **🧠 Conversation Management** | Complex scenarios | Advanced error recovery and adaptation |

### 🚀 Core Capabilities

- **🧠 Claude Sonnet-4 Integration**: Latest AI model with structured JSON responses
- **💾 Persistent Sessions**: Automatic save/restore with timeout handling
- **📊 Progress Tracking**: Real-time stage completion and engagement monitoring
- **🔄 Error Recovery**: Robust handling of API failures and network issues
- **📈 Analytics Engine**: Built-in metrics collection and performance monitoring
- **⚡ Concurrent Users**: Support for multiple simultaneous interviews
- **🎯 Adaptive Questioning**: Dynamic question depth based on user responses
- **🌐 Intelligent Localization**: Automatic language detection and switching
- **🎤 Voice Message Support**: High-quality speech-to-text transcription

### 🛠 Technical Features

- **🐳 Container Ready**: Full Docker support with docker-compose
- **🔧 Flexible Storage**: File system, Redis, or PostgreSQL backends
- **📝 Structured Logging**: JSON logging for production monitoring
- **🧪 Testing Suite**: Comprehensive unit and integration tests
- **🔒 Security First**: Input validation, rate limiting, secure storage
- **📱 Cross-Platform**: Works on Linux, macOS, Windows, and cloud platforms
- **🎵 Audio Processing**: Advanced audio optimization with pydub and ffmpeg
- **🔄 Multi-language APIs**: Comprehensive localization framework

## 📋 Prerequisites

1. **Telegram Bot Token**: Get from [@BotFather](https://t.me/botfather)
2. **Anthropic API Key**: Get from [Anthropic Console](https://console.anthropic.com/)
3. **AssemblyAI API Key** (for voice messages): Get from [AssemblyAI Console](https://www.assemblyai.com/)
4. **Python 3.11+** or **Docker**
5. **FFmpeg** (for audio processing): Required for voice message support

## ⚡ Quick Start

### 🎯 30-Second Setup (Docker - Recommended)

```bash
# Clone and configure
git clone https://github.com/your-username/ai-interviewer-telegram-bot.git
cd ai-interviewer-telegram-bot
cp .env.example .env

# Add your API keys to .env file
echo "TELEGRAM_BOT_TOKEN=your_bot_token" >> .env
echo "ANTHROPIC_API_KEY=your_claude_key" >> .env
echo "ASSEMBLYAI_API_KEY=your_assemblyai_key" >> .env

# Launch immediately
docker-compose up -d
```

🎉 **Your bot is now live!** Start a conversation with your bot on Telegram.

### 🔧 Detailed Setup Options

<details>
<summary><b>🐳 Docker Deployment (Production Ready)</b></summary>

**Advantages**: Isolated environment, automatic restarts, easy scaling, production logging

```bash
# 1. Clone repository
git clone https://github.com/your-username/ai-interviewer-telegram-bot.git
cd ai-interviewer-telegram-bot

# 2. Environment configuration
cp .env.example .env
```

**Edit `.env` with your credentials:**
```bash
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_from_botfather
ANTHROPIC_API_KEY=your_anthropic_api_key
ASSEMBLYAI_API_KEY=your_assemblyai_api_key

# Optional: Advanced configuration
BOT_USERNAME=your_bot_username
LOG_LEVEL=INFO
SESSION_TIMEOUT_MINUTES=180
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Voice Processing Configuration
VOICE_PROCESSING_ENABLED=true
VOICE_MAX_DURATION_SECONDS=600
VOICE_QUALITY_THRESHOLD=0.6

# Localization Configuration
DEFAULT_LANGUAGE=en
AUTO_DETECT_LANGUAGE=true
```

```bash
# 3. Create persistent storage
mkdir -p data/{sessions,completed_sessions,logs}

# 4. Start services
docker-compose up -d

# 5. Monitor deployment
docker-compose logs -f ai-interviewer-bot

# 6. Verify health
docker-compose ps
```

**Production deployment with Redis and PostgreSQL:**
```bash
# Full production stack
docker-compose --profile production up -d

# Scale bot instances
docker-compose up -d --scale ai-interviewer-bot=3
```

</details>

<details>
<summary><b>🐍 Local Python Development</b></summary>

**Advantages**: Direct debugging, faster iteration, development tools

```bash
# 1. Prerequisites check
python --version  # Ensure 3.11+
pip --version

# 2. Virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Environment setup
cp .env.example .env
# Edit .env with your API keys

# 5. Run the bot
python bot_enhanced.py  # Enhanced version (recommended)
# OR
python telegram_bot.py  # Basic version
```

**Development mode with hot reload:**
```bash
# Install development dependencies
pip install watchdog

# Run with auto-restart
watchmedo auto-restart --patterns="*.py" --recursive -- python bot_enhanced.py
```

</details>

<details>
<summary><b>☁️ PythonAnywhere Deployment</b></summary>

Perfect for hosting the bot in the cloud with minimal setup.

```bash
# 1. Upload files to PythonAnywhere
# 2. Install dependencies in console
pip3.11 install --user -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your keys

# 4. Create task in Tasks tab
# Command: python3.11 /home/yourusername/ai-interviewer-bot/bot_enhanced.py
```

📖 **Detailed guide**: See [PYTHONANYWHERE.md](PYTHONANYWHERE.md) for complete instructions.

</details>

## 🤖 Bot Usage

### Starting an Interview

1. **Start conversation**: Send `/start` to the bot
2. **Select language**: Choose between 🇺🇸 English or 🇷🇺 Russian (auto-detected from Telegram locale)
3. **Choose style**: Select from 5 interview approaches:
   - 🎯 **Master Interviewer**: Comprehensive and systematic
   - 📱 **Telegram Optimized**: Mobile-friendly, concise messages
   - 💬 **Conversational Balance**: Natural flow with systematic coverage
   - 🎪 **Stage Specific**: Detailed approach for each stage
   - 🧠 **Conversation Management**: Advanced recovery and adaptation

4. **Begin interview**: Click "🚀 Begin Interview" and start responding

### Language Support

The bot supports **full localization** in:
- 🇺🇸 **English**: Complete interface and responses
- 🇷🇺 **Russian**: Полная локализация интерфейса и ответов

**Language Detection**:
- Automatic detection from your Telegram locale
- Manual language selection available
- Persistent language preferences
- All bot messages, commands, and responses localized

### Voice Message Support 🎤

Send voice messages in any supported language and the bot will:

**Features**:
- 🎯 **High-Quality Transcription**: AssemblyAI-powered speech-to-text
- 🌍 **Multi-Language**: English and Russian voice recognition
- ⚡ **Real-Time Processing**: Fast audio conversion and transcription
- 🔧 **Auto-Optimization**: Audio enhancement for better accuracy
- 📊 **Quality Indicators**: Confidence scores and transcription quality

**Usage**:
1. Record and send a voice message (up to 10 minutes)
2. Bot processes and transcribes your message
3. Continues interview with transcribed text
4. Quality indicators show transcription confidence

**Supported Formats**: OGG, MP3, M4A, WAV, WebM, Opus

**Example Voice Response**:
```
🎤✨ Voice Message Transcribed:

I'm a senior software engineer with 8 years of experience 
in full-stack development, specializing in Python and React.
```

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

## 🏗 Architecture Overview

### System Architecture

The AI Interviewer Bot follows a layered architecture designed for scalability, maintainability, and reliability:

```
┌─────────────────────────────────────────────────────────────┐
│                    🌐 User Interface Layer                  │
├─────────────────────────────────────────────────────────────┤
│  👤 Telegram Users  ←→  🤖 Telegram Bot API  ←→  📱 Bot UI   │
└─────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────┐
│                   🧠 Application Layer                       │
├─────────────────────────────────────────────────────────────┤
│  📋 Enhanced Bot  ←→  💾 Session Manager  ←→  📊 Metrics     │
│       Controller           (Persistence)      Collector     │
│                               ↕                              │
│  🎭 Prompt Manager  ←→  🔄 Error Recovery  ←→  ⚙️ Config     │
└─────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────┐
│                  🌍 Integration Layer                        │
├─────────────────────────────────────────────────────────────┤
│     🧠 Claude API Integration  ←→  ☁️ Anthropic Claude     │
│           (Structured JSON)         Sonnet-4 Model         │
└─────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────┐
│                   💾 Data Layer                             │
├─────────────────────────────────────────────────────────────┤
│  📁 File Storage  ←→  🔴 Redis Cache  ←→  🐘 PostgreSQL     │
│    (Sessions,          (Optional)         (Optional)       │
│     Logs, Archive)                                          │
└─────────────────────────────────────────────────────────────┘
```

📊 **Interactive Architecture Diagram**: See [architecture_diagrams.md](architecture_diagrams.md) for detailed Mermaid diagrams and component relationships.

### Core Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **EnhancedAIInterviewerBot** | Main controller managing all bot interactions | Session routing, error handling, command processing |
| **SessionManager** | Persistent session storage and lifecycle management | Auto-save/restore, timeout handling, cleanup |
| **PromptManager** | AI interviewer personality management | 5 distinct styles, dynamic prompt loading |
| **ClaudeIntegration** | AI response generation with structured output | JSON parsing, retry logic, fallback handling |
| **MetricsCollector** | Performance and usage analytics | Real-time stats, completion rates, error tracking |

### Data Flow

```
User Message → Bot Controller → Session Manager → Prompt Manager
      ↓                                                ↓
 Telegram API ← Response Formatter ← Claude Integration ← AI Prompt
      ↓                                                ↓
 User Interface ← Session Update ← Metrics Collection ← Structured Response
```

### Interview State Management

The system maintains sophisticated state tracking across the 9-stage interview process:

```
Session State = {
    user_context: UserProfile,
    interview_progress: StageCompleteness[1-9],
    conversation_history: MessageBuffer,
    ai_context: InterviewerPersonality,
    metrics: ProgressTracking
}
```

**Key State Features:**
- **Persistent Storage**: Sessions survive bot restarts and crashes
- **Timeout Management**: Automatic cleanup of inactive sessions
- **Progress Tracking**: Real-time completion percentage per stage
- **Recovery Points**: Ability to resume interrupted interviews
- **Analytics Integration**: Session data feeds into performance metrics

### Deployment Architectures

<details>
<summary><b>🏠 Development Setup</b></summary>

```
┌─────────────────┐
│   Developer     │
│   Machine       │
├─────────────────┤
│ Python Process  │
│ File Storage    │
│ Local Logging   │
└─────────────────┘
```

**Best for**: Development, testing, small-scale deployments

</details>

<details>
<summary><b>🐳 Docker Deployment</b></summary>

```
┌──────────────────────────────────┐
│         Docker Host              │
├──────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐│
│  │ Bot         │  │ Optional    ││
│  │ Container   │  │ Services    ││
│  │             │  │ - Redis     ││
│  │             │  │ - PostgreSQL││
│  └─────────────┘  └─────────────┘│
│  └── Volume Mounts ──┘          │
│       (sessions, logs)           │
└──────────────────────────────────┘
```

**Best for**: Production deployments, scaling, DevOps workflows

</details>

<details>
<summary><b>☁️ Cloud Production</b></summary>

```
┌─────────────────────────────────────┐
│              Cloud Provider         │
├─────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────────┐ │
│ │ Load        │ │ Bot Instances   │ │
│ │ Balancer    │ │ (Auto-scaling)  │ │
│ └─────────────┘ └─────────────────┘ │
│         │               │           │
│ ┌─────────────────────────────────┐ │
│ │      Managed Services           │ │
│ │ - Redis Cluster                 │ │
│ │ - PostgreSQL RDS               │ │
│ │ - CloudWatch Logs              │ │
│ │ - Application Monitoring       │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Best for**: High availability, automatic scaling, enterprise deployments

</details>

### Security Architecture

- **🔐 API Key Management**: Environment-based secrets, never hardcoded
- **🛡️ Input Validation**: All user inputs sanitized and validated  
- **🔒 Session Security**: Encrypted session storage with secure serialization
- **📝 Audit Logging**: Complete audit trail of all user interactions
- **⚡ Rate Limiting**: Protection against abuse and API quota management
- **🚫 Error Handling**: Secure error messages that don't expose system details

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | - | Telegram bot token from @BotFather |
| `ANTHROPIC_API_KEY` | ✅ | - | Claude API key from Anthropic Console |
| `ASSEMBLYAI_API_KEY` | ✅* | - | AssemblyAI API key for voice processing |
| `BOT_USERNAME` | ❌ | - | Bot username for logging |
| `BOT_NAME` | ❌ | AI Interviewer | Display name for the bot |
| `LOG_LEVEL` | ❌ | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FORMAT` | ❌ | text | Log format (text or json) |
| `SESSION_TIMEOUT_MINUTES` | ❌ | 180 | Session timeout in minutes |
| `MAX_CONVERSATION_HISTORY` | ❌ | 100 | Max messages to keep in history |
| `CLAUDE_MODEL` | ❌ | claude-3-5-sonnet-20241022 | Claude model to use |
| `CLAUDE_MAX_TOKENS` | ❌ | 1000 | Max tokens per response |
| `CLAUDE_TEMPERATURE` | ❌ | 0.7 | Response creativity (0.0-1.0) |

#### 🎤 Voice Processing Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VOICE_PROCESSING_ENABLED` | ❌ | true | Enable/disable voice message processing |
| `VOICE_MAX_DURATION_SECONDS` | ❌ | 600 | Maximum voice message duration (10 min) |
| `VOICE_MAX_FILE_SIZE_MB` | ❌ | 25 | Maximum voice file size |
| `VOICE_QUALITY_THRESHOLD` | ❌ | 0.6 | Minimum transcription confidence |
| `VOICE_CONCURRENT_REQUESTS` | ❌ | 3 | Max concurrent AssemblyAI requests |
| `VOICE_AUTO_LANGUAGE_DETECTION` | ❌ | true | Enable automatic language detection |

#### 🌐 Localization Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEFAULT_LANGUAGE` | ❌ | en | Default language (en/ru) |
| `AUTO_DETECT_LANGUAGE` | ❌ | true | Auto-detect from Telegram locale |
| `FORCE_LANGUAGE_SELECTION` | ❌ | false | Always show language selection |

*AssemblyAI API key is required only if voice processing is enabled

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
   - Clean up temporary voice files

2. **Slow responses**:
   - Check internet connection
   - Verify Claude API status
   - Review `CLAUDE_MAX_TOKENS` setting
   - Check AssemblyAI API performance

### Voice Message Issues

1. **Voice transcription failures**:
   ```bash
   # Check AssemblyAI API key
   curl -H "authorization: YOUR_ASSEMBLYAI_KEY" \
        https://api.assemblyai.com/v2/transcript
   
   # Verify audio dependencies
   ffmpeg -version
   pip show pydub assemblyai
   ```

2. **Poor transcription quality**:
   - Speak clearly and slowly
   - Use quiet environment
   - Check microphone quality
   - Reduce background noise
   - Keep messages under 10 minutes

3. **Voice processing errors**:
   ```bash
   # Check temp directory permissions
   ls -la /tmp/ai_interviewer_audio/
   
   # Monitor voice processing logs
   docker-compose logs -f ai-interviewer-bot | grep voice
   ```

### Language Issues

1. **Wrong language detected**:
   - Set Telegram language preference
   - Use manual language selection
   - Check locale settings: Settings → Language

2. **Mixed language responses**:
   - Reset session with `/reset`
   - Manually select language in bot
   - Clear language preferences

3. **Missing translations**:
   ```bash
   # Check localization files
   python -c "from localization import localization; print(localization.get_supported_languages())"
   
   # Verify language preference storage
   ls user_language_preferences.json
   ```

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

## 🔌 API Usage & Integration

### SDK-Style Usage

For developers who want to integrate the bot as a library:

```python
#!/usr/bin/env python3
from bot_enhanced import EnhancedAIInterviewerBot
from telegram_bot import PromptVariant
import asyncio

# Initialize the bot
bot = EnhancedAIInterviewerBot(
    telegram_token="your_telegram_token",
    anthropic_api_key="your_anthropic_key"
)

# Programmatic session management
async def create_interview_session(user_id: int, username: str):
    """Create a new interview session"""
    session = await bot.session_manager.create_session(
        user_id=user_id,
        username=username,
        prompt_variant=PromptVariant.MASTER_INTERVIEWER
    )
    return session

async def send_message_to_interview(user_id: int, message: str):
    """Send a message to an active interview session"""
    response = await bot.handle_user_message(user_id, message)
    return response

# Usage example
async def main():
    # Start an interview
    session = await create_interview_session(12345, "john_doe")
    
    # Send messages
    response1 = await send_message_to_interview(12345, "I'm a software engineer")
    print(f"Bot: {response1['response']}")
    
    response2 = await send_message_to_interview(12345, "I work with Python and React")
    print(f"Bot: {response2['response']}")
    
    # Check progress
    status = bot.session_manager.get_session_status(12345)
    print(f"Progress: {status['completion_percentage']}%")

if __name__ == "__main__":
    asyncio.run(main())
```

### Integration Patterns

<details>
<summary><b>🔗 Webhook Integration</b></summary>

Integrate the bot into existing web applications:

```python
from flask import Flask, request, jsonify
from bot_enhanced import EnhancedAIInterviewerBot

app = Flask(__name__)
bot = EnhancedAIInterviewerBot(token, api_key)

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Handle incoming Telegram updates"""
    try:
        update_data = request.get_json()
        # Process update asynchronously
        asyncio.create_task(bot.process_update(update_data))
        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/api/sessions', methods=['GET'])
def get_active_sessions():
    """Get list of active interview sessions"""
    sessions = bot.session_manager.get_active_sessions()
    return jsonify([{
        "user_id": s.user_id,
        "username": s.username,
        "stage": s.current_stage.value,
        "progress": s.get_completion_percentage()
    } for s in sessions])

@app.route('/api/sessions/<int:user_id>/status', methods=['GET'])
def get_session_status(user_id):
    """Get detailed session status"""
    session = bot.session_manager.get_session(user_id)
    if not session:
        return {"error": "Session not found"}, 404
    
    return jsonify({
        "user_id": session.user_id,
        "current_stage": session.current_stage.value,
        "completion": session.get_completion_percentage(),
        "duration": session.get_duration_minutes(),
        "message_count": len(session.conversation_history)
    })
```

</details>

<details>
<summary><b>💾 Custom Storage Backend</b></summary>

Implement custom session storage (e.g., for databases):

```python
from typing import Optional
import json
from bot_enhanced import SessionManager, InterviewSession

class DatabaseSessionManager(SessionManager):
    """Custom session manager with PostgreSQL backend"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        super().__init__()
    
    async def save_session(self, session: InterviewSession):
        """Save session to database"""
        session_data = {
            'user_id': session.user_id,
            'username': session.username,
            'prompt_variant': session.prompt_variant.value,
            'current_stage': session.current_stage.value,
            'conversation_history': session.conversation_history,
            'start_time': session.start_time.isoformat(),
            'last_activity': session.last_activity.isoformat()
        }
        
        query = """
        INSERT INTO interview_sessions (user_id, data, updated_at)
        VALUES ($1, $2, NOW())
        ON CONFLICT (user_id) 
        DO UPDATE SET data = $2, updated_at = NOW()
        """
        await self.db.execute(query, session.user_id, json.dumps(session_data))
    
    async def load_session(self, user_id: int) -> Optional[InterviewSession]:
        """Load session from database"""
        query = "SELECT data FROM interview_sessions WHERE user_id = $1"
        row = await self.db.fetchrow(query, user_id)
        
        if row:
            data = json.loads(row['data'])
            return InterviewSession.from_dict(data)
        return None

# Usage
from bot_enhanced import EnhancedAIInterviewerBot
import asyncpg

async def create_bot_with_db():
    db_pool = await asyncpg.create_pool(
        "postgresql://user:password@localhost/interviews"
    )
    
    # Use custom session manager
    bot = EnhancedAIInterviewerBot(token, api_key)
    bot.session_manager = DatabaseSessionManager(db_pool)
    
    return bot
```

</details>

<details>
<summary><b>📊 Analytics Integration</b></summary>

Add custom analytics and monitoring:

```python
from bot_enhanced import MetricsCollector
import requests

class CustomMetricsCollector(MetricsCollector):
    """Enhanced metrics with external service integration"""
    
    def __init__(self, analytics_endpoint: str):
        super().__init__()
        self.analytics_endpoint = analytics_endpoint
    
    async def track_session_start(self, user_id: int, prompt_variant: str):
        """Track session start with external analytics"""
        await super().track_session_start(user_id, prompt_variant)
        
        # Send to external service
        payload = {
            'event': 'interview_started',
            'user_id': user_id,
            'prompt_variant': prompt_variant,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            requests.post(self.analytics_endpoint, json=payload)
        except Exception as e:
            logger.warning(f"Analytics tracking failed: {e}")
    
    async def track_stage_completion(self, user_id: int, stage: str, duration: int):
        """Track stage completion with timing"""
        await super().track_stage_completion(user_id, stage, duration)
        
        # Custom analytics logic
        if stage == "expertise_map" and duration > 1800:  # 30 minutes
            await self._alert_long_session(user_id, stage, duration)
    
    async def _alert_long_session(self, user_id: int, stage: str, duration: int):
        """Alert for unusually long sessions"""
        alert_data = {
            'alert_type': 'long_session',
            'user_id': user_id,
            'stage': stage,
            'duration_seconds': duration
        }
        # Send alert to monitoring system
        requests.post(f"{self.analytics_endpoint}/alerts", json=alert_data)

# Integration
bot = EnhancedAIInterviewerBot(token, api_key)
bot.metrics_collector = CustomMetricsCollector("https://analytics.company.com/api")
```

</details>

### API Reference

#### Session Data Structure

```python
@dataclass
class InterviewSession:
    user_id: int                               # Telegram user ID
    username: str                              # Telegram username
    prompt_variant: PromptVariant              # Selected interviewer personality
    current_stage: InterviewStage              # Current interview stage (1-9)
    stage_completeness: Dict[str, int]         # Completion percentage per stage
    conversation_history: List[Dict[str, Any]] # Complete message history
    start_time: datetime                       # Session start timestamp
    last_activity: datetime                    # Last interaction timestamp
    question_depth: int = 1                    # Current question depth (1-4)
    engagement_level: str = "medium"           # User engagement (high/medium/low)
    examples_collected: int = 0                # Number of examples gathered
    key_insights: List[str] = None             # Extracted key insights
    
    # Methods
    def get_completion_percentage(self) -> int
    def get_duration_minutes(self) -> int
    def is_expired(self, timeout_minutes: int) -> bool
    def to_dict(self) -> dict
    @classmethod
    def from_dict(cls, data: dict) -> 'InterviewSession'
```

#### Claude Response Format

```json
{
  "interview_stage": "profiling|essence|operations|expertise_map|failure_modes|mastery|growth_path|wrap_up",
  "response": "AI interviewer's response message",
  "metadata": {
    "question_depth": 1-4,
    "completeness": 0-100,
    "engagement_level": "high|medium|low",
    "estimated_time_remaining": 45
  },
  "internal_tracking": {
    "key_insights": ["insight1", "insight2"],
    "examples_collected": 3,
    "follow_up_needed": ["area1", "area2"],
    "stage_transition_ready": false,
    "conversation_quality": "excellent|good|needs_improvement"
  }
}
```

#### Bot Commands API

| Command | Description | Response Format |
|---------|-------------|-----------------|
| `/start` | Begin new interview or resume existing | Prompt selection interface |
| `/status` | Get current progress | Stage completion summary with percentages |
| `/reset` | Clear current session | Confirmation dialog |
| `/complete` | Manual interview completion | Final summary and archive |
| `/metrics` | Show bot statistics | Usage analytics (enhanced version) |
| `/help` | Display help information | Command list and usage guide |

#### Integration Endpoints

```python
# Session Management
async def create_session(user_id: int, username: str, variant: PromptVariant) -> InterviewSession
async def get_session(user_id: int) -> Optional[InterviewSession]
async def update_session(session: InterviewSession) -> None
async def delete_session(user_id: int) -> bool
async def get_active_sessions() -> List[InterviewSession]

# Message Handling
async def handle_user_message(user_id: int, message: str) -> Dict[str, Any]
async def send_bot_message(user_id: int, message: str) -> None

# Analytics
async def get_session_metrics(user_id: int) -> Dict[str, Any]
async def get_bot_statistics() -> Dict[str, Any]
async def export_session_data(user_id: int, format: str = "json") -> str
```

📚 **Complete API Documentation**: See [developer-api-reference.md](developer-api-reference.md) for detailed API specifications, [integration-guide.md](integration-guide.md) for implementation patterns, and [json-response-schema.md](json-response-schema.md) for Claude response formats.

## ⚡ Performance & Monitoring

### Performance Characteristics

The AI Interviewer Bot is optimized for production use with the following performance targets:

| Metric | Target | Notes |
|--------|--------|-------|
| **Response Time** | < 3 seconds | 95th percentile for Claude API calls |
| **Concurrent Users** | 100+ | Limited by Claude API rate limits |
| **Memory Usage** | < 512MB | Per bot instance (configurable) |
| **Session Storage** | 10,000+ sessions | File system or database backend |
| **Uptime** | 99.9%+ | With proper error handling and retries |

### Built-in Monitoring

#### Real-time Metrics

The enhanced bot version (`bot_enhanced.py`) includes comprehensive metrics collection:

```python
# Access built-in metrics
bot = EnhancedAIInterviewerBot(token, api_key)
metrics = bot.metrics_collector.get_current_metrics()

print(f"Active sessions: {metrics['active_sessions']}")
print(f"Messages processed: {metrics['messages_processed']}")
print(f"API success rate: {metrics['api_success_rate']}%")
print(f"Average response time: {metrics['avg_response_time']}s")
```

#### Metrics Dashboard

Access real-time metrics through the `/metrics` command or programmatically:

```bash
# Via Telegram bot
/metrics

# Sample output:
📊 Bot Performance Metrics
━━━━━━━━━━━━━━━━━━━━
🏃 Active Sessions: 12
📥 Messages Today: 1,247
🤖 Claude API Calls: 892
✅ Success Rate: 99.2%
⏱️ Avg Response: 2.1s
💾 Memory Usage: 234MB
🕐 Uptime: 2d 14h 23m
```

#### Performance Monitoring Setup

<details>
<summary><b>📊 Prometheus Integration</b></summary>

Add Prometheus metrics endpoint for production monitoring:

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from bot_enhanced import EnhancedAIInterviewerBot

# Create metrics
sessions_total = Counter('interviews_started_total', 'Total interviews started')
response_time = Histogram('claude_response_time_seconds', 'Claude API response time')
active_sessions = Gauge('active_sessions', 'Current active sessions')
api_errors = Counter('claude_api_errors_total', 'Claude API errors')

class MonitoredBot(EnhancedAIInterviewerBot):
    """Bot with Prometheus monitoring"""
    
    async def handle_user_message(self, user_id: int, message: str):
        with response_time.time():
            try:
                response = await super().handle_user_message(user_id, message)
                return response
            except Exception as e:
                api_errors.inc()
                raise
    
    async def create_session(self, user_id: int, username: str):
        session = await super().create_session(user_id, username)
        sessions_total.inc()
        active_sessions.set(len(self.session_manager.sessions))
        return session

# Start Prometheus metrics server
start_http_server(8000)
bot = MonitoredBot(token, api_key)
```

</details>

<details>
<summary><b>🔍 Health Check Endpoint</b></summary>

Implement health checks for load balancers and monitoring:

```python
from flask import Flask, jsonify
import asyncio
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })

@app.route('/health/detailed')
def detailed_health():
    """Detailed health check with dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check Claude API connectivity
    try:
        # Quick test call to Claude
        asyncio.run(test_claude_connection())
        health_status["checks"]["claude_api"] = "healthy"
    except Exception as e:
        health_status["checks"]["claude_api"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check session storage
    try:
        sessions_dir = Path("sessions")
        if sessions_dir.exists() and sessions_dir.is_dir():
            health_status["checks"]["session_storage"] = "healthy"
        else:
            health_status["checks"]["session_storage"] = "error: directory not found"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["session_storage"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check active sessions
    try:
        active_count = len(bot.session_manager.sessions)
        health_status["checks"]["active_sessions"] = active_count
        if active_count > 1000:  # Alert threshold
            health_status["status"] = "warning"
    except Exception as e:
        health_status["checks"]["active_sessions"] = f"error: {str(e)}"
    
    return jsonify(health_status)

# Run health check server alongside bot
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
```

</details>

### Performance Optimization

#### Memory Management

```python
# Configure session cleanup
SESSION_CLEANUP_INTERVAL = 300  # 5 minutes
MAX_INACTIVE_SESSIONS = 100
MAX_SESSION_HISTORY = 50  # Limit conversation history

# Enable in bot configuration
bot = EnhancedAIInterviewerBot(
    telegram_token=token,
    anthropic_api_key=api_key,
    session_cleanup_interval=SESSION_CLEANUP_INTERVAL,
    max_conversation_history=MAX_SESSION_HISTORY
)
```

#### Claude API Optimization

```python
# Optimize Claude API calls
CLAUDE_CONFIG = {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 800,  # Reduce for faster responses
    "temperature": 0.7,
    "timeout": 30,  # Fail fast for better UX
    "retry_attempts": 3,
    "retry_delay": 1.0
}
```

#### Database Connection Pooling

For production deployments with database backends:

```python
import asyncpg
from bot_enhanced import EnhancedAIInterviewerBot

async def create_optimized_bot():
    # Connection pool for better performance
    db_pool = await asyncpg.create_pool(
        database_url,
        min_size=5,
        max_size=20,
        command_timeout=10,
        server_settings={
            'application_name': 'ai_interviewer_bot',
            'jit': 'off'  # Disable JIT for faster small queries
        }
    )
    
    bot = EnhancedAIInterviewerBot(token, api_key)
    bot.session_manager = DatabaseSessionManager(db_pool)
    return bot
```

### Monitoring & Alerting

#### Key Metrics to Monitor

1. **Response Time Metrics**
   - Claude API response time
   - End-to-end message processing time
   - Session load/save operations

2. **Error Rate Monitoring**
   - Claude API failures
   - JSON parsing errors
   - Session persistence failures

3. **Resource Usage**
   - Memory consumption per instance
   - CPU utilization during peak hours
   - Disk space for session storage

4. **User Experience Metrics**
   - Session completion rates
   - User engagement levels
   - Interview duration patterns

#### Alert Thresholds

```yaml
# Sample alerting rules (Prometheus AlertManager)
groups:
  - name: ai_interviewer_bot
    rules:
      - alert: HighErrorRate
        expr: rate(claude_api_errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High Claude API error rate"
          
      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(claude_response_time_seconds_bucket[5m])) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow Claude API responses"
          
      - alert: MemoryUsageHigh
        expr: process_resident_memory_bytes > 1073741824  # 1GB
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage"
```

### Load Testing

Verify bot performance under load:

```python
import asyncio
import aiohttp
import random
from concurrent.futures import ThreadPoolExecutor

async def simulate_user_session(session_id: int):
    """Simulate a complete user interview session"""
    
    messages = [
        "I'm a software engineer",
        "I work with Python and machine learning",
        "I've been in this role for 3 years",
        "My biggest challenge is scaling systems",
        # ... more realistic interview responses
    ]
    
    for message in messages:
        # Simulate realistic user typing delay
        await asyncio.sleep(random.uniform(2, 8))
        
        # Send message to bot (via webhook or direct API)
        response = await send_message_to_bot(session_id, message)
        
        if not response:
            print(f"Session {session_id} failed")
            break
    
    print(f"Session {session_id} completed")

async def load_test(concurrent_users: int = 50):
    """Run load test with specified number of concurrent users"""
    
    print(f"Starting load test with {concurrent_users} concurrent users")
    start_time = asyncio.get_event_loop().time()
    
    # Create concurrent sessions
    tasks = [
        simulate_user_session(user_id) 
        for user_id in range(concurrent_users)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    duration = asyncio.get_event_loop().time() - start_time
    successes = sum(1 for r in results if not isinstance(r, Exception))
    
    print(f"Load test completed in {duration:.2f}s")
    print(f"Success rate: {successes}/{concurrent_users} ({100*successes/concurrent_users:.1f}%)")

# Run load test
if __name__ == "__main__":
    asyncio.run(load_test(concurrent_users=25))
```

## 🔐 Security Considerations

### 🔑 Secrets Management

**Environment Variables (Required)**
```bash
# ✅ Secure - Use environment variables
export TELEGRAM_BOT_TOKEN="1234567890:AABBccDDee..."
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# ❌ NEVER commit secrets to git
# TELEGRAM_BOT_TOKEN=actual_token_here  # Wrong!
```

**Production Secrets Management:**
- Use AWS Secrets Manager, HashiCorp Vault, or K8s secrets
- Rotate API keys regularly (quarterly recommended)
- Use least-privilege access principles
- Monitor for leaked credentials in code repositories

### 🛡️ Data Protection

**Session Data Security:**
```python
# Sessions contain sensitive professional information
class SecureSessionManager(SessionManager):
    def __init__(self, encryption_key: bytes):
        super().__init__()
        self.cipher = Fernet(encryption_key)
    
    def save_session(self, session: InterviewSession):
        # Encrypt session data before storing
        session_data = pickle.dumps(session)
        encrypted_data = self.cipher.encrypt(session_data)
        
        with open(self._get_session_file(session.user_id), 'wb') as f:
            f.write(encrypted_data)
    
    def load_session(self, user_id: int) -> Optional[InterviewSession]:
        try:
            with open(self._get_session_file(user_id), 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return pickle.loads(decrypted_data)
        except Exception:
            return None
```

**Data Retention Policies:**
- Automatic session cleanup after 30 days of inactivity
- Completed interviews archived with encryption
- Option to purge user data on request (GDPR compliance)
- No sensitive data in application logs

### 🚫 Input Validation & Sanitization

```python
import re
from html import escape

class InputValidator:
    """Comprehensive input validation for user messages"""
    
    MAX_MESSAGE_LENGTH = 4000  # Telegram's limit
    BLOCKED_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS prevention
        r'javascript:',                # JavaScript URLs
        r'data:text/html',            # Data URLs
    ]
    
    @classmethod
    def sanitize_user_input(cls, text: str) -> str:
        """Sanitize user input before processing"""
        if not isinstance(text, str):
            return ""
        
        # Length check
        if len(text) > cls.MAX_MESSAGE_LENGTH:
            text = text[:cls.MAX_MESSAGE_LENGTH] + "..."
        
        # Remove dangerous patterns
        for pattern in cls.BLOCKED_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # HTML escape for storage safety
        text = escape(text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    @classmethod
    def validate_user_id(cls, user_id: int) -> bool:
        """Validate Telegram user ID format"""
        return isinstance(user_id, int) and 0 < user_id < 2**63
```

### ⚡ Rate Limiting & Abuse Prevention

```python
from collections import defaultdict
import time
from typing import Dict

class RateLimiter:
    """Protect against API abuse and excessive usage"""
    
    def __init__(self, max_requests: int = 10, window_minutes: int = 1):
        self.max_requests = max_requests
        self.window_seconds = window_minutes * 60
        self.user_requests: Dict[int, list] = defaultdict(list)
    
    def is_allowed(self, user_id: int) -> bool:
        """Check if user is within rate limits"""
        now = time.time()
        user_history = self.user_requests[user_id]
        
        # Remove old requests outside window
        cutoff = now - self.window_seconds
        user_history[:] = [req_time for req_time in user_history if req_time > cutoff]
        
        # Check if user has exceeded limit
        if len(user_history) >= self.max_requests:
            return False
        
        # Record this request
        user_history.append(now)
        return True
    
    def get_retry_after(self, user_id: int) -> int:
        """Get seconds until user can make next request"""
        if not self.user_requests[user_id]:
            return 0
        
        oldest_request = min(self.user_requests[user_id])
        return max(0, int(self.window_seconds - (time.time() - oldest_request)))

# Usage in bot
rate_limiter = RateLimiter(max_requests=30, window_minutes=5)

async def handle_user_message(self, user_id: int, message: str):
    if not rate_limiter.is_allowed(user_id):
        retry_after = rate_limiter.get_retry_after(user_id)
        await self.send_message(user_id, 
            f"⚠️ Rate limit exceeded. Please wait {retry_after} seconds.")
        return
    
    # Process message normally
    ...
```

### 📝 Secure Logging

```python
import logging
import json
from typing import Any, Dict

class SecureFormatter(logging.Formatter):
    """Logging formatter that removes sensitive information"""
    
    SENSITIVE_KEYS = {
        'telegram_token', 'anthropic_api_key', 'api_key', 'token',
        'password', 'secret', 'key', 'auth', 'credential'
    }
    
    def format(self, record):
        # Create a copy of the record dict to avoid modifying original
        record_dict = record.__dict__.copy()
        
        # Remove sensitive information
        for key in list(record_dict.keys()):
            if any(sensitive in key.lower() for sensitive in self.SENSITIVE_KEYS):
                record_dict[key] = "[REDACTED]"
        
        # Handle message content
        if hasattr(record, 'getMessage'):
            message = record.getMessage()
            record_dict['message'] = self._sanitize_message(message)
        
        return super().format(record)
    
    def _sanitize_message(self, message: str) -> str:
        """Remove potential sensitive data from log messages"""
        # Remove anything that looks like API keys
        import re
        patterns = [
            r'sk-[a-zA-Z0-9-_]{20,}',    # Anthropic API keys
            r'\d{10}:[a-zA-Z0-9-_]{35}', # Telegram bot tokens
            r'Bearer [a-zA-Z0-9-_.~+/]+=*', # Bearer tokens
        ]
        
        for pattern in patterns:
            message = re.sub(pattern, '[REDACTED]', message)
        
        return message

# Configure secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)

# Use custom formatter
for handler in logging.getLogger().handlers:
    handler.setFormatter(SecureFormatter())
```

### 🔒 Network Security

**Docker Network Isolation:**
```yaml
# docker-compose.yml - Production security
version: '3.8'

services:
  ai-interviewer-bot:
    build: .
    networks:
      - internal
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    # No exposed ports - bot connects outbound only
    
  redis:
    image: redis:7-alpine
    networks:
      - internal
    # Only accessible within internal network
    
networks:
  internal:
    driver: bridge
    internal: false  # Allows outbound internet access
```

**TLS/SSL Configuration:**
```python
# For webhook deployments
import ssl

# Create secure SSL context
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')

# Use in webhook server
app.run(host='0.0.0.0', port=8443, ssl_context=ssl_context)
```

### 🛡️ Security Best Practices Checklist

- [ ] **Secrets Management**: All API keys stored securely, never in code
- [ ] **Input Validation**: All user inputs sanitized and validated
- [ ] **Rate Limiting**: Protection against abuse and DoS attacks
- [ ] **Session Security**: Session data encrypted at rest
- [ ] **Secure Logging**: No sensitive data in logs
- [ ] **Network Security**: Proper firewall and network isolation
- [ ] **Dependency Updates**: Regular security updates for dependencies
- [ ] **Error Handling**: No sensitive information in error messages
- [ ] **Access Control**: Principle of least privilege for all services
- [ ] **Monitoring**: Security event logging and alerting
- [ ] **Data Retention**: Automatic cleanup of old session data
- [ ] **Incident Response**: Plan for security incidents and breaches

## 🛠 Troubleshooting

### 🚨 Common Issues & Solutions

<details>
<summary><b>❌ Bot Not Responding to Messages</b></summary>

**Symptoms**: Bot shows as online but doesn't respond to commands or messages.

**Diagnostic Steps**:
```bash
# 1. Check bot logs
docker-compose logs -f ai-interviewer-bot
# OR for local deployment:
tail -f logs/bot.log

# 2. Test Telegram API connectivity
curl -X GET "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"

# 3. Check webhook status (if using webhooks)
curl -X GET "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
```

**Common Solutions**:
- **Invalid Token**: Verify `TELEGRAM_BOT_TOKEN` in `.env` file
- **Network Issues**: Check internet connectivity and firewall rules
- **Rate Limiting**: Wait 10 minutes if you've hit Telegram's rate limits
- **Webhook Conflicts**: Remove webhook if running in polling mode:
  ```bash
  curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/deleteWebhook"
  ```

**Code Fix for Polling Issues**:
```python
# If using polling, ensure webhook is not set
from telegram.ext import Application

app = Application.builder().token(token).build()
await app.bot.delete_webhook()  # Clear any existing webhook
app.run_polling(drop_pending_updates=True)
```

</details>

<details>
<summary><b>🤖 Claude API Errors</b></summary>

**Symptoms**: Bot responds with "Sorry, I encountered an error" or similar messages.

**Error Types & Solutions**:

1. **Authentication Errors (401)**
   ```bash
   # Verify API key format and validity
   curl -X POST "https://api.anthropic.com/v1/messages" \
     -H "x-api-key: ${ANTHROPIC_API_KEY}" \
     -H "anthropic-version: 2023-06-01" \
     -H "content-type: application/json" \
     -d '{"model": "claude-3-sonnet-20240229", "max_tokens": 10, "messages": [{"role": "user", "content": "Hi"}]}'
   ```
   **Fix**: Check API key format (should start with `sk-ant-api03-`)

2. **Rate Limiting (429)**
   ```bash
   # Check current usage
   curl -X GET "https://api.anthropic.com/v1/usage" \
     -H "x-api-key: ${ANTHROPIC_API_KEY}"
   ```
   **Fix**: Implement exponential backoff or upgrade API plan

3. **Invalid Model (400)**
   ```python
   # Update to correct model name
   CLAUDE_MODEL = "claude-3-5-sonnet-20241022"  # Current model
   ```

4. **Token Limit Exceeded (400)**
   ```python
   # Reduce token limit in configuration
   CLAUDE_MAX_TOKENS = 800  # Reduce from 1000
   MAX_CONVERSATION_HISTORY = 20  # Reduce history
   ```

**Debug Mode**:
```python
# Enable detailed Claude API logging
import logging
logging.getLogger('anthropic').setLevel(logging.DEBUG)

# Add custom error handler
async def handle_claude_error(error):
    logger.error(f"Claude API Error: {error}")
    if "rate_limit" in str(error).lower():
        return "I'm experiencing high demand. Please try again in a moment."
    elif "invalid_request" in str(error).lower():
        return "I'm having trouble understanding. Could you rephrase that?"
    else:
        return "I'm temporarily unavailable. Please try again later."
```

</details>

<details>
<summary><b>💾 Session Storage Issues</b></summary>

**Symptoms**: Bot loses conversation state, users can't resume interviews.

**File System Storage Problems**:
```bash
# Check session directory permissions
ls -la sessions/
# Should show read/write permissions for bot user

# Check disk space
df -h
# Ensure sufficient space in sessions directory

# Check for corrupted session files
python3 -c "
import pickle
import os
for f in os.listdir('sessions'):
    try:
        with open(f'sessions/{f}', 'rb') as file:
            pickle.load(file)
        print(f'{f}: OK')
    except Exception as e:
        print(f'{f}: ERROR - {e}')
"
```

**Quick Fixes**:
```bash
# Fix permissions
sudo chmod 755 sessions/
sudo chown -R $(whoami):$(whoami) sessions/

# Clean corrupted sessions
find sessions/ -name "*.pkl" -size 0 -delete  # Remove empty files
```

**Database Storage Problems**:
```python
# Test database connectivity
import asyncpg

async def test_db_connection():
    try:
        conn = await asyncpg.connect("postgresql://user:pass@host/db")
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        print("Database connection: OK")
    except Exception as e:
        print(f"Database error: {e}")

asyncio.run(test_db_connection())
```

</details>

<details>
<summary><b>🐳 Docker Deployment Issues</b></summary>

**Container Won't Start**:
```bash
# Check container status
docker-compose ps

# View startup logs
docker-compose logs ai-interviewer-bot

# Common startup failures:
# 1. Missing .env file
ls -la .env
# Solution: cp .env.example .env

# 2. Invalid environment variables
docker-compose config  # Validates compose file

# 3. Port conflicts
docker ps  # Check if ports are already in use
```

**Container Keeps Restarting**:
```bash
# Check resource limits
docker stats ai-interviewer-bot

# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G  # Increase from 512M
```

**Volume Mount Issues**:
```bash
# Check volume mounts
docker inspect ai-interviewer-bot | grep -A 10 "Mounts"

# Fix volume permissions
mkdir -p data/{sessions,completed_sessions,logs}
sudo chown -R 1000:1000 data/  # Use container user ID
```

**Network Connectivity Issues**:
```bash
# Test external connectivity from container
docker exec ai-interviewer-bot ping -c 3 api.telegram.org
docker exec ai-interviewer-bot ping -c 3 api.anthropic.com

# Check DNS resolution
docker exec ai-interviewer-bot nslookup api.telegram.org
```

</details>

<details>
<summary><b>⚡ Performance Issues</b></summary>

**Slow Response Times**:
```bash
# Monitor system resources
htop  # Check CPU and memory usage
iotop  # Check disk I/O

# Monitor bot performance
docker exec ai-interviewer-bot python -c "
from bot_enhanced import EnhancedAIInterviewerBot
# Check metrics endpoint
bot.metrics_collector.get_current_metrics()
"
```

**Memory Leaks**:
```python
# Add memory monitoring
import psutil
import gc

def monitor_memory():
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.1f} MB")
    
    if memory_mb > 500:  # Alert threshold
        print("High memory usage detected!")
        gc.collect()  # Force garbage collection

# Call periodically
asyncio.create_task(periodic_memory_check())
```

**Database Connection Pool Exhaustion**:
```python
# Monitor connection pool
async def check_pool_status(pool):
    print(f"Pool size: {pool.get_size()}")
    print(f"Available connections: {pool.get_idle_size()}")
    
    if pool.get_idle_size() == 0:
        print("WARNING: Connection pool exhausted!")
        
# Increase pool size if needed
db_pool = await asyncpg.create_pool(
    database_url,
    min_size=10,  # Increase from 5
    max_size=50,  # Increase from 20
)
```

</details>

### 🔧 Diagnostic Tools

#### Health Check Script

```bash
#!/bin/bash
# healthcheck.sh - Comprehensive system health check

echo "🔍 AI Interviewer Bot Health Check"
echo "================================="

# Check environment variables
echo "📋 Environment Variables:"
if [ -f .env ]; then
    echo "✅ .env file exists"
    if grep -q "TELEGRAM_BOT_TOKEN" .env && grep -q "ANTHROPIC_API_KEY" .env; then
        echo "✅ Required API keys present"
    else
        echo "❌ Missing required API keys in .env"
    fi
else
    echo "❌ .env file missing"
fi

# Check API connectivity
echo -e "\n🌐 API Connectivity:"
if curl -s -f "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" > /dev/null; then
    echo "✅ Telegram API accessible"
else
    echo "❌ Telegram API unreachable"
fi

# Test Claude API (basic check)
if [ ! -z "$ANTHROPIC_API_KEY" ]; then
    if curl -s -H "x-api-key: $ANTHROPIC_API_KEY" \
            -H "anthropic-version: 2023-06-01" \
            "https://api.anthropic.com/v1/messages" \
            -d '{"model": "claude-3-sonnet-20240229", "max_tokens": 1, "messages": [{"role": "user", "content": "test"}]}' \
            > /dev/null 2>&1; then
        echo "✅ Claude API accessible"
    else
        echo "❌ Claude API unreachable or invalid key"
    fi
fi

# Check storage
echo -e "\n💾 Storage:"
if [ -d "sessions" ]; then
    echo "✅ Sessions directory exists"
    echo "📊 Session count: $(ls sessions/*.pkl 2>/dev/null | wc -l)"
else
    echo "❌ Sessions directory missing"
fi

# Check Docker if running
echo -e "\n🐳 Docker Status:"
if docker-compose ps 2>/dev/null | grep -q "ai-interviewer-bot"; then
    if docker-compose ps | grep -q "Up"; then
        echo "✅ Docker container running"
    else
        echo "❌ Docker container not running"
    fi
else
    echo "ℹ️ Not running in Docker mode"
fi

echo -e "\n🔍 Health check complete!"
```

#### Log Analysis Script

```python
#!/usr/bin/env python3
"""
Log analysis tool for AI Interviewer Bot
Usage: python log_analyzer.py [log_file]
"""

import re
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import sys

def analyze_logs(log_file='logs/bot.log'):
    """Analyze bot logs for common issues and patterns"""
    
    error_patterns = {
        'claude_api_error': r'Claude API.*error|anthropic.*error',
        'telegram_error': r'telegram.*error|bot.*error',
        'session_error': r'session.*error|pickle.*error',
        'timeout_error': r'timeout|timed out',
        'rate_limit': r'rate limit|too many requests'
    }
    
    stats = {
        'total_lines': 0,
        'errors': defaultdict(int),
        'error_messages': defaultdict(list),
        'hourly_activity': defaultdict(int),
        'users': set(),
        'sessions': set()
    }
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                stats['total_lines'] += 1
                
                # Extract timestamp
                timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
                if timestamp_match:
                    hour = timestamp_match.group(1)[:13]  # YYYY-MM-DDTHH
                    stats['hourly_activity'][hour] += 1
                
                # Check for errors
                for error_type, pattern in error_patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        stats['errors'][error_type] += 1
                        stats['error_messages'][error_type].append(line.strip())
                
                # Extract user IDs
                user_match = re.search(r'user_id[:\s=]+(\d+)', line)
                if user_match:
                    stats['users'].add(user_match.group(1))
                
                # Extract session info
                session_match = re.search(r'session[:\s=]+(\w+)', line)
                if session_match:
                    stats['sessions'].add(session_match.group(1))
    
    except FileNotFoundError:
        print(f"❌ Log file not found: {log_file}")
        return
    
    # Print analysis
    print(f"📊 Log Analysis for {log_file}")
    print("=" * 50)
    print(f"📋 Total log lines: {stats['total_lines']}")
    print(f"👥 Unique users: {len(stats['users'])}")
    print(f"💼 Total sessions: {len(stats['sessions'])}")
    
    if stats['errors']:
        print(f"\n❌ Error Summary:")
        for error_type, count in stats['errors'].most_common():
            print(f"  {error_type}: {count} occurrences")
            
        print(f"\n🔍 Recent Error Examples:")
        for error_type, messages in stats['error_messages'].items():
            if messages:
                print(f"\n{error_type}:")
                for msg in messages[-3:]:  # Show last 3 errors
                    print(f"  • {msg}")
    
    # Activity analysis
    if stats['hourly_activity']:
        print(f"\n📈 Activity by Hour:")
        sorted_hours = sorted(stats['hourly_activity'].items())
        for hour, count in sorted_hours[-10:]:  # Show last 10 hours
            print(f"  {hour}: {count} events")

if __name__ == "__main__":
    log_file = sys.argv[1] if len(sys.argv) > 1 else 'logs/bot.log'
    analyze_logs(log_file)
```

### 🆘 Emergency Procedures

#### Quick Recovery Commands

```bash
# Emergency bot restart
docker-compose restart ai-interviewer-bot

# Clear all sessions (last resort)
rm -rf sessions/*.pkl
docker-compose restart

# Reset to clean state
docker-compose down
docker system prune -f
docker-compose up -d

# Check system resources
free -h && df -h && docker system df
```

#### Support Information Gathering

When reporting issues, collect this information:

```bash
#!/bin/bash
# collect_debug_info.sh

echo "🔍 Debug Information Collection"
echo "=============================="

echo "📅 Date: $(date)"
echo "🖥️  System: $(uname -a)"
echo "🐳 Docker Version: $(docker --version)"
echo "🐙 Docker Compose Version: $(docker-compose --version)"

echo -e "\n📋 Environment Check:"
echo "Python version: $(python3 --version)"
echo "Available memory: $(free -h | grep Mem)"
echo "Disk space: $(df -h | grep -E '/$|/var')"

echo -e "\n🐳 Container Status:"
docker-compose ps

echo -e "\n📊 Container Resources:"
docker stats --no-stream

echo -e "\n📝 Recent Logs:"
docker-compose logs --tail=50 ai-interviewer-bot

echo -e "\n⚙️ Configuration:"
echo "Environment variables (sanitized):"
env | grep -E "BOT_|CLAUDE_|LOG_|SESSION_" | sed 's/=.*/=[HIDDEN]/'
```

### 📞 Getting Help

1. **Check Documentation**:
   - [Integration Guide](integration-guide.md) for deployment issues
   - [Developer API Reference](developer-api-reference.md) for code issues
   - [Architecture Diagrams](architecture_diagrams.md) for system understanding

2. **Community Resources**:
   - GitHub Issues: Report bugs and feature requests
   - Discussions: General questions and community support

3. **Professional Support**:
   - Commercial support available for production deployments
   - Custom integrations and enterprise features

4. **Debug Mode**:
   ```bash
   # Enable maximum logging
   LOG_LEVEL=DEBUG docker-compose up
   ```

## 🚀 Development Guide

### Local Development Setup

```bash
# 1. Clone and setup environment
git clone https://github.com/your-username/ai-interviewer-telegram-bot.git
cd ai-interviewer-telegram-bot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development tools

# 4. Setup pre-commit hooks
pre-commit install

# 5. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 6. Run tests
pytest

# 7. Start development server
python bot_enhanced.py
```

### Development Workflow

#### Code Style & Standards

```bash
# Format code with Black
black *.py

# Lint with flake8
flake8 *.py --max-line-length=88 --extend-ignore=E203,W503

# Type checking with mypy
mypy bot_enhanced.py --ignore-missing-imports

# Import sorting with isort
isort *.py --profile black
```

#### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_session_manager.py -v

# Run integration tests
pytest tests/test_integration.py -v --slow

# Load testing (for performance validation)
python load_test.py --users 25 --duration 300
```

#### Adding New Features

1. **New Interviewer Personality**:
   ```python
   # 1. Add to PromptVariant enum
   class PromptVariant(Enum):
       YOUR_NEW_STYLE = "your_new_style"
   
   # 2. Create prompt file
   # prompt_v6_your_new_style.md
   
   # 3. Add to PromptManager
   def load_prompts(self):
       self.prompts[PromptVariant.YOUR_NEW_STYLE] = self._load_prompt_file("prompt_v6_your_new_style.md")
   
   # 4. Update UI in start_command()
   keyboard.append([InlineKeyboardButton("🎨 Your New Style", callback_data="prompt_your_new_style")])
   ```

2. **Custom Session Storage Backend**:
   ```python
   from bot_enhanced import SessionManager
   
   class YourCustomSessionManager(SessionManager):
       def __init__(self, connection_string):
           super().__init__()
           self.connection = connection_string
       
       async def save_session(self, session):
           # Implement your storage logic
           pass
       
       async def load_session(self, user_id):
           # Implement your retrieval logic
           pass
   ```

3. **Additional Bot Commands**:
   ```python
   async def your_custom_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
       """Your custom command handler"""
       # Implementation
       pass
   
   # Register in _setup_handlers()
   def _setup_handlers(self):
       # ... existing handlers
       self.application.add_handler(CommandHandler("yourcmd", self.your_custom_command))
   ```

#### Database Migrations

For database-backed deployments:

```bash
# Create migration
alembic revision --autogenerate -m "Add new feature"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Extension Points

#### Custom Metrics Collection

```python
from bot_enhanced import MetricsCollector

class CustomMetricsCollector(MetricsCollector):
    def __init__(self, external_service_url: str):
        super().__init__()
        self.external_service = external_service_url
    
    async def track_custom_event(self, event_name: str, metadata: dict):
        # Send to external analytics service
        await self.send_to_external_service(event_name, metadata)
```

#### Interview Process Customization

```python
# Custom interview stage progression
class CustomInterviewStageManager:
    def __init__(self):
        self.custom_stages = [
            "greeting", "technical_background", "problem_solving",
            "architecture_discussion", "wrap_up"
        ]
    
    def get_next_stage(self, current_stage: str, completion: int) -> str:
        # Custom logic for stage transitions
        pass
```

## 🤝 Contributing

We welcome contributions! Here's how to get involved:

### 🌟 Ways to Contribute

- **🐛 Bug Reports**: Found an issue? [Open an issue](https://github.com/your-username/ai-interviewer-telegram-bot/issues)
- **💡 Feature Requests**: Have an idea? [Start a discussion](https://github.com/your-username/ai-interviewer-telegram-bot/discussions)
- **📝 Documentation**: Improve docs, add examples, fix typos
- **🔧 Code Contributions**: Bug fixes, new features, performance improvements
- **🧪 Testing**: Add test cases, improve test coverage
- **🎨 UI/UX**: Enhance user experience, improve bot interactions

### 📋 Contribution Process

1. **Fork the Repository**
   ```bash
   git fork https://github.com/your-username/ai-interviewer-telegram-bot.git
   cd ai-interviewer-telegram-bot
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # OR
   git checkout -b fix/issue-number
   ```

3. **Make Changes**
   - Follow code style guidelines (Black, flake8, mypy)
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

4. **Commit Changes**
   ```bash
   # Use conventional commits
   git commit -m "feat: add new interviewer personality for technical roles"
   git commit -m "fix: resolve session timeout issue in Redis backend"
   git commit -m "docs: update API documentation with new endpoints"
   ```

5. **Submit Pull Request**
   - Push to your fork: `git push origin feature/your-feature-name`
   - Open PR with clear description
   - Link related issues
   - Wait for review

### 📊 Development Standards

#### Code Quality Requirements

- **Test Coverage**: Minimum 80% coverage for new code
- **Code Style**: Black formatting, flake8 linting
- **Type Hints**: All public methods must have type hints
- **Documentation**: Docstrings for all classes and public methods
- **Performance**: No performance regressions in core paths

#### Commit Message Format

```
type(scope): description

- feat: new features
- fix: bug fixes  
- docs: documentation changes
- style: formatting, no code change
- refactor: code change that neither fixes bug nor adds feature
- test: adding tests
- chore: updating build tasks, package manager configs, etc

Examples:
feat(api): add Claude-4 model support
fix(sessions): handle corrupted session files gracefully
docs(readme): update deployment instructions
```

#### Pull Request Guidelines

- **Title**: Clear, descriptive title
- **Description**: What changed and why
- **Testing**: How was this tested?
- **Breaking Changes**: List any breaking changes
- **Screenshots**: For UI changes

### 🧪 Testing Guidelines

#### Required Tests

```python
# Unit tests for new functionality
def test_new_feature():
    # Arrange
    bot = create_test_bot()
    
    # Act
    result = bot.new_feature()
    
    # Assert
    assert result.status == "success"

# Integration tests
@pytest.mark.asyncio
async def test_end_to_end_interview():
    # Test complete interview flow
    pass

# Performance tests
def test_concurrent_sessions():
    # Test bot handles multiple sessions
    pass
```

#### Test Data

```python
# Use factories for test data
@pytest.fixture
def sample_session():
    return InterviewSession(
        user_id=12345,
        username="test_user",
        prompt_variant=PromptVariant.MASTER_INTERVIEWER,
        current_stage=InterviewStage.PROFILING
    )
```

### 🏷️ Release Process

#### Version Management

- Follow [Semantic Versioning](https://semver.org/)
- Update version in `__version__.py`
- Tag releases: `git tag -a v1.2.0 -m "Release v1.2.0"`

#### Release Notes

Include in each release:
- **New Features**: What's new
- **Bug Fixes**: What's fixed
- **Breaking Changes**: Migration guide
- **Dependencies**: Updated packages

### 🎯 Priority Areas

We especially welcome contributions in:

1. **🌍 Internationalization**: Multi-language support
2. **🎨 Interview Personalities**: New interviewer styles
3. **📊 Analytics**: Advanced metrics and insights
4. **🔌 Integrations**: New storage backends, external services
5. **🧪 Testing**: More comprehensive test coverage
6. **📖 Documentation**: Examples, tutorials, use cases

### 💬 Community

- **GitHub Discussions**: General questions, ideas, showcase
- **Issues**: Bug reports, feature requests
- **Discord**: Real-time community chat (coming soon)

## 📖 Documentation Suite

This project includes comprehensive documentation to support different user needs:

### 📚 Core Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| **[README.md](README.md)** | Main project overview and quick start | All users |
| **[Integration Guide](integration-guide.md)** | Deployment and integration patterns | DevOps, Integrators |
| **[Developer API Reference](developer-api-reference.md)** | Complete API documentation | Developers |
| **[Architecture Diagrams](architecture_diagrams.md)** | System architecture and component relationships | Architects, Developers |

### 🔧 Technical References

| Document | Purpose | Audience |
|----------|---------|----------|
| **[JSON Response Schema](json-response-schema.md)** | Claude AI response format specification | API Developers |
| **[API Documentation](api-documentation.yaml)** | OpenAPI/Swagger specification | Integration Developers |
| **[User Testing Guide](USER_TESTING_GUIDE.md)** | Manual testing procedures | QA, Testers |
| **[PythonAnywhere Deployment](PYTHONANYWHERE.md)** | Cloud deployment guide | DevOps |

### 🎯 Quick Navigation

**🚀 Getting Started**
- New to the project? Start with [Quick Start](#-quick-start)
- Want to deploy? See [Deployment Options](#-detailed-setup-options)
- Need help? Check [Troubleshooting](#-troubleshooting)

**👩‍💻 For Developers**
- API integration: [API Usage & Integration](#-api-usage--integration)
- Code reference: [Developer API Reference](developer-api-reference.md)
- System design: [Architecture Overview](#-architecture-overview)

**🏗️ For DevOps**
- Production setup: [Integration Guide](integration-guide.md)
- Performance tuning: [Performance & Monitoring](#-performance--monitoring)
- Security hardening: [Security Considerations](#-security-considerations)

**🤝 For Contributors**
- How to contribute: [Contributing](#-contributing)
- Development setup: [Development Guide](#-development-guide)
- Testing guidelines: Above in Contributing section

### 📋 Documentation Standards

All documentation follows these principles:

- **📱 Mobile-First**: Readable on all devices
- **🔍 Searchable**: Clear headings and structure
- **💡 Example-Rich**: Practical code examples
- **🔄 Up-to-Date**: Synchronized with code changes
- **🌍 Accessible**: Clear language, multiple skill levels

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 📜 License Summary

- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ❌ Liability limitations
- ❌ Warranty disclaimers

## 📞 Support & Contact

### 🆘 Getting Help

1. **📖 Documentation First**: Check this README and linked docs
2. **🔍 Search Issues**: Look for existing solutions in GitHub issues
3. **💬 Community**: Join discussions for general questions
4. **🐛 Bug Reports**: Create detailed issue reports

### 🏢 Commercial Support

Professional support available for:
- **🚀 Production Deployments**: Setup and optimization
- **🔧 Custom Integrations**: Tailored implementations  
- **📊 Analytics & Reporting**: Advanced metrics and dashboards
- **🎓 Training & Consulting**: Team training and best practices

Contact: [your-email@domain.com](mailto:your-email@domain.com)

### 🤝 Community

- **GitHub**: [Repository](https://github.com/your-username/ai-interviewer-telegram-bot)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/ai-interviewer-telegram-bot/discussions)
- **Issues**: [Bug Reports & Features](https://github.com/your-username/ai-interviewer-telegram-bot/issues)

---

<div align="center">

**🎯 AI Interviewer Telegram Bot** - *Professional knowledge extraction made simple*

[![⭐ Star on GitHub](https://img.shields.io/github/stars/your-username/ai-interviewer-telegram-bot?style=social)](https://github.com/your-username/ai-interviewer-telegram-bot)
[![🍴 Fork on GitHub](https://img.shields.io/github/forks/your-username/ai-interviewer-telegram-bot?style=social)](https://github.com/your-username/ai-interviewer-telegram-bot/fork)

Made with ❤️ by [Your Name](https://github.com/your-username)

</div>