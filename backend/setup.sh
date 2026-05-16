#!/bin/bash

# IBM Dexter Backend Setup Script
# This script automates the installation and testing process

set -e  # Exit on error

echo "🚀 IBM Dexter Backend Setup"
echo "================================"
echo ""

# Step 1: Clean up old installation
echo "📦 Step 1: Cleaning up old installation..."
if [ -d "venv" ]; then
    echo "   Removing old venv directory..."
    rm -rf venv
    echo "   ✅ Old venv removed"
else
    echo "   ✅ No old venv found"
fi
echo ""

# Step 2: Create fresh virtual environment
echo "🐍 Step 2: Creating fresh virtual environment..."
python3 -m venv venv
echo "   ✅ Virtual environment created"
echo ""

# Step 3: Activate virtual environment
echo "⚡ Step 3: Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Virtual environment activated"
echo ""

# Step 4: Upgrade pip
echo "📦 Step 4: Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "   ✅ Pip upgraded"
echo ""

# Step 5: Install minimal requirements
echo "📥 Step 5: Installing minimal requirements..."
echo "   This should take 2-3 minutes..."
pip install -r requirements.txt
echo "   ✅ Requirements installed"
echo ""

# Step 5.5: Ensure critical dependencies are installed
echo "🔧 Step 5.5: Verifying critical dependencies..."
echo "   Installing aiosqlite (async SQLite support)..."
pip install aiosqlite>=0.19.0 --quiet
echo "   Installing greenlet (SQLAlchemy async support)..."
pip install greenlet>=2.0.0 --quiet
echo "   Installing email-validator (Pydantic EmailStr support)..."
pip install email-validator>=2.0.0 --quiet
echo "   ✅ Critical dependencies verified"
echo ""

# Step 6: Configure environment
echo "⚙️  Step 6: Configuring environment..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "   ✅ .env file created from .env.example"
    else
        echo "   ⚠️  No .env.example found, skipping"
    fi
else
    echo "   ✅ .env file already exists"
fi
echo ""

# Step 7: Test installation
echo "🧪 Step 7: Testing installation..."
python3 -c "
import sys
print('   Testing imports...')

try:
    import fastapi
    print('   ✅ FastAPI imported')
except ImportError as e:
    print(f'   ❌ FastAPI import failed: {e}')
    sys.exit(1)

try:
    import sqlalchemy
    print('   ✅ SQLAlchemy imported')
except ImportError as e:
    print(f'   ❌ SQLAlchemy import failed: {e}')
    sys.exit(1)

try:
    import aiosqlite
    print('   ✅ aiosqlite imported (async SQLite)')
except ImportError as e:
    print(f'   ❌ aiosqlite import failed: {e}')
    sys.exit(1)

try:
    import greenlet
    print('   ✅ greenlet imported (SQLAlchemy async)')
except ImportError as e:
    print(f'   ❌ greenlet import failed: {e}')
    sys.exit(1)

try:
    import email_validator
    print('   ✅ email-validator imported (Pydantic EmailStr)')
except ImportError as e:
    print(f'   ❌ email-validator import failed: {e}')
    sys.exit(1)

try:
    import langchain
    print('   ✅ LangChain imported')
except ImportError as e:
    print(f'   ❌ LangChain import failed: {e}')
    sys.exit(1)

try:
    import ollama
    print('   ✅ Ollama imported')
except ImportError as e:
    print(f'   ❌ Ollama import failed: {e}')
    sys.exit(1)

print('   ✅ All core imports successful')
"
echo ""

# Step 8: Check if main.py exists
echo "📄 Step 8: Checking application files..."
if [ -f "main.py" ]; then
    echo "   ✅ main.py found"
else
    echo "   ❌ main.py not found"
    exit 1
fi
echo ""

# Step 9: Success message
echo "🎉 Setup Complete!"
echo "================================"
echo ""
echo "✅ Virtual environment created"
echo "✅ Dependencies installed (~50 packages)"
echo "✅ Environment configured"
echo "✅ Installation tested"
echo ""
echo "🚀 To start the server:"
echo "   source venv/bin/activate"
echo "   python3 -m uvicorn main:app --reload"
echo ""
echo "📚 API Documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "💡 To deactivate virtual environment:"
echo "   deactivate"
echo ""

# Made with Bob
