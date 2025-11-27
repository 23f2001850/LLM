#!/bin/bash
# Quick Deployment Script for Render.com
# This helps prepare your repository for deployment

echo "🚀 Preparing LLM Analysis Quiz Bot for Deployment..."
echo ""

# Check if .env exists in backend
if [ -f "backend/.env" ]; then
    echo "✅ backend/.env found"
else
    echo "⚠️  Warning: backend/.env not found"
    echo "   Creating template..."
    echo "QUIZ_SECRET=my-quiz-secret-2025" > backend/.env
    echo "MAX_QUIZ_TIME=180" >> backend/.env
    echo "✅ Created backend/.env"
fi

# Check if .gitignore exists
if [ -f ".gitignore" ]; then
    echo "✅ .gitignore found"
else
    echo "❌ .gitignore missing - create it!"
fi

# Check if LICENSE exists
if [ -f "LICENSE" ]; then
    echo "✅ LICENSE found"
else
    echo "❌ LICENSE missing - add MIT License!"
fi

# Check if requirements.txt exists
if [ -f "backend/requirements.txt" ]; then
    echo "✅ backend/requirements.txt found"
else
    echo "❌ backend/requirements.txt missing!"
fi

echo ""
echo "📋 Pre-Deployment Checklist:"
echo "1. [ ] .gitignore includes backend/.env"
echo "2. [ ] LICENSE file exists (MIT)"
echo "3. [ ] All code committed to git"
echo "4. [ ] Repository pushed to GitHub"
echo "5. [ ] Repository is PUBLIC"
echo ""
echo "🌐 Next Steps:"
echo "1. Go to https://render.com"
echo "2. Create new Web Service"
echo "3. Connect your GitHub repo"
echo "4. Use these settings:"
echo "   Build Command: cd backend && pip install -r requirements.txt && playwright install chromium"
echo "   Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port \$PORT"
echo "   Environment Variables:"
echo "     QUIZ_SECRET=my-quiz-secret-2025"
echo "     MAX_QUIZ_TIME=180"
echo ""
echo "✅ Ready to deploy!"
