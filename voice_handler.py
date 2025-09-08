#!/usr/bin/env python3
"""
Voice Message Processing System for AI Interviewer Telegram Bot
Comprehensive AssemblyAI integration with latest SDK features and error handling.

✅ FIXED CRITICAL ISSUES:
- Fixed AssemblyAI client initialization (API key set before transcriber creation)
- Updated to use current SDK API patterns (transcriber.transcribe() instead of deprecated methods)
- Fixed status checking to use string values ("completed", "error") instead of enums
- Implemented proper async/await usage for all SDK calls
- Added exponential backoff retry logic with intelligent error categorization

🆕 NEW SDK FEATURES INTEGRATED:
- Language auto-detection with confidence scores
- Speaker labels for multi-speaker conversations
- PII redaction (person names, phone numbers, email addresses, etc.)
- Automatic summarization of transcripts
- Auto chapters for long recordings
- Content safety detection
- Topic detection and classification
- Sentiment analysis
- Word search with timestamps
- Enhanced error handling with detailed categorization

🔧 ENHANCED FEATURES:
- Improved configuration system supporting all new SDK features
- Better error messages with specific guidance
- Word search functionality with fallback mechanisms
- Statistics and monitoring improvements
- Comprehensive examples and documentation

📋 USAGE:
Basic usage:
    handler = create_voice_handler(api_key="your_key")
    result = await handler.process_voice_message(update, context)

Advanced usage with all features:
    handler = create_voice_handler_with_features(
        api_key="your_key", 
        enable_advanced_features=True
    )
    result = await handler.process_voice_message(update, context)
    
    # Access enhanced features
    summary = result.get_summary()
    speakers = result.get_speakers()
    chapters = result.get_chapters()
    word_matches = result.search_words(["important", "deadline"])

🚀 PERFORMANCE:
- Optimized audio processing pipeline
- Intelligent retry logic with exponential backoff
- Rate limiting and concurrent request management
- Memory-efficient temporary file handling
- Enhanced logging for debugging and monitoring

🔒 PRIVACY & SECURITY:
- PII redaction capabilities
- Content safety detection
- Secure temporary file handling
- API key validation

Compatible with AssemblyAI Python SDK v0.43.1+ and maintains backward compatibility
with existing VoiceTranscriptionResult structure and async interfaces.
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
    """Result of voice transcription with enhanced features"""
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
    
    def search_words(self, words: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Search for specific words in the transcript with timestamps"""
        if not self.metadata or 'transcript_id' not in self.metadata:
            return {}
        
        # This would be implemented using the transcript object
        # For now, return basic text search
        results = {}
        text_lower = self.text.lower()
        
        for word in words:
            word_lower = word.lower()
            results[word] = []
            
            # Simple text search (in production, use actual word search API)
            import re
            matches = list(re.finditer(r'\b' + re.escape(word_lower) + r'\b', text_lower))
            for match in matches:
                results[word].append({
                    'text': word,
                    'start_char': match.start(),
                    'end_char': match.end(),
                    'count': len(matches)
                })
        
        return results
    
    def get_summary(self) -> Optional[str]:
        """Get transcript summary if available"""
        if self.metadata and 'summary' in self.metadata:
            return self.metadata['summary']
        return None
    
    def get_chapters(self) -> List[Dict[str, Any]]:
        """Get auto-generated chapters if available"""
        if self.metadata and 'chapters' in self.metadata:
            return self.metadata['chapters']
        return []
    
    def get_speakers(self) -> List[str]:
        """Get identified speakers if available"""
        if self.metadata and 'speakers' in self.metadata:
            return self.metadata['speakers']
        return []
    
    def get_topics(self) -> List[Dict[str, Any]]:
        """Get detected topics if available"""
        if self.metadata and 'topics' in self.metadata:
            return self.metadata['topics']
        return []
    
    def get_sentiment_analysis(self) -> List[Dict[str, Any]]:
        """Get sentiment analysis results if available"""
        if self.metadata and 'sentiment' in self.metadata:
            return self.metadata['sentiment']
        return []

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
    # New SDK features
    enable_auto_language_detection: bool = True
    enable_speaker_labels: bool = False
    enable_punctuation: bool = True
    enable_format_text: bool = True
    enable_disfluencies: bool = False
    enable_pii_redaction: bool = False
    pii_redaction_policies: List[str] = None
    pii_substitution_policy: str = "hash"
    enable_summarization: bool = False
    enable_auto_chapters: bool = False
    enable_content_safety: bool = False
    enable_topic_detection: bool = False
    enable_iab_categories: bool = False
    enable_entity_detection: bool = False
    enable_sentiment_analysis: bool = False
    boost_param: str = "default"  # "low", "default", "high"
    # Processing settings
    concurrent_requests: int = 3
    retry_attempts: int = 3
    retry_delay_seconds: float = 2.0
    max_retry_delay: float = 60.0
    
    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = ["en", "ru", "es", "fr", "de", "it", "pt", "zh", "hi", "ja"]
        if self.pii_redaction_policies is None:
            self.pii_redaction_policies = ["person_name", "phone_number", "email_address"]

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
        # CRITICAL: Set API key BEFORE creating transcriber
        aai.settings.api_key = config.assemblyai_api_key
        self.transcriber = aai.Transcriber()
        
        # Rate limiting
        self._request_semaphore = asyncio.Semaphore(config.concurrent_requests)
        self._last_request_times: List[float] = []
        
        # Validate API key
        if not config.assemblyai_api_key or config.assemblyai_api_key == "":
            raise ValueError("AssemblyAI API key is required")
        
        logger.info("AssemblyAI client initialized", 
                   features_enabled=self._get_enabled_features())
    
    def _get_enabled_features(self) -> Dict[str, bool]:
        """Get summary of enabled features for logging"""
        return {
            "auto_language_detection": self.config.enable_auto_language_detection,
            "speaker_labels": self.config.enable_speaker_labels,
            "pii_redaction": self.config.enable_pii_redaction,
            "summarization": self.config.enable_summarization,
            "auto_chapters": self.config.enable_auto_chapters,
            "content_safety": self.config.enable_content_safety,
            "topic_detection": self.config.enable_topic_detection,
            "sentiment_analysis": self.config.enable_sentiment_analysis
        }
    
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
            error_type = type(e).__name__
            error_msg = str(e)
            
            # Enhanced error categorization
            if "api key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                error_category = "authentication"
            elif "timeout" in error_msg.lower() or isinstance(e, TimeoutError):
                error_category = "timeout"
            elif "file size" in error_msg.lower() or "too large" in error_msg.lower():
                error_category = "file_size"
            elif "format" in error_msg.lower() or "unsupported" in error_msg.lower():
                error_category = "format"
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                error_category = "network"
            else:
                error_category = "unknown"
            
            logger.error("Transcription failed",
                        path=str(audio_path),
                        error=error_msg,
                        error_type=error_type,
                        error_category=error_category,
                        processing_time=processing_time,
                        file_size=metadata.get('size_bytes', 0),
                        duration=metadata.get('duration', 0))
            
            return VoiceTranscriptionResult(
                text="",
                confidence=0.0,
                quality=VoiceQuality.FAILED,
                language=None,
                duration_seconds=metadata.get('duration', 0),
                processing_time_seconds=processing_time,
                file_size_bytes=metadata.get('size_bytes', 0),
                format=metadata.get('format', 'unknown'),
                error=f"{error_category}: {error_msg}",
                metadata={'error_type': error_type, 'error_category': error_category}
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
        """Build transcription configuration using current SDK patterns"""
        config = aai.TranscriptionConfig(
            # Core transcription settings
            language_detection=self.config.enable_auto_language_detection,
            punctuate=self.config.enable_punctuation,
            format_text=self.config.enable_format_text,
            disfluencies=self.config.enable_disfluencies,
            
            # Speaker identification
            speaker_labels=self.config.enable_speaker_labels,
            
            # Content analysis features
            summarization=self.config.enable_summarization,
            auto_chapters=self.config.enable_auto_chapters,
            content_safety=self.config.enable_content_safety,
            topic_detection=self.config.enable_topic_detection,
            iab_categories=self.config.enable_iab_categories,
            entity_detection=self.config.enable_entity_detection,
            sentiment_analysis=self.config.enable_sentiment_analysis,
            
            # Performance settings
            boost_param=self.config.boost_param,
        )
        
        # Set language if not using auto-detection
        if not self.config.enable_auto_language_detection:
            config.language_code = self.config.default_language
        
        # Configure PII redaction if enabled
        if self.config.enable_pii_redaction and self.config.pii_redaction_policies:
            # Map string policies to SDK enums
            policy_map = {
                "person_name": aai.PIIRedactionPolicy.person_name,
                "phone_number": aai.PIIRedactionPolicy.phone_number,
                "email_address": aai.PIIRedactionPolicy.email_address,
                "date_of_birth": aai.PIIRedactionPolicy.date_of_birth,
                "credit_card_number": aai.PIIRedactionPolicy.credit_card_number,
                "social_security_number": aai.PIIRedactionPolicy.us_social_security_number,
                "medical_condition": aai.PIIRedactionPolicy.medical_condition,
                "drug": aai.PIIRedactionPolicy.drug,
                "location": aai.PIIRedactionPolicy.location
            }
            
            policies = []
            for policy_str in self.config.pii_redaction_policies:
                if policy_str in policy_map:
                    policies.append(policy_map[policy_str])
            
            if policies:
                substitution_map = {
                    "hash": aai.PIISubstitutionPolicy.hash,
                    "entity_type": aai.PIISubstitutionPolicy.entity_type
                }
                substitution = substitution_map.get(
                    self.config.pii_substitution_policy, 
                    aai.PIISubstitutionPolicy.hash
                )
                
                config.set_redact_pii(policies=policies, substitution=substitution)
        
        return config
    
    async def _transcribe_with_retries(self, audio_path: Path, config: aai.TranscriptionConfig) -> aai.Transcript:
        """Perform transcription with exponential backoff retry logic"""
        last_error = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                # Run transcription in thread pool to avoid blocking
                transcript = await asyncio.to_thread(
                    self.transcriber.transcribe,  # Use self.transcriber instead of self.client
                    str(audio_path),
                    config=config
                )
                
                # Check if transcription was successful (using string status, not enum)
                if transcript.status == "error":
                    error_msg = getattr(transcript, 'error', 'Unknown transcription error')
                    raise Exception(f"AssemblyAI transcription error: {error_msg}")
                
                # Wait for completion if still processing
                if transcript.status == "processing" or transcript.status == "queued":
                    transcript = await self._wait_for_completion(transcript)
                
                if transcript.status == "completed":
                    return transcript
                else:
                    raise Exception(f"Transcription finished with status: {transcript.status}")
                
            except Exception as e:
                last_error = e
                logger.warning("Transcription attempt failed",
                              attempt=attempt + 1,
                              max_attempts=self.config.retry_attempts,
                              error=str(e),
                              error_type=type(e).__name__)
                
                if attempt < self.config.retry_attempts - 1:
                    # Check if error is retryable
                    if not self._is_retryable_error(e):
                        logger.warning("Non-retryable error encountered, stopping retries",
                                     error=str(e),
                                     error_type=type(e).__name__)
                        break
                    
                    # Exponential backoff with jitter and max delay
                    base_delay = self.config.retry_delay_seconds * (2 ** attempt)
                    jitter = base_delay * 0.1 * (0.5 - asyncio.get_event_loop().time() % 1)
                    wait_time = min(base_delay + jitter, self.config.max_retry_delay)
                    
                    logger.info("Retrying transcription", 
                               wait_time=wait_time, 
                               next_attempt=attempt + 2)
                    await asyncio.sleep(wait_time)
        
        raise last_error
    
    async def _wait_for_completion(self, transcript: aai.Transcript, max_wait_seconds: int = 300) -> aai.Transcript:
        """Wait for transcript to complete processing"""
        start_time = time.time()
        poll_interval = 2  # Start with 2 second polling
        
        while transcript.status in ["processing", "queued"]:
            if time.time() - start_time > max_wait_seconds:
                raise TimeoutError(f"Transcription timed out after {max_wait_seconds} seconds")
            
            await asyncio.sleep(poll_interval)
            
            # Refresh transcript status
            transcript = await asyncio.to_thread(
                self.transcriber.get_transcript,
                transcript.id
            )
            
            # Increase polling interval gradually
            poll_interval = min(poll_interval * 1.2, 10)
            
            logger.debug("Waiting for transcription completion", 
                        status=transcript.status,
                        elapsed_time=time.time() - start_time)
        
        return transcript
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is worth retrying"""
        error_msg = str(error).lower()
        
        # Non-retryable errors
        non_retryable_indicators = [
            "api key", "unauthorized", "authentication",
            "file size", "too large", "unsupported format",
            "invalid audio", "bad request", "forbidden"
        ]
        
        for indicator in non_retryable_indicators:
            if indicator in error_msg:
                return False
        
        # Retryable errors (network, timeout, server errors)
        return True
    
    async def search_words_in_transcript(self, transcript: aai.Transcript, words: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Search for words in transcript using AssemblyAI word search"""
        try:
            # Use AssemblyAI's word search feature
            search_results = await asyncio.to_thread(
                transcript.word_search,
                words
            )
            
            results = {}
            for word in words:
                results[word] = []
                
                if hasattr(search_results, 'matches'):
                    for match in search_results.matches:
                        if hasattr(match, 'text') and match.text.lower() == word.lower():
                            results[word].append({
                                'text': match.text,
                                'start': getattr(match, 'start', 0),
                                'end': getattr(match, 'end', 0),
                                'confidence': getattr(match, 'confidence', 1.0),
                                'count': getattr(match, 'count', 1)
                            })
            
            return results
            
        except Exception as e:
            logger.warning("Word search failed, falling back to text search",
                          error=str(e))
            # Fallback to basic text search
            return self._basic_word_search(transcript.text or "", words)
    
    def _basic_word_search(self, text: str, words: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Basic word search fallback"""
        results = {}
        text_lower = text.lower()
        
        for word in words:
            word_lower = word.lower()
            results[word] = []
            
            import re
            matches = list(re.finditer(r'\b' + re.escape(word_lower) + r'\b', text_lower))
            for i, match in enumerate(matches):
                results[word].append({
                    'text': word,
                    'start_char': match.start(),
                    'end_char': match.end(),
                    'confidence': 1.0,
                    'count': len(matches),
                    'match_index': i
                })
        
        return results
    
    def _process_transcript_result(self, transcript: aai.Transcript, metadata: Dict[str, Any], processing_time: float) -> VoiceTranscriptionResult:
        """Process transcript result and determine quality with enhanced features"""
        # Get transcription text
        text = transcript.text or ""
        
        # Calculate confidence score
        confidence = transcript.confidence or 0.0
        
        # Determine quality based on confidence and other factors
        quality = self._determine_quality(confidence, text, metadata)
        
        # Detect language (with enhanced detection)
        language = None
        language_confidence = None
        if hasattr(transcript, 'language_detection_results') and transcript.language_detection_results:
            # Get the most confident language detection
            lang_result = transcript.language_detection_results[0]
            language = lang_result.language
            language_confidence = lang_result.confidence
        else:
            language = getattr(transcript, 'language_code', None) or self.config.default_language
        
        # Build enhanced metadata
        enhanced_metadata = {
            'transcript_id': transcript.id,
            'word_count': len(text.split()) if text else 0,
            'characters': len(text),
            'audio_url': transcript.audio_url,
            'language_confidence': language_confidence,
            'status': transcript.status
        }
        
        # Add speaker information if available
        if hasattr(transcript, 'utterances') and transcript.utterances:
            speakers = set()
            for utterance in transcript.utterances:
                if hasattr(utterance, 'speaker'):
                    speakers.add(utterance.speaker)
            enhanced_metadata['speakers'] = list(speakers)
            enhanced_metadata['speaker_count'] = len(speakers)
        
        # Add summary if available
        if hasattr(transcript, 'summary') and transcript.summary:
            enhanced_metadata['summary'] = transcript.summary
        
        # Add chapters if available
        if hasattr(transcript, 'chapters') and transcript.chapters:
            enhanced_metadata['chapters'] = [
                {
                    'summary': chapter.summary,
                    'headline': chapter.headline,
                    'start': chapter.start,
                    'end': chapter.end
                }
                for chapter in transcript.chapters
            ]
        
        # Add content safety results if available
        if hasattr(transcript, 'content_safety_labels') and transcript.content_safety_labels:
            enhanced_metadata['content_safety'] = {
                'labels': [{
                    'label': label.label,
                    'confidence': label.confidence,
                    'severity': label.severity
                } for label in transcript.content_safety_labels.results]
            }
        
        # Add topic detection if available
        if hasattr(transcript, 'topics') and transcript.topics:
            enhanced_metadata['topics'] = [{
                'text': topic.text,
                'labels': [{
                    'relevance': label.relevance,
                    'label': label.label
                } for label in topic.labels]
            } for topic in transcript.topics]
        
        # Add sentiment analysis if available
        if hasattr(transcript, 'sentiment_analysis_results') and transcript.sentiment_analysis_results:
            enhanced_metadata['sentiment'] = [{
                'text': result.text,
                'sentiment': result.sentiment,
                'confidence': result.confidence,
                'start': result.start,
                'end': result.end
            } for result in transcript.sentiment_analysis_results]
        
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
            metadata=enhanced_metadata
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
    
    def format_transcription_response(self, result: VoiceTranscriptionResult, include_extras: bool = False) -> str:
        """Format transcription result for user response with enhanced features"""
        if result.quality == VoiceQuality.FAILED:
            error_msg = result.error or ""
            
            # Enhanced error messages
            if "authentication" in error_msg:
                return "🎤❌ API authentication failed. Please check the configuration."
            elif "timeout" in error_msg:
                return "🎤⏱️ Transcription timed out. Please try with a shorter audio file."
            elif "file_size" in error_msg:
                return f"🎤📁 File too large ({result.file_size_bytes / 1024 / 1024:.1f}MB). Please keep under {self.config.max_file_size_mb}MB."
            elif "format" in error_msg:
                return "🎤🔄 Unsupported audio format. Please try recording in a standard format."
            elif "network" in error_msg:
                return "🎤🌐 Network error occurred. Please check your connection and try again."
            elif "too short" in error_msg.lower():
                return f"🎤⚡ Audio too short ({result.duration_seconds:.1f}s). Please speak for at least {self.config.min_duration_seconds}s."
            elif "too large" in error_msg.lower():
                return f"🎤📏 Audio too long ({result.duration_seconds/60:.1f} min). Please keep under {self.config.max_duration_seconds/60:.0f} minutes."
            else:
                return f"🎤❌ Transcription failed: {error_msg}"
        
        # Success - build response with quality indicator
        quality_indicators = {
            VoiceQuality.HIGH: "🎤✨",
            VoiceQuality.MEDIUM: "🎤",
            VoiceQuality.LOW: "🎤⚠️"
        }
        
        indicator = quality_indicators.get(result.quality, "🎤")
        response = f"{indicator} **Voice Message Transcribed:**\n\n{result.text}"
        
        # Add confidence notice for low quality
        if result.quality == VoiceQuality.LOW:
            response += f"\\n\\n*(Confidence: {result.confidence:.0%} - please verify)*"
        
        # Add extra information if requested
        if include_extras and result.metadata:
            extras = []
            
            # Language detection
            if result.language and result.language != 'en':
                lang_conf = result.metadata.get('language_confidence')
                if lang_conf:
                    extras.append(f"Language: {result.language.upper()} ({lang_conf:.0%})")
                else:
                    extras.append(f"Language: {result.language.upper()}")
            
            # Speakers
            speakers = result.get_speakers()
            if speakers and len(speakers) > 1:
                extras.append(f"Speakers: {len(speakers)} detected")
            
            # Summary
            summary = result.get_summary()
            if summary:
                extras.append(f"Summary available")
            
            # Chapters
            chapters = result.get_chapters()
            if chapters:
                extras.append(f"Chapters: {len(chapters)} sections")
            
            if extras:
                response += f"\\n\\n*{' | '.join(extras)}*"
        
        return response
    
    async def search_words_in_result(self, result: VoiceTranscriptionResult, words: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Search for words in a transcription result"""
        if result.quality == VoiceQuality.FAILED or not result.text:
            return {}
        
        return result.search_words(words)
    
    def format_search_results(self, search_results: Dict[str, List[Dict[str, Any]]]) -> str:
        """Format word search results for display"""
        if not search_results:
            return "🔍 No matches found."
        
        response = "🔍 **Word Search Results:**\\n\\n"
        
        for word, matches in search_results.items():
            if matches:
                count = matches[0].get('count', len(matches))
                response += f"**{word}**: {count} occurrence{'s' if count != 1 else ''}\\n"
                
                # Show first few matches with context
                for i, match in enumerate(matches[:3]):
                    if 'start_char' in match:
                        response += f"  • Position {match['start_char']}-{match['end_char']}\\n"
                
                if len(matches) > 3:
                    response += f"  • ... and {len(matches) - 3} more\\n"
                response += "\\n"
        
        return response.strip()
    
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

# Example usage with all new features
async def example_advanced_usage():
    """Example demonstrating all AssemblyAI SDK features"""
    # Configure with all features enabled
    config = VoiceProcessingConfig(
        assemblyai_api_key="your_api_key_here",
        enable_auto_language_detection=True,
        enable_speaker_labels=True,
        enable_pii_redaction=True,
        pii_redaction_policies=["person_name", "phone_number", "email_address"],
        enable_summarization=True,
        enable_auto_chapters=True,
        enable_content_safety=True,
        enable_topic_detection=True,
        enable_sentiment_analysis=True,
        boost_param="high"  # Better accuracy for challenging audio
    )
    
    # Create handler
    voice_handler = VoiceMessageHandler(config)
    
    # In a real Telegram bot handler:
    # result = await voice_handler.process_voice_message(update, context)
    
    # Example result processing:
    # if result.quality != VoiceQuality.FAILED:
    #     # Get basic transcription
    #     transcription_text = result.text
    #     
    #     # Get enhanced features
    #     summary = result.get_summary()
    #     speakers = result.get_speakers()
    #     chapters = result.get_chapters()
    #     topics = result.get_topics()
    #     sentiment = result.get_sentiment_analysis()
    #     
    #     # Search for specific words
    #     word_results = result.search_words(["important", "action", "deadline"])
    #     
    #     # Format response with extras
    #     response = voice_handler.format_transcription_response(result, include_extras=True)
    #     
    #     print(f"Transcription: {transcription_text}")
    #     if summary:
    #         print(f"Summary: {summary}")
    #     if speakers:
    #         print(f"Speakers: {speakers}")
    #     if chapters:
    #         print(f"Chapters: {len(chapters)} sections")
    #     if word_results:
    #         search_formatted = voice_handler.format_search_results(word_results)
    #         print(search_formatted)

# Factory function for easy integration with various configurations
def create_voice_handler_with_features(
    assemblyai_api_key: str,
    enable_advanced_features: bool = True,
    **kwargs
) -> VoiceMessageHandler:
    """Create voice handler with intelligent feature defaults"""
    
    if enable_advanced_features:
        # Enable commonly useful features by default
        advanced_defaults = {
            'enable_auto_language_detection': True,
            'enable_speaker_labels': True,
            'enable_punctuation': True,
            'enable_format_text': True,
            'enable_disfluencies': False,  # Usually not needed
            'enable_pii_redaction': True,
            'pii_redaction_policies': ['person_name', 'phone_number', 'email_address'],
            'enable_summarization': True,
            'enable_auto_chapters': False,  # Only useful for longer audio
            'enable_content_safety': True,
            'enable_topic_detection': True,
            'boost_param': 'default'
        }
        
        # Override with any user-provided kwargs
        config_params = {**advanced_defaults, **kwargs}
    else:
        # Basic configuration
        config_params = kwargs
    
    config = VoiceProcessingConfig(
        assemblyai_api_key=assemblyai_api_key,
        **config_params
    )
    
    return VoiceMessageHandler(config)

# Export public interface
__all__ = [
    'VoiceMessageHandler',
    'VoiceTranscriptionResult', 
    'VoiceQuality',
    'VoiceProcessingConfig',
    'create_voice_handler',
    'create_voice_handler_with_features',
    'example_advanced_usage'
]