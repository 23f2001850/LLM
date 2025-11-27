# 🧪 Quiz Test Suite - Testing Guide

## 📋 10 Different Quiz Types

I've created 10 quiz HTML files to test different analysis capabilities:

### **Quiz 1: Average Calculation** 
- File: `quiz1-average.html`
- Question: Average temperature
- Answer: **23.48**
- Type: Mean/Average computation

### **Quiz 2: Maximum Value**
- File: `quiz2-maximum.html`
- Question: Highest score
- Answer: **95**
- Type: Max computation

### **Quiz 3: Count Items**
- File: `quiz3-count.html`
- Question: How many products
- Answer: **7**
- Type: Row count

### **Quiz 4: Minimum Value**
- File: `quiz4-minimum.html`
- Question: Lowest price
- Answer: **15.75**
- Type: Min computation

### **Quiz 5: Total Revenue**
- File: `quiz5-total.html`
- Question: Total revenue
- Answer: **8117** or **8117.00**
- Type: Sum computation

### **Quiz 6: Average Sales**
- File: `quiz6-mean.html`
- Question: Mean sales amount
- Answer: **44000**
- Type: Average computation

### **Quiz 7: Maximum Temperature**
- File: `quiz7-highest.html`
- Question: Highest temperature
- Answer: **33.5**
- Type: Max computation

### **Quiz 8: Employee Count**
- File: `quiz8-employee-count.html`
- Question: Number of employees
- Answer: **10**
- Type: Count computation

### **Quiz 9: Minimum Stock**
- File: `quiz9-lowest.html`
- Question: Lowest stock quantity
- Answer: **45**
- Type: Min computation

### **Quiz 10: Total Orders**
- File: `quiz10-orders-sum.html`
- Question: Sum of all orders
- Answer: **7617.25**
- Type: Sum computation

---

## 🎯 How to Test Each Quiz

### **Method 1: Using Live Server (Recommended)**

1. **Make sure you have Live Server running** (port 5500)
2. **Go to dashboard**: http://localhost:3000
3. **Test each quiz** with this URL pattern:
   ```
   http://127.0.0.1:5500/quiz-tests/quiz1-average.html
   http://127.0.0.1:5500/quiz-tests/quiz2-maximum.html
   http://127.0.0.1:5500/quiz-tests/quiz3-count.html
   ... and so on
   ```

### **Method 2: Using File Protocol**

If you don't have Live Server:
```
file:///c:/Krishna_Jain/LLM/quiz-tests/quiz1-average.html
file:///c:/Krishna_Jain/LLM/quiz-tests/quiz2-maximum.html
... etc
```

---

## ✅ Testing Checklist

For EACH quiz, verify:

- [ ] Bot finds the question correctly
- [ ] Bot detects data: URL
- [ ] Bot downloads/parses CSV data
- [ ] Bot computes correct answer
- [ ] Bot submits answer
- [ ] Dashboard shows success
- [ ] Answer matches expected value

---

## 📊 Quick Test All Script

Run all 10 quizzes in sequence from the dashboard:

1. **Quiz 1** → Expect: **23.48**
2. **Quiz 2** → Expect: **95**
3. **Quiz 3** → Expect: **7**
4. **Quiz 4** → Expect: **15.75**
5. **Quiz 5** → Expect: **8117**
6. **Quiz 6** → Expect: **44000**
7. **Quiz 7** → Expect: **33.5**
8. **Quiz 8** → Expect: **10**
9. **Quiz 9** → Expect: **45**
10. **Quiz 10** → Expect: **7617.25**

---

## 🎨 Quiz Categories Tested

- **Sum/Total**: Quiz 5, Quiz 10 (Original test quiz)
- **Average/Mean**: Quiz 1, Quiz 6
- **Maximum/Highest**: Quiz 2, Quiz 7
- **Minimum/Lowest**: Quiz 4, Quiz 9
- **Count**: Quiz 3, Quiz 8

---

## 🚀 Testing Instructions

### **Step-by-Step for Each Quiz:**

1. Open quiz HTML file in browser (or via Live Server)
2. Copy the URL from browser address bar
3. Go to dashboard: http://localhost:3000
4. Enter:
   - Email: `test@example.com`
   - Secret: `my-quiz-secret-2025`
   - Quiz URL: [paste the copied URL]
5. Click "Submit Quiz"
6. Watch Live Logs
7. Verify answer in History table
8. Check answer matches expected value

### **All Files Location:**
```
c:\Krishna_Jain\LLM\quiz-tests\
├── quiz1-average.html
├── quiz2-maximum.html
├── quiz3-count.html
├── quiz4-minimum.html
├── quiz5-total.html
├── quiz6-mean.html
├── quiz7-highest.html
├── quiz8-employee-count.html
├── quiz9-lowest.html
└── quiz10-orders-sum.html
```

---

## 🎯 Expected Results Summary

| Quiz | Type | Expected Answer | Status |
|------|------|----------------|--------|
| 1 | Average | 23.48 | ⏳ Test |
| 2 | Maximum | 95 | ⏳ Test |
| 3 | Count | 7 | ⏳ Test |
| 4 | Minimum | 15.75 | ⏳ Test |
| 5 | Sum | 8117 | ⏳ Test |
| 6 | Average | 44000 | ⏳ Test |
| 7 | Maximum | 33.5 | ⏳ Test |
| 8 | Count | 10 | ⏳ Test |
| 9 | Minimum | 45 | ⏳ Test |
| 10 | Sum | 7617.25 | ⏳ Test |

---

## 💡 Troubleshooting

**If a quiz fails:**
1. Check backend logs for errors
2. Verify CSV data is being downloaded
3. Check analysis type detection
4. Verify number parsing
5. Check form submission

**Common Issues:**
- Wrong answer → Check data parsing
- No answer → Check data source detection
- Error → Check logs in backend terminal

---

## 🎉 Success Criteria

✅ All 10 quizzes should:
- Complete in 4-8 seconds each
- Return correct answers
- Show "Success" status
- Display in History table
- No errors in logs

Start testing now! 🚀
