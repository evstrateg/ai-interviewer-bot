"""
Shared pytest configuration and fixtures for AssemblyAI integration tests

This file provides common fixtures, configuration, and utilities used across
all test modules in the project.
"""

import asyncio
import os
import tempfile
import wave
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

import pytest
import pytest_asyncio

# Test constants
TEST_API_KEY = "test_api_key_12345"
TEST_AUDIO_DURATION = 5.0
TEST_AUDIO_SIZE = 1024 * 100  # 100KB
INTEGRATION_TEST_ENABLED = os.getenv('ASSEMBLYAI_INTEGRATION_TESTS', 'false').lower() == 'true'

# Configure asyncio for tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# =============================================================================
# CONFIGURATION FIXTURES
# =============================================================================

@pytest.fixture
def test_config():
    """Create comprehensive test configuration with all features enabled"""
    from src.handlers.voice_handler import VoiceProcessingConfig
    
    return VoiceProcessingConfig(
        assemblyai_api_key=TEST_API_KEY,
        max_file_size_mb=25,
        min_duration_seconds=0.5,
        max_duration_seconds=600,
        confidence_threshold=0.6,
        default_language="en",
        enable_auto_language_detection=True,
        enable_speaker_labels=True,
        enable_punctuation=True,
        enable_format_text=True,
        enable_disfluencies=False,
        enable_pii_redaction=True,
        pii_redaction_policies=["person_name", "phone_number", "email_address"],
        pii_substitution_policy="hash",
        enable_summarization=True,
        enable_auto_chapters=False,
        enable_content_safety=True,
        enable_topic_detection=True,
        enable_iab_categories=False,
        enable_entity_detection=False,
        enable_sentiment_analysis=True,
        boost_param="default",
        concurrent_requests=3,
        retry_attempts=3,
        retry_delay_seconds=1.0,
        max_retry_delay=10.0
    )

@pytest.fixture
def minimal_config():
    """Create minimal test configuration with basic features only"""
    from src.handlers.voice_handler import VoiceProcessingConfig
    
    return VoiceProcessingConfig(
        assemblyai_api_key=TEST_API_KEY,
        enable_auto_language_detection=False,
        enable_speaker_labels=False,
        enable_pii_redaction=False,
        enable_summarization=False,
        enable_content_safety=False,
        enable_topic_detection=False,
        enable_sentiment_analysis=False
    )

@pytest.fixture
def real_config():
    """Create configuration for real API testing (if enabled)"""
    from src.handlers.voice_handler import VoiceProcessingConfig
    
    real_api_key = os.getenv('ASSEMBLYAI_API_KEY')
    if not real_api_key:
        pytest.skip("ASSEMBLYAI_API_KEY not set for real API tests")
    
    return VoiceProcessingConfig(
        assemblyai_api_key=real_api_key,
        retry_attempts=2,  # Reduce for faster testing
        retry_delay_seconds=1.0,
        enable_auto_language_detection=True,
        enable_summarization=False,  # Disable to reduce API cost
        enable_content_safety=False,
        enable_topic_detection=False
    )

# =============================================================================
# MOCK TELEGRAM FIXTURES
# =============================================================================

@pytest.fixture
def mock_telegram_voice():
    """Create mock Telegram voice message object"""
    voice = Mock()
    voice.duration = TEST_AUDIO_DURATION
    voice.file_size = TEST_AUDIO_SIZE
    voice.mime_type = "audio/ogg"
    voice.file_id = "test_file_id_123"
    voice.file_unique_id = "unique_test_123"
    return voice

@pytest.fixture
def mock_telegram_file():
    """Create mock Telegram file object"""
    file = Mock()
    file.file_id = "test_file_id_123"
    file.file_unique_id = "unique_test_123"
    file.mime_type = "audio/ogg"
    file.file_size = TEST_AUDIO_SIZE
    file.file_path = "voice/file_123.ogg"
    
    # Mock async download method
    async def mock_download(file_path):
        # Create dummy audio file
        with open(file_path, 'wb') as f:
            f.write(b'OggS\x00\x02\x00\x00' + b'\x00' * (TEST_AUDIO_SIZE - 4))
    
    file.download_to_drive = AsyncMock(side_effect=mock_download)
    return file

@pytest.fixture
def mock_telegram_update(mock_telegram_voice):
    """Create mock Telegram update with voice message"""
    update = Mock()
    update.effective_user.id = 12345
    update.effective_user.username = "test_user"
    update.effective_user.first_name = "Test"
    update.effective_chat.id = 67890
    update.effective_chat.type = "private"
    update.message.voice = mock_telegram_voice
    update.message.message_id = 98765
    update.message.date = "2024-01-15T10:30:00Z"
    return update

@pytest.fixture
def mock_telegram_context(mock_telegram_file):
    """Create mock Telegram context"""
    context = Mock()
    context.bot.get_file = AsyncMock(return_value=mock_telegram_file)
    context.bot.send_chat_action = AsyncMock()
    context.bot.send_message = AsyncMock()
    context.bot.edit_message_text = AsyncMock()
    return context

# =============================================================================
# AUDIO FILE FIXTURES
# =============================================================================

@pytest.fixture
def sample_ogg_file():
    """Create a temporary OGG audio file for testing"""
    temp_file = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
    # Create minimal OGG file header + some data
    ogg_header = b'OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00'
    temp_file.write(ogg_header + b'\x00' * (TEST_AUDIO_SIZE - len(ogg_header)))
    temp_file.close()
    
    yield Path(temp_file.name)
    
    # Cleanup
    try:
        Path(temp_file.name).unlink()
    except FileNotFoundError:
        pass

@pytest.fixture
def sample_wav_file():
    """Create a temporary WAV audio file for testing"""
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    
    # Create a proper WAV file with 1 second of silence
    with wave.open(temp_file.name, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(16000)  # 16kHz
        # 1 second of silence
        silence = b'\x00\x00' * 16000
        wav_file.writeframes(silence)
    
    yield Path(temp_file.name)
    
    # Cleanup
    try:
        Path(temp_file.name).unlink()
    except FileNotFoundError:
        pass

@pytest.fixture
def sample_mp3_file():
    """Create a temporary MP3-like file for testing"""
    temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    # Create minimal MP3 header
    mp3_header = b'\xFF\xFB\x90\x00'  # MP3 frame header
    temp_file.write(mp3_header + b'\x00' * (TEST_AUDIO_SIZE - len(mp3_header)))
    temp_file.close()
    
    yield Path(temp_file.name)
    
    # Cleanup
    try:
        Path(temp_file.name).unlink()
    except FileNotFoundError:
        pass

@pytest.fixture
def large_audio_file():
    """Create a large audio file for testing file size limits"""
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    
    # Create 30MB file (over the 25MB limit)
    large_size = 30 * 1024 * 1024
    with open(temp_file.name, 'wb') as f:
        # Write WAV header
        f.write(b'RIFF\x00\x00\x00\x00WAVE')
        # Fill with zeros
        f.write(b'\x00' * (large_size - 12))
    
    yield Path(temp_file.name)
    
    # Cleanup
    try:
        Path(temp_file.name).unlink()
    except FileNotFoundError:
        pass

@pytest.fixture
def corrupted_audio_file():
    """Create a corrupted audio file for testing error handling"""
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    # Write invalid audio data
    temp_file.write(b'This is not valid audio data at all!')
    temp_file.close()
    
    yield Path(temp_file.name)
    
    # Cleanup
    try:
        Path(temp_file.name).unlink()
    except FileNotFoundError:
        pass

# =============================================================================
# METADATA FIXTURES
# =============================================================================

@pytest.fixture
def test_audio_metadata():
    """Create standard test audio metadata"""
    return {
        "duration": TEST_AUDIO_DURATION,
        "channels": 1,
        "frame_rate": 16000,
        "format": "ogg",
        "size_bytes": TEST_AUDIO_SIZE,
        "processing_time": 0.5,
        "compression_ratio": 0.8,
        "telegram_duration": TEST_AUDIO_DURATION,
        "telegram_file_size": TEST_AUDIO_SIZE,
        "telegram_mime_type": "audio/ogg"
    }

@pytest.fixture
def large_file_metadata():
    """Create metadata for large file testing"""
    return {
        "duration": 300.0,  # 5 minutes
        "channels": 1,
        "frame_rate": 16000,
        "format": "wav",
        "size_bytes": 20 * 1024 * 1024,  # 20MB
        "processing_time": 2.0,
        "compression_ratio": 1.0,
        "telegram_duration": 300.0,
        "telegram_file_size": 20 * 1024 * 1024,
        "telegram_mime_type": "audio/wav"
    }

# =============================================================================
# MOCK ASSEMBLYAI FIXTURES
# =============================================================================

@pytest.fixture
def mock_successful_transcript():
    """Create mock successful AssemblyAI transcript"""
    transcript = Mock()
    transcript.id = "transcript_success_123"
    transcript.status = "completed"
    transcript.text = "Hello, this is a successful test transcription with good quality audio"
    transcript.confidence = 0.95
    transcript.language_code = "en"
    transcript.audio_url = "https://api.assemblyai.com/v2/transcript/transcript_success_123/audio"
    transcript.words = []
    transcript.error = None
    
    # Enhanced features
    transcript.summary = "This is a test summary of the transcription"
    
    # Language detection
    language_result = Mock()
    language_result.language = "en"
    language_result.confidence = 0.98
    transcript.language_detection_results = [language_result]
    
    # Speaker labels
    utterance = Mock()
    utterance.speaker = "A"
    utterance.text = "Hello, this is a successful test"
    utterance.confidence = 0.95
    utterance.start = 0
    utterance.end = 2500
    transcript.utterances = [utterance]
    
    # Chapters
    chapter = Mock()
    chapter.summary = "Introduction and greeting"
    chapter.headline = "Test Introduction"
    chapter.start = 0
    chapter.end = 5000
    transcript.chapters = [chapter]
    
    # Content safety
    safety_result = Mock()
    safety_result.label = "safe_content"
    safety_result.confidence = 0.99
    safety_result.severity = 0.1
    safety_labels = Mock()
    safety_labels.results = [safety_result]
    transcript.content_safety_labels = safety_labels
    
    # Topics
    topic_label = Mock()
    topic_label.relevance = 0.8
    topic_label.label = "technology"
    topic = Mock()
    topic.text = "test transcription"
    topic.labels = [topic_label]
    transcript.topics = [topic]
    
    # Sentiment analysis
    sentiment_result = Mock()
    sentiment_result.text = "Hello, this is a successful test"
    sentiment_result.sentiment = "POSITIVE"
    sentiment_result.confidence = 0.85
    sentiment_result.start = 0
    sentiment_result.end = 2500
    transcript.sentiment_analysis_results = [sentiment_result]
    
    return transcript

@pytest.fixture
def mock_failed_transcript():
    """Create mock failed AssemblyAI transcript"""
    transcript = Mock()
    transcript.id = "transcript_failed_123"
    transcript.status = "error"
    transcript.text = None
    transcript.confidence = None
    transcript.error = "Audio file could not be processed due to unsupported format"
    transcript.language_code = None
    transcript.audio_url = None
    
    # No enhanced features for failed transcript
    transcript.summary = None
    transcript.language_detection_results = []
    transcript.utterances = []
    transcript.chapters = []
    transcript.content_safety_labels = None
    transcript.topics = []
    transcript.sentiment_analysis_results = []
    
    return transcript

@pytest.fixture
def mock_low_confidence_transcript():
    """Create mock transcript with low confidence"""
    transcript = Mock()
    transcript.id = "transcript_low_conf_123"
    transcript.status = "completed"
    transcript.text = "umm... this... maybe... unclear audio"
    transcript.confidence = 0.3  # Low confidence
    transcript.language_code = "en"
    transcript.audio_url = "https://api.assemblyai.com/v2/transcript/transcript_low_conf_123/audio"
    transcript.error = None
    
    # Minimal enhanced features
    transcript.summary = None
    transcript.language_detection_results = []
    transcript.utterances = []
    transcript.chapters = []
    transcript.content_safety_labels = None
    transcript.topics = []
    transcript.sentiment_analysis_results = []
    
    return transcript

@pytest.fixture
def mock_processing_transcript():
    """Create mock transcript in processing state"""
    transcript = Mock()
    transcript.id = "transcript_processing_123"
    transcript.status = "processing"  # Still processing
    transcript.text = None
    transcript.confidence = None
    transcript.error = None
    return transcript

# =============================================================================
# TEMPORARY DIRECTORY FIXTURES
# =============================================================================

@pytest.fixture
def temp_audio_dir():
    """Create temporary directory for audio files"""
    temp_dir = tempfile.mkdtemp(prefix="test_audio_")
    yield Path(temp_dir)
    
    # Cleanup
    import shutil
    try:
        shutil.rmtree(temp_dir)
    except FileNotFoundError:
        pass

@pytest.fixture
def mock_audio_processor_temp_dir(temp_audio_dir):
    """Create audio processor with custom temp directory for testing"""
    from voice_handler import AudioProcessor
    
    processor = AudioProcessor()
    processor.temp_dir = temp_audio_dir
    return processor

# =============================================================================
# PERFORMANCE TEST FIXTURES
# =============================================================================

@pytest.fixture
def performance_config():
    """Create configuration optimized for performance testing"""
    from src.handlers.voice_handler import VoiceProcessingConfig
    
    return VoiceProcessingConfig(
        assemblyai_api_key=TEST_API_KEY,
        concurrent_requests=5,  # Higher concurrency
        retry_attempts=2,       # Fewer retries for speed
        retry_delay_seconds=0.5,
        max_retry_delay=5.0,
        # Disable features that slow down testing
        enable_summarization=False,
        enable_auto_chapters=False,
        enable_content_safety=False,
        enable_topic_detection=False,
        enable_sentiment_analysis=False
    )

# =============================================================================
# MOCK ASSEMBLYAI SDK
# =============================================================================

@pytest.fixture
def mock_assemblyai_sdk():
    """Create comprehensive mock of AssemblyAI SDK"""
    mock_aai = MagicMock()
    
    # Settings
    mock_aai.settings = Mock()
    mock_aai.settings.api_key = None
    
    # Transcriber
    mock_transcriber = Mock()
    mock_aai.Transcriber.return_value = mock_transcriber
    
    # Configuration classes
    mock_aai.TranscriptionConfig = Mock()
    mock_aai.PIIRedactionPolicy = Mock()
    mock_aai.PIISubstitutionPolicy = Mock()
    
    # Enum-like behavior for PII policies
    mock_aai.PIIRedactionPolicy.person_name = "person_name"
    mock_aai.PIIRedactionPolicy.phone_number = "phone_number"
    mock_aai.PIIRedactionPolicy.email_address = "email_address"
    mock_aai.PIISubstitutionPolicy.hash = "hash"
    mock_aai.PIISubstitutionPolicy.entity_type = "entity_type"
    
    return mock_aai

# =============================================================================
# TEST RESULT FIXTURES
# =============================================================================

@pytest.fixture
def successful_transcription_result():
    """Create successful transcription result"""
    from voice_handler import VoiceTranscriptionResult, VoiceQuality
    
    return VoiceTranscriptionResult(
        text="This is a successful test transcription with high quality",
        confidence=0.95,
        quality=VoiceQuality.HIGH,
        language="en",
        duration_seconds=TEST_AUDIO_DURATION,
        processing_time_seconds=2.0,
        file_size_bytes=TEST_AUDIO_SIZE,
        format="wav",
        metadata={
            'transcript_id': 'test_123',
            'word_count': 10,
            'language_confidence': 0.98,
            'speakers': ['A'],
            'summary': 'Test summary'
        }
    )

@pytest.fixture
def failed_transcription_result():
    """Create failed transcription result"""
    from voice_handler import VoiceTranscriptionResult, VoiceQuality
    
    return VoiceTranscriptionResult(
        text="",
        confidence=0.0,
        quality=VoiceQuality.FAILED,
        language=None,
        duration_seconds=0,
        processing_time_seconds=0,
        file_size_bytes=0,
        format="unknown",
        error="authentication: Invalid API key",
        metadata={'error_type': 'AuthenticationError', 'error_category': 'authentication'}
    )

# =============================================================================
# UTILITY FIXTURES
# =============================================================================

@pytest.fixture
def capture_logs():
    """Capture logs during test execution"""
    import logging
    from io import StringIO
    
    log_capture_string = StringIO()
    ch = logging.StreamHandler(log_capture_string)
    ch.setLevel(logging.DEBUG)
    
    # Get the logger used by voice_handler
    logger = logging.getLogger('voice_handler')
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)
    
    yield log_capture_string
    
    # Cleanup
    logger.removeHandler(ch)

@pytest.fixture
def timing_context():
    """Context manager for timing test operations"""
    import time
    from contextlib import contextmanager
    
    @contextmanager
    def timer():
        start_time = time.time()
        result = {'elapsed_time': 0}
        yield result
        result['elapsed_time'] = time.time() - start_time
    
    return timer

# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers and settings"""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "performance: marks tests as performance tests") 
    config.addinivalue_line("markers", "real_api: marks tests that use real AssemblyAI API")
    config.addinivalue_line("markers", "slow: marks tests as slow running")

def pytest_collection_modifyitems(config, items):
    """Modify test collection based on environment and markers"""
    # Skip real API tests if integration testing is not enabled
    if not INTEGRATION_TEST_ENABLED:
        skip_real_api = pytest.mark.skip(reason="Real API tests disabled (set ASSEMBLYAI_INTEGRATION_TESTS=true to enable)")
        for item in items:
            if "real_api" in item.keywords:
                item.add_marker(skip_real_api)
    
    # Mark slow tests
    for item in items:
        if "performance" in item.keywords or "integration" in item.keywords:
            item.add_marker(pytest.mark.slow)

# =============================================================================
# CUSTOM ASSERTIONS
# =============================================================================

def assert_transcription_result_valid(result):
    """Assert that a transcription result is valid"""
    from voice_handler import VoiceTranscriptionResult, VoiceQuality
    
    assert isinstance(result, VoiceTranscriptionResult)
    assert isinstance(result.text, str)
    assert isinstance(result.confidence, float)
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.quality, VoiceQuality)
    assert result.duration_seconds >= 0
    assert result.processing_time_seconds >= 0
    assert result.file_size_bytes >= 0
    assert isinstance(result.format, str)

def assert_config_valid(config):
    """Assert that a voice processing config is valid"""
    from src.handlers.voice_handler import VoiceProcessingConfig
    
    assert isinstance(config, VoiceProcessingConfig)
    assert config.assemblyai_api_key
    assert config.max_file_size_mb > 0
    assert config.min_duration_seconds > 0
    assert config.max_duration_seconds > config.min_duration_seconds
    assert 0.0 <= config.confidence_threshold <= 1.0
    assert config.concurrent_requests > 0
    assert config.retry_attempts >= 0

# Export custom assertions for use in tests
pytest.assert_transcription_result_valid = assert_transcription_result_valid
pytest.assert_config_valid = assert_config_valid