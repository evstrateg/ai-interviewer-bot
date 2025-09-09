# AssemblyAI API Reference for AI Interviewer Bot

*Complete API documentation for voice processing with enterprise-grade features*

## Table of Contents

- [Quick Start](#quick-start)
- [SDK Installation & Setup](#sdk-installation--setup)
- [Basic Transcription](#basic-transcription)
- [Advanced Features](#advanced-features)
- [Configuration Reference](#configuration-reference)
- [Error Handling](#error-handling)
- [Performance Optimization](#performance-optimization)
- [Code Examples](#code-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Cost Optimization](#cost-optimization)
- [Migration Guide](#migration-guide)

## Quick Start

### 1. SDK Installation

```bash
# Install latest AssemblyAI SDK
pip install assemblyai>=0.30.0

# Install additional dependencies
pip install pydub>=0.25.1 httpx>=0.26.0
```

### 2. Basic Setup

```python
import assemblyai as aai

# Set your API key
aai.settings.api_key = "your_assemblyai_api_key"

# Create a transcriber
transcriber = aai.Transcriber()

# Basic transcription
transcript = transcriber.transcribe("audio_file.wav")
print(f"Text: {transcript.text}")
```

### 3. Advanced Features Setup

```python
# Configuration with all advanced features
config = aai.TranscriptionConfig(
    language_detection=True,
    speaker_labels=True,
    redact_pii=True,
    sentiment_analysis=True,
    summarization=True,
    iab_categories=True,
    content_safety=True
)

# Advanced transcription
transcript = transcriber.transcribe("audio_file.wav", config=config)
```

## SDK Installation & Setup

### System Requirements

- **Python**: 3.8+ (3.11+ recommended)
- **Memory**: 512MB+ available RAM
- **Storage**: 100MB+ free disk space for temporary files
- **Network**: Stable internet connection for API calls

### Installation Methods

#### pip (Recommended)
```bash
pip install assemblyai>=0.30.0
```

#### Conda
```bash
conda install -c conda-forge assemblyai
```

#### Poetry
```bash
poetry add assemblyai
```

#### Requirements File
```txt
# requirements.txt
assemblyai>=0.30.0
pydub>=0.25.1
httpx>=0.26.0
```

### Environment Setup

#### Environment Variables
```bash
# .env file
ASSEMBLYAI_API_KEY=your_api_key_here
ASSEMBLYAI_API_URL=https://api.assemblyai.com  # Optional: custom endpoint
ASSEMBLYAI_TIMEOUT=30  # Optional: request timeout in seconds
```

#### Configuration Class
```python
import os
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AssemblyAIConfig:
    """AssemblyAI configuration settings"""
    api_key: str
    api_url: str = "https://api.assemblyai.com"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv("ASSEMBLYAI_API_KEY"),
            api_url=os.getenv("ASSEMBLYAI_API_URL", "https://api.assemblyai.com"),
            timeout=int(os.getenv("ASSEMBLYAI_TIMEOUT", "30"))
        )

# Usage
config = AssemblyAIConfig.from_env()
aai.settings.api_key = config.api_key
```

## Basic Transcription

### Simple File Transcription

```python
import assemblyai as aai

# Initialize
aai.settings.api_key = "your_api_key"
transcriber = aai.Transcriber()

# Transcribe local file
transcript = transcriber.transcribe("path/to/audio.wav")

# Check status
if transcript.status == "completed":
    print(f"Transcription: {transcript.text}")
    print(f"Confidence: {transcript.confidence}")
elif transcript.status == "error":
    print(f"Error: {transcript.error}")
```

### Supported Audio Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| WAV | `.wav` | Uncompressed, best quality |
| MP3 | `.mp3` | Compressed, widely supported |
| M4A | `.m4a` | Apple format, good compression |
| OGG | `.ogg` | Open source format |
| FLAC | `.flac` | Lossless compression |
| WebM | `.webm` | Web format |
| AMR | `.amr` | Mobile format |

### Audio Constraints

| Parameter | Limit | Notes |
|-----------|-------|-------|
| **File Size** | 25MB (Free), 50MB (Pro) | Per file |
| **Duration** | No limit | Streaming available |
| **Sample Rate** | 8kHz - 48kHz | 16kHz recommended |
| **Channels** | Mono/Stereo | Mono preferred |
| **Bit Depth** | 16-bit, 24-bit, 32-bit | 16-bit sufficient |

### URL-based Transcription

```python
# Transcribe from URL
transcript = transcriber.transcribe("https://example.com/audio.mp3")

# Transcribe from cloud storage
s3_url = "https://s3.amazonaws.com/bucket/audio.wav"
transcript = transcriber.transcribe(s3_url)
```

### Real-time Streaming (Beta)

```python
import asyncio
from assemblyai.streaming import StreamingTranscriber

async def stream_transcription():
    """Real-time streaming transcription"""
    
    async def on_transcript(transcript):
        print(f"Partial: {transcript.text}")
    
    async def on_final_transcript(transcript):
        print(f"Final: {transcript.text}")
    
    # Configure streaming
    streaming_transcriber = StreamingTranscriber(
        token="your_token",
        on_transcript=on_transcript,
        on_final_transcript=on_final_transcript
    )
    
    # Start streaming
    await streaming_transcriber.start()
    
    # Send audio data (example with microphone)
    # await streaming_transcriber.send_audio(audio_data)

# Run streaming
asyncio.run(stream_transcription())
```

## Advanced Features

### Language Detection

```python
# Enable automatic language detection
config = aai.TranscriptionConfig(
    language_detection=True
)

transcript = transcriber.transcribe("audio.wav", config=config)

# Access detected language
print(f"Detected Language: {transcript.language_code}")
print(f"Language Confidence: {transcript.language_confidence}")

# Language detection results
if hasattr(transcript, 'language_detection_results'):
    for result in transcript.language_detection_results:
        print(f"Language: {result.language}, Confidence: {result.confidence}")
```

#### Supported Languages (100+)

**Major Languages:**
- English (en) - US, UK, AU, CA variants
- Spanish (es) - Spain, Mexico, Argentina variants  
- French (fr) - France, Canada variants
- German (de)
- Italian (it)
- Portuguese (pt) - Brazil, Portugal variants
- Russian (ru)
- Chinese (zh) - Mandarin, Cantonese
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- Hindi (hi)
- Turkish (tr)
- Dutch (nl)
- Polish (pl)
- Swedish (sv)
- Norwegian (no)
- Danish (da)
- Finnish (fi)

### Speaker Labels (Diarization)

```python
# Enable speaker identification
config = aai.TranscriptionConfig(
    speaker_labels=True,
    speakers_expected=2  # Optional: hint for number of speakers
)

transcript = transcriber.transcribe("meeting.wav", config=config)

# Access speaker information
for utterance in transcript.utterances:
    print(f"Speaker {utterance.speaker}: {utterance.text}")
    print(f"Start: {utterance.start}ms, End: {utterance.end}ms")

# Speaker summary
speakers = set(utterance.speaker for utterance in transcript.utterances)
print(f"Total speakers detected: {len(speakers)}")
```

### PII Redaction & Privacy

```python
# Configure PII redaction
config = aai.TranscriptionConfig(
    redact_pii=True,
    redact_pii_policies=[
        aai.PIIRedactionPolicy.phone_number,
        aai.PIIRedactionPolicy.email_address,
        aai.PIIRedactionPolicy.credit_card_number,
        aai.PIIRedactionPolicy.social_security_number,
        aai.PIIRedactionPolicy.name,
        aai.PIIRedactionPolicy.address,
        aai.PIIRedactionPolicy.date_of_birth,
        aai.PIIRedactionPolicy.bank_account_number
    ],
    redact_pii_sub="[REDACTED]"  # Custom replacement text
)

transcript = transcriber.transcribe("sensitive_audio.wav", config=config)

# Original text with PII redacted
print(f"Redacted Text: {transcript.text}")

# PII detection results
if hasattr(transcript, 'redacted_pii'):
    for pii_item in transcript.redacted_pii:
        print(f"PII Type: {pii_item.label}, Location: {pii_item.start}-{pii_item.end}")
```

#### Available PII Policies

| Policy | Description | Example |
|--------|-------------|---------|
| `phone_number` | Phone numbers | (555) 123-4567 |
| `email_address` | Email addresses | john@example.com |
| `credit_card_number` | Credit card numbers | 4111-1111-1111-1111 |
| `social_security_number` | SSN (US) | 123-45-6789 |
| `name` | Person names | John Smith |
| `address` | Physical addresses | 123 Main St |
| `date_of_birth` | Birth dates | 01/01/1990 |
| `bank_account_number` | Bank account numbers | 123456789 |

### Sentiment Analysis

```python
# Enable sentiment analysis
config = aai.TranscriptionConfig(
    sentiment_analysis=True
)

transcript = transcriber.transcribe("interview.wav", config=config)

# Overall sentiment
print(f"Overall Sentiment: {transcript.sentiment_analysis_results}")

# Sentence-level sentiment
for sentence in transcript.sentiment_analysis_results:
    print(f"Text: {sentence.text}")
    print(f"Sentiment: {sentence.sentiment} (Confidence: {sentence.confidence})")
    print(f"Start: {sentence.start}ms, End: {sentence.end}ms")
```

#### Sentiment Classifications

| Sentiment | Range | Interpretation |
|-----------|--------|----------------|
| **POSITIVE** | 0.6 - 1.0 | Happy, excited, satisfied |
| **NEUTRAL** | 0.4 - 0.6 | Calm, matter-of-fact |
| **NEGATIVE** | 0.0 - 0.4 | Sad, angry, frustrated |

### Topic Detection

```python
# Enable topic detection (IAB categories)
config = aai.TranscriptionConfig(
    iab_categories=True
)

transcript = transcriber.transcribe("business_call.wav", config=config)

# Topic results
if transcript.iab_categories_result:
    print("Detected Topics:")
    for category, relevance in transcript.iab_categories_result.summary.items():
        print(f"- {category}: {relevance:.2f} relevance")
    
    # Detailed results with timestamps
    for result in transcript.iab_categories_result.results:
        print(f"Text: {result.text}")
        for label in result.labels:
            print(f"  Topic: {label.label} (Confidence: {label.confidence})")
```

#### IAB Topic Categories

**Business & Technology:**
- Business/Business Software
- Technology & Computing/Software
- Careers/Job Search
- Finance/Personal Finance

**Education & Science:**
- Education/Online Learning
- Science/Computer Science
- Technology & Computing/Programming

**Entertainment & Media:**
- Entertainment/Audio Content
- Music and Audio/Podcasts
- Pop Culture/Celebrity News

### Auto-Summarization

```python
# Enable summarization
config = aai.TranscriptionConfig(
    summarization=True,
    summary_model=aai.SummarizationModel.conversational,  # or informational
    summary_type=aai.SummaryType.bullets  # or paragraph, gist, headline
)

transcript = transcriber.transcribe("long_meeting.wav", config=config)

# Access summary
print(f"Summary: {transcript.summary}")
```

#### Summarization Options

**Models:**
- `conversational`: Best for meetings, interviews, casual conversations
- `informational`: Best for lectures, presentations, formal content

**Types:**
- `bullets`: Bullet point format
- `paragraph`: Paragraph format  
- `gist`: Very brief summary
- `headline`: Single sentence summary

### Content Safety & Moderation

```python
# Enable content safety
config = aai.TranscriptionConfig(
    content_safety=True
)

transcript = transcriber.transcribe("user_content.wav", config=config)

# Content safety results
if transcript.content_safety_labels:
    print("Content Safety Analysis:")
    for label in transcript.content_safety_labels.summary:
        print(f"- {label}: {transcript.content_safety_labels.summary[label]}")
    
    # Detailed results with timestamps
    for result in transcript.content_safety_labels.results:
        for label in result.labels:
            print(f"Timestamp {result.start}-{result.end}ms: {label.label} (Confidence: {label.confidence})")
```

#### Content Safety Categories

| Category | Description |
|----------|-------------|
| **accidents** | Accidents, disasters |
| **alcohol** | Alcohol-related content |
| **crime_violence** | Criminal activity, violence |
| **disasters** | Natural disasters |
| **drugs** | Drug-related content |
| **gambling** | Gambling content |
| **hate_speech** | Hate speech, discrimination |
| **health_issues** | Medical conditions |
| **manmade_disasters** | Human-caused disasters |
| **profanity** | Profane language |
| **sensitive_social_issues** | Controversial topics |
| **terrorism** | Terrorism-related content |
| **weapons** | Weapons, firearms |

### Auto Chapters

```python
# Enable auto chapters (for long content)
config = aai.TranscriptionConfig(
    auto_chapters=True
)

transcript = transcriber.transcribe("long_interview.wav", config=config)

# Chapter breakdown
if transcript.chapters:
    for chapter in transcript.chapters:
        print(f"Chapter: {chapter.summary}")
        print(f"Start: {chapter.start}ms, End: {chapter.end}ms")
        print(f"Gist: {chapter.gist}")
        print(f"Headline: {chapter.headline}")
        print("---")
```

### Word-level Timestamps

```python
# Get detailed word-level timing
transcript = transcriber.transcribe("presentation.wav")

# Access word-level data
for word in transcript.words:
    print(f"Word: '{word.text}' - Start: {word.start}ms, End: {word.end}ms, Confidence: {word.confidence}")

# Find specific words/phrases
def find_word_timestamps(transcript, search_term):
    """Find timestamps for specific words or phrases"""
    results = []
    words = transcript.words
    
    for i, word in enumerate(words):
        if search_term.lower() in word.text.lower():
            results.append({
                'word': word.text,
                'start': word.start,
                'end': word.end,
                'confidence': word.confidence
            })
    
    return results

# Usage
python_mentions = find_word_timestamps(transcript, "python")
for mention in python_mentions:
    print(f"Found 'python' at {mention['start']}ms - {mention['end']}ms")
```

## Configuration Reference

### Complete Configuration Example

```python
import assemblyai as aai

# Comprehensive configuration with all options
config = aai.TranscriptionConfig(
    # Basic Settings
    language_code="en",  # Specific language (or None for auto-detection)
    punctuate=True,      # Add punctuation
    format_text=True,    # Format text (capitalize, etc.)
    
    # Language Detection
    language_detection=True,
    
    # Speaker Features
    speaker_labels=True,
    speakers_expected=2,  # Hint for number of speakers
    
    # Privacy & Security
    redact_pii=True,
    redact_pii_policies=[
        aai.PIIRedactionPolicy.phone_number,
        aai.PIIRedactionPolicy.email_address,
        aai.PIIRedactionPolicy.credit_card_number,
        aai.PIIRedactionPolicy.social_security_number
    ],
    redact_pii_sub="[REDACTED]",
    
    # Content Analysis
    sentiment_analysis=True,
    iab_categories=True,
    content_safety=True,
    
    # Summarization
    summarization=True,
    summary_model=aai.SummarizationModel.conversational,
    summary_type=aai.SummaryType.bullets,
    
    # Long Content Features
    auto_chapters=True,
    
    # Audio Enhancement
    audio_start_from=0,      # Start transcription from timestamp (ms)
    audio_end_at=None,       # End transcription at timestamp (ms)
    
    # Custom Vocabulary
    word_boost=["Python", "JavaScript", "React", "API"],  # Boost specific words
    boost_param="high",  # low, default, high
    
    # Dual Channel (Stereo)
    dual_channel=False,  # Treat stereo channels separately
    
    # Webhook
    webhook_url="https://yourapp.com/webhook",
    webhook_auth_header_name="Authorization",
    webhook_auth_header_value="Bearer your_token"
)
```

### Configuration Parameters Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `language_code` | str/None | None | Language code or None for auto-detection |
| `punctuate` | bool | True | Add punctuation to transcript |
| `format_text` | bool | True | Format text (capitalization, etc.) |
| `language_detection` | bool | False | Enable automatic language detection |
| `speaker_labels` | bool | False | Enable speaker diarization |
| `speakers_expected` | int | None | Expected number of speakers |
| `redact_pii` | bool | False | Enable PII redaction |
| `redact_pii_policies` | List | [] | PII types to redact |
| `redact_pii_sub` | str | "[REDACTED]" | PII replacement text |
| `sentiment_analysis` | bool | False | Enable sentiment analysis |
| `iab_categories` | bool | False | Enable topic detection |
| `content_safety` | bool | False | Enable content moderation |
| `summarization` | bool | False | Enable auto-summarization |
| `summary_model` | enum | conversational | Summarization model type |
| `summary_type` | enum | bullets | Summary format type |
| `auto_chapters` | bool | False | Enable auto chapter detection |
| `word_boost` | List[str] | [] | Words to boost recognition |
| `boost_param` | str | "default" | Boost strength level |
| `dual_channel` | bool | False | Process stereo channels separately |
| `webhook_url` | str | None | Webhook URL for notifications |

## Error Handling

### Common Error Types

```python
import assemblyai as aai
from assemblyai.exceptions import (
    TranscriptionError,
    APIError,
    AuthError,
    QuotaExceededError
)

def robust_transcription(audio_file):
    """Transcription with comprehensive error handling"""
    
    try:
        transcript = transcriber.transcribe(audio_file)
        
        # Check transcript status
        if transcript.status == "completed":
            return transcript
        elif transcript.status == "error":
            raise TranscriptionError(f"Transcription failed: {transcript.error}")
        
    except AuthError as e:
        print(f"Authentication failed: {e}")
        print("Check your ASSEMBLYAI_API_KEY")
        return None
        
    except QuotaExceededError as e:
        print(f"Quota exceeded: {e}")
        print("Upgrade your AssemblyAI plan or wait for quota reset")
        return None
        
    except APIError as e:
        print(f"API error: {e}")
        print("Check AssemblyAI service status")
        return None
        
    except TranscriptionError as e:
        print(f"Transcription error: {e}")
        return None
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage with retry logic
def transcribe_with_retry(audio_file, max_retries=3):
    """Transcription with automatic retry"""
    
    for attempt in range(max_retries):
        try:
            result = robust_transcription(audio_file)
            if result:
                return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return None
```

### Error Response Codes

| Code | Description | Solution |
|------|-------------|----------|
| **400** | Bad Request | Check audio format and parameters |
| **401** | Unauthorized | Verify API key |
| **403** | Forbidden | Check account permissions |
| **404** | Not Found | Verify audio URL accessibility |
| **413** | Payload Too Large | Reduce file size or use streaming |
| **429** | Rate Limited | Implement backoff, upgrade plan |
| **500** | Server Error | Retry request, check status page |

### Validation Functions

```python
def validate_audio_file(file_path: str) -> dict:
    """Validate audio file before transcription"""
    import os
    from pydub import AudioSegment
    
    validation_result = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "info": {}
    }
    
    # Check file existence
    if not os.path.exists(file_path):
        validation_result["errors"].append("File does not exist")
        return validation_result
    
    # Check file size
    file_size = os.path.getsize(file_path)
    file_size_mb = file_size / (1024 * 1024)
    validation_result["info"]["file_size_mb"] = file_size_mb
    
    if file_size_mb > 25:
        validation_result["errors"].append(f"File too large: {file_size_mb:.1f}MB (max 25MB)")
    
    try:
        # Load audio file
        audio = AudioSegment.from_file(file_path)
        
        # Check duration
        duration_seconds = len(audio) / 1000
        validation_result["info"]["duration_seconds"] = duration_seconds
        
        # Check sample rate
        sample_rate = audio.frame_rate
        validation_result["info"]["sample_rate"] = sample_rate
        
        if sample_rate < 8000:
            validation_result["warnings"].append(f"Low sample rate: {sample_rate}Hz (recommend 16kHz+)")
        
        # Check channels
        channels = audio.channels
        validation_result["info"]["channels"] = channels
        
        if channels > 2:
            validation_result["warnings"].append(f"Multi-channel audio: {channels} channels")
        
        # If no errors, mark as valid
        if not validation_result["errors"]:
            validation_result["valid"] = True
            
    except Exception as e:
        validation_result["errors"].append(f"Audio processing error: {e}")
    
    return validation_result

# Usage
validation = validate_audio_file("interview.wav")
if validation["valid"]:
    transcript = transcriber.transcribe("interview.wav")
else:
    print("Validation errors:", validation["errors"])
```

## Performance Optimization

### Concurrent Processing

```python
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

class AsyncTranscriptionManager:
    """Manage concurrent transcriptions efficiently"""
    
    def __init__(self, api_key: str, max_concurrent: int = 3):
        self.api_key = api_key
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        
    def transcribe_single(self, audio_file: str, config: aai.TranscriptionConfig = None) -> Dict[str, Any]:
        """Single transcription with error handling"""
        try:
            aai.settings.api_key = self.api_key
            transcriber = aai.Transcriber()
            
            transcript = transcriber.transcribe(audio_file, config=config)
            
            return {
                "file": audio_file,
                "status": "success",
                "transcript": transcript,
                "error": None
            }
            
        except Exception as e:
            return {
                "file": audio_file,
                "status": "error",
                "transcript": None,
                "error": str(e)
            }
    
    def transcribe_batch(self, audio_files: List[str], config: aai.TranscriptionConfig = None) -> List[Dict[str, Any]]:
        """Process multiple files concurrently"""
        futures = []
        results = []
        
        # Submit jobs
        for audio_file in audio_files:
            future = self.executor.submit(self.transcribe_single, audio_file, config)
            futures.append(future)
        
        # Collect results as they complete
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"Completed: {result['file']} - {result['status']}")
        
        return results
    
    def __del__(self):
        self.executor.shutdown(wait=True)

# Usage
manager = AsyncTranscriptionManager(
    api_key="your_api_key",
    max_concurrent=3
)

audio_files = ["interview1.wav", "interview2.wav", "interview3.wav"]
results = manager.transcribe_batch(audio_files)

# Process results
for result in results:
    if result["status"] == "success":
        print(f"✅ {result['file']}: {len(result['transcript'].text)} characters")
    else:
        print(f"❌ {result['file']}: {result['error']}")
```

### Caching Strategy

```python
import hashlib
import pickle
import os
from datetime import datetime, timedelta
from typing import Optional

class TranscriptionCache:
    """Cache transcription results to avoid re-processing"""
    
    def __init__(self, cache_dir: str = ".transcription_cache", cache_ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_file_hash(self, file_path: str) -> str:
        """Generate hash for audio file"""
        hasher = hashlib.md5()
        
        # Include file path and modification time
        hasher.update(file_path.encode())
        hasher.update(str(os.path.getmtime(file_path)).encode())
        
        return hasher.hexdigest()
    
    def _get_cache_path(self, file_hash: str) -> str:
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{file_hash}.pkl")
    
    def get_cached_transcript(self, audio_file: str) -> Optional[aai.Transcript]:
        """Retrieve cached transcript if available and valid"""
        file_hash = self._get_file_hash(audio_file)
        cache_path = self._get_cache_path(file_hash)
        
        if not os.path.exists(cache_path):
            return None
        
        # Check cache age
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        if datetime.now() - cache_time > self.cache_ttl:
            os.remove(cache_path)  # Remove expired cache
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None
    
    def cache_transcript(self, audio_file: str, transcript: aai.Transcript) -> None:
        """Cache transcript result"""
        file_hash = self._get_file_hash(audio_file)
        cache_path = self._get_cache_path(file_hash)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(transcript, f)
        except Exception as e:
            print(f"Cache write error: {e}")
    
    def clear_cache(self) -> None:
        """Clear all cached transcripts"""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.pkl'):
                os.remove(os.path.join(self.cache_dir, filename))

# Cached transcription function
def transcribe_with_cache(audio_file: str, config: aai.TranscriptionConfig = None, cache: TranscriptionCache = None):
    """Transcribe with caching support"""
    
    if cache is None:
        cache = TranscriptionCache()
    
    # Try to get from cache
    cached_transcript = cache.get_cached_transcript(audio_file)
    if cached_transcript:
        print(f"✅ Using cached transcript for {audio_file}")
        return cached_transcript
    
    # Transcribe and cache
    print(f"🔄 Transcribing {audio_file}...")
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file, config=config)
    
    if transcript.status == "completed":
        cache.cache_transcript(audio_file, transcript)
        print(f"✅ Transcription cached for {audio_file}")
    
    return transcript

# Usage
cache = TranscriptionCache(cache_ttl_hours=24)
transcript = transcribe_with_cache("interview.wav", cache=cache)
```

### Memory Optimization

```python
import gc
from typing import Generator, List

def process_large_transcript(transcript: aai.Transcript) -> Generator[str, None, None]:
    """Process large transcripts in chunks to save memory"""
    
    # Process words in batches
    batch_size = 1000
    words = transcript.words
    
    for i in range(0, len(words), batch_size):
        batch = words[i:i + batch_size]
        
        # Process batch
        batch_text = " ".join(word.text for word in batch)
        yield batch_text
        
        # Clear batch from memory
        del batch
        gc.collect()

def extract_key_information(transcript: aai.Transcript) -> dict:
    """Extract only essential information to reduce memory usage"""
    
    key_info = {
        "text": transcript.text,
        "confidence": transcript.confidence,
        "duration": getattr(transcript, 'duration', None),
        "word_count": len(transcript.words) if transcript.words else 0
    }
    
    # Add advanced features if available
    if hasattr(transcript, 'sentiment_analysis_results') and transcript.sentiment_analysis_results:
        key_info["sentiment_summary"] = {
            "overall": transcript.sentiment_analysis_results[0].sentiment if transcript.sentiment_analysis_results else None
        }
    
    if hasattr(transcript, 'iab_categories_result') and transcript.iab_categories_result:
        key_info["topics"] = list(transcript.iab_categories_result.summary.keys())[:5]  # Top 5 topics
    
    return key_info

# Usage for memory-constrained environments
def memory_efficient_transcription(audio_file: str):
    """Transcribe and extract key info without keeping full transcript in memory"""
    
    transcript = transcriber.transcribe(audio_file)
    
    # Extract essential information
    key_info = extract_key_information(transcript)
    
    # Clear full transcript from memory
    del transcript
    gc.collect()
    
    return key_info
```

## Code Examples

### Interview Bot Integration

```python
import assemblyai as aai
from datetime import datetime
from typing import Dict, Any, Optional

class InterviewVoiceProcessor:
    """Voice processor specifically designed for interview scenarios"""
    
    def __init__(self, api_key: str):
        aai.settings.api_key = api_key
        self.transcriber = aai.Transcriber()
        
        # Interview-optimized configuration
        self.config = aai.TranscriptionConfig(
            language_detection=True,       # Support multiple languages
            speaker_labels=True,           # Identify interviewer vs candidate
            redact_pii=True,               # Protect candidate privacy
            redact_pii_policies=[
                aai.PIIRedactionPolicy.phone_number,
                aai.PIIRedactionPolicy.email_address,
                aai.PIIRedactionPolicy.social_security_number,
                aai.PIIRedactionPolicy.name  # Optional: may want to preserve names
            ],
            sentiment_analysis=True,       # Gauge candidate emotions
            iab_categories=True,          # Categorize discussion topics
            summarization=True,           # Generate interview summaries
            summary_model=aai.SummarizationModel.conversational,
            summary_type=aai.SummaryType.bullets,
            word_boost=[                  # Boost interview-related terms
                "experience", "skills", "project", "team", "leadership",
                "challenge", "solution", "responsibility", "achievement"
            ]
        )
    
    def process_interview_audio(self, audio_file: str, interview_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process interview audio with comprehensive analysis"""
        
        try:
            # Transcribe with interview-specific config
            transcript = self.transcriber.transcribe(audio_file, config=self.config)
            
            if transcript.status != "completed":
                return {"error": f"Transcription failed: {transcript.error}"}
            
            # Build comprehensive results
            results = {
                "transcription": {
                    "text": transcript.text,
                    "confidence": transcript.confidence,
                    "language": transcript.language_code if hasattr(transcript, 'language_code') else 'en',
                    "language_confidence": getattr(transcript, 'language_confidence', None)
                },
                "timing": {
                    "duration_ms": transcript.audio_duration if hasattr(transcript, 'audio_duration') else None,
                    "word_count": len(transcript.words) if transcript.words else 0,
                    "speaking_rate": self._calculate_speaking_rate(transcript)
                },
                "speakers": self._analyze_speakers(transcript),
                "sentiment": self._analyze_sentiment(transcript),
                "topics": self._extract_topics(transcript),
                "summary": transcript.summary if hasattr(transcript, 'summary') else None,
                "privacy": self._analyze_privacy(transcript),
                "insights": self._generate_insights(transcript, interview_context)
            }
            
            return results
            
        except Exception as e:
            return {"error": f"Processing failed: {str(e)}"}
    
    def _calculate_speaking_rate(self, transcript) -> Optional[float]:
        """Calculate words per minute"""
        if not transcript.words or not hasattr(transcript, 'audio_duration'):
            return None
        
        duration_minutes = transcript.audio_duration / (1000 * 60)
        return len(transcript.words) / duration_minutes if duration_minutes > 0 else None
    
    def _analyze_speakers(self, transcript) -> Dict[str, Any]:
        """Analyze speaker patterns"""
        if not transcript.utterances:
            return {"count": 1, "distribution": {}}
        
        speaker_stats = {}
        for utterance in transcript.utterances:
            speaker = utterance.speaker
            if speaker not in speaker_stats:
                speaker_stats[speaker] = {
                    "word_count": 0,
                    "duration_ms": 0,
                    "utterances": 0
                }
            
            words_in_utterance = len(utterance.text.split())
            speaker_stats[speaker]["word_count"] += words_in_utterance
            speaker_stats[speaker]["duration_ms"] += utterance.end - utterance.start
            speaker_stats[speaker]["utterances"] += 1
        
        return {
            "count": len(speaker_stats),
            "distribution": speaker_stats
        }
    
    def _analyze_sentiment(self, transcript) -> Dict[str, Any]:
        """Analyze sentiment patterns"""
        if not hasattr(transcript, 'sentiment_analysis_results') or not transcript.sentiment_analysis_results:
            return {"overall": "neutral", "distribution": {}}
        
        sentiments = [result.sentiment for result in transcript.sentiment_analysis_results]
        sentiment_counts = {
            "positive": sentiments.count("POSITIVE"),
            "neutral": sentiments.count("NEUTRAL"), 
            "negative": sentiments.count("NEGATIVE")
        }
        
        # Determine overall sentiment
        overall = max(sentiment_counts, key=sentiment_counts.get)
        
        return {
            "overall": overall.lower(),
            "distribution": sentiment_counts,
            "confidence": sum(result.confidence for result in transcript.sentiment_analysis_results) / len(transcript.sentiment_analysis_results)
        }
    
    def _extract_topics(self, transcript) -> List[str]:
        """Extract relevant topics discussed"""
        if not hasattr(transcript, 'iab_categories_result') or not transcript.iab_categories_result:
            return []
        
        # Get top topics with high relevance
        topics = []
        for category, relevance in transcript.iab_categories_result.summary.items():
            if relevance > 0.5:  # High relevance threshold
                topics.append(category)
        
        return topics[:10]  # Top 10 topics
    
    def _analyze_privacy(self, transcript) -> Dict[str, Any]:
        """Analyze privacy protection effectiveness"""
        privacy_info = {
            "pii_detected": False,
            "pii_redacted": False,
            "redaction_count": 0
        }
        
        if hasattr(transcript, 'redacted_pii') and transcript.redacted_pii:
            privacy_info["pii_detected"] = True
            privacy_info["pii_redacted"] = True
            privacy_info["redaction_count"] = len(transcript.redacted_pii)
        
        return privacy_info
    
    def _generate_insights(self, transcript, interview_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate interview-specific insights"""
        insights = {
            "quality_score": self._calculate_quality_score(transcript),
            "engagement_level": self._assess_engagement(transcript),
            "communication_style": self._analyze_communication_style(transcript),
            "technical_content": self._detect_technical_content(transcript)
        }
        
        return insights
    
    def _calculate_quality_score(self, transcript) -> float:
        """Calculate overall audio/transcription quality score"""
        score = transcript.confidence
        
        # Adjust based on other factors
        if hasattr(transcript, 'language_confidence') and transcript.language_confidence:
            score = (score + transcript.language_confidence) / 2
        
        return round(score, 2)
    
    def _assess_engagement(self, transcript) -> str:
        """Assess candidate engagement level"""
        # Simple heuristic based on response length and sentiment
        word_count = len(transcript.words) if transcript.words else 0
        
        if word_count < 50:
            return "low"
        elif word_count > 200:
            return "high"
        else:
            return "medium"
    
    def _analyze_communication_style(self, transcript) -> Dict[str, Any]:
        """Analyze communication style characteristics"""
        text = transcript.text.lower()
        
        # Count question words (showing curiosity)
        question_words = ["what", "how", "why", "when", "where", "who"]
        question_count = sum(text.count(word) for word in question_words)
        
        # Count uncertainty words
        uncertainty_words = ["maybe", "perhaps", "possibly", "might", "could"]
        uncertainty_count = sum(text.count(word) for word in uncertainty_words)
        
        # Count confidence words
        confidence_words = ["definitely", "certainly", "absolutely", "confident", "sure"]
        confidence_count = sum(text.count(word) for word in confidence_words)
        
        return {
            "inquisitive": question_count > 3,
            "uncertainty_level": "high" if uncertainty_count > 5 else "medium" if uncertainty_count > 2 else "low",
            "confidence_level": "high" if confidence_count > 3 else "medium" if confidence_count > 1 else "low"
        }
    
    def _detect_technical_content(self, transcript) -> Dict[str, Any]:
        """Detect technical discussion content"""
        text = transcript.text.lower()
        
        # Technical keywords by category
        tech_categories = {
            "programming": ["code", "programming", "software", "development", "algorithm", "database"],
            "leadership": ["team", "manage", "lead", "project", "coordinate", "responsibility"],
            "problem_solving": ["problem", "solution", "challenge", "resolve", "debug", "troubleshoot"],
            "tools": ["git", "docker", "kubernetes", "aws", "python", "javascript", "react", "sql"]
        }
        
        detected_categories = {}
        for category, keywords in tech_categories.items():
            count = sum(text.count(keyword) for keyword in keywords)
            detected_categories[category] = count
        
        return {
            "technical_depth": "high" if sum(detected_categories.values()) > 10 else "medium" if sum(detected_categories.values()) > 5 else "low",
            "categories": detected_categories
        }

# Usage Example
processor = InterviewVoiceProcessor("your_api_key")

# Process interview audio
interview_context = {
    "position": "Senior Python Developer",
    "interviewer": "John Smith",
    "date": datetime.now().isoformat()
}

results = processor.process_interview_audio("candidate_interview.wav", interview_context)

# Display results
if "error" not in results:
    print(f"✅ Interview processed successfully")
    print(f"📊 Quality Score: {results['insights']['quality_score']}")
    print(f"🎯 Engagement: {results['insights']['engagement_level']}")
    print(f"💭 Overall Sentiment: {results['sentiment']['overall']}")
    print(f"👥 Speakers Detected: {results['speakers']['count']}")
    print(f"🏷️ Topics: {', '.join(results['topics'][:5])}")
    print(f"📝 Summary: {results['summary']}")
else:
    print(f"❌ Error: {results['error']}")
```

### Webhook Integration

```python
from flask import Flask, request, jsonify
import assemblyai as aai
from typing import Dict, Any
import hmac
import hashlib

app = Flask(__name__)

class WebhookHandler:
    """Handle AssemblyAI webhook notifications"""
    
    def __init__(self, webhook_secret: str = None):
        self.webhook_secret = webhook_secret
        self.transcription_callbacks = {}
    
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        if not self.webhook_secret:
            return True  # Skip verification if no secret configured
        
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def register_callback(self, transcript_id: str, callback_func):
        """Register callback for transcript completion"""
        self.transcription_callbacks[transcript_id] = callback_func
    
    def handle_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook event"""
        
        transcript_id = event_data.get("transcript_id")
        status = event_data.get("status")
        
        if status == "completed":
            # Fetch full transcript
            transcript = aai.Transcript.get_by_id(transcript_id)
            
            # Call registered callback if exists
            if transcript_id in self.transcription_callbacks:
                callback = self.transcription_callbacks[transcript_id]
                try:
                    callback(transcript)
                    del self.transcription_callbacks[transcript_id]  # Clean up
                except Exception as e:
                    print(f"Callback error: {e}")
            
            return {"status": "processed", "transcript_id": transcript_id}
        
        elif status == "error":
            error_msg = event_data.get("error", "Unknown error")
            print(f"Transcription failed: {transcript_id} - {error_msg}")
            
            # Clean up callback
            if transcript_id in self.transcription_callbacks:
                del self.transcription_callbacks[transcript_id]
            
            return {"status": "error", "transcript_id": transcript_id}
        
        return {"status": "ignored"}

# Global webhook handler
webhook_handler = WebhookHandler(webhook_secret="your_webhook_secret")

@app.route("/webhook/assemblyai", methods=["POST"])
def handle_assemblyai_webhook():
    """Handle AssemblyAI webhook endpoint"""
    
    # Verify signature
    signature = request.headers.get("X-AssemblyAI-Signature", "")
    if not webhook_handler.verify_webhook(request.data, signature):
        return jsonify({"error": "Invalid signature"}), 401
    
    # Process event
    event_data = request.json
    result = webhook_handler.handle_webhook_event(event_data)
    
    return jsonify(result)

def async_transcribe_with_webhook(audio_file: str, callback_func=None) -> str:
    """Start async transcription with webhook notification"""
    
    # Configure webhook URL
    config = aai.TranscriptionConfig(
        webhook_url="https://yourapp.com/webhook/assemblyai",
        # Add other configuration as needed
        sentiment_analysis=True,
        iab_categories=True
    )
    
    # Submit transcription
    transcript = transcriber.submit(audio_file, config=config)
    transcript_id = transcript.id
    
    # Register callback if provided
    if callback_func:
        webhook_handler.register_callback(transcript_id, callback_func)
    
    print(f"Transcription submitted: {transcript_id}")
    return transcript_id

# Example callback function
def interview_completion_callback(transcript):
    """Handle completed interview transcription"""
    print(f"Interview transcript completed: {transcript.id}")
    
    # Process results
    results = {
        "text": transcript.text,
        "confidence": transcript.confidence,
        "duration": len(transcript.text.split()) * 0.5  # Rough estimate
    }
    
    # Save to database or send notification
    print(f"Saving interview results: {len(results['text'])} characters")
    
    # Could integrate with email, Slack, etc.
    # send_notification(f"Interview transcription ready: {transcript.id}")

# Usage
if __name__ == "__main__":
    # Start async transcription
    transcript_id = async_transcribe_with_webhook(
        "interview.wav", 
        callback_func=interview_completion_callback
    )
    
    # Run webhook server
    app.run(host="0.0.0.0", port=5000)
```

## Best Practices

### 1. Audio Preparation

```python
def optimize_audio_for_transcription(input_file: str, output_file: str) -> str:
    """Optimize audio file for best transcription results"""
    from pydub import AudioSegment
    from pydub.effects import normalize
    
    # Load audio
    audio = AudioSegment.from_file(input_file)
    
    # Optimize settings
    audio = audio.set_frame_rate(16000)  # Optimal sample rate
    audio = audio.set_channels(1)        # Convert to mono
    audio = normalize(audio)             # Normalize volume
    
    # Remove silence from beginning and end
    audio = audio.strip_silence(silence_threshold=-40.0)
    
    # Export optimized version
    audio.export(output_file, format="wav")
    
    return output_file

# Usage
optimized_file = optimize_audio_for_transcription("raw_interview.m4a", "optimized_interview.wav")
transcript = transcriber.transcribe(optimized_file)
```

### 2. Configuration Best Practices

```python
# Production configuration
def get_production_config(use_case: str = "interview") -> aai.TranscriptionConfig:
    """Get optimized configuration for different use cases"""
    
    base_config = {
        "punctuate": True,
        "format_text": True,
        "language_detection": True
    }
    
    if use_case == "interview":
        return aai.TranscriptionConfig(
            **base_config,
            speaker_labels=True,
            redact_pii=True,
            redact_pii_policies=[
                aai.PIIRedactionPolicy.phone_number,
                aai.PIIRedactionPolicy.email_address,
                aai.PIIRedactionPolicy.social_security_number
            ],
            sentiment_analysis=True,
            iab_categories=True,
            summarization=True,
            summary_type=aai.SummaryType.bullets,
            word_boost=["experience", "skills", "project", "team", "leadership"]
        )
    
    elif use_case == "meeting":
        return aai.TranscriptionConfig(
            **base_config,
            speaker_labels=True,
            speakers_expected=4,
            auto_chapters=True,
            summarization=True,
            summary_model=aai.SummarizationModel.conversational
        )
    
    elif use_case == "content_safety":
        return aai.TranscriptionConfig(
            **base_config,
            content_safety=True,
            redact_pii=True,
            redact_pii_policies=list(aai.PIIRedactionPolicy)
        )
    
    else:  # default
        return aai.TranscriptionConfig(**base_config)
```

### 3. Error Recovery Strategies

```python
import time
import random
from typing import Optional, Callable

class RobustTranscriber:
    """Transcriber with built-in resilience"""
    
    def __init__(self, api_key: str):
        aai.settings.api_key = api_key
        self.transcriber = aai.Transcriber()
        self.max_retries = 3
        self.base_delay = 1.0
    
    def transcribe_with_resilience(
        self, 
        audio_file: str, 
        config: aai.TranscriptionConfig = None,
        progress_callback: Callable[[str], None] = None
    ) -> Optional[aai.Transcript]:
        """Transcribe with automatic retry and progress tracking"""
        
        for attempt in range(self.max_retries):
            try:
                if progress_callback:
                    progress_callback(f"Starting transcription attempt {attempt + 1}")
                
                transcript = self.transcriber.transcribe(audio_file, config=config)
                
                if transcript.status == "completed":
                    if progress_callback:
                        progress_callback("Transcription completed successfully")
                    return transcript
                elif transcript.status == "error":
                    raise Exception(f"Transcription failed: {transcript.error}")
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    if progress_callback:
                        progress_callback(f"All attempts failed: {e}")
                    return None
                
                # Calculate delay with exponential backoff and jitter
                delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                
                if progress_callback:
                    progress_callback(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
                
                time.sleep(delay)
        
        return None
    
    def transcribe_with_fallback(
        self, 
        audio_file: str, 
        primary_config: aai.TranscriptionConfig,
        fallback_config: aai.TranscriptionConfig = None
    ) -> Optional[aai.Transcript]:
        """Try transcription with primary config, fallback to simpler config if needed"""
        
        # Try with primary configuration
        try:
            return self.transcribe_with_resilience(audio_file, primary_config)
        except Exception as e:
            print(f"Primary configuration failed: {e}")
        
        # Try with fallback configuration
        if fallback_config:
            try:
                print("Attempting with fallback configuration...")
                return self.transcribe_with_resilience(audio_file, fallback_config)
            except Exception as e:
                print(f"Fallback configuration also failed: {e}")
        
        return None

# Usage
robust_transcriber = RobustTranscriber("your_api_key")

# Primary config with all features
primary_config = aai.TranscriptionConfig(
    language_detection=True,
    speaker_labels=True,
    redact_pii=True,
    sentiment_analysis=True,
    iab_categories=True,
    summarization=True
)

# Fallback config with basic features only
fallback_config = aai.TranscriptionConfig(
    language_detection=True
)

def progress_tracker(message: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

transcript = robust_transcriber.transcribe_with_fallback(
    "interview.wav",
    primary_config=primary_config,
    fallback_config=fallback_config
)
```

### 4. Monitoring and Metrics

```python
import time
from dataclasses import dataclass, field
from typing import Dict, List
from collections import defaultdict, deque

@dataclass
class TranscriptionMetrics:
    """Track transcription performance metrics"""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration_seconds: float = 0.0
    total_processing_time: float = 0.0
    confidence_scores: List[float] = field(default_factory=list)
    error_types: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    language_distribution: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    recent_response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def record_success(self, transcript: aai.Transcript, processing_time: float):
        """Record successful transcription"""
        self.total_requests += 1
        self.successful_requests += 1
        self.total_processing_time += processing_time
        self.recent_response_times.append(processing_time)
        
        if transcript.confidence:
            self.confidence_scores.append(transcript.confidence)
        
        if hasattr(transcript, 'language_code') and transcript.language_code:
            self.language_distribution[transcript.language_code] += 1
        
        if hasattr(transcript, 'audio_duration') and transcript.audio_duration:
            self.total_duration_seconds += transcript.audio_duration / 1000
    
    def record_failure(self, error: str, processing_time: float):
        """Record failed transcription"""
        self.total_requests += 1
        self.failed_requests += 1
        self.total_processing_time += processing_time
        self.recent_response_times.append(processing_time)
        self.error_types[error] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if self.total_requests == 0:
            return {"error": "No requests recorded"}
        
        success_rate = self.successful_requests / self.total_requests
        avg_processing_time = self.total_processing_time / self.total_requests
        avg_confidence = sum(self.confidence_scores) / len(self.confidence_scores) if self.confidence_scores else 0
        
        recent_avg_time = sum(self.recent_response_times) / len(self.recent_response_times) if self.recent_response_times else 0
        
        return {
            "total_requests": self.total_requests,
            "success_rate": round(success_rate, 3),
            "avg_processing_time_seconds": round(avg_processing_time, 2),
            "avg_confidence_score": round(avg_confidence, 3),
            "recent_avg_response_time": round(recent_avg_time, 2),
            "total_audio_duration_minutes": round(self.total_duration_seconds / 60, 1),
            "most_common_language": max(self.language_distribution, key=self.language_distribution.get) if self.language_distribution else "unknown",
            "error_breakdown": dict(self.error_types),
            "languages_processed": len(self.language_distribution)
        }

class MonitoredTranscriber:
    """Transcriber with built-in monitoring"""
    
    def __init__(self, api_key: str):
        aai.settings.api_key = api_key
        self.transcriber = aai.Transcriber()
        self.metrics = TranscriptionMetrics()
    
    def transcribe(self, audio_file: str, config: aai.TranscriptionConfig = None) -> Optional[aai.Transcript]:
        """Transcribe with metrics collection"""
        start_time = time.time()
        
        try:
            transcript = self.transcriber.transcribe(audio_file, config=config)
            processing_time = time.time() - start_time
            
            if transcript.status == "completed":
                self.metrics.record_success(transcript, processing_time)
                return transcript
            else:
                self.metrics.record_failure(f"status_{transcript.status}", processing_time)
                return None
                
        except Exception as e:
            processing_time = time.time() - start_time
            self.metrics.record_failure(str(type(e).__name__), processing_time)
            return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.get_summary()
    
    def reset_metrics(self):
        """Reset metrics collection"""
        self.metrics = TranscriptionMetrics()

# Usage
monitored_transcriber = MonitoredTranscriber("your_api_key")

# Process multiple files
audio_files = ["interview1.wav", "interview2.wav", "interview3.wav"]
for audio_file in audio_files:
    transcript = monitored_transcriber.transcribe(audio_file)
    if transcript:
        print(f"✅ {audio_file}: {len(transcript.text)} characters")
    else:
        print(f"❌ {audio_file}: Failed")

# Get performance report
metrics = monitored_transcriber.get_metrics()
print("\n📊 Performance Report:")
print(f"Success Rate: {metrics['success_rate']:.1%}")
print(f"Avg Processing Time: {metrics['avg_processing_time_seconds']:.1f}s")
print(f"Avg Confidence: {metrics['avg_confidence_score']:.1%}")
print(f"Most Common Language: {metrics['most_common_language']}")
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Authentication Errors

```bash
# Error: 401 Unauthorized
# Solution: Check API key
python -c "
import assemblyai as aai
aai.settings.api_key = 'your_key'
print('API Key set:', aai.settings.api_key[:10] + '...')
"
```

#### 2. Audio Format Issues

```python
def diagnose_audio_file(file_path: str):
    """Diagnose audio file compatibility"""
    from pydub import AudioSegment
    import os
    
    print(f"Analyzing: {file_path}")
    
    # Check file existence and size
    if not os.path.exists(file_path):
        print("❌ File does not exist")
        return
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"📁 File size: {file_size_mb:.1f} MB")
    
    if file_size_mb > 25:
        print("⚠️  File exceeds 25MB limit")
    
    try:
        # Analyze audio properties
        audio = AudioSegment.from_file(file_path)
        
        print(f"⏱️  Duration: {len(audio) / 1000:.1f} seconds")
        print(f"🔊 Sample rate: {audio.frame_rate} Hz")
        print(f"🎵 Channels: {audio.channels}")
        print(f"📊 Bit depth: {audio.sample_width * 8} bit")
        
        # Recommendations
        if audio.frame_rate < 16000:
            print("💡 Recommendation: Increase sample rate to 16kHz or higher")
        
        if audio.channels > 1:
            print("💡 Recommendation: Convert to mono for better processing")
        
        print("✅ Audio file appears compatible")
        
    except Exception as e:
        print(f"❌ Audio analysis failed: {e}")

# Usage
diagnose_audio_file("problematic_audio.mp3")
```

#### 3. Performance Issues

```python
def performance_test():
    """Test API performance"""
    import time
    
    start_time = time.time()
    
    try:
        # Simple transcription test
        test_audio = "https://github.com/AssemblyAI-Examples/audio-examples/raw/main/20210130_001_FarFromTheTree.wav"
        
        transcript = transcriber.transcribe(test_audio)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✅ Test completed in {processing_time:.1f} seconds")
        print(f"📊 Confidence: {transcript.confidence:.1%}")
        print(f"📝 Text length: {len(transcript.text)} characters")
        
        # Performance evaluation
        if processing_time < 30:
            print("🚀 Performance: Excellent")
        elif processing_time < 60:
            print("👍 Performance: Good")
        else:
            print("🐌 Performance: Slow - Check network connection")
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")

performance_test()
```

#### 4. Feature Availability Issues

```python
def check_feature_availability():
    """Check which features are available on current plan"""
    
    # Test basic features
    basic_config = aai.TranscriptionConfig()
    print("✅ Basic transcription: Available")
    
    # Test advanced features
    advanced_features = [
        ("Language Detection", "language_detection"),
        ("Speaker Labels", "speaker_labels"),
        ("PII Redaction", "redact_pii"),
        ("Sentiment Analysis", "sentiment_analysis"),
        ("Topic Detection", "iab_categories"),
        ("Summarization", "summarization"),
        ("Content Safety", "content_safety")
    ]
    
    for feature_name, feature_param in advanced_features:
        try:
            config_dict = {feature_param: True}
            config = aai.TranscriptionConfig(**config_dict)
            print(f"✅ {feature_name}: Available")
        except Exception as e:
            print(f"❌ {feature_name}: Not available - {e}")

check_feature_availability()
```

### Debugging Tools

```python
import logging

def setup_debug_logging():
    """Enable debug logging for AssemblyAI"""
    
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create logger
    logger = logging.getLogger('assemblyai')
    logger.setLevel(logging.DEBUG)
    
    # Add handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    print("🐛 Debug logging enabled")

# Usage
setup_debug_logging()

# Now all AssemblyAI operations will log debug information
transcript = transcriber.transcribe("audio.wav")
```

## Cost Optimization

### 1. Plan Comparison

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| **Monthly Hours** | 5 hours | Unlimited | Unlimited |
| **File Size** | 25MB | 50MB | 50MB+ |
| **Basic Transcription** | ✅ | ✅ | ✅ |
| **Language Detection** | ✅ | ✅ | ✅ |
| **Speaker Labels** | ❌ | ✅ | ✅ |
| **PII Redaction** | ❌ | ✅ | ✅ |
| **Sentiment Analysis** | ❌ | ✅ | ✅ |
| **Topic Detection** | ❌ | ✅ | ✅ |
| **Summarization** | ❌ | ✅ | ✅ |
| **Content Safety** | ❌ | ✅ | ✅ |
| **Priority Support** | ❌ | ❌ | ✅ |

### 2. Cost-Effective Configuration

```python
def get_cost_optimized_config(budget_level: str = "low") -> aai.TranscriptionConfig:
    """Get configuration optimized for different budget levels"""
    
    if budget_level == "low":
        # Minimal features for maximum cost savings
        return aai.TranscriptionConfig(
            punctuate=True,
            format_text=True
            # No advanced features to stay on free tier
        )
    
    elif budget_level == "medium":
        # Essential features only
        return aai.TranscriptionConfig(
            punctuate=True,
            format_text=True,
            language_detection=True,
            speaker_labels=True  # Most valuable feature
        )
    
    elif budget_level == "high":
        # Full features for maximum value
        return aai.TranscriptionConfig(
            punctuate=True,
            format_text=True,
            language_detection=True,
            speaker_labels=True,
            redact_pii=True,
            sentiment_analysis=True,
            iab_categories=True,
            summarization=True
        )

# Usage tracking
class CostTracker:
    """Track API usage costs"""
    
    def __init__(self, rate_per_hour: float = 0.65):  # Pro plan rate
        self.rate_per_hour = rate_per_hour
        self.total_duration_seconds = 0
        self.total_requests = 0
        self.feature_usage = defaultdict(int)
    
    def track_usage(self, duration_seconds: float, features_used: List[str]):
        """Track usage for cost calculation"""
        self.total_duration_seconds += duration_seconds
        self.total_requests += 1
        
        for feature in features_used:
            self.feature_usage[feature] += 1
    
    def get_estimated_cost(self) -> Dict[str, Any]:
        """Calculate estimated costs"""
        duration_hours = self.total_duration_seconds / 3600
        base_cost = duration_hours * self.rate_per_hour
        
        return {
            "duration_hours": round(duration_hours, 2),
            "estimated_cost_usd": round(base_cost, 2),
            "requests": self.total_requests,
            "avg_cost_per_request": round(base_cost / self.total_requests if self.total_requests > 0 else 0, 3),
            "feature_usage": dict(self.feature_usage)
        }

# Usage
cost_tracker = CostTracker()

# Track each transcription
audio_duration = 300  # 5 minutes
features_used = ["language_detection", "speaker_labels", "sentiment_analysis"]
cost_tracker.track_usage(audio_duration, features_used)

print(cost_tracker.get_estimated_cost())
```

### 3. Batch Processing for Cost Savings

```python
def process_batch_efficiently(audio_files: List[str], max_batch_size: int = 10):
    """Process files in batches to optimize costs"""
    
    # Group files by similar characteristics to optimize processing
    batches = []
    current_batch = []
    current_batch_duration = 0
    max_batch_duration = 3600  # 1 hour per batch
    
    for audio_file in audio_files:
        # Estimate duration (you might want to actually check file duration)
        estimated_duration = 300  # 5 minutes average
        
        if (len(current_batch) >= max_batch_size or 
            current_batch_duration + estimated_duration > max_batch_duration):
            
            batches.append(current_batch)
            current_batch = [audio_file]
            current_batch_duration = estimated_duration
        else:
            current_batch.append(audio_file)
            current_batch_duration += estimated_duration
    
    if current_batch:
        batches.append(current_batch)
    
    print(f"📦 Created {len(batches)} batches for processing")
    
    # Process each batch
    results = []
    for i, batch in enumerate(batches):
        print(f"Processing batch {i+1}/{len(batches)}: {len(batch)} files")
        
        batch_results = []
        for audio_file in batch:
            try:
                transcript = transcriber.transcribe(audio_file)
                batch_results.append({
                    "file": audio_file,
                    "status": "success",
                    "transcript": transcript
                })
            except Exception as e:
                batch_results.append({
                    "file": audio_file,
                    "status": "error",
                    "error": str(e)
                })
        
        results.extend(batch_results)
        
        # Brief pause between batches to avoid rate limits
        time.sleep(1)
    
    return results
```

## Migration Guide

### From Old Implementation to New SDK

If you're upgrading from an older implementation, here's how to migrate:

#### Old Way (Incorrect)
```python
# ❌ Don't use this approach
client = aai.Transcriber()
aai.settings.api_key = api_key
config = aai.TranscriptionConfig(...)
transcript = await client.transcribe_with_retries(audio_path, config)
if transcript.status == aai.TranscriptStatus.error:
    handle_error()
```

#### New Way (Correct)
```python
# ✅ Use this approach
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
    handle_error()
```

### Migration Checklist

- [ ] Update to `assemblyai>=0.30.0`
- [ ] Initialize API key with `aai.settings.api_key`
- [ ] Create transcriber with `aai.Transcriber()`
- [ ] Use new configuration options
- [ ] Update status checking logic
- [ ] Test advanced features
- [ ] Update error handling
- [ ] Verify performance improvements

---

*This comprehensive reference covers all aspects of AssemblyAI integration for the AI Interviewer Bot. For the latest updates and features, always refer to the [official AssemblyAI documentation](https://www.assemblyai.com/docs/).*