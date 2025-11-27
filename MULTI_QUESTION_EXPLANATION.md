# Understanding Quiz Bot Capabilities

## 🤔 Your Question: Does it solve only one question at a time?

**YES**, the current implementation solves **ONE question per quiz page**.

---

## 📖 How It Currently Works

### **Single Question Per Page:**
```
Quiz Page → One Question → One Dataset → One Answer → Submit
```

**Example:**
```
Page: quiz1-average.html
Question: "What is the average temperature?"
Dataset: temperature.csv
Answer: 23.48
Result: Submits "23.48" and done ✅
```

---

## 🔄 What About Multiple Questions?

You have **THREE options**:

### **Option 1: Separate Pages (Current Approach)**
Create separate HTML files for each question:
```
quiz1.html → Question 1 → Answer 1
quiz2.html → Question 2 → Answer 2
quiz3.html → Question 3 → Answer 3
```

**Pros:** Simple, clean, easy to test
**Cons:** Need multiple submissions from dashboard

---

### **Option 2: Question Chaining (Advanced)**
One page redirects to the next after answering:

```html
<!-- quiz-part1.html -->
<form action="quiz-part2.html">
  <input name="answer1" />
</form>

<!-- quiz-part2.html -->
<form action="quiz-part3.html">
  <input name="answer2" />
</form>
```

**How bot handles it:**
1. Visits quiz-part1.html
2. Answers question 1
3. Submits and page redirects to quiz-part2.html
4. Answers question 2
5. Continues until final page

**Pros:** Automated flow through multiple questions
**Cons:** Requires quiz URLs to be set up with redirects

---

### **Option 3: All Questions on One Page (What You Asked)**

**Current Bot Limitation:**
The bot reads the **FIRST question** it finds on a page and answers that.

**Example - Multi-Question Page:**
```html
<div class="question">Q1: What is the sum?</div>
<div class="question">Q2: What is the average?</div>
<div class="question">Q3: What is the max?</div>
<form>
  <input name="answer1" />
  <input name="answer2" />
  <input name="answer3" />
</form>
```

**What Bot Does:**
- ✅ Finds Q1: "What is the sum?"
- ✅ Computes answer for Q1
- ❌ Ignores Q2 and Q3
- ❌ Only fills first input field

**Why?**
The parser extracts **one question** from the page (the first one it finds).

---

## 💡 Solution: How to Handle Multiple Questions

### **A) Test Each Question Separately (Recommended)**
This is why I created 10 separate quiz files:
```
quiz1-average.html   → Test averages
quiz2-maximum.html   → Test maximums
quiz3-count.html     → Test counting
... etc
```

**Test them all from dashboard by submitting each URL!**

---

### **B) Implement Multi-Question Support (Advanced)**

To make the bot solve ALL questions on one page, you'd need to:

**1. Update Parser** (`solver/parser.py`):
```python
def _extract_questions(self) -> List[str]:
    """Extract ALL questions, not just one"""
    questions = []
    # Find all question elements
    # Return list of questions
```

**2. Update Analyzer** (`solver/analyzer.py`):
```python
def analyze_multiple(self, questions, data):
    """Analyze each question separately"""
    answers = []
    for question in questions:
        answer = self.analyze_single(question, data)
        answers.append(answer)
    return answers
```

**3. Update Submitter** (`solver/submitter.py`):
```python
def submit_multiple_answers(self, answers):
    """Fill multiple form fields"""
    for i, answer in enumerate(answers):
        input_field = find_nth_input(i)
        input_field.fill(answer)
```

**This would be a significant feature enhancement!**

---

## 🎯 Current Best Practice

**For testing different analysis types:**

✅ **Use separate quiz pages** (what I created):
- `quiz1-average.html` → Tests averages
- `quiz2-maximum.html` → Tests max values
- `quiz3-count.html` → Tests counting
- etc.

**Submit each URL to the dashboard separately:**
```
1. Submit: http://127.0.0.1:5500/quiz-tests/quiz1-average.html
   → Get answer: 23.48 ✅

2. Submit: http://127.0.0.1:5500/quiz-tests/quiz2-maximum.html
   → Get answer: 95 ✅

3. Submit: http://127.0.0.1:5500/quiz-tests/quiz3-count.html
   → Get answer: 7 ✅
```

**This tests all functionality without needing multi-question support!**

---

## 🔥 For Complex Real-World Scenarios

If your actual quizzes have multiple questions on one page:

**Option A:** Split them into separate submissions
**Option B:** Enhance the bot to support multi-question (requires coding)
**Option C:** Use question chaining with redirects

---

## ✅ Summary

| Scenario | Current Support | How to Test |
|----------|----------------|-------------|
| 1 question per page | ✅ YES | Submit URL directly |
| Multiple pages chained | ✅ YES | Bot follows redirects |
| Multiple questions same page | ❌ NO* | Need to enhance parser |

*Bot currently only answers the first question found on a page.

---

## 🎯 Recommendation

**Test with the 10 separate quiz files I created!** Each tests a different analysis type:
- Sum calculations
- Averages
- Max/Min values
- Counting

This comprehensively tests all bot capabilities without needing multi-question support.

If you need multi-question support for your real use case, let me know and I can implement it! 🚀
