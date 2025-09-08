# 🚀 Новые функции: Русский язык и голосовые сообщения

*Руководство по обновлению бота с поддержкой русского языка и голосовых сообщений*

## 📋 Обзор обновлений

### ✨ Новые возможности:
1. **🌐 Полная поддержка русского языка** - интерфейс, сообщения, команды
2. **🎤 Обработка голосовых сообщений** - интеграция с Assembly AI
3. **⚙️ Система конфигурации** - легкая настройка новых функций
4. **📊 Расширенная аналитика** - метрики голосовых сообщений

## 🛠️ Инструкция по обновлению

### Шаг 1: Обновление зависимостей

```bash
# Установка новых зависимостей
pip install -r requirements_new_features.txt

# Установка системных зависимостей для обработки аудио
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install ffmpeg libavcodec-extra

# macOS:
brew install ffmpeg

# Проверка установки
ffmpeg -version
```

### Шаг 2: Настройка переменных окружения

Обновите ваш `.env` файл:

```env
# Существующие переменные
TELEGRAM_BOT_TOKEN=your_bot_token
ANTHROPIC_API_KEY=your_anthropic_key

# Новые переменные для голосовых сообщений
ASSEMBLYAI_API_KEY=your_assembly_ai_key
VOICE_PROCESSING_ENABLED=true
VOICE_LANGUAGE=ru  # или 'en' для английского

# Языковые настройки
DEFAULT_LANGUAGE=ru  # Язык по умолчанию (ru/en)
LANGUAGE_DETECTION_ENABLED=true

# Настройки производительности (опционально)
MAX_VOICE_DURATION=300  # 5 минут максимум
MAX_CONCURRENT_TRANSCRIPTIONS=3
VOICE_CONFIDENCE_THRESHOLD=0.7
```

### Шаг 3: Получение API ключа Assembly AI

1. Зарегистрируйтесь на https://www.assemblyai.com/
2. Получите бесплатный API ключ (100 часов в месяц)
3. Добавьте ключ в `.env` файл как `ASSEMBLYAI_API_KEY`

### Шаг 4: Обновление кода бота

#### Интеграция системы локализации:

```python
# В начале файла telegram_bot.py
from localization import LocalizationManager, t, set_user_language, get_user_language

# В методе start_command добавить выбор языка
async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Определение языка пользователя
    user_lang = get_user_language(user_id) or 'en'
    
    if user_lang is None:
        # Показать выбор языка для новых пользователей
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
             InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Please choose your language / Выберите язык:",
            reply_markup=reply_markup
        )
        return
    
    # Использование локализованного текста
    welcome_text = t("welcome_message", user_id)
    await update.message.reply_text(welcome_text)
```

#### Интеграция обработки голоса:

```python
# В начале файла telegram_bot.py
from voice_handler import VoiceHandler

# В конструкторе класса
def __init__(self, telegram_token: str, anthropic_api_key: str):
    # ... существующий код ...
    self.voice_handler = VoiceHandler()

# Добавить обработчик голосовых сообщений
def _setup_handlers(self):
    # ... существующие обработчики ...
    self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))

async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосовых сообщений"""
    user_id = update.effective_user.id
    
    # Показать индикатор обработки
    await update.message.reply_text(t("processing_voice", user_id))
    
    try:
        # Обработка голосового сообщения
        transcription = await self.voice_handler.process_voice_message(
            update.message.voice, user_id
        )
        
        if transcription:
            # Передача текста в обычный обработчик сообщений
            await self._process_transcribed_message(update, context, transcription)
        else:
            await update.message.reply_text(t("voice_processing_failed", user_id))
            
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        await update.message.reply_text(t("voice_processing_error", user_id))
```

## 📱 Использование новых функций

### Выбор языка

При первом запуске бота (`/start`) пользователь увидит:
```
Please choose your language / Выберите язык:
[🇬🇧 English] [🇷🇺 Русский]
```

### Голосовые сообщения

1. Запишите голосовое сообщение в Telegram
2. Отправьте боту (как обычное голосовое сообщение)
3. Бот покажет "Обрабатываю голосовое сообщение..."
4. Через несколько секунд получите текстовый ответ

### Команды на русском языке

- `/start` - Начать интервью
- `/status` - Проверить прогресс
- `/reset` - Сбросить сессию
- `/help` - Помощь
- `/metrics` - Статистика

## 🧪 Тестирование

### Проверка локализации:

```bash
# Запуск тестов локализации
python -m pytest tests/test_localization.py -v

# Проверка всех переводов
python localization.py --test
```

### Проверка голосовых сообщений:

```bash
# Запуск тестов голосовой обработки
python -m pytest tests/test_voice_handler.py -v

# Тест интеграции с Assembly AI
python voice_handler.py --test
```

## 🔧 Настройка производительности

### Для высокой нагрузки:

```env
# Увеличить количество одновременных транскрипций
MAX_CONCURRENT_TRANSCRIPTIONS=10

# Уменьшить порог уверенности (больше сообщений будет обработано)
VOICE_CONFIDENCE_THRESHOLD=0.6

# Включить кеширование (если используете Redis)
REDIS_CACHE_ENABLED=true
REDIS_URL=redis://localhost:6379
```

### Для экономии ресурсов:

```env
# Ограничить продолжительность голосовых сообщений
MAX_VOICE_DURATION=60  # 1 минута

# Уменьшить количество одновременных запросов
MAX_CONCURRENT_TRANSCRIPTIONS=1

# Повысить порог уверенности
VOICE_CONFIDENCE_THRESHOLD=0.8
```

## 🐳 Docker обновления

Обновите `docker-compose.yml`:

```yaml
services:
  ai-interviewer-bot:
    # ... существующая конфигурация ...
    
    environment:
      # Новые переменные
      - ASSEMBLYAI_API_KEY=${ASSEMBLYAI_API_KEY}
      - VOICE_PROCESSING_ENABLED=${VOICE_PROCESSING_ENABLED:-true}
      - DEFAULT_LANGUAGE=${DEFAULT_LANGUAGE:-ru}
      - VOICE_LANGUAGE=${VOICE_LANGUAGE:-ru}
    
    volumes:
      # Добавить временную папку для аудио
      - ./data/temp:/app/temp
```

## 📊 Мониторинг

### Новые метрики:

- `voice_messages_processed` - Количество обработанных голосовых сообщений
- `voice_transcription_accuracy` - Средняя точность транскрипции
- `voice_processing_time` - Среднее время обработки
- `language_distribution` - Распределение языков пользователей

### Логи:

```python
# Примеры логов голосовых сообщений
INFO: Voice message processed: user=12345, duration=15s, confidence=0.92
WARN: Low confidence transcription: user=67890, confidence=0.65
ERROR: AssemblyAI API timeout: user=54321, retry_count=3
```

## ❗ Устранение неполадок

### Проблемы с голосовыми сообщениями:

1. **"Voice processing failed"**
   - Проверьте API ключ Assembly AI
   - Убедитесь, что ffmpeg установлен
   - Проверьте интернет соединение

2. **"Audio format not supported"**
   - Обновите pydub: `pip install --upgrade pydub`
   - Установите кодеки: `sudo apt-get install libavcodec-extra`

3. **Медленная обработка**
   - Уменьшите `MAX_CONCURRENT_TRANSCRIPTIONS`
   - Проверьте скорость интернета
   - Оптимизируйте аудио настройки

### Проблемы с локализацией:

1. **Тексты не переводятся**
   - Проверьте файл `user_languages.json`
   - Убедитесь, что `t()` функция используется корректно
   - Проверьте логи на ошибки

2. **Неправильное определение языка**
   - Отключите автоопределение: `LANGUAGE_DETECTION_ENABLED=false`
   - Установите язык вручную: `DEFAULT_LANGUAGE=ru`

## 🎯 Дальнейшие улучшения

1. **Больше языков**: Добавить поддержку других языков
2. **Голосовые ответы**: Генерация голосовых ответов через TTS
3. **Распознавание эмоций**: Анализ тона голоса
4. **Улучшенная локализация**: Контекстные переводы
5. **Кеширование**: Redis кеш для переводов и транскрипций

---

*Эти обновления значительно улучшают пользовательский опыт и делают бота доступным для русскоязычной аудитории с поддержкой современных голосовых интерфейсов.*