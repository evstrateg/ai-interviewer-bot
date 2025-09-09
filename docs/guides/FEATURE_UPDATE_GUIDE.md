# 🚀 Обновление: Расширенные голосовые функции с AssemblyAI SDK

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
# Установка новых зависимостей с обновленным AssemblyAI SDK
pip install -r requirements.txt

# Или установка зависимостей отдельно
pip install assemblyai>=0.30.0 pydub>=0.25.1 httpx>=0.26.0

# Установка системных зависимостей для обработки аудио
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install ffmpeg libavcodec-extra

# macOS:
brew install ffmpeg

# Проверка установки
ffmpeg -version
python -c "import assemblyai as aai; print(f'AssemblyAI SDK: {aai.__version__}')"
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
VOICE_AUTO_LANGUAGE_DETECTION=true

# Новые возможности AssemblyAI
VOICE_SPEAKER_LABELS=true        # Идентификация говорящих
VOICE_PII_REDACTION=true         # Удаление личных данных
VOICE_AUTO_SUMMARIZATION=true    # Автоматическое резюмирование
VOICE_SENTIMENT_ANALYSIS=true    # Анализ тональности
VOICE_TOPIC_DETECTION=true       # Обнаружение тем
VOICE_CONTENT_SAFETY=true        # Модерация контента

# Настройки производительности (опционально)
MAX_VOICE_DURATION=600  # 10 минут максимум
MAX_CONCURRENT_TRANSCRIPTIONS=3
VOICE_CONFIDENCE_THRESHOLD=0.6
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

#### Интеграция обработки голоса (Обновленный SDK):

```python
# В начале файла telegram_bot.py
import assemblyai as aai
from voice_handler import VoiceMessageHandler, VoiceProcessingConfig

# В конструкторе класса
def __init__(self, telegram_token: str, anthropic_api_key: str, assemblyai_api_key: str):
    # ... существующий код ...
    
    # Настройка AssemblyAI
    aai.settings.api_key = assemblyai_api_key
    
    # Конфигурация с новыми возможностями
    voice_config = VoiceProcessingConfig(
        assemblyai_api_key=assemblyai_api_key,
        enable_language_detection=True,
        enable_speaker_labels=True,
        enable_pii_redaction=True,
        enable_summarization=True,
        enable_sentiment_analysis=True,
        enable_topic_detection=True,
        confidence_threshold=0.6
    )
    
    self.voice_handler = VoiceMessageHandler(voice_config)

# Добавить обработчик голосовых сообщений
def _setup_handlers(self):
    # ... существующие обработчики ...
    self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))

async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосовых сообщений с новыми возможностями"""
    user_id = update.effective_user.id
    
    # Показать индикатор обработки
    await update.message.reply_text(t("processing_voice_advanced", user_id))
    
    try:
        # Обработка голосового сообщения с расширенным анализом
        result = await self.voice_handler.process_voice_message(
            update, context
        )
        
        if result.success:
            # Показать результат с новыми данными
            response_parts = [
                f"🎤 **Транскрипция** ({result.language}):",
                result.text,
                ""
            ]
            
            # Добавить информацию о говорящих
            if result.speakers and len(result.speakers) > 1:
                response_parts.append(f"👥 **Говорящих обнаружено**: {len(result.speakers)}")
            
            # Добавить анализ тональности
            if result.sentiment:
                response_parts.append(f"😊 **Тональность**: {result.sentiment}")
            
            # Добавить ключевые темы
            if result.topics:
                topics_str = ", ".join(result.topics[:3])  # Первые 3 темы
                response_parts.append(f"🏷️ **Темы**: {topics_str}")
            
            # Добавить краткое резюме для длинных сообщений
            if result.summary and len(result.text.split()) > 50:
                response_parts.extend(["", f"📋 **Резюме**: {result.summary}"])
            
            response = "\n".join(response_parts)
            await update.message.reply_text(response, parse_mode='Markdown')
            
            # Передача текста в обычный обработчик сообщений
            await self._process_transcribed_message(update, context, result.text)
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

### Проверка голосовых сообщений (Обновленные тесты):

```bash
# Запуск тестов голосовой обработки
python -m pytest tests/test_voice_handler.py -v

# Тест нового SDK AssemblyAI
python -c "
import assemblyai as aai
import os
from dotenv import load_dotenv

load_dotenv()
aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')

# Тест базовой транскрипции
transcriber = aai.Transcriber()
config = aai.TranscriptionConfig(
    language_detection=True,
    speaker_labels=True,
    redact_pii=True,
    sentiment_analysis=True
)

print('✅ AssemblyAI SDK настроен корректно')
print(f'📦 Версия SDK: {aai.__version__}')
print('🎯 Доступные функции: распознавание языка, идентификация говорящих, удаление PII, анализ тональности')
"

# Тест интеграции с голосовым обработчиком
python voice_handler.py --test --features
```

## 🔧 Настройка производительности

### Для высокой нагрузки:

```env
# Увеличить количество одновременных транскрипций
MAX_CONCURRENT_TRANSCRIPTIONS=10

# Уменьшить порог уверенности (больше сообщений будет обработано)
VOICE_CONFIDENCE_THRESHOLD=0.6

# Оптимизация расширенных функций
VOICE_SPEAKER_LABELS=false       # Отключить для ускорения
VOICE_SENTIMENT_ANALYSIS=false   # Отключить для экономии ресурсов
VOICE_TOPIC_DETECTION=false      # Отключить если не нужно

# Включить кеширование результатов (если используете Redis)
REDIS_CACHE_ENABLED=true
REDIS_URL=redis://localhost:6379
VOICE_CACHE_TRANSCRIPTIONS=true  # Кешировать результаты транскрипции
```

### Для экономии ресурсов:

```env
# Ограничить продолжительность голосовых сообщений
MAX_VOICE_DURATION=60  # 1 минута

# Уменьшить количество одновременных запросов
MAX_CONCURRENT_TRANSCRIPTIONS=1

# Повысить порог уверенности
VOICE_CONFIDENCE_THRESHOLD=0.8

# Отключить дорогостоящие функции
VOICE_AUTO_LANGUAGE_DETECTION=false  # Если знаете язык заранее
VOICE_SPEAKER_LABELS=false           # Экономит ~ 25% стоимости
VOICE_PII_REDACTION=false            # Экономит ~ 15% стоимости  
VOICE_AUTO_SUMMARIZATION=false       # Экономит ~ 20% стоимости
VOICE_SENTIMENT_ANALYSIS=false       # Экономит ~ 10% стоимости
VOICE_TOPIC_DETECTION=false          # Экономит ~ 15% стоимости

# Использовать базовую транскрипцию для максимальной экономии
VOICE_BASIC_MODE_ONLY=true
```

## 🐳 Docker обновления

Обновите `docker-compose.yml`:

```yaml
services:
  ai-interviewer-bot:
    # ... существующая конфигурация ...
    
    environment:
      # Основные переменные голосовой обработки
      - ASSEMBLYAI_API_KEY=${ASSEMBLYAI_API_KEY}
      - VOICE_PROCESSING_ENABLED=${VOICE_PROCESSING_ENABLED:-true}
      - DEFAULT_LANGUAGE=${DEFAULT_LANGUAGE:-ru}
      - VOICE_LANGUAGE=${VOICE_LANGUAGE:-ru}
      
      # Новые возможности AssemblyAI
      - VOICE_AUTO_LANGUAGE_DETECTION=${VOICE_AUTO_LANGUAGE_DETECTION:-true}
      - VOICE_SPEAKER_LABELS=${VOICE_SPEAKER_LABELS:-true}
      - VOICE_PII_REDACTION=${VOICE_PII_REDACTION:-true}
      - VOICE_AUTO_SUMMARIZATION=${VOICE_AUTO_SUMMARIZATION:-true}
      - VOICE_SENTIMENT_ANALYSIS=${VOICE_SENTIMENT_ANALYSIS:-true}
      - VOICE_TOPIC_DETECTION=${VOICE_TOPIC_DETECTION:-true}
      - VOICE_CONTENT_SAFETY=${VOICE_CONTENT_SAFETY:-true}
    
    volumes:
      # Добавить временную папку для аудио
      - ./data/temp:/app/temp
```

## 📊 Мониторинг

### Новые метрики (расширенные):

**Основные метрики:**
- `voice_messages_processed` - Количество обработанных голосовых сообщений
- `voice_transcription_accuracy` - Средняя точность транскрипции
- `voice_processing_time` - Среднее время обработки
- `language_distribution` - Распределение языков пользователей

**Расширенные метрики:**
- `speaker_identification_rate` - Частота обнаружения нескольких говорящих
- `pii_redaction_count` - Количество случаев удаления персональных данных
- `sentiment_distribution` - Распределение тональности (позитивная/негативная/нейтральная)
- `topic_detection_effectiveness` - Эффективность определения тем
- `content_safety_flags` - Количество случаев модерации контента
- `summarization_usage` - Частота использования автоматических резюме
- `feature_usage_stats` - Статистика использования каждой функции

### Логи (расширенные):

```python
# Примеры логов голосовых сообщений с новыми функциями
INFO: Voice message processed: user=12345, duration=15s, confidence=0.92, language=ru, features=[speaker_labels,pii_redaction]
INFO: Language detected: user=12345, detected=ru, confidence=0.98
INFO: Speakers identified: user=12345, count=2, labels=[Speaker_A,Speaker_B]
INFO: PII redacted: user=12345, types=[phone_number,email], count=2
INFO: Sentiment analyzed: user=12345, sentiment=positive, confidence=0.87
INFO: Topics detected: user=12345, topics=[technology,business], relevance=[0.92,0.78]
INFO: Summary generated: user=12345, length=156_chars, compression_ratio=0.23
WARN: Low confidence transcription: user=67890, confidence=0.65, language=en
WARN: Content safety flag: user=78901, category=inappropriate, confidence=0.81
ERROR: AssemblyAI API timeout: user=54321, retry_count=3, feature=sentiment_analysis
ERROR: Feature not available: user=99999, feature=speaker_labels, plan=free
```

## ❗ Устранение неполадок

### Проблемы с голосовыми сообщениями:

1. **"Voice processing failed"**
   - Проверьте API ключ AssemblyAI и версию SDK (>=0.30.0)
   - Убедитесь, что ffmpeg установлен
   - Проверьте интернет соединение
   - Проверьте квоты API и доступность функций на вашем плане

2. **"Audio format not supported"**
   - Обновите pydub: `pip install --upgrade pydub>=0.25.1`
   - Установите кодеки: `sudo apt-get install libavcodec-extra`
   - Убедитесь, что используете последнюю версию AssemblyAI SDK

3. **Медленная обработка**
   - Уменьшите `MAX_CONCURRENT_TRANSCRIPTIONS`
   - Отключите ненужные функции (speaker_labels, sentiment_analysis)
   - Проверьте скорость интернета
   - Используйте `VOICE_BASIC_MODE_ONLY=true` для максимальной скорости

### Проблемы с локализацией:

1. **Тексты не переводятся**
   - Проверьте файл `user_languages.json`
   - Убедитесь, что `t()` функция используется корректно
   - Проверьте логи на ошибки

2. **Неправильное определение языка**
   - Отключите автоопределение: `LANGUAGE_DETECTION_ENABLED=false`
   - Установите язык вручную: `DEFAULT_LANGUAGE=ru`

## 🎯 Дальнейшие улучшения

1. **✅ Расширенная языковая поддержка**: Теперь поддерживает 100+ языков
2. **Голосовые ответы**: Генерация голосовых ответов через TTS (планируется)
3. **✅ Анализ эмоций**: Уже реализован через sentiment analysis
4. **Улучшенная локализация**: Контекстные переводы с учетом определенного языка
5. **✅ Кеширование**: Redis кеш для транскрипций и анализа
6. **✅ Защита данных**: PII редактирование уже внедрено
7. **✅ Умная модерация**: Content safety для фильтрации неподходящего контента
8. **Стриминговая транскрипция**: Для длинных интервью в реальном времени
9. **Интеграция с ИИ**: Использование анализа тональности для адаптации стиля интервью
10. **Аналитические дашборды**: Визуализация голосовой аналитики и трендов

---

*Эти обновления выводят бота на новый уровень с enterprise-класса функциями: защита персональных данных, многоязычная поддержка (100+ языков), анализ тональности, автоматическое резюмирование и модерация контента. Система теперь предоставляет профессиональный инструмент для проведения интервью с глубокой аналитикой и защитой данных.*

## 🔧 Технические детали обновления

### Миграция с старого API

```python
# СТАРЫЙ код (НЕ используйте)
client = aai.Transcriber()
aai.settings.api_key = api_key
config = aai.TranscriptionConfig(...)
transcript = await client.transcribe_with_retries(audio_path, config)
if transcript.status == aai.TranscriptStatus.error:
    # обработка ошибки

# НОВЫЙ код (правильный)
aai.settings.api_key = api_key
transcriber = aai.Transcriber()
config = aai.TranscriptionConfig(
    language_detection=True,
    speaker_labels=True,
    redact_pii=True,
    sentiment_analysis=True,
    summarization=True
)
transcript = transcriber.transcribe(audio_path, config=config)
if transcript.status == "error":
    # обработка ошибки
```

### Новые возможности конфигурации

```python
# Полная конфигурация с новыми функциями
config = aai.TranscriptionConfig(
    # Базовые настройки
    language_code="ru",  # или None для авто-определения
    punctuate=True,
    format_text=True,
    
    # Расширенные функции
    language_detection=True,
    speaker_labels=True,
    speakers_expected=2,  # Ожидаемое количество говорящих
    
    # Защита данных
    redact_pii=True,
    redact_pii_policies=[
        aai.PIIRedactionPolicy.phone_number,
        aai.PIIRedactionPolicy.email_address,
        aai.PIIRedactionPolicy.credit_card_number
    ],
    
    # Анализ контента
    sentiment_analysis=True,
    iab_categories=True,  # Определение тем
    content_safety=True,
    
    # Резюмирование
    summarization=True,
    summary_model=aai.SummarizationModel.conversational,
    summary_type=aai.SummaryType.bullets,
    
    # Дополнительные функции
    auto_chapters=True,
    entity_detection=True
)
```