"""
Configuration management for AI Interviewer Bot
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class BotConfig:
    """Bot configuration settings"""
    
    # Required settings
    telegram_token: str
    anthropic_api_key: str
    
    # Optional bot settings
    bot_username: Optional[str] = None
    bot_name: str = "AI Interviewer"
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "text"  # text or json
    
    # Session management
    session_timeout_minutes: int = 180
    max_conversation_history: int = 100
    
    # Claude API settings
    claude_model: str = "claude-3-5-haiku-20241022"
    claude_max_tokens: int = 1000
    claude_temperature: float = 0.7
    
    # Optional storage settings
    redis_url: Optional[str] = None
    redis_password: Optional[str] = None
    database_url: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'BotConfig':
        """Create config from environment variables"""
        
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        if not anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        return cls(
            telegram_token=telegram_token,
            anthropic_api_key=anthropic_api_key,
            bot_username=os.getenv('BOT_USERNAME'),
            bot_name=os.getenv('BOT_NAME', 'AI Interviewer'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_format=os.getenv('LOG_FORMAT', 'text'),
            session_timeout_minutes=int(os.getenv('SESSION_TIMEOUT_MINUTES', 180)),
            max_conversation_history=int(os.getenv('MAX_CONVERSATION_HISTORY', 100)),
            claude_model=os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022'),
            claude_max_tokens=int(os.getenv('CLAUDE_MAX_TOKENS', 1000)),
            claude_temperature=float(os.getenv('CLAUDE_TEMPERATURE', 0.7)),
            redis_url=os.getenv('REDIS_URL'),
            redis_password=os.getenv('REDIS_PASSWORD'),
            database_url=os.getenv('DATABASE_URL')
        )
    
    def validate(self) -> None:
        """Validate configuration"""
        if not self.telegram_token:
            raise ValueError("Telegram bot token is required")
        
        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key is required")
        
        if self.session_timeout_minutes <= 0:
            raise ValueError("Session timeout must be positive")
        
        if self.max_conversation_history <= 0:
            raise ValueError("Max conversation history must be positive")
        
        if self.claude_max_tokens <= 0:
            raise ValueError("Claude max tokens must be positive")
        
        if not 0 <= self.claude_temperature <= 1:
            raise ValueError("Claude temperature must be between 0 and 1")

# Global config instance
config = BotConfig.from_env()
config.validate()