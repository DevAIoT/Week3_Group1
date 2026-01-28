#!/usr/bin/env bash
set -euo pipefail

echo "=== GestureRating Setup ==="

# Install system dependencies
echo "Installing system packages..."
sudo apt-get update
sudo apt-get install -y libatlas-base-dev python3-venv

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setup complete. Activate with: source venv/bin/activate"
echo "Run with: python main.py"
