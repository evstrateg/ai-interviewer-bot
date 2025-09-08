# Voice Message Processing Setup Guide

The AI Interviewer Telegram Bot now supports voice message processing using AssemblyAI for transcription. This guide explains how to set up and configure voice processing.

## Features

### Voice Processing Capabilities
- **Multi-format Support**: OGG, MP3, M4A, WAV, WebM, Opus
- **Automatic Format Detection**: Detects and handles Telegram voice message formats
- **Audio Optimization**: Converts to optimal format (16kHz mono WAV) for transcription
- **Quality Assessment**: Confidence scoring and transcription quality checks
- **Multi-language Support**: English, Russian, Spanish, French, German, Italian, Portuguese
- **Error Handling**: Comprehensive retry logic and fallback mechanisms
- **Rate Limiting**: Manages concurrent AssemblyAI API requests
- **Temporary File Management**: Automatic cleanup of audio files

### Integration Features
- **Seamless Bot Integration**: Works with both basic and enhanced bot versions
- **Session Preservation**: Maintains conversation context and session state
- **Voice Metadata Tracking**: Stores transcription quality, duration, confidence
- **Conversation History**: Voice messages included in interview conversation logs
- **Progress Indicators**: Shows processing status to users
- **Statistics Tracking**: Monitors transcription success rates and performance

## Prerequisites

### 1. AssemblyAI Account
1. Sign up at [AssemblyAI](https://www.assemblyai.com/)
2. Get your API key from the dashboard
3. Note: AssemblyAI offers free tier with monthly limits

### 2. System Dependencies
Install required system packages for audio processing:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg libavcodec-extra
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
- Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Add FFmpeg to your system PATH

## Installation

### 1. Install Python Dependencies
```bash
# Install all dependencies including voice processing
pip install -r requirements.txt

# Or install voice processing dependencies separately
pip install assemblyai==0.20.0 pydub==0.25.1 httpx==0.25.2
```

### 2. Environment Configuration
Add the following to your `.env` file:

```env
# Required for voice processing
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
VOICE_PROCESSING_ENABLED=true

# Optional voice processing settings
VOICE_MAX_FILE_SIZE_MB=25
VOICE_MIN_DURATION_SECONDS=0.5
VOICE_MAX_DURATION_SECONDS=600
VOICE_CONFIDENCE_THRESHOLD=0.6
VOICE_DEFAULT_LANGUAGE=en
VOICE_AUTO_LANGUAGE_DETECTION=true
VOICE_SPEAKER_LABELS=false
VOICE_CONCURRENT_REQUESTS=3
VOICE_RETRY_ATTEMPTS=3
```

### 3. Verify Installation
Test the voice processing setup:

```python
python -c "
from voice_handler import create_voice_handler
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ASSEMBLYAI_API_KEY')
if api_key:
    handler = create_voice_handler(api_key)
    print('✅ Voice processing setup successful')
else:
    print('❌ AssemblyAI API key not found')
"
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ASSEMBLYAI_API_KEY` | - | **Required**: Your AssemblyAI API key |
| `VOICE_PROCESSING_ENABLED` | `false` | Enable/disable voice processing |
| `VOICE_MAX_FILE_SIZE_MB` | `25` | Maximum audio file size (AssemblyAI limit) |
| `VOICE_MIN_DURATION_SECONDS` | `0.5` | Minimum audio duration to process |
| `VOICE_MAX_DURATION_SECONDS` | `600` | Maximum audio duration (10 minutes) |
| `VOICE_CONFIDENCE_THRESHOLD` | `0.6` | Minimum confidence for good quality |
| `VOICE_DEFAULT_LANGUAGE` | `en` | Default language when auto-detection disabled |
| `VOICE_AUTO_LANGUAGE_DETECTION` | `true` | Enable automatic language detection |
| `VOICE_SPEAKER_LABELS` | `false` | Enable speaker identification (premium) |
| `VOICE_CONCURRENT_REQUESTS` | `3` | Maximum concurrent API requests |
| `VOICE_RETRY_ATTEMPTS` | `3` | Number of retry attempts for failed requests |

### Supported Languages
- `en` - English
- `ru` - Russian  
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese

## Usage

### For Users
1. Start an interview with `/start`
2. Choose your preferred interview style
3. Send voice messages instead of text
4. The bot will:
   - Show "Processing your voice message..."
   - Display the transcribed text
   - Continue the interview with the AI response

### Voice Message Quality Indicators
- 🎤✨ **High Quality**: Confidence ≥ 85%, clear transcription
- 🎤 **Medium Quality**: Confidence 60-84%, good transcription  
- 🎤⚠️ **Low Quality**: Confidence < 60%, verification recommended

### Error Messages
- **"Voice message too short"**: Speak for at least 0.5 seconds
- **"Voice message too large"**: Keep messages under 10 minutes
- **"Couldn't process format"**: Try recording again
- **"Please verify"**: Low confidence transcription

## Bot Commands

### Enhanced Commands (bot_enhanced.py)
- `/metrics` - Shows voice processing statistics
- `/complete` - Complete interview (works with voice sessions)
- `/status` - View current session (includes voice metadata)

### Statistics Included
- Voice messages processed
- Successful vs failed transcriptions  
- Success rate percentage
- Average audio duration
- Average processing time

## Architecture

### File Structure
```
voice_handler.py          # Main voice processing system
├── VoiceMessageHandler   # High-level interface
├── AssemblyAIClient     # API client with retry logic
├── AudioProcessor       # File handling and optimization
└── Configuration        # Settings and validation

config.py                # Updated with voice settings
telegram_bot.py          # Basic bot with voice support
bot_enhanced.py         # Enhanced bot with voice metrics
requirements.txt        # Updated dependencies
```

### Processing Flow
1. **Receive Voice**: User sends voice message via Telegram
2. **Download**: Bot downloads voice file from Telegram servers
3. **Convert**: Audio converted to optimal format (16kHz mono WAV)
4. **Transcribe**: Sent to AssemblyAI for speech-to-text processing
5. **Quality Check**: Confidence scoring and quality assessment
6. **Response**: Transcribed text processed by Claude AI
7. **Cleanup**: Temporary files automatically removed

## Monitoring and Maintenance

### Logging
Voice processing includes structured logging:
- Voice message received
- Download and conversion status
- Transcription results and quality
- Error conditions and retries
- Performance metrics

### Automatic Cleanup
- Temporary audio files cleaned every 6 hours
- Failed downloads removed immediately
- Session data includes voice metadata

### Performance Monitoring
Track these metrics:
- Success rate (target: >90%)
- Average processing time (target: <10s)
- API error rate (target: <5%)
- File cleanup effectiveness

## Troubleshooting

### Common Issues

#### 1. "Voice processing not available"
- **Cause**: Missing dependencies or API key
- **Solution**: Install `assemblyai`, `pydub`, `httpx` and set `ASSEMBLYAI_API_KEY`

#### 2. "Couldn't decode audio"
- **Cause**: Unsupported format or corrupted file
- **Solution**: Ensure FFmpeg is installed and accessible

#### 3. "API quota exceeded" 
- **Cause**: AssemblyAI monthly limit reached
- **Solution**: Check your AssemblyAI usage dashboard

#### 4. High processing times
- **Cause**: Network latency or large files
- **Solution**: Reduce `VOICE_CONCURRENT_REQUESTS` or implement file size limits

### Debug Mode
Enable debug logging to troubleshoot issues:

```env
LOG_LEVEL=DEBUG
LOG_FORMAT=text  # or json for structured logs
```

### API Limits
- **Free Tier**: 5 hours/month transcription
- **File Size**: 25MB maximum
- **Duration**: 10 minutes maximum per file
- **Rate Limits**: Managed automatically by the bot

## Security Considerations

### Data Privacy
- Audio files processed temporarily and deleted
- No permanent storage of voice data
- Transcriptions included in session logs (configurable)

### API Security  
- API keys stored in environment variables
- HTTPS used for all API communications
- Rate limiting prevents API abuse

### File Security
- Temporary files isolated to secure directory
- Automatic cleanup prevents disk space issues
- File access limited to bot process

## Cost Optimization

### AssemblyAI Usage
- Monitor monthly usage in dashboard
- Set file size limits to control costs
- Use confidence thresholds to retry only when needed
- Consider disabling auto-language detection for consistent languages

### System Resources
- Enable periodic cleanup (every 6 hours)
- Monitor disk space in temp directory
- Set reasonable concurrent request limits
- Use voice processing only when needed

## Development

### Testing Voice Processing
```python
# Test basic functionality
from voice_handler import create_voice_handler
handler = create_voice_handler(api_key="your_key")

# Test with sample audio file
result = await handler.process_voice_message(update, context)
print(f"Transcription: {result.text}")
print(f"Quality: {result.quality}")
print(f"Confidence: {result.confidence}")
```

### Extending Functionality
The voice handler is designed to be extensible:
- Add new audio formats in `AudioProcessor`
- Implement custom quality assessment in `AssemblyAIClient`
- Add voice processing analytics in `VoiceMessageHandler`

## Support

For voice processing issues:

1. **Check Logs**: Enable debug logging to see detailed processing steps
2. **Verify Setup**: Confirm FFmpeg installation and API key configuration  
3. **Test Components**: Use the verification script to test each component
4. **Monitor Usage**: Check AssemblyAI dashboard for quota and errors
5. **Review Metrics**: Use `/metrics` command to see processing statistics

The voice processing system is designed to be robust and handle errors gracefully while providing users with a seamless experience for voice-based interviews.