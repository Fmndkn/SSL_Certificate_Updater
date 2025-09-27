#!/bin/bash
# Simple installation script for SSL Certificate Updater

set -e

echo "🔧 SSL Certificate Updater - Installation"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.6+"
    exit 1
fi

# Create virtual environment (recommended)
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Installation completed!"
echo ""
echo "🚀 Usage:"
echo "   source venv/bin/activate"
echo "   python cert_updater.py"
echo ""
echo "📋 Or make the script executable:"
echo "   chmod +x cert_updater.py"
echo "   ./cert_updater.py"