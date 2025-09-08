# Interview Agent Prompts

This directory contains all the AI prompt templates and configurations used by the interview agent system.

## Available Prompts

### Core Interview Prompts
- **[Master Interviewer Prompt v1](./prompt_v1_master_interviewer.md)** - Original comprehensive interviewer prompt
- **[Telegram Optimized Prompt v2](./prompt_v2_telegram_optimized.md)** - Optimized for Telegram bot interactions
- **[Conversational Balanced Prompt v3](./prompt_v3_conversational_balanced.md)** - Balanced approach for natural conversations
- **[Stage-Specific Prompt v4](./prompt_v4_stage_specific.md)** - Different prompts for different interview stages
- **[Conversation Management Prompt v5](./prompt_v5_conversation_management.md)** - Advanced conversation flow management

## Prompt Evolution

### Version History
1. **v1 - Master Interviewer**: Comprehensive but rigid interview approach
2. **v2 - Telegram Optimized**: Adapted for messaging platform constraints
3. **v3 - Conversational Balanced**: Natural dialogue with professional structure
4. **v4 - Stage-Specific**: Contextual prompts based on interview phase
5. **v5 - Conversation Management**: Advanced flow control and user experience

### Current Active Prompt
**Version 5 (Conversation Management)** is currently used in production, providing:
- Adaptive conversation flow
- Context-aware responses
- Professional yet approachable tone
- Multi-language support integration
- Error handling and recovery

## Prompt Usage

### Integration Points
- **OpenAI GPT Models**: Primary AI engine for interview conversations
- **Language Processing**: Multi-language prompt variations
- **Context Management**: Session-aware prompt modification
- **Response Formatting**: Structured output for system processing

### Configuration
Prompts are configured through:
- Environment variables for dynamic content
- JSON configuration files for structured prompts
- Database settings for user-specific customizations
- API endpoints for real-time prompt updates

### Best Practices
1. **Maintain Professional Tone**: Keep interviews respectful and structured
2. **Cultural Sensitivity**: Adapt prompts for different languages and cultures
3. **Clear Instructions**: Ensure AI understands expected behavior
4. **Error Handling**: Include fallback responses for unexpected situations
5. **Version Control**: Track changes and test thoroughly before deployment

---
*Return to [Documentation Hub](../docs/README.md)*