#!/bin/bash
# AI Interviewer Bot - PythonAnywhere Deployment Script
# Run this script in your PythonAnywhere bash console

set -e

echo "🚀 Starting AI Interviewer Bot deployment on PythonAnywhere..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're on PythonAnywhere
if [[ ! "$HOSTNAME" == *"pythonanywhere"* ]]; then
    echo "⚠️  Warning: This script is designed for PythonAnywhere"
    echo "   Current hostname: $HOSTNAME"
    echo "   Continue anyway? (y/N)"
    read -n 1 -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get username (should be your PythonAnywhere username)
USERNAME=$(whoami)
echo -e "${BLUE}[INFO]${NC} Deploying for user: $USERNAME"

# Set deployment directory
DEPLOY_DIR="/home/$USERNAME/ai-interviewer-bot"
echo -e "${BLUE}[INFO]${NC} Deployment directory: $DEPLOY_DIR"

# Clone or update repository
if [ -d "$DEPLOY_DIR" ]; then
    echo -e "${YELLOW}[UPDATE]${NC} Repository exists, updating..."
    cd "$DEPLOY_DIR"
    git pull origin main
else
    echo -e "${BLUE}[CLONE]${NC} Cloning repository..."
    cd "/home/$USERNAME"
    git clone https://github.com/evstrateg/ai-interviewer-bot.git
    cd "$DEPLOY_DIR"
fi

# Check Python version
echo -e "${BLUE}[INFO]${NC} Python version: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}[CREATE]${NC} Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}[ACTIVATE]${NC} Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}[UPGRADE]${NC} Upgrading pip..."
python -m pip install --upgrade pip

# Install minimal requirements for production
echo -e "${BLUE}[INSTALL]${NC} Installing core Python dependencies..."
pip install -r config/requirements_minimal.txt

# Ask about voice processing
echo ""
echo -e "${YELLOW}[OPTIONAL]${NC} Enable voice message processing? (y/N)"
echo "This will install additional dependencies (AssemblyAI, pydub, etc.)"
read -n 1 -r VOICE_REPLY
echo ""

if [[ $VOICE_REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}[INSTALL]${NC} Installing voice processing dependencies..."
    pip install -r config/requirements_voice.txt
    VOICE_ENABLED=true
    echo -e "${GREEN}[OK]${NC} Voice processing dependencies installed"
else
    VOICE_ENABLED=false
    echo -e "${YELLOW}[SKIP]${NC} Voice processing skipped"
fi

# Create necessary directories
echo -e "${BLUE}[MKDIR]${NC} Creating required directories..."
mkdir -p sessions completed_sessions logs data/{sessions,completed_sessions,logs}

# Setup environment file
if [ ! -f .env ]; then
    echo -e "${YELLOW}[ENV]${NC} Creating .env file from template..."
    cp .env.example .env
    
    # Configure voice processing setting
    if [ "$VOICE_ENABLED" = true ]; then
        echo "VOICE_PROCESSING_ENABLED=true" >> .env
        echo "ASSEMBLYAI_API_KEY=your_assemblyai_key_here" >> .env
    else
        echo "VOICE_PROCESSING_ENABLED=false" >> .env
    fi
    
    echo -e "${YELLOW}[IMPORTANT]${NC} =================================="
    echo "🔑 Please edit the .env file with your API keys:"
    echo "   nano .env"
    echo ""
    echo "Required variables:"
    echo "   TELEGRAM_BOT_TOKEN=your_telegram_bot_token"
    echo "   ANTHROPIC_API_KEY=your_anthropic_api_key"
    
    # Add voice processing note if enabled
    if [ "$VOICE_ENABLED" = true ]; then
        echo "   ASSEMBLYAI_API_KEY=your_assemblyai_api_key"
        echo ""
        echo "Voice processing is ENABLED. Make sure to:"
        echo "1. Set ASSEMBLYAI_API_KEY in .env"
        echo "2. Install FFmpeg: sudo apt install ffmpeg"
    else
        echo ""
        echo "Voice processing is DISABLED (saves resources)"
        echo "To enable later: set VOICE_PROCESSING_ENABLED=true in .env"
        echo "and install voice dependencies: pip install -r config/requirements_voice.txt"
    fi
    echo -e "${YELLOW}=================================="${NC}
else
    echo -e "${GREEN}[OK]${NC} .env file already exists"
fi

# Check if Always-On Tasks are available (paid accounts)
echo -e "${BLUE}[INFO]${NC} Checking PythonAnywhere account type..."
if [ -d "/var/services" ]; then
    echo -e "${GREEN}[PAID]${NC} Paid account detected - Always-On Tasks available"
    echo -e "${BLUE}[INFO]${NC} You can run the bot as an Always-On Task"
    echo "   Command: /home/$USERNAME/ai-interviewer-bot/venv/bin/python -m src.core.bot_enhanced"
    echo "   Working directory: /home/$USERNAME/ai-interviewer-bot"
else
    echo -e "${YELLOW}[FREE]${NC} Free account detected - use bash console to run bot"
    echo -e "${BLUE}[INFO]${NC} To run the bot manually:"
    echo "   cd $DEPLOY_DIR && source venv/bin/activate && python -m src.core.bot_enhanced"
fi

# Test configuration
echo -e "${BLUE}[TEST]${NC} Testing configuration..."
if python -c "from src.core.config import config; print('✅ Config loaded successfully')"; then
    echo -e "${GREEN}[OK]${NC} Configuration test passed"
else
    echo -e "${YELLOW}[WARNING]${NC} Configuration test failed - please check .env file"
fi

# Create run script
echo -e "${BLUE}[CREATE]${NC} Creating run script..."
cat > run_bot.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "🤖 Starting AI Interviewer Bot..."
# Run bot directly via Python module
python -m src.core.bot_enhanced
EOF
chmod +x run_bot.sh

echo -e "${GREEN}[SUCCESS]${NC} Deployment completed!"
echo ""
echo "🎯 Next Steps:"
echo "1. Edit environment variables: nano .env"
echo "2. Test the bot: ./run_bot.sh"
echo "3. For production:"
if [ -d "/var/services" ]; then
    echo "   • Set up Always-On Task in PythonAnywhere dashboard"
    echo "   • Command: $DEPLOY_DIR/venv/bin/python -m src.core.bot_enhanced"
    echo "   • Working directory: $DEPLOY_DIR"
else
    echo "   • Keep bash console open and run: ./run_bot.sh"
    echo "   • Consider upgrading to paid account for Always-On Tasks"
fi
echo ""
echo "📊 Monitoring:"
echo "   • Logs: tail -f logs/*.log (when available)"
echo "   • Sessions: ls -la sessions/"
echo "   • Completed interviews: ls -la completed_sessions/"
echo ""
echo -e "${GREEN}🚀 Ready to launch!${NC}"