#!/bin/bash
# Quick Start Script for NOUS Intelligence Local Development

set -e

echo "🚀 NOUS Intelligence - Quick Start"
echo "=================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python $python_version detected"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo ""
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -e . > /dev/null 2>&1
echo "   ✅ Dependencies installed"

# Check for .env file
echo ""
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found"
    echo "   Copying .env.example to .env..."
    cp .env.example .env
    echo "   ✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - DATABASE_URL (use SQLite for local: sqlite:///instance/nous_local.db)"
    echo "   - SESSION_SECRET (generate with: python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
    echo "   - GEMINI_API_KEY (get free key from https://makersuite.google.com/app/apikey)"
    echo ""
    echo "Press Enter after you've edited .env..."
    read
else
    echo "✅ .env file exists"
fi

# Initialize database
echo ""
echo "🗄️  Initializing database..."
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('   ✅ Database initialized')"

# Seed demo data (optional)
echo ""
read -p "📊 Would you like to seed demo data? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 seed_demo_data.py
fi

# Run verification
echo ""
echo "🔍 Running pre-launch verification..."
python3 verify_sponsor_ready.py

echo ""
echo "✨ Setup complete!"
echo ""
echo "To start the server:"
echo "   python3 main.py"
echo ""
echo "Then visit: http://localhost:5000"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Project overview"
echo "   - DEPLOYMENT_QUICKSTART.md - Deployment guide"
echo "   - docs/AI_SETUP_GUIDE.md - AI configuration"
echo ""
