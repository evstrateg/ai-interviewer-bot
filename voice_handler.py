#!/usr/bin/env python3
"""
Voice Message Processing System for AI Interviewer Telegram Bot
Comprehensive AssemblyAI integration with error handling and optimization.

Features:
- AssemblyAI client setup and configuration
- Telegram voice message download handling
- Audio file format conversion and optimization
- Transcription with error handling and retries
- Multi-language support (English/Russian)
- Rate limiting and concurrent request management
- Integration with existing bot session management
"""

import asyncio
import json
import logging
import os
import tempfile
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import time
import hashlib
import mimetypes
from dataclasses import dataclass
from enum import Enum

import assemblyai as aai
import structlog
from telegram import Update, File
from telegram.ext import ContextTypes
import httpx
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

logger = structlog.get_logger()

class VoiceQuality(Enum):
    """Voice transcription quality levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    FAILED = "failed"

class AudioFormat(Enum):
    """Supported audio formats"""
    OGG = "ogg"
    MP3 = "mp3" 
    M4A = "m4a"
    WAV = "wav"
    WEBM = "webm"
    OPUS = "opus"

@dataclass
class VoiceTranscriptionResult:
    """Result of voice transcription"""
    text: str
    confidence: float
    quality: VoiceQuality
    language: Optional[str]
    duration_seconds: float
    processing_time_seconds: float
    file_size_bytes: int
    format: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class VoiceProcessingConfig:
    """Voice processing configuration"""
    assemblyai_api_key: str
    max_file_size_mb: int = 25  # AssemblyAI limit
    min_duration_seconds: float = 0.5
    max_duration_seconds: float = 600  # 10 minutes
    confidence_threshold: float = 0.6
    default_language: str = "en"
    supported_languages: List[str] = None
    enable_auto_language_detection: bool = True
    enable_speaker_labels: bool = False
    enable_punctuation: bool = True
    enable_format_text: bool = True
    concurrent_requests: int = 3
    retry_attempts: int = 3
    retry_delay_seconds: float = 2.0
    
    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = ["en", "ru", "es", "fr", "de", "it", "pt"]

class AudioProcessor:
    """Audio file processing and optimization"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "ai_interviewer_audio"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def download_voice_message(self, file: File, user_id: int) -> Path:
        """Download voice message from Telegram"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = hashlib.md5(f"{user_id}_{timestamp}_{file.file_id}".encode()).hexdigest()[:8]
            
            # Detect file extension
            mime_type = file.mime_type or "audio/ogg"
            extension = self._mime_to_extension(mime_type)
            
            output_path = self.temp_dir / f"voice_{user_id}_{file_hash}.{extension}"
            
            # Download file
            start_time = time.time()
            await file.download_to_drive(output_path)
            download_time = time.time() - start_time
            
            logger.info("Voice message downloaded",
                       user_id=user_id,
                       file_id=file.file_id,
                       size_bytes=output_path.stat().st_size,
                       download_time=download_time,
                       path=str(output_path))
            
            return output_path
            
        except Exception as e:
            logger.error("Voice download failed",
                        user_id=user_id,
                        file_id=file.file_id,
                        error=str(e))
            raise
    
    def _mime_to_extension(self, mime_type: str) -> str:
        """Convert MIME type to file extension"""
        mime_to_ext = {
            "audio/ogg": "ogg",
            "audio/mpeg": "mp3",
            "audio/mp4": "m4a",
            "audio/wav": "wav",
            "audio/webm": "webm",
            "audio/opus": "opus"
        }
        return mime_to_ext.get(mime_type, "ogg")
    
    async def convert_and_optimize(self, input_path: Path) -> Tuple[Path, Dict[str, Any]]:
        """Convert audio to optimal format for AssemblyAI"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(str(input_path))
            
            # Get original metadata
            original_metadata = {
                "duration": len(audio) / 1000.0,  # Convert to seconds
                "channels": audio.channels,
                "frame_rate": audio.frame_rate,
                "format": input_path.suffix[1:].lower()
            }
            
            # Optimize for transcription
            optimized_audio = await self._optimize_audio(audio)
            
            # Generate output path
            output_path = input_path.with_suffix('.wav')
            
            # Export optimized audio
            start_time = time.time()
            optimized_audio.export(
                str(output_path),
                format="wav",
                parameters=["-ar", "16000", "-ac", "1"]  # 16kHz mono
            )
            processing_time = time.time() - start_time
            
            # Get optimized metadata
            optimized_metadata = {
                "duration": len(optimized_audio) / 1000.0,
                "channels": optimized_audio.channels,
                "frame_rate": optimized_audio.frame_rate,
                "format": "wav",
                "processing_time": processing_time,
                "size_bytes": output_path.stat().st_size,
                "compression_ratio": output_path.stat().st_size / input_path.stat().st_size
            }
            
            logger.info("Audio conversion complete",
                       original=original_metadata,
                       optimized=optimized_metadata)
            
            return output_path, {**original_metadata, **optimized_metadata}
            
        except CouldntDecodeError as e:
            logger.error("Audio decoding failed", path=str(input_path), error=str(e))
            raise ValueError(f"Unsupported audio format: {e}")
        except Exception as e:
            logger.error("Audio conversion failed", path=str(input_path), error=str(e))
            raise
    
    async def _optimize_audio(self, audio: AudioSegment) -> AudioSegment:
        """Optimize audio for transcription quality"""
        # Convert to mono
        if audio.channels > 1:
            audio = audio.set_channels(1)
        
        # Normalize sample rate to 16kHz (optimal for speech recognition)
        if audio.frame_rate != 16000:
            audio = audio.set_frame_rate(16000)
        
        # Apply noise reduction and normalization
        # Normalize volume
        normalized_audio = audio.normalize()
        
        # Apply high-pass filter to remove low-frequency noise
        # This is a simple approximation - more sophisticated filtering could be added
        filtered_audio = normalized_audio.high_pass_filter(100)
        
        return filtered_audio
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary audio files"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            cleaned_count = 0
            
            for file_path in self.temp_dir.glob("voice_*"):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info("Cleaned up temp audio files", count=cleaned_count)
                
        except Exception as e:
            logger.error("Temp file cleanup failed", error=str(e))

class AssemblyAIClient:
    """Enhanced AssemblyAI client with retry logic and error handling"""
    
    def __init__(self, config: VoiceProcessingConfig):
        self.config = config
        self.client = aai.Transcriber()
        aai.settings.api_key = config.assemblyai_api_key
        
        # Rate limiting
        self._request_semaphore = asyncio.Semaphore(config.concurrent_requests)
        self._last_request_times: List[float] = []
    
    async def transcribe_audio(self, audio_path: Path, metadata: Dict[str, Any]) -> VoiceTranscriptionResult:
        """Transcribe audio file with comprehensive error handling"""
        start_time = time.time()
        
        try:
            # Rate limiting
            await self._rate_limit()
            
            # Validate file
            await self._validate_audio_file(audio_path, metadata)
            
            # Configure transcription
            transcript_config = self._build_transcript_config(metadata)
            
            # Perform transcription with retries
            transcript = await self._transcribe_with_retries(audio_path, transcript_config)
            
            processing_time = time.time() - start_time
            
            # Process result
            result = self._process_transcript_result(transcript, metadata, processing_time)
            
            logger.info("Transcription completed",
                       duration=metadata.get('duration', 0),
                       confidence=result.confidence,
                       quality=result.quality.value,
                       processing_time=processing_time,
                       text_length=len(result.text))
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error("Transcription failed",
                        path=str(audio_path),
                        error=str(e),
                        processing_time=processing_time)
            
            return VoiceTranscriptionResult(
                text="",
                confidence=0.0,
                quality=VoiceQuality.FAILED,
                language=None,
                duration_seconds=metadata.get('duration', 0),
                processing_time_seconds=processing_time,
                file_size_bytes=metadata.get('size_bytes', 0),
                format=metadata.get('format', 'unknown'),
                error=str(e)
            )
    
    async def _rate_limit(self):
        """Implement rate limiting for API calls"""
        async with self._request_semaphore:
            current_time = time.time()
            
            # Clean old requests (older than 1 minute)
            self._last_request_times = [
                t for t in self._last_request_times 
                if current_time - t < 60
            ]
            
            # Check if we need to wait
            if len(self._last_request_times) >= self.config.concurrent_requests:
                oldest_request = min(self._last_request_times)
                wait_time = 60 - (current_time - oldest_request)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
            
            self._last_request_times.append(current_time)
    
    async def _validate_audio_file(self, audio_path: Path, metadata: Dict[str, Any]):
        """Validate audio file for transcription"""
        file_size_mb = metadata.get('size_bytes', 0) / (1024 * 1024)
        duration = metadata.get('duration', 0)
        
        if not audio_path.exists():
            raise ValueError("Audio file not found")
        
        if file_size_mb > self.config.max_file_size_mb:
            raise ValueError(f"File too large: {file_size_mb:.1f}MB (max: {self.config.max_file_size_mb}MB)")
        
        if duration < self.config.min_duration_seconds:
            raise ValueError(f"Audio too short: {duration:.1f}s (min: {self.config.min_duration_seconds}s)")
        
        if duration > self.config.max_duration_seconds:
            raise ValueError(f"Audio too long: {duration:.1f}s (max: {self.config.max_duration_seconds}s)")
    
    def _build_transcript_config(self, metadata: Dict[str, Any]) -> aai.TranscriptionConfig:
        """Build transcription configuration"""
        config = aai.TranscriptionConfig(
            language_detection=self.config.enable_auto_language_detection,
            punctuate=self.config.enable_punctuation,
            format_text=self.config.enable_format_text,
            speaker_labels=self.config.enable_speaker_labels
        )
        
        # Set language if not using auto-detection
        if not self.config.enable_auto_language_detection:
            config.language_code = self.config.default_language
        
        return config
    
    async def _transcribe_with_retries(self, audio_path: Path, config: aai.TranscriptionConfig) -> aai.Transcript:
        """Perform transcription with retry logic"""
        last_error = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                # Run transcription in thread pool to avoid blocking
                transcript = await asyncio.to_thread(
                    self.client.transcribe,
                    str(audio_path),
                    config=config
                )
                
                # Check if transcription was successful
                if transcript.status == aai.TranscriptStatus.error:
                    raise Exception(f"AssemblyAI error: {transcript.error}")
                
                return transcript
                
            except Exception as e:
                last_error = e
                logger.warning("Transcription attempt failed",
                              attempt=attempt + 1,
                              max_attempts=self.config.retry_attempts,
                              error=str(e))
                
                if attempt < self.config.retry_attempts - 1:
                    wait_time = self.config.retry_delay_seconds * (2 ** attempt)
                    await asyncio.sleep(wait_time)
        
        raise last_error
    
    def _process_transcript_result(self, transcript: aai.Transcript, metadata: Dict[str, Any], processing_time: float) -> VoiceTranscriptionResult:
        """Process transcript result and determine quality"""
        # Get transcription text
        text = transcript.text or ""
        
        # Calculate confidence score
        confidence = transcript.confidence or 0.0
        
        # Determine quality based on confidence and other factors
        quality = self._determine_quality(confidence, text, metadata)
        
        # Detect language
        language = getattr(transcript, 'language_code', None) or self.config.default_language
        
        # Build result
        result = VoiceTranscriptionResult(
            text=text,
            confidence=confidence,
            quality=quality,
            language=language,
            duration_seconds=metadata.get('duration', 0),
            processing_time_seconds=processing_time,
            file_size_bytes=metadata.get('size_bytes', 0),
            format=metadata.get('format', 'unknown'),
            metadata={
                'transcript_id': transcript.id,
                'word_count': len(text.split()) if text else 0,
                'characters': len(text),
                'audio_url': transcript.audio_url,
                'language_confidence': getattr(transcript, 'language_confidence', None)
            }
        )
        
        return result
    
    def _determine_quality(self, confidence: float, text: str, metadata: Dict[str, Any]) -> VoiceQuality:
        """Determine transcription quality"""
        if not text or confidence == 0.0:
            return VoiceQuality.FAILED
        
        # Check confidence threshold
        if confidence < self.config.confidence_threshold:
            return VoiceQuality.LOW
        
        # Check text quality indicators
        word_count = len(text.split())
        duration = metadata.get('duration', 0)
        
        # Very short text for longer audio might indicate poor quality
        if duration > 10 and word_count < 3:
            return VoiceQuality.LOW
        
        # High confidence and reasonable text length
        if confidence >= 0.85 and word_count >= 3:
            return VoiceQuality.HIGH
        
        return VoiceQuality.MEDIUM

class VoiceMessageHandler:
    """Main voice message handler integrating all components"""
    
    def __init__(self, config: VoiceProcessingConfig):
        self.config = config
        self.audio_processor = AudioProcessor()
        self.assemblyai_client = AssemblyAIClient(config)
        
        # Statistics
        self.stats = {
            'messages_processed': 0,
            'successful_transcriptions': 0,
            'failed_transcriptions': 0,
            'total_audio_duration': 0.0,
            'total_processing_time': 0.0
        }
    
    async def process_voice_message(self, 
                                  update: Update, 
                                  context: ContextTypes.DEFAULT_TYPE,
                                  session_data: Optional[Dict[str, Any]] = None) -> VoiceTranscriptionResult:
        """Process voice message and return transcription result"""
        user_id = update.effective_user.id
        voice = update.message.voice
        
        logger.info("Processing voice message",
                   user_id=user_id,
                   duration=voice.duration,
                   file_size=voice.file_size,
                   mime_type=voice.mime_type)
        
        temp_files = []
        
        try:
            self.stats['messages_processed'] += 1
            
            # Show processing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
            
            # Get file object
            file = await context.bot.get_file(voice.file_id)
            
            # Download voice message
            downloaded_path = await self.audio_processor.download_voice_message(file, user_id)
            temp_files.append(downloaded_path)
            
            # Convert and optimize audio
            optimized_path, audio_metadata = await self.audio_processor.convert_and_optimize(downloaded_path)
            if optimized_path != downloaded_path:
                temp_files.append(optimized_path)
            
            # Add Telegram metadata
            audio_metadata.update({
                'telegram_duration': voice.duration,
                'telegram_file_size': voice.file_size,
                'telegram_mime_type': voice.mime_type
            })
            
            # Transcribe audio
            result = await self.assemblyai_client.transcribe_audio(optimized_path, audio_metadata)
            
            # Update statistics
            self.stats['total_audio_duration'] += result.duration_seconds
            self.stats['total_processing_time'] += result.processing_time_seconds
            
            if result.quality != VoiceQuality.FAILED:
                self.stats['successful_transcriptions'] += 1
                logger.info("Voice transcription successful",
                           user_id=user_id,
                           text_preview=result.text[:100] + "..." if len(result.text) > 100 else result.text,
                           confidence=result.confidence,
                           quality=result.quality.value)
            else:
                self.stats['failed_transcriptions'] += 1
                logger.warning("Voice transcription failed",
                              user_id=user_id,
                              error=result.error)
            
            return result
            
        except Exception as e:
            self.stats['failed_transcriptions'] += 1
            logger.error("Voice processing failed",
                        user_id=user_id,
                        error=str(e),
                        traceback=traceback.format_exc())
            
            return VoiceTranscriptionResult(
                text="",
                confidence=0.0,
                quality=VoiceQuality.FAILED,
                language=None,
                duration_seconds=voice.duration if voice else 0,
                processing_time_seconds=0,
                file_size_bytes=voice.file_size if voice else 0,
                format=voice.mime_type if voice else 'unknown',
                error=str(e)
            )
        
        finally:
            # Cleanup temporary files
            await self._cleanup_temp_files(temp_files)
    
    async def _cleanup_temp_files(self, file_paths: List[Path]):
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception as e:
                logger.warning("Failed to cleanup temp file",
                              path=str(file_path),
                              error=str(e))
    
    def format_transcription_response(self, result: VoiceTranscriptionResult) -> str:
        """Format transcription result for user response"""
        if result.quality == VoiceQuality.FAILED:
            if "too short" in (result.error or "").lower():
                return "🎤 Your voice message was too short. Please speak for at least 1 second and try again."
            elif "too large" in (result.error or "").lower():
                return "🎤 Your voice message is too large. Please keep messages under 10 minutes."
            elif "unsupported" in (result.error or "").lower():
                return "🎤 Sorry, I couldn't process your voice message format. Please try recording again."
            else:
                return "🎤 I couldn't process your voice message. Please try speaking more clearly or use text instead."
        
        # Success - add quality indicator
        quality_indicators = {
            VoiceQuality.HIGH: "🎤✨",
            VoiceQuality.MEDIUM: "🎤",
            VoiceQuality.LOW: "🎤⚠️"
        }
        
        indicator = quality_indicators.get(result.quality, "🎤")
        
        # Add confidence notice for low quality
        if result.quality == VoiceQuality.LOW:
            confidence_notice = f" *(Confidence: {result.confidence:.0%} - please verify)*"
        else:
            confidence_notice = ""
        
        return f"{indicator} **Voice Message Transcribed:**\n\n{result.text}{confidence_notice}"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = self.stats.copy()
        
        if stats['messages_processed'] > 0:
            stats['success_rate'] = stats['successful_transcriptions'] / stats['messages_processed']
            stats['avg_processing_time'] = stats['total_processing_time'] / stats['messages_processed']
            stats['avg_audio_duration'] = stats['total_audio_duration'] / stats['messages_processed']
        
        return stats
    
    async def cleanup_periodic(self):
        """Periodic cleanup of temporary files"""
        self.audio_processor.cleanup_temp_files(max_age_hours=24)

# Factory function for easy integration
def create_voice_handler(assemblyai_api_key: str, **kwargs) -> VoiceMessageHandler:
    """Create configured voice message handler"""
    config = VoiceProcessingConfig(
        assemblyai_api_key=assemblyai_api_key,
        **kwargs
    )
    return VoiceMessageHandler(config)

# Export public interface
__all__ = [
    'VoiceMessageHandler',
    'VoiceTranscriptionResult', 
    'VoiceQuality',
    'VoiceProcessingConfig',
    'create_voice_handler'
]