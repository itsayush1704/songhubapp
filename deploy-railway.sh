#!/bin/bash

# SongHub Railway Deployment Script
# This script helps deploy your SongHub app to Railway

echo "🚂 SongHub Railway Deployment Script"
echo "====================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
else
    echo "✅ Railway CLI found"
fi

# Check if user is logged in
echo "🔐 Checking Railway authentication..."
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged in to Railway. Please login:"
    railway login
else
    echo "✅ Already logged in to Railway"
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Initializing..."
    git init
    git add .
    git commit -m "Initial commit for Railway deployment"
else
    echo "✅ Git repository found"
fi

# Check if we have a Railway project
if [ ! -f "railway.toml" ] && [ ! -f ".railway" ]; then
    echo "🚀 Initializing Railway project..."
    railway init
else
    echo "✅ Railway project already initialized"
fi

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "🌐 Your app should be available at the URL shown above"
    echo "📊 Monitor your app: https://railway.app/dashboard"
else
    echo "❌ Deployment failed. Check the logs above for details."
    exit 1
fi

echo ""
echo "🎉 SongHub is now live on Railway!"
echo "📝 Next steps:"
echo "   1. Test your app at the provided URL"
echo "   2. Set up custom domain (optional)"
echo "   3. Monitor performance in Railway dashboard"
echo "   4. Set up environment variables if needed"