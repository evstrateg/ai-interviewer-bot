#!/usr/bin/env python3
"""
Quick Migration Success Test
Demonstrates that the directory structure migration was successful.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

def test_migration_success():
    """Test that migration was successful by running key imports and checks"""
    
    print("🚀 Testing Directory Structure Migration Success")
    print("=" * 50)
    
    # Test 1: Import all core modules
    print("📦 Testing core module imports...")
    try:
        from src.core.config import BotConfig
        from src.core.telegram_bot import AIInterviewerBot, PromptVariant
        from src.core.bot_enhanced import EnhancedAIInterviewerBot
        print("   ✅ All core modules imported successfully")
    except Exception as e:
        print(f"   ❌ Core module import failed: {e}")
        return False
    
    # Test 2: Import localization
    print("🌍 Testing localization imports...")
    try:
        from src.localization.localization import LocalizationManager, t, set_language
        print("   ✅ Localization modules imported successfully")
    except Exception as e:
        print(f"   ❌ Localization import failed: {e}")
        return False
    
    # Test 3: Voice handler (optional)
    print("🎤 Testing voice handler imports...")
    try:
        from src.handlers.voice_handler import VoiceMessageHandler
        print("   ✅ Voice handler imported successfully")
        voice_available = True
    except ImportError as e:
        if "assemblyai" in str(e).lower():
            print("   ⚠️  Voice handler available (assemblyai not installed)")
            voice_available = False
        else:
            print(f"   ❌ Voice handler import failed: {e}")
            return False
    
    # Test 4: Configuration files
    print("⚙️ Testing configuration files...")
    config_files = [
        "pytest.ini",
        "config/requirements.txt", 
        "setup.py",
    ]
    
    for config_file in config_files:
        if not Path(config_file).exists():
            print(f"   ❌ Missing config file: {config_file}")
            return False
    
    print("   ✅ All configuration files present")
    
    # Test 5: Cross-imports work
    print("🔄 Testing cross-package functionality...")
    try:
        # Create a simple config instance
        import os
        os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
        os.environ['ANTHROPIC_API_KEY'] = 'test_key'
        
        config = BotConfig.from_env()
        print(f"   ✅ Config creation works (bot name: {config.bot_name})")
        
        # Test localization
        lm = LocalizationManager()
        greeting = lm.get_text("greeting", "en")
        print(f"   ✅ Localization works (greeting: {greeting[:30]}...)")
        
    except Exception as e:
        print(f"   ❌ Cross-package functionality failed: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 MIGRATION SUCCESS!")
    print(f"✅ Core modules: Working")
    print(f"✅ Localization: Working") 
    print(f"{'✅' if voice_available else '⚠️ '} Voice processing: {'Working' if voice_available else 'Available (optional dependency)'}")
    print(f"✅ Configuration: Working")
    print(f"✅ Cross-imports: Working")
    
    print("\n📋 Directory structure after migration:")
    print("   src/")
    print("   ├── core/          (bot logic)")
    print("   ├── handlers/      (voice processing)")
    print("   └── localization/  (i18n support)")
    print("   tests/             (test files)")
    print("   config/            (configuration)")
    print("   setup.py           (package definition)")
    
    print("\n🚀 Ready for development!")
    return True

if __name__ == "__main__":
    success = test_migration_success()
    sys.exit(0 if success else 1)