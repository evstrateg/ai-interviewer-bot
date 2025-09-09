# 🛠️ AI Interviewer Bot - Developer Guide

*Complete guide for developers working with and extending the AI Interviewer Bot*

## 📋 Table of Contents

- [Development Setup](#development-setup)
- [Architecture Overview](#architecture-overview)
- [Core Components](#core-components)
- [Adding New Features](#adding-new-features)
- [Working with Prompts](#working-with-prompts)
- [Session Management](#session-management)
- [Voice Processing Development](#voice-processing-development)
- [Localization Development](#localization-development)
- [Testing and Debugging](#testing-and-debugging)
- [Performance Optimization](#performance-optimization)
- [Contributing Guidelines](#contributing-guidelines)

## 🚀 Development Setup

### Prerequisites

```bash
# Python 3.11+
python --version

# Git for version control
git --version

# Docker (optional but recommended)
docker --version

# FFmpeg (required for voice processing)
ffmpeg -version
```

### Local Development Environment

```bash
# 1. Clone the repository
git clone <repository-url>
cd ai-interviewer-telegram-bot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies
pip install pytest pytest-asyncio black flake8 mypy

# 5. Install voice processing dependencies
pip install assemblyai>=0.30.0 pydub>=0.25.1

# 6. Verify FFmpeg installation (required for audio processing)
ffmpeg -version || echo "Please install FFmpeg for voice processing"

# 7. Setup environment variables
cp .env.example .env
# Edit .env with your tokens:
# TELEGRAM_BOT_TOKEN=your_bot_token
# ANTHROPIC_API_KEY=your_api_key
# ASSEMBLYAI_API_KEY=your_assemblyai_key (for voice processing)
```

### IDE Setup

#### VS Code Configuration
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.testing.pytestEnabled": true,
  "files.associations": {
    "*.md": "markdown"
  }
}
```

#### PyCharm Configuration
- Set interpreter to `./venv/bin/python`
- Enable Black formatter
- Configure pytest as test runner
- Set up run configurations for main scripts

### Development Commands

```bash
# Format code
black *.py

# Lint code  
flake8 *.py

# Type checking
mypy *.py

# Run tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run bot locally
python telegram_bot.py

# Run enhanced bot
python bot_enhanced.py
```

## 🏗️ Architecture Overview

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram      │────│  Bot Framework  │────│  Claude AI      │
│   Bot API       │    │                 │    │  Integration    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                    ┌─────────────────┐
                    │ Session Manager │
                    └─────────────────┘
                              │
                    ┌─────────────────┐
                    │ File Storage /  │
                    │ Database        │
                    └─────────────────┘
```

### Directory Structure

```
ai-interviewer-telegram-bot/
├── telegram_bot.py              # Main bot implementation
├── bot_enhanced.py              # Enhanced version with metrics
├── config.py                    # Configuration management
├── requirements.txt             # Dependencies
├── docker-compose.yml           # Container orchestration
├── Dockerfile                   # Container definition
├── prompt_v*.md                 # Interview prompt variants
├── json_response_specifications.md
├── tests/                       # Test suite
│   ├── test_session_manager.py
│   ├── test_prompt_manager.py
│   └── test_claude_integration.py
├── sessions/                    # Local session storage
├── completed_sessions/          # Completed interviews
└── docs/                        # Documentation
```

## 🧩 Core Components

### 1. AIInterviewerBot Class

The main bot class handles Telegram interactions and interview orchestration.

```python
class AIInterviewerBot:
    """Main bot class handling Telegram integration and interview flow"""
    
    def __init__(self, telegram_token: str, anthropic_api_key: str):
        self.telegram_token = telegram_token
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.session_manager = SessionManager()
        self.prompt_manager = PromptManager()
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - entry point for new interviews"""
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process user messages and generate AI responses"""
        
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button presses"""
```

**Key Methods**:
- `start_command()` - Initialize new interview sessions
- `handle_message()` - Process user responses and generate questions  
- `handle_callback_query()` - Handle button interactions
- `_get_claude_response()` - Integration with Claude AI
- `_update_session_state()` - Manage interview progression

### 2. SessionManager Class

Manages interview session persistence and state tracking.

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

class SessionManager:
    """Handles session persistence and state management"""
    
    def __init__(self, storage_path: str = "sessions"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
    
    def save_session(self, session: InterviewSession):
        """Persist session to storage"""
        
    def load_session(self, user_id: int) -> Optional[InterviewSession]:
        """Load existing session from storage"""
        
    def delete_session(self, user_id: int):
        """Remove session from storage"""
```

**Extension Points**:
```python
# Add database storage backend
class DatabaseSessionManager(SessionManager):
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)
        
# Add Redis caching
class RedisSessionManager(SessionManager):
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)
```

### 3. PromptManager Class

Manages the different interviewer personality variants.

```python
class PromptManager:
    """Manages different prompt variants and interview styles"""
    
    def __init__(self):
        self.prompts = self._load_prompts()
    
    def get_prompt(self, variant: PromptVariant) -> str:
        """Get prompt template for specified variant"""
        
    def get_system_message(self, variant: PromptVariant, session: InterviewSession) -> str:
        """Generate contextual system message"""
        
    def _load_prompts(self) -> Dict[PromptVariant, str]:
        """Load prompt templates from markdown files"""
```

**Adding New Variants**:
```python
# 1. Add to enum
class PromptVariant(Enum):
    YOUR_VARIANT = "v6_your_variant"

# 2. Create prompt file
# prompt_v6_your_variant.md

# 3. Update prompt loading
prompt_files = {
    # ... existing variants
    PromptVariant.YOUR_VARIANT: "prompt_v6_your_variant.md"
}
```

### 4. ClaudeIntegration

Handles AI API interactions and response processing.

```python
class ClaudeIntegration:
    """Handles Claude AI API interactions"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    async def get_interview_response(
        self, 
        prompt: str, 
        user_message: str, 
        conversation_history: List[Dict]
    ) -> Dict[str, Any]:
        """Generate structured interview response"""
        
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate JSON response format"""
        
    def _handle_api_error(self, error: Exception) -> Dict[str, Any]:
        """Handle API errors with fallback responses"""
```

**Response Format**:
```python
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
        "stage_transition_ready": False
    }
}
```

## ➕ Adding New Features

### Adding New Commands

```python
# 1. Define command handler
async def your_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /yourcommand"""
    user_id = update.effective_user.id
    
    # Your command logic here
    await update.message.reply_text("Command response")

# 2. Register in _setup_handlers()
def _setup_handlers(self):
    # ... existing handlers
    self.application.add_handler(CommandHandler("yourcommand", self.your_command))
```

### Adding New Interview Stages

```python
# 1. Update InterviewStage enum
class InterviewStage(Enum):
    # ... existing stages
    YOUR_STAGE = "your_stage"

# 2. Update prompt templates to handle new stage

# 3. Update stage completeness initialization
def __post_init__(self):
    if not self.stage_completeness:
        self.stage_completeness = {stage.value: 0 for stage in InterviewStage}
```

### Adding Metrics and Analytics

```python
class MetricsCollector:
    """Collect and track bot performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'sessions_started': 0,
            'sessions_completed': 0,
            'messages_processed': 0,
            'api_calls': 0,
            'errors': 0
        }
    
    def increment(self, metric: str, value: int = 1):
        """Increment metric counter"""
        self.metrics[metric] = self.metrics.get(metric, 0) + value
    
    def get_metrics(self) -> Dict[str, int]:
        """Get current metrics snapshot"""
        return self.metrics.copy()

# Usage in bot
self.metrics = MetricsCollector()
self.metrics.increment('sessions_started')
```

### Adding Database Integration

```python
# models.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class InterviewSessionDB(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255))
    prompt_variant = Column(String(50))
    current_stage = Column(String(50))
    session_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# database.py
class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)
        self.SessionLocal = sessionmaker(self.engine, class_=AsyncSession)
    
    async def save_session(self, session: InterviewSession):
        """Save session to database"""
        async with self.SessionLocal() as db:
            db_session = InterviewSessionDB(
                user_id=session.user_id,
                username=session.username,
                prompt_variant=session.prompt_variant.value,
                current_stage=session.current_stage.value,
                session_data=asdict(session)
            )
            db.add(db_session)
            await db.commit()
```

## 🎨 Working with Prompts

### Prompt Template Structure

Each prompt variant follows this structure:

```markdown
# Interview Variant Name

## Core Directive
Brief description of the interviewer personality and approach.

## Response Format
Strict JSON format requirements.

## Stage Definitions
Detailed description of each interview stage.

## Behavioral Guidelines
- Communication style
- Progression rules  
- Engagement strategies

## Examples
Sample interactions showing the expected style.
```

### Creating Custom Prompts

```python
# 1. Create new prompt file: prompt_v6_custom.md
"""
# Custom Interviewer Variant

## Core Directive
You are a specialized interviewer focused on [your domain].
Your approach is [describe style and methodology].

## Response Format
[Include standard JSON format]

## Stage-Specific Adaptations
- **Greeting**: Focus on [specific area]
- **Profiling**: Emphasize [particular aspects]
- [Continue for all stages]

## Behavioral Guidelines
- Use [specific language style]
- Maintain [particular tone]
- Focus on [domain-specific areas]
"""

# 2. Update PromptVariant enum
class PromptVariant(Enum):
    CUSTOM = "v6_custom"

# 3. Update prompt loading
prompt_files = {
    PromptVariant.CUSTOM: "prompt_v6_custom.md"
}

# 4. Add to style selection menu
interview_styles = [
    ("🎯 Master Interviewer", PromptVariant.MASTER),
    ("📱 Telegram Optimized", PromptVariant.TELEGRAM_OPTIMIZED),
    ("💬 Conversational", PromptVariant.CONVERSATIONAL),
    ("🎪 Stage Specific", PromptVariant.STAGE_SPECIFIC), 
    ("🧠 Conversation Mgmt", PromptVariant.CONVERSATION_MGMT),
    ("🎨 Custom Style", PromptVariant.CUSTOM)  # New addition
]
```

### Dynamic Prompt Generation

```python
class DynamicPromptManager:
    """Generate prompts based on user characteristics"""
    
    def generate_custom_prompt(
        self, 
        user_role: str, 
        industry: str, 
        experience_level: str
    ) -> str:
        """Generate role-specific prompt"""
        
        base_template = self._get_base_template()
        customizations = self._get_role_customizations(user_role, industry)
        
        return base_template.format(**customizations)
    
    def _get_role_customizations(self, role: str, industry: str) -> Dict[str, str]:
        """Get role-specific customizations"""
        customizations = {
            'software_engineer': {
                'focus_areas': 'technical architecture, code quality, development processes',
                'key_questions': 'system design, debugging approaches, code review practices'
            },
            'product_manager': {
                'focus_areas': 'user needs, roadmap planning, stakeholder management',
                'key_questions': 'prioritization methods, success metrics, user feedback integration'
            }
        }
        return customizations.get(role, {})
```

## 💾 Session Management

### Session Lifecycle

```python
# Session States
1. CREATED     # New session initialized
2. ACTIVE      # Interview in progress
3. PAUSED      # Temporarily inactive
4. COMPLETED   # Successfully finished
5. ABANDONED   # Timed out or reset
6. ERROR       # Failed state

class SessionLifecycle:
    """Manage session state transitions"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    def transition_to(self, session: InterviewSession, new_state: str):
        """Handle state transitions with validation"""
        valid_transitions = {
            'CREATED': ['ACTIVE', 'ABANDONED'],
            'ACTIVE': ['PAUSED', 'COMPLETED', 'ABANDONED', 'ERROR'],
            'PAUSED': ['ACTIVE', 'ABANDONED'],
            'COMPLETED': [],  # Terminal state
            'ABANDONED': [],  # Terminal state
            'ERROR': ['ACTIVE', 'ABANDONED']  # Can recover
        }
        
        current_state = session.state
        if new_state not in valid_transitions.get(current_state, []):
            raise ValueError(f"Invalid transition from {current_state} to {new_state}")
        
        session.state = new_state
        session.last_activity = datetime.now()
        self.session_manager.save_session(session)
```

### Advanced Session Features

```python
# Session Backup and Recovery
class SessionBackupManager:
    """Handle session backup and recovery"""
    
    def create_checkpoint(self, session: InterviewSession):
        """Create session checkpoint"""
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'stage': session.current_stage.value,
            'completeness': session.stage_completeness.copy(),
            'key_insights': session.key_insights.copy(),
            'message_count': len(session.conversation_history)
        }
        
        checkpoint_file = f"checkpoints/{session.user_id}_{checkpoint['timestamp']}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
    
    def restore_from_checkpoint(self, session: InterviewSession, checkpoint_id: str):
        """Restore session from checkpoint"""
        # Implementation for recovery
        pass

# Session Analytics
class SessionAnalytics:
    """Analyze session patterns and performance"""
    
    def analyze_completion_rate(self) -> float:
        """Calculate interview completion rate"""
        total_sessions = self._count_total_sessions()
        completed_sessions = self._count_completed_sessions()
        return completed_sessions / total_sessions if total_sessions > 0 else 0.0
    
    def analyze_stage_performance(self) -> Dict[str, Dict[str, float]]:
        """Analyze average time and completion rate by stage"""
        # Implementation for stage analysis
        pass
    
    def identify_dropout_patterns(self) -> List[Dict[str, Any]]:
        """Identify common dropout points"""
        # Implementation for dropout analysis
        pass
```

## 🎤 Voice Processing Development

### Voice Handler Architecture (Updated SDK)

The voice processing system uses the latest AssemblyAI SDK with enterprise features:

```python
# voice_handler.py - Core Components with New SDK
import assemblyai as aai
from voice_handler import (
    VoiceMessageHandler,
    VoiceProcessingConfig, 
    VoiceTranscriptionResult,
    VoiceQuality,
    create_voice_handler
)

# Initialize AssemblyAI SDK
aai.settings.api_key = "your_api_key"

# Configuration with Advanced Features
config = VoiceProcessingConfig(
    assemblyai_api_key="your_api_key",
    max_file_size_mb=25,
    max_duration_seconds=600,
    confidence_threshold=0.6,
    default_language="en",
    supported_languages=["en", "ru", "es", "fr", "de"],  # 100+ supported
    enable_auto_language_detection=True,
    # New Advanced Features
    enable_speaker_labels=True,
    enable_pii_redaction=True,
    enable_sentiment_analysis=True,
    enable_topic_detection=True,
    enable_content_safety=True,
    enable_summarization=True
)

# Create handler with enhanced capabilities
voice_handler = VoiceMessageHandler(config)
```

### Processing Voice Messages

```python
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming voice messages"""
    user_id = update.effective_user.id
    
    try:
        # Process voice message with the handler
        result = await voice_handler.process_voice_message(
            update, 
            context,
            session_data=get_user_session_data(user_id)
        )
        
        if result.quality != VoiceQuality.FAILED:
            # Use transcribed text as user input
            await process_user_message(result.text, update, context)
            
            # Send transcription confirmation
            response = voice_handler.format_transcription_response(result)
            await update.message.reply_text(response)
        else:
            # Handle transcription failure
            await update.message.reply_text(
                "🎤 Sorry, I couldn't process your voice message. "
                "Please try speaking more clearly or use text."
            )
            
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        await update.message.reply_text(
            "🎤 Voice processing temporarily unavailable. Please use text."
        )
```

### Voice Processing Configuration

```python
# Advanced configuration options
voice_config = VoiceProcessingConfig(
    assemblyai_api_key=os.getenv("ASSEMBLYAI_API_KEY"),
    
    # File constraints
    max_file_size_mb=25,  # AssemblyAI limit
    min_duration_seconds=0.5,
    max_duration_seconds=600,  # 10 minutes
    
    # Quality thresholds
    confidence_threshold=0.6,
    
    # Language settings
    default_language="en",
    supported_languages=["en", "ru", "es", "fr"],
    enable_auto_language_detection=True,
    
    # AssemblyAI features
    enable_speaker_labels=False,  # For multi-speaker detection
    enable_punctuation=True,
    enable_format_text=True,
    
    # Performance settings
    concurrent_requests=3,
    retry_attempts=3,
    retry_delay_seconds=2.0
)
```

## 🌐 Localization Development

### Localization Architecture

The localization system provides comprehensive multi-language support:

```python
# localization.py - Core Components
from localization import (
    LocalizationManager,
    SupportedLanguage, 
    LanguagePreference,
    t,  # Translation function
    ts,  # Multiple translations
    set_language,
    detect_language
)

# Initialize localization manager
localization = LocalizationManager(default_language=SupportedLanguage.ENGLISH)

# Get translated text
welcome_text = t("welcome_greeting", user_id=12345, username="John")
```

### Adding New Translations

```python
# Extend localization manager with new language
class ExtendedLocalizationManager(LocalizationManager):
    """Extended localization with additional languages"""
    
    def _get_spanish_translations(self) -> Dict[str, str]:
        """Spanish translations"""
        return {
            "welcome_greeting": "¡Hola {username}! Soy un entrevistador de IA...",
            "begin_interview": "🚀 Comenzar Entrevista",
            "interview_complete": "🎉 ¡Entrevista Completa!",
            # ... more translations
        }
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load all translations including new language"""
        translations = super()._load_translations()
        translations["es"] = self._get_spanish_translations()
        return translations

# Usage with custom localization
class SupportedLanguage(Enum):
    ENGLISH = "en"
    RUSSIAN = "ru" 
    SPANISH = "es"  # New language

localization = ExtendedLocalizationManager()
```

### Dynamic Language Detection

```python
async def detect_user_language(update: Update) -> SupportedLanguage:
    """Detect user language from various sources"""
    
    # 1. Check explicit user preference
    user_id = update.effective_user.id
    stored_lang = localization.get_user_language(user_id)
    if stored_lang != localization.default_language:
        return stored_lang
    
    # 2. Detect from Telegram locale
    user = update.effective_user
    if hasattr(user, 'language_code') and user.language_code:
        detected_lang = localization.detect_language_from_locale(user.language_code)
        if detected_lang != localization.default_language:
            # Auto-set preference
            localization.set_user_language(user_id, detected_lang)
            return detected_lang
    
    # 3. Analyze message content (simple heuristic)
    if update.message and update.message.text:
        detected_lang = analyze_text_language(update.message.text)
        if detected_lang and detected_lang != localization.default_language:
            return SupportedLanguage(detected_lang)
    
    # 4. Default fallback
    return localization.default_language

def analyze_text_language(text: str) -> Optional[str]:
    """Simple language detection from text patterns"""
    # Cyrillic characters indicate Russian
    if any('\u0400' <= char <= '\u04FF' for char in text):
        return "ru"
    
    # Common Spanish words
    spanish_words = {"hola", "gracias", "por favor", "sí", "no"}
    words = set(text.lower().split())
    if len(words.intersection(spanish_words)) >= 2:
        return "es"
    
    return None
```

### Testing Voice and Localization Features

```python
def test_voice_processing():
    """Test voice processing functionality"""
    config = VoiceProcessingConfig(
        assemblyai_api_key="test_key",
        confidence_threshold=0.5
    )
    
    handler = VoiceMessageHandler(config)
    
    # Test configuration
    assert config.max_file_size_mb == 25
    assert config.confidence_threshold == 0.5
    
    print("✅ Voice processing tests passed")

def test_localization():
    """Test localization functionality"""
    # Test user preferences
    test_user_en = 12345
    test_user_ru = 67890
    
    set_language(test_user_en, SupportedLanguage.ENGLISH)
    set_language(test_user_ru, SupportedLanguage.RUSSIAN)
    
    # Test translations
    assert t("welcome_greeting", test_user_en, username="John") != ""
    assert t("welcome_greeting", test_user_ru, username="Иван") != ""
    
    # Test fallback
    assert t("nonexistent_key", test_user_en) == "[Missing: nonexistent_key]"
    
    print("✅ All localization tests passed")
```

## 🧪 Testing and Debugging

### Test Structure

```python
# tests/test_session_manager.py
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from telegram_bot import SessionManager, InterviewSession, PromptVariant, InterviewStage

class TestSessionManager:
    """Test session management functionality"""
    
    @pytest.fixture
    def session_manager(self):
        """Create session manager for testing"""
        return SessionManager(storage_path="test_sessions")
    
    @pytest.fixture
    def sample_session(self):
        """Create sample session for testing"""
        return InterviewSession(
            user_id=12345,
            username="testuser",
            prompt_variant=PromptVariant.MASTER,
            current_stage=InterviewStage.GREETING,
            stage_completeness={},
            conversation_history=[],
            start_time=datetime.now(),
            last_activity=datetime.now()
        )
    
    def test_save_and_load_session(self, session_manager, sample_session):
        """Test session persistence"""
        # Save session
        session_manager.save_session(sample_session)
        
        # Load session
        loaded_session = session_manager.load_session(sample_session.user_id)
        
        assert loaded_session is not None
        assert loaded_session.user_id == sample_session.user_id
        assert loaded_session.username == sample_session.username
    
    def test_session_timeout(self, session_manager):
        """Test session timeout handling"""
        # Create old session
        old_session = InterviewSession(
            user_id=99999,
            username="olduser",
            prompt_variant=PromptVariant.MASTER,
            current_stage=InterviewStage.GREETING,
            stage_completeness={},
            conversation_history=[],
            start_time=datetime.now() - timedelta(hours=4),
            last_activity=datetime.now() - timedelta(hours=4)
        )
        
        session_manager.save_session(old_session)
        
        # Should return None for expired session
        loaded_session = session_manager.load_session(
            old_session.user_id, 
            max_age_hours=3
        )
        assert loaded_session is None
```

### Integration Testing

```python
# tests/test_bot_integration.py
import pytest
from unittest.mock import AsyncMock, patch
from telegram import Update, User, Message
from telegram.ext import ContextTypes

@pytest.mark.asyncio
class TestBotIntegration:
    """Test full bot integration scenarios"""
    
    @pytest.fixture
    def mock_update(self):
        """Create mock Telegram update"""
        user = User(id=12345, first_name="Test", is_bot=False)
        message = Message(
            message_id=1,
            date=datetime.now(),
            chat=user,
            from_user=user,
            text="/start"
        )
        return Update(update_id=1, message=message)
    
    @pytest.fixture
    def mock_context(self):
        """Create mock context"""
        return AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
    
    async def test_start_command_flow(self, mock_update, mock_context):
        """Test complete /start command flow"""
        bot = AIInterviewerBot(
            telegram_token="test_token",
            anthropic_api_key="test_key"
        )
        
        with patch.object(bot, '_get_claude_response', new_callable=AsyncMock) as mock_claude:
            mock_claude.return_value = {
                "interview_stage": "greeting",
                "response": "Hello! Welcome to the interview.",
                "metadata": {"question_depth": 1, "completeness": 0}
            }
            
            await bot.start_command(mock_update, mock_context)
            
            # Verify session was created
            session = bot.session_manager.load_session(12345)
            assert session is not None
            assert session.current_stage == InterviewStage.GREETING
```

### Debugging Tools

```python
# debug_tools.py
class BotDebugger:
    """Debugging utilities for bot development"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    def dump_session_state(self, user_id: int):
        """Dump complete session state for debugging"""
        session = self.bot.session_manager.load_session(user_id)
        if not session:
            print(f"No session found for user {user_id}")
            return
        
        print(f"=== Session State for User {user_id} ===")
        print(f"Username: {session.username}")
        print(f"Prompt Variant: {session.prompt_variant.value}")
        print(f"Current Stage: {session.current_stage.value}")
        print(f"Question Depth: {session.question_depth}")
        print(f"Engagement Level: {session.engagement_level}")
        print(f"Stage Completeness: {session.stage_completeness}")
        print(f"Key Insights: {len(session.key_insights)}")
        print(f"Conversation Length: {len(session.conversation_history)}")
    
    def simulate_user_message(self, user_id: int, message: str):
        """Simulate user message for testing"""
        # Create mock update and context
        # Process through bot handlers
        # Return response for inspection
        pass
    
    def validate_json_responses(self, user_id: int):
        """Validate all JSON responses in session history"""
        session = self.bot.session_manager.load_session(user_id)
        if not session:
            return []
        
        invalid_responses = []
        for i, msg in enumerate(session.conversation_history):
            if msg['role'] == 'assistant':
                try:
                    json.loads(msg['content'])
                except json.JSONDecodeError as e:
                    invalid_responses.append({
                        'message_index': i,
                        'error': str(e),
                        'content': msg['content']
                    })
        
        return invalid_responses

# Usage
debugger = BotDebugger(bot_instance)
debugger.dump_session_state(12345)
invalid_json = debugger.validate_json_responses(12345)
```

## ⚡ Performance Optimization

### Async Best Practices

```python
# Efficient Claude API usage
class OptimizedClaudeIntegration:
    """Optimized Claude API integration with connection pooling"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(
            api_key=api_key,
            max_retries=3,
            timeout=30.0
        )
        self._rate_limiter = asyncio.Semaphore(10)  # Limit concurrent requests
    
    async def get_interview_response(self, prompt: str, user_message: str) -> Dict[str, Any]:
        """Rate-limited API request"""
        async with self._rate_limiter:
            try:
                response = await self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_message}
                    ]
                )
                return self._parse_response(response.content[0].text)
            except Exception as e:
                logger.error(f"Claude API error: {e}")
                return self._create_fallback_response()

# Efficient session caching
class CachedSessionManager(SessionManager):
    """Session manager with in-memory caching"""
    
    def __init__(self, storage_path: str = "sessions", cache_size: int = 1000):
        super().__init__(storage_path)
        self._cache = {}
        self._cache_order = []
        self._max_cache_size = cache_size
    
    async def load_session(self, user_id: int) -> Optional[InterviewSession]:
        """Load session with caching"""
        # Check cache first
        if user_id in self._cache:
            self._update_cache_order(user_id)
            return self._cache[user_id]
        
        # Load from storage
        session = await super().load_session(user_id)
        if session:
            self._add_to_cache(user_id, session)
        
        return session
    
    def _add_to_cache(self, user_id: int, session: InterviewSession):
        """Add session to cache with LRU eviction"""
        if len(self._cache) >= self._max_cache_size:
            oldest_user = self._cache_order.pop(0)
            del self._cache[oldest_user]
        
        self._cache[user_id] = session
        self._cache_order.append(user_id)
```

### Memory Management

```python
# Efficient conversation history management
class TruncatedConversationHistory:
    """Manage conversation history with size limits"""
    
    def __init__(self, max_messages: int = 100, max_chars_per_message: int = 2000):
        self.max_messages = max_messages
        self.max_chars_per_message = max_chars_per_message
    
    def add_message(self, history: List[Dict[str, Any]], role: str, content: str) -> List[Dict[str, Any]]:
        """Add message with automatic truncation"""
        # Truncate content if too long
        if len(content) > self.max_chars_per_message:
            content = content[:self.max_chars_per_message] + "... [truncated]"
        
        # Add new message
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        history.append(message)
        
        # Truncate history if too long
        if len(history) > self.max_messages:
            # Keep first few messages (context) and recent messages
            context_messages = history[:5]  # Keep greeting and profiling
            recent_messages = history[-(self.max_messages-5):]
            history = context_messages + recent_messages
        
        return history

# Background session cleanup
class SessionCleanupService:
    """Background service for session maintenance"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self._cleanup_task = None
    
    async def start(self):
        """Start background cleanup task"""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop(self):
        """Stop background cleanup"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
    
    async def _cleanup_loop(self):
        """Periodic cleanup of expired sessions"""
        while True:
            try:
                await self._cleanup_expired_sessions()
                await self._compact_session_files()
                await asyncio.sleep(3600)  # Run every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
```

## 🤝 Contributing Guidelines

### Code Style Standards

```python
# Follow PEP 8 with these specific guidelines:

# 1. Line length: 100 characters (not 79)
# 2. Use type hints for all functions
# 3. Use descriptive variable names
# 4. Add docstrings for all public methods

# Example function:
async def process_interview_response(
    self, 
    user_message: str, 
    session: InterviewSession,
    context: ContextTypes.DEFAULT_TYPE
) -> Dict[str, Any]:
    """
    Process user response and generate next interview question.
    
    Args:
        user_message: The user's response text
        session: Current interview session state
        context: Telegram bot context
    
    Returns:
        Dictionary containing bot response and updated session data
        
    Raises:
        ClaudeAPIError: If Claude API call fails
        SessionValidationError: If session state is invalid
    """
    # Implementation here
    pass
```

### Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes and test
python -m pytest
python -m black *.py
python -m flake8 *.py

# 3. Commit with descriptive messages
git add .
git commit -m "feat: add conversation recovery mechanism

- Add session backup checkpoints
- Implement recovery from interruptions  
- Add tests for recovery scenarios"

# 4. Push and create PR
git push origin feature/your-feature-name
# Create PR through GitHub/GitLab interface
```

### Pull Request Checklist

- [ ] All tests pass (`pytest`)
- [ ] Code formatted with Black (`black *.py`)
- [ ] Linting passes (`flake8 *.py`)  
- [ ] Type checking passes (`mypy *.py`)
- [ ] Documentation updated for new features
- [ ] Changelog entry added
- [ ] Manual testing completed

### Testing Requirements

```python
# All new features must include:

# 1. Unit tests for individual functions
def test_stage_progression():
    """Test interview stage progression logic"""
    pass

# 2. Integration tests for user flows  
async def test_complete_interview_flow():
    """Test complete interview from start to finish"""
    pass

# 3. Error handling tests
def test_claude_api_failure_recovery():
    """Test graceful handling of API failures"""
    pass

# 4. Performance tests for critical paths
def test_session_loading_performance():
    """Test session loading under high concurrency"""
    pass
```

### Release Process

1. **Version Bumping**: Update version in `__version__ = "x.y.z"`
2. **Changelog**: Add entry to CHANGELOG.md
3. **Testing**: Run full test suite including integration tests
4. **Documentation**: Update documentation and API references  
5. **Docker**: Build and test Docker images
6. **Deployment**: Deploy to staging environment first
7. **Release**: Create GitHub release with binaries and changelog

### Getting Help

- **Technical Questions**: Open GitHub Issues with `question` label
- **Bug Reports**: Use bug report template with reproduction steps
- **Feature Requests**: Use feature request template with use case
- **Security Issues**: Email security@yourproject.com (private disclosure)

---

*This developer guide provides comprehensive information for extending and maintaining the AI Interviewer Bot. For user-focused documentation, see the [User Guide](END_USER_GUIDE.md) and [API Documentation](../api/developer-api-reference.md).*