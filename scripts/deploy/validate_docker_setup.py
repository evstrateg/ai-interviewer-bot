#!/usr/bin/env python3
"""
Docker Setup Validation Script
Validates that the Docker configuration works with the new package structure.
"""

import os
import sys
from pathlib import Path
import subprocess
import json


def print_status(message, status="INFO"):
    colors = {
        "INFO": "\033[0;34m",
        "SUCCESS": "\033[0;32m", 
        "WARNING": "\033[1;33m",
        "ERROR": "\033[0;31m",
        "NC": "\033[0m"
    }
    print(f"{colors.get(status, '')}{message}{colors['NC']}")


def check_file_exists(file_path, description):
    """Check if a file exists and return True/False"""
    if Path(file_path).exists():
        print_status(f"✅ {description}: {file_path}", "SUCCESS")
        return True
    else:
        print_status(f"❌ {description} missing: {file_path}", "ERROR")
        return False


def check_directory_structure():
    """Validate the new package directory structure"""
    print_status("🔍 Checking directory structure...", "INFO")
    
    required_dirs = [
        ("src/core", "Core bot modules"),
        ("src/handlers", "Message handlers"),
        ("src/localization", "Localization modules"),
        ("config", "Configuration files"),
        ("docker", "Docker configuration"),
        ("scripts/deploy", "Deployment scripts"),
        ("tests", "Test files"),
        ("data", "Data directories")
    ]
    
    all_exist = True
    for dir_path, description in required_dirs:
        if not check_file_exists(dir_path, description):
            all_exist = False
    
    return all_exist


def check_docker_files():
    """Validate Docker configuration files"""
    print_status("🐳 Checking Docker configuration...", "INFO")
    
    required_files = [
        ("docker/Dockerfile", "Production Dockerfile"),
        ("docker/docker-compose.yml", "Production compose file"),
        ("docker/docker-compose.development.yml", "Development compose file"),
        ("setup.py", "Package setup file"),
        ("config/requirements.txt", "Requirements file")
    ]
    
    all_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist


def check_package_structure():
    """Validate Python package structure"""
    print_status("📦 Checking Python package structure...", "INFO")
    
    # Check for __init__.py files
    init_files = [
        "src/__init__.py",
        "src/core/__init__.py", 
        "src/handlers/__init__.py",
        "src/localization/__init__.py"
    ]
    
    all_exist = True
    for init_file in init_files:
        if not check_file_exists(init_file, f"Package init file"):
            all_exist = False
    
    # Check main module files
    main_modules = [
        ("src/core/telegram_bot.py", "Main telegram bot"),
        ("src/core/bot_enhanced.py", "Enhanced bot"),
        ("src/core/config.py", "Configuration module"),
        ("src/handlers/voice_handler.py", "Voice handler"),
        ("src/localization/localization.py", "Localization module")
    ]
    
    for module_path, description in main_modules:
        if not check_file_exists(module_path, description):
            all_exist = False
    
    return all_exist


def validate_dockerfile():
    """Validate Dockerfile content for package structure"""
    print_status("🔍 Validating Dockerfile content...", "INFO")
    
    dockerfile_path = Path("docker/Dockerfile")
    if not dockerfile_path.exists():
        print_status("❌ Dockerfile not found", "ERROR")
        return False
    
    content = dockerfile_path.read_text()
    
    # Check for package-specific patterns
    patterns = [
        ("COPY setup.py", "Package setup copy"),
        ("COPY src/", "Source code copy"),
        ("pip wheel", "Wheel building"),
        ("telegram-interview-bot", "Package installation"),
        ("interview-bot-enhanced", "Entry point usage")
    ]
    
    all_valid = True
    for pattern, description in patterns:
        if pattern in content:
            print_status(f"✅ {description} found", "SUCCESS")
        else:
            print_status(f"❌ {description} missing in Dockerfile", "ERROR")
            all_valid = False
    
    return all_valid


def validate_compose_file():
    """Validate docker-compose configuration"""
    print_status("🔍 Validating docker-compose.yml...", "INFO")
    
    compose_path = Path("docker/docker-compose.yml")
    if not compose_path.exists():
        print_status("❌ docker-compose.yml not found", "ERROR")
        return False
    
    content = compose_path.read_text()
    
    # Check for updated paths
    patterns = [
        ("context: ..", "Updated build context"),
        ("dockerfile: docker/Dockerfile", "Updated Dockerfile path"),
        ("../data/sessions", "Updated session volume"),
        ("ASSEMBLYAI_API_KEY", "Voice processing env var")
    ]
    
    all_valid = True
    for pattern, description in patterns:
        if pattern in content:
            print_status(f"✅ {description} found", "SUCCESS")
        else:
            print_status(f"❌ {description} missing in compose file", "ERROR") 
            all_valid = False
    
    return all_valid


def validate_setup_py():
    """Validate setup.py configuration"""
    print_status("🔍 Validating setup.py...", "INFO")
    
    setup_path = Path("setup.py")
    if not setup_path.exists():
        print_status("❌ setup.py not found", "ERROR")
        return False
    
    content = setup_path.read_text()
    
    patterns = [
        ('packages=find_packages(where="src")', "Package discovery"),
        ('package_dir={"": "src"}', "Package directory"),
        ("interview-bot-enhanced=core.bot_enhanced:main", "Entry point"),
        ("config/requirements.txt", "Requirements path")
    ]
    
    all_valid = True
    for pattern, description in patterns:
        if pattern in content:
            print_status(f"✅ {description} found", "SUCCESS")
        else:
            print_status(f"❌ {description} missing in setup.py", "WARNING")
    
    return all_valid


def check_deployment_scripts():
    """Check deployment scripts are updated"""
    print_status("🚀 Checking deployment scripts...", "INFO")
    
    scripts = [
        ("scripts/deploy/deploy_pythonanywhere.sh", "PythonAnywhere deployment"),
        ("scripts/deploy/deploy_docker.sh", "Docker deployment"),
        ("scripts/deploy/test_docker_build.sh", "Docker test script")
    ]
    
    all_exist = True
    for script_path, description in scripts:
        if check_file_exists(script_path, description):
            # Check if script is executable
            if os.access(script_path, os.X_OK):
                print_status(f"  ✅ {script_path} is executable", "SUCCESS")
            else:
                print_status(f"  ⚠️  {script_path} is not executable", "WARNING")
        else:
            all_exist = False
    
    return all_exist


def generate_validation_report():
    """Generate a comprehensive validation report"""
    print_status("📋 Docker Configuration Validation Report", "INFO")
    print("=" * 60)
    
    tests = [
        ("Directory Structure", check_directory_structure),
        ("Docker Files", check_docker_files),
        ("Package Structure", check_package_structure),
        ("Dockerfile Content", validate_dockerfile),
        ("Docker Compose", validate_compose_file),
        ("Setup.py", validate_setup_py),
        ("Deployment Scripts", check_deployment_scripts)
    ]
    
    results = {}
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        result = test_func()
        results[test_name] = result
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        color = "SUCCESS" if result else "ERROR"
        print_status(f"{test_name:<25} {status:>8}", color)
    
    print("\n" + "=" * 60)
    if all_passed:
        print_status("🎉 ALL VALIDATIONS PASSED!", "SUCCESS")
        print_status("Docker configuration is ready for the new package structure", "SUCCESS")
        print("\nNext steps:")
        print("  1. Test the build: make test")
        print("  2. Run development: make dev")
        print("  3. Deploy production: make deploy")
    else:
        print_status("❌ SOME VALIDATIONS FAILED", "ERROR")
        print_status("Please fix the issues above before proceeding", "ERROR")
        return 1
    
    return 0


def main():
    """Main validation function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # JSON output for CI/CD integration
        results = {}
        results["directory_structure"] = check_directory_structure()
        results["docker_files"] = check_docker_files()
        results["package_structure"] = check_package_structure()
        results["dockerfile_content"] = validate_dockerfile()
        results["compose_file"] = validate_compose_file()
        results["setup_py"] = validate_setup_py()
        results["deployment_scripts"] = check_deployment_scripts()
        
        results["all_passed"] = all(results.values())
        print(json.dumps(results, indent=2))
        return 0 if results["all_passed"] else 1
    else:
        return generate_validation_report()


if __name__ == "__main__":
    sys.exit(main())