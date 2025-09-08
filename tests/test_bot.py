#!/usr/bin/env python3
"""
Test script for AI Interviewer Telegram Bot
Validates configuration, API connectivity, and basic functionality
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.core.config import config
    from src.core.telegram_bot import PromptManager, ClaudeIntegration, InterviewSession, PromptVariant, InterviewStage
    import anthropic
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you have installed all dependencies: pip install -r requirements.txt")
    sys.exit(1)

class BotTester:
    """Test suite for the AI Interviewer Bot"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and record results"""
        print(f"🧪 Testing: {test_name}")
        try:
            result = test_func()
            if asyncio.iscoroutine(result):
                result = asyncio.run(result)
            
            if result:
                print(f"✅ PASS: {test_name}")
                self.tests_passed += 1
                self.test_results.append({"test": test_name, "status": "PASS", "error": None})
            else:
                print(f"❌ FAIL: {test_name}")
                self.tests_failed += 1
                self.test_results.append({"test": test_name, "status": "FAIL", "error": "Test returned False"})
        
        except Exception as e:
            print(f"❌ ERROR: {test_name} - {str(e)}")
            self.tests_failed += 1
            self.test_results.append({"test": test_name, "status": "ERROR", "error": str(e)})
    
    def test_environment_variables(self):
        """Test that required environment variables are set"""
        required_vars = ['TELEGRAM_BOT_TOKEN', 'ANTHROPIC_API_KEY']
        
        for var in required_vars:
            if not os.getenv(var):
                print(f"   ❌ Missing environment variable: {var}")
                return False
        
        print(f"   ✅ All required environment variables present")
        return True
    
    def test_config_loading(self):
        """Test configuration loading"""
        try:
            # Test that config loads without errors
            test_config = config
            
            # Validate required fields
            if not test_config.telegram_token:
                print("   ❌ Telegram token not loaded")
                return False
                
            if not test_config.anthropic_api_key:
                print("   ❌ Anthropic API key not loaded")
                return False
            
            print(f"   ✅ Configuration loaded successfully")
            print(f"      - Bot name: {test_config.bot_name}")
            print(f"      - Claude model: {test_config.claude_model}")
            print(f"      - Session timeout: {test_config.session_timeout_minutes} minutes")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Config loading failed: {e}")
            return False
    
    def test_prompt_loading(self):
        """Test that all prompt files can be loaded"""
        try:
            prompt_manager = PromptManager()
            
            # Check all variants
            for variant in PromptVariant:
                prompt = prompt_manager.get_prompt(variant)
                if not prompt or len(prompt) < 100:  # Basic sanity check
                    print(f"   ❌ Prompt variant {variant.value} failed to load or too short")
                    return False
                
                description = prompt_manager.get_variant_description(variant)
                print(f"      - {variant.value}: {description[:50]}...")
            
            print(f"   ✅ All {len(PromptVariant)} prompt variants loaded successfully")
            return True
            
        except Exception as e:
            print(f"   ❌ Prompt loading failed: {e}")
            return False
    
    async def test_claude_connection(self):
        """Test Claude API connectivity"""
        try:
            claude = ClaudeIntegration(config.anthropic_api_key)
            
            # Create a minimal test session
            test_session = InterviewSession(
                user_id=12345,
                username="test_user",
                prompt_variant=PromptVariant.CONVERSATIONAL,
                current_stage=InterviewStage.GREETING,
                stage_completeness={},
                conversation_history=[],
                start_time=datetime.now(),
                last_activity=datetime.now()
            )
            
            # Test API call with a simple message
            response = await claude.generate_interview_response(
                test_session,
                "Hello, I'm ready to start the interview",
                PromptManager()
            )
            
            # Validate response structure
            if not isinstance(response, dict):
                print("   ❌ Response is not a dictionary")
                return False
            
            required_fields = ['interview_stage', 'response', 'metadata']
            for field in required_fields:
                if field not in response:
                    print(f"   ❌ Missing field in response: {field}")
                    return False
            
            print(f"   ✅ Claude API connection successful")
            print(f"      - Model: {config.claude_model}")
            print(f"      - Response length: {len(response['response'])} characters")
            print(f"      - Stage: {response['interview_stage']}")
            
            return True
            
        except anthropic.APIConnectionError as e:
            print(f"   ❌ Claude API connection failed: {e}")
            return False
        except anthropic.AuthenticationError as e:
            print(f"   ❌ Claude API authentication failed: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Claude API test failed: {e}")
            return False
    
    def test_session_management(self):
        """Test session creation and management"""
        try:
            # Create test session
            session = InterviewSession(
                user_id=12345,
                username="test_user",
                prompt_variant=PromptVariant.MASTER,
                current_stage=InterviewStage.GREETING,
                stage_completeness={stage.value: 0 for stage in InterviewStage},
                conversation_history=[],
                start_time=datetime.now(),
                last_activity=datetime.now()
            )
            
            # Test message adding
            session.add_message("user", "Hello")
            session.add_message("assistant", "Hi there!", {"depth": 1})
            
            if len(session.conversation_history) != 2:
                print("   ❌ Message adding failed")
                return False
            
            # Test stage completeness
            if len(session.stage_completeness) != len(InterviewStage):
                print("   ❌ Stage completeness initialization failed")
                return False
            
            print(f"   ✅ Session management working correctly")
            print(f"      - Messages: {len(session.conversation_history)}")
            print(f"      - Stages tracked: {len(session.stage_completeness)}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Session management test failed: {e}")
            return False
    
    def test_json_parsing(self):
        """Test JSON response parsing"""
        try:
            claude = ClaudeIntegration(config.anthropic_api_key)
            
            # Test valid JSON
            valid_json = '''
            {
                "interview_stage": "greeting",
                "response": "Hello! Ready to start?",
                "metadata": {
                    "question_depth": 1,
                    "completeness": 10,
                    "engagement_level": "medium"
                }
            }
            '''
            
            parsed = claude._parse_json_response(valid_json)
            if not all(key in parsed for key in ['interview_stage', 'response', 'metadata']):
                print("   ❌ Valid JSON parsing failed")
                return False
            
            # Test malformed JSON
            malformed_json = "This is not JSON at all"
            parsed_malformed = claude._parse_json_response(malformed_json)
            if 'error' not in parsed_malformed:
                print("   ❌ Malformed JSON should have error field")
                return False
            
            print(f"   ✅ JSON parsing working correctly")
            print(f"      - Valid JSON parsed successfully")
            print(f"      - Malformed JSON handled gracefully")
            
            return True
            
        except Exception as e:
            print(f"   ❌ JSON parsing test failed: {e}")
            return False
    
    def test_file_structure(self):
        """Test that all required files are present"""
        required_files = [
            'telegram_bot.py',
            'bot_enhanced.py',
            'config.py',
            'requirements.txt',
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
    
    def test_directories(self):
        """Test directory creation"""
        required_dirs = ['sessions', 'completed_sessions']
        
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
        
        print(f"   ✅ All required directories ready")
        return True
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting AI Interviewer Bot Tests")
        print("=" * 50)
        
        # Run all tests
        self.run_test("Environment Variables", self.test_environment_variables)
        self.run_test("Configuration Loading", self.test_config_loading)
        self.run_test("File Structure", self.test_file_structure)
        self.run_test("Directory Structure", self.test_directories)
        self.run_test("Prompt Loading", self.test_prompt_loading)
        self.run_test("Session Management", self.test_session_management)
        self.run_test("JSON Parsing", self.test_json_parsing)
        self.run_test("Claude API Connection", self.test_claude_connection)
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"🧪 Test Results Summary")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"📊 Total: {self.tests_passed + self.tests_failed}")
        
        if self.tests_failed == 0:
            print("\n🎉 All tests passed! Bot is ready to deploy.")
            return True
        else:
            print(f"\n⚠️  {self.tests_failed} test(s) failed. Please fix issues before deployment.")
            return False
    
    def save_test_report(self):
        """Save test results to file"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "results": self.test_results
        }
        
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Test report saved to: test_report.json")

def main():
    """Main test function"""
    print("AI Interviewer Telegram Bot - Test Suite")
    print("========================================")
    
    # Check if .env file exists
    if not Path('.env').exists() and not all(os.getenv(var) for var in ['TELEGRAM_BOT_TOKEN', 'ANTHROPIC_API_KEY']):
        print("\n⚠️  Warning: No .env file found and required environment variables not set.")
        print("Please create .env file from .env.example and add your API keys.")
        print("\nYou can still run basic tests without API keys...")
        
        response = input("\nContinue with limited tests? (y/N): ")
        if response.lower() != 'y':
            print("Exiting. Please setup environment first.")
            return 1
    
    # Run tests
    tester = BotTester()
    success = tester.run_all_tests()
    tester.save_test_report()
    
    return 0 if success else 1

if __name__ == '__main__':
    exit(main())