# AI Interviewer Telegram Bot - Developer API Reference

## Table of Contents

1. [Overview](#overview)
2. [Core Classes](#core-classes)
3. [Data Structures](#data-structures)
4. [API Methods](#api-methods)
5. [Integration Examples](#integration-examples)
6. [Error Handling](#error-handling)
7. [Configuration](#configuration)
8. [Testing](#testing)

## Overview

The AI Interviewer Telegram Bot is a sophisticated system for conducting structured professional knowledge extraction interviews. This document provides comprehensive API reference for developers who want to extend, integrate with, or modify the bot.

### Architecture Components

- **AIInterviewerBot**: Main bot controller
- **EnhancedAIInterviewerBot**: Enhanced version with persistence and monitoring
- **SessionManager**: Handles interview session persistence
- **ClaudeIntegration**: AI response generation via Claude API
- **PromptManager**: Manages multiple interviewer personalities
- **MetricsCollector**: Tracks bot performance and usage

## Core Classes

### AIInterviewerBot

The main bot implementation handling Telegram interactions.

#### Constructor

```python
def __init__(self, telegram_token: str, anthropic_api_key: str):
    """
    Initialize the AI Interviewer Bot.
    
    Args:
        telegram_token (str): Telegram Bot API token
        anthropic_api_key (str): Anthropic Claude API key
    """
```

#### Key Methods

##### start_command(update, context)
```python
async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command - displays welcome message and prompt selection.
    
    Args:
        update: Telegram Update object
        context: Bot context
        
    Returns:
        None - sends inline keyboard with prompt variants
    """
```

##### handle_message(update, context)
```python
async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Process user messages during interview.
    
    Args:
        update: Telegram Update object containing user message
        context: Bot context
        
    Flow:
        1. Validate active session exists
        2. Add user message to conversation history
        3. Generate AI response via Claude
        4. Update session state from response metadata
        5. Check for stage transitions
        6. Send response to user
    """
```

##### button_callback(update, context)
```python
async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle inline keyboard button presses.
    
    Args:
        update: Telegram Update object with callback query
        context: Bot context
        
    Handles:
        - Prompt variant selection (prompt_*)
        - Interview start (start_interview)
        - Help information (learn_more)
    """
```

### EnhancedAIInterviewerBot

Extended version with session persistence and enhanced error handling.

#### Additional Features

- Session persistence to disk
- Automatic session cleanup
- Enhanced error recovery
- Performance metrics tracking
- Background job scheduling

#### Constructor

```python
def __init__(self, telegram_token: str, anthropic_api_key: str):
    """
    Initialize enhanced bot with session management and metrics.
    
    Creates:
        - SessionManager for persistence
        - MetricsCollector for tracking
        - Periodic cleanup tasks
    """
```

#### Enhanced Methods

##### handle_message(update, context)
```python
async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Enhanced message handling with retry logic and error recovery.
    
    Features:
        - Automatic API retry with exponential backoff
        - Graceful error handling with user feedback
        - Session state preservation
        - Metrics tracking
    """
```

### SessionManager

Manages interview session persistence and lifecycle.

#### Constructor

```python
def __init__(self, storage_dir: str = "sessions"):
    """
    Initialize session manager with file-based storage.
    
    Args:
        storage_dir (str): Directory for session files
    """
```

#### Key Methods

##### create_session(user_id, username, variant)
```python
def create_session(self, user_id: int, username: str, variant: PromptVariant) -> InterviewSession:
    """
    Create new interview session.
    
    Args:
        user_id (int): Telegram user ID
        username (str): User display name
        variant (PromptVariant): Selected prompt variant
        
    Returns:
        InterviewSession: New session object
        
    Side Effects:
        - Saves session to disk
        - Logs session creation
        - Updates metrics
    """
```

##### get_session(user_id)
```python
def get_session(self, user_id: int) -> Optional[InterviewSession]:
    """
    Retrieve session for user, checking validity.
    
    Args:
        user_id (int): Telegram user ID
        
    Returns:
        InterviewSession or None: Active session if valid
        
    Validation:
        - Checks session timeout (default: 3 hours)
        - Removes expired sessions automatically
    """
```

### ClaudeIntegration

Handles AI response generation via Anthropic Claude API.

#### Constructor

```python
def __init__(self, api_key: str):
    """
    Initialize Claude integration.
    
    Args:
        api_key (str): Anthropic API key
        
    Configuration:
        - Model: claude-sonnet-4-20250514
        - Max tokens: 1000
        - Temperature: 0.7
    """
```

#### Key Methods

##### generate_interview_response(session, user_message, prompt_manager)
```python
async def generate_interview_response(self, 
                                    session: InterviewSession, 
                                    user_message: str,
                                    prompt_manager: PromptManager) -> Dict[str, Any]:
    """
    Generate structured interview response.
    
    Args:
        session: Current interview session
        user_message: User's latest message
        prompt_manager: For accessing prompt variants
        
    Returns:
        Dict containing:
            - interview_stage: Current stage code
            - response: Interviewer message
            - metadata: Progress tracking data
            - internal_tracking: Session state updates
            - error: Error code if generation failed
            
    Process:
        1. Build conversation context
        2. Get system prompt for variant
        3. Call Claude API
        4. Parse JSON response
        5. Validate structure
        6. Return structured data
    """
```

### PromptManager

Manages multiple interviewer prompt variants.

#### Constructor

```python
def __init__(self):
    """
    Load all prompt variants from markdown files.
    
    Variants loaded:
        - v1_master: prompt_v1_master_interviewer.md
        - v2_telegram: prompt_v2_telegram_optimized.md
        - v3_conversational: prompt_v3_conversational_balanced.md
        - v4_stage_specific: prompt_v4_stage_specific.md
        - v5_conversation_mgmt: prompt_v5_conversation_management.md
    """
```

#### Key Methods

##### get_prompt(variant)
```python
def get_prompt(self, variant: PromptVariant) -> str:
    """
    Get system prompt for specified variant.
    
    Args:
        variant (PromptVariant): Prompt variant enum
        
    Returns:
        str: Complete system prompt text
        
    Fallback: Returns basic prompt if file not found
    """
```

##### get_variant_description(variant)
```python
def get_variant_description(self, variant: PromptVariant) -> str:
    """
    Get human-readable description for UI display.
    
    Args:
        variant (PromptVariant): Prompt variant enum
        
    Returns:
        str: Description with emoji and explanation
    """
```

## Data Structures

### InterviewSession

Core data structure representing an interview session.

```python
@dataclass
class InterviewSession:
    """Interview session state"""
    user_id: int                              # Telegram user ID
    username: str                             # Display name
    prompt_variant: PromptVariant             # Selected interviewer style
    current_stage: InterviewStage             # Current interview stage
    stage_completeness: Dict[str, int]        # Completion % per stage
    conversation_history: List[Dict[str, Any]] # Complete message log
    start_time: datetime                      # Session start timestamp
    last_activity: datetime                   # Last user interaction
    question_depth: int = 1                   # Current question depth (1-4)
    engagement_level: str = "medium"          # User engagement (high/medium/low)
    examples_collected: int = 0               # Number of examples gathered
    key_insights: List[str] = None            # Important insights discovered
```

#### Methods

##### add_message(role, content, metadata)
```python
def add_message(self, role: str, content: str, metadata: Dict = None):
    """
    Add message to conversation history.
    
    Args:
        role (str): 'user' or 'assistant'
        content (str): Message content
        metadata (Dict): Optional metadata
        
    Automatic fields:
        - timestamp: Current ISO timestamp
        - stage: Current interview stage
        - last_activity: Updates to current time
    """
```

### PromptVariant

Enumeration of available interviewer personalities.

```python
class PromptVariant(Enum):
    """Available prompt variants for the interviewer"""
    MASTER = "v1_master"                    # Comprehensive systematic approach
    TELEGRAM_OPTIMIZED = "v2_telegram"     # Mobile-friendly concise messages
    CONVERSATIONAL = "v3_conversational"   # Natural flow with systematic coverage
    STAGE_SPECIFIC = "v4_stage_specific"    # Detailed approach per stage
    CONVERSATION_MGMT = "v5_conversation_mgmt"  # Advanced recovery and adaptation
```

### InterviewStage

Enumeration of the 9-stage interview process.

```python
class InterviewStage(Enum):
    """Interview stages according to specification"""
    GREETING = "greeting"           # Initial rapport building (3-5 min)
    PROFILING = "profiling"         # Expert background mapping (10 min)
    ESSENCE = "essence"             # Core role philosophy (15 min)
    OPERATIONS = "operations"       # Daily work processes (20 min)
    EXPERTISE_MAP = "expertise_map" # Knowledge hierarchy (20 min)
    FAILURE_MODES = "failure_modes" # Error patterns and prevention (20 min)
    MASTERY = "mastery"            # Expert-level insights (15 min)
    GROWTH_PATH = "growth_path"     # Professional development timeline (15 min)
    WRAP_UP = "wrap_up"            # Interview conclusion (5 min)
```

## API Methods

### Bot Command Handlers

All command handlers follow the same signature pattern:

```python
async def command_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command handler documentation"""
    pass
```

#### Available Commands

| Command | Description | Parameters | Response |
|---------|-------------|------------|----------|
| `/start` | Begin new interview | None | Prompt selection keyboard |
| `/status` | Show progress | None | Stage completion status |
| `/reset` | Clear session | None | Confirmation message |
| `/help` | Show help | None | Usage instructions |
| `/complete` | End interview | None | Completion summary |
| `/metrics` | Show stats | None | Bot performance metrics |

### Session API Methods

#### Create Session
```python
session = session_manager.create_session(
    user_id=12345,
    username="john_doe", 
    variant=PromptVariant.CONVERSATIONAL
)
```

#### Update Session
```python
session.add_message("user", "I work in software development")
session_manager.update_session(session)
```

#### Get Session
```python
session = session_manager.get_session(user_id=12345)
if session:
    print(f"Current stage: {session.current_stage}")
```

### Claude API Integration

#### Generate Response
```python
response = await claude.generate_interview_response(
    session=current_session,
    user_message="I've been a developer for 5 years",
    prompt_manager=prompt_manager
)

# Response structure
{
    "interview_stage": "profiling",
    "response": "What type of development do you primarily focus on?",
    "metadata": {
        "question_depth": 2,
        "completeness": 30,
        "engagement_level": "medium"
    },
    "internal_tracking": {
        "key_insights": ["5 years experience"],
        "examples_collected": 0,
        "follow_up_needed": ["specific technologies"],
        "stage_transition_ready": false
    }
}
```

## Integration Examples

### Basic Bot Setup

```python
from config import config
from bot_enhanced import EnhancedAIInterviewerBot

# Initialize bot
bot = EnhancedAIInterviewerBot(
    telegram_token=config.telegram_token,
    anthropic_api_key=config.anthropic_api_key
)

# Run bot
bot.run()
```

### Custom Command Handler

```python
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom command example"""
    user_id = update.effective_user.id
    
    # Get user session
    session = bot.session_manager.get_session(user_id)
    if not session:
        await update.message.reply_text("No active session")
        return
    
    # Process custom logic
    await update.message.reply_text(f"Stage: {session.current_stage.value}")

# Add to bot
bot.application.add_handler(CommandHandler("custom", custom_command))
```

### Session Analysis

```python
def analyze_session(session: InterviewSession) -> Dict[str, Any]:
    """Analyze completed interview session"""
    duration = datetime.now() - session.start_time
    
    return {
        "duration_minutes": duration.total_seconds() / 60,
        "message_count": len(session.conversation_history),
        "avg_stage_completion": sum(session.stage_completeness.values()) / 9,
        "key_insights": len(session.key_insights),
        "examples_collected": session.examples_collected,
        "engagement_level": session.engagement_level
    }
```

### Custom Metrics Collection

```python
class CustomMetrics(MetricsCollector):
    """Extended metrics collection"""
    
    def __init__(self):
        super().__init__()
        self.metrics.update({
            'average_session_duration': 0,
            'completion_rate': 0,
            'popular_prompt_variant': 'unknown'
        })
    
    def calculate_advanced_metrics(self, sessions: List[InterviewSession]):
        """Calculate advanced metrics from session data"""
        if not sessions:
            return
            
        # Average duration
        durations = [
            (datetime.now() - s.start_time).total_seconds() / 60 
            for s in sessions
        ]
        self.metrics['average_session_duration'] = sum(durations) / len(durations)
        
        # Completion rate
        completed = sum(1 for s in sessions if s.current_stage == InterviewStage.WRAP_UP)
        self.metrics['completion_rate'] = (completed / len(sessions)) * 100
        
        # Popular variant
        variants = [s.prompt_variant.value for s in sessions]
        self.metrics['popular_prompt_variant'] = max(set(variants), key=variants.count)
```

## Error Handling

### Exception Types

The bot handles several types of errors gracefully:

#### API Errors
```python
try:
    response = await claude.generate_interview_response(session, message, prompt_manager)
except anthropic.APIError as e:
    # Handle Claude API errors
    fallback_response = create_fallback_response(session, message)
    
except asyncio.TimeoutError as e:
    # Handle timeout errors
    await update.message.reply_text("Response taking longer than expected...")
```

#### Session Errors
```python
try:
    session = session_manager.get_session(user_id)
    if not session:
        await update.message.reply_text("No active session. Use /start to begin.")
        return
        
except SessionExpiredError as e:
    await update.message.reply_text("Session expired. Starting fresh...")
    session_manager.remove_session(user_id)
```

#### JSON Parsing Errors
```python
def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
    """Parse JSON response with error handling"""
    try:
        # Try to extract JSON
        parsed = json.loads(response_text)
        
        # Validate required fields
        required_fields = ['interview_stage', 'response', 'metadata']
        if not all(field in parsed for field in required_fields):
            raise ValueError("Missing required fields")
            
        return parsed
        
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"JSON parsing failed: {e}")
        
        # Return fallback structure
        return {
            'interview_stage': 'greeting',
            'response': response_text,  # Use raw text
            'metadata': {
                'question_depth': 1,
                'completeness': 10,
                'engagement_level': 'medium'
            },
            'error': 'JSON_PARSE_FAILED'
        }
```

### Error Response Codes

| Error Code | Description | Recovery Action |
|------------|-------------|-----------------|
| `JSON_PARSE_FAILED` | AI response not valid JSON | Use raw text response |
| `API_ERROR` | Claude API call failed | Retry with backoff |
| `API_RETRY_FAILED` | All retries exhausted | Use fallback response |
| `SESSION_EXPIRED` | User session timed out | Prompt to restart |
| `INVALID_STAGE` | Unknown interview stage | Reset to greeting |

## Configuration

### Environment Variables

Required configuration via `.env` file:

```bash
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional bot settings
BOT_USERNAME=ai_interviewer_bot
BOT_NAME="AI Interviewer"

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=text  # or json

# Session management
SESSION_TIMEOUT_MINUTES=180
MAX_CONVERSATION_HISTORY=100

# Claude API
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_MAX_TOKENS=1000
CLAUDE_TEMPERATURE=0.7
```

### BotConfig Class

```python
from config import config

# Access configuration
print(f"Using Claude model: {config.claude_model}")
print(f"Session timeout: {config.session_timeout_minutes} minutes")

# Validate configuration
try:
    config.validate()
    print("Configuration valid")
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Testing

### Unit Testing

```python
import pytest
from unittest.mock import Mock, AsyncMock
from telegram_bot import AIInterviewerBot, InterviewSession

@pytest.mark.asyncio
async def test_start_command():
    """Test /start command handler"""
    bot = AIInterviewerBot("fake_token", "fake_api_key")
    
    # Mock Telegram objects
    update = Mock()
    update.effective_user.id = 12345
    update.effective_user.username = "testuser"
    update.message.reply_text = AsyncMock()
    
    # Execute command
    await bot.start_command(update, None)
    
    # Verify response
    update.message.reply_text.assert_called_once()
    call_args = update.message.reply_text.call_args
    assert "AI Professional Knowledge Interviewer" in call_args[0][0]
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_interview_flow():
    """Test complete interview flow"""
    bot = AIInterviewerBot("fake_token", "fake_api_key")
    
    # Mock Claude response
    bot.claude.generate_interview_response = AsyncMock(return_value={
        'interview_stage': 'profiling',
        'response': 'Tell me about your background',
        'metadata': {
            'question_depth': 1,
            'completeness': 20,
            'engagement_level': 'medium'
        }
    })
    
    # Create session
    session = InterviewSession(
        user_id=12345,
        username="testuser",
        prompt_variant=PromptVariant.CONVERSATIONAL,
        current_stage=InterviewStage.GREETING,
        stage_completeness={},
        conversation_history=[],
        start_time=datetime.now(),
        last_activity=datetime.now()
    )
    
    bot.sessions[12345] = session
    
    # Test message handling
    update = Mock()
    update.effective_user.id = 12345
    update.message.text = "I'm a software developer"
    update.message.reply_text = AsyncMock()
    
    context = Mock()
    context.bot.send_chat_action = AsyncMock()
    
    await bot.handle_message(update, context)
    
    # Verify session updated
    assert len(session.conversation_history) == 2  # user + assistant
    assert session.conversation_history[0]['role'] == 'user'
    assert session.conversation_history[1]['role'] == 'assistant'
```

### Load Testing

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

async def simulate_user_session(bot, user_id):
    """Simulate a complete user session"""
    messages = [
        "I'm a software engineer with 5 years experience",
        "I work primarily in Python and JavaScript",
        "I lead a team of 3 developers",
        "We use agile methodologies"
    ]
    
    # Create session
    session = bot.session_manager.create_session(
        user_id, f"user_{user_id}", PromptVariant.CONVERSATIONAL
    )
    
    # Send messages
    for message in messages:
        await bot.claude.generate_interview_response(session, message, bot.prompt_manager)
        await asyncio.sleep(0.1)  # Simulate typing delay

async def load_test(concurrent_users=10):
    """Test bot under load"""
    bot = EnhancedAIInterviewerBot("fake_token", "fake_api_key")
    
    start_time = time.time()
    
    # Create concurrent user sessions
    tasks = [
        simulate_user_session(bot, user_id) 
        for user_id in range(concurrent_users)
    ]
    
    await asyncio.gather(*tasks)
    
    duration = time.time() - start_time
    print(f"Load test completed: {concurrent_users} users in {duration:.2f}s")
    
    # Check metrics
    metrics = bot.metrics.get_metrics()
    print(f"Sessions started: {metrics['sessions_started']}")
    print(f"API calls: {metrics['api_calls']}")
    print(f"Errors: {metrics['errors_occurred']}")

# Run load test
asyncio.run(load_test(50))
```

---

This comprehensive API reference provides everything developers need to understand, extend, and integrate with the AI Interviewer Telegram Bot system. For additional examples and implementation details, refer to the source code and OpenAPI specification.