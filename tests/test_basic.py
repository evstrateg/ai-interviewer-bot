#!/usr/bin/env python3
"""
Basic test script for AI Interviewer Telegram Bot
Tests core functionality without external dependencies
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

def test_environment_variables():
    """Test that required environment variables are set"""
    print("🧪 Testing: Environment Variables")
    
    required_vars = ['TELEGRAM_BOT_TOKEN', 'ANTHROPIC_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"   ❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("   ✅ All required environment variables present")
    return True

def test_file_structure():
    """Test that all required files are present"""
    print("🧪 Testing: File Structure")
    
    required_files = [
        'src/core/telegram_bot.py',
        'src/core/bot_enhanced.py', 
        'src/core/config.py',
        'config/requirements.txt',
        'prompt_v1_master_interviewer.md',
        'prompt_v2_telegram_optimized.md',
        'prompt_v3_conversational_balanced.md',
        'prompt_v4_stage_specific.md',
        'prompt_v5_conversation_management.md',
        'json_response_specifications.md',
        '.env.example'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"   ❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print(f"   ✅ All required files present ({len(required_files)} files)")
    return True

def test_prompt_files():
    """Test that prompt files contain valid content"""
    print("🧪 Testing: Prompt Files Content")
    
    prompt_files = [
        'prompt_v1_master_interviewer.md',
        'prompt_v2_telegram_optimized.md', 
        'prompt_v3_conversational_balanced.md',
        'prompt_v4_stage_specific.md',
        'prompt_v5_conversation_management.md'
    ]
    
    for file in prompt_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content) < 500:  # Basic length check
                print(f"   ❌ Prompt file {file} seems too short")
                return False
            
            # Check for key elements
            key_elements = ['interview', 'stage', 'question', 'response']
            missing_elements = []
            for element in key_elements:
                if element.lower() not in content.lower():
                    missing_elements.append(element)
            
            if missing_elements:
                print(f"   ⚠️  Prompt file {file} missing elements: {', '.join(missing_elements)}")
            
        except Exception as e:
            print(f"   ❌ Error reading {file}: {e}")
            return False
    
    print(f"   ✅ All prompt files contain valid content")
    return True

def test_json_specifications():
    """Test JSON response specifications"""
    print("🧪 Testing: JSON Response Specifications")
    
    try:
        with open('json_response_specifications.md', 'r') as f:
            content = f.read()
        
        # Check for required JSON structure elements
        required_elements = [
            'interview_stage',
            'response', 
            'metadata',
            'question_depth',
            'completeness',
            'engagement_level'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"   ❌ JSON spec missing elements: {', '.join(missing_elements)}")
            return False
        
        print("   ✅ JSON response specifications are complete")
        return True
        
    except Exception as e:
        print(f"   ❌ Error reading JSON specifications: {e}")
        return False

def test_env_file():
    """Test .env file existence and basic structure"""
    print("🧪 Testing: Environment File")
    
    if not Path('.env').exists():
        print("   ⚠️  .env file not found - using environment variables")
        return test_environment_variables()
    
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
        
        # Check for required keys (even if values are placeholders)
        required_keys = ['TELEGRAM_BOT_TOKEN', 'ANTHROPIC_API_KEY']
        found_keys = []
        
        for key in required_keys:
            if key in env_content:
                found_keys.append(key)
        
        if len(found_keys) != len(required_keys):
            missing = [k for k in required_keys if k not in found_keys]
            print(f"   ❌ .env file missing keys: {', '.join(missing)}")
            return False
        
        print("   ✅ .env file structure is correct")
        return True
        
    except Exception as e:
        print(f"   ❌ Error reading .env file: {e}")
        return False

def test_python_syntax():
    """Test that Python files have valid syntax"""
    print("🧪 Testing: Python Syntax")
    
    python_files = ['src/core/telegram_bot.py', 'src/core/bot_enhanced.py', 'src/core/config.py']
    
    for file in python_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic syntax check by compiling
            compile(content, file, 'exec')
            print(f"      - {file}: ✅ Valid syntax")
            
        except SyntaxError as e:
            print(f"   ❌ Syntax error in {file}: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Error checking {file}: {e}")
            return False
    
    print("   ✅ All Python files have valid syntax")
    return True

def test_directories():
    """Test directory structure"""
    print("🧪 Testing: Directory Structure")
    
    # Create required directories if they don't exist
    required_dirs = ['sessions', 'completed_sessions', 'logs']
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            try:
                dir_path.mkdir(exist_ok=True)
                print(f"      - Created directory: {dir_name}")
            except Exception as e:
                print(f"   ❌ Failed to create directory {dir_name}: {e}")
                return False
        else:
            print(f"      - Directory exists: {dir_name}")
    
    print("   ✅ All required directories ready")
    return True

def test_docker_files():
    """Test Docker configuration files"""
    print("🧪 Testing: Docker Configuration")
    
    docker_files = ['Dockerfile', 'docker-compose.yml']
    
    for file in docker_files:
        if not Path(file).exists():
            print(f"   ❌ Missing Docker file: {file}")
            return False
        
        try:
            with open(file, 'r') as f:
                content = f.read()
            
            if len(content) < 100:  # Basic sanity check
                print(f"   ❌ Docker file {file} seems incomplete")
                return False
                
            print(f"      - {file}: ✅ Present and non-empty")
            
        except Exception as e:
            print(f"   ❌ Error reading {file}: {e}")
            return False
    
    print("   ✅ Docker configuration files are present")
    return True

def main():
    """Run all basic tests"""
    print("🚀 AI Interviewer Bot - Basic Tests")
    print("=" * 40)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Environment File", test_env_file),  
        ("Python Syntax", test_python_syntax),
        ("Prompt Files Content", test_prompt_files),
        ("JSON Specifications", test_json_specifications),
        ("Directory Structure", test_directories),
        ("Docker Configuration", test_docker_files),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            failed += 1
        
        print()  # Empty line between tests
    
    # Summary
    print("=" * 40)
    print(f"🧪 Basic Test Results")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All basic tests passed! System structure is valid.")
        print("\n📝 Next steps:")
        print("   1. Install Python dependencies: pip install -r requirements.txt")
        print("   2. Run full tests: ./run.sh test")
        print("   3. Start the bot: ./run.sh run-enhanced")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please fix issues before deployment.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)