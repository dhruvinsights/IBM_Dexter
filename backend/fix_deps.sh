#!/bin/bash

# ============================================================================
# IBM DEXTER - Quick Dependency Fix Script
# ============================================================================
# This script installs missing critical dependencies that are commonly missed
# during initial setup.
# ============================================================================

set -e  # Exit on error

echo "🔧 IBM DEXTER - Fixing Missing Dependencies"
echo "============================================"
echo ""

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found!"
    echo "   Please run this script from the backend directory."
    exit 1
fi

# Activate venv if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
    echo "   ✅ Virtual environment activated"
    echo ""
fi

# Install critical missing dependencies
echo "📦 Installing critical dependencies..."
echo ""

echo "   Installing aiosqlite (async SQLite support)..."
pip install aiosqlite>=0.19.0 --quiet

echo "   Installing greenlet (SQLAlchemy async support)..."
pip install greenlet>=2.0.0 --quiet

echo "   Installing email-validator (Pydantic EmailStr support)..."
pip install email-validator>=2.0.0 --quiet

echo ""
echo "✅ Critical dependencies installed successfully!"
echo ""

# Test imports
echo "🧪 Testing imports..."
echo ""

if python3 test_deps.py; then
    echo ""
    echo "============================================"
    echo "✅ ALL DEPENDENCIES FIXED!"
    echo "============================================"
    echo ""
    echo "🚀 You can now start the server:"
    echo "   ./start.sh"
    echo ""
    echo "   Or manually:"
    echo "   python3 -m uvicorn main:app --reload"
    echo ""
else
    echo ""
    echo "============================================"
    echo "⚠️  Some dependencies still missing"
    echo "============================================"
    echo ""
    echo "🔧 Try full reinstall:"
    echo "   pip install -r requirements.txt"
    echo ""
    exit 1
fi

# Made with Bob
