# LLM Analysis Quiz Bot - Backend

Complete backend service for automated quiz solving with data analysis capabilities.

## Features

- **Headless Browser**: Playwright-based browser automation for JavaScript-rendered pages
- **Multi-format Data Processing**: PDF, CSV, Excel, JSON, images, API responses
- **Intelligent Analysis**: Statistical analysis, data aggregation, filtering, ML operations
- **Dynamic Submit Detection**: Automatically finds and uses submit URLs
- **Quiz Chaining**: Handles multiple quiz sequences until completion
- **Visualization**: Creates charts and converts to base64
- **OCR Support**: Extracts text from images using Tesseract
- **Timeout Management**: Ensures completion within 3 minutes
- **Production Ready**: Full error handling, logging, and deployment configs

## Architecture

```
backend/
├── main.py              # FastAPI application entry point
├── solver/              # Core solving logic
│   ├── browser.py       # Playwright browser management
│   ├── parser.py        # Quiz content extraction
│   ├── downloader.py    # Multi-format data downloader
│   ├── analyzer.py      # Data analysis and computation
│   ├── visualizer.py    # Chart generation
│   ├── submitter.py     # Answer submission
│   └── utils.py         # Utility functions
├── requirements.txt     # Python dependencies
└── Dockerfile          # Container configuration
```

## API Specification

### POST /quiz

Submit a quiz to be solved.

**Request Body:**
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
    {"step": "validate_secret", "status": "success", "time": 0.01},
    {"step": "load_quiz_1", "url": "...", "status": "success", "time": 0.5}
  ],
  "final_url": "https://example.com/submit",
  "final_answer": 42,
  "time_taken": 45.2
}
```

**Error Responses:**
- `400 Bad Request`: Invalid JSON format
- `403 Forbidden`: Invalid secret
- `500 Internal Server Error`: Processing error

### GET /

Service health check and information.

### GET /health

Simple health status.

### GET /history

Get recent quiz solving history (last 50 entries).

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `QUIZ_SECRET` | Secret key for authentication | `default-secret-change-me` |
| `MAX_QUIZ_TIME` | Maximum processing time (seconds) | `180` |
| `PORT` | Server port | `8000` |

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

3. Set environment variables:
```bash
# Windows PowerShell
$env:QUIZ_SECRET="your-secret-key"

# Linux/Mac
export QUIZ_SECRET="your-secret-key"
```

4. Run the server:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --port 8000
```

5. Test the endpoint:
```bash
curl -X POST http://localhost:8000/quiz `
  -H "Content-Type: application/json" `
  -d '{"email":"test@example.com","secret":"your-secret-key","url":"https://example.com/quiz"}'
```

## Docker Deployment

### Build Image

```bash
docker build -t quiz-bot-backend .
```

### Run Container

```bash
docker run -d `
  -p 8000:8000 `
  -e QUIZ_SECRET=your-secret-key `
  -e MAX_QUIZ_TIME=180 `
  --name quiz-bot `
  quiz-bot-backend
```

## Cloud Deployment

### Render

1. Create new Web Service
2. Connect repository
3. Set build command: `pip install -r requirements.txt && playwright install chromium`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

### Railway

1. Create new project from GitHub repo
2. Add environment variables
3. Railway auto-detects Dockerfile

### AWS/GCP

Deploy using container services (ECS, Cloud Run) with the provided Dockerfile.

## Processing Flow

1. **Validate Secret**: Check authentication
2. **Load Page**: Use Playwright to render JavaScript
3. **Parse Content**: Extract question, data sources, submit URL
4. **Download Data**: Fetch PDFs, CSVs, Excel files, images
5. **Analyze**: Process data, compute statistics, apply filters
6. **Visualize** (if needed): Create charts as base64
7. **Submit Answer**: POST to detected submit URL
8. **Chain**: If next URL provided, repeat process
9. **Return Results**: Complete response with all steps

## Data Processing Capabilities

### Supported Formats

- **PDF**: Table extraction, text parsing (pdfplumber, PyPDF2)
- **CSV**: Pandas processing with encoding detection
- **Excel**: Multi-sheet support (openpyxl)
- **JSON**: Direct parsing and nested data extraction
- **Images**: OCR with Tesseract, base64 encoding/decoding
- **HTML Tables**: Automatic DataFrame conversion
- **APIs**: JSON/text response handling

### Analysis Operations

- Sum, average, min, max, count
- Filtering and conditional selection
- Grouping and aggregation
- Data cleaning and regex operations
- Missing value handling
- Statistical computations

## Security

- Environment-based secret management
- Input validation and sanitization
- No secret logging
- Safe parsing with error handling
- Request timeout enforcement

## Monitoring

- Structured logging to console and file
- Request history tracking
- Performance metrics per step
- Error tracing with full context

## Troubleshooting

### Browser Launch Fails

Install system dependencies:
```bash
playwright install-deps chromium
```

### PDF Parsing Errors

Ensure pdfplumber and PyPDF2 are installed correctly.

### Timeout Issues

Increase `MAX_QUIZ_TIME` or optimize network connection.

### Memory Issues

Limit concurrent requests or increase container memory.

## License

MIT License - See root LICENSE file
