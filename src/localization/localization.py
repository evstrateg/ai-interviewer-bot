#!/usr/bin/env python3
"""
Comprehensive Localization System for AI Interviewer Telegram Bot
Supports English and Russian languages with fallback mechanism.
"""

import os
import json
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class SupportedLanguage(Enum):
    """Supported languages"""
    ENGLISH = "en"
    RUSSIAN = "ru"


@dataclass
class LanguagePreference:
    """User language preference"""
    user_id: int
    language: SupportedLanguage
    country_code: Optional[str] = None
    fallback_language: SupportedLanguage = SupportedLanguage.ENGLISH


class LocalizationManager:
    """Comprehensive localization management system"""
    
    def __init__(self, default_language: SupportedLanguage = SupportedLanguage.ENGLISH):
        self.default_language = default_language
        self.translations = self._load_translations()
        self.user_preferences: Dict[int, LanguagePreference] = {}
        self.preferences_file = Path("user_language_preferences.json")
        self._load_user_preferences()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load all translations"""
        return {
            SupportedLanguage.ENGLISH.value: self._get_english_translations(),
            SupportedLanguage.RUSSIAN.value: self._get_russian_translations()
        }
    
    def _get_english_translations(self) -> Dict[str, str]:
        """English translations (base language)"""
        return {
            # Welcome and introduction
            "welcome_title": "🤖 <b>AI Professional Knowledge Interviewer</b>",
            "welcome_title_short": "🤖 **AI Interviewer**",
            "welcome_greeting": "Hello {username}! I'm an AI interviewer specialized in extracting deep professional insights through structured conversations.",
            "welcome_greeting_short": "Hello {username}! Ready for a professional interview? 🎯",
            "welcome_what_i_do": "<b>What I do:</b>",
            "welcome_features": [
                "• Conduct 9-stage professional knowledge interviews",
                "• Extract implicit expertise and best practices",
                "• Ask one focused question at a time",
                "• Adapt to your communication style",
                "• Generate comprehensive insights"
            ],
            "welcome_duration": "<b>Interview Duration:</b> 90-120 minutes",
            "welcome_method": "<b>Method:</b> Systematic questioning with adaptive deepening",
            "welcome_choose_style": "Choose your preferred interview style:",
            
            # Prompt variant descriptions
            "prompt_master": "🎯 Master Interviewer",
            "prompt_telegram": "📱 Telegram Optimized",
            "prompt_conversational": "💬 Conversational Balance",
            "prompt_stage_specific": "🎪 Stage Specific",
            "prompt_conversation_mgmt": "🧠 Conversation Management",
            "prompt_learn_more": "ℹ️ Learn More",
            
            # Prompt variant detailed descriptions
            "prompt_details_title": "**📋 Interview Styles Explained:**",
            "prompt_master_desc": [
                "🎯 **Master Interviewer**",
                "• Most comprehensive approach",
                "• Systematic knowledge extraction",
                "• Best for detailed documentation"
            ],
            "prompt_telegram_desc": [
                "📱 **Telegram Optimized**",
                "• Mobile-friendly messages",
                "• Concise but thorough",
                "• Great for quick interviews"
            ],
            "prompt_conversational_desc": [
                "💬 **Conversational Balance**",
                "• Natural conversation flow",
                "• Maintains systematic coverage",
                "• Most comfortable experience"
            ],
            "prompt_stage_specific_desc": [
                "🎪 **Stage Specific**",
                "• Detailed approach per stage",
                "• Specialized questioning",
                "• Comprehensive coverage"
            ],
            "prompt_conversation_mgmt_desc": [
                "🧠 **Conversation Management**",
                "• Advanced recovery protocols",
                "• Handles complex situations",
                "• Most robust option"
            ],
            "prompt_details_footer": "Select your preferred style to begin!",
            
            # Interview setup
            "setup_complete": "✅ **Interview Setup Complete**",
            "selected_style": "**Selected Style:** {variant_description}",
            "interview_process_title": "**Interview Process:**",
            "interview_stages": [
                "1. **Greeting** - Building rapport (3-5 min)",
                "2. **Profiling** - Your background (10 min)",
                "3. **Essence** - Role philosophy (15 min)",
                "4. **Operations** - Work processes (20 min)",
                "5. **Expertise Map** - Knowledge levels (20 min)",
                "6. **Failure Modes** - Common mistakes (20 min)",
                "7. **Mastery** - Expert insights (15 min)",
                "8. **Growth Path** - Development timeline (15 min)",
                "9. **Wrap Up** - Final validation (5 min)"
            ],
            "ready_to_begin": "**Ready to begin?** Click below to start your interview!",
            "begin_interview": "🚀 Begin Interview",
            
            # Interview start
            "interview_started": "**🎤 Interview Started**",
            "session_expired": "Session expired. Please use /start to begin again.",
            
            # Stage transitions
            "stage_complete": "📊 **Stage Complete!**",
            "previous_stage_finished": "✅ Previous stage finished with {completeness}% completeness",
            "moving_to": "🎯 **Moving to:** {stage_name}",
            
            # Stage names
            "stage_greeting": "Greeting",
            "stage_profiling": "Profiling (Background)",
            "stage_essence": "Essence (Role Philosophy)",
            "stage_operations": "Operations (Work Processes)",
            "stage_expertise_map": "Expertise Map (Knowledge Levels)",
            "stage_failure_modes": "Failure Modes (Common Mistakes)",
            "stage_mastery": "Mastery (Expert Insights)",
            "stage_growth_path": "Growth Path (Development)",
            "stage_wrap_up": "Wrap Up (Final Questions)",
            
            # Interview completion
            "interview_complete": "🎉 **Interview Complete!**",
            "session_summary": "**Session Summary:**",
            "duration": "• Duration: {duration} minutes",
            "messages_exchanged": "• Messages exchanged: {count}",
            "examples_collected": "• Examples collected: {count}",
            "key_insights": "• Key insights: {count}",
            "stages_completed": "**Stages Completed:**",
            "thank_you": "**Thank you for participating!** Your professional insights have been valuable.",
            "completion_options": "Use /reset to start a new interview or /metrics to see bot statistics.",
            
            # Commands
            "cmd_start_desc": "🚀 Begin new interview",
            "cmd_status_desc": "📊 Check interview progress",
            "cmd_complete_desc": "✅ Complete current interview",
            "cmd_reset_desc": "🔄 Reset current session",
            "cmd_help_desc": "❓ Get help and instructions",
            "cmd_metrics_desc": "📈 View bot statistics",
            
            # Status command
            "interview_status": "📊 **Interview Status**",
            "current_stage": "**Current Stage:** {stage}",
            "duration_status": "**Duration:** {duration} minutes",
            "question_depth": "**Question Depth:** {depth}/4",
            "engagement": "**Engagement:** {level}",
            "examples": "**Examples:** {count}",
            "progress_title": "**Progress:**",
            "current_stage_indicator": "▶️ **{stage}**: {completeness}%",
            "completed_stage_indicator": "✅ {stage}: {completeness}%",
            "pending_stage_indicator": "⏳ {stage}: 0%",
            
            # Reset command
            "session_reset": "🔄 Session reset complete. Use /start to begin a new interview.",
            
            # Help command
            "help_title": "🤖 **AI Interviewer Bot Commands**",
            "help_commands_title": "**Commands:**",
            "help_interview_process": "**Interview Process:**",
            "help_process_desc": "This bot conducts structured professional interviews to extract your expertise and knowledge. The process follows 9 stages from greeting to completion.",
            "help_tips_title": "**Tips for Best Results:**",
            "help_tips": [
                "• Provide detailed, specific responses",
                "• Share concrete examples from your experience",
                "• Be open about your professional challenges",
                "• Take your time - quality over speed"
            ],
            "help_duration_note": "**Interview typically takes 90-120 minutes**",
            
            # Metrics command
            "metrics_title": "📊 **Bot Metrics**",
            "metrics_sessions": "**Sessions:**",
            "metrics_active": "• Active: {count}",
            "metrics_started": "• Started: {count}",
            "metrics_completed": "• Completed: {count}",
            "metrics_messages": "**Messages:**",
            "metrics_processed": "• Processed: {count}",
            "metrics_api_calls": "**API Calls:**",
            "metrics_api_total": "• Total: {count}",
            "metrics_api_errors": "• Errors: {count}",
            "metrics_system": "**System:**",
            "metrics_errors": "• Errors: {count}",
            "metrics_uptime": "• Uptime: Since bot restart",
            
            # Complete command
            "complete_confirmation": "🤔 Are you sure you want to complete the current interview?\n\nThis will save your session to completed interviews and end the current conversation.",
            "confirm_complete": "✅ Yes, Complete Interview",
            "cancel_complete": "❌ Cancel",
            "interview_completed_archived": "✅ Interview completed and archived!",
            "completion_cancelled": "❌ Interview completion cancelled. Your session continues.",
            "complete_hint": "💡 You can manually complete this interview if you're done.",
            
            # Error messages
            "no_active_session": "No active interview session. Please use /start to begin an interview.",
            "no_active_session_found": "❌ No active interview found. Use /start to begin a new interview.",
            "invalid_prompt_selection": "Invalid prompt selection. Please try again.",
            "setup_error": "❌ Sorry, there was an error setting up your interview. Please try again with /start.",
            "message_processing_error": "❌ I encountered an error processing your message. Please try again or use /reset to restart the interview.",
            "technical_difficulties": "I'm experiencing some technical difficulties. Could you please rephrase your last response?",
            "api_error": "I apologize, but I'm experiencing technical difficulties. Could you please repeat your response?",
            
            # Error notices
            "error_json_parse": "*Note: Response formatting issue - continuing interview*",
            "error_api_general": "*Note: Temporary API issue - please continue*",
            "error_api_retry_failed": "*Note: Service temporarily unstable - responses may be delayed*",
            
            # Language selection
            "language_selection": "🌐 **Language Selection**",
            "select_language": "Please select your preferred language:",
            "language_english": "🇺🇸 English",
            "language_russian": "🇷🇺 Русский",
            "language_set": "✅ Language set to {language}. Starting interview...",
            
            # Buttons
            "btn_master": "🎯 Master",
            "btn_telegram": "📱 Telegram", 
            "btn_conversational": "💬 Conversational",
            "btn_stage_specific": "🎪 Stage Specific",
            "btn_conversation_mgmt": "🧠 Conversation Mgmt",
            
            # System messages
            "typing_indicator": "typing",
            "stage_transition_ready": "ready for next stage",
            "interview_in_progress": "Interview in progress...",
        }
    
    def _get_russian_translations(self) -> Dict[str, str]:
        """Russian translations"""
        return {
            # Welcome and introduction
            "welcome_title": "🤖 <b>ИИ Интервьюер для Извлечения Профессиональных Знаний</b>",
            "welcome_title_short": "🤖 **ИИ Интервьюер**",
            "welcome_greeting": "Привет, {username}! Я ИИ-интервьюер для извлечения профессиональных знаний и экспертизы.",
            "welcome_greeting_short": "Привет, {username}! Готовы к профессиональному интервью? 🎯",
            "welcome_what_i_do": "<b>Что я делаю:</b>",
            "welcome_features": [
                "• Извлечение профессиональных знаний",
                "• Глубокий анализ экспертизы",
                "• Фокусированные вопросы",
                "• Адаптация к стилю общения",
                "• Комплексные инсайты"
            ],
            "welcome_duration": "<b>Длительность интервью:</b> 90-120 минут",
            "welcome_method": "<b>Метод:</b> Систематические вопросы с адаптивным углублением",
            "welcome_choose_style": "Выберите предпочитаемый стиль интервью:",
            
            # Prompt variant descriptions
            "prompt_master": "🎯 Мастер-Интервьюер",
            "prompt_telegram": "📱 Оптимизированный для Telegram",
            "prompt_conversational": "💬 Сбалансированная Беседа",
            "prompt_stage_specific": "🎪 Специфичный по Этапам",
            "prompt_conversation_mgmt": "🧠 Управление Диалогом",
            "prompt_learn_more": "ℹ️ Узнать Больше",
            
            # Prompt variant detailed descriptions
            "prompt_details_title": "**📋 Объяснение Стилей Интервью:**",
            "prompt_master_desc": [
                "🎯 **Мастер-Интервьюер**",
                "• Комплексный подход",
                "• Систематическое извлечение",
                "• Для детальной документации"
            ],
            "prompt_telegram_desc": [
                "📱 **Оптимизированный для Telegram**",
                "• Мобильные сообщения",
                "• Краткие и тщательные",
                "• Для быстрых интервью"
            ],
            "prompt_conversational_desc": [
                "💬 **Сбалансированная Беседа**",
                "• Естественный поток",
                "• Систематическое покрытие",
                "• Комфортный опыт"
            ],
            "prompt_stage_specific_desc": [
                "🎪 **Специфичный по Этапам**",
                "• Детальный подход",
                "• Специализированные вопросы",
                "• Всестороннее покрытие"
            ],
            "prompt_conversation_mgmt_desc": [
                "🧠 **Управление Диалогом**",
                "• Протоколы восстановления",
                "• Сложные ситуации",
                "• Надежный вариант"
            ],
            "prompt_details_footer": "Выберите предпочитаемый стиль для начала!",
            
            # Interview setup
            "setup_complete": "✅ **Настройка Интервью Завершена**",
            "selected_style": "**Выбранный Стиль:** {variant_description}",
            "interview_process_title": "**Процесс Интервью:**",
            "interview_stages": [
                "1. **Приветствие** (3-5 мин)",
                "2. **Профилирование** (10 мин)",
                "3. **Суть роли** (15 мин)",
                "4. **Операции** (20 мин)",
                "5. **Экспертиза** (20 мин)",
                "6. **Ошибки** (20 мин)",
                "7. **Мастерство** (15 мин)",
                "8. **Развитие** (15 мин)",
                "9. **Заключение** (5 мин)"
            ],
            "ready_to_begin": "**Готовы начать?** Нажмите ниже, чтобы начать интервью!",
            "begin_interview": "🚀 Начать Интервью",
            
            # Interview start
            "interview_started": "**🎤 Интервью Началось**",
            "session_expired": "Сессия истекла. Пожалуйста, используйте /start для начала заново.",
            
            # Stage transitions
            "stage_complete": "📊 **Этап Завершен!**",
            "previous_stage_finished": "✅ Предыдущий этап завершен с {completeness}% полнотой",
            "moving_to": "🎯 **Переходим к:** {stage_name}",
            
            # Stage names
            "stage_greeting": "Приветствие",
            "stage_profiling": "Профилирование (Бэкграунд)",
            "stage_essence": "Суть (Философия Роли)",
            "stage_operations": "Операции (Рабочие Процессы)",
            "stage_expertise_map": "Карта Экспертизы (Уровни Знаний)",
            "stage_failure_modes": "Типы Ошибок (Частые Проблемы)",
            "stage_mastery": "Мастерство (Экспертные Инсайты)",
            "stage_growth_path": "Путь Развития (Развитие)",
            "stage_wrap_up": "Заключение (Финальные Вопросы)",
            
            # Interview completion
            "interview_complete": "🎉 **Интервью Завершено!**",
            "session_summary": "**Сводка Сессии:**",
            "duration": "• Длительность: {duration} минут",
            "messages_exchanged": "• Сообщений обменено: {count}",
            "examples_collected": "• Примеров собрано: {count}",
            "key_insights": "• Ключевых инсайтов: {count}",
            "stages_completed": "**Этапы Завершены:**",
            "thank_you": "**Спасибо за участие!** Ваши профессиональные инсайты были ценными.",
            "completion_options": "Используйте /reset для нового интервью или /metrics для статистики бота.",
            
            # Commands
            "cmd_start_desc": "🚀 Начать новое интервью",
            "cmd_status_desc": "📊 Проверить прогресс интервью",
            "cmd_complete_desc": "✅ Завершить текущее интервью",
            "cmd_reset_desc": "🔄 Сбросить текущую сессию",
            "cmd_help_desc": "❓ Получить помощь и инструкции",
            "cmd_metrics_desc": "📈 Посмотреть статистику бота",
            
            # Status command
            "interview_status": "📊 **Статус Интервью**",
            "current_stage": "**Текущий Этап:** {stage}",
            "duration_status": "**Длительность:** {duration} минут",
            "question_depth": "**Глубина Вопросов:** {depth}/4",
            "engagement": "**Вовлеченность:** {level}",
            "examples": "**Примеры:** {count}",
            "progress_title": "**Прогресс:**",
            "current_stage_indicator": "▶️ **{stage}**: {completeness}%",
            "completed_stage_indicator": "✅ {stage}: {completeness}%",
            "pending_stage_indicator": "⏳ {stage}: 0%",
            
            # Reset command
            "session_reset": "🔄 Сброс сессии завершен. Используйте /start для начала нового интервью.",
            
            # Help command
            "help_title": "🤖 **Команды ИИ Интервьюера**",
            "help_commands_title": "**Команды:**",
            "help_interview_process": "**Процесс Интервью:**",
            "help_process_desc": "Этот бот проводит структурированные профессиональные интервью для извлечения вашей экспертизы и знаний. Процесс состоит из 9 этапов от приветствия до завершения.",
            "help_tips_title": "**Советы для Лучших Результатов:**",
            "help_tips": [
                "• Предоставляйте детальные, конкретные ответы",
                "• Делитесь конкретными примерами из опыта",
                "• Будьте открыты о профессиональных вызовах",
                "• Не торопитесь - качество важнее скорости"
            ],
            "help_duration_note": "**Интервью обычно занимает 90-120 минут**",
            
            # Metrics command
            "metrics_title": "📊 **Метрики Бота**",
            "metrics_sessions": "**Сессии:**",
            "metrics_active": "• Активных: {count}",
            "metrics_started": "• Начато: {count}",
            "metrics_completed": "• Завершено: {count}",
            "metrics_messages": "**Сообщения:**",
            "metrics_processed": "• Обработано: {count}",
            "metrics_api_calls": "**API Вызовы:**",
            "metrics_api_total": "• Всего: {count}",
            "metrics_api_errors": "• Ошибок: {count}",
            "metrics_system": "**Система:**",
            "metrics_errors": "• Ошибок: {count}",
            "metrics_uptime": "• Время работы: С перезапуска бота",
            
            # Complete command
            "complete_confirmation": "🤔 Вы уверены, что хотите завершить текущее интервью?\n\nЭто сохранит вашу сессию в завершенные интервью и закончит текущий разговор.",
            "confirm_complete": "✅ Да, Завершить Интервью",
            "cancel_complete": "❌ Отмена",
            "interview_completed_archived": "✅ Интервью завершено и архивировано!",
            "completion_cancelled": "❌ Завершение интервью отменено. Ваша сессия продолжается.",
            "complete_hint": "💡 Вы можете вручную завершить это интервью, если закончили.",
            
            # Error messages
            "no_active_session": "Нет активной сессии интервью. Используйте /start для начала интервью.",
            "no_active_session_found": "❌ Активное интервью не найдено. Используйте /start для начала нового интервью.",
            "invalid_prompt_selection": "Неверный выбор стиля. Пожалуйста, попробуйте снова.",
            "setup_error": "❌ Извините, произошла ошибка при настройке интервью. Попробуйте снова с /start.",
            "message_processing_error": "❌ Произошла ошибка при обработке вашего сообщения. Попробуйте снова или используйте /reset для перезапуска интервью.",
            "technical_difficulties": "У меня технические трудности. Не могли бы вы перефразировать ваш последний ответ?",
            "api_error": "Извините, у меня технические трудности. Не могли бы вы повторить ваш ответ?",
            
            # Error notices
            "error_json_parse": "*Примечание: Проблема с форматированием ответа - продолжаем интервью*",
            "error_api_general": "*Примечание: Временная проблема с API - продолжайте*",
            "error_api_retry_failed": "*Примечание: Сервис временно нестабилен - ответы могут задерживаться*",
            
            # Language selection
            "language_selection": "🌐 **Выбор Языка**",
            "select_language": "Пожалуйста, выберите предпочитаемый язык:",
            "language_english": "🇺🇸 English",
            "language_russian": "🇷🇺 Русский",
            "language_set": "✅ Язык установлен на {language}. Начинаем интервью...",
            
            # Buttons
            "btn_master": "🎯 Мастер",
            "btn_telegram": "📱 Telegram",
            "btn_conversational": "💬 Беседа",
            "btn_stage_specific": "🎪 По Этапам",
            "btn_conversation_mgmt": "🧠 Управление",
            
            # System messages
            "typing_indicator": "печатает",
            "stage_transition_ready": "готов к следующему этапу",
            "interview_in_progress": "Интервью в процессе...",
        }
    
    def get_text(self, key: str, user_id: Optional[int] = None, **kwargs) -> str:
        """
        Get localized text for a key with optional formatting
        
        Args:
            key: Translation key
            user_id: User ID for language preference lookup
            **kwargs: Format arguments for string formatting
            
        Returns:
            Localized and formatted text
        """
        # Get user language preference
        language = self._get_user_language(user_id)
        
        # Get translation
        translations = self.translations.get(language.value, {})
        text = translations.get(key)
        
        # Fallback to default language if not found
        if text is None and language != self.default_language:
            fallback_translations = self.translations.get(self.default_language.value, {})
            text = fallback_translations.get(key)
        
        # Final fallback to key itself
        if text is None:
            text = f"[Missing: {key}]"
            
        # Handle list formatting
        if isinstance(text, list):
            text = "\n".join(text)
        
        # Apply string formatting if kwargs provided
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError) as e:
                # If formatting fails, return unformatted text
                pass
        
        return text
    
    def get_texts(self, keys: List[str], user_id: Optional[int] = None, **kwargs) -> List[str]:
        """Get multiple localized texts"""
        return [self.get_text(key, user_id, **kwargs) for key in keys]
    
    def set_user_language(self, user_id: int, language: SupportedLanguage, country_code: Optional[str] = None):
        """Set user language preference"""
        preference = LanguagePreference(
            user_id=user_id,
            language=language,
            country_code=country_code
        )
        self.user_preferences[user_id] = preference
        self._save_user_preferences()
    
    def get_user_language(self, user_id: int) -> SupportedLanguage:
        """Get user's preferred language"""
        preference = self.user_preferences.get(user_id)
        return preference.language if preference else self.default_language
    
    def _get_user_language(self, user_id: Optional[int]) -> SupportedLanguage:
        """Internal method to get user language with None handling"""
        if user_id is None:
            return self.default_language
        return self.get_user_language(user_id)
    
    def detect_language_from_locale(self, locale: str) -> SupportedLanguage:
        """
        Detect language from Telegram user locale
        
        Args:
            locale: Locale string like 'en-US', 'ru-RU', etc.
            
        Returns:
            Detected supported language
        """
        if locale:
            lang_code = locale.lower().split('-')[0]
            if lang_code == 'ru':
                return SupportedLanguage.RUSSIAN
            elif lang_code == 'en':
                return SupportedLanguage.ENGLISH
        
        return self.default_language
    
    def _load_user_preferences(self):
        """Load user language preferences from file"""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for user_id_str, pref_data in data.items():
                    user_id = int(user_id_str)
                    language = SupportedLanguage(pref_data['language'])
                    country_code = pref_data.get('country_code')
                    
                    self.user_preferences[user_id] = LanguagePreference(
                        user_id=user_id,
                        language=language,
                        country_code=country_code
                    )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If preferences file is corrupted, start fresh
            pass
    
    def _save_user_preferences(self):
        """Save user language preferences to file"""
        try:
            data = {}
            for user_id, preference in self.user_preferences.items():
                data[str(user_id)] = {
                    'language': preference.language.value,
                    'country_code': preference.country_code
                }
            
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            # Don't fail the application if preferences can't be saved
            pass
    
    def get_supported_languages(self) -> List[SupportedLanguage]:
        """Get list of supported languages"""
        return list(SupportedLanguage)
    
    def format_stage_name(self, stage_key: str, user_id: Optional[int] = None) -> str:
        """Format stage name for display"""
        return self.get_text(f"stage_{stage_key.lower()}", user_id)
    
    def format_prompt_description(self, variant_name: str, user_id: Optional[int] = None) -> str:
        """Format prompt variant description"""
        # Map variant names to translation keys
        variant_mapping = {
            "v1_master": "prompt_master",
            "v2_telegram": "prompt_telegram", 
            "v3_conversational": "prompt_conversational",
            "v4_stage_specific": "prompt_stage_specific",
            "v5_conversation_mgmt": "prompt_conversation_mgmt"
        }
        
        key = variant_mapping.get(variant_name, "prompt_master")
        return self.get_text(key, user_id)
    
    def get_language_selection_keyboard(self) -> List[List[Dict[str, str]]]:
        """Get keyboard layout for language selection"""
        return [
            [
                {"text": self.get_text("language_english"), "callback_data": "lang_en"},
                {"text": self.get_text("language_russian"), "callback_data": "lang_ru"}
            ]
        ]
    
    def is_rtl_language(self, user_id: Optional[int] = None) -> bool:
        """Check if user's language is right-to-left (for future Arabic support)"""
        # Currently only supports LTR languages
        return False


# Global localization manager instance
localization = LocalizationManager()


# Convenience functions for easy integration
def t(key: str, user_id: Optional[int] = None, **kwargs) -> str:
    """Shortcut function for getting translated text"""
    return localization.get_text(key, user_id, **kwargs)


def ts(keys: List[str], user_id: Optional[int] = None, **kwargs) -> List[str]:
    """Shortcut function for getting multiple translated texts"""
    return localization.get_texts(keys, user_id, **kwargs)


def set_language(user_id: int, language: SupportedLanguage):
    """Shortcut function for setting user language"""
    localization.set_user_language(user_id, language)


def detect_language(locale: str) -> SupportedLanguage:
    """Shortcut function for language detection"""
    return localization.detect_language_from_locale(locale)


# Example usage and testing functions
def demo_localization():
    """Demonstrate localization functionality"""
    print("=== Localization Demo ===\n")
    
    # Test user preferences
    test_user_en = 12345
    test_user_ru = 67890
    
    # Set languages
    set_language(test_user_en, SupportedLanguage.ENGLISH)
    set_language(test_user_ru, SupportedLanguage.RUSSIAN)
    
    # Test basic translations
    print("English welcome:")
    print(t("welcome_greeting", test_user_en, username="John"))
    print()
    
    print("Russian welcome:")
    print(t("welcome_greeting", test_user_ru, username="Иван"))
    print()
    
    # Test stage names
    print("Stage names comparison:")
    stages = ["greeting", "profiling", "essence", "operations"]
    for stage in stages:
        en_name = localization.format_stage_name(stage, test_user_en)
        ru_name = localization.format_stage_name(stage, test_user_ru)
        print(f"  {stage}: EN='{en_name}' | RU='{ru_name}'")
    print()
    
    # Test prompt descriptions
    print("Prompt descriptions:")
    variants = ["v1_master", "v2_telegram", "v3_conversational"]
    for variant in variants:
        en_desc = localization.format_prompt_description(variant, test_user_en)
        ru_desc = localization.format_prompt_description(variant, test_user_ru)
        print(f"  {variant}: EN='{en_desc}' | RU='{ru_desc}'")


if __name__ == "__main__":
    demo_localization()