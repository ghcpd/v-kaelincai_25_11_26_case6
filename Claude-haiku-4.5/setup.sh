#!/bin/bash

# Setup script for Linux/macOS
# This script sets up the environment for running the Flask application

set -e

echo "=== Setting up secure Flask application ==="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please update .env file with actual values"
fi

# Create logs directory
mkdir -p logs

echo "=== Setup complete ==="
echo "To activate the environment, run: source venv/bin/activate"
echo "To run the application, run: python inputs.py"
