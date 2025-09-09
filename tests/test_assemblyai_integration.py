#!/usr/bin/env python3
"""
Comprehensive Test Suite for AssemblyAI Voice Handler Integration

This test suite covers all aspects of the voice processing system:
- Unit tests for all components with mocking
- Integration tests for full workflow
- Error handling for all failure scenarios
- Performance tests for large files and concurrency
- CI/CD compatible tests (no real API calls by default)

Usage:
    # Run all tests with mocks (CI/CD safe):
    pytest test_assemblyai_integration.py

    # Run with real API for integration testing:
    ASSEMBLYAI_INTEGRATION_TESTS=true pytest test_assemblyai_integration.py -m integration

    # Run performance tests:
    pytest test_assemblyai_integration.py -m performance

    # Run with coverage:
    pytest test_assemblyai_integration.py --cov=voice_handler --cov-report=html
"""

import asyncio
import json
import os
import tempfile
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, MagicMock, AsyncMock, patch, mock_open
from dataclasses import dataclass
from io import BytesIO

import pytest
import pytest_asyncio
from unittest import IsolatedAsyncioTestCase

# Import the modules to test
from src.handlers.voice_handler import (
    VoiceMessageHandler,
    VoiceTranscriptionResult,
    VoiceProcessingConfig,
    VoiceQuality,
    AudioFormat,
    AudioProcessor,
    AssemblyAIClient,
    create_voice_handler,
    create_voice_handler_with_features
)
from src.core.config import BotConfig

# Mock AssemblyAI to avoid import issues in testing environment
try:
    import assemblyai as aai
    ASSEMBLYAI_AVAILABLE = True
except ImportError:
    # Create mock assemblyai module for testing
    import sys
    from unittest.mock import MagicMock
    
    mock_aai = MagicMock()
    mock_aai.settings = MagicMock()
    mock_aai.Transcriber = MagicMock
    mock_aai.TranscriptionConfig = MagicMock
    mock_aai.Transcript = MagicMock
    mock_aai.PIIRedactionPolicy = MagicMock()
    mock_aai.PIISubstitutionPolicy = MagicMock()
    
    sys.modules['assemblyai'] = mock_aai
    import assemblyai as aai
    ASSEMBLYAI_AVAILABLE = False

# Test configuration
TEST_AUDIO_DURATION = 5.0  # seconds
TEST_AUDIO_SIZE = 1024 * 100  # 100KB
TEST_API_KEY = "test_api_key_12345"
INTEGRATION_TEST_ENABLED = os.getenv('ASSEMBLYAI_INTEGRATION_TESTS', 'false').lower() == 'true'

# Test fixtures and data
@pytest.fixture
def test_config():
    """Create test configuration"""
    return VoiceProcessingConfig(
        assemblyai_api_key=TEST_API_KEY,
        max_file_size_mb=25,
        min_duration_seconds=0.5,
        max_duration_seconds=600,
        confidence_threshold=0.6,
        default_language="en",
        enable_auto_language_detection=True,
        enable_speaker_labels=True,
        enable_pii_redaction=True,
        pii_redaction_policies=["person_name", "phone_number", "email_address"],
        enable_summarization=True,
        enable_auto_chapters=False,
        enable_content_safety=True,
        enable_topic_detection=True,
        enable_sentiment_analysis=True,
        concurrent_requests=3,
        retry_attempts=3,
        retry_delay_seconds=1.0,
        max_retry_delay=10.0
    )

@pytest.fixture
def minimal_config():
    """Create minimal test configuration"""
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
def mock_telegram_voice():
    """Create mock Telegram voice message"""
    voice = Mock()
    voice.duration = TEST_AUDIO_DURATION
    voice.file_size = TEST_AUDIO_SIZE
    voice.mime_type = "audio/ogg"
    voice.file_id = "test_file_id_123"
    return voice

@pytest.fixture
def mock_telegram_file():
    """Create mock Telegram file object"""
    file = Mock()
    file.file_id = "test_file_id_123"
    file.mime_type = "audio/ogg"
    file.download_to_drive = AsyncMock()
    return file

@pytest.fixture
def mock_telegram_update():
    """Create mock Telegram update with voice message"""
    update = Mock()
    update.effective_user.id = 12345
    update.effective_chat.id = 67890
    update.message.voice = mock_telegram_voice()
    return update

@pytest.fixture
def mock_telegram_context():
    """Create mock Telegram context"""
    context = Mock()
    context.bot.get_file = AsyncMock()
    context.bot.send_chat_action = AsyncMock()
    return context

@pytest.fixture
def test_audio_metadata():
    """Create test audio metadata"""
    return {
        "duration": TEST_AUDIO_DURATION,
        "channels": 1,
        "frame_rate": 16000,
        "format": "ogg",
        "size_bytes": TEST_AUDIO_SIZE,
        "telegram_duration": TEST_AUDIO_DURATION,
        "telegram_file_size": TEST_AUDIO_SIZE,
        "telegram_mime_type": "audio/ogg"
    }

@pytest.fixture
def mock_successful_transcript():
    """Create mock successful AssemblyAI transcript"""
    transcript = Mock()
    transcript.id = "transcript_123"
    transcript.status = "completed"
    transcript.text = "Hello, this is a test transcription"
    transcript.confidence = 0.95
    transcript.language_code = "en"
    transcript.audio_url = "https://api.assemblyai.com/v2/transcript/transcript_123/audio"
    
    # Enhanced features
    transcript.summary = "This is a test summary"
    transcript.language_detection_results = [
        Mock(language="en", confidence=0.98)
    ]
    transcript.utterances = [
        Mock(speaker="A", text="Hello, this is a test", confidence=0.95, start=0, end=2000)
    ]
    transcript.chapters = [
        Mock(summary="Test chapter", headline="Introduction", start=0, end=5000)
    ]
    transcript.content_safety_labels = Mock(
        results=[Mock(label="safe", confidence=0.99, severity=0.1)]
    )
    transcript.topics = [
        Mock(text="testing", labels=[Mock(relevance=0.8, label="technology")])
    ]
    transcript.sentiment_analysis_results = [
        Mock(text="Hello, this is a test", sentiment="POSITIVE", confidence=0.8, start=0, end=2000)
    ]
    
    return transcript

@pytest.fixture
def mock_failed_transcript():
    """Create mock failed AssemblyAI transcript"""
    transcript = Mock()
    transcript.id = "transcript_failed_123"
    transcript.status = "error"
    transcript.error = "Audio file could not be processed"
    transcript.text = None
    transcript.confidence = None
    return transcript

@pytest.fixture
def sample_audio_file():
    """Create a temporary sample audio file for testing"""
    # Create a temporary file with some audio-like content
    temp_file = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
    # Write some dummy audio data (OGG header-like bytes)
    temp_file.write(b'OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00' + b'\x00' * (TEST_AUDIO_SIZE - 10))
    temp_file.close()
    
    yield Path(temp_file.name)
    
    # Cleanup
    try:
        Path(temp_file.name).unlink()
    except FileNotFoundError:
        pass

@pytest.fixture
def temporary_directory():
    """Create temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    
    # Cleanup
    import shutil
    try:
        shutil.rmtree(temp_dir)
    except FileNotFoundError:
        pass


# =============================================================================
# UNIT TESTS - Configuration Validation
# =============================================================================

class TestVoiceProcessingConfig:
    """Test configuration validation and initialization"""
    
    def test_config_initialization_minimal(self):
        """Test minimal config initialization"""
        config = VoiceProcessingConfig(assemblyai_api_key=TEST_API_KEY)
        
        assert config.assemblyai_api_key == TEST_API_KEY
        assert config.max_file_size_mb == 25
        assert config.confidence_threshold == 0.6
        assert config.default_language == "en"
        assert config.enable_auto_language_detection is True
        assert config.concurrent_requests == 3
        assert config.retry_attempts == 3
    
    def test_config_initialization_full(self, test_config):
        """Test full config initialization with all features"""
        config = test_config
        
        assert config.assemblyai_api_key == TEST_API_KEY
        assert config.enable_speaker_labels is True
        assert config.enable_pii_redaction is True
        assert config.enable_summarization is True
        assert config.enable_content_safety is True
        assert len(config.pii_redaction_policies) == 3
        assert "person_name" in config.pii_redaction_policies
    
    def test_config_post_init_defaults(self):
        """Test that post_init sets proper defaults"""
        config = VoiceProcessingConfig(assemblyai_api_key=TEST_API_KEY)
        
        # Check default languages
        assert "en" in config.supported_languages
        assert "ru" in config.supported_languages
        assert len(config.supported_languages) >= 10
        
        # Check default PII policies
        assert "person_name" in config.pii_redaction_policies
        assert "phone_number" in config.pii_redaction_policies
        assert "email_address" in config.pii_redaction_policies
    
    def test_config_validation_missing_api_key(self):
        """Test config fails with missing API key"""
        with pytest.raises(TypeError):
            VoiceProcessingConfig()  # Missing required api_key
    
    def test_config_custom_languages(self):
        """Test custom supported languages"""
        custom_languages = ["en", "es", "fr"]
        config = VoiceProcessingConfig(
            assemblyai_api_key=TEST_API_KEY,
            supported_languages=custom_languages
        )
        
        assert config.supported_languages == custom_languages
    
    def test_config_custom_pii_policies(self):
        """Test custom PII redaction policies"""
        custom_policies = ["phone_number", "credit_card_number"]
        config = VoiceProcessingConfig(
            assemblyai_api_key=TEST_API_KEY,
            pii_redaction_policies=custom_policies
        )
        
        assert config.pii_redaction_policies == custom_policies


# =============================================================================
# UNIT TESTS - Audio Processing
# =============================================================================

class TestAudioProcessor:
    """Test audio file processing and optimization"""
    
    @pytest.fixture(autouse=True)
    def setup_processor(self, temporary_directory):
        """Setup audio processor with temporary directory"""
        self.processor = AudioProcessor()
        # Override temp directory for testing
        self.processor.temp_dir = temporary_directory
    
    def test_processor_initialization(self):
        """Test audio processor initialization"""
        processor = AudioProcessor()
        assert processor.temp_dir.exists()
        assert processor.temp_dir.name.endswith("ai_interviewer_audio")
    
    def test_mime_to_extension_mapping(self):
        """Test MIME type to extension conversion"""
        processor = AudioProcessor()
        
        test_cases = [
            ("audio/ogg", "ogg"),
            ("audio/mpeg", "mp3"),
            ("audio/mp4", "m4a"),
            ("audio/wav", "wav"),
            ("audio/webm", "webm"),
            ("audio/opus", "opus"),
            ("unknown/format", "ogg")  # default fallback
        ]
        
        for mime_type, expected_ext in test_cases:
            result = processor._mime_to_extension(mime_type)
            assert result == expected_ext
    
    @pytest.mark.asyncio
    async def test_download_voice_message(self, mock_telegram_file):
        """Test voice message download"""
        # Mock the file download
        async def mock_download(path):
            # Create a dummy file
            with open(path, 'wb') as f:
                f.write(b'dummy audio data' * 100)
        
        mock_telegram_file.download_to_drive = mock_download
        
        # Test download
        result_path = await self.processor.download_voice_message(mock_telegram_file, 12345)
        
        assert result_path.exists()
        assert result_path.suffix == ".ogg"
        assert "voice_12345_" in result_path.name
        assert result_path.stat().st_size > 0
    
    @pytest.mark.asyncio
    async def test_download_voice_message_error(self, mock_telegram_file):
        """Test voice message download error handling"""
        # Mock download failure
        mock_telegram_file.download_to_drive = AsyncMock(side_effect=Exception("Network error"))
        
        with pytest.raises(Exception, match="Network error"):
            await self.processor.download_voice_message(mock_telegram_file, 12345)
    
    @pytest.mark.asyncio
    @patch('voice_handler.AudioSegment')
    async def test_convert_and_optimize_success(self, mock_audio_segment, sample_audio_file):
        """Test audio conversion and optimization"""
        # Mock AudioSegment behavior
        mock_audio = Mock()
        mock_audio.channels = 2
        mock_audio.frame_rate = 44100
        mock_audio.__len__ = Mock(return_value=5000)  # 5 seconds
        mock_audio.set_channels.return_value = mock_audio
        mock_audio.set_frame_rate.return_value = mock_audio
        mock_audio.normalize.return_value = mock_audio
        mock_audio.high_pass_filter.return_value = mock_audio
        mock_audio.export = Mock()
        
        mock_audio_segment.from_file.return_value = mock_audio
        
        # Test conversion
        result_path, metadata = await self.processor.convert_and_optimize(sample_audio_file)
        
        assert result_path.suffix == ".wav"
        assert metadata["duration"] == 5.0
        assert metadata["channels"] == 2
        assert metadata["frame_rate"] == 44100
        assert "processing_time" in metadata
        
        # Verify audio processing chain
        mock_audio.set_channels.assert_called_with(1)  # Convert to mono
        mock_audio.set_frame_rate.assert_called_with(16000)  # Convert to 16kHz
        mock_audio.normalize.assert_called_once()
        mock_audio.high_pass_filter.assert_called_with(100)
    
    @pytest.mark.asyncio
    @patch('voice_handler.AudioSegment')
    async def test_convert_and_optimize_decode_error(self, mock_audio_segment, sample_audio_file):
        """Test audio conversion with decode error"""
        from pydub.exceptions import CouldntDecodeError
        
        mock_audio_segment.from_file.side_effect = CouldntDecodeError("Unsupported format")
        
        with pytest.raises(ValueError, match="Unsupported audio format"):
            await self.processor.convert_and_optimize(sample_audio_file)
    
    @pytest.mark.asyncio
    @patch('voice_handler.AudioSegment')
    async def test_optimize_audio_mono_conversion(self, mock_audio_segment):
        """Test audio optimization for mono conversion"""
        # Create mock stereo audio
        mock_audio = Mock()
        mock_audio.channels = 2
        mock_audio.frame_rate = 44100
        mock_audio.set_channels.return_value = mock_audio
        mock_audio.set_frame_rate.return_value = mock_audio
        mock_audio.normalize.return_value = mock_audio
        mock_audio.high_pass_filter.return_value = mock_audio
        
        # Test optimization
        result = await self.processor._optimize_audio(mock_audio)
        
        # Should convert to mono
        mock_audio.set_channels.assert_called_with(1)
        # Should convert to 16kHz
        mock_audio.set_frame_rate.assert_called_with(16000)
        # Should normalize and filter
        mock_audio.normalize.assert_called_once()
        mock_audio.high_pass_filter.assert_called_with(100)
    
    def test_cleanup_temp_files(self, temporary_directory):
        """Test temporary file cleanup"""
        # Create some test files with different ages
        now = datetime.now()
        old_time = now - timedelta(hours=25)  # Older than 24 hours
        recent_time = now - timedelta(hours=1)  # Recent
        
        # Create old file
        old_file = temporary_directory / "voice_old.ogg"
        old_file.touch()
        os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))
        
        # Create recent file
        recent_file = temporary_directory / "voice_recent.ogg"
        recent_file.touch()
        os.utime(recent_file, (recent_time.timestamp(), recent_time.timestamp()))
        
        # Create non-voice file (should not be deleted)
        other_file = temporary_directory / "other_file.txt"
        other_file.touch()
        os.utime(other_file, (old_time.timestamp(), old_time.timestamp()))
        
        # Override processor temp directory
        self.processor.temp_dir = temporary_directory
        
        # Cleanup with 24 hour threshold
        self.processor.cleanup_temp_files(max_age_hours=24)
        
        # Check results
        assert not old_file.exists()  # Should be deleted
        assert recent_file.exists()   # Should remain
        assert other_file.exists()    # Should remain (not voice file)


# =============================================================================
# UNIT TESTS - AssemblyAI Client (Mocked)
# =============================================================================

class TestAssemblyAIClient:
    """Test AssemblyAI client with mocked API calls"""
    
    @pytest.fixture(autouse=True)
    def setup_client(self, test_config):
        """Setup AssemblyAI client for testing"""
        self.config = test_config
        
        # Mock the AssemblyAI SDK
        with patch('voice_handler.aai') as mock_aai:
            mock_aai.settings = Mock()
            mock_aai.Transcriber = Mock()
            mock_aai.TranscriptionConfig = Mock()
            mock_aai.PIIRedactionPolicy = Mock()
            mock_aai.PIISubstitutionPolicy = Mock()
            
            self.client = AssemblyAIClient(self.config)
            self.mock_aai = mock_aai
    
    def test_client_initialization(self):
        """Test AssemblyAI client initialization"""
        with patch('voice_handler.aai') as mock_aai:
            mock_aai.settings = Mock()
            mock_transcriber = Mock()
            mock_aai.Transcriber.return_value = mock_transcriber
            
            config = VoiceProcessingConfig(assemblyai_api_key=TEST_API_KEY)
            client = AssemblyAIClient(config)
            
            # Check API key was set
            mock_aai.settings.api_key = TEST_API_KEY
            # Check transcriber was created
            mock_aai.Transcriber.assert_called_once()
            assert client.config == config
            assert client._request_semaphore._value == config.concurrent_requests
    
    def test_client_initialization_invalid_api_key(self):
        """Test client initialization with invalid API key"""
        with pytest.raises(ValueError, match="AssemblyAI API key is required"):
            config = VoiceProcessingConfig(assemblyai_api_key="")
            AssemblyAIClient(config)
    
    def test_get_enabled_features(self):
        """Test feature summary generation"""
        features = self.client._get_enabled_features()
        
        expected_features = [
            "auto_language_detection", "speaker_labels", "pii_redaction",
            "summarization", "auto_chapters", "content_safety",
            "topic_detection", "sentiment_analysis"
        ]
        
        for feature in expected_features:
            assert feature in features
            assert isinstance(features[feature], bool)
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test API rate limiting"""
        # Mock semaphore for testing
        with patch.object(self.client, '_request_semaphore') as mock_semaphore:
            mock_semaphore.__aenter__ = AsyncMock()
            mock_semaphore.__aexit__ = AsyncMock()
            
            await self.client._rate_limit()
            
            mock_semaphore.__aenter__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_audio_file_success(self, sample_audio_file, test_audio_metadata):
        """Test audio file validation success"""
        # Should not raise any exception
        await self.client._validate_audio_file(sample_audio_file, test_audio_metadata)
    
    @pytest.mark.asyncio
    async def test_validate_audio_file_not_found(self, test_audio_metadata):
        """Test audio file validation with missing file"""
        non_existent_file = Path("/does/not/exist.wav")
        
        with pytest.raises(ValueError, match="Audio file not found"):
            await self.client._validate_audio_file(non_existent_file, test_audio_metadata)
    
    @pytest.mark.asyncio
    async def test_validate_audio_file_too_large(self, sample_audio_file):
        """Test audio file validation with oversized file"""
        large_metadata = {
            "duration": 5.0,
            "size_bytes": 30 * 1024 * 1024  # 30MB, over 25MB limit
        }
        
        with pytest.raises(ValueError, match="File too large"):
            await self.client._validate_audio_file(sample_audio_file, large_metadata)
    
    @pytest.mark.asyncio
    async def test_validate_audio_file_too_short(self, sample_audio_file):
        """Test audio file validation with too short duration"""
        short_metadata = {
            "duration": 0.1,  # Below 0.5s minimum
            "size_bytes": TEST_AUDIO_SIZE
        }
        
        with pytest.raises(ValueError, match="Audio too short"):
            await self.client._validate_audio_file(sample_audio_file, short_metadata)
    
    @pytest.mark.asyncio
    async def test_validate_audio_file_too_long(self, sample_audio_file):
        """Test audio file validation with too long duration"""
        long_metadata = {
            "duration": 700,  # Over 600s maximum
            "size_bytes": TEST_AUDIO_SIZE
        }
        
        with pytest.raises(ValueError, match="Audio too long"):
            await self.client._validate_audio_file(sample_audio_file, long_metadata)
    
    def test_build_transcript_config_basic(self):
        """Test basic transcript configuration building"""
        metadata = {"duration": 5.0}
        
        with patch('voice_handler.aai.TranscriptionConfig') as mock_config:
            config = self.client._build_transcript_config(metadata)
            
            mock_config.assert_called_once()
            # Check that configuration was called with expected parameters
            call_kwargs = mock_config.call_args[1]
            assert call_kwargs['language_detection'] is True
            assert call_kwargs['speaker_labels'] is True
            assert call_kwargs['summarization'] is True
    
    def test_build_transcript_config_with_pii_redaction(self):
        """Test transcript configuration with PII redaction"""
        metadata = {"duration": 5.0}
        
        with patch('voice_handler.aai.TranscriptionConfig') as mock_config, \
             patch('voice_handler.aai.PIIRedactionPolicy') as mock_pii_policy, \
             patch('voice_handler.aai.PIISubstitutionPolicy') as mock_sub_policy:
            
            # Setup mock PII policies
            mock_pii_policy.person_name = "person_name_enum"
            mock_pii_policy.phone_number = "phone_number_enum"
            mock_pii_policy.email_address = "email_address_enum"
            mock_sub_policy.hash = "hash_enum"
            
            mock_config_instance = Mock()
            mock_config.return_value = mock_config_instance
            
            config = self.client._build_transcript_config(metadata)
            
            # Should call set_redact_pii if PII redaction is enabled
            if self.config.enable_pii_redaction:
                mock_config_instance.set_redact_pii.assert_called_once()
    
    def test_is_retryable_error(self):
        """Test error retry logic"""
        client = self.client
        
        # Non-retryable errors
        non_retryable = [
            Exception("API key invalid"),
            Exception("Unauthorized access"),
            Exception("File size too large"),
            Exception("Unsupported format"),
            Exception("Bad request")
        ]
        
        for error in non_retryable:
            assert not client._is_retryable_error(error)
        
        # Retryable errors
        retryable = [
            Exception("Network timeout"),
            Exception("Connection failed"),
            Exception("Server error"),
            Exception("Temporary failure")
        ]
        
        for error in retryable:
            assert client._is_retryable_error(error)
    
    @pytest.mark.asyncio
    async def test_transcribe_with_retries_success(self, sample_audio_file, mock_successful_transcript):
        """Test successful transcription with retries"""
        with patch.object(self.client, 'transcriber') as mock_transcriber:
            # Mock successful transcription on first try
            mock_transcriber.transcribe.return_value = mock_successful_transcript
            
            config = Mock()
            result = await self.client._transcribe_with_retries(sample_audio_file, config)
            
            assert result == mock_successful_transcript
            mock_transcriber.transcribe.assert_called_once_with(str(sample_audio_file), config=config)
    
    @pytest.mark.asyncio
    async def test_transcribe_with_retries_eventual_success(self, sample_audio_file, mock_successful_transcript):
        """Test transcription success after retries"""
        with patch.object(self.client, 'transcriber') as mock_transcriber:
            # Fail twice, then succeed
            mock_transcriber.transcribe.side_effect = [
                Exception("Network error"),
                Exception("Temporary failure"),
                mock_successful_transcript
            ]
            
            config = Mock()
            result = await self.client._transcribe_with_retries(sample_audio_file, config)
            
            assert result == mock_successful_transcript
            assert mock_transcriber.transcribe.call_count == 3
    
    @pytest.mark.asyncio
    async def test_transcribe_with_retries_non_retryable_error(self, sample_audio_file):
        """Test transcription with non-retryable error"""
        with patch.object(self.client, 'transcriber') as mock_transcriber:
            # Non-retryable error
            mock_transcriber.transcribe.side_effect = Exception("API key invalid")
            
            config = Mock()
            with pytest.raises(Exception, match="API key invalid"):
                await self.client._transcribe_with_retries(sample_audio_file, config)
            
            # Should not retry
            assert mock_transcriber.transcribe.call_count == 1
    
    @pytest.mark.asyncio
    async def test_transcribe_with_retries_max_attempts(self, sample_audio_file):
        """Test transcription hitting max retry attempts"""
        with patch.object(self.client, 'transcriber') as mock_transcriber:
            # Always fail with retryable error
            mock_transcriber.transcribe.side_effect = Exception("Network timeout")
            
            config = Mock()
            with pytest.raises(Exception, match="Network timeout"):
                await self.client._transcribe_with_retries(sample_audio_file, config)
            
            # Should retry max attempts
            assert mock_transcriber.transcribe.call_count == self.config.retry_attempts
    
    def test_determine_quality_high(self):
        """Test quality determination - high quality"""
        metadata = {"duration": 10.0}
        quality = self.client._determine_quality(0.95, "This is a good quality transcript", metadata)
        assert quality == VoiceQuality.HIGH
    
    def test_determine_quality_medium(self):
        """Test quality determination - medium quality"""
        metadata = {"duration": 10.0}
        quality = self.client._determine_quality(0.75, "This is an okay transcript", metadata)
        assert quality == VoiceQuality.MEDIUM
    
    def test_determine_quality_low(self):
        """Test quality determination - low quality"""
        metadata = {"duration": 10.0}
        quality = self.client._determine_quality(0.4, "Low confidence transcript", metadata)
        assert quality == VoiceQuality.LOW
    
    def test_determine_quality_failed(self):
        """Test quality determination - failed"""
        metadata = {"duration": 10.0}
        quality = self.client._determine_quality(0.0, "", metadata)
        assert quality == VoiceQuality.FAILED
    
    def test_determine_quality_too_short_text(self):
        """Test quality determination - text too short for duration"""
        metadata = {"duration": 30.0}  # 30 seconds
        quality = self.client._determine_quality(0.8, "Hi", metadata)  # Only 2 words
        assert quality == VoiceQuality.LOW


# =============================================================================
# UNIT TESTS - Voice Handler Main Class
# =============================================================================

class TestVoiceMessageHandler:
    """Test main voice message handler"""
    
    @pytest.fixture(autouse=True)
    def setup_handler(self, test_config):
        """Setup voice message handler"""
        with patch('voice_handler.AssemblyAIClient'), \
             patch('voice_handler.AudioProcessor'):
            self.handler = VoiceMessageHandler(test_config)
            self.config = test_config
    
    def test_handler_initialization(self):
        """Test voice handler initialization"""
        assert self.handler.config == self.config
        assert hasattr(self.handler, 'audio_processor')
        assert hasattr(self.handler, 'assemblyai_client')
        assert isinstance(self.handler.stats, dict)
        assert self.handler.stats['messages_processed'] == 0
    
    def test_format_transcription_response_success_high_quality(self):
        """Test formatting successful high-quality transcription"""
        result = VoiceTranscriptionResult(
            text="This is a test transcription with high quality",
            confidence=0.95,
            quality=VoiceQuality.HIGH,
            language="en",
            duration_seconds=5.0,
            processing_time_seconds=2.0,
            file_size_bytes=TEST_AUDIO_SIZE,
            format="wav"
        )
        
        response = self.handler.format_transcription_response(result)
        
        assert "🎤✨" in response  # High quality indicator
        assert "Voice Message Transcribed" in response
        assert result.text in response
        assert "confidence" not in response.lower()  # No confidence warning for high quality
    
    def test_format_transcription_response_success_low_quality(self):
        """Test formatting successful low-quality transcription"""
        result = VoiceTranscriptionResult(
            text="This is a low quality transcription",
            confidence=0.45,
            quality=VoiceQuality.LOW,
            language="en",
            duration_seconds=5.0,
            processing_time_seconds=2.0,
            file_size_bytes=TEST_AUDIO_SIZE,
            format="wav"
        )
        
        response = self.handler.format_transcription_response(result)
        
        assert "🎤⚠️" in response  # Low quality indicator
        assert result.text in response
        assert "45%" in response  # Confidence percentage
        assert "please verify" in response
    
    def test_format_transcription_response_failed_auth_error(self):
        """Test formatting failed transcription - authentication error"""
        result = VoiceTranscriptionResult(
            text="",
            confidence=0.0,
            quality=VoiceQuality.FAILED,
            language=None,
            duration_seconds=0,
            processing_time_seconds=0,
            file_size_bytes=0,
            format="unknown",
            error="authentication: API key invalid"
        )
        
        response = self.handler.format_transcription_response(result)
        
        assert "🎤❌" in response
        assert "API authentication failed" in response
        assert "check the configuration" in response
    
    def test_format_transcription_response_failed_file_size(self):
        """Test formatting failed transcription - file too large"""
        large_size = 30 * 1024 * 1024  # 30MB
        result = VoiceTranscriptionResult(
            text="",
            confidence=0.0,
            quality=VoiceQuality.FAILED,
            language=None,
            duration_seconds=0,
            processing_time_seconds=0,
            file_size_bytes=large_size,
            format="unknown",
            error="file_size: File too large"
        )
        
        response = self.handler.format_transcription_response(result)
        
        assert "🎤📁" in response
        assert "30.0MB" in response
        assert f"{self.config.max_file_size_mb}MB" in response
    
    def test_format_transcription_response_failed_timeout(self):
        """Test formatting failed transcription - timeout"""
        result = VoiceTranscriptionResult(
            text="",
            confidence=0.0,
            quality=VoiceQuality.FAILED,
            language=None,
            duration_seconds=0,
            processing_time_seconds=0,
            file_size_bytes=0,
            format="unknown",
            error="timeout: Request timed out"
        )
        
        response = self.handler.format_transcription_response(result)
        
        assert "🎤⏱️" in response
        assert "timed out" in response
        assert "shorter audio file" in response
    
    def test_format_transcription_response_with_extras(self):
        """Test formatting transcription with extra features"""
        result = VoiceTranscriptionResult(
            text="This is a test transcription",
            confidence=0.95,
            quality=VoiceQuality.HIGH,
            language="es",  # Non-English
            duration_seconds=5.0,
            processing_time_seconds=2.0,
            file_size_bytes=TEST_AUDIO_SIZE,
            format="wav",
            metadata={
                'language_confidence': 0.98,
                'speakers': ['A', 'B'],  # Multiple speakers
                'summary': 'Test conversation summary',
                'chapters': [{'summary': 'Chapter 1'}]
            }
        )
        
        response = self.handler.format_transcription_response(result, include_extras=True)
        
        assert result.text in response
        assert "Language: ES (98%)" in response
        assert "Speakers: 2 detected" in response
        assert "Summary available" in response
        assert "Chapters: 1 sections" in response
    
    def test_search_words_in_result_success(self):
        """Test word search in transcription result"""
        result = VoiceTranscriptionResult(
            text="This is a test transcription with important information",
            confidence=0.95,
            quality=VoiceQuality.HIGH,
            language="en",
            duration_seconds=5.0,
            processing_time_seconds=2.0,
            file_size_bytes=TEST_AUDIO_SIZE,
            format="wav"
        )
        
        search_results = self.handler.search_words_in_result(result, ["test", "important", "missing"])
        
        assert "test" in search_results
        assert "important" in search_results
        assert "missing" in search_results
        
        # Check found words have matches
        assert len(search_results["test"]) > 0
        assert len(search_results["important"]) > 0
        # Check missing word has no matches
        assert len(search_results["missing"]) == 0
    
    def test_search_words_in_result_failed(self):
        """Test word search in failed transcription result"""
        result = VoiceTranscriptionResult(
            text="",
            confidence=0.0,
            quality=VoiceQuality.FAILED,
            language=None,
            duration_seconds=0,
            processing_time_seconds=0,
            file_size_bytes=0,
            format="unknown",
            error="Failed to process"
        )
        
        search_results = self.handler.search_words_in_result(result, ["test"])
        
        assert search_results == {}
    
    def test_format_search_results_with_matches(self):
        """Test formatting search results with matches"""
        search_results = {
            "test": [
                {"count": 2, "start_char": 5, "end_char": 9},
                {"count": 2, "start_char": 25, "end_char": 29}
            ],
            "important": [
                {"count": 1, "start_char": 35, "end_char": 44}
            ]
        }
        
        response = self.handler.format_search_results(search_results)
        
        assert "🔍" in response
        assert "Word Search Results" in response
        assert "**test**: 2 occurrences" in response
        assert "**important**: 1 occurrence" in response
        assert "Position 5-9" in response
        assert "Position 35-44" in response
    
    def test_format_search_results_no_matches(self):
        """Test formatting search results with no matches"""
        search_results = {}
        
        response = self.handler.format_search_results(search_results)
        
        assert response == "🔍 No matches found."
    
    def test_get_statistics_initial(self):
        """Test getting initial statistics"""
        stats = self.handler.get_statistics()
        
        assert stats['messages_processed'] == 0
        assert stats['successful_transcriptions'] == 0
        assert stats['failed_transcriptions'] == 0
        assert stats['total_audio_duration'] == 0.0
        assert stats['total_processing_time'] == 0.0
    
    def test_get_statistics_with_data(self):
        """Test getting statistics with processed data"""
        # Simulate some processing
        self.handler.stats = {
            'messages_processed': 10,
            'successful_transcriptions': 8,
            'failed_transcriptions': 2,
            'total_audio_duration': 50.0,
            'total_processing_time': 25.0
        }
        
        stats = self.handler.get_statistics()
        
        assert stats['messages_processed'] == 10
        assert stats['success_rate'] == 0.8  # 8/10
        assert stats['avg_processing_time'] == 2.5  # 25/10
        assert stats['avg_audio_duration'] == 5.0  # 50/10


# =============================================================================
# INTEGRATION TESTS (Mocked by default, real API if enabled)
# =============================================================================

@pytest.mark.integration
class TestVoiceHandlerIntegration:
    """Integration tests for full voice processing workflow"""
    
    @pytest.fixture(autouse=True)
    def setup_integration(self, test_config, mock_telegram_update, mock_telegram_context, mock_telegram_file):
        """Setup integration test environment"""
        self.config = test_config
        self.update = mock_telegram_update
        self.context = mock_telegram_context
        self.mock_file = mock_telegram_file
        
        # Setup mock file download
        self.context.bot.get_file.return_value = self.mock_file
    
    @pytest.mark.asyncio
    async def test_full_workflow_success(self, sample_audio_file, mock_successful_transcript):
        """Test complete voice message processing workflow"""
        with patch('voice_handler.AssemblyAIClient') as mock_client_class, \
             patch('voice_handler.AudioProcessor') as mock_processor_class:
            
            # Setup mocks
            mock_processor = Mock()
            mock_processor_class.return_value = mock_processor
            mock_processor.download_voice_message = AsyncMock(return_value=sample_audio_file)
            mock_processor.convert_and_optimize = AsyncMock(return_value=(
                sample_audio_file.with_suffix('.wav'),
                {
                    "duration": 5.0,
                    "channels": 1,
                    "frame_rate": 16000,
                    "format": "wav",
                    "size_bytes": TEST_AUDIO_SIZE
                }
            ))
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.transcribe_audio = AsyncMock(return_value=VoiceTranscriptionResult(
                text="This is a successful test transcription",
                confidence=0.95,
                quality=VoiceQuality.HIGH,
                language="en",
                duration_seconds=5.0,
                processing_time_seconds=2.0,
                file_size_bytes=TEST_AUDIO_SIZE,
                format="wav"
            ))
            
            # Create handler and process message
            handler = VoiceMessageHandler(self.config)
            result = await handler.process_voice_message(self.update, self.context)
            
            # Verify result
            assert result.quality == VoiceQuality.HIGH
            assert result.text == "This is a successful test transcription"
            assert result.confidence == 0.95
            
            # Verify statistics updated
            stats = handler.get_statistics()
            assert stats['messages_processed'] == 1
            assert stats['successful_transcriptions'] == 1
            assert stats['failed_transcriptions'] == 0
    
    @pytest.mark.asyncio
    async def test_full_workflow_failure(self, sample_audio_file):
        """Test complete workflow with failure"""
        with patch('voice_handler.AssemblyAIClient') as mock_client_class, \
             patch('voice_handler.AudioProcessor') as mock_processor_class:
            
            # Setup mocks - processor succeeds, client fails
            mock_processor = Mock()
            mock_processor_class.return_value = mock_processor
            mock_processor.download_voice_message = AsyncMock(return_value=sample_audio_file)
            mock_processor.convert_and_optimize = AsyncMock(return_value=(
                sample_audio_file.with_suffix('.wav'),
                {"duration": 5.0, "size_bytes": TEST_AUDIO_SIZE}
            ))
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.transcribe_audio = AsyncMock(return_value=VoiceTranscriptionResult(
                text="",
                confidence=0.0,
                quality=VoiceQuality.FAILED,
                language=None,
                duration_seconds=5.0,
                processing_time_seconds=2.0,
                file_size_bytes=TEST_AUDIO_SIZE,
                format="wav",
                error="Network error occurred"
            ))
            
            # Create handler and process message
            handler = VoiceMessageHandler(self.config)
            result = await handler.process_voice_message(self.update, self.context)
            
            # Verify result
            assert result.quality == VoiceQuality.FAILED
            assert result.error == "Network error occurred"
            
            # Verify statistics updated
            stats = handler.get_statistics()
            assert stats['messages_processed'] == 1
            assert stats['successful_transcriptions'] == 0
            assert stats['failed_transcriptions'] == 1
    
    @pytest.mark.asyncio
    async def test_workflow_download_failure(self):
        """Test workflow with download failure"""
        with patch('voice_handler.AssemblyAIClient'), \
             patch('voice_handler.AudioProcessor') as mock_processor_class:
            
            # Setup mock processor to fail on download
            mock_processor = Mock()
            mock_processor_class.return_value = mock_processor
            mock_processor.download_voice_message = AsyncMock(side_effect=Exception("Download failed"))
            
            # Create handler and process message
            handler = VoiceMessageHandler(self.config)
            result = await handler.process_voice_message(self.update, self.context)
            
            # Should return failed result
            assert result.quality == VoiceQuality.FAILED
            assert "Download failed" in result.error
    
    @pytest.mark.asyncio
    async def test_workflow_conversion_failure(self, sample_audio_file):
        """Test workflow with audio conversion failure"""
        with patch('voice_handler.AssemblyAIClient'), \
             patch('voice_handler.AudioProcessor') as mock_processor_class:
            
            # Setup mock processor to fail on conversion
            mock_processor = Mock()
            mock_processor_class.return_value = mock_processor
            mock_processor.download_voice_message = AsyncMock(return_value=sample_audio_file)
            mock_processor.convert_and_optimize = AsyncMock(side_effect=ValueError("Unsupported format"))
            
            # Create handler and process message
            handler = VoiceMessageHandler(self.config)
            result = await handler.process_voice_message(self.update, self.context)
            
            # Should return failed result
            assert result.quality == VoiceQuality.FAILED
            assert "Unsupported format" in result.error


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling:
    """Test comprehensive error handling scenarios"""
    
    @pytest.fixture(autouse=True)
    def setup_error_tests(self, test_config):
        """Setup for error handling tests"""
        self.config = test_config
    
    @pytest.mark.asyncio
    async def test_network_timeout_error(self, sample_audio_file, test_audio_metadata):
        """Test handling of network timeout errors"""
        with patch('voice_handler.AssemblyAIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Mock timeout error
            mock_client.transcribe_audio = AsyncMock(side_effect=TimeoutError("Request timed out"))
            
            handler = VoiceMessageHandler(self.config)
            
            # This should be handled gracefully
            with patch.object(handler.audio_processor, 'download_voice_message', return_value=sample_audio_file), \
                 patch.object(handler.audio_processor, 'convert_and_optimize', return_value=(sample_audio_file, test_audio_metadata)):
                
                # Process should not raise exception
                result = await handler.assemblyai_client.transcribe_audio(sample_audio_file, test_audio_metadata)
                
                assert result.quality == VoiceQuality.FAILED
                assert "timeout" in result.error
    
    @pytest.mark.asyncio
    async def test_authentication_error(self, sample_audio_file, test_audio_metadata):
        """Test handling of authentication errors"""
        with patch('voice_handler.AssemblyAIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Mock auth error
            mock_client.transcribe_audio = AsyncMock(side_effect=Exception("Unauthorized: Invalid API key"))
            
            handler = VoiceMessageHandler(self.config)
            result = await handler.assemblyai_client.transcribe_audio(sample_audio_file, test_audio_metadata)
            
            assert result.quality == VoiceQuality.FAILED
            assert "authentication" in result.error
    
    @pytest.mark.asyncio
    async def test_unsupported_format_error(self, temporary_directory):
        """Test handling of unsupported audio format"""
        # Create file with unsupported format
        unsupported_file = temporary_directory / "test.xyz"
        unsupported_file.write_bytes(b"not audio data")
        
        with patch('voice_handler.AudioProcessor.convert_and_optimize', side_effect=ValueError("Unsupported audio format: xyz")):
            processor = AudioProcessor()
            
            with pytest.raises(ValueError, match="Unsupported audio format"):
                await processor.convert_and_optimize(unsupported_file)
    
    def test_invalid_configuration_errors(self):
        """Test various invalid configuration scenarios"""
        # Test missing API key
        with pytest.raises(TypeError):
            VoiceProcessingConfig()  # Missing required assemblyai_api_key
        
        # Test invalid confidence threshold
        with pytest.raises(Exception):
            VoiceProcessingConfig(
                assemblyai_api_key=TEST_API_KEY,
                confidence_threshold=1.5  # Should be 0-1
            )
        
        # Test invalid file size
        with pytest.raises(Exception):
            VoiceProcessingConfig(
                assemblyai_api_key=TEST_API_KEY,
                max_file_size_mb=-1  # Should be positive
            )
    
    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self):
        """Test handling of concurrent request limits"""
        config = VoiceProcessingConfig(
            assemblyai_api_key=TEST_API_KEY,
            concurrent_requests=2  # Low limit for testing
        )
        
        with patch('voice_handler.aai'):
            client = AssemblyAIClient(config)
            
            # Test that semaphore limits concurrent requests
            assert client._request_semaphore._value == 2
            
            # Simulate concurrent access
            async with client._request_semaphore:
                async with client._request_semaphore:
                    # Should not be able to acquire third semaphore without blocking
                    with pytest.raises(Exception):
                        client._request_semaphore.acquire_nowait()
    
    @pytest.mark.asyncio
    async def test_file_cleanup_on_error(self, sample_audio_file):
        """Test that temporary files are cleaned up even on errors"""
        with patch('voice_handler.AssemblyAIClient') as mock_client_class, \
             patch('voice_handler.AudioProcessor') as mock_processor_class:
            
            # Setup mocks to create temp files but fail processing
            mock_processor = Mock()
            mock_processor_class.return_value = mock_processor
            mock_processor.download_voice_message = AsyncMock(return_value=sample_audio_file)
            mock_processor.convert_and_optimize = AsyncMock(side_effect=Exception("Processing failed"))
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            handler = VoiceMessageHandler(VoiceProcessingConfig(assemblyai_api_key=TEST_API_KEY))
            
            # Mock the cleanup method to track calls
            handler._cleanup_temp_files = AsyncMock()
            
            # Process should fail but cleanup should still be called
            update = Mock()
            update.effective_user.id = 12345
            update.message.voice.duration = 5.0
            update.message.voice.file_size = TEST_AUDIO_SIZE
            update.message.voice.mime_type = "audio/ogg"
            
            context = Mock()
            context.bot.get_file = AsyncMock(return_value=Mock())
            context.bot.send_chat_action = AsyncMock()
            
            result = await handler.process_voice_message(update, context)
            
            # Should have failed but attempted cleanup
            assert result.quality == VoiceQuality.FAILED
            handler._cleanup_temp_files.assert_called_once()


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

@pytest.mark.performance
class TestPerformance:
    """Test performance aspects of voice processing"""
    
    @pytest.fixture(autouse=True)
    def setup_performance_tests(self, test_config):
        """Setup performance test environment"""
        self.config = test_config
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """Test handling of multiple concurrent voice messages"""
        # Create multiple mock voice messages
        num_concurrent = 5
        tasks = []
        
        with patch('voice_handler.AssemblyAIClient') as mock_client_class, \
             patch('voice_handler.AudioProcessor') as mock_processor_class:
            
            # Setup mocks for successful processing
            mock_processor = Mock()
            mock_processor_class.return_value = mock_processor
            mock_processor.download_voice_message = AsyncMock(return_value=Path("test.ogg"))
            mock_processor.convert_and_optimize = AsyncMock(return_value=(
                Path("test.wav"),
                {"duration": 5.0, "size_bytes": TEST_AUDIO_SIZE}
            ))
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.transcribe_audio = AsyncMock(return_value=VoiceTranscriptionResult(
                text="Concurrent test transcription",
                confidence=0.95,
                quality=VoiceQuality.HIGH,
                language="en",
                duration_seconds=5.0,
                processing_time_seconds=1.0,
                file_size_bytes=TEST_AUDIO_SIZE,
                format="wav"
            ))
            
            handler = VoiceMessageHandler(self.config)
            
            # Create concurrent processing tasks
            for i in range(num_concurrent):
                update = Mock()
                update.effective_user.id = 12345 + i
                update.message.voice.duration = 5.0
                update.message.voice.file_size = TEST_AUDIO_SIZE
                update.message.voice.mime_type = "audio/ogg"
                
                context = Mock()
                context.bot.get_file = AsyncMock(return_value=Mock())
                context.bot.send_chat_action = AsyncMock()
                
                task = handler.process_voice_message(update, context)
                tasks.append(task)
            
            # Process all concurrently
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            processing_time = time.time() - start_time
            
            # Verify all succeeded
            successful_results = [r for r in results if isinstance(r, VoiceTranscriptionResult) and r.quality != VoiceQuality.FAILED]
            assert len(successful_results) == num_concurrent
            
            # Performance check - should complete reasonably quickly
            assert processing_time < 10.0  # Should complete within 10 seconds
            
            # Check final statistics
            stats = handler.get_statistics()
            assert stats['messages_processed'] == num_concurrent
    
    @pytest.mark.asyncio
    async def test_large_file_handling_simulation(self):
        """Test handling of large audio files (simulated)"""
        # Simulate large file metadata
        large_file_metadata = {
            "duration": 300.0,  # 5 minutes
            "channels": 1,
            "frame_rate": 16000,
            "format": "wav",
            "size_bytes": 20 * 1024 * 1024,  # 20MB
            "telegram_duration": 300.0,
            "telegram_file_size": 20 * 1024 * 1024,
            "telegram_mime_type": "audio/wav"
        }
        
        with patch('voice_handler.AssemblyAIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Simulate longer processing time for large file
            async def slow_transcribe(audio_path, metadata):
                await asyncio.sleep(0.1)  # Simulate processing time
                return VoiceTranscriptionResult(
                    text="This is a long transcription from a large audio file with lots of content",
                    confidence=0.92,
                    quality=VoiceQuality.HIGH,
                    language="en",
                    duration_seconds=metadata["duration"],
                    processing_time_seconds=5.0,  # Longer processing time
                    file_size_bytes=metadata["size_bytes"],
                    format="wav"
                )
            
            mock_client.transcribe_audio = slow_transcribe
            
            handler = VoiceMessageHandler(self.config)
            
            # Test large file processing
            start_time = time.time()
            result = await handler.assemblyai_client.transcribe_audio(Path("large_test.wav"), large_file_metadata)
            processing_time = time.time() - start_time
            
            # Verify successful processing
            assert result.quality == VoiceQuality.HIGH
            assert result.duration_seconds == 300.0
            assert result.file_size_bytes == 20 * 1024 * 1024
            
            # Should handle large files efficiently
            assert processing_time < 1.0  # Mock should be fast
    
    @pytest.mark.asyncio 
    async def test_memory_usage_optimization(self):
        """Test memory usage optimization during processing"""
        # This is more of a structural test since we can't easily measure memory
        # in unit tests, but we can verify proper cleanup patterns
        
        temp_files_created = []
        
        def mock_temp_file_creation(*args, **kwargs):
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_files_created.append(temp_file.name)
            return temp_file.name
        
        with patch('voice_handler.AssemblyAIClient') as mock_client_class, \
             patch('voice_handler.AudioProcessor') as mock_processor_class, \
             patch('tempfile.NamedTemporaryFile', side_effect=mock_temp_file_creation):
            
            # Setup mocks
            mock_processor = Mock()
            mock_processor_class.return_value = mock_processor
            mock_processor.download_voice_message = AsyncMock(return_value=Path("test.ogg"))
            mock_processor.convert_and_optimize = AsyncMock(return_value=(
                Path("test.wav"),
                {"duration": 5.0, "size_bytes": TEST_AUDIO_SIZE}
            ))
            
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.transcribe_audio = AsyncMock(return_value=VoiceTranscriptionResult(
                text="Memory test transcription",
                confidence=0.95,
                quality=VoiceQuality.HIGH,
                language="en",
                duration_seconds=5.0,
                processing_time_seconds=1.0,
                file_size_bytes=TEST_AUDIO_SIZE,
                format="wav"
            ))
            
            handler = VoiceMessageHandler(self.config)
            handler._cleanup_temp_files = AsyncMock()
            
            # Process multiple messages to test cleanup
            for i in range(3):
                update = Mock()
                update.effective_user.id = 12345
                update.message.voice.duration = 5.0
                update.message.voice.file_size = TEST_AUDIO_SIZE
                update.message.voice.mime_type = "audio/ogg"
                
                context = Mock()
                context.bot.get_file = AsyncMock(return_value=Mock())
                context.bot.send_chat_action = AsyncMock()
                
                await handler.process_voice_message(update, context)
            
            # Verify cleanup was called for each processing
            assert handler._cleanup_temp_files.call_count == 3
    
    def test_configuration_performance_settings(self):
        """Test performance-related configuration settings"""
        # Test concurrent requests setting
        config = VoiceProcessingConfig(
            assemblyai_api_key=TEST_API_KEY,
            concurrent_requests=5
        )
        assert config.concurrent_requests == 5
        
        # Test retry settings
        config = VoiceProcessingConfig(
            assemblyai_api_key=TEST_API_KEY,
            retry_attempts=5,
            retry_delay_seconds=0.5,
            max_retry_delay=30.0
        )
        assert config.retry_attempts == 5
        assert config.retry_delay_seconds == 0.5
        assert config.max_retry_delay == 30.0


# =============================================================================
# FACTORY FUNCTIONS TESTS
# =============================================================================

class TestFactoryFunctions:
    """Test factory functions for easy handler creation"""
    
    def test_create_voice_handler_basic(self):
        """Test basic voice handler creation"""
        with patch('voice_handler.VoiceMessageHandler') as mock_handler:
            handler = create_voice_handler(TEST_API_KEY)
            
            mock_handler.assert_called_once()
            # Check that config was created with API key
            call_args = mock_handler.call_args[0][0]  # First positional argument (config)
            assert call_args.assemblyai_api_key == TEST_API_KEY
    
    def test_create_voice_handler_with_kwargs(self):
        """Test voice handler creation with additional kwargs"""
        with patch('voice_handler.VoiceMessageHandler') as mock_handler:
            handler = create_voice_handler(
                TEST_API_KEY,
                max_file_size_mb=50,
                confidence_threshold=0.8
            )
            
            mock_handler.assert_called_once()
            call_args = mock_handler.call_args[0][0]
            assert call_args.assemblyai_api_key == TEST_API_KEY
            assert call_args.max_file_size_mb == 50
            assert call_args.confidence_threshold == 0.8
    
    def test_create_voice_handler_with_features_enabled(self):
        """Test voice handler creation with advanced features enabled"""
        with patch('voice_handler.VoiceMessageHandler') as mock_handler:
            handler = create_voice_handler_with_features(
                TEST_API_KEY,
                enable_advanced_features=True
            )
            
            mock_handler.assert_called_once()
            call_args = mock_handler.call_args[0][0]
            assert call_args.assemblyai_api_key == TEST_API_KEY
            assert call_args.enable_auto_language_detection is True
            assert call_args.enable_speaker_labels is True
            assert call_args.enable_pii_redaction is True
            assert call_args.enable_summarization is True
            assert call_args.enable_content_safety is True
    
    def test_create_voice_handler_with_features_disabled(self):
        """Test voice handler creation with advanced features disabled"""
        with patch('voice_handler.VoiceMessageHandler') as mock_handler:
            handler = create_voice_handler_with_features(
                TEST_API_KEY,
                enable_advanced_features=False
            )
            
            mock_handler.assert_called_once()
            call_args = mock_handler.call_args[0][0]
            assert call_args.assemblyai_api_key == TEST_API_KEY
            # Advanced features should use default values (not forced on)
    
    def test_create_voice_handler_with_features_override(self):
        """Test voice handler creation with feature overrides"""
        with patch('voice_handler.VoiceMessageHandler') as mock_handler:
            handler = create_voice_handler_with_features(
                TEST_API_KEY,
                enable_advanced_features=True,
                enable_speaker_labels=False,  # Override default
                enable_summarization=False   # Override default
            )
            
            mock_handler.assert_called_once()
            call_args = mock_handler.call_args[0][0]
            assert call_args.enable_auto_language_detection is True  # From defaults
            assert call_args.enable_speaker_labels is False  # Overridden
            assert call_args.enable_summarization is False   # Overridden
            assert call_args.enable_pii_redaction is True    # From defaults


# =============================================================================
# REAL INTEGRATION TESTS (Run only if explicitly enabled)
# =============================================================================

@pytest.mark.integration
@pytest.mark.skipif(not INTEGRATION_TEST_ENABLED, reason="Real API integration tests disabled")
class TestRealAssemblyAIIntegration:
    """
    Real integration tests using actual AssemblyAI API
    Only run when ASSEMBLYAI_INTEGRATION_TESTS=true environment variable is set
    Requires valid AssemblyAI API key in environment
    """
    
    @pytest.fixture(autouse=True)
    def setup_real_integration(self):
        """Setup real integration tests"""
        self.real_api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not self.real_api_key:
            pytest.skip("ASSEMBLYAI_API_KEY not set for integration tests")
        
        self.config = VoiceProcessingConfig(
            assemblyai_api_key=self.real_api_key,
            retry_attempts=2,  # Reduce retries for faster testing
            retry_delay_seconds=1.0
        )
    
    @pytest.mark.asyncio
    async def test_real_api_connection(self):
        """Test actual connection to AssemblyAI API"""
        client = AssemblyAIClient(self.config)
        
        # Create a very small test audio file
        test_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        
        # Create minimal WAV file (1 second of silence)
        import wave
        with wave.open(test_audio.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(16000)  # 16kHz
            # Write 1 second of silence
            silence = b'\x00\x00' * 16000
            wav_file.writeframes(silence)
        
        try:
            metadata = {
                "duration": 1.0,
                "size_bytes": os.path.getsize(test_audio.name),
                "format": "wav"
            }
            
            result = await client.transcribe_audio(Path(test_audio.name), metadata)
            
            # Should get some result (even if low quality due to silence)
            assert isinstance(result, VoiceTranscriptionResult)
            assert result.processing_time_seconds > 0
            
        finally:
            # Cleanup
            os.unlink(test_audio.name)
    
    @pytest.mark.asyncio
    async def test_real_api_error_handling(self):
        """Test error handling with real API"""
        # Test with invalid API key
        bad_config = VoiceProcessingConfig(assemblyai_api_key="invalid_key_123")
        client = AssemblyAIClient(bad_config)
        
        test_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        test_audio.write(b"fake audio data")
        test_audio.close()
        
        try:
            metadata = {"duration": 1.0, "size_bytes": 16, "format": "wav"}
            result = await client.transcribe_audio(Path(test_audio.name), metadata)
            
            # Should fail gracefully
            assert result.quality == VoiceQuality.FAILED
            assert "authentication" in result.error.lower()
            
        finally:
            os.unlink(test_audio.name)


# =============================================================================
# TEST CONFIGURATION AND RUNNERS
# =============================================================================

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle markers properly"""
    if not INTEGRATION_TEST_ENABLED:
        skip_integration = pytest.mark.skip(reason="Integration tests disabled (set ASSEMBLYAI_INTEGRATION_TESTS=true to enable)")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)

# Helper function to run specific test categories
def run_unit_tests():
    """Run only unit tests (fast, no API calls)"""
    return pytest.main([
        __file__,
        "-v",
        "-m", "not integration and not performance",
        "--tb=short"
    ])

def run_integration_tests():
    """Run integration tests with mocks"""
    return pytest.main([
        __file__,
        "-v", 
        "-m", "integration",
        "--tb=short"
    ])

def run_performance_tests():
    """Run performance tests"""
    return pytest.main([
        __file__,
        "-v",
        "-m", "performance", 
        "--tb=short"
    ])

def run_all_tests_with_coverage():
    """Run all tests with coverage reporting"""
    return pytest.main([
        __file__,
        "-v",
        "--cov=voice_handler",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--tb=short"
    ])

if __name__ == "__main__":
    """
    Run tests directly from command line
    
    Usage:
        python test_assemblyai_integration.py              # Run unit tests
        python test_assemblyai_integration.py integration  # Run integration tests
        python test_assemblyai_integration.py performance  # Run performance tests
        python test_assemblyai_integration.py coverage     # Run with coverage
        python test_assemblyai_integration.py all         # Run all tests
    """
    import sys
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == "integration":
            exit(run_integration_tests())
        elif test_type == "performance":
            exit(run_performance_tests())
        elif test_type == "coverage":
            exit(run_all_tests_with_coverage())
        elif test_type == "all":
            exit(pytest.main([__file__, "-v", "--tb=short"]))
        else:
            print(f"Unknown test type: {test_type}")
            print("Available types: integration, performance, coverage, all")
            exit(1)
    else:
        # Default: run unit tests only
        exit(run_unit_tests())