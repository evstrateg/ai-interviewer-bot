#!/usr/bin/env python3
"""
Setup configuration for Telegram Interview Bot
Makes the project installable as a package with proper dependency management.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
README_PATH = Path(__file__).parent / "README.md"
long_description = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""

# Read requirements from config directory
REQUIREMENTS_PATH = Path(__file__).parent / "config" / "requirements.txt"
install_requires = []
if REQUIREMENTS_PATH.exists():
    with open(REQUIREMENTS_PATH, "r", encoding="utf-8") as f:
        install_requires = [
            line.strip() 
            for line in f.readlines() 
            if line.strip() and not line.startswith("#")
        ]

# Optional requirements for different features
extras_require = {}

# Voice processing dependencies (optional)
VOICE_REQUIREMENTS_PATH = Path(__file__).parent / "config" / "requirements_new_features.txt"
if VOICE_REQUIREMENTS_PATH.exists():
    with open(VOICE_REQUIREMENTS_PATH, "r", encoding="utf-8") as f:
        voice_deps = [
            line.strip() 
            for line in f.readlines() 
            if line.strip() and not line.startswith("#") and "assemblyai" in line.lower()
        ]
        if voice_deps:
            extras_require["voice"] = voice_deps

# Development dependencies
dev_requirements = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
    "pytest-timeout>=2.1.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
    "structlog>=23.0.0",
]
extras_require["dev"] = dev_requirements

# All optional dependencies
extras_require["all"] = list(set(
    sum(extras_require.values(), [])
))

setup(
    name="telegram-interview-bot",
    version="1.0.0",
    author="AI Interview Bot Team",
    author_email="noreply@example.com",
    description="AI-powered Telegram bot for conducting professional interviews",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/telegram-interview-bot",
    
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Requirements
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    
    # Entry points for command-line scripts
    entry_points={
        "console_scripts": [
            "interview-bot=core.telegram_bot:main",
            "interview-bot-enhanced=core.bot_enhanced:main",
            "run-tests=tests.run_tests:main",
        ],
    },
    
    # Package data
    include_package_data=True,
    package_data={
        "localization": ["*.json", "*.yaml"],
        "": ["*.txt", "*.md", "*.cfg", "*.ini"],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # Keywords
    keywords="telegram bot ai interview claude anthropic voice-processing",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/your-username/telegram-interview-bot/issues",
        "Source": "https://github.com/your-username/telegram-interview-bot",
        "Documentation": "https://github.com/your-username/telegram-interview-bot/blob/main/README.md",
    },
)