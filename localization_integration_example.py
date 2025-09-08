#!/usr/bin/env python3
"""
Example integration of localization system with AI Interviewer Bot
This shows how to modify the existing bot to support multiple languages.
"""

from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Import localization system
from src.localization.localization import (
    localization, t, ts, set_language, detect_language,
    SupportedLanguage, LocalizationManager
)

# Import existing bot classes (would be from your actual files)
# from telegram_bot import AIInterviewerBot, PromptVariant, InterviewStage
# from bot_enhanced import EnhancedAIInterviewerBot

class LocalizedAIInterviewerBot:
    """
    Example of how to integrate localization into the existing bot
    This shows the key methods that would need modification
    """
    
    def __init__(self, telegram_token: str, anthropic_api_key: str):
        # Initialize existing bot functionality
        # self.original_bot = EnhancedAIInterviewerBot(telegram_token, anthropic_api_key)
        pass
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Localized start command with language selection"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name
        
        # Check if user already has language preference
        user_language = localization.get_user_language(user_id)
        
        # If no preference set, show language selection first
        if user_id not in localization.user_preferences:
            await self._show_language_selection(update, username)
            return
        
        # Show localized welcome message
        await self._show_welcome_message(update, user_id, username)
    
    async def _show_language_selection(self, update: Update, username: str):
        """Show language selection interface"""
        message = t("language_selection") + "\n\n" + t("select_language")
        
        keyboard = [
            [InlineKeyboardButton(t("language_english"), callback_data="lang_en")],
            [InlineKeyboardButton(t("language_russian"), callback_data="lang_ru")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='HTML')
    
    async def _show_welcome_message(self, update: Update, user_id: int, username: str):
        """Show localized welcome message"""
        # Build welcome message using localization
        welcome_parts = [
            t("welcome_title", user_id),
            "",
            t("welcome_greeting", user_id, username=username),
            "",
            t("welcome_what_i_do", user_id)
        ]
        
        # Add features list
        features = t("welcome_features", user_id)  # This returns joined string
        welcome_parts.append(features)
        welcome_parts.extend([
            "",
            t("welcome_duration", user_id),
            t("welcome_method", user_id),
            "",
            t("welcome_choose_style", user_id)
        ])
        
        welcome_message = "\n".join(welcome_parts)
        
        # Create localized keyboard
        keyboard = [
            [InlineKeyboardButton(t("prompt_master", user_id), callback_data="prompt_v1_master")],
            [InlineKeyboardButton(t("prompt_telegram", user_id), callback_data="prompt_v2_telegram")],
            [InlineKeyboardButton(t("prompt_conversational", user_id), callback_data="prompt_v3_conversational")],
            [InlineKeyboardButton(t("prompt_stage_specific", user_id), callback_data="prompt_v4_stage_specific")],
            [InlineKeyboardButton(t("prompt_conversation_mgmt", user_id), callback_data="prompt_v5_conversation_mgmt")],
            [InlineKeyboardButton(t("prompt_learn_more", user_id), callback_data="learn_more")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='HTML')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Localized button callback handler"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        username = query.from_user.username or query.from_user.first_name
        
        # Handle language selection
        if query.data == "lang_en":
            set_language(user_id, SupportedLanguage.ENGLISH)
            await query.edit_message_text(t("language_set", user_id, language="English"))
            # Show welcome message after language selection
            await self._show_welcome_message_after_delay(query, user_id, username)
            
        elif query.data == "lang_ru":
            set_language(user_id, SupportedLanguage.RUSSIAN)
            await query.edit_message_text(t("language_set", user_id, language="Русский"))
            # Show welcome message after language selection
            await self._show_welcome_message_after_delay(query, user_id, username)
        
        elif query.data == "learn_more":
            await self._show_prompt_details(query, user_id)
        
        # Handle other callbacks...
        else:
            # Process other button callbacks with localization
            pass
    
    async def _show_welcome_message_after_delay(self, query, user_id: int, username: str):
        """Show welcome message after language selection"""
        # In real implementation, you might want to send a new message
        # or edit the existing one after a short delay
        pass
    
    async def _show_prompt_details(self, query, user_id: int):
        """Show localized prompt variant details"""
        details_parts = [
            t("prompt_details_title", user_id),
            "",
            "\n".join(t("prompt_master_desc", user_id)),
            "",
            "\n".join(t("prompt_telegram_desc", user_id)),
            "",
            "\n".join(t("prompt_conversational_desc", user_id)),
            "",
            "\n".join(t("prompt_stage_specific_desc", user_id)),
            "",
            "\n".join(t("prompt_conversation_mgmt_desc", user_id)),
            "",
            t("prompt_details_footer", user_id)
        ]
        
        details = "\n".join(details_parts)
        
        keyboard = [
            [InlineKeyboardButton(t("btn_master", user_id), callback_data="prompt_v1_master"),
             InlineKeyboardButton(t("btn_telegram", user_id), callback_data="prompt_v2_telegram")],
            [InlineKeyboardButton(t("btn_conversational", user_id), callback_data="prompt_v3_conversational"),
             InlineKeyboardButton(t("btn_stage_specific", user_id), callback_data="prompt_v4_stage_specific")],
            [InlineKeyboardButton(t("btn_conversation_mgmt", user_id), callback_data="prompt_v5_conversation_mgmt")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(details, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Localized status command"""
        user_id = update.effective_user.id
        
        # Check if session exists (simplified)
        if not self._has_active_session(user_id):
            await update.message.reply_text(t("no_active_session_found", user_id))
            return
        
        # Get session data (would be from actual session)
        session_data = self._get_session_data(user_id)
        
        status_parts = [
            t("interview_status", user_id),
            "",
            t("current_stage", user_id, stage=session_data['current_stage']),
            t("duration_status", user_id, duration=session_data['duration']),
            t("question_depth", user_id, depth=session_data['depth']),
            t("engagement", user_id, level=session_data['engagement']),
            t("examples", user_id, count=session_data['examples']),
            "",
            t("progress_title", user_id)
        ]
        
        # Add progress for each stage
        for stage, completeness in session_data['stage_progress'].items():
            if stage == session_data['current_stage']:
                status_parts.append(t("current_stage_indicator", user_id, 
                                     stage=stage, completeness=completeness))
            elif completeness > 0:
                status_parts.append(t("completed_stage_indicator", user_id,
                                     stage=stage, completeness=completeness))
            else:
                status_parts.append(t("pending_stage_indicator", user_id, stage=stage))
        
        status_message = "\n".join(status_parts)
        await update.message.reply_text(status_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Localized help command"""
        user_id = update.effective_user.id
        
        help_parts = [
            t("help_title", user_id),
            "",
            t("help_commands_title", user_id),
            f"/start - {t('cmd_start_desc', user_id)}",
            f"/status - {t('cmd_status_desc', user_id)}",
            f"/complete - {t('cmd_complete_desc', user_id)}",
            f"/reset - {t('cmd_reset_desc', user_id)}",
            f"/help - {t('cmd_help_desc', user_id)}",
            f"/metrics - {t('cmd_metrics_desc', user_id)}",
            "",
            t("help_interview_process", user_id),
            t("help_process_desc", user_id),
            "",
            t("help_tips_title", user_id)
        ]
        
        # Add tips
        tips = t("help_tips", user_id)  # Returns joined string
        help_parts.append(tips)
        help_parts.extend([
            "",
            t("help_duration_note", user_id)
        ])
        
        help_text = "\n".join(help_parts)
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def _complete_interview(self, session, update: Update, user_id: int):
        """Localized interview completion"""
        # Calculate session stats (would be from actual session)
        duration = 95  # minutes
        message_count = 42
        examples = 8
        insights = 15
        
        summary_parts = [
            t("interview_complete", user_id),
            "",
            t("session_summary", user_id),
            t("duration", user_id, duration=duration),
            t("messages_exchanged", user_id, count=message_count),
            t("examples_collected", user_id, count=examples),
            t("key_insights", user_id, count=insights),
            "",
            t("stages_completed", user_id)
        ]
        
        # Add stage completeness (would be from actual session)
        stages_data = [
            ("greeting", 100), ("profiling", 95), ("essence", 90),
            ("operations", 85), ("expertise_map", 80), ("failure_modes", 75),
            ("mastery", 70), ("growth_path", 65), ("wrap_up", 60)
        ]
        
        for stage, completeness in stages_data:
            status = "✅" if completeness >= 80 else "⚠️" if completeness >= 50 else "❌"
            stage_name = localization.format_stage_name(stage, user_id)
            summary_parts.append(f"{status} {stage_name}: {completeness}%")
        
        summary_parts.extend([
            "",
            t("thank_you", user_id),
            "",
            t("completion_options", user_id)
        ])
        
        summary = "\n".join(summary_parts)
        await update.message.reply_text(summary, parse_mode='Markdown')
    
    # Helper methods (simplified for example)
    def _has_active_session(self, user_id: int) -> bool:
        """Check if user has active session"""
        return True  # Simplified
    
    def _get_session_data(self, user_id: int) -> Dict:
        """Get session data for user"""
        return {
            'current_stage': localization.format_stage_name('profiling', user_id),
            'duration': 25,
            'depth': 2,
            'engagement': 'высокая' if localization.get_user_language(user_id) == SupportedLanguage.RUSSIAN else 'high',
            'examples': 3,
            'stage_progress': {
                'Приветствие' if localization.get_user_language(user_id) == SupportedLanguage.RUSSIAN else 'Greeting': 100,
                'Профилирование' if localization.get_user_language(user_id) == SupportedLanguage.RUSSIAN else 'Profiling': 65,
                'Суть' if localization.get_user_language(user_id) == SupportedLanguage.RUSSIAN else 'Essence': 0,
            }
        }


# Integration steps for existing bot:
"""
1. Import localization system:
   from src.localization.localization import localization, t, ts, set_language, detect_language, SupportedLanguage

2. Add language detection on first user interaction:
   - Check if user has language preference
   - If not, detect from Telegram locale or show selection

3. Replace hardcoded strings with t() calls:
   - Replace "Welcome message" with t("welcome_greeting", user_id, username=username)
   - Replace button texts with localized versions
   - Replace error messages with localized versions

4. Update keyboard creation:
   - Use localized button texts
   - Consider RTL languages for future (currently N/A)

5. Add language switching command (optional):
   - /language command to change language preference
   - Update user preference and reload interface

6. Session management:
   - Store user language in session data
   - Use user_id parameter in all t() calls

7. Error handling:
   - Localize all error messages
   - Provide fallbacks for missing translations

Key methods to modify in existing bot:
- start_command()
- button_callback()  
- help_command()
- status_command()
- _complete_interview()
- All error message handling
- All keyboard creation
"""


def get_integration_checklist() -> List[str]:
    """Get checklist for integrating localization"""
    return [
        "✅ Created comprehensive localization.py with English and Russian translations",
        "✅ Added LocalizationManager class with user preference storage",
        "✅ Implemented convenience functions (t, ts, set_language, detect_language)", 
        "✅ Added language detection from Telegram locale",
        "✅ Created example integration showing key modifications needed",
        "📋 TODO: Modify start_command() in main bot files",
        "📋 TODO: Modify button_callback() for language selection",
        "📋 TODO: Update all keyboard creation with localized texts",
        "📋 TODO: Replace hardcoded strings with t() calls",
        "📋 TODO: Add language preference to session management",
        "📋 TODO: Test both languages thoroughly",
        "📋 TODO: Add /language command for switching languages"
    ]


if __name__ == "__main__":
    checklist = get_integration_checklist()
    print("=== Localization Integration Checklist ===\n")
    for item in checklist:
        print(item)
    print("\n=== Ready for integration! ===")