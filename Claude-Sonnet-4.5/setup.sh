#!/bin/bash

# setup.sh - Environment setup script for Linux/macOS

echo "Setting up Python environment..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $PYTHON_VERSION"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Set environment variables (for testing purposes)
export THIRD_PARTY_API_KEY="test_api_key_12345"
export DB_PASSWORD="test_db_password_456"
export JWT_SECRET="test_jwt_secret_789"

echo ""
echo "Setup complete!"
echo "To activate the virtual environment, run: source venv/bin/activate"
echo "To set environment variables, run:"
echo "  export THIRD_PARTY_API_KEY='your_api_key'"
echo "  export DB_PASSWORD='your_password'"
echo "  export JWT_SECRET='your_secret'"
