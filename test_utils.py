#!/usr/bin/env python3
"""
Test utilities and helpers for AssemblyAI integration tests

This module provides utility functions, test data generators, and helper classes
to support comprehensive testing of the voice processing system.
"""

import asyncio
import os
import tempfile
import wave
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import Mock, AsyncMock
from dataclasses import dataclass
from datetime import datetime, timedelta

import pytest

# Test constants
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_CHANNELS = 1
DEFAULT_SAMPLE_WIDTH = 2  # 16-bit
SILENCE_BYTE = b'\x00\x00'

@dataclass
class AudioTestFile:
    """Represents a test audio file with metadata"""
    path: Path
    duration_seconds: float
    sample_rate: int
    channels: int
    format: str
    size_bytes: int
    is_valid: bool = True

class AudioFileGenerator:
    """Generate various types of audio files for testing"""
    
    @staticmethod
    def create_wav_silence(duration_seconds: float, 
                          sample_rate: int = DEFAULT_SAMPLE_RATE,
                          channels: int = DEFAULT_CHANNELS,
                          sample_width: int = DEFAULT_SAMPLE_WIDTH) -> AudioTestFile:
        """Create a WAV file with silence"""
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        
        with wave.open(temp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            
            # Calculate number of frames
            num_frames = int(duration_seconds * sample_rate)
            silence = SILENCE_BYTE * num_frames * channels
            wav_file.writeframes(silence)
        
        file_path = Path(temp_file.name)
        return AudioTestFile(
            path=file_path,
            duration_seconds=duration_seconds,
            sample_rate=sample_rate,
            channels=channels,
            format="wav",
            size_bytes=file_path.stat().st_size,
            is_valid=True
        )
    
    @staticmethod
    def create_wav_tone(duration_seconds: float,
                       frequency: float = 440.0,  # A4 note
                       sample_rate: int = DEFAULT_SAMPLE_RATE,
                       channels: int = DEFAULT_CHANNELS) -> AudioTestFile:
        """Create a WAV file with a sine wave tone"""
        import math
        
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        
        with wave.open(temp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(DEFAULT_SAMPLE_WIDTH)
            wav_file.setframerate(sample_rate)
            
            num_frames = int(duration_seconds * sample_rate)
            amplitude = 32767  # Max amplitude for 16-bit
            
            frames = []
            for i in range(num_frames):
                # Generate sine wave
                sample_value = int(amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
                # Convert to bytes (little-endian 16-bit)
                sample_bytes = sample_value.to_bytes(2, byteorder='little', signed=True)
                frames.append(sample_bytes * channels)
            
            wav_file.writeframes(b''.join(frames))
        
        file_path = Path(temp_file.name)
        return AudioTestFile(
            path=file_path,
            duration_seconds=duration_seconds,
            sample_rate=sample_rate,
            channels=channels,
            format="wav",
            size_bytes=file_path.stat().st_size,
            is_valid=True
        )
    
    @staticmethod
    def create_ogg_like_file(size_bytes: int) -> AudioTestFile:
        """Create an OGG-like file (not real OGG, just for testing)"""
        temp_file = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
        
        # Write minimal OGG header
        ogg_header = b'OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00'
        remaining_bytes = size_bytes - len(ogg_header)
        
        temp_file.write(ogg_header)
        temp_file.write(b'\x00' * max(0, remaining_bytes))
        temp_file.close()
        
        file_path = Path(temp_file.name)
        return AudioTestFile(
            path=file_path,
            duration_seconds=5.0,  # Estimated
            sample_rate=DEFAULT_SAMPLE_RATE,
            channels=DEFAULT_CHANNELS,
            format="ogg",
            size_bytes=size_bytes,
            is_valid=False  # Not a real OGG file
        )
    
    @staticmethod
    def create_mp3_like_file(size_bytes: int) -> AudioTestFile:
        """Create an MP3-like file (not real MP3, just for testing)"""
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        
        # Write minimal MP3 header
        mp3_header = b'\xFF\xFB\x90\x00'  # MP3 frame header
        remaining_bytes = size_bytes - len(mp3_header)
        
        temp_file.write(mp3_header)
        temp_file.write(b'\x00' * max(0, remaining_bytes))
        temp_file.close()
        
        file_path = Path(temp_file.name)
        return AudioTestFile(
            path=file_path,
            duration_seconds=5.0,  # Estimated
            sample_rate=44100,  # Typical MP3 rate
            channels=2,  # Stereo
            format="mp3",
            size_bytes=size_bytes,
            is_valid=False  # Not a real MP3 file
        )
    
    @staticmethod
    def create_corrupted_file(extension: str = ".wav") -> AudioTestFile:
        """Create a corrupted audio file"""
        temp_file = tempfile.NamedTemporaryFile(suffix=extension, delete=False)
        temp_file.write(b'This is definitely not valid audio data!')
        temp_file.close()
        
        file_path = Path(temp_file.name)
        return AudioTestFile(
            path=file_path,
            duration_seconds=0,
            sample_rate=0,
            channels=0,
            format=extension[1:],  # Remove dot
            size_bytes=file_path.stat().st_size,
            is_valid=False
        )
    
    @staticmethod
    def create_large_file(size_mb: float, extension: str = ".wav") -> AudioTestFile:
        """Create a large audio file for testing size limits"""
        temp_file = tempfile.NamedTemporaryFile(suffix=extension, delete=False)
        
        size_bytes = int(size_mb * 1024 * 1024)
        
        if extension == ".wav":
            # Write WAV header
            temp_file.write(b'RIFF')
            temp_file.write((size_bytes - 8).to_bytes(4, 'little'))
            temp_file.write(b'WAVE')
            # Fill rest with zeros
            temp_file.write(b'\x00' * (size_bytes - 12))
        else:
            # Just fill with zeros
            temp_file.write(b'\x00' * size_bytes)
        
        temp_file.close()
        
        file_path = Path(temp_file.name)
        estimated_duration = size_bytes / (DEFAULT_SAMPLE_RATE * DEFAULT_CHANNELS * DEFAULT_SAMPLE_WIDTH)
        
        return AudioTestFile(
            path=file_path,
            duration_seconds=estimated_duration,
            sample_rate=DEFAULT_SAMPLE_RATE,
            channels=DEFAULT_CHANNELS,
            format=extension[1:],
            size_bytes=size_bytes,
            is_valid=extension == ".wav"
        )

class MockTranscriptGenerator:
    """Generate mock transcript objects for testing"""
    
    @staticmethod
    def create_successful_transcript(text: str = "Test transcription", 
                                   confidence: float = 0.95,
                                   language: str = "en",
                                   transcript_id: str = "test_123") -> Mock:
        """Create a mock successful transcript"""
        transcript = Mock()
        transcript.id = transcript_id
        transcript.status = "completed"
        transcript.text = text
        transcript.confidence = confidence
        transcript.language_code = language
        transcript.audio_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}/audio"
        transcript.error = None
        
        # Language detection
        lang_detection = Mock()
        lang_detection.language = language
        lang_detection.confidence = confidence + 0.02  # Slightly higher
        transcript.language_detection_results = [lang_detection]
        
        # Speaker labels
        utterance = Mock()
        utterance.speaker = "A"
        utterance.text = text
        utterance.confidence = confidence
        utterance.start = 0
        utterance.end = len(text) * 100  # Rough timing
        transcript.utterances = [utterance]
        
        # Summary
        transcript.summary = f"Summary of: {text[:50]}..."
        
        # Chapters
        chapter = Mock()
        chapter.summary = "Main content"
        chapter.headline = "Introduction"
        chapter.start = 0
        chapter.end = len(text) * 100
        transcript.chapters = [chapter]
        
        # Content safety
        safety_label = Mock()
        safety_label.label = "safe"
        safety_label.confidence = 0.99
        safety_label.severity = 0.1
        safety_labels = Mock()
        safety_labels.results = [safety_label]
        transcript.content_safety_labels = safety_labels
        
        # Topics
        topic_label = Mock()
        topic_label.relevance = 0.8
        topic_label.label = "general"
        topic = Mock()
        topic.text = text
        topic.labels = [topic_label]
        transcript.topics = [topic]
        
        # Sentiment analysis
        sentiment = Mock()
        sentiment.text = text
        sentiment.sentiment = "POSITIVE"
        sentiment.confidence = 0.8
        sentiment.start = 0
        sentiment.end = len(text) * 100
        transcript.sentiment_analysis_results = [sentiment]
        
        return transcript
    
    @staticmethod
    def create_failed_transcript(error_message: str = "Processing failed",
                               transcript_id: str = "failed_123") -> Mock:
        """Create a mock failed transcript"""
        transcript = Mock()
        transcript.id = transcript_id
        transcript.status = "error"
        transcript.text = None
        transcript.confidence = None
        transcript.language_code = None
        transcript.error = error_message
        transcript.audio_url = None
        
        # No enhanced features
        transcript.language_detection_results = []
        transcript.utterances = []
        transcript.summary = None
        transcript.chapters = []
        transcript.content_safety_labels = None
        transcript.topics = []
        transcript.sentiment_analysis_results = []
        
        return transcript
    
    @staticmethod
    def create_low_confidence_transcript(confidence: float = 0.3,
                                       transcript_id: str = "low_conf_123") -> Mock:
        """Create a mock transcript with low confidence"""
        return MockTranscriptGenerator.create_successful_transcript(
            text="umm... unclear... maybe...",
            confidence=confidence,
            transcript_id=transcript_id
        )
    
    @staticmethod
    def create_processing_transcript(transcript_id: str = "processing_123") -> Mock:
        """Create a mock transcript still processing"""
        transcript = Mock()
        transcript.id = transcript_id
        transcript.status = "processing"
        transcript.text = None
        transcript.confidence = None
        transcript.error = None
        return transcript

class TelegramMockFactory:
    """Factory for creating Telegram-related mocks"""
    
    @staticmethod
    def create_voice_message(duration: float = 5.0,
                           file_size: int = 100 * 1024,
                           mime_type: str = "audio/ogg",
                           file_id: str = "test_file_123") -> Mock:
        """Create a mock Telegram voice message"""
        voice = Mock()
        voice.duration = duration
        voice.file_size = file_size
        voice.mime_type = mime_type
        voice.file_id = file_id
        voice.file_unique_id = f"unique_{file_id}"
        return voice
    
    @staticmethod
    def create_update(user_id: int = 12345,
                     chat_id: int = 67890,
                     voice_message: Optional[Mock] = None) -> Mock:
        """Create a mock Telegram update"""
        if voice_message is None:
            voice_message = TelegramMockFactory.create_voice_message()
        
        update = Mock()
        update.effective_user.id = user_id
        update.effective_user.username = f"user_{user_id}"
        update.effective_user.first_name = "Test"
        update.effective_chat.id = chat_id
        update.effective_chat.type = "private"
        update.message.voice = voice_message
        update.message.message_id = hash(f"{user_id}_{chat_id}") % 100000
        update.message.date = datetime.now()
        return update
    
    @staticmethod
    def create_context() -> Mock:
        """Create a mock Telegram context"""
        context = Mock()
        context.bot.get_file = AsyncMock()
        context.bot.send_chat_action = AsyncMock()
        context.bot.send_message = AsyncMock()
        context.bot.edit_message_text = AsyncMock()
        return context
    
    @staticmethod
    def create_file(file_id: str = "test_file_123",
                   mime_type: str = "audio/ogg",
                   file_size: int = 100 * 1024) -> Mock:
        """Create a mock Telegram file"""
        file_obj = Mock()
        file_obj.file_id = file_id
        file_obj.file_unique_id = f"unique_{file_id}"
        file_obj.mime_type = mime_type
        file_obj.file_size = file_size
        file_obj.file_path = f"voice/{file_id}.ogg"
        
        # Mock download method
        async def mock_download(file_path):
            # Create a dummy file
            with open(file_path, 'wb') as f:
                f.write(b'dummy audio data' * (file_size // 16))
        
        file_obj.download_to_drive = AsyncMock(side_effect=mock_download)
        return file_obj

class TestDataValidator:
    """Validate test data and results"""
    
    @staticmethod
    def validate_transcription_result(result) -> bool:
        """Validate a VoiceTranscriptionResult object"""
        from voice_handler import VoiceTranscriptionResult, VoiceQuality
        
        if not isinstance(result, VoiceTranscriptionResult):
            return False
        
        # Check required fields
        required_attrs = [
            'text', 'confidence', 'quality', 'language', 
            'duration_seconds', 'processing_time_seconds',
            'file_size_bytes', 'format'
        ]
        
        for attr in required_attrs:
            if not hasattr(result, attr):
                return False
        
        # Check value ranges
        if not (0.0 <= result.confidence <= 1.0):
            return False
        
        if not isinstance(result.quality, VoiceQuality):
            return False
        
        if result.duration_seconds < 0 or result.processing_time_seconds < 0:
            return False
        
        if result.file_size_bytes < 0:
            return False
        
        return True
    
    @staticmethod
    def validate_config(config) -> bool:
        """Validate a VoiceProcessingConfig object"""
        from voice_handler import VoiceProcessingConfig
        
        if not isinstance(config, VoiceProcessingConfig):
            return False
        
        # Check API key
        if not config.assemblyai_api_key:
            return False
        
        # Check numeric ranges
        if config.max_file_size_mb <= 0:
            return False
        
        if not (0.0 <= config.confidence_threshold <= 1.0):
            return False
        
        if config.min_duration_seconds <= 0:
            return False
        
        if config.max_duration_seconds <= config.min_duration_seconds:
            return False
        
        if config.concurrent_requests <= 0:
            return False
        
        if config.retry_attempts < 0:
            return False
        
        return True

class PerformanceTracker:
    """Track performance metrics during tests"""
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.metrics: Dict[str, Any] = {}
    
    def start(self):
        """Start timing"""
        self.start_time = time.time()
    
    def stop(self):
        """Stop timing"""
        self.end_time = time.time()
    
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time is None:
            return 0.0
        
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time
    
    def add_metric(self, name: str, value: Any):
        """Add a performance metric"""
        self.metrics[name] = value
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics including timing"""
        metrics = self.metrics.copy()
        metrics['elapsed_time'] = self.elapsed_time()
        return metrics
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()

class AsyncTestHelper:
    """Helper for async testing operations"""
    
    @staticmethod
    async def wait_for_condition(condition_func, 
                               timeout_seconds: float = 5.0,
                               poll_interval: float = 0.1) -> bool:
        """Wait for a condition to become true"""
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            if condition_func():
                return True
            await asyncio.sleep(poll_interval)
        
        return False
    
    @staticmethod
    async def run_concurrent_tasks(tasks: List, max_concurrent: int = 5) -> List:
        """Run tasks with limited concurrency"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_task(task):
            async with semaphore:
                return await task
        
        limited_tasks = [limited_task(task) for task in tasks]
        return await asyncio.gather(*limited_tasks, return_exceptions=True)

class TestEnvironment:
    """Manage test environment setup and teardown"""
    
    def __init__(self):
        self.temp_files: List[Path] = []
        self.temp_dirs: List[Path] = []
    
    def create_temp_file(self, suffix: str = ".tmp", content: bytes = b"") -> Path:
        """Create a temporary file"""
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        temp_file.write(content)
        temp_file.close()
        
        path = Path(temp_file.name)
        self.temp_files.append(path)
        return path
    
    def create_temp_dir(self, prefix: str = "test_") -> Path:
        """Create a temporary directory"""
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def cleanup(self):
        """Clean up all temporary files and directories"""
        # Clean up files
        for file_path in self.temp_files:
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception as e:
                print(f"Failed to delete temp file {file_path}: {e}")
        
        # Clean up directories
        import shutil
        for dir_path in self.temp_dirs:
            try:
                if dir_path.exists():
                    shutil.rmtree(dir_path)
            except Exception as e:
                print(f"Failed to delete temp dir {dir_path}: {e}")
        
        self.temp_files.clear()
        self.temp_dirs.clear()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()

# Utility functions for common test operations
def create_test_config(**overrides) -> 'VoiceProcessingConfig':
    """Create a test configuration with optional overrides"""
    from voice_handler import VoiceProcessingConfig
    
    defaults = {
        'assemblyai_api_key': 'test_api_key_12345',
        'max_file_size_mb': 25,
        'confidence_threshold': 0.6,
        'retry_attempts': 3,
        'concurrent_requests': 3
    }
    
    config_params = {**defaults, **overrides}
    return VoiceProcessingConfig(**config_params)

def assert_timing_reasonable(elapsed_time: float, expected_max: float = 5.0):
    """Assert that timing is reasonable for tests"""
    assert elapsed_time >= 0, f"Elapsed time should be non-negative, got {elapsed_time}"
    assert elapsed_time <= expected_max, f"Elapsed time {elapsed_time}s exceeds maximum {expected_max}s"

def mock_assemblyai_client_methods(client_mock):
    """Add common mock methods to AssemblyAI client mock"""
    client_mock.transcribe_audio = AsyncMock()
    client_mock._rate_limit = AsyncMock()
    client_mock._validate_audio_file = AsyncMock()
    client_mock._build_transcript_config = Mock()
    client_mock._transcribe_with_retries = AsyncMock()
    client_mock._is_retryable_error = Mock(return_value=True)
    client_mock.search_words_in_transcript = AsyncMock()
    return client_mock

# Export commonly used classes and functions
__all__ = [
    'AudioTestFile',
    'AudioFileGenerator',
    'MockTranscriptGenerator', 
    'TelegramMockFactory',
    'TestDataValidator',
    'PerformanceTracker',
    'AsyncTestHelper',
    'TestEnvironment',
    'create_test_config',
    'assert_timing_reasonable',
    'mock_assemblyai_client_methods'
]