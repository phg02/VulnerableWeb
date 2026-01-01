#!/bin/bash

# Flask Application Setup Script
# This script sets up the Flask application and initializes the database

echo "================================"
echo "Flask Application Setup"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
echo ""
echo "Initializing database..."
python3 << 'EOF'
from app import create_app
from app.database import init_db, get_db

app = create_app()
with app.app_context():
    get_db()
    init_db()
    print("Database initialized successfully!")
EOF

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "To start the application:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the development server:"
echo "     python run.py"
echo ""
echo "  3. Open browser to:"
echo "     http://127.0.0.1:5000"
echo ""
