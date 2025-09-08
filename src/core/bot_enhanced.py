#!/usr/bin/env python3
"""
Enhanced AI Interviewer Telegram Bot with better error handling,
session persistence, and monitoring capabilities.
"""

import asyncio
import json
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pickle
import os
from pathlib import Path

from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from src.core.telegram_bot import (
    AIInterviewerBot, InterviewSession, PromptVariant, 
    InterviewStage, PromptManager, ClaudeIntegration
)
from src.core.config import config

# Configure structured logging
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if config.log_format == "json" else structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class SessionManager:
    """Enhanced session management with persistence"""
    
    def __init__(self, storage_dir: str = "sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.sessions: Dict[int, InterviewSession] = {}
        
        # Load existing sessions on startup
        self._load_sessions()
    
    def _get_session_file(self, user_id: int) -> Path:
        """Get session file path for user"""
        return self.storage_dir / f"session_{user_id}.pkl"
    
    def _load_sessions(self):
        """Load sessions from disk"""
        try:
            for session_file in self.storage_dir.glob("session_*.pkl"):
                try:
                    with open(session_file, 'rb') as f:
                        session = pickle.load(f)
                        
                    # Check if session is not expired
                    if self._is_session_valid(session):
                        self.sessions[session.user_id] = session
                        logger.info("Loaded session", user_id=session.user_id)
                    else:
                        # Remove expired session file
                        session_file.unlink()
                        logger.info("Removed expired session", user_id=session.user_id)
                        
                except Exception as e:
                    logger.error("Failed to load session", file=str(session_file), error=str(e))
                    
        except Exception as e:
            logger.error("Failed to load sessions", error=str(e))
    
    def _is_session_valid(self, session: InterviewSession) -> bool:
        """Check if session is still valid"""
        timeout = timedelta(minutes=config.session_timeout_minutes)
        return datetime.now() - session.last_activity < timeout
    
    def get_session(self, user_id: int) -> Optional[InterviewSession]:
        """Get session for user"""
        session = self.sessions.get(user_id)
        if session and self._is_session_valid(session):
            return session
        elif session:
            # Session expired
            self.remove_session(user_id)
        return None
    
    def create_session(self, user_id: int, username: str, variant: PromptVariant) -> InterviewSession:
        """Create new session"""
        session = InterviewSession(
            user_id=user_id,
            username=username,
            prompt_variant=variant,
            current_stage=InterviewStage.GREETING,
            stage_completeness={stage.value: 0 for stage in InterviewStage},
            conversation_history=[],
            start_time=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.sessions[user_id] = session
        self._save_session(session)
        
        logger.info("Created new session", 
                   user_id=user_id, 
                   username=username, 
                   variant=variant.value)
        
        return session
    
    def update_session(self, session: InterviewSession):
        """Update existing session"""
        session.last_activity = datetime.now()
        self.sessions[session.user_id] = session
        self._save_session(session)
    
    def remove_session(self, user_id: int):
        """Remove session"""
        if user_id in self.sessions:
            del self.sessions[user_id]
        
        session_file = self._get_session_file(user_id)
        if session_file.exists():
            session_file.unlink()
            
        logger.info("Removed session", user_id=user_id)
    
    def _save_session(self, session: InterviewSession):
        """Save session to disk"""
        try:
            session_file = self._get_session_file(session.user_id)
            with open(session_file, 'wb') as f:
                pickle.dump(session, f)
        except Exception as e:
            logger.error("Failed to save session", 
                        user_id=session.user_id, 
                        error=str(e))
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired_users = []
        for user_id, session in self.sessions.items():
            if not self._is_session_valid(session):
                expired_users.append(user_id)
        
        for user_id in expired_users:
            self.remove_session(user_id)
            
        if expired_users:
            logger.info("Cleaned up expired sessions", count=len(expired_users))

class MetricsCollector:
    """Collect and track bot metrics"""
    
    def __init__(self):
        self.metrics = {
            'sessions_started': 0,
            'sessions_completed': 0,
            'messages_processed': 0,
            'errors_occurred': 0,
            'api_calls': 0,
            'api_errors': 0,
        }
    
    def increment(self, metric: str, value: int = 1):
        """Increment metric counter"""
        self.metrics[metric] = self.metrics.get(metric, 0) + value
        logger.debug("Metric updated", metric=metric, value=self.metrics[metric])
    
    def get_metrics(self) -> Dict[str, int]:
        """Get current metrics"""
        return self.metrics.copy()
    
    def log_metrics(self):
        """Log current metrics"""
        logger.info("Bot metrics", **self.metrics)

class EnhancedAIInterviewerBot(AIInterviewerBot):
    """Enhanced version with better error handling and monitoring"""
    
    def __init__(self, telegram_token: str, anthropic_api_key: str, assemblyai_api_key: Optional[str] = None):
        # Initialize session manager and metrics
        self.session_manager = SessionManager()
        self.metrics = MetricsCollector()
        
        # Initialize parent class with voice support
        super().__init__(telegram_token, anthropic_api_key, assemblyai_api_key)
        
        # Override sessions with session manager
        self.sessions = self.session_manager.sessions
        
        # Setup periodic cleanup
        self._setup_periodic_tasks()
    
    def _setup_periodic_tasks(self):
        """Setup periodic maintenance tasks"""
        if self.application.job_queue is not None:
            # Cleanup expired sessions every 30 minutes
            self.application.job_queue.run_repeating(
                self._cleanup_task,
                interval=timedelta(minutes=30),
                first=timedelta(minutes=30)
            )
            
            # Log metrics every hour
            self.application.job_queue.run_repeating(
                self._metrics_task,
                interval=timedelta(hours=1),
                first=timedelta(hours=1)
            )
            
            # Cleanup voice processing temp files every 6 hours (if voice processing enabled)
            if self.voice_handler:
                self.application.job_queue.run_repeating(
                    self._voice_cleanup_task,
                    interval=timedelta(hours=6),
                    first=timedelta(hours=6)
                )
            
            logger.info("Periodic tasks scheduled successfully")
        else:
            logger.warning("Job queue not available. Periodic tasks disabled. Install with: pip install 'python-telegram-bot[job-queue]'")
    
    async def _cleanup_task(self, context):
        """Periodic cleanup task"""
        try:
            self.session_manager.cleanup_expired_sessions()
        except Exception as e:
            logger.error("Cleanup task failed", error=str(e))
    
    async def _metrics_task(self, context):
        """Periodic metrics logging task"""
        try:
            self.metrics.log_metrics()
            
            # Also log voice processing statistics if available
            if self.voice_handler:
                voice_stats = self.voice_handler.get_statistics()
                logger.info("Voice processing metrics", **voice_stats)
                
        except Exception as e:
            logger.error("Metrics task failed", error=str(e))
    
    async def _voice_cleanup_task(self, context):
        """Periodic voice processing cleanup task"""
        try:
            if self.voice_handler:
                await self.voice_handler.cleanup_periodic()
                logger.info("Voice processing cleanup completed")
        except Exception as e:
            logger.error("Voice cleanup task failed", error=str(e))
    
    async def _start_interview(self, query, user_id: int, username: str, variant: PromptVariant):
        """Enhanced interview start with metrics"""
        try:
            # Remove existing session if any
            if user_id in self.sessions:
                self.session_manager.remove_session(user_id)
            
            # Create new session
            session = self.session_manager.create_session(user_id, username, variant)
            self.metrics.increment('sessions_started')
            
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
            
        except Exception as e:
            logger.error("Failed to start interview", 
                        user_id=user_id, 
                        username=username,
                        error=str(e),
                        traceback=traceback.format_exc())
            
            await query.edit_message_text(
                "❌ Sorry, there was an error setting up your interview. Please try again with /start."
            )
            self.metrics.increment('errors_occurred')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced message handling with error recovery"""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        try:
            # Get session
            session = self.session_manager.get_session(user_id)
            if not session:
                await update.message.reply_text(
                    "No active interview session. Please use /start to begin an interview."
                )
                return
            
            self.metrics.increment('messages_processed')
            
            # Add user message to history
            session.add_message("user", user_message)
            
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
            
            # Generate response with retry logic
            max_retries = 3
            response_data = None
            
            for attempt in range(max_retries):
                try:
                    self.metrics.increment('api_calls')
                    response_data = await self.claude.generate_interview_response(
                        session, user_message, self.prompt_manager
                    )
                    break
                    
                except Exception as api_error:
                    logger.warning("API call failed", 
                                 attempt=attempt + 1,
                                 max_retries=max_retries,
                                 error=str(api_error))
                    
                    self.metrics.increment('api_errors')
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        # Final fallback response
                        response_data = {
                            'interview_stage': session.current_stage.value,
                            'response': "I'm experiencing some technical difficulties. Could you please rephrase your last response?",
                            'metadata': {
                                'question_depth': session.question_depth,
                                'completeness': session.stage_completeness.get(session.current_stage.value, 0),
                                'engagement_level': session.engagement_level
                            },
                            'error': 'API_RETRY_FAILED'
                        }
            
            # Update session state
            await self._update_session_from_response(session, response_data)
            
            # Check for stage transitions
            if self._should_transition_stage(session, response_data):
                await self._handle_stage_transition(session, update, response_data)
                return
            
            # Add response to history and save session
            session.add_message("assistant", response_data['response'], response_data.get('metadata'))
            self.session_manager.update_session(session)
            
            # Send response to user
            await self._send_response(update, response_data)
            
        except Exception as e:
            logger.error("Message handling failed",
                        user_id=user_id,
                        message=user_message,
                        error=str(e),
                        traceback=traceback.format_exc())
            
            self.metrics.increment('errors_occurred')
            
            await update.message.reply_text(
                "❌ I encountered an error processing your message. Please try again or use /reset to restart the interview."
            )
    
    async def _update_session_from_response(self, session: InterviewSession, response_data: Dict):
        """Update session state from response metadata"""
        if 'metadata' in response_data:
            metadata = response_data['metadata']
            session.question_depth = metadata.get('question_depth', session.question_depth)
            session.engagement_level = metadata.get('engagement_level', session.engagement_level)
            
            # Update stage completeness
            stage = response_data.get('interview_stage', session.current_stage.value)
            completeness = metadata.get('completeness', 0)
            session.stage_completeness[stage] = completeness
        
        # Update insights and examples from internal tracking
        if 'internal_tracking' in response_data:
            tracking = response_data['internal_tracking']
            if 'key_insights' in tracking:
                session.key_insights.extend(tracking['key_insights'])
            if 'examples_collected' in tracking:
                session.examples_collected = tracking['examples_collected']
    
    def _should_transition_stage(self, session: InterviewSession, response_data: Dict) -> bool:
        """Check if should transition to next stage"""
        if 'internal_tracking' in response_data:
            return response_data['internal_tracking'].get('stage_transition_ready', False)
        
        # Fallback: check completeness
        current_completeness = session.stage_completeness.get(session.current_stage.value, 0)
        return current_completeness >= 80
    
    async def _send_response(self, update: Update, response_data: Dict):
        """Send response to user with error information if needed"""
        response_text = response_data['response']
        
        # Add error notice if applicable
        if 'error' in response_data:
            error_notices = {
                'JSON_PARSE_FAILED': "*Note: Response formatting issue - continuing interview*",
                'API_ERROR': "*Note: Temporary API issue - please continue*",
                'API_RETRY_FAILED': "*Note: Service temporarily unstable - responses may be delayed*"
            }
            
            error_notice = error_notices.get(response_data['error'])
            if error_notice:
                response_text += f"\n\n{error_notice}"
        
        # Send with typing delay for better UX
        words = response_text.split()
        typing_delay = min(len(words) * 0.1, 3.0)  # Max 3 seconds
        await asyncio.sleep(typing_delay)
        
        await update.message.reply_text(response_text, parse_mode='Markdown')
    
    async def _complete_interview(self, session: InterviewSession, update: Update, from_callback: bool = False):
        """Enhanced interview completion with metrics"""
        try:
            self.metrics.increment('sessions_completed')
            
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

Use /reset to start a new interview or /metrics to see bot statistics.
"""
            
            # Send message differently based on source
            if from_callback:
                # From button callback - send new message
                await update.effective_chat.send_message(summary, parse_mode='Markdown')
            else:
                # From regular command - reply to message
                await update.message.reply_text(summary, parse_mode='Markdown')
            
            # Archive completed session
            self._archive_session(session)
            self.session_manager.remove_session(session.user_id)
            
        except Exception as e:
            logger.error("Interview completion failed",
                        user_id=session.user_id,
                        error=str(e))
    
    def _archive_session(self, session: InterviewSession):
        """Archive completed session for analysis"""
        try:
            archive_dir = Path("completed_sessions")
            archive_dir.mkdir(exist_ok=True)
            
            timestamp = session.start_time.strftime("%Y%m%d_%H%M%S")
            archive_file = archive_dir / f"session_{session.user_id}_{timestamp}.json"
            
            # Convert session to JSON-serializable format
            session_data = {
                'user_id': session.user_id,
                'username': session.username,
                'prompt_variant': session.prompt_variant.value,
                'start_time': session.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'stage_completeness': session.stage_completeness,
                'conversation_history': session.conversation_history,
                'examples_collected': session.examples_collected,
                'key_insights': session.key_insights
            }
            
            with open(archive_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
            logger.info("Archived session", 
                       user_id=session.user_id,
                       file=str(archive_file))
                       
        except Exception as e:
            logger.error("Session archival failed",
                        user_id=session.user_id,
                        error=str(e))
    
    async def metrics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot metrics"""
        metrics = self.metrics.get_metrics()
        active_sessions = len(self.sessions)
        
        metrics_text = f"""
📊 **Bot Metrics**

**Sessions:**
• Active: {active_sessions}
• Started: {metrics.get('sessions_started', 0)}
• Completed: {metrics.get('sessions_completed', 0)}

**Messages:**
• Processed: {metrics.get('messages_processed', 0)}

**API Calls:**
• Total: {metrics.get('api_calls', 0)}
• Errors: {metrics.get('api_errors', 0)}

**System:**
• Errors: {metrics.get('errors_occurred', 0)}
• Uptime: Since bot restart
"""
        
        # Add voice processing metrics if available
        if self.voice_handler:
            voice_stats = self.voice_handler.get_statistics()
            voice_text = f"""
**Voice Processing:**
• Messages: {voice_stats.get('messages_processed', 0)}
• Successful: {voice_stats.get('successful_transcriptions', 0)}
• Failed: {voice_stats.get('failed_transcriptions', 0)}
• Success Rate: {voice_stats.get('success_rate', 0):.1%}
• Avg Duration: {voice_stats.get('avg_audio_duration', 0):.1f}s
• Avg Processing: {voice_stats.get('avg_processing_time', 0):.1f}s
"""
            metrics_text += voice_text
        
        await update.message.reply_text(metrics_text, parse_mode='Markdown')
    
    async def complete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manually complete current interview"""
        user_id = update.effective_user.id
        
        if user_id not in self.sessions:
            await update.message.reply_text(
                "❌ No active interview found. Use /start to begin a new interview."
            )
            return
        
        session = self.sessions[user_id]
        
        # Show completion confirmation with button
        keyboard = [
            [InlineKeyboardButton("✅ Yes, Complete Interview", callback_data="confirm_complete")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_complete")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤔 Are you sure you want to complete the current interview?\n\n"
            "This will save your session to completed interviews and end the current conversation.",
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced button callback handler"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        # Handle completion confirmation
        if query.data == "confirm_complete":
            await query.answer()
            
            if user_id in self.sessions:
                session = self.sessions[user_id]
                await self._complete_interview(session, update, from_callback=True)
                await query.edit_message_text("✅ Interview completed and archived!")
            else:
                await query.edit_message_text("❌ No active session found.")
        
        elif query.data == "cancel_complete":
            await query.answer()
            await query.edit_message_text("❌ Interview completion cancelled. Your session continues.")
        
        else:
            # Handle other callbacks from parent class
            await super().button_callback(update, context)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced status command with complete button"""
        user_id = update.effective_user.id
        
        if user_id not in self.sessions:
            await update.message.reply_text(
                "❌ No active interview found. Use /start to begin a new interview."
            )
            return
        
        session = self.sessions[user_id]
        
        # Build status message (reuse parent logic)
        await super().status_command(update, context)
        
        # Add completion button if interview has some progress
        total_completeness = sum(session.stage_completeness.values())
        if total_completeness > 10:  # If some progress made
            keyboard = [[InlineKeyboardButton("✅ Complete Interview", callback_data="confirm_complete")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "💡 You can manually complete this interview if you're done.",
                reply_markup=reply_markup
            )
    
    async def setup_bot_commands(self):
        """Setup bot commands menu with enhanced version commands"""
        commands = [
            BotCommand("start", "🚀 Begin new interview"),
            BotCommand("status", "📊 Check interview progress"),
            BotCommand("complete", "✅ Complete current interview"),
            BotCommand("reset", "🔄 Reset current session"),
            BotCommand("help", "❓ Get help and instructions"),
            BotCommand("metrics", "📈 View bot statistics"),
        ]
        await self.application.bot.set_my_commands(commands)
        logger.info("Enhanced bot commands menu configured")

def main():
    """Main function with enhanced error handling"""
    try:
        # Create and run enhanced bot with voice support
        assemblyai_key = config.assemblyai_api_key if config.voice_processing_enabled else None
        bot = EnhancedAIInterviewerBot(config.telegram_token, config.anthropic_api_key, assemblyai_key)
        
        # Add enhanced commands
        bot.application.add_handler(CommandHandler("metrics", bot.metrics_command))
        bot.application.add_handler(CommandHandler("complete", bot.complete_command))
        
        logger.info("Starting Enhanced AI Interviewer Bot...",
                   log_level=config.log_level,
                   claude_model=config.claude_model,
                   voice_processing=bool(bot.voice_handler))
        
        bot.run()
        
    except Exception as e:
        logger.error("Bot startup failed", 
                    error=str(e),
                    traceback=traceback.format_exc())
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())