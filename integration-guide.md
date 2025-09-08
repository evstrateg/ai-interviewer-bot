# AI Interviewer Bot - Developer Integration Guide

## Table of Contents

1. [Quick Start](#quick-start)
2. [SDK-Style Usage](#sdk-style-usage)
3. [Integration Patterns](#integration-patterns)
4. [Code Examples](#code-examples)
5. [Testing Your Integration](#testing-your-integration)
6. [Deployment Guide](#deployment-guide)
7. [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### Basic Setup

```python
#!/usr/bin/env python3
"""
Minimal AI Interviewer Bot setup
"""

import os
from dotenv import load_dotenv
from bot_enhanced import EnhancedAIInterviewerBot

# Load environment variables
load_dotenv()

# Create and run bot
def main():
    bot = EnhancedAIInterviewerBot(
        telegram_token=os.getenv('TELEGRAM_BOT_TOKEN'),
        anthropic_api_key=os.getenv('ANTHROPIC_API_KEY')
    )
    
    print("🤖 AI Interviewer Bot starting...")
    bot.run()

if __name__ == '__main__':
    main()
```

### Environment Configuration

```bash
# .env file
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ANTHROPIC_API_KEY=sk-ant-api03-...

# Optional settings
BOT_USERNAME=ai_interviewer_bot
LOG_LEVEL=INFO
SESSION_TIMEOUT_MINUTES=180
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

## SDK-Style Usage

### Core Bot Interface

```python
from telegram_bot import AIInterviewerBot, PromptVariant, InterviewStage
from typing import Dict, Any

class InterviewerSDK:
    """SDK-style wrapper for the AI Interviewer Bot"""
    
    def __init__(self, telegram_token: str, anthropic_api_key: str):
        self.bot = AIInterviewerBot(telegram_token, anthropic_api_key)
    
    async def create_interview_session(self, user_id: int, username: str, 
                                     variant: PromptVariant = PromptVariant.CONVERSATIONAL) -> bool:
        """Create new interview session for user"""
        try:
            session = InterviewSession(
                user_id=user_id,
                username=username,
                prompt_variant=variant,
                current_stage=InterviewStage.GREETING,
                stage_completeness={stage.value: 0 for stage in InterviewStage},
                conversation_history=[],
                start_time=datetime.now(),
                last_activity=datetime.now()
            )
            
            self.bot.sessions[user_id] = session
            return True
            
        except Exception as e:
            print(f"Failed to create session: {e}")
            return False
    
    async def send_message(self, user_id: int, message: str) -> Dict[str, Any]:
        """Send message and get AI response"""
        session = self.bot.sessions.get(user_id)
        if not session:
            return {"error": "No active session"}
        
        try:
            # Generate AI response
            response = await self.bot.claude.generate_interview_response(
                session, message, self.bot.prompt_manager
            )
            
            # Update session
            session.add_message("user", message)
            session.add_message("assistant", response['response'], response.get('metadata'))
            
            return response
            
        except Exception as e:
            return {"error": f"Message processing failed: {e}"}
    
    def get_session_status(self, user_id: int) -> Dict[str, Any]:
        """Get current interview status"""
        session = self.bot.sessions.get(user_id)
        if not session:
            return {"error": "No active session"}
        
        duration = datetime.now() - session.start_time
        
        return {
            "user_id": user_id,
            "current_stage": session.current_stage.value,
            "duration_minutes": duration.total_seconds() / 60,
            "question_depth": session.question_depth,
            "engagement_level": session.engagement_level,
            "examples_collected": session.examples_collected,
            "stage_progress": session.stage_completeness,
            "total_messages": len(session.conversation_history)
        }
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        return [
            {
                "user_id": session.user_id,
                "username": session.username,
                "stage": session.current_stage.value,
                "variant": session.prompt_variant.value,
                "start_time": session.start_time.isoformat()
            }
            for session in self.bot.sessions.values()
        ]

# Usage example
async def sdk_example():
    sdk = InterviewerSDK("your_token", "your_api_key")
    
    # Create session
    success = await sdk.create_interview_session(12345, "john_doe")
    print(f"Session created: {success}")
    
    # Send message
    response = await sdk.send_message(12345, "I'm a software developer")
    print(f"AI Response: {response['response']}")
    
    # Check status
    status = sdk.get_session_status(12345)
    print(f"Current stage: {status['current_stage']}")
```

### Session Management

```python
from bot_enhanced import SessionManager, InterviewSession
import json
from pathlib import Path

class InterviewSessionAPI:
    """High-level session management API"""
    
    def __init__(self, storage_dir: str = "sessions"):
        self.session_manager = SessionManager(storage_dir)
    
    def create_session(self, user_data: Dict[str, Any]) -> str:
        """Create session with validation"""
        required_fields = ['user_id', 'username', 'prompt_variant']
        
        if not all(field in user_data for field in required_fields):
            raise ValueError(f"Missing required fields: {required_fields}")
        
        variant = PromptVariant(user_data['prompt_variant'])
        session = self.session_manager.create_session(
            user_data['user_id'],
            user_data['username'],
            variant
        )
        
        return f"Session created for user {session.user_id}"
    
    def get_session_data(self, user_id: int) -> Dict[str, Any]:
        """Get complete session data"""
        session = self.session_manager.get_session(user_id)
        if not session:
            return {"error": "Session not found"}
        
        return {
            "session_id": f"session_{user_id}",
            "user_info": {
                "user_id": session.user_id,
                "username": session.username
            },
            "interview_config": {
                "prompt_variant": session.prompt_variant.value,
                "current_stage": session.current_stage.value,
                "start_time": session.start_time.isoformat()
            },
            "progress": {
                "stage_completeness": session.stage_completeness,
                "question_depth": session.question_depth,
                "engagement_level": session.engagement_level,
                "examples_collected": session.examples_collected,
                "key_insights": session.key_insights
            },
            "conversation": {
                "message_count": len(session.conversation_history),
                "last_activity": session.last_activity.isoformat(),
                "recent_messages": session.conversation_history[-5:]  # Last 5 messages
            }
        }
    
    def export_session(self, user_id: int, format: str = "json") -> str:
        """Export session in various formats"""
        session = self.session_manager.get_session(user_id)
        if not session:
            raise ValueError("Session not found")
        
        session_data = self.get_session_data(user_id)
        
        if format == "json":
            return json.dumps(session_data, indent=2)
        elif format == "csv":
            return self._export_to_csv(session_data)
        elif format == "markdown":
            return self._export_to_markdown(session_data)
        else:
            raise ValueError("Unsupported format")
    
    def _export_to_markdown(self, session_data: Dict) -> str:
        """Export session as markdown report"""
        md = f"""# Interview Session Report
        
## User Information
- **User ID**: {session_data['user_info']['user_id']}
- **Username**: {session_data['user_info']['username']}
- **Start Time**: {session_data['interview_config']['start_time']}

## Interview Configuration
- **Prompt Variant**: {session_data['interview_config']['prompt_variant']}
- **Current Stage**: {session_data['interview_config']['current_stage']}

## Progress Summary
- **Messages**: {session_data['conversation']['message_count']}
- **Examples Collected**: {session_data['progress']['examples_collected']}
- **Engagement Level**: {session_data['progress']['engagement_level']}

## Stage Completion
"""
        for stage, completion in session_data['progress']['stage_completeness'].items():
            status = "✅" if completion >= 80 else "🟡" if completion >= 50 else "❌"
            md += f"- {status} **{stage.title()}**: {completion}%\n"
        
        md += "\n## Key Insights\n"
        for insight in session_data['progress']['key_insights']:
            md += f"- {insight}\n"
        
        return md

# Usage
api = InterviewSessionAPI()

# Create session
session_info = api.create_session({
    'user_id': 12345,
    'username': 'john_doe',
    'prompt_variant': 'v3_conversational'
})

# Export session
report = api.export_session(12345, format='markdown')
print(report)
```

## Integration Patterns

### Webhook Integration

```python
from flask import Flask, request, jsonify
from telegram_bot import AIInterviewerBot
import asyncio

app = Flask(__name__)

# Initialize bot
bot = AIInterviewerBot(
    telegram_token=os.getenv('TELEGRAM_BOT_TOKEN'),
    anthropic_api_key=os.getenv('ANTHROPIC_API_KEY')
)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates"""
    try:
        update_data = request.get_json()
        
        # Process update asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Create Telegram Update object
        from telegram import Update
        update = Update.de_json(update_data, bot.application.bot)
        
        # Process update
        loop.run_until_complete(
            bot.application.process_update(update)
        )
        
        return jsonify({"status": "ok"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sessions/<int:user_id>', methods=['GET'])
def get_session(user_id):
    """REST API for session data"""
    session = bot.sessions.get(user_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify({
        "user_id": session.user_id,
        "stage": session.current_stage.value,
        "progress": session.stage_completeness,
        "message_count": len(session.conversation_history)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Database Integration

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()

class InterviewSessionDB(Base):
    __tablename__ = 'interview_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    prompt_variant = Column(String(50))
    current_stage = Column(String(50))
    stage_completeness = Column(JSON)
    conversation_history = Column(JSON)
    start_time = Column(DateTime)
    last_activity = Column(DateTime)
    metadata = Column(JSON)

class DatabaseSessionManager:
    """Database-backed session manager"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def save_session(self, session: InterviewSession):
        """Save session to database"""
        db_session = self.SessionLocal()
        
        try:
            # Check if session exists
            existing = db_session.query(InterviewSessionDB).filter_by(
                user_id=session.user_id
            ).first()
            
            if existing:
                # Update existing
                existing.current_stage = session.current_stage.value
                existing.stage_completeness = session.stage_completeness
                existing.conversation_history = session.conversation_history
                existing.last_activity = session.last_activity
                existing.metadata = {
                    'question_depth': session.question_depth,
                    'engagement_level': session.engagement_level,
                    'examples_collected': session.examples_collected,
                    'key_insights': session.key_insights
                }
            else:
                # Create new
                db_session.add(InterviewSessionDB(
                    user_id=session.user_id,
                    username=session.username,
                    prompt_variant=session.prompt_variant.value,
                    current_stage=session.current_stage.value,
                    stage_completeness=session.stage_completeness,
                    conversation_history=session.conversation_history,
                    start_time=session.start_time,
                    last_activity=session.last_activity,
                    metadata={
                        'question_depth': session.question_depth,
                        'engagement_level': session.engagement_level,
                        'examples_collected': session.examples_collected,
                        'key_insights': session.key_insights
                    }
                ))
            
            db_session.commit()
            
        finally:
            db_session.close()
    
    def load_session(self, user_id: int) -> Optional[InterviewSession]:
        """Load session from database"""
        db_session = self.SessionLocal()
        
        try:
            db_record = db_session.query(InterviewSessionDB).filter_by(
                user_id=user_id
            ).first()
            
            if not db_record:
                return None
            
            # Convert back to InterviewSession
            session = InterviewSession(
                user_id=db_record.user_id,
                username=db_record.username,
                prompt_variant=PromptVariant(db_record.prompt_variant),
                current_stage=InterviewStage(db_record.current_stage),
                stage_completeness=db_record.stage_completeness,
                conversation_history=db_record.conversation_history,
                start_time=db_record.start_time,
                last_activity=db_record.last_activity
            )
            
            # Restore metadata
            if db_record.metadata:
                metadata = db_record.metadata
                session.question_depth = metadata.get('question_depth', 1)
                session.engagement_level = metadata.get('engagement_level', 'medium')
                session.examples_collected = metadata.get('examples_collected', 0)
                session.key_insights = metadata.get('key_insights', [])
            
            return session
            
        finally:
            db_session.close()

# Usage
db_manager = DatabaseSessionManager("postgresql://user:pass@localhost/interviews")

# Enhanced bot with database persistence
class DatabaseAIInterviewerBot(EnhancedAIInterviewerBot):
    def __init__(self, telegram_token: str, anthropic_api_key: str, database_url: str):
        super().__init__(telegram_token, anthropic_api_key)
        self.db_manager = DatabaseSessionManager(database_url)
    
    async def handle_message(self, update, context):
        # Process message normally
        await super().handle_message(update, context)
        
        # Save to database
        user_id = update.effective_user.id
        if user_id in self.sessions:
            self.db_manager.save_session(self.sessions[user_id])
```

### Analytics Integration

```python
import pandas as pd
from typing import List, Dict
import matplotlib.pyplot as plt
import seaborn as sns

class InterviewAnalytics:
    """Analytics for interview sessions"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    def get_session_dataframe(self) -> pd.DataFrame:
        """Convert sessions to pandas DataFrame for analysis"""
        sessions_data = []
        
        for session in self.session_manager.sessions.values():
            duration = datetime.now() - session.start_time
            
            sessions_data.append({
                'user_id': session.user_id,
                'username': session.username,
                'prompt_variant': session.prompt_variant.value,
                'current_stage': session.current_stage.value,
                'duration_minutes': duration.total_seconds() / 60,
                'message_count': len(session.conversation_history),
                'examples_collected': session.examples_collected,
                'engagement_level': session.engagement_level,
                'question_depth': session.question_depth,
                'total_completeness': sum(session.stage_completeness.values()),
                'start_time': session.start_time,
                'last_activity': session.last_activity
            })
        
        return pd.DataFrame(sessions_data)
    
    def analyze_engagement_patterns(self) -> Dict[str, Any]:
        """Analyze user engagement patterns"""
        df = self.get_session_dataframe()
        
        if df.empty:
            return {"error": "No session data available"}
        
        return {
            "engagement_distribution": df['engagement_level'].value_counts().to_dict(),
            "avg_duration_by_engagement": df.groupby('engagement_level')['duration_minutes'].mean().to_dict(),
            "completion_by_engagement": df.groupby('engagement_level')['total_completeness'].mean().to_dict(),
            "popular_variants": df['prompt_variant'].value_counts().to_dict()
        }
    
    def generate_completion_report(self) -> str:
        """Generate completion analysis report"""
        df = self.get_session_dataframe()
        
        if df.empty:
            return "No session data available"
        
        report = f"""# Interview Completion Analysis
        
## Overall Statistics
- **Total Sessions**: {len(df)}
- **Average Duration**: {df['duration_minutes'].mean():.1f} minutes
- **Average Messages**: {df['message_count'].mean():.1f}
- **Average Examples**: {df['examples_collected'].mean():.1f}

## Engagement Breakdown
"""
        
        engagement_stats = df.groupby('engagement_level').agg({
            'duration_minutes': ['mean', 'count'],
            'total_completeness': 'mean',
            'examples_collected': 'mean'
        }).round(2)
        
        for engagement in ['high', 'medium', 'low']:
            if engagement in engagement_stats.index:
                stats = engagement_stats.loc[engagement]
                report += f"""
### {engagement.title()} Engagement
- Sessions: {stats[('duration_minutes', 'count')]}
- Avg Duration: {stats[('duration_minutes', 'mean')]:.1f} min
- Avg Completion: {stats[('total_completeness', 'mean')]:.1f}%
- Avg Examples: {stats[('examples_collected', 'mean')]:.1f}
"""
        
        return report
    
    def export_analytics_dashboard(self, filename: str = "interview_analytics.html"):
        """Create interactive analytics dashboard"""
        df = self.get_session_dataframe()
        
        if df.empty:
            return "No data to visualize"
        
        # Create visualizations
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Engagement distribution
        df['engagement_level'].value_counts().plot(kind='bar', ax=axes[0,0])
        axes[0,0].set_title('Engagement Level Distribution')
        
        # Duration vs Completion
        sns.scatterplot(data=df, x='duration_minutes', y='total_completeness', 
                       hue='engagement_level', ax=axes[0,1])
        axes[0,1].set_title('Duration vs Completion by Engagement')
        
        # Prompt variant popularity
        df['prompt_variant'].value_counts().plot(kind='pie', ax=axes[1,0], autopct='%1.1f%%')
        axes[1,0].set_title('Prompt Variant Usage')
        
        # Examples collected distribution
        df['examples_collected'].hist(bins=20, ax=axes[1,1])
        axes[1,1].set_title('Examples Collected Distribution')
        
        plt.tight_layout()
        plt.savefig(filename.replace('.html', '.png'), dpi=300, bbox_inches='tight')
        
        return f"Analytics saved to {filename.replace('.html', '.png')}"

# Usage
analytics = InterviewAnalytics(bot.session_manager)
engagement_analysis = analytics.analyze_engagement_patterns()
print(engagement_analysis)

completion_report = analytics.generate_completion_report()
print(completion_report)
```

## Code Examples

### Custom Prompt Integration

```python
class CustomPromptManager(PromptManager):
    """Extended prompt manager with custom variants"""
    
    def __init__(self, custom_prompts: Dict[str, str] = None):
        super().__init__()
        self.custom_prompts = custom_prompts or {}
    
    def add_custom_prompt(self, variant_name: str, prompt_content: str, description: str):
        """Add custom prompt variant"""
        # Create new enum value dynamically
        setattr(PromptVariant, variant_name.upper(), variant_name)
        
        # Store prompt content
        self.prompts[PromptVariant(variant_name)] = prompt_content
        
        # Update descriptions
        descriptions = {
            variant_name: description
        }
        
        return f"Added custom prompt variant: {variant_name}"
    
    def load_prompts_from_api(self, api_endpoint: str):
        """Load prompts from external API"""
        import requests
        
        try:
            response = requests.get(api_endpoint)
            response.raise_for_status()
            
            prompt_data = response.json()
            
            for variant_name, prompt_info in prompt_data.items():
                self.add_custom_prompt(
                    variant_name,
                    prompt_info['content'],
                    prompt_info['description']
                )
            
            return f"Loaded {len(prompt_data)} custom prompts from API"
            
        except requests.RequestException as e:
            return f"Failed to load prompts from API: {e}"

# Usage
custom_manager = CustomPromptManager()

# Add domain-specific prompt
technical_prompt = """
You are a technical interviewer specializing in software engineering roles.
Focus heavily on:
- System design questions
- Code architecture discussions  
- Technical problem-solving approaches
- Tool and technology expertise
- Performance optimization strategies

Always ask for specific code examples and architectural decisions.
"""

custom_manager.add_custom_prompt(
    "technical_specialist",
    technical_prompt,
    "🔧 Technical Specialist - Deep technical focus"
)
```

### Real-time Monitoring

```python
import asyncio
from datetime import datetime, timedelta
import websockets
import json

class InterviewMonitor:
    """Real-time interview monitoring system"""
    
    def __init__(self, bot: EnhancedAIInterviewerBot):
        self.bot = bot
        self.connected_clients = set()
        self.monitoring_active = False
    
    async def start_monitoring(self, host='localhost', port=8765):
        """Start WebSocket monitoring server"""
        self.monitoring_active = True
        
        async def handle_client(websocket, path):
            """Handle WebSocket client connections"""
            self.connected_clients.add(websocket)
            print(f"Monitor client connected: {websocket.remote_address}")
            
            try:
                # Send initial state
                await self.send_initial_state(websocket)
                
                # Keep connection alive
                await websocket.wait_closed()
                
            finally:
                self.connected_clients.remove(websocket)
                print(f"Monitor client disconnected: {websocket.remote_address}")
        
        # Start monitoring tasks
        asyncio.create_task(self.broadcast_metrics())
        asyncio.create_task(self.broadcast_session_updates())
        
        # Start WebSocket server
        server = await websockets.serve(handle_client, host, port)
        print(f"🔍 Interview Monitor started on ws://{host}:{port}")
        
        return server
    
    async def send_initial_state(self, websocket):
        """Send current bot state to new client"""
        state = {
            "type": "initial_state",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "active_sessions": len(self.bot.sessions),
                "metrics": self.bot.metrics.get_metrics(),
                "sessions": [
                    {
                        "user_id": s.user_id,
                        "username": s.username,
                        "stage": s.current_stage.value,
                        "duration": (datetime.now() - s.start_time).seconds // 60,
                        "completeness": sum(s.stage_completeness.values()) // 9
                    }
                    for s in self.bot.sessions.values()
                ]
            }
        }
        
        await websocket.send(json.dumps(state))
    
    async def broadcast_metrics(self):
        """Broadcast metrics updates every 30 seconds"""
        while self.monitoring_active:
            if self.connected_clients:
                metrics_update = {
                    "type": "metrics_update",
                    "timestamp": datetime.now().isoformat(),
                    "data": self.bot.metrics.get_metrics()
                }
                
                # Broadcast to all connected clients
                disconnected = []
                for client in self.connected_clients:
                    try:
                        await client.send(json.dumps(metrics_update))
                    except websockets.exceptions.ConnectionClosed:
                        disconnected.append(client)
                
                # Clean up disconnected clients
                for client in disconnected:
                    self.connected_clients.discard(client)
            
            await asyncio.sleep(30)
    
    async def broadcast_session_updates(self):
        """Broadcast session state changes"""
        last_session_count = len(self.bot.sessions)
        
        while self.monitoring_active:
            current_count = len(self.bot.sessions)
            
            if current_count != last_session_count:
                session_update = {
                    "type": "session_update",
                    "timestamp": datetime.now().isoformat(),
                    "data": {
                        "active_sessions": current_count,
                        "change": current_count - last_session_count
                    }
                }
                
                # Broadcast update
                disconnected = []
                for client in self.connected_clients:
                    try:
                        await client.send(json.dumps(session_update))
                    except websockets.exceptions.ConnectionClosed:
                        disconnected.append(client)
                
                for client in disconnected:
                    self.connected_clients.discard(client)
                
                last_session_count = current_count
            
            await asyncio.sleep(5)
    
    def stop_monitoring(self):
        """Stop monitoring system"""
        self.monitoring_active = False

# Usage
monitor = InterviewMonitor(bot)

# Start monitoring in background
async def run_bot_with_monitoring():
    # Start monitoring server
    monitor_server = await monitor.start_monitoring()
    
    # Start bot
    bot_task = asyncio.create_task(bot.application.run_polling())
    
    # Wait for both
    await asyncio.gather(
        monitor_server.wait_closed(),
        bot_task
    )

# HTML Dashboard for monitoring
dashboard_html = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Interviewer Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { display: inline-block; margin: 10px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .sessions { margin-top: 20px; }
        .session { padding: 10px; margin: 5px 0; background: #f5f5f5; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>🤖 AI Interviewer Monitor</h1>
    
    <div id="metrics">
        <div class="metric">
            <strong>Active Sessions:</strong> <span id="active-sessions">0</span>
        </div>
        <div class="metric">
            <strong>Total Started:</strong> <span id="sessions-started">0</span>
        </div>
        <div class="metric">
            <strong>API Calls:</strong> <span id="api-calls">0</span>
        </div>
        <div class="metric">
            <strong>Errors:</strong> <span id="errors">0</span>
        </div>
    </div>
    
    <div class="sessions">
        <h2>Active Sessions</h2>
        <div id="session-list"></div>
    </div>
    
    <script>
        const ws = new WebSocket('ws://localhost:8765');
        
        ws.onmessage = function(event) {
            const message = JSON.parse(event.data);
            
            if (message.type === 'initial_state' || message.type === 'metrics_update') {
                updateMetrics(message.data.metrics || message.data);
                
                if (message.data.sessions) {
                    updateSessions(message.data.sessions);
                }
            }
        };
        
        function updateMetrics(metrics) {
            document.getElementById('active-sessions').textContent = metrics.sessions_active || 0;
            document.getElementById('sessions-started').textContent = metrics.sessions_started || 0;
            document.getElementById('api-calls').textContent = metrics.api_calls || 0;
            document.getElementById('errors').textContent = metrics.errors_occurred || 0;
        }
        
        function updateSessions(sessions) {
            const sessionList = document.getElementById('session-list');
            sessionList.innerHTML = '';
            
            sessions.forEach(session => {
                const div = document.createElement('div');
                div.className = 'session';
                div.innerHTML = `
                    <strong>@${session.username}</strong> (ID: ${session.user_id})<br>
                    Stage: ${session.stage} | Duration: ${session.duration}min | Progress: ${session.completeness}%
                `;
                sessionList.appendChild(div);
            });
        }
        
        ws.onopen = function() {
            console.log('Connected to interview monitor');
        };
        
        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
    </script>
</body>
</html>
"""

# Save dashboard
with open('monitor_dashboard.html', 'w') as f:
    f.write(dashboard_html)
```

## Testing Your Integration

### Unit Tests

```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

@pytest.fixture
def mock_bot():
    """Create mock bot for testing"""
    bot = Mock()
    bot.sessions = {}
    bot.claude = Mock()
    bot.claude.generate_interview_response = AsyncMock()
    bot.prompt_manager = Mock()
    return bot

@pytest.mark.asyncio
async def test_sdk_create_session(mock_bot):
    """Test SDK session creation"""
    sdk = InterviewerSDK("fake_token", "fake_key")
    sdk.bot = mock_bot
    
    success = await sdk.create_interview_session(12345, "testuser")
    
    assert success == True
    assert 12345 in mock_bot.sessions
    assert mock_bot.sessions[12345].username == "testuser"

@pytest.mark.asyncio
async def test_sdk_send_message(mock_bot):
    """Test SDK message sending"""
    # Setup
    sdk = InterviewerSDK("fake_token", "fake_key")
    sdk.bot = mock_bot
    
    # Create session
    await sdk.create_interview_session(12345, "testuser")
    
    # Mock Claude response
    mock_response = {
        'interview_stage': 'profiling',
        'response': 'What is your background?',
        'metadata': {
            'question_depth': 1,
            'completeness': 20,
            'engagement_level': 'medium'
        }
    }
    mock_bot.claude.generate_interview_response.return_value = mock_response
    
    # Test message
    response = await sdk.send_message(12345, "I'm a developer")
    
    assert response['response'] == 'What is your background?'
    assert len(mock_bot.sessions[12345].conversation_history) == 2

def test_session_export():
    """Test session data export"""
    api = InterviewSessionAPI()
    
    # Mock session
    session = InterviewSession(
        user_id=12345,
        username="testuser",
        prompt_variant=PromptVariant.CONVERSATIONAL,
        current_stage=InterviewStage.PROFILING,
        stage_completeness={"profiling": 50},
        conversation_history=[
            {"role": "user", "content": "Hello", "timestamp": "2024-01-01T00:00:00"}
        ],
        start_time=datetime(2024, 1, 1),
        last_activity=datetime(2024, 1, 1),
        key_insights=["Experienced developer"]
    )
    
    api.session_manager.sessions[12345] = session
    
    # Test export
    json_export = api.export_session(12345, format="json")
    assert "testuser" in json_export
    assert "profiling" in json_export
    
    md_export = api.export_session(12345, format="markdown")
    assert "# Interview Session Report" in md_export
    assert "testuser" in md_export
```

### Integration Tests

```python
@pytest.mark.integration
async def test_full_interview_flow():
    """Test complete interview flow"""
    # Setup real bot with test credentials
    bot = AIInterviewerBot(
        telegram_token="test_token",
        anthropic_api_key="test_api_key"
    )
    
    # Mock Telegram objects
    user = Mock()
    user.id = 12345
    user.username = "testuser"
    
    message = Mock()
    message.text = "I'm ready to start"
    message.reply_text = AsyncMock()
    
    update = Mock()
    update.effective_user = user
    update.message = message
    
    context = Mock()
    
    # Test start command
    await bot.start_command(update, context)
    message.reply_text.assert_called_once()
    
    # Verify welcome message
    call_args = message.reply_text.call_args[0][0]
    assert "AI Professional Knowledge Interviewer" in call_args

@pytest.mark.integration 
def test_database_persistence():
    """Test database session persistence"""
    db_url = "sqlite:///test.db"
    db_manager = DatabaseSessionManager(db_url)
    
    # Create test session
    session = InterviewSession(
        user_id=12345,
        username="testuser",
        prompt_variant=PromptVariant.CONVERSATIONAL,
        current_stage=InterviewStage.PROFILING,
        stage_completeness={},
        conversation_history=[],
        start_time=datetime.now(),
        last_activity=datetime.now()
    )
    
    # Save and load
    db_manager.save_session(session)
    loaded_session = db_manager.load_session(12345)
    
    assert loaded_session is not None
    assert loaded_session.user_id == 12345
    assert loaded_session.username == "testuser"
    assert loaded_session.prompt_variant == PromptVariant.CONVERSATIONAL
```

### Load Testing

```bash
#!/bin/bash
# load_test.sh - Load test script

echo "🚀 Starting AI Interviewer Bot Load Test"

# Start bot in background
python bot_enhanced.py &
BOT_PID=$!

echo "Bot started with PID: $BOT_PID"

# Wait for bot to initialize
sleep 10

# Run concurrent user simulations
for i in {1..50}; do
    python -c "
import asyncio
import aiohttp

async def simulate_user():
    session = aiohttp.ClientSession()
    
    # Simulate user interactions
    for msg in ['Hello', 'I am a developer', 'I work in Python', 'I lead a team']:
        try:
            async with session.post('http://localhost:8080/webhook', 
                                  json={'message': {'text': msg, 'from': {'id': $i}}}) as resp:
                print(f'User $i: {resp.status}')
        except Exception as e:
            print(f'User $i error: {e}')
    
    await session.close()

asyncio.run(simulate_user())
" &
done

# Wait for all simulations to complete
wait

# Stop bot
kill $BOT_PID

echo "✅ Load test completed"
```

## Deployment Guide

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for session storage
RUN mkdir -p sessions completed_sessions

# Set environment variables
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

# Expose port for monitoring (optional)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Run the enhanced bot
CMD ["python", "bot_enhanced.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  ai-interviewer:
    build: .
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - LOG_LEVEL=INFO
      - SESSION_TIMEOUT_MINUTES=180
    volumes:
      - ./data/sessions:/app/sessions
      - ./data/completed:/app/completed_sessions
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
    
  # Optional: Database for persistence
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=interviews
      - POSTGRES_USER=interviewer
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  # Optional: Redis for caching
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### PythonAnywhere Deployment

```python
# wsgi.py for PythonAnywhere
import os
import sys
import asyncio
from threading import Thread

# Add project directory to path
sys.path.insert(0, '/home/yourusername/ai-interviewer')

from bot_enhanced import EnhancedAIInterviewerBot
from config import config

# Create bot instance
bot = EnhancedAIInterviewerBot(config.telegram_token, config.anthropic_api_key)

def run_bot():
    """Run bot in separate thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot.run()

# Start bot in background thread
bot_thread = Thread(target=run_bot, daemon=True)
bot_thread.start()

# WSGI application for web interface (optional)
from flask import Flask, jsonify

application = Flask(__name__)

@application.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'active_sessions': len(bot.sessions),
        'metrics': bot.metrics.get_metrics()
    })

if __name__ == '__main__':
    application.run()
```

### Production Configuration

```yaml
# production.yml - Production environment config
version: '3.8'

services:
  ai-interviewer:
    build: .
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=postgresql://user:pass@postgres:5432/interviews
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
      - LOG_FORMAT=json
    depends_on:
      - postgres
      - redis
    volumes:
      - app_data:/app/data
    networks:
      - app_network
    
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=interviews
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app_network
    
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - app_network
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ai-interviewer
    networks:
      - app_network

networks:
  app_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  app_data:
```

## Troubleshooting

### Common Issues

#### Bot Not Responding
```python
# Debug webhook issues
import requests

def test_webhook(bot_token, webhook_url):
    """Test webhook configuration"""
    url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    response = requests.get(url)
    
    webhook_info = response.json()
    print(f"Webhook URL: {webhook_info.get('result', {}).get('url')}")
    print(f"Last Error: {webhook_info.get('result', {}).get('last_error_message')}")
    
    # Test webhook endpoint
    if webhook_url:
        try:
            test_response = requests.post(webhook_url, json={
                "update_id": 1,
                "message": {
                    "message_id": 1,
                    "from": {"id": 12345, "is_bot": False, "first_name": "Test"},
                    "chat": {"id": 12345, "type": "private"},
                    "date": 1640995200,
                    "text": "/start"
                }
            })
            print(f"Webhook test: {test_response.status_code}")
        except Exception as e:
            print(f"Webhook test failed: {e}")
```

#### Session Issues
```python
def diagnose_session_issues():
    """Diagnose common session problems"""
    from bot_enhanced import SessionManager
    
    session_manager = SessionManager()
    
    print(f"Active sessions: {len(session_manager.sessions)}")
    print(f"Session storage directory: {session_manager.storage_dir}")
    
    # Check storage directory
    if not session_manager.storage_dir.exists():
        print("❌ Session storage directory doesn't exist")
        session_manager.storage_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Created session storage directory")
    
    # Check session files
    session_files = list(session_manager.storage_dir.glob("session_*.pkl"))
    print(f"Session files found: {len(session_files)}")
    
    for session_file in session_files:
        try:
            with open(session_file, 'rb') as f:
                session = pickle.load(f)
            print(f"✅ Valid session: {session_file.name} (User: {session.user_id})")
        except Exception as e:
            print(f"❌ Corrupted session: {session_file.name} ({e})")
```

#### Claude API Issues
```python
async def diagnose_claude_issues(api_key: str):
    """Diagnose Claude API connectivity"""
    import anthropic
    
    client = anthropic.Anthropic(api_key=api_key)
    
    try:
        # Test basic API call
        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        print("✅ Claude API connection successful")
        print(f"Response: {response.content[0].text}")
        
    except anthropic.APIError as e:
        print(f"❌ Claude API error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        if "authentication" in str(e).lower():
            print("💡 Check your ANTHROPIC_API_KEY")
        elif "rate limit" in str(e).lower():
            print("💡 Rate limit exceeded - implement backoff")
        elif "quota" in str(e).lower():
            print("💡 API quota exceeded - check billing")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
```

### Performance Monitoring

```python
import time
import psutil
from threading import Timer

class PerformanceMonitor:
    """Monitor bot performance metrics"""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.metrics_history = []
        
    def collect_system_metrics(self):
        """Collect system performance metrics"""
        process = psutil.Process()
        
        return {
            'timestamp': time.time(),
            'cpu_percent': process.cpu_percent(),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'threads': process.num_threads(),
            'open_files': len(process.open_files()),
            'active_sessions': len(self.bot.sessions),
            'uptime_hours': (time.time() - self.start_time) / 3600
        }
    
    def start_monitoring(self, interval=60):
        """Start periodic monitoring"""
        def monitor():
            metrics = self.collect_system_metrics()
            self.metrics_history.append(metrics)
            
            # Keep only last 24 hours
            cutoff = time.time() - (24 * 3600)
            self.metrics_history = [
                m for m in self.metrics_history 
                if m['timestamp'] > cutoff
            ]
            
            # Log if concerning metrics
            if metrics['memory_mb'] > 500:
                print(f"⚠️ High memory usage: {metrics['memory_mb']:.1f} MB")
            
            if metrics['cpu_percent'] > 80:
                print(f"⚠️ High CPU usage: {metrics['cpu_percent']:.1f}%")
            
            # Schedule next monitoring
            Timer(interval, monitor).start()
        
        monitor()
    
    def get_performance_report(self):
        """Generate performance report"""
        if not self.metrics_history:
            return "No metrics collected yet"
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 readings
        
        avg_cpu = sum(m['cpu_percent'] for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m['memory_mb'] for m in recent_metrics) / len(recent_metrics)
        max_sessions = max(m['active_sessions'] for m in recent_metrics)
        
        return f"""
Performance Report (Last {len(recent_metrics)} readings):
- Average CPU: {avg_cpu:.1f}%
- Average Memory: {avg_memory:.1f} MB
- Peak Sessions: {max_sessions}
- Uptime: {recent_metrics[-1]['uptime_hours']:.1f} hours
- Current Threads: {recent_metrics[-1]['threads']}
"""

# Usage
monitor = PerformanceMonitor(bot)
monitor.start_monitoring(interval=30)  # Every 30 seconds

# Get report
print(monitor.get_performance_report())
```

This comprehensive integration guide provides everything developers need to successfully integrate with, extend, and deploy the AI Interviewer Telegram Bot. The examples cover common use cases, patterns, and production scenarios.