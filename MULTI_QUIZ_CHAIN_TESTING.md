# Multi-Quiz Chain Testing Guide

## 🔗 Overview

This document explains how to test the **multi-quiz chaining** feature of the LLM Analysis Quiz Bot. The bot automatically follows quiz chains by detecting `next_url` or `url` fields in submit responses and continuing until no more URLs are provided.

---

## 📋 Test Files

Three test quiz files are provided in `quiz-tests/` directory:

| File | Quiz # | Task | Expected Answer | Next URL |
|------|--------|------|----------------|----------|
| `chain-quiz-1.html` | 1 of 3 | Sum of sales | **1420** | → chain-quiz-2.html |
| `chain-quiz-2.html` | 2 of 3 | Average temperature | **23.46** | → chain-quiz-3.html |
| `chain-quiz-3.html` | 3 of 3 | Maximum score | **98** | ❌ None (complete) |

---

## 🚀 How to Test

### Prerequisites

1. **Backend running** on `http://localhost:8000`
2. **Live Server** extension in VS Code OR any local HTTP server
3. **Secret key**: `my-quiz-secret-2025` (configured in `backend/.env`)

### Step 1: Start Live Server

Open VS Code and start Live Server for the quiz test files:

```
Right-click on quiz-tests/chain-quiz-1.html → "Open with Live Server"
```

This will serve files at: `http://127.0.0.1:5500/quiz-tests/`

### Step 2: Submit First Quiz URL to Backend

Use the dashboard at `http://localhost:3000` or cURL:

```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "my-quiz-secret-2025",
    "url": "http://127.0.0.1:5500/quiz-tests/chain-quiz-1.html"
  }'
```

### Step 3: Observe Automatic Chaining

The bot will automatically:

1. **Load Quiz 1** → Parse question and data
2. **Solve Quiz 1** → Calculate sum = 1420
3. **Submit Answer** → POST to form action URL
4. **Receive Response** with `next_url: chain-quiz-2.html`
5. **Load Quiz 2** automatically → Parse question and data
6. **Solve Quiz 2** → Calculate average = 23.46
7. **Submit Answer** → POST to form action URL
8. **Receive Response** with `next_url: chain-quiz-3.html`
9. **Load Quiz 3** automatically → Parse question and data
10. **Solve Quiz 3** → Find maximum = 98
11. **Submit Answer** → POST to form action URL
12. **Receive Response** with NO next_url (chain complete)
13. **Return Results** with all 3 quizzes solved

---

## 📊 Expected Backend Response

```json
{
  "status": "ok",
  "steps": [
    {"step": "validate_secret", "status": "success", "time": 0.01},
    {"step": "start_browser", "status": "success", "time": 1.2},
    
    // Quiz 1
    {"step": "load_quiz_1", "url": ".../chain-quiz-1.html", "status": "success", "time": 1.8},
    {"step": "parse_quiz_1", "question": "Calculate Total Sales", "status": "success", "time": 1.9},
    {"step": "download_data_1", "files": 1, "status": "success", "time": 2.0},
    {"step": "analyze_data_1", "status": "success", "time": 2.1},
    {"step": "submit_answer_1", "url": "...", "correct": true, "status": "success", "time": 2.5},
    {"step": "chain_continue_1", "next_url": ".../chain-quiz-2.html", "status": "continuing", "time": 2.5},
    
    // Quiz 2
    {"step": "load_quiz_2", "url": ".../chain-quiz-2.html", "status": "success", "time": 3.1},
    {"step": "parse_quiz_2", "question": "Calculate Average Temperature", "status": "success", "time": 3.2},
    {"step": "download_data_2", "files": 1, "status": "success", "time": 3.3},
    {"step": "analyze_data_2", "status": "success", "time": 3.4},
    {"step": "submit_answer_2", "url": "...", "correct": true, "status": "success", "time": 3.8},
    {"step": "chain_continue_2", "next_url": ".../chain-quiz-3.html", "status": "continuing", "time": 3.8},
    
    // Quiz 3
    {"step": "load_quiz_3", "url": ".../chain-quiz-3.html", "status": "success", "time": 4.4},
    {"step": "parse_quiz_3", "question": "Find Maximum Score", "status": "success", "time": 4.5},
    {"step": "download_data_3", "files": 1, "status": "success", "time": 4.6},
    {"step": "analyze_data_3", "status": "success", "time": 4.7},
    {"step": "submit_answer_3", "url": "...", "correct": true, "status": "success", "time": 5.1},
    {"step": "chain_complete", "total_quizzes": 3, "status": "success", "time": 5.1}
  ],
  "final_url": "http://localhost:3001/submit-chain-3",
  "final_answer": 98,
  "time_taken": 5.1,
  "quizzes_solved": 3,
  "chain_complete": true,
  "message": "Successfully solved 3 quiz(es) in chain"
}
```

---

## 🔍 What to Check

### ✅ Success Indicators

1. **All 3 quizzes solved**: `quizzes_solved: 3`
2. **Chain completed**: `chain_complete: true`
3. **Correct answers**:
   - Quiz 1: 1420
   - Quiz 2: 23.46
   - Quiz 3: 98
4. **Steps show chaining**:
   - `chain_continue_1` with next_url
   - `chain_continue_2` with next_url
   - `chain_complete` at the end
5. **Total time under 3 minutes**: `time_taken < 180`

### ❌ Failure Scenarios

1. **Stops after first quiz**: Check if `submitter.py` extracts `next_url` correctly
2. **Wrong answers**: Verify data parsing and analysis logic
3. **Timeout**: Chain took too long (>3 minutes)
4. **Missing URL extraction**: Bot doesn't detect next quiz URL

---

## 🧪 Backend Logs

Watch backend logs for chain progress:

```
INFO:     Starting quiz for test@example.com: http://127.0.0.1:5500/quiz-tests/chain-quiz-1.html
INFO:     Processing quiz 1: http://127.0.0.1:5500/quiz-tests/chain-quiz-1.html
INFO:     Computed answer: 1420
INFO:     Submitting answer to http://localhost:3001/submit-chain-1
INFO:     Next quiz URL detected: http://127.0.0.1:5500/quiz-tests/chain-quiz-2.html
INFO:     ✓ Quiz 1 correct. Next quiz URL: http://127.0.0.1:5500/quiz-tests/chain-quiz-2.html
INFO:     Processing quiz 2: http://127.0.0.1:5500/quiz-tests/chain-quiz-2.html
INFO:     Computed answer: 23.46
INFO:     Submitting answer to http://localhost:3001/submit-chain-2
INFO:     Next quiz URL detected: http://127.0.0.1:5500/quiz-tests/chain-quiz-3.html
INFO:     ✓ Quiz 2 correct. Next quiz URL: http://127.0.0.1:5500/quiz-tests/chain-quiz-3.html
INFO:     Processing quiz 3: http://127.0.0.1:5500/quiz-tests/chain-quiz-3.html
INFO:     Computed answer: 98
INFO:     Submitting answer to http://localhost:3001/submit-chain-3
INFO:     ✓ Chain completed successfully after 3 quiz(es)
INFO:     ✓ Quiz chain completed: 3 quiz(es) solved in 5.1s
```

---

## 🎯 Manual Testing with Browser

You can also open the quiz files manually to see their behavior:

1. Open `chain-quiz-1.html` in browser
2. Fill email and answer `1420`
3. Click "Submit Answer"
4. See alert showing JSON response with `next_url`
5. Note the URL points to `chain-quiz-2.html`

Repeat for quiz 2 and 3 to understand the chain flow.

---

## 🔧 Troubleshooting

### Problem: Bot stops after first quiz

**Solution**: Check `submitter.py` logs. Verify the `_extract_next_url()` method is detecting the URL field.

### Problem: Wrong answers

**Solution**: Check `analyzer.py` logs. Verify data parsing and analysis type detection.

### Problem: Form submission fails

**Solution**: The test quiz files use client-side JavaScript for simulation. In production, they should POST to a real server endpoint.

### Problem: Next URL not absolute

**Solution**: The bot handles relative URLs. Ensure the base URL is correct when constructing next quiz URLs.

---

## 🎉 Success Criteria

The multi-quiz chaining feature is working correctly when:

1. ✅ Bot solves Quiz 1 and automatically continues to Quiz 2
2. ✅ Bot solves Quiz 2 and automatically continues to Quiz 3
3. ✅ Bot solves Quiz 3 and detects chain completion (no next URL)
4. ✅ Response includes `quizzes_solved: 3` and `chain_complete: true`
5. ✅ All steps are logged in the `steps` array
6. ✅ Total time is under 3 minutes

---

## 📚 Additional Resources

- **Main README**: `README.md` - Complete project documentation
- **API Specification**: See `README.md` API section
- **Architecture**: See `README.md` Architecture section
- **Code Reference**:
  - `backend/main.py` - Main chaining loop
  - `backend/solver/submitter.py` - Next URL extraction
  - `backend/solver/utils.py` - Timeout management

---

**Happy Testing! 🚀**

If you encounter issues, check backend logs with `python main.py` and dashboard console with browser DevTools.
