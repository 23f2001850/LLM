# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Option 1: Docker (Easiest - Recommended)

1. **Prerequisites**: Install Docker Desktop for Windows
   - Download from: https://www.docker.com/products/docker-desktop

2. **Clone/Download this project**

3. **Configure environment**:
   ```powershell
   # Copy the example environment file
   Copy-Item .env.example .env
   
   # Edit .env and set your secret:
   # QUIZ_SECRET=your-unique-secret-key-here
   ```

4. **Start the application**:
   ```powershell
   docker-compose up -d
   ```

5. **Access the application**:
   - Dashboard: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

6. **Stop the application**:
   ```powershell
   docker-compose down
   ```

### Option 2: Local Development

#### Backend Setup (5 minutes)

1. **Prerequisites**:
   - Python 3.11 or higher
   - pip

2. **Navigate to backend**:
   ```powershell
   cd backend
   ```

3. **Create virtual environment**:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   playwright install chromium
   ```

5. **Set environment variable**:
   ```powershell
   $env:QUIZ_SECRET="your-secret-key"
   ```

6. **Run the server**:
   ```powershell
   python main.py
   ```
   
   Backend is now running at: http://localhost:8000

#### Dashboard Setup (5 minutes)

1. **Prerequisites**:
   - Node.js 20 or higher
   - npm

2. **Open a new PowerShell window and navigate to dashboard**:
   ```powershell
   cd dashboard
   ```

3. **Install dependencies**:
   ```powershell
   npm install
   ```

4. **Create environment file**:
   ```powershell
   echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local
   ```

5. **Run the dashboard**:
   ```powershell
   npm run dev
   ```
   
   Dashboard is now running at: http://localhost:3000

## 🧪 Testing the Application

### Using the Dashboard

1. Open http://localhost:3000
2. Fill in the quiz form:
   - Email: your-email@example.com
   - Secret: (the secret you set in .env)
   - Quiz URL: (a valid quiz URL)
3. Click "Submit Quiz"
4. Watch the live logs and history

### Using cURL

```powershell
curl -X POST http://localhost:8000/quiz `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@example.com\",\"secret\":\"your-secret-key\",\"url\":\"https://example.com/quiz\"}'
```

### Using Postman

1. Create a new POST request
2. URL: http://localhost:8000/quiz
3. Body (JSON):
   ```json
   {
     "email": "test@example.com",
     "secret": "your-secret-key",
     "url": "https://example.com/quiz"
   }
   ```
4. Send request

## 📊 Understanding the Response

A successful response looks like:

```json
{
  "status": "ok",
  "steps": [
    {"step": "validate_secret", "status": "success", "time": 0.01},
    {"step": "start_browser", "status": "success", "time": 1.5},
    {"step": "load_quiz_1", "url": "...", "status": "success", "time": 2.0},
    {"step": "parse_quiz_1", "question": "What is...", "status": "success", "time": 2.1},
    {"step": "download_data_1", "files": 2, "status": "success", "time": 3.5},
    {"step": "analyze_data_1", "status": "success", "time": 4.0},
    {"step": "submit_answer_1", "correct": true, "status": "success", "time": 4.5}
  ],
  "final_url": "https://example.com/submit",
  "final_answer": 42,
  "time_taken": 4.52
}
```

## 🔧 Common Issues

### Issue: Docker not starting

**Solution**: Make sure Docker Desktop is running and you have sufficient resources allocated.

### Issue: Port already in use

**Solution**: 
```powershell
# Change ports in docker-compose.yml
# Or stop the conflicting service
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

### Issue: Backend connection refused

**Solution**: 
- Check if backend is running: http://localhost:8000/health
- Verify NEXT_PUBLIC_BACKEND_URL in dashboard/.env.local
- Check firewall settings

### Issue: Module not found (Python)

**Solution**:
```powershell
cd backend
pip install -r requirements.txt
playwright install chromium
```

### Issue: Cannot find module (Node)

**Solution**:
```powershell
cd dashboard
Remove-Item -Recurse -Force node_modules
npm install
```

## 📈 Next Steps

1. **Customize**: Edit configuration in `.env`
2. **Deploy**: Follow deployment guide in README.md
3. **Integrate**: Use the API in your applications
4. **Monitor**: Check the dashboard for analytics
5. **Scale**: Add more workers or deploy to cloud

## 📚 More Information

- Full Documentation: See [README.md](README.md)
- Backend Details: See [backend/README.md](backend/README.md)
- Dashboard Details: See [dashboard/README.md](dashboard/README.md)
- API Documentation: http://localhost:8000/docs (when running)

## 🆘 Getting Help

If you encounter any issues:

1. Check this guide first
2. Review the main README.md
3. Check the logs:
   - Backend: `backend/quiz_bot.log`
   - Docker: `docker-compose logs`
4. Verify environment variables are set correctly

## ✅ Verification Checklist

Before reporting issues, verify:

- [ ] Docker Desktop is running (if using Docker)
- [ ] All dependencies are installed
- [ ] Environment variables are set correctly
- [ ] Ports 3000 and 8000 are available
- [ ] Python version is 3.11+
- [ ] Node version is 20+
- [ ] Firewall allows local connections

---

**You're all set! 🎉**

The LLM Analysis Quiz Bot is now ready to solve quizzes automatically!
