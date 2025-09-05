# PythonAnywhere Deployment Guide

## 🚀 Quick Deploy (5 минут)

### 1. Войти в PythonAnywhere
- Откройте [pythonanywhere.com](https://pythonanywhere.com)
- Войдите в свой аккаунт
- Откройте **Bash console** (кнопка "$ Bash" на Dashboard)

### 2. Запустить deployment скрипт
```bash
# Скачать и запустить deployment скрипт
curl -sSL https://raw.githubusercontent.com/evstrateg/ai-interviewer-bot/main/deploy_pythonanywhere.sh | bash
```

**ИЛИ** клонировать вручную:
```bash
# В bash console PythonAnywhere:
git clone https://github.com/evstrateg/ai-interviewer-bot.git
cd ai-interviewer-bot
chmod +x deploy_pythonanywhere.sh
./deploy_pythonanywhere.sh
```

### 3. Настроить API ключи
```bash
# Редактировать .env файл
nano .env
```

Добавить ваши ключи:
```
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
ANTHROPIC_API_KEY=ваш_ключ_Claude_API
```

### 4. Запустить бот

**Для бесплатного аккаунта:**
```bash
cd ~/ai-interviewer-bot
./run_bot.sh
```

**Для платного аккаунта (Always-On Tasks):**
- Идите в **Tasks** на Dashboard PythonAnywhere  
- Создать Always-On Task
- Command: `/home/ваш_username/ai-interviewer-bot/venv/bin/python /home/ваш_username/ai-interviewer-bot/bot_enhanced.py`
- Working directory: `/home/ваш_username/ai-interviewer-bot`

## 📊 Мониторинг

### Проверить статус бота:
```bash
# Посмотреть активные процессы
ps aux | grep python

# Проверить логи (если настроены)
tail -f logs/*.log

# Посмотреть сессии
ls -la sessions/
ls -la completed_sessions/
```

### Перезапуск:
```bash
# Для бесплатного аккаунта: Ctrl+C и снова запустить
./run_bot.sh

# Для платного: перезапустить Always-On Task в веб-интерфейсе
```

## 🔧 Технические детали

- **Python версия**: 3.8+ (PythonAnywhere поддерживает до 3.11)
- **Основные зависимости**: python-telegram-bot, anthropic, python-dotenv
- **Хранение сессий**: локальные файлы в `sessions/` и `completed_sessions/`
- **Модель Claude**: claude-sonnet-4-20250514

## ⚠️ Важные моменты

1. **Бесплатный аккаунт**: Бот работает только пока открыт bash console
2. **Платный аккаунт**: Always-On Tasks позволяют боту работать 24/7
3. **Сессии**: Сохраняются локально, при перезапуске восстанавливаются (enhanced версия)
4. **Логи**: В бесплатной версии логи только в консоль

## 🐛 Troubleshooting

### Ошибка "Module not found":
```bash
cd ~/ai-interviewer-bot
source venv/bin/activate
pip install -r requirements_minimal.txt
```

### Бот не отвечает:
```bash
# Проверить .env файл
cat .env

# Проверить подключение к API
python -c "from config import config; print('Config OK')"
```

### Забыли токен:
- Telegram: найдите @BotFather в Telegram, `/mytoken`
- Claude API: [console.anthropic.com](https://console.anthropic.com)

---

🎯 **Готово!** Ваш AI Interviewer Bot работает на PythonAnywhere!