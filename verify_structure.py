#!/usr/bin/env python3
"""
Directory Structure Verification Script

This script verifies that the new directory structure works correctly after migration.
It tests all imports, configurations, and package structure without requiring external dependencies.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path
from typing import List, Tuple, Optional

class StructureVerifier:
    """Comprehensive structure verification"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.src_dir = self.project_root / "src"
        self.tests_dir = self.project_root / "tests"
        self.config_dir = self.project_root / "config"
        
        # Add src to Python path for imports
        if str(self.src_dir) not in sys.path:
            sys.path.insert(0, str(self.src_dir))
    
    def run_test(self, test_name: str, test_func) -> Tuple[bool, Optional[str]]:
        """Run a test and return result"""
        try:
            result = test_func()
            if isinstance(result, tuple):
                success, message = result
            else:
                success, message = result, None
            return success, message
        except Exception as e:
            return False, str(e)
    
    def test_directory_structure(self) -> bool:
        """Test that all expected directories exist"""
        print("🧪 Testing directory structure...")
        
        expected_dirs = [
            "src",
            "src/core",
            "src/handlers", 
            "src/localization",
            "tests",
            "config"
        ]
        
        missing = []
        for dir_path in expected_dirs:
            if not (self.project_root / dir_path).exists():
                missing.append(dir_path)
        
        if missing:
            print(f"   ❌ Missing directories: {', '.join(missing)}")
            return False
        
        print("   ✅ All expected directories exist")
        return True
    
    def test_python_files_exist(self) -> bool:
        """Test that all expected Python files exist"""
        print("🧪 Testing Python files existence...")
        
        expected_files = [
            "src/__init__.py",
            "src/core/__init__.py", 
            "src/core/config.py",
            "src/core/telegram_bot.py",
            "src/core/bot_enhanced.py",
            "src/handlers/__init__.py",
            "src/handlers/voice_handler.py",
            "src/localization/__init__.py",
            "src/localization/localization.py",
            "tests/__init__.py",
            "tests/test_basic.py",
            "tests/conftest.py",
            "tests/run_tests.py",
            "localization_integration_example.py",
            "setup.py"
        ]
        
        missing = []
        for file_path in expected_files:
            if not (self.project_root / file_path).exists():
                missing.append(file_path)
        
        if missing:
            print(f"   ❌ Missing Python files: {', '.join(missing)}")
            return False
        
        print(f"   ✅ All expected Python files exist ({len(expected_files)} files)")
        return True
    
    def test_config_files(self) -> bool:
        """Test configuration files"""
        print("🧪 Testing configuration files...")
        
        config_files = [
            ("pytest.ini", ["testpaths", "pythonpath"]),
            ("config/requirements.txt", ["telegram", "anthropic"]),
            ("setup.py", ["setup(", "find_packages"])
        ]
        
        for file_path, required_content in config_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                print(f"   ❌ Missing config file: {file_path}")
                return False
            
            try:
                content = full_path.read_text()
                missing_content = []
                for required in required_content:
                    if required not in content:
                        missing_content.append(required)
                
                if missing_content:
                    print(f"   ❌ {file_path} missing content: {', '.join(missing_content)}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error reading {file_path}: {e}")
                return False
        
        print("   ✅ All configuration files valid")
        return True
    
    def test_basic_imports(self) -> bool:
        """Test basic module imports"""
        print("🧪 Testing basic imports...")
        
        import_tests = [
            ("src.core.config", "config"),
            ("src.core.telegram_bot", "AIInterviewerBot"),
            ("src.core.bot_enhanced", "EnhancedAIInterviewerBot"),
            ("src.localization.localization", "LocalizationManager"),
        ]
        
        failed = []
        for module_name, attribute in import_tests:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, attribute):
                    print(f"      - {module_name}.{attribute}: ✅")
                else:
                    print(f"      - {module_name}.{attribute}: ❌ (missing attribute)")
                    failed.append(f"{module_name}.{attribute}")
            except ImportError as e:
                if "assemblyai" in str(e).lower():
                    print(f"      - {module_name}.{attribute}: ⚠️  (optional dependency missing)")
                else:
                    print(f"      - {module_name}.{attribute}: ❌ ({e})")
                    failed.append(f"{module_name}.{attribute}")
            except Exception as e:
                print(f"      - {module_name}.{attribute}: ❌ ({e})")
                failed.append(f"{module_name}.{attribute}")
        
        if failed:
            print(f"   ❌ Failed imports: {', '.join(failed)}")
            return False
        
        print("   ✅ All basic imports successful")
        return True
    
    def test_voice_handler_import(self) -> bool:
        """Test voice handler import (with optional dependency handling)"""
        print("🧪 Testing voice handler import...")
        
        try:
            from src.handlers.voice_handler import VoiceMessageHandler
            print("   ✅ Voice handler imports successfully (with assemblyai)")
            return True
        except ImportError as e:
            if "assemblyai" in str(e).lower():
                print("   ⚠️  Voice handler import requires assemblyai (expected for testing)")
                # Try to import the module without assemblyai-dependent parts
                try:
                    spec = importlib.util.spec_from_file_location(
                        "voice_handler_test", 
                        self.src_dir / "handlers" / "voice_handler.py"
                    )
                    # Just check if the file syntax is valid
                    with open(self.src_dir / "handlers" / "voice_handler.py", "r") as f:
                        content = f.read()
                        compile(content, "voice_handler.py", "exec")
                    print("   ✅ Voice handler syntax valid (assemblyai dependency expected)")
                    return True
                except Exception as syntax_error:
                    print(f"   ❌ Voice handler syntax error: {syntax_error}")
                    return False
            else:
                print(f"   ❌ Voice handler import failed: {e}")
                return False
        except Exception as e:
            print(f"   ❌ Voice handler import failed: {e}")
            return False
    
    def test_cross_imports(self) -> bool:
        """Test cross-package imports"""
        print("🧪 Testing cross-package imports...")
        
        try:
            # Test telegram_bot importing voice_handler 
            from src.core import telegram_bot
            has_voice = hasattr(telegram_bot, 'VOICE_PROCESSING_AVAILABLE')
            print(f"      - telegram_bot -> voice_handler: ✅ (available: {getattr(telegram_bot, 'VOICE_PROCESSING_AVAILABLE', False)})")
            
            # Test enhanced bot importing telegram bot
            from src.core.bot_enhanced import EnhancedAIInterviewerBot
            from src.core.telegram_bot import AIInterviewerBot
            print("      - bot_enhanced -> telegram_bot: ✅")
            
            # Test localization standalone
            from src.localization.localization import LocalizationManager
            print("      - localization standalone: ✅")
            
            print("   ✅ All cross-package imports successful")
            return True
            
        except Exception as e:
            print(f"   ❌ Cross-import failed: {e}")
            return False
    
    def test_package_installation(self) -> bool:
        """Test package installation readiness"""
        print("🧪 Testing package installation readiness...")
        
        try:
            # Test setup.py validation
            result = subprocess.run(
                [sys.executable, "setup.py", "check"], 
                capture_output=True, text=True, timeout=30,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print("   ✅ setup.py validation passed")
            else:
                print(f"   ❌ setup.py validation failed: {result.stderr}")
                return False
                
            # Test find_packages discovery
            try:
                from setuptools import find_packages
                packages = find_packages(where="src")
                expected_packages = ['core', 'handlers', 'localization']
                
                missing = [pkg for pkg in expected_packages if pkg not in packages]
                if missing:
                    print(f"   ❌ Missing packages in discovery: {missing}")
                    return False
                
                print(f"   ✅ Package discovery found: {packages}")
                return True
                
            except Exception as e:
                print(f"   ❌ Package discovery failed: {e}")
                return False
                
        except Exception as e:
            print(f"   ❌ Installation test failed: {e}")
            return False
    
    def test_pytest_configuration(self) -> bool:
        """Test pytest configuration"""
        print("🧪 Testing pytest configuration...")
        
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(self.project_root / "pytest.ini")
            
            # Check key settings
            tool_pytest = config["tool:pytest"]
            coverage_run = config["coverage:run"]
            
            if tool_pytest["testpaths"] != "tests":
                print("   ❌ pytest testpaths not set to 'tests'")
                return False
            
            if "src" not in tool_pytest["pythonpath"]:
                print("   ❌ pytest pythonpath doesn't include 'src'")
                return False
            
            if coverage_run["source"] != "src":
                print("   ❌ coverage source not set to 'src'")
                return False
            
            print("   ✅ pytest configuration valid")
            return True
            
        except Exception as e:
            print(f"   ❌ pytest configuration test failed: {e}")
            return False
    
    def test_example_scripts(self) -> bool:
        """Test example scripts can run"""
        print("🧪 Testing example scripts...")
        
        try:
            # Test localization example
            result = subprocess.run(
                [sys.executable, "localization_integration_example.py"],
                capture_output=True, text=True, timeout=10,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print("   ✅ localization_integration_example.py runs successfully")
            else:
                print(f"   ❌ localization example failed: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"   ❌ Example script test failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all verification tests"""
        print("🚀 Directory Structure Migration Verification")
        print("=" * 60)
        
        tests = [
            ("Directory Structure", self.test_directory_structure),
            ("Python Files Existence", self.test_python_files_exist),
            ("Configuration Files", self.test_config_files),
            ("Basic Imports", self.test_basic_imports),
            ("Voice Handler Import", self.test_voice_handler_import),
            ("Cross-Package Imports", self.test_cross_imports),
            ("Package Installation", self.test_package_installation),
            ("Pytest Configuration", self.test_pytest_configuration),
            ("Example Scripts", self.test_example_scripts),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            success, message = self.run_test(test_name, test_func)
            if success:
                passed += 1
            else:
                failed += 1
                if message:
                    print(f"   Additional info: {message}")
            print()  # Empty line
        
        # Summary
        print("=" * 60)
        print(f"📊 Verification Results")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Total: {passed + failed}")
        
        if failed == 0:
            print("\n🎉 All verification tests passed!")
            print("\n✅ Directory structure migration was successful")
            print("\n📝 Ready for:")
            print("   • Import resolution works correctly")
            print("   • Package structure is valid")
            print("   • Configuration files updated")
            print("   • Tests can run with new structure")
            print("   • Package installation ready")
            
            print("\n🚀 Next steps:")
            print("   1. Install dependencies: pip install -r config/requirements.txt")
            print("   2. Install in development mode: pip install -e .")
            print("   3. Run tests: python tests/run_tests.py --fast")
            print("   4. Run full tests: python tests/run_tests.py")
            
        else:
            print(f"\n⚠️  {failed} verification test(s) failed")
            print("Please fix issues before proceeding with development.")
        
        return failed == 0

def main():
    """Main entry point"""
    verifier = StructureVerifier()
    success = verifier.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()