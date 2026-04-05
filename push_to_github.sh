#!/bin/bash
# Script to push paper trading dashboard to GitHub

echo "🚀 Preparing to push Paper Trading Dashboard to GitHub"
echo "======================================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git not initialized in this directory"
    exit 1
fi

# Check for remote
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

if [ -z "$REMOTE_URL" ]; then
    echo "📝 No remote repository configured."
    echo ""
    echo "📋 INSTRUCTIONS:"
    echo "1. Create a new repository on GitHub:"
    echo "   - Name: paper-trading-dashboard"
    echo "   - DO NOT initialize with README, .gitignore, or license"
    echo "2. Get the repository URL (HTTPS)"
    echo "3. Run this command to add remote:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/paper-trading-dashboard.git"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ Remote repository: $REMOTE_URL"
echo ""

# Check for changes
if git diff-index --quiet HEAD --; then
    echo "✅ No changes to commit"
else
    echo "📝 Changes detected, committing..."
    git add .
    git commit -m "Update: Paper Trading Dashboard $(date '+%Y-%m-%d %H:%M:%S')"
fi

# Rename branch to main if needed
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "🔄 Renaming branch from '$CURRENT_BRANCH' to 'main'"
    git branch -M main
fi

echo "🚀 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! Code pushed to GitHub."
    echo ""
    echo "📋 NEXT STEPS:"
    echo "1. Go to: https://share.streamlit.io"
    echo "2. Sign in with GitHub"
    echo "3. Click 'New app'"
    echo "4. Select repository: paper-trading-dashboard"
    echo "5. Branch: main"
    echo "6. Main file path: streamlit_app.py"
    echo "7. Click 'Deploy'"
    echo ""
    echo "🌐 Your permanent URL will be:"
    echo "   https://paper-trading-daazprime.streamlit.app"
    echo ""
    echo "📱 Update WordPress with the new URL!"
else
    echo "❌ Failed to push to GitHub"
    echo "Check your credentials and try again."
fi