# LLM Analysis Quiz Bot

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Node](https://img.shields.io/badge/node-20+-green.svg)

**Fully automated quiz solver with intelligent data analysis, visualization, and web dashboard**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Architecture](#-architecture) • [Deployment](#-deployment)

</div>

---

## 🎯 Overview

LLM Analysis Quiz Bot is a production-ready, automated system that solves complex data analysis quizzes by:

- Loading JavaScript-rendered web pages using headless browsers
- Extracting questions and instructions dynamically
- Downloading and processing multiple data formats (PDF, CSV, Excel, JSON, images)
- Performing statistical analysis, aggregation, and visualization
- Computing correct answers using intelligent algorithms
- Submitting answers to dynamically detected endpoints
- Handling quiz chains seamlessly until completion
- Completing all operations within 3 minutes

## ✨ Features

### Core Capabilities

- **🌐 Headless Browser Automation**: Playwright-based rendering of complex JavaScript pages
- **📊 Multi-Format Data Processing**: PDF tables, CSV, Excel, JSON, API responses, images
- **🧮 Intelligent Analysis**: Sum, average, count, max/min, filtering, aggregation, statistics
- **📈 Visualization**: Automatic chart generation with base64 encoding
- **🔍 OCR Support**: Text extraction from images using Tesseract
- **🔗 Multi-Quiz Chaining**: Automatically follows quiz chains until completion
- **⚡ Performance**: Sub-3-minute processing with timeout management across entire chain
- **🔒 Security**: Secret-based authentication, input sanitization, safe parsing

### Dashboard Features

- **📱 Responsive UI**: Modern TailwindCSS design, mobile-friendly
- **🌓 Dark/Light Theme**: Automatic theme switching with persistence
- **📊 Real-time Stats**: Success rate, timing, performance metrics
- **📝 Live Logs**: Console-style log streaming
- **📜 History Tracking**: Complete quiz attempt history
- **✅ Status Monitoring**: Service health and version information

### Production Ready

- **🐳 Docker Support**: Complete containerization with Docker Compose
- **📦 Easy Deployment**: Render, Railway, AWS, GCP, Vercel compatible
- **🔧 Configuration**: Environment-based settings
- **🧪 Comprehensive Tests**: Full test suite with pytest
- **📖 Complete Documentation**: Detailed README files
- **⚠️ Error Handling**: Graceful degradation and fallback methods

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended)
- OR Python 3.11+ & Node.js 20+ (local development)

### Using Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd LLM
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and set your QUIZ_SECRET
```

3. **Start services**
```bash
docker-compose up -d
```

4. **Access the dashboard**
```
http://localhost:3000
```

5. **API endpoint**
```
http://localhost:8000
```

### Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set environment variable
$env:QUIZ_SECRET="your-secret-key"  # Windows PowerShell

# Run server
python main.py
```

#### Dashboard Setup

```bash
cd dashboard

# Install dependencies
npm install

# Set environment variable
# Create .env.local with:
# NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Run development server
npm run dev
```

## 📖 Documentation

**📚 Full Documentation Index:** See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for complete guide to all documentation files.

**🔗 Multi-Quiz Chaining:** See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for quick overview or [MULTI_QUIZ_CHAIN_TESTING.md](MULTI_QUIZ_CHAIN_TESTING.md) for complete testing guide.

### API Specification

#### POST /quiz

Submit a quiz for automated solving.

**Request:**
```json
{
  "email": "student@example.com",
  "secret": "your-secret-key",
  "url": "https://example.com/quiz-123"
}
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "steps": [
    {
      "step": "validate_secret",
      "status": "success",
      "time": 0.01
    },
    {
      "step": "load_quiz_1",
      "url": "https://example.com/quiz-123",
      "status": "success",
      "time": 0.5
    },
    {
      "step": "parse_quiz_1",
      "question": "What is the sum...",
      "status": "success",
      "time": 0.6
    }
  ],
  "final_url": "https://example.com/submit",
  "final_answer": 42,
  "time_taken": 45.2
}
```

**Error Responses:**
- `400 Bad Request`: Invalid JSON format
- `403 Forbidden`: Invalid secret key
- `500 Internal Server Error`: Processing error

#### GET /

Service information and health check.

#### GET /health

Simple health status endpoint.

#### GET /history

Retrieve quiz solving history (last 50 entries).

### Example Usage

#### Using cURL

```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "secret": "your-secret-key",
    "url": "https://example.com/quiz"
  }'
```

#### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/quiz",
    json={
        "email": "student@example.com",
        "secret": "your-secret-key",
        "url": "https://example.com/quiz"
    }
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Answer: {result['final_answer']}")
print(f"Time: {result['time_taken']}s")
```

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐
│   Dashboard     │  ← User Interface (Next.js)
│   (Port 3000)   │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────┐
│   Backend API   │  ← FastAPI Server
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┼────┬────────┬──────────┐
    │    │    │        │          │
┌───▼┐ ┌─▼─┐ ┌▼──┐  ┌─▼───┐  ┌──▼───┐
│PWR │ │DL │ │ANA│  │VIZ  │  │SUB   │
└────┘ └───┘ └───┘  └─────┘  └──────┘
Browser Down- Analy- Visual-  Answer
        load  zer    izer     Submit
```

### Processing Flow

1. **Request Reception**: Validate secret and parameters
2. **Browser Launch**: Start Playwright headless browser
3. **Quiz Chain Loop** (continues until no next URL):
   - **Page Loading**: Render JavaScript and execute dynamic content
   - **Content Parsing**: Extract question, data sources, submit URL
   - **Data Download**: Fetch PDFs, CSVs, Excel files, images, API data
   - **Data Analysis**: 
     - Parse and clean data
     - Detect analysis type from question
     - Perform statistical computations
     - Apply filters and aggregations
   - **Visualization** (if needed): Generate charts as base64
   - **Answer Submission**: POST to detected submit endpoint
   - **Chain Detection**: Check response for next quiz URL
   - **Continue or Complete**: Loop to next quiz or finish
4. **Response Return**: Complete results with all steps, chain metadata

## 🔗 Multi-Quiz Chaining

### Overview

This bot **automatically follows quiz chains** until completion. When a quiz server returns a next URL after answer submission, the bot continues solving quizzes in a loop without manual intervention.

### How It Works

```
User submits Quiz 1 URL
         ↓
Bot solves Quiz 1 → Submits answer
         ↓
Server returns: {"correct": true, "next_url": "quiz-2-url"}
         ↓
Bot automatically loads Quiz 2 → Solves → Submits
         ↓
Server returns: {"correct": true, "next_url": "quiz-3-url"}
         ↓
Bot automatically loads Quiz 3 → Solves → Submits
         ↓
Server returns: {"correct": true}  (no next_url)
         ↓
Chain complete ✓
```

### Response Format Detection

The bot detects next quiz URLs from various response formats:

```json
// Option 1: Standard field
{"correct": true, "url": "https://example.com/quiz-2"}

// Option 2: Explicit next_url
{"correct": true, "next_url": "https://example.com/quiz-2"}

// Option 3: Nested data
{"correct": true, "data": {"url": "https://example.com/quiz-2"}}

// Option 4: Chain complete (no URL)
{"correct": true, "message": "All quizzes complete"}
```

### Chain Management Features

- ✅ **Automatic Continuation**: No manual intervention between quizzes
- ✅ **Timeout Enforcement**: 3-minute limit across entire chain
- ✅ **Chain Metadata**: Returns `quizzes_solved` and `chain_complete` status
- ✅ **Safety Limits**: Maximum 10 quizzes per chain to prevent infinite loops
- ✅ **Error Handling**: Stops gracefully on incorrect answers or timeouts
- ✅ **Comprehensive Logging**: Tracks each quiz transition with timestamps

### API Response for Chains

```json
{
  "status": "ok",
  "steps": [
    {"step": "load_quiz_1", "url": "...", "status": "success", "time": 0.5},
    {"step": "submit_answer_1", "correct": true, "time": 2.1},
    {"step": "chain_continue_1", "next_url": "...", "time": 2.2},
    {"step": "load_quiz_2", "url": "...", "status": "success", "time": 3.0},
    {"step": "submit_answer_2", "correct": true, "time": 5.5},
    {"step": "chain_continue_2", "next_url": "...", "time": 5.6},
    {"step": "load_quiz_3", "url": "...", "status": "success", "time": 6.2},
    {"step": "submit_answer_3", "correct": true, "time": 8.0},
    {"step": "chain_complete", "total_quizzes": 3, "time": 8.1}
  ],
  "final_url": "https://example.com/submit-3",
  "final_answer": 42,
  "time_taken": 8.1,
  "quizzes_solved": 3,
  "chain_complete": true,
  "message": "Successfully solved 3 quiz(es) in chain"
}
```

### Testing Multi-Quiz Chains

Test quiz chain files are provided in `quiz-tests/`:

```bash
# Open these files in a browser with Live Server
quiz-tests/chain-quiz-1.html  # Returns next_url → chain-quiz-2.html
quiz-tests/chain-quiz-2.html  # Returns next_url → chain-quiz-3.html
quiz-tests/chain-quiz-3.html  # Returns no next_url (chain complete)
```

Submit the first quiz URL to the bot:
```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "secret": "my-quiz-secret-2025",
    "url": "http://127.0.0.1:5500/quiz-tests/chain-quiz-1.html"
  }'
```

The bot will automatically:
1. Solve Quiz 1 (sum calculation) → Answer: 1420
2. Receive next URL → Load Quiz 2
3. Solve Quiz 2 (average) → Answer: 23.46
4. Receive next URL → Load Quiz 3
5. Solve Quiz 3 (maximum) → Answer: 98
6. Detect chain completion (no next URL)
7. Return complete results

### Chain Timeout Behavior

- Global 3-minute timeout across **entire chain**
- Each quiz checked against remaining time
- Graceful termination if timeout approaches
- Returns partial results with `chain_complete: false`

### Technology Stack

#### Backend
- **Framework**: FastAPI (async Python web framework)
- **Browser**: Playwright (headless Chromium)
- **Data Processing**: pandas, numpy, openpyxl
- **PDF**: pdfplumber, PyPDF2
- **Images**: Pillow, pytesseract
- **Visualization**: matplotlib
- **Server**: uvicorn/gunicorn

#### Frontend
- **Framework**: Next.js 14 (React)
- **Styling**: TailwindCSS
- **Language**: TypeScript
- **HTTP**: Axios

#### DevOps
- **Containerization**: Docker, Docker Compose
- **Testing**: pytest, httpx
- **CI/CD**: Compatible with GitHub Actions, GitLab CI

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=solver --cov-report=html
```

### Test Coverage

- ✅ API endpoint validation
- ✅ Secret authentication
- ✅ Quiz parsing
- ✅ Data downloading
- ✅ PDF/CSV/Excel processing
- ✅ Data analysis algorithms
- ✅ Visualization generation
- ✅ Answer submission
- ✅ Timeout management
- ✅ Integration flows

## 🚀 Deployment

### Render

**Backend:**
1. Create new Web Service
2. Connect repository
3. Build command: `pip install -r requirements.txt && playwright install chromium`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables: `QUIZ_SECRET`, `MAX_QUIZ_TIME`

**Frontend:**
1. Create new Web Service
2. Build command: `npm install && npm run build`
3. Start command: `npm start`
4. Add environment: `NEXT_PUBLIC_BACKEND_URL`

### Railway

1. Create new project from GitHub
2. Add environment variables
3. Railway auto-detects Dockerfile
4. Deploy both services

### AWS/GCP

Deploy using container services:
- **AWS**: ECS, Fargate, or App Runner
- **GCP**: Cloud Run or GKE
- Use provided Dockerfiles

### Vercel (Dashboard Only)

```bash
cd dashboard
npm install -g vercel
vercel --prod
```

Set environment variable: `NEXT_PUBLIC_BACKEND_URL`

## ⚙️ Configuration

### Environment Variables

#### Backend (`backend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `QUIZ_SECRET` | Secret key for authentication | `default-secret-change-me` |
| `MAX_QUIZ_TIME` | Max processing time (seconds) | `180` |
| `PORT` | Server port | `8000` |

#### Dashboard (`dashboard/.env.local`)

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_BACKEND_URL` | Backend API URL | `http://localhost:8000` |

## 📊 Project Structure

```
LLM/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── solver/
│   │   ├── browser.py          # Playwright automation
│   │   ├── parser.py           # Content extraction
│   │   ├── downloader.py       # Data fetching
│   │   ├── analyzer.py         # Data analysis
│   │   ├── visualizer.py       # Chart generation
│   │   ├── submitter.py        # Answer submission
│   │   └── utils.py            # Utilities
│   ├── tests/
│   │   ├── test_backend.py     # Unit tests
│   │   └── test_api.py         # API tests
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Backend container
│   └── README.md               # Backend docs
│
├── dashboard/
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   └── globals.css         # Global styles
│   ├── components/
│   │   ├── Header.tsx          # App header
│   │   ├── StatsCards.tsx      # Statistics
│   │   ├── QuizForm.tsx        # Submit form
│   │   ├── HistoryList.tsx     # History display
│   │   ├── LiveLogs.tsx        # Log viewer
│   │   └── ThemeProvider.tsx   # Theme management
│   ├── package.json            # Node dependencies
│   ├── tailwind.config.js      # Tailwind setup
│   ├── Dockerfile              # Dashboard container
│   └── README.md               # Dashboard docs
│
├── docker-compose.yml          # Docker orchestration
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
└── README.md                   # This file
```

## 🔍 Supported Quiz Types

### Data Formats
- ✅ PDF (table extraction, text parsing)
- ✅ CSV (encoding detection, pandas processing)
- ✅ Excel (multi-sheet support)
- ✅ JSON (nested data extraction)
- ✅ HTML Tables (automatic DataFrame conversion)
- ✅ Images (OCR with Tesseract)
- ✅ API Responses (JSON/text)
- ✅ Base64 encoded data

### Analysis Types
- ✅ Sum, Average, Count
- ✅ Maximum, Minimum
- ✅ Filtering and conditional selection
- ✅ Grouping and aggregation
- ✅ Data cleaning and regex operations
- ✅ Missing value handling
- ✅ Statistical computations
- ✅ Visualization generation

### Answer Formats
- ✅ Numbers (int, float)
- ✅ Strings
- ✅ Booleans
- ✅ JSON objects
- ✅ Arrays
- ✅ Base64 images

## 🐛 Troubleshooting

### Browser Issues

**Problem**: Playwright fails to launch browser

**Solution**:
```bash
playwright install chromium
playwright install-deps chromium
```

### PDF Parsing Errors

**Problem**: Cannot extract PDF tables

**Solution**: Ensure pdfplumber and PyPDF2 are installed:
```bash
pip install pdfplumber PyPDF2
```

### Timeout Issues

**Problem**: Quizzes taking too long

**Solution**: Increase `MAX_QUIZ_TIME` environment variable or optimize network.

### Memory Issues

**Problem**: High memory usage

**Solution**: Limit concurrent requests or increase container memory allocation.

### Dashboard Connection Error

**Problem**: Cannot connect to backend

**Solution**: Verify `NEXT_PUBLIC_BACKEND_URL` is set correctly and backend is running.

## 📝 Development

### Adding New Analysis Types

Edit `backend/solver/analyzer.py`:

```python
def _determine_analysis_type(self, question: str) -> str:
    # Add your custom analysis type detection
    if 'your_keyword' in question.lower():
        return "your_custom_type"
```

### Adding New Data Formats

Edit `backend/solver/downloader.py` and `analyzer.py`:

```python
async def _download_custom_format(self, url: str):
    # Implement custom download logic
    pass
```

### Customizing Dashboard

Edit components in `dashboard/components/` and styles in `tailwind.config.js`.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Playwright for browser automation
- FastAPI for the excellent web framework
- Next.js for the modern React framework
- TailwindCSS for utility-first styling
- All open-source contributors

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

<div align="center">

**Built with ❤️ using Python, FastAPI, Next.js, and TailwindCSS**

</div>
