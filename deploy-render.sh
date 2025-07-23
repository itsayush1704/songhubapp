#!/bin/bash

# SongHub Render Deployment Script
# This script prepares and deploys your SongHub app to Render

echo "🎵 SongHub Render Deployment Script"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_error "Git repository not found. Please initialize git first:"
    echo "  git init"
    echo "  git remote add origin <your-repo-url>"
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found!"
    exit 1
fi

# Check if gunicorn is in requirements
if ! grep -q "gunicorn" requirements.txt; then
    print_warning "gunicorn not found in requirements.txt"
    print_status "Adding gunicorn to requirements.txt..."
    echo "gunicorn==21.2.0" >> requirements.txt
fi

print_status "Checking app.py for Render compatibility..."

# Check if app.py exists
if [ ! -f "app.py" ]; then
    print_error "app.py not found!"
    exit 1
fi

# Check for health endpoint
if ! grep -q "/health" app.py; then
    print_warning "Health endpoint not found in app.py"
    print_status "Consider adding a health check endpoint for monitoring"
fi

print_status "Preparing files for deployment..."

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    print_status "Creating .gitignore..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Data files (keep local only)
*.pkl
*.db
*.sqlite

# Temporary files
tmp/
temp/
EOF
    print_success ".gitignore created"
fi

# Check git status
print_status "Checking git status..."
git status --porcelain

if [ -n "$(git status --porcelain)" ]; then
    print_status "Adding files to git..."
    git add .
    
    # Get commit message from user or use default
    if [ -z "$1" ]; then
        COMMIT_MSG="Prepare SongHub for Render deployment"
    else
        COMMIT_MSG="$1"
    fi
    
    print_status "Committing changes: $COMMIT_MSG"
    git commit -m "$COMMIT_MSG"
    
    print_status "Pushing to remote repository..."
    if git push; then
        print_success "Code pushed successfully!"
    else
        print_error "Failed to push to remote repository"
        print_status "Please check your git remote configuration:"
        echo "  git remote -v"
        exit 1
    fi
else
    print_status "No changes to commit"
fi

print_success "Deployment preparation complete!"
echo ""
echo "🚀 Next Steps:"
echo "1. Go to https://dashboard.render.com"
echo "2. Click 'New' → 'Web Service'"
echo "3. Connect your GitHub repository"
echo "4. Use these settings:"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: gunicorn app:app --bind 0.0.0.0:\$PORT"
echo "   - Python Version: 3.10.12"
echo "5. Add environment variables:"
echo "   - PYTHON_VERSION: 3.10.12"
echo "   - SECRET_KEY: [generate random]"
echo "   - FLASK_ENV: production"
echo ""
print_success "Your SongHub app will be live at: https://your-app-name.onrender.com"
echo ""
echo "📖 For detailed instructions, see: RENDER_DEPLOYMENT.md"
echo "🎵 Happy deploying!"