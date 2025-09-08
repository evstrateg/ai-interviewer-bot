# AI Interviewer Bot Localization System

This document describes the comprehensive localization system implemented for the AI Interviewer Telegram Bot, supporting English and Russian languages.

## 🌐 Features

- **Dual Language Support**: English (default) and Russian
- **User Preference Storage**: Persistent language preferences per user
- **Automatic Language Detection**: From Telegram user locale
- **Graceful Fallbacks**: Missing translations fall back to English
- **Professional Translations**: High-quality, contextually appropriate translations
- **Easy Integration**: Simple API for existing bot code
- **Future-Ready**: Easy to add more languages

## 📁 Files

### `localization.py`
Main localization system with:
- `LocalizationManager` class - Core localization management
- `SupportedLanguage` enum - Available languages (EN, RU)
- Translation dictionaries for all bot texts
- User preference storage and retrieval
- Convenience functions for easy integration

### `localization_integration_example.py`
Integration examples showing:
- How to modify existing bot methods
- Language selection interface
- Localized message creation
- Button and keyboard localization

## 🚀 Quick Start

### 1. Basic Usage

```python
from localization import t, set_language, SupportedLanguage

# Set user language
user_id = 12345
set_language(user_id, SupportedLanguage.RUSSIAN)

# Get localized text
welcome_msg = t("welcome_greeting", user_id, username="Иван")
# Returns: "Привет, Иван! Я ИИ-интервьюер..."
```

### 2. Integration with Telegram Keyboards

```python
from localization import t
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Create localized keyboard
keyboard = [
    [InlineKeyboardButton(t("prompt_master", user_id), callback_data="prompt_v1_master")],
    [InlineKeyboardButton(t("prompt_telegram", user_id), callback_data="prompt_v2_telegram")],
]
reply_markup = InlineKeyboardMarkup(keyboard)
```

## 🔤 Translation Keys

### Core Interface
- `welcome_title`, `welcome_greeting`, `welcome_features`
- `prompt_master`, `prompt_telegram`, `prompt_conversational`
- `begin_interview`, `interview_started`

### Commands
- `cmd_start_desc`, `cmd_status_desc`, `cmd_help_desc`
- `help_title`, `help_tips`, `help_duration_note`

### Interview Flow
- `setup_complete`, `interview_process_title`
- `stage_complete`, `moving_to`
- `interview_complete`, `session_summary`

### Stage Names
- `stage_greeting`, `stage_profiling`, `stage_essence`
- `stage_operations`, `stage_expertise_map`, `stage_failure_modes`
- `stage_mastery`, `stage_growth_path`, `stage_wrap_up`

### Error Messages
- `no_active_session`, `setup_error`, `technical_difficulties`
- `error_json_parse`, `error_api_general`

## 🛠 API Reference

### LocalizationManager Class

#### Methods

```python
get_text(key: str, user_id: Optional[int] = None, **kwargs) -> str
```
Get localized text with optional formatting.

```python
set_user_language(user_id: int, language: SupportedLanguage)
```
Set user's preferred language.

```python
get_user_language(user_id: int) -> SupportedLanguage
```
Get user's preferred language.

```python
detect_language_from_locale(locale: str) -> SupportedLanguage
```
Auto-detect language from Telegram locale.

### Convenience Functions

```python
t(key: str, user_id: Optional[int] = None, **kwargs) -> str
```
Shortcut for getting translated text.

```python
set_language(user_id: int, language: SupportedLanguage)
```
Shortcut for setting user language.

```python
detect_language(locale: str) -> SupportedLanguage
```
Shortcut for language detection.

## 🔧 Integration Steps

### Step 1: Import Localization
```python
from localization import localization, t, set_language, SupportedLanguage
```

### Step 2: Add Language Selection
```python
async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check for existing language preference
    if user_id not in localization.user_preferences:
        await self._show_language_selection(update)
        return
    
    # Continue with localized welcome
    await self._show_welcome(update, user_id)
```

### Step 3: Replace Hardcoded Strings
```python
# Before
welcome_message = "Hello! I'm an AI interviewer..."

# After  
welcome_message = t("welcome_greeting", user_id, username=username)
```

### Step 4: Localize Keyboards
```python
keyboard = [
    [InlineKeyboardButton(t("begin_interview", user_id), callback_data="start")],
    [InlineKeyboardButton(t("prompt_learn_more", user_id), callback_data="learn_more")]
]
```

### Step 5: Handle Language Selection
```python
async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "lang_ru":
        set_language(user_id, SupportedLanguage.RUSSIAN)
        await query.edit_message_text(t("language_set", user_id, language="Русский"))
```

## 🌍 Language Support

### Currently Supported
- **English** (`en`) - Default language, comprehensive coverage
- **Russian** (`ru`) - Full translation, professional tone

### Adding New Languages

1. **Add to SupportedLanguage enum**:
```python
class SupportedLanguage(Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"
    SPANISH = "es"  # New language
```

2. **Add translation dictionary**:
```python
def _get_spanish_translations(self) -> Dict[str, str]:
    return {
        "welcome_greeting": "¡Hola {username}! Soy un entrevistador de IA...",
        # ... more translations
    }
```

3. **Update _load_translations method**:
```python
return {
    SupportedLanguage.ENGLISH.value: self._get_english_translations(),
    SupportedLanguage.RUSSIAN.value: self._get_russian_translations(),
    SupportedLanguage.SPANISH.value: self._get_spanish_translations(),  # New
}
```

## 📊 Translation Quality

### Russian Translation Features
- **Professional Tone**: Maintains business-appropriate language
- **Technical Accuracy**: Preserves technical terms correctly
- **Cultural Adaptation**: Uses appropriate Russian conventions
- **Concise Mobile Text**: Optimized for Telegram interface
- **Consistent Terminology**: Unified vocabulary across all texts

### Key Translation Decisions
- "AI Interviewer" → "ИИ Интервьюер" (preserves technical clarity)
- "Professional Knowledge" → "Профессиональные Знания"  
- "Interview Stages" → "Этапы Интервью"
- Button texts kept concise for mobile UI
- Error messages are user-friendly and actionable

## 🔍 Testing

### Automated Testing
```python
# Run localization demo
python3 localization.py

# Test integration example
python3 localization_integration_example.py
```

### Manual Testing Checklist
- [ ] Language selection interface works
- [ ] All buttons display correctly in both languages
- [ ] Stage transitions use localized names
- [ ] Error messages appear in user's language
- [ ] Help command shows localized content
- [ ] Interview completion uses correct language
- [ ] User preferences persist between sessions

## 🚀 Deployment Notes

### File Storage
- User language preferences stored in `user_language_preferences.json`
- Automatically created on first use
- JSON format for easy backup/migration

### Performance
- Translations loaded once at startup
- User preferences cached in memory
- File I/O only for preference persistence
- Negligible performance impact

### Backup Considerations
- Back up `user_language_preferences.json` to preserve user settings
- Translation updates require bot restart
- Consider database storage for high-scale deployments

## 📈 Future Enhancements

### Planned Features
- **Dynamic Language Switching**: `/language` command
- **Regional Variants**: en-US vs en-GB, ru-RU vs ru-BY
- **Context-Aware Translations**: Formal vs informal modes
- **Translation Validation**: Automated testing of all keys
- **Admin Interface**: Translation management tools

### Potential Languages
- Spanish (es) - Large user base
- German (de) - European market  
- French (fr) - International presence
- Portuguese (pt) - Brazilian market
- Chinese (zh) - Asian expansion

## 🐛 Troubleshooting

### Common Issues

**Missing Translation Keys**
```
[Missing: some_key]
```
- Add the missing key to both language dictionaries
- Restart the bot to reload translations

**Language Not Persisting**
- Check file permissions on `user_language_preferences.json`
- Ensure write access to bot directory
- Check for JSON formatting errors

**Formatting Errors**
```python
# Wrong - will cause KeyError
t("welcome_greeting", user_id, name="John")  

# Correct - matches format string
t("welcome_greeting", user_id, username="John")
```

**Fallback Not Working**
- Ensure English translations are complete
- Check translation key spelling
- Verify fallback language is set correctly

## 📞 Support

For questions or issues with the localization system:

1. Check translation keys in `localization.py`
2. Review integration examples 
3. Test with the demo functions
4. Verify user preference storage
5. Check file permissions and access

The localization system is designed to be robust and fail gracefully, but proper integration testing is recommended before deployment.