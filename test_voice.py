#!/usr/bin/env python3
"""
Quick test for voice transcription
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from mutagen import File as MutagenFile
from src.handlers.voice_handler import AssemblyAIClient, VoiceProcessingConfig

# Load environment variables
load_dotenv()


async def test_voice_transcription():
    """Test voice transcription with the provided OGG file"""
    
    # Path to test file
    test_file = Path("tests/audio_2025-09-09_12-16-25.ogg")
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"🎤 Testing voice transcription with: {test_file}")
    print(f"📁 File size: {test_file.stat().st_size} bytes")
    
    # Get audio duration using mutagen
    audio_file = MutagenFile(test_file)
    duration = audio_file.info.length if audio_file else 0
    print(f"⏱️  Audio duration: {duration}s")
    
    # Load configuration
    config = VoiceProcessingConfig(
        assemblyai_api_key=os.getenv('ASSEMBLYAI_API_KEY'),
        # Disable problematic features for now
        enable_topic_detection=False,
        enable_summarization=False,
        enable_auto_chapters=False,
        enable_content_safety=False,
        enable_iab_categories=False,
        enable_entity_detection=False,
        enable_sentiment_analysis=False
    )
    
    # Create transcription API
    transcription_api = AssemblyAIClient(config)
    
    try:
        print("🔄 Starting transcription...")
        metadata = {'duration': duration, 'format': 'ogg', 'size_bytes': test_file.stat().st_size}
        result = await transcription_api.transcribe_audio(test_file, metadata)
        
        print(f"✅ Transcription successful!")
        print(f"📝 Text: {result.text}")
        print(f"⏱️  Duration: {result.duration_seconds}s")
        print(f"🎯 Confidence: {result.confidence}")
        print(f"🌐 Language: {result.language}")
        
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_voice_transcription())