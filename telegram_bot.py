#!/usr/bin/env python3
"""
AI Interviewer Telegram Bot MVP
Professional Knowledge Extraction System

Features:
- 5 different interviewer prompt variants
- Claude Sonnet-4 integration
- JSON response handling
- Session management
- Interview state tracking
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Voice processing imports (optional)
try:
    from voice_handler import VoiceMessageHandler, VoiceProcessingConfig, VoiceQuality
    VOICE_PROCESSING_AVAILABLE = True
except ImportError:
    VOICE_PROCESSING_AVAILABLE = False

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class PromptVariant(Enum):
    """Available prompt variants for the interviewer"""
    MASTER = "v1_master"
    TELEGRAM_OPTIMIZED = "v2_telegram"
    CONVERSATIONAL = "v3_conversational"
    STAGE_SPECIFIC = "v4_stage_specific"
    CONVERSATION_MGMT = "v5_conversation_mgmt"

class InterviewStage(Enum):
    """Interview stages according to specification"""
    GREETING = "greeting"
    PROFILING = "profiling"
    ESSENCE = "essence"
    OPERATIONS = "operations"
    EXPERTISE_MAP = "expertise_map"
    FAILURE_MODES = "failure_modes"
    MASTERY = "mastery"
    GROWTH_PATH = "growth_path"
    WRAP_UP = "wrap_up"

@dataclass
class InterviewSession:
    """Interview session state"""
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
    
    def __post_init__(self):
        if self.key_insights is None:
            self.key_insights = []
        if not self.stage_completeness:
            self.stage_completeness = {stage.value: 0 for stage in InterviewStage}
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add message to conversation history"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'stage': self.current_stage.value,
            'metadata': metadata or {}
        }
        self.conversation_history.append(message)
        self.last_activity = datetime.now()

class PromptManager:
    """Manages different prompt variants"""
    
    def __init__(self):
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[PromptVariant, str]:
        """Load all prompt variants from files"""
        prompts = {}
        
        prompt_files = {
            PromptVariant.MASTER: "prompt_v1_master_interviewer.md",
            PromptVariant.TELEGRAM_OPTIMIZED: "prompt_v2_telegram_optimized.md", 
            PromptVariant.CONVERSATIONAL: "prompt_v3_conversational_balanced.md",
            PromptVariant.STAGE_SPECIFIC: "prompt_v4_stage_specific.md",
            PromptVariant.CONVERSATION_MGMT: "prompt_v5_conversation_management.md"
        }
        
        for variant, filename in prompt_files.items():
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    prompts[variant] = f.read()
                logger.info(f"Loaded prompt variant: {variant.value}")
            except FileNotFoundError:
                logger.error(f"Prompt file not found: {filename}")
                # Fallback basic prompt
                prompts[variant] = self._get_basic_prompt()
        
        return prompts
    
    def _get_basic_prompt(self) -> str:
        """Fallback basic prompt if files not found"""
        return """
You are an AI interviewer conducting professional knowledge extraction interviews.
Follow the 9-stage interview process and always respond in JSON format.
Ask one question at a time and dig deeper into responses.
        """
    
    def get_prompt(self, variant: PromptVariant) -> str:
        """Get prompt for specified variant"""
        return self.prompts.get(variant, self._get_basic_prompt())
    
    def get_variant_description(self, variant: PromptVariant) -> str:
        """Get human-readable description of prompt variant"""
        descriptions = {
            PromptVariant.MASTER: "🎯 Master Interviewer - Comprehensive and systematic approach",
            PromptVariant.TELEGRAM_OPTIMIZED: "📱 Telegram Optimized - Mobile-friendly with concise messages", 
            PromptVariant.CONVERSATIONAL: "💬 Conversational Balance - Natural flow with systematic coverage",
            PromptVariant.STAGE_SPECIFIC: "🎪 Stage Specific - Detailed approach for each interview stage",
            PromptVariant.CONVERSATION_MGMT: "🧠 Conversation Management - Advanced recovery and adaptation"
        }
        return descriptions.get(variant, "Unknown variant")

class ClaudeIntegration:
    """Claude Sonnet-4 integration for interview responses"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"  # Latest Claude Sonnet-4 model
        
    async def generate_interview_response(self, 
                                        session: InterviewSession, 
                                        user_message: str,
                                        prompt_manager: PromptManager) -> Dict[str, Any]:
        """Generate interview response using Claude"""
        try:
            # Get system prompt for current variant
            system_prompt = prompt_manager.get_prompt(session.prompt_variant)
            
            # Build conversation context
            context = self._build_context(session, user_message)
            
            # Generate response
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=1000,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": context}]
            )
            
            # Parse response
            response_text = response.content[0].text
            return self._parse_json_response(response_text)
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return self._create_fallback_response(session, user_message)
    
    def _build_context(self, session: InterviewSession, user_message: str) -> str:
        """Build conversation context for Claude"""
        # Get recent conversation history (last 5 exchanges)
        recent_history = session.conversation_history[-10:]
        
        context = f"""
Current Interview State:
- Stage: {session.current_stage.value}
- Question Depth: {session.question_depth}
- Engagement Level: {session.engagement_level}
- Examples Collected: {session.examples_collected}
- Stage Completeness: {session.stage_completeness[session.current_stage.value]}%

Recent Conversation History:
"""
        for msg in recent_history:
            context += f"{msg['role']}: {msg['content']}\n"
        
        context += f"\nuser: {user_message}\n\nPlease respond in the specified JSON format."
        
        return context
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from Claude"""
        try:
            # Try to extract JSON from response
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                # Look for JSON-like structure
                json_text = response_text.strip()
            
            parsed = json.loads(json_text)
            
            # Validate required fields
            if not all(key in parsed for key in ['interview_stage', 'response', 'metadata']):
                raise ValueError("Missing required fields in JSON response")
            
            return parsed
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Response text: {response_text}")
            
            # Extract plain text response as fallback
            return {
                'interview_stage': 'greeting',
                'response': response_text,
                'metadata': {
                    'question_depth': 1,
                    'completeness': 10,
                    'engagement_level': 'medium'
                },
                'error': 'JSON_PARSE_FAILED'
            }
    
    def _create_fallback_response(self, session: InterviewSession, user_message: str) -> Dict[str, Any]:
        """Create fallback response when API fails"""
        return {
            'interview_stage': session.current_stage.value,
            'response': "I apologize, but I'm experiencing technical difficulties. Could you please repeat your response?",
            'metadata': {
                'question_depth': session.question_depth,
                'completeness': session.stage_completeness[session.current_stage.value],
                'engagement_level': session.engagement_level
            },
            'error': 'API_ERROR'
        }

class AIInterviewerBot:
    """Main AI Interviewer Telegram Bot"""
    
    def __init__(self, telegram_token: str, anthropic_api_key: str, assemblyai_api_key: Optional[str] = None):
        self.telegram_token = telegram_token
        self.prompt_manager = PromptManager()
        self.claude = ClaudeIntegration(anthropic_api_key)
        self.sessions: Dict[int, InterviewSession] = {}
        
        # Initialize voice processing if available and configured
        self.voice_handler = None
        if VOICE_PROCESSING_AVAILABLE and assemblyai_api_key:
            try:
                voice_config = VoiceProcessingConfig(
                    assemblyai_api_key=assemblyai_api_key,
                    max_file_size_mb=25,
                    min_duration_seconds=0.5,
                    max_duration_seconds=600,
                    confidence_threshold=0.6,
                    default_language="en",
                    supported_languages=["en", "ru", "es", "fr", "de"],
                    enable_auto_language_detection=True
                )
                self.voice_handler = VoiceMessageHandler(voice_config)
                logger.info("Voice processing enabled with AssemblyAI")
            except Exception as e:
                logger.error(f"Failed to initialize voice processing: {e}")
                self.voice_handler = None
        elif assemblyai_api_key:
            logger.warning("Voice processing requested but voice_handler module not available")
        
        # Build application
        self.application = Application.builder().token(telegram_token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup Telegram bot handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("reset", self.reset_command))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Voice message handlers (if voice processing is available)
        if self.voice_handler:
            self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))
            self.application.add_handler(MessageHandler(filters.AUDIO, self.handle_voice_message))
            logger.info("Voice message handlers added")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name
        
        welcome_message = f"""🤖 <b>AI Professional Knowledge Interviewer</b>

Hello {username}! I'm an AI interviewer specialized in extracting deep professional insights through structured conversations.

<b>What I do:</b>
• Conduct 9-stage professional knowledge interviews
• Extract implicit expertise and best practices  
• Ask one focused question at a time
• Adapt to your communication style
• Generate comprehensive insights

<b>Interview Duration:</b> 90-120 minutes
<b>Method:</b> Systematic questioning with adaptive deepening

Choose your preferred interview style:"""
        
        keyboard = [
            [InlineKeyboardButton("🎯 Master Interviewer", callback_data=f"prompt_{PromptVariant.MASTER.value}")],
            [InlineKeyboardButton("📱 Telegram Optimized", callback_data=f"prompt_{PromptVariant.TELEGRAM_OPTIMIZED.value}")],
            [InlineKeyboardButton("💬 Conversational Balance", callback_data=f"prompt_{PromptVariant.CONVERSATIONAL.value}")],
            [InlineKeyboardButton("🎪 Stage Specific", callback_data=f"prompt_{PromptVariant.STAGE_SPECIFIC.value}")],
            [InlineKeyboardButton("🧠 Conversation Management", callback_data=f"prompt_{PromptVariant.CONVERSATION_MGMT.value}")],
            [InlineKeyboardButton("ℹ️ Learn More", callback_data="learn_more")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='HTML')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        username = query.from_user.username or query.from_user.first_name
        
        if query.data.startswith("prompt_"):
            # Prompt selection
            variant_value = query.data.replace("prompt_", "")
            try:
                variant = PromptVariant(variant_value)
                await self._start_interview(query, user_id, username, variant)
            except ValueError:
                await query.edit_message_text("Invalid prompt selection. Please try again.")
                
        elif query.data == "learn_more":
            await self._show_prompt_details(query)
        elif query.data == "start_interview":
            await self._begin_interview(query, user_id)
    
    async def _show_prompt_details(self, query):
        """Show details about prompt variants"""
        details = """
**📋 Interview Styles Explained:**

🎯 **Master Interviewer**
• Most comprehensive approach
• Systematic knowledge extraction
• Best for detailed documentation

📱 **Telegram Optimized** 
• Mobile-friendly messages
• Concise but thorough
• Great for quick interviews

💬 **Conversational Balance**
• Natural conversation flow
• Maintains systematic coverage
• Most comfortable experience

🎪 **Stage Specific**
• Detailed approach per stage
• Specialized questioning
• Comprehensive coverage

🧠 **Conversation Management**
• Advanced recovery protocols
• Handles complex situations
• Most robust option

Select your preferred style to begin!
"""
        
        keyboard = [
            [InlineKeyboardButton("🎯 Master", callback_data=f"prompt_{PromptVariant.MASTER.value}"),
             InlineKeyboardButton("📱 Telegram", callback_data=f"prompt_{PromptVariant.TELEGRAM_OPTIMIZED.value}")],
            [InlineKeyboardButton("💬 Conversational", callback_data=f"prompt_{PromptVariant.CONVERSATIONAL.value}"),
             InlineKeyboardButton("🎪 Stage Specific", callback_data=f"prompt_{PromptVariant.STAGE_SPECIFIC.value}")],
            [InlineKeyboardButton("🧠 Conversation Mgmt", callback_data=f"prompt_{PromptVariant.CONVERSATION_MGMT.value}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(details, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _start_interview(self, query, user_id: int, username: str, variant: PromptVariant):
        """Initialize interview session"""
        # Create new session
        session = InterviewSession(
            user_id=user_id,
            username=username,
            prompt_variant=variant,
            current_stage=InterviewStage.GREETING,
            stage_completeness={},
            conversation_history=[],
            start_time=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.sessions[user_id] = session
        
        confirmation_message = f"""
✅ **Interview Setup Complete**

**Selected Style:** {self.prompt_manager.get_variant_description(variant)}

**Interview Process:**
1. **Greeting** - Building rapport (3-5 min)
2. **Profiling** - Your background (10 min) 
3. **Essence** - Role philosophy (15 min)
4. **Operations** - Work processes (20 min)
5. **Expertise Map** - Knowledge levels (20 min)
6. **Failure Modes** - Common mistakes (20 min)
7. **Mastery** - Expert insights (15 min) 
8. **Growth Path** - Development timeline (15 min)
9. **Wrap Up** - Final validation (5 min)

**Ready to begin?** Click below to start your interview!
"""
        
        keyboard = [[InlineKeyboardButton("🚀 Begin Interview", callback_data="start_interview")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(confirmation_message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _begin_interview(self, query, user_id: int):
        """Begin the actual interview"""
        if user_id not in self.sessions:
            await query.edit_message_text("Session expired. Please use /start to begin again.")
            return
        
        session = self.sessions[user_id]
        
        # Generate first question
        initial_response = await self.claude.generate_interview_response(
            session, 
            "I'm ready to begin the interview",
            self.prompt_manager
        )
        
        # Update session state
        session.add_message("assistant", initial_response['response'], initial_response.get('metadata'))
        
        await query.edit_message_text(
            f"**🎤 Interview Started**\n\n{initial_response['response']}", 
            parse_mode='Markdown'
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user messages during interview"""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        if user_id not in self.sessions:
            await update.message.reply_text(
                "No active interview session. Please use /start to begin an interview."
            )
            return
        
        session = self.sessions[user_id]
        
        # Add user message to history
        session.add_message("user", user_message)
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
        
        # Generate response
        response_data = await self.claude.generate_interview_response(
            session, user_message, self.prompt_manager
        )
        
        # Update session state from response metadata
        if 'metadata' in response_data:
            metadata = response_data['metadata']
            session.question_depth = metadata.get('question_depth', session.question_depth)
            session.engagement_level = metadata.get('engagement_level', session.engagement_level)
            
            # Update stage completeness
            stage = response_data.get('interview_stage', session.current_stage.value)
            completeness = metadata.get('completeness', 0)
            session.stage_completeness[stage] = completeness
            
            # Check for stage transitions
            if completeness >= 80:
                await self._handle_stage_transition(session, update, response_data)
                return
        
        # Add response to history
        session.add_message("assistant", response_data['response'], response_data.get('metadata'))
        
        # Send response to user
        response_text = response_data['response']
        if 'error' in response_data:
            response_text += f"\n\n*[Technical issue: {response_data['error']}]*"
        
        await update.message.reply_text(response_text, parse_mode='Markdown')
    
    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages by transcribing and processing as text"""
        if not self.voice_handler:
            await update.message.reply_text(
                "🎤 Voice messages are not supported in this configuration. Please use text messages."
            )
            return
        
        user_id = update.effective_user.id
        
        # Check if user has an active session
        if user_id not in self.sessions:
            await update.message.reply_text(
                "🎤 Please start an interview first using /start to send voice messages."
            )
            return
        
        try:
            # Show processing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
            await update.message.reply_text(
                "🎤 Processing your voice message... This may take a moment."
            )
            
            # Process voice message
            transcription_result = await self.voice_handler.process_voice_message(
                update, context, session_data={'user_id': user_id}
            )
            
            # Handle transcription result
            if transcription_result.quality == VoiceQuality.FAILED:
                error_message = self.voice_handler.format_transcription_response(transcription_result)
                await update.message.reply_text(error_message)
                return
            
            # Send transcription confirmation
            transcription_message = self.voice_handler.format_transcription_response(transcription_result)
            await update.message.reply_text(transcription_message, parse_mode='Markdown')
            
            # Process transcribed text as regular message
            if transcription_result.text.strip():
                # Update the message text to be the transcribed text for processing
                # We'll simulate a text message with the transcribed content
                session = self.sessions[user_id]
                
                # Add voice message metadata to session
                voice_metadata = {
                    'message_type': 'voice',
                    'duration': transcription_result.duration_seconds,
                    'confidence': transcription_result.confidence,
                    'quality': transcription_result.quality.value,
                    'language': transcription_result.language,
                    'processing_time': transcription_result.processing_time_seconds
                }
                
                # Add user message to history with voice metadata
                session.add_message("user", transcription_result.text, voice_metadata)
                
                # Generate response
                response_data = await self.claude.generate_interview_response(
                    session, transcription_result.text, self.prompt_manager
                )
                
                # Update session state from response metadata
                if 'metadata' in response_data:
                    metadata = response_data['metadata']
                    session.question_depth = metadata.get('question_depth', session.question_depth)
                    session.engagement_level = metadata.get('engagement_level', session.engagement_level)
                    
                    # Update stage completeness
                    stage = response_data.get('interview_stage', session.current_stage.value)
                    completeness = metadata.get('completeness', 0)
                    session.stage_completeness[stage] = completeness
                    
                    # Check for stage transitions
                    if completeness >= 80:
                        await self._handle_stage_transition(session, update, response_data)
                        return
                
                # Add response to history
                session.add_message("assistant", response_data['response'], response_data.get('metadata'))
                
                # Send response to user
                response_text = response_data['response']
                if 'error' in response_data:
                    response_text += f"\n\n*[Technical issue: {response_data['error']}]*"
                
                await update.message.reply_text(response_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Voice message processing failed: {e}")
            await update.message.reply_text(
                "🎤 I encountered an error processing your voice message. Please try again or use text instead."
            )
    
    async def _handle_stage_transition(self, session: InterviewSession, update: Update, response_data: Dict):
        """Handle transition between interview stages"""
        current_stage_index = list(InterviewStage).index(session.current_stage)
        
        # Check if this is the last stage
        if current_stage_index >= len(InterviewStage) - 1:
            await self._complete_interview(session, update)
            return
        
        # Move to next stage
        next_stage = list(InterviewStage)[current_stage_index + 1]
        session.current_stage = next_stage
        session.question_depth = 1  # Reset depth for new stage
        
        # Notify user of stage transition
        stage_names = {
            InterviewStage.PROFILING: "Profiling (Background)",
            InterviewStage.ESSENCE: "Essence (Role Philosophy)", 
            InterviewStage.OPERATIONS: "Operations (Work Processes)",
            InterviewStage.EXPERTISE_MAP: "Expertise Map (Knowledge Levels)",
            InterviewStage.FAILURE_MODES: "Failure Modes (Common Mistakes)",
            InterviewStage.MASTERY: "Mastery (Expert Insights)",
            InterviewStage.GROWTH_PATH: "Growth Path (Development)",
            InterviewStage.WRAP_UP: "Wrap Up (Final Questions)"
        }
        
        transition_message = f"""
📊 **Stage Complete!** 

✅ Previous stage finished with {session.stage_completeness[list(InterviewStage)[current_stage_index].value]}% completeness

🎯 **Moving to:** {stage_names.get(next_stage, next_stage.value)}

{response_data['response']}
"""
        
        session.add_message("assistant", response_data['response'], response_data.get('metadata'))
        await update.message.reply_text(transition_message, parse_mode='Markdown')
    
    async def _complete_interview(self, session: InterviewSession, update: Update):
        """Complete the interview and provide summary"""
        end_time = datetime.now()
        duration = end_time - session.start_time
        
        summary = f"""
🎉 **Interview Complete!**

**Session Summary:**
• Duration: {duration.total_seconds() // 60:.0f} minutes
• Messages exchanged: {len(session.conversation_history)}
• Examples collected: {session.examples_collected}
• Key insights: {len(session.key_insights)}

**Stages Completed:**
"""
        
        for stage in InterviewStage:
            completeness = session.stage_completeness.get(stage.value, 0)
            status = "✅" if completeness >= 80 else "⚠️" if completeness >= 50 else "❌"
            summary += f"{status} {stage.value.title()}: {completeness}%\n"
        
        summary += """
**Thank you for participating!** Your professional insights have been valuable.

Use /reset to start a new interview or /status to review this session.
"""
        
        await update.message.reply_text(summary, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current interview status"""
        user_id = update.effective_user.id
        
        if user_id not in self.sessions:
            await update.message.reply_text("No active interview session.")
            return
        
        session = self.sessions[user_id]
        current_time = datetime.now()
        duration = current_time - session.start_time
        
        status_message = f"""
📊 **Interview Status**

**Current Stage:** {session.current_stage.value.title()}
**Duration:** {duration.total_seconds() // 60:.0f} minutes
**Question Depth:** {session.question_depth}/4
**Engagement:** {session.engagement_level}
**Examples:** {session.examples_collected}

**Progress:**
"""
        
        for stage in InterviewStage:
            completeness = session.stage_completeness.get(stage.value, 0)
            if stage == session.current_stage:
                status_message += f"▶️ **{stage.value.title()}**: {completeness}%\n"
            elif completeness > 0:
                status_message += f"✅ {stage.value.title()}: {completeness}%\n"
            else:
                status_message += f"⏳ {stage.value.title()}: 0%\n"
        
        await update.message.reply_text(status_message, parse_mode='Markdown')
    
    async def reset_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reset current session"""
        user_id = update.effective_user.id
        
        if user_id in self.sessions:
            del self.sessions[user_id]
        
        await update.message.reply_text(
            "🔄 Session reset complete. Use /start to begin a new interview."
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help information"""
        help_text = """
🤖 **AI Interviewer Bot Commands**

**/start** - Begin new interview
**/status** - Check current progress  
**/reset** - Reset current session
**/help** - Show this help

**Interview Process:**
This bot conducts structured professional interviews to extract your expertise and knowledge. The process follows 9 stages from greeting to completion.

**Tips for Best Results:**
• Provide detailed, specific responses
• Share concrete examples from your experience
• Be open about your professional challenges
• Take your time - quality over speed

**Interview typically takes 90-120 minutes**
"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def setup_bot_commands(self):
        """Setup bot commands menu in Telegram"""
        commands = [
            BotCommand("start", "🚀 Begin new interview"),
            BotCommand("status", "📊 Check interview progress"),
            BotCommand("reset", "🔄 Reset current session"),
            BotCommand("help", "❓ Get help and instructions"),
        ]
        await self.application.bot.set_my_commands(commands)
        logger.info("Bot commands menu configured")
    
    def run(self):
        """Run the bot"""
        logger.info("Starting AI Interviewer Bot...")
        
        # Setup commands menu
        async def setup_commands():
            await self.setup_bot_commands()
        
        # Run setup then start polling
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(setup_commands())
        
        # Start polling
        self.application.run_polling()

def main():
    """Main function"""
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    # Load configuration
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    assemblyai_api_key = os.getenv('ASSEMBLYAI_API_KEY')
    
    if not telegram_token or not anthropic_api_key:
        logger.error("Missing required environment variables:")
        logger.error("- TELEGRAM_BOT_TOKEN")  
        logger.error("- ANTHROPIC_API_KEY")
        return
    
    # Create and run bot
    bot = AIInterviewerBot(telegram_token, anthropic_api_key, assemblyai_api_key)
    
    # Log voice processing status
    if bot.voice_handler:
        logger.info("Bot initialized with voice processing enabled")
    elif assemblyai_api_key:
        logger.info("Bot initialized - voice processing disabled (dependencies missing)")
    else:
        logger.info("Bot initialized - voice processing disabled (no API key)")
    
    bot.run()

if __name__ == '__main__':
    main()