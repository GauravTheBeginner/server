#!/bin/bash

# Staff Hub Backend - Quick Setup Script
echo "🚀 Setting up Staff Hub Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

echo "✓ Python is installed"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists, if not copy from .env.example
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "✓ Created .env file (using defaults)"
else
    echo "✓ .env file already exists"
fi

# Create migrations for api app
echo "📝 Creating migrations..."
python manage.py makemigrations api

# Run migrations
echo "🗄️ Setting up database..."
python manage.py migrate

# Seed database with sample data
echo "🌱 Seeding database with sample data..."
python manage.py seed_data

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "To start the development server, run:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "The API will be available at: http://127.0.0.1:8000/api/"
echo ""
echo "Login credentials:"
echo "  Email: admin@hrms.com"
echo "  Password: admin123"
echo ""
