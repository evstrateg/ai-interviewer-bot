# AI Interviewer Telegram Bot - API Documentation Suite

## Overview

This comprehensive API documentation suite provides everything developers need to understand, integrate with, and extend the AI Interviewer Telegram Bot. The bot conducts structured professional knowledge extraction interviews using Claude AI through a sophisticated 9-stage process.

## Documentation Structure

### 📋 [OpenAPI/Swagger Specification](./api-documentation.yaml)
Complete OpenAPI 3.0 specification covering all bot APIs, endpoints, and data models. Use this for:
- API client generation
- Interactive API exploration
- Contract validation
- Integration planning

**Key Features:**
- Telegram Bot webhook endpoints
- Session management APIs
- Claude integration interfaces
- Prompt management endpoints
- Comprehensive data schemas

### 📖 [Developer API Reference](./developer-api-reference.md)
Comprehensive technical reference for all classes, methods, and integration patterns. Includes:
- Core class documentation
- Method signatures and parameters
- Data structure specifications
- Code examples and usage patterns
- Error handling strategies
- Testing methodologies

**Target Audience:** Developers extending or maintaining the bot

### 🚀 [Integration Guide](./integration-guide.md)
Practical guide for integrating with and extending the bot system. Contains:
- Quick start setup
- SDK-style usage examples
- Integration patterns (webhook, database, analytics)
- Production deployment configurations
- Monitoring and troubleshooting
- Load testing strategies

**Target Audience:** Developers deploying or integrating the bot

### 🔧 [JSON Response Schema](./json-response-schema.md)
Detailed specification for the structured JSON responses from Claude AI. Covers:
- Complete schema definition
- Field-by-field documentation
- Usage examples and patterns
- Validation rules and error handling
- Integration best practices

**Target Audience:** Developers working with Claude API responses

### 📊 [JSON Response Format (Original)](./json_response_specifications.md)
Original specification document defining the Claude AI response format. Reference for:
- Response structure requirements
- Stage progression logic
- Metadata field definitions
- Error handling specifications

## Quick Start

### Basic Setup
```bash
# Clone repository
git clone <repository-url>
cd ai-interviewer-bot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the bot
python bot_enhanced.py
```

### Environment Variables
```bash
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional
SESSION_TIMEOUT_MINUTES=180
CLAUDE_MODEL=claude-3-5-sonnet-20241022
LOG_LEVEL=INFO
```

## Core Architecture

### System Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram      │    │   Bot Core       │    │   Claude AI     │
│   Users         │◄──►│   (Enhanced)     │◄──►│   Integration   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Session        │
                       │   Management     │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Persistence    │
                       │   (File/DB)      │
                       └──────────────────┘
```

### Interview Flow

```
Greeting (3-5min) → Profiling (10min) → Essence (15min) → Operations (20min) → 
Expertise Map (20min) → Failure Modes (20min) → Mastery (15min) → 
Growth Path (15min) → Wrap Up (5min)
```

## Key Features

### 🎯 Multiple Interviewer Styles
- **Master**: Comprehensive systematic approach
- **Telegram Optimized**: Mobile-friendly concise messages
- **Conversational**: Natural flow with systematic coverage
- **Stage Specific**: Detailed approach for each stage
- **Conversation Management**: Advanced recovery and adaptation

### 📊 Progress Tracking
- Real-time stage completion monitoring
- Question depth progression (1-4 levels)
- User engagement assessment (high/medium/low)
- Example collection counting
- Key insight extraction

### 🔄 Session Management
- Persistent session storage
- Automatic timeout handling
- Cross-platform compatibility
- Session analytics and reporting

### 🚨 Error Handling
- Graceful Claude API failures
- JSON parsing fallbacks
- Automatic retry logic
- User-friendly error messages

## API Endpoints Summary

### Bot Commands
| Command | Description | Response |
|---------|-------------|----------|
| `/start` | Begin interview | Prompt selection interface |
| `/status` | Show progress | Stage completion summary |
| `/reset` | Clear session | Session reset confirmation |
| `/complete` | End interview | Completion summary |
| `/metrics` | Show stats | Bot performance data |

### Session Management
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/sessions` | GET | List active sessions |
| `/sessions` | POST | Create new session |
| `/sessions/{user_id}` | GET | Get user session |
| `/sessions/{user_id}` | PUT | Update session |
| `/sessions/{user_id}` | DELETE | Remove session |

### Claude Integration
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/claude/interview-response` | POST | Generate AI response |

## Data Models

### InterviewSession
Core session state containing:
- User identification and metadata
- Current interview stage and progress
- Conversation history with timestamps
- Progress tracking metrics
- Key insights and examples collected

### ClaudeResponse
Structured AI response format:
- Interview stage identifier
- User-facing response message
- Progress metadata (depth, completion, engagement)
- Internal tracking data
- Error information if applicable

### PromptVariant
Interview personality configurations:
- Variant identifier and description
- System prompt content
- Usage guidelines and characteristics

## Integration Patterns

### SDK-Style Usage
```python
from interviewer_sdk import InterviewerSDK

sdk = InterviewerSDK(telegram_token, anthropic_key)
await sdk.create_interview_session(user_id, username)
response = await sdk.send_message(user_id, "I'm a developer")
status = sdk.get_session_status(user_id)
```

### Webhook Integration
```python
@app.route('/webhook', methods=['POST'])
def webhook():
    update_data = request.get_json()
    # Process Telegram update
    bot.process_update(update_data)
    return {"status": "ok"}
```

### Database Integration
```python
class DatabaseSessionManager(SessionManager):
    def save_session(self, session):
        # Save to PostgreSQL/MySQL
        
    def load_session(self, user_id):
        # Load from database
```

## Testing

### Unit Testing
```python
@pytest.mark.asyncio
async def test_interview_flow():
    bot = AIInterviewerBot(test_token, test_key)
    session = create_test_session()
    response = await bot.handle_message(test_update)
    assert response['interview_stage'] == 'profiling'
```

### Load Testing
```python
async def load_test(concurrent_users=50):
    tasks = [simulate_user_session(i) for i in range(concurrent_users)]
    await asyncio.gather(*tasks)
```

## Deployment Options

### Docker
```dockerfile
FROM python:3.11-slim
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "bot_enhanced.py"]
```

### Docker Compose
```yaml
services:
  ai-interviewer:
    build: .
    environment:
      - TELEGRAM_BOT_TOKEN=${TOKEN}
      - ANTHROPIC_API_KEY=${API_KEY}
  postgres:
    image: postgres:15
```

### PythonAnywhere
```python
# wsgi.py
from bot_enhanced import EnhancedAIInterviewerBot
bot = EnhancedAIInterviewerBot(token, api_key)
bot.run()
```

## Monitoring & Analytics

### Performance Metrics
- Active sessions count
- Message processing rate
- API call success/failure rates
- Average session duration
- Stage completion rates

### Real-time Monitoring
```python
monitor = InterviewMonitor(bot)
await monitor.start_monitoring(port=8765)
# WebSocket dashboard at ws://localhost:8765
```

### Analytics Dashboard
```python
analytics = InterviewAnalytics(session_manager)
engagement_data = analytics.analyze_engagement_patterns()
report = analytics.generate_completion_report()
```

## Error Handling

### Common Issues
- **Bot not responding**: Check webhook configuration
- **Session persistence**: Verify storage directory permissions
- **Claude API errors**: Validate API key and rate limits
- **JSON parsing**: Enable fallback response handling

### Debugging Tools
```python
# Test Claude connectivity
await diagnose_claude_issues(api_key)

# Check session files
diagnose_session_issues()

# Test webhook endpoint
test_webhook(bot_token, webhook_url)
```

## Support & Resources

### Documentation Files
- `api-documentation.yaml` - OpenAPI specification
- `developer-api-reference.md` - Technical API reference
- `integration-guide.md` - Integration and deployment guide
- `json-response-schema.md` - Claude response format specification

### Code Examples
- Session management patterns
- Custom prompt integration
- Performance monitoring
- Database persistence
- Real-time analytics

### Testing Resources
- Unit test examples
- Integration test patterns
- Load testing scripts
- Mock data generators

## Version Information

- **API Version**: 1.0.0
- **Python Version**: 3.8+
- **Claude Model**: claude-3-5-sonnet-20241022
- **Telegram Bot API**: Compatible with latest version

---

This documentation suite provides comprehensive coverage of the AI Interviewer Telegram Bot system. Each document serves a specific purpose and audience, ensuring developers can quickly find the information they need for their use case.

For questions or contributions, please refer to the project repository and follow the contribution guidelines.