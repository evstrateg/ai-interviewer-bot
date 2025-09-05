# Telegram Bot Implementation for AI Interviewer

## Bot Configuration

### Basic Setup
```python
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import json
from datetime import datetime
import anthropic

class AIInterviewerBot:
    def __init__(self, telegram_token, anthropic_api_key):
        self.telegram_token = telegram_token
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        self.user_sessions = {}  # Store interview states
        
    async def start_command(self, update: Update, context):
        """Handle /start command"""
        user_id = update.effective_user.id
        
        # Initialize user session
        self.user_sessions[user_id] = {
            'stage': 'greeting',
            'stage_progress': {},
            'conversation_history': [],
            'start_time': datetime.now(),
            'completeness': 0
        }
        
        keyboard = [
            [InlineKeyboardButton("Begin Interview 🎯", callback_data="start_interview")],
            [InlineKeyboardButton("Learn About Process 📋", callback_data="learn_more")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = """
🤖 **AI Knowledge Interviewer**

I'm here to help extract and structure your professional expertise through a comprehensive interview process.

**What to expect:**
• 9 structured stages covering your professional knowledge
• 90-120 minutes of engaging conversation  
• Deep dive into your expertise and experience
• One question at a time for focused responses

Ready to begin?
        """
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
```

### Interview Session Management
```python
class InterviewSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.current_stage = 'greeting'
        self.stage_completeness = {
            'greeting': 0,
            'profiling': 0, 
            'essence': 0,
            'operations': 0,
            'expertise_map': 0,
            'failure_modes': 0,
            'mastery': 0,
            'growth_path': 0,
            'wrap_up': 0
        }
        self.conversation_history = []
        self.insights_collected = []
        self.examples_count = 0
        self.depth_level = 1
        
    def add_message(self, role, content, metadata=None):
        """Add message to conversation history"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now(),
            'stage': self.current_stage,
            'metadata': metadata or {}
        }
        self.conversation_history.append(message)
        
    def get_context_for_llm(self):
        """Prepare conversation context for LLM"""
        # Get last 10 messages to maintain context without overwhelming
        recent_history = self.conversation_history[-10:]
        
        context = f"""
Current Interview Stage: {self.current_stage}
Stage Completeness: {self.stage_completeness[self.current_stage]}%
Current Question Depth: {self.depth_level}
Examples Collected: {self.examples_count}

Recent Conversation:
"""
        for msg in recent_history:
            context += f"{msg['role']}: {msg['content']}\n"
            
        return context
```

### Claude Sonnet-4 Integration
```python
async def generate_interview_response(self, user_message, session):
    """Generate interview response using Claude Sonnet-4"""
    
    # Select appropriate prompt based on session state
    if session.current_stage == 'greeting':
        system_prompt = self.load_prompt('greeting_stage')
    elif session.current_stage in ['profiling', 'essence']:
        system_prompt = self.load_prompt('exploration_stage') 
    elif session.current_stage in ['operations', 'expertise_map']:
        system_prompt = self.load_prompt('detailed_extraction')
    else:
        system_prompt = self.load_prompt('master_interviewer')
    
    # Prepare the conversation context
    context = session.get_context_for_llm()
    
    # Construct the prompt
    full_prompt = f"""
{system_prompt}

{context}