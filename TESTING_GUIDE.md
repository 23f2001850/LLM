# 🧪 LLM Analysis Quiz Bot - Testing Guide

## ✅ What Your Website Does

Your quiz bot automatically:
1. **Visits quiz pages** with questions and data sources
2. **Downloads data** (CSV, PDF, images, Excel files)
3. **Analyzes the data** using Python (pandas, numpy)
4. **Generates visualizations** if needed
5. **Computes the answer** based on the question
6. **Submits the answer** automatically

---

## 📋 Step-by-Step Testing Instructions

### **STEP 1: Verify Both Servers are Running**

✅ **Backend API** should show:
```
INFO: Uvicorn running on http://0.0.0.0:8000
```

✅ **Dashboard** should show:
```
✓ Ready in 2.9s
Local: http://localhost:3000
```

---

### **STEP 2: Open the Dashboard**

1. Go to your browser
2. Open: **http://localhost:3000**
3. You should see:
   - Header with "LLM Analysis Quiz Bot Dashboard"
   - Stats showing "Total Quizzes: 0"
   - A form to enter quiz URLs
   - Empty history table

---

### **STEP 3: Test with Local Sample Quiz**

**Method A: Use the Test Quiz File**
1. Open file: `c:\Krishna_Jain\LLM\test-quiz.html` in your browser
2. Copy the URL from browser address bar (should be like: `file:///c:/Krishna_Jain/LLM/test-quiz.html`)
3. Go back to dashboard (http://localhost:3000)
4. Paste the URL in "Quiz URL" field
5. Click "Solve Quiz" button
6. Watch the "Live Logs" section update in real-time
7. After 10-30 seconds, check "History" section for results

**What Should Happen:**
- ✅ Bot visits the quiz page
- ✅ Extracts question: "What is the total sum..."
- ✅ Downloads sales-data.csv
- ✅ Calculates: 150+200+175+225+300 = 1050
- ✅ Submits answer: "1050"
- ✅ Shows success in history

---

### **STEP 4: Test API Directly (Advanced)**

You can test the backend API directly using PowerShell:

```powershell
# Test with a quiz URL
$body = @{
    quiz_url = "file:///c:/Krishna_Jain/LLM/test-quiz.html"
    secret_key = "your-secret-key-12345"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/quiz" -Method POST -Body $body -ContentType "application/json"
```

---

### **STEP 5: Check Features**

#### **Dashboard Features to Test:**

1. **Theme Toggle** 🌙
   - Click moon/sun icon in header
   - Page should switch between light and dark mode

2. **Statistics** 📊
   - After submitting quizzes, numbers should update
   - Total Quizzes count increases
   - Success Rate shows percentage

3. **Live Logs** 🔴
   - Shows real-time progress while solving
   - Updates every few seconds
   - Shows steps: "Visiting page", "Downloading data", etc.

4. **History Table** 📜
   - Shows all submitted quizzes
   - Displays: Quiz URL, Answer, Status, Timestamp
   - Color-coded: Green for success, Red for failed

5. **Responsive Design** 📱
   - Resize browser window
   - Layout should adapt to smaller screens

---

### **STEP 6: Test with Real Quiz URLs**

If you have actual quiz URLs (from courses, assignments, etc.):

1. Make sure the quiz page has:
   - A clear question
   - Data sources (CSV links, PDF links, or embedded data)
   - A submit form

2. Enter the URL in dashboard
3. Add your secret key if required
4. Click "Solve Quiz"
5. Monitor progress in Live Logs

---

## 🔍 What to Look For

### ✅ **Success Indicators:**
- History shows "Success" status (green)
- Answer is computed and submitted
- Logs show all steps completed
- Stats update correctly

### ❌ **Failure Indicators:**
- History shows "Failed" status (red)
- Error messages in logs
- Browser automation issues
- Data parsing errors

---

## 🐛 Common Issues & Solutions

### **Issue 1: "Failed to connect"**
**Solution:** Make sure backend is running on http://localhost:8000

### **Issue 2: "Browser launch failed"**
**Solution:** Run: `playwright install chromium` in backend directory

### **Issue 3: "Cannot download data"**
**Solution:** Check if quiz page has valid data source links

### **Issue 4: "Parsing error"**
**Solution:** Quiz page might have unusual structure - check logs for details

---

## 📊 Understanding the Results

### **Success Response:**
```json
{
  "success": true,
  "quiz_url": "...",
  "question": "What is the total...",
  "answer": "1050",
  "data_sources": ["sales-data.csv"],
  "submission_status": "success"
}
```

### **Failed Response:**
```json
{
  "success": false,
  "error": "Unable to extract question",
  "quiz_url": "..."
}
```

---

## 🎯 Next Steps

1. ✅ Test with sample quiz (test-quiz.html)
2. ✅ Verify all dashboard features work
3. ✅ Test with real quiz URLs from your courses
4. ✅ Check history and logs for insights
5. ✅ Export results if needed

---

## 📝 Quick Test Checklist

- [ ] Backend server running (port 8000)
- [ ] Dashboard accessible (port 3000)
- [ ] Sample quiz opens in browser
- [ ] Quiz URL submitted successfully
- [ ] Live logs showing progress
- [ ] History table updated
- [ ] Stats showing correct numbers
- [ ] Theme toggle works
- [ ] No errors in browser console

---

## 🆘 Need Help?

If something doesn't work:
1. Check both terminal windows for errors
2. Look at Live Logs in dashboard
3. Verify quiz URL is accessible
4. Ensure data sources are downloadable
5. Check browser console (F12) for errors

---

**Your application is fully functional and ready to solve quizzes! 🚀**
