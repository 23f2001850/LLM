# Multi-Quiz Chaining Architecture

## 🏗️ System Overview

This document explains the technical architecture of the multi-quiz chaining feature in the LLM Analysis Quiz Bot.

---

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER / EVALUATOR                         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ POST /quiz
                          │ {"email", "secret", "url"}
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                      FastAPI Backend                             │
│                     (main.py: /quiz)                             │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Multi-Quiz Chain Loop (while loop)              │   │
│  │                                                           │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  1. Browser Manager (browser.py)                 │   │   │
│  │  │     • Launch Playwright Chromium                 │   │   │
│  │  │     • Load quiz URL                               │   │   │
│  │  │     • Wait for page render                        │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                        ↓                                 │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  2. Quiz Parser (parser.py)                      │   │   │
│  │  │     • Extract question text                       │   │   │
│  │  │     • Find data source links                      │   │   │
│  │  │     • Detect submit URL                           │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                        ↓                                 │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  3. Data Downloader (downloader.py)              │   │   │
│  │  │     • Download CSV/PDF/Excel/images               │   │   │
│  │  │     • Handle data: URLs (inline base64)           │   │   │
│  │  │     • Fetch from HTTP/HTTPS                       │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                        ↓                                 │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  4. Data Analyzer (analyzer.py)                  │   │   │
│  │  │     • Parse data (pandas, openpyxl, pdfplumber)  │   │   │
│  │  │     • Detect analysis type (sum/avg/max/min)     │   │   │
│  │  │     • Compute answer                              │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                        ↓                                 │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  5. Answer Submitter (submitter.py)              │   │   │
│  │  │     • POST answer to submit URL                   │   │   │
│  │  │     • Receive JSON response                       │   │   │
│  │  │     • Extract next_url/url field                  │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                        ↓                                 │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  6. Chain Decision Logic                         │   │   │
│  │  │     • If next_url exists → Continue loop          │   │   │
│  │  │     • If no next_url → Break loop (complete)      │   │   │
│  │  │     • If timeout near → Break loop (timeout)      │   │   │
│  │  │     • If incorrect answer → Break loop (failed)   │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                        ↓                                 │   │
│  │            Loop back to step 1 OR exit                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Return QuizResponse:                                        │
│    • status: "ok" / "error"                                  │
│    • steps: [array of all quiz steps]                        │
│    • quizzes_solved: count                                   │
│    • chain_complete: true/false                              │
│    • time_taken: total seconds                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 🔄 Multi-Quiz Chain Flow

### 1. Initial Request

```
POST /quiz
{
  "email": "student@example.com",
  "secret": "my-quiz-secret-2025",
  "url": "https://eval-server.com/quiz/1"
}
```

### 2. Quiz Chain Loop

```python
# Simplified pseudocode from main.py

current_url = quiz_request.url
quiz_count = 0
max_quizzes = 10

while current_url and quiz_count < max_quizzes:
    quiz_count += 1
    
    # Check timeout
    if timeout_exceeded():
        break
    
    # Load quiz page
    page_content = browser.load_page(current_url)
    
    # Parse quiz
    quiz_data = parser.parse(page_content)
    
    # Download data
    downloaded_data = downloader.download_all(quiz_data)
    
    # Analyze and compute answer
    analysis = analyzer.analyze(quiz_data, downloaded_data)
    answer = analysis["answer"]
    
    # Submit answer
    submit_url = quiz_data["submit_url"]
    response = submitter.submit(submit_url, answer, email)
    
    # Check for next quiz
    next_url = response.get("next_url") or response.get("url")
    
    if next_url and response.get("correct"):
        current_url = next_url  # Continue to next quiz
        log("Continuing to next quiz...")
    else:
        break  # Chain complete or answer incorrect
```

### 3. Response Construction

```json
{
  "status": "ok",
  "steps": [
    // All steps from all quizzes
  ],
  "final_url": "https://eval-server.com/submit/3",
  "final_answer": 42,
  "time_taken": 45.2,
  "quizzes_solved": 3,
  "chain_complete": true,
  "message": "Successfully solved 3 quiz(es) in chain"
}
```

---

## 🔍 Key Components

### Browser Manager (`solver/browser.py`)

**Responsibilities:**
- Launch Playwright Chromium browser
- Load URLs with JavaScript execution
- Wait for page stability
- Extract rendered HTML content
- Handle navigation and page errors

**Key Methods:**
```python
class BrowserManager:
    async def start(self)
    async def load_page(self, url: str) -> str
    async def close(self)
```

### Quiz Parser (`solver/parser.py`)

**Responsibilities:**
- Extract question text from HTML
- Find all data source links (CSV, PDF, Excel, data: URLs)
- Detect submit URL from forms or links
- Parse instructions and requirements

**Key Methods:**
```python
class QuizParser:
    def parse(self) -> Dict[str, Any]
    def _extract_question(self) -> str
    def _find_data_sources(self) -> List[str]
    def _find_submit_url(self) -> str
```

**Important:** Uses `getAttribute('href')` instead of `el.href` to preserve `data:` URLs.

### Data Downloader (`solver/downloader.py`)

**Responsibilities:**
- Download files from HTTP/HTTPS URLs
- Parse inline `data:` URLs (base64 or URL-encoded)
- Handle various MIME types
- Return binary content for processing

**Key Methods:**
```python
class DataDownloader:
    async def download_all(self, quiz_data: Dict) -> List[Dict]
    async def download_file(self, url: str) -> bytes
    def _parse_data_url(self, url: str) -> bytes
```

### Data Analyzer (`solver/analyzer.py`)

**Responsibilities:**
- Parse CSV, Excel, PDF, JSON data
- Detect analysis type from question keywords
- Perform statistical operations (sum, average, max, min, count)
- Apply filters and aggregations
- Return computed answer

**Key Methods:**
```python
class DataAnalyzer:
    def analyze(self, quiz_data: Dict, downloaded_data: List) -> Dict
    def _determine_analysis_type(self, question: str) -> str
    def _compute_sum(self, df: DataFrame) -> float
    def _compute_average(self, df: DataFrame) -> float
    def _compute_max(self, df: DataFrame) -> float
```

**Analysis Types Supported:**
- Sum / Total
- Average / Mean
- Maximum / Highest
- Minimum / Lowest
- Count / Number of items

### Answer Submitter (`solver/submitter.py`)

**Responsibilities:**
- POST answer to submit URL
- Parse JSON response
- **Extract next quiz URL** from response
- Handle different response formats
- Retry with alternative formats if needed

**Key Methods:**
```python
class AnswerSubmitter:
    async def submit(self, submit_url: str, answer: Any, email: str) -> Dict
    def _extract_next_url(self, response: Dict) -> Optional[str]
```

**Next URL Detection:**
```python
def _extract_next_url(self, response_data: Dict) -> Optional[str]:
    # Check common fields
    url_fields = ["url", "next_url", "nextUrl", "next", "redirect"]
    
    for field in url_fields:
        if field in response_data:
            url = response_data[field]
            if url and url.startswith(("http://", "https://", "/")):
                return url
    
    # Check nested data
    if "data" in response_data:
        return self._extract_next_url(response_data["data"])
    
    return None
```

---

## ⏱️ Timeout Management

### Global Timeout

- **Limit**: 3 minutes (180 seconds) across entire chain
- **Tracking**: `TimeoutManager` class in `solver/utils.py`
- **Checks**: Before each quiz in the loop

```python
class TimeoutManager:
    def __init__(self, max_time: int):
        self.start_time = time.time()
        self.max_time = max_time
    
    def is_expired(self) -> bool:
        return (time.time() - self.start_time) > self.max_time
    
    def remaining_time(self) -> float:
        return self.max_time - (time.time() - self.start_time)
```

### Timeout Behavior

```python
while current_url and quiz_count < max_quizzes:
    if timeout_mgr.is_expired():
        logger.warning("Timeout approaching, stopping chain")
        break
    
    # Process quiz...
```

---

## 🛡️ Safety Mechanisms

### 1. Maximum Quiz Limit

Prevents infinite loops:
```python
max_quizzes = 10
```

### 2. Timeout Enforcement

Ensures compliance with 3-minute rule:
```python
if timeout_mgr.is_expired():
    break
```

### 3. Incorrect Answer Handling

Stops chain on wrong answer:
```python
if not response.get("correct"):
    logger.warning("Answer incorrect, stopping chain")
    break
```

### 4. Missing URL Detection

Completes chain when no next URL:
```python
next_url = response.get("next_url") or response.get("url")
if not next_url:
    logger.info("Chain complete - no more URLs")
    break
```

---

## 📝 Logging Strategy

### Chain Progress Logging

```python
logger.info(f"Processing quiz {quiz_count}: {current_url}")
logger.info(f"Computed answer: {answer}")
logger.info(f"Next quiz URL detected: {next_url}")
logger.info(f"✓ Quiz {quiz_count} correct. Next quiz URL: {next_url}")
logger.info(f"✓ Chain completed successfully after {quiz_count} quiz(es)")
```

### Step Tracking

Every operation is logged in the `steps` array:

```python
steps.append({
    "step": f"load_quiz_{quiz_count}",
    "url": current_url,
    "status": "success",
    "time": time.time() - start_time
})

steps.append({
    "step": f"submit_answer_{quiz_count}",
    "url": submit_url,
    "correct": response.get("correct"),
    "status": "success",
    "time": time.time() - start_time
})

steps.append({
    "step": f"chain_continue_{quiz_count}",
    "next_url": next_url,
    "status": "continuing",
    "time": time.time() - start_time
})
```

---

## 🧪 Testing Architecture

### Test Quiz Chain

```
chain-quiz-1.html → chain-quiz-2.html → chain-quiz-3.html
     (Sum)              (Average)           (Maximum)
  Answer: 1420       Answer: 23.46       Answer: 98
     ↓                    ↓                    ↓
  Returns next_url   Returns next_url    No next_url
                                        (chain complete)
```

### Test Verification

1. **Single Quiz Test**: Verify each quiz works independently
2. **Chain Test**: Submit quiz 1 URL, verify automatic continuation
3. **Timeout Test**: Create long chain to test timeout handling
4. **Error Test**: Submit wrong URL to test error handling

---

## 🚀 Performance Considerations

### Parallel Processing Opportunities

- **Data downloads**: Multiple files can be downloaded in parallel
- **Parsing**: Can parse multiple data sources simultaneously
- **Analysis**: Independent analysis operations can run concurrently

### Bottlenecks

- **Browser rendering**: Sequential (one page at a time)
- **Quiz chaining**: Sequential (must wait for submit response)
- **Network latency**: Depends on external servers

### Optimization Strategies

1. **Browser reuse**: Keep browser instance alive across chain
2. **Connection pooling**: Reuse HTTP connections for downloads
3. **Parallel downloads**: Use `asyncio.gather()` for multiple files
4. **Efficient parsing**: Use BeautifulSoup selectors wisely

---

## 📚 Code References

| Component | File | Lines |
|-----------|------|-------|
| Main chain loop | `backend/main.py` | 150-280 |
| Next URL extraction | `backend/solver/submitter.py` | 100-145 |
| Browser automation | `backend/solver/browser.py` | 1-100 |
| Quiz parsing | `backend/solver/parser.py` | 1-200 |
| Data download | `backend/solver/downloader.py` | 1-150 |
| Data analysis | `backend/solver/analyzer.py` | 1-300 |
| Timeout management | `backend/solver/utils.py` | 1-50 |

---

## 🎯 Success Metrics

A successful multi-quiz chain execution shows:

1. ✅ `quizzes_solved >= 1` (at least one quiz solved)
2. ✅ `chain_complete: true` (all quizzes completed)
3. ✅ `time_taken < 180` (under 3 minutes)
4. ✅ All `submit_answer_N` steps show `correct: true`
5. ✅ `chain_continue_N` steps show transitions
6. ✅ Final `chain_complete` step present

---

**Architecture designed for robustness, scalability, and production readiness! 🚀**
