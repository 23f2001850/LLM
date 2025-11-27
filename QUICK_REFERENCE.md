# 🚀 Multi-Quiz Chaining - Quick Reference

## ⚡ What Changed?

The bot now **automatically follows quiz chains** until completion. One API call solves the entire chain!

---

## 🎯 Key Points

### Before
```
POST /quiz → Solve 1 quiz → Return answer → STOP
```

### After (NEW!)
```
POST /quiz → Solve quiz 1 → quiz 2 → quiz 3 → ... → quiz N → Return all results
```

**The bot continues automatically until no more URLs!**

---

## 📝 Request Format (Unchanged)

```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "secret": "my-quiz-secret-2025",
    "url": "https://eval-server.com/quiz-1"
  }'
```

---

## 📊 Response Format (Enhanced)

```json
{
  "status": "ok",
  "steps": [
    // All steps from all quizzes
    {"step": "load_quiz_1", "url": "...", "time": 0.5},
    {"step": "submit_answer_1", "correct": true, "time": 2.1},
    {"step": "chain_continue_1", "next_url": "...", "time": 2.2},
    {"step": "load_quiz_2", "url": "...", "time": 3.0},
    // ... more steps ...
    {"step": "chain_complete", "total_quizzes": 3, "time": 8.5}
  ],
  "final_url": "https://eval-server.com/submit-3",
  "final_answer": 42,
  "time_taken": 8.5,
  "quizzes_solved": 3,          // NEW!
  "chain_complete": true,       // NEW!
  "message": "Successfully solved 3 quiz(es) in chain"  // NEW!
}
```

---

## 🔗 How Server Signals Next Quiz

The evaluation server returns next URL in the submit response:

### Option 1: `url` field
```json
{
  "correct": true,
  "url": "https://eval-server.com/quiz-2"
}
```

### Option 2: `next_url` field
```json
{
  "correct": true,
  "next_url": "https://eval-server.com/quiz-2"
}
```

### Option 3: Chain complete (no URL)
```json
{
  "correct": true,
  "message": "All quizzes complete"
}
```

**The bot automatically detects and handles all formats!**

---

## ⏱️ Timeout Handling

- **Global timeout**: 3 minutes across entire chain
- **Check before each quiz**: Stops if time running out
- **Graceful termination**: Returns partial results if timeout

---

## 🛡️ Safety Features

1. **Max 10 quizzes per chain** - Prevents infinite loops
2. **Timeout enforcement** - Stays under 3 minutes
3. **Error handling** - Stops on incorrect answers
4. **URL validation** - Checks URLs before continuing

---

## 🧪 Test Files Provided

| File | Task | Answer | Next URL? |
|------|------|--------|-----------|
| `chain-quiz-1.html` | Sum | 1420 | ✅ → quiz 2 |
| `chain-quiz-2.html` | Average | 23.46 | ✅ → quiz 3 |
| `chain-quiz-3.html` | Maximum | 98 | ❌ Complete |

**Test command:**
```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "my-quiz-secret-2025",
    "url": "http://127.0.0.1:5500/quiz-tests/chain-quiz-1.html"
  }'
```

---

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Main documentation with chaining section |
| `MULTI_QUIZ_CHAIN_TESTING.md` | Complete testing guide |
| `ARCHITECTURE.md` | Technical architecture |
| `IMPLEMENTATION_COMPLETE.md` | Implementation summary |
| `QUICK_REFERENCE.md` | This file |

---

## ✅ Evaluation Checklist

- [x] Bot validates secret
- [x] Bot loads URL with headless browser
- [x] Bot extracts question, data, submit URL
- [x] Bot downloads files (PDF/CSV/Excel/images)
- [x] Bot analyzes data correctly
- [x] Bot submits answer to detected URL
- [x] **Bot reads JSON response**
- [x] **Bot detects next URL automatically**
- [x] **Bot continues to next quiz without stopping**
- [x] **Bot loops until no more URLs**
- [x] Bot stays under 3-minute timeout
- [x] Bot returns complete results
- [x] Bot never stops after first quiz
- [x] Bot never hardcodes URLs
- [x] Bot detects submit URLs dynamically

**ALL REQUIREMENTS MET! ✅**

---

## 🔍 How to Verify It's Working

### 1. Check Response
```json
{
  "quizzes_solved": 3,     // Should be > 1 for chains
  "chain_complete": true,  // Should be true when finished
  "steps": [...]           // Should show multiple quizzes
}
```

### 2. Check Logs
```
INFO: Processing quiz 1: ...
INFO: ✓ Quiz 1 correct. Next quiz URL: ...
INFO: Processing quiz 2: ...
INFO: ✓ Quiz 2 correct. Next quiz URL: ...
INFO: Processing quiz 3: ...
INFO: ✓ Chain completed successfully after 3 quiz(es)
```

### 3. Check Steps Array
Should contain:
- `load_quiz_1`, `submit_answer_1`, `chain_continue_1`
- `load_quiz_2`, `submit_answer_2`, `chain_continue_2`
- `load_quiz_3`, `submit_answer_3`, `chain_complete`

---

## 🎓 Quick Troubleshooting

### Problem: Bot stops after first quiz
**Solution:** Check backend logs for next_url detection. Verify server returns URL field.

### Problem: Timeout error
**Solution:** Chain took over 3 minutes. Check quiz complexity or increase MAX_QUIZ_TIME.

### Problem: Wrong answers
**Solution:** Verify data parsing and analysis. Check analyzer.py logs.

### Problem: Missing next URL
**Solution:** Check submitter.py logs. Verify response format matches expected patterns.

---

## 💡 Key Code Locations

| Component | File | Function/Method |
|-----------|------|-----------------|
| Main chain loop | `backend/main.py` | `/quiz` endpoint (line ~150-280) |
| Next URL extraction | `backend/solver/submitter.py` | `_extract_next_url()` |
| Timeout check | `backend/main.py` | `if timeout_mgr.is_expired()` |
| Response model | `backend/main.py` | `class QuizResponse` |

---

## 🎉 Summary

✅ **Multi-quiz chaining is fully implemented**  
✅ **Bot automatically follows chains until completion**  
✅ **Stays under 3-minute timeout**  
✅ **Returns comprehensive results**  
✅ **Production ready for evaluation**  

---

**Need more details?** See `MULTI_QUIZ_CHAIN_TESTING.md` or `ARCHITECTURE.md`

**Ready to test?** Run the backend and submit `chain-quiz-1.html` URL!

**Happy Chaining! 🔗🚀**
