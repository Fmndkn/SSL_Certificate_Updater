#!/bin/bash
# SSL Certificate Updater - Dependency Installer
# Usage: ./install_dependencies.sh

set -e

echo "=== SSL Certificate Updater - Dependency Installation ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is required but not installed.${NC}"
    echo "Please install Python 3.6 or higher from https://python.org"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}Python version: $PYTHON_VERSION${NC}"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}ERROR: pip3 is required but not installed.${NC}"
    echo "Please install pip for Python 3."
    exit 1
fi

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Not running in a virtual environment.${NC}"
    echo -e "${YELLOW}💡 Recommendation: Use virtual environment for better isolation${NC}"
    echo ""
    echo "To create and activate virtual environment:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo ""
    read -p "Do you want to create a virtual environment now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 -m venv venv
        echo -e "${GREEN}Virtual environment created. Activate with: source venv/bin/activate${NC}"
        echo -e "${YELLOW}Please activate the virtual environment and run this script again.${NC}"
        exit 0
    fi
else
    echo -e "${GREEN}✓ Running in virtual environment: $VIRTUAL_ENV${NC}"
fi

echo "Installing dependencies from requirements.txt..."

# Install dependencies with appropriate method
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Installing for current user only (--user flag)${NC}"
    pip3 install --user -r requirements.txt
else
    pip3 install -r requirements.txt
fi

# Verify installation
echo "Verifying installation..."
if python3 -c "import paramiko; print('✓ Paramiko installed successfully')" 2>/dev/null; then
    echo -e "${GREEN}✓ Paramiko installed successfully${NC}"
else
    echo -e "${RED}✗ Paramiko installation failed${NC}"
    exit 1
fi

if python3 -c "import cryptography; print('✓ Cryptography installed successfully')" 2>/dev/null; then
    echo -e "${GREEN}✓ Cryptography installed successfully${NC}"
else
    echo -e "${RED}✗ Cryptography installation failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=== Dependencies installed successfully! ===${NC}"
echo ""
echo -e "${GREEN}You can now:${NC}"
echo "  1. Run the script directly:"
echo "     python3 cert_updater.py"
echo ""
echo "  2. Or install as a package:"
if [ -z "$VIRTUAL_ENV" ]; then
    echo "     pip3 install --user ."
else
    echo "     pip3 install ."
fi
echo ""
echo "  3. Or make it executable and run:"
echo "     chmod +x cert_updater.py"
echo "     ./cert_updater.py"