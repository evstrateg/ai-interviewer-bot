#!/usr/bin/env python3
"""
Test Runner Script for AssemblyAI Integration Tests

This script provides easy command-line interface for running various test configurations.
It handles test environment setup and provides detailed output formatting.

Usage:
    python run_tests.py                    # Run all safe tests (no real API)
    python run_tests.py --unit             # Run unit tests only
    python run_tests.py --integration      # Run integration tests
    python run_tests.py --performance      # Run performance tests
    python run_tests.py --real-api         # Run real API tests (requires API key)
    python run_tests.py --coverage         # Run with coverage report
    python run_tests.py --fast             # Quick test run
    python run_tests.py --ci               # CI/CD simulation mode
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional
import tempfile

class TestRunner:
    """Enhanced test runner for AssemblyAI integration tests"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = Path(__file__).parent
        self.test_file = self.test_dir / "test_assemblyai_integration.py"
        self.coverage_dir = self.test_dir / "htmlcov"
        
    def run_command(self, cmd: List[str], description: str) -> int:
        """Run a command and return exit code"""
        print(f"\n🚀 {description}")
        print(f"Command: {' '.join(cmd)}")
        print("=" * 80)
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, check=False)
            if result.returncode == 0:
                print(f"✅ {description} - PASSED")
            else:
                print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return result.returncode
        except Exception as e:
            print(f"💥 {description} - ERROR: {e}")
            return 1
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed"""
        required_packages = [
            'pytest', 'pytest-asyncio', 'pytest-cov', 'pytest-mock'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing.append(package)
        
        if missing:
            print(f"❌ Missing required packages: {', '.join(missing)}")
            print(f"Install with: pip install {' '.join(missing)}")
            return False
        
        return True
    
    def check_test_files(self) -> bool:
        """Check if test files exist"""
        required_files = [
            self.test_file,
            self.test_dir / "conftest.py",
            self.project_root / "src" / "handlers" / "voice_handler.py"
        ]
        
        missing = []
        for file_path in required_files:
            if not file_path.exists():
                missing.append(str(file_path))
        
        if missing:
            print(f"❌ Missing required files: {', '.join(missing)}")
            return False
        
        return True
    
    def setup_environment(self, real_api: bool = False) -> dict:
        """Setup test environment variables"""
        env = os.environ.copy()
        
        # Test configuration
        env['PYTEST_CURRENT_TEST'] = 'true'
        env['TZ'] = 'UTC'
        
        # Disable real API tests by default
        if not real_api:
            env['ASSEMBLYAI_INTEGRATION_TESTS'] = 'false'
        else:
            env['ASSEMBLYAI_INTEGRATION_TESTS'] = 'true'
            # Check if API key is available
            if not os.getenv('ASSEMBLYAI_API_KEY'):
                print("⚠️  ASSEMBLYAI_API_KEY not set for real API tests")
        
        # Ensure required test environment variables
        if not env.get('TELEGRAM_BOT_TOKEN'):
            env['TELEGRAM_BOT_TOKEN'] = 'test_token_for_testing'
        
        if not env.get('ANTHROPIC_API_KEY'):
            env['ANTHROPIC_API_KEY'] = 'test_key_for_testing'
        
        return env
    
    def run_unit_tests(self, coverage: bool = False) -> int:
        """Run unit tests only"""
        cmd = [
            'python', '-m', 'pytest', 
            str(self.test_file),
            '-v',
            '-m', 'not integration and not performance and not real_api',
            '--tb=short',
            '--timeout=120'
        ]
        
        if coverage:
            cmd.extend(['--cov=src.handlers.voice_handler', '--cov-report=term-missing'])
        
        return self.run_command(cmd, "Unit Tests")
    
    def run_integration_tests(self, coverage: bool = False) -> int:
        """Run integration tests with mocked APIs"""
        cmd = [
            'python', '-m', 'pytest',
            str(self.test_file),
            '-v',
            '-m', 'integration and not real_api',
            '--tb=short',
            '--timeout=300'
        ]
        
        if coverage:
            cmd.extend(['--cov=src.handlers.voice_handler', '--cov-report=term-missing'])
        
        return self.run_command(cmd, "Integration Tests (Mocked)")
    
    def run_performance_tests(self) -> int:
        """Run performance tests"""
        cmd = [
            'python', '-m', 'pytest',
            str(self.test_file),
            '-v',
            '-m', 'performance',
            '--tb=short',
            '--timeout=600'
        ]
        
        return self.run_command(cmd, "Performance Tests")
    
    def run_real_api_tests(self) -> int:
        """Run tests with real AssemblyAI API"""
        if not os.getenv('ASSEMBLYAI_API_KEY'):
            print("❌ ASSEMBLYAI_API_KEY environment variable required for real API tests")
            return 1
        
        cmd = [
            'python', '-m', 'pytest',
            str(self.test_file),
            '-v',
            '-m', 'real_api',
            '--tb=short',
            '--timeout=900'
        ]
        
        return self.run_command(cmd, "Real API Tests")
    
    def run_coverage_tests(self) -> int:
        """Run tests with comprehensive coverage reporting"""
        cmd = [
            'python', '-m', 'pytest',
            str(self.test_file),
            '-v',
            '-m', 'not real_api',  # Exclude real API for coverage
            '--cov=src.handlers.voice_handler',
            '--cov-report=html',
            '--cov-report=term-missing',
            '--cov-report=xml',
            '--tb=short',
            '--timeout=600'
        ]
        
        exit_code = self.run_command(cmd, "Coverage Tests")
        
        if exit_code == 0 and self.coverage_dir.exists():
            print(f"\n📊 Coverage report generated: {self.coverage_dir / 'index.html'}")
        
        return exit_code
    
    def run_fast_tests(self) -> int:
        """Run a fast subset of tests for quick feedback"""
        cmd = [
            'python', '-m', 'pytest',
            str(self.test_file),
            '-x',  # Stop on first failure
            '--maxfail=3',  # Stop after 3 failures
            '-m', 'unit',  # Only unit tests
            '--tb=short',
            '--timeout=60'
        ]
        
        return self.run_command(cmd, "Fast Tests")
    
    def run_ci_tests(self) -> int:
        """Run tests in CI/CD simulation mode"""
        print("🏗️  Running in CI/CD simulation mode")
        
        # Set CI environment variables
        env = self.setup_environment()
        env['CI'] = 'true'
        env['GITHUB_ACTIONS'] = 'true'
        
        # Run lint checks first
        lint_cmd = ['python', '-m', 'flake8', '../src/handlers/voice_handler.py', 'test_assemblyai_integration.py', '--max-line-length=127']
        lint_result = self.run_command(lint_cmd, "Lint Check")
        
        if lint_result != 0:
            print("⚠️  Lint check failed, continuing with tests...")
        
        # Run tests with coverage
        cmd = [
            'python', '-m', 'pytest',
            str(self.test_file),
            '-v',
            '-m', 'not real_api',
            '--cov=src.handlers.voice_handler',
            '--cov-report=xml',
            '--cov-report=term-missing',
            '--tb=short',
            '--timeout=600',
            '--maxfail=10'
        ]
        
        # Use CI environment
        original_env = os.environ.copy()
        os.environ.update(env)
        
        try:
            exit_code = self.run_command(cmd, "CI Tests")
        finally:
            os.environ.clear()
            os.environ.update(original_env)
        
        return exit_code
    
    def run_all_safe_tests(self, coverage: bool = False) -> int:
        """Run all tests except real API tests"""
        cmd = [
            'python', '-m', 'pytest',
            str(self.test_file),
            '-v',
            '-m', 'not real_api',
            '--tb=short',
            '--timeout=600'
        ]
        
        if coverage:
            cmd.extend(['--cov=src.handlers.voice_handler', '--cov-report=term-missing'])
        
        return self.run_command(cmd, "All Safe Tests")
    
    def validate_setup(self) -> bool:
        """Validate test setup"""
        print("🔍 Validating test setup...")
        
        if not self.check_dependencies():
            return False
        
        if not self.check_test_files():
            return False
        
        # Check if voice_handler can be imported
        try:
            sys.path.insert(0, str(self.project_root))
            from src.handlers import voice_handler
            print("✅ voice_handler module imports successfully")
        except ImportError as e:
            print(f"❌ Failed to import voice_handler: {e}")
            return False
        
        print("✅ Test setup validation passed")
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run AssemblyAI integration tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all safe tests
  python run_tests.py --unit             # Run unit tests only
  python run_tests.py --coverage         # Run with coverage
  python run_tests.py --fast             # Quick test run
  python run_tests.py --real-api         # Include real API tests
  python run_tests.py --ci               # Simulate CI environment
        """
    )
    
    parser.add_argument('--unit', action='store_true', 
                       help='Run unit tests only')
    parser.add_argument('--integration', action='store_true',
                       help='Run integration tests with mocked APIs')
    parser.add_argument('--performance', action='store_true',
                       help='Run performance tests')
    parser.add_argument('--real-api', action='store_true',
                       help='Run real API tests (requires ASSEMBLYAI_API_KEY)')
    parser.add_argument('--coverage', action='store_true',
                       help='Generate coverage report')
    parser.add_argument('--fast', action='store_true',
                       help='Run quick test subset for fast feedback')
    parser.add_argument('--ci', action='store_true',
                       help='Run in CI/CD simulation mode')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate test setup, don\'t run tests')
    
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunner()
    
    # Validate setup
    if not runner.validate_setup():
        print("\n❌ Test setup validation failed")
        return 1
    
    if args.validate_only:
        print("\n✅ Test setup validation completed successfully")
        return 0
    
    # Setup environment
    env = runner.setup_environment(real_api=args.real_api)
    original_env = os.environ.copy()
    os.environ.update(env)
    
    try:
        exit_code = 0
        
        # Run specified test type
        if args.fast:
            exit_code = runner.run_fast_tests()
        elif args.ci:
            exit_code = runner.run_ci_tests()
        elif args.unit:
            exit_code = runner.run_unit_tests(coverage=args.coverage)
        elif args.integration:
            exit_code = runner.run_integration_tests(coverage=args.coverage)
        elif args.performance:
            exit_code = runner.run_performance_tests()
        elif args.real_api:
            exit_code = runner.run_real_api_tests()
        elif args.coverage:
            exit_code = runner.run_coverage_tests()
        else:
            # Default: run all safe tests
            exit_code = runner.run_all_safe_tests(coverage=args.coverage)
        
        # Print summary
        print("\n" + "=" * 80)
        if exit_code == 0:
            print("🎉 All tests completed successfully!")
            if args.coverage and runner.coverage_dir.exists():
                print(f"📊 Coverage report: file://{runner.coverage_dir.absolute()}/index.html")
        else:
            print(f"💥 Tests failed with exit code: {exit_code}")
            print("Check the output above for details.")
        
        return exit_code
        
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)

if __name__ == "__main__":
    sys.exit(main())