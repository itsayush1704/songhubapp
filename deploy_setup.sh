#!/bin/bash

# SongHub PythonAnywhere Deployment Setup Script
# Run this script in your PythonAnywhere Bash console after uploading files

echo "🚀 Starting SongHub deployment setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    print_error "app.py not found. Please run this script from the songhub directory."
    exit 1
fi

print_status "Found app.py, proceeding with setup..."

# Get PythonAnywhere username
USERNAME=$(whoami)
print_status "Detected username: $USERNAME"

# Create virtual environment
print_status "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3.10 -m venv venv
    if [ $? -eq 0 ]; then
        print_status "Virtual environment created successfully"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        print_status "Requirements installed successfully"
    else
        print_error "Failed to install some requirements"
        print_warning "Please check the error messages above and install missing packages manually"
    fi
else
    print_error "requirements.txt not found"
    exit 1
fi

# Update WSGI file with correct username
print_status "Updating WSGI configuration..."
if [ -f "wsgi.py" ]; then
    sed -i "s/yourusername/$USERNAME/g" wsgi.py
    print_status "WSGI file updated with username: $USERNAME"
else
    print_warning "wsgi.py not found. You'll need to create it manually."
fi

# Create logs directory
print_status "Creating logs directory..."
mkdir -p logs

# Set up data directory with proper permissions
print_status "Setting up data directory..."
mkdir -p data
chmod 755 data

# Create a simple test script
print_status "Creating test script..."
cat > test_app.py << 'EOF'
#!/usr/bin/env python3
"""
Simple test script to verify the application works
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    print("✅ App import successful")
    
    # Test basic route
    with app.test_client() as client:
        response = client.get('/health')
        if response.status_code == 200:
            print("✅ Health check endpoint working")
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please check your dependencies and try again.")
except Exception as e:
    print(f"❌ Error: {e}")
EOF

# Make test script executable
chmod +x test_app.py

# Run basic tests
print_status "Running basic application tests..."
python test_app.py

# Create environment file template
print_status "Creating environment file template..."
cat > .env.example << 'EOF'
# Environment variables for SongHub
# Copy this file to .env and fill in your values

# Flask configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# Add any other environment variables your app needs
# API_KEY=your-api-key
# DATABASE_URL=your-database-url
EOF

print_status "Environment template created as .env.example"

# Display next steps
echo ""
print_status "Setup completed! Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Create a new web app (Manual configuration, Python 3.10)"
echo "3. Set source code directory to: /home/$USERNAME/songhub"
echo "4. Set working directory to: /home/$USERNAME/songhub"
echo "5. Update WSGI configuration file to: /home/$USERNAME/songhub/wsgi.py"
echo "6. Add static files mapping: URL=/static/, Directory=/home/$USERNAME/songhub/static/"
echo "7. Set up environment variables in the Web tab if needed"
echo "8. Reload your web app"
echo ""
print_status "Your app should be available at: https://$USERNAME.pythonanywhere.com"
echo ""
print_warning "Don't forget to:"
echo "- Copy .env.example to .env and configure your environment variables"
echo "- Test your application thoroughly"
echo "- Check the error logs if something doesn't work"
echo ""
print_status "Deployment setup complete! 🎉"