# PowerShell Setup Script for LLM Analysis Quiz Bot
# Run this script to set up the project quickly

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LLM Analysis Quiz Bot - Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator (optional but recommended)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Note: Running without administrator privileges. Some features may be limited." -ForegroundColor Yellow
    Write-Host ""
}

# Function to check if command exists
function Test-Command {
    param($Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    } catch {
        return $false
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Green

$hasDocker = Test-Command "docker"
$hasPython = Test-Command "python"
$hasNode = Test-Command "node"

Write-Host "  Docker: $(if ($hasDocker) { '✓ Installed' } else { '✗ Not found' })" -ForegroundColor $(if ($hasDocker) { 'Green' } else { 'Red' })
Write-Host "  Python: $(if ($hasPython) { '✓ Installed' } else { '✗ Not found' })" -ForegroundColor $(if ($hasPython) { 'Green' } else { 'Red' })
Write-Host "  Node.js: $(if ($hasNode) { '✓ Installed' } else { '✗ Not found' })" -ForegroundColor $(if ($hasNode) { 'Green' } else { 'Red' })
Write-Host ""

# Setup method selection
if ($hasDocker) {
    Write-Host "Select setup method:" -ForegroundColor Cyan
    Write-Host "  1. Docker (Recommended - Easiest)"
    Write-Host "  2. Local Development"
    Write-Host "  3. Exit"
    $choice = Read-Host "Enter your choice (1-3)"
} else {
    Write-Host "Docker not found. Will use local development setup." -ForegroundColor Yellow
    $choice = "2"
}

switch ($choice) {
    "1" {
        # Docker setup
        Write-Host ""
        Write-Host "Setting up with Docker..." -ForegroundColor Green
        Write-Host ""
        
        # Check if .env exists
        if (-not (Test-Path ".env")) {
            Write-Host "Creating .env file..." -ForegroundColor Yellow
            Copy-Item ".env.example" ".env"
            Write-Host "✓ .env file created from template" -ForegroundColor Green
            Write-Host ""
            Write-Host "IMPORTANT: Please edit .env and set your QUIZ_SECRET!" -ForegroundColor Yellow
            $editNow = Read-Host "Do you want to edit .env now? (y/n)"
            if ($editNow -eq "y") {
                notepad .env
            }
        }
        
        Write-Host ""
        Write-Host "Starting Docker containers..." -ForegroundColor Green
        docker-compose up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "✓ Setup Complete!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Your application is now running:" -ForegroundColor Cyan
            Write-Host "  Dashboard: http://localhost:3000" -ForegroundColor White
            Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
            Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
            Write-Host ""
            Write-Host "To stop: docker-compose down" -ForegroundColor Yellow
            Write-Host "To view logs: docker-compose logs -f" -ForegroundColor Yellow
        } else {
            Write-Host "Error: Docker setup failed. Please check the logs." -ForegroundColor Red
        }
    }
    
    "2" {
        # Local development setup
        Write-Host ""
        Write-Host "Setting up for local development..." -ForegroundColor Green
        Write-Host ""
        
        if (-not $hasPython) {
            Write-Host "Error: Python is required but not installed." -ForegroundColor Red
            Write-Host "Please install Python 3.11+ from: https://www.python.org/downloads/" -ForegroundColor Yellow
            exit 1
        }
        
        if (-not $hasNode) {
            Write-Host "Error: Node.js is required but not installed." -ForegroundColor Red
            Write-Host "Please install Node.js 20+ from: https://nodejs.org/" -ForegroundColor Yellow
            exit 1
        }
        
        # Backend setup
        Write-Host "Setting up backend..." -ForegroundColor Cyan
        Push-Location backend
        
        # Create virtual environment
        if (-not (Test-Path "venv")) {
            Write-Host "  Creating virtual environment..." -ForegroundColor Yellow
            python -m venv venv
        }
        
        # Activate virtual environment
        Write-Host "  Activating virtual environment..." -ForegroundColor Yellow
        & "venv\Scripts\Activate.ps1"
        
        # Install dependencies
        Write-Host "  Installing Python dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
        
        # Install Playwright
        Write-Host "  Installing Playwright browsers..." -ForegroundColor Yellow
        playwright install chromium
        
        Pop-Location
        Write-Host "✓ Backend setup complete" -ForegroundColor Green
        Write-Host ""
        
        # Dashboard setup
        Write-Host "Setting up dashboard..." -ForegroundColor Cyan
        Push-Location dashboard
        
        # Install dependencies
        Write-Host "  Installing Node dependencies (this may take a few minutes)..." -ForegroundColor Yellow
        npm install
        
        # Create .env.local
        if (-not (Test-Path ".env.local")) {
            Write-Host "  Creating .env.local..." -ForegroundColor Yellow
            "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" | Out-File -FilePath ".env.local" -Encoding utf8
        }
        
        Pop-Location
        Write-Host "✓ Dashboard setup complete" -ForegroundColor Green
        Write-Host ""
        
        # Create .env if not exists
        if (-not (Test-Path ".env")) {
            Copy-Item ".env.example" ".env"
            Write-Host "✓ .env file created" -ForegroundColor Green
        }
        
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "✓ Setup Complete!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "To start the application:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. Terminal 1 - Start Backend:" -ForegroundColor White
        Write-Host "   cd backend" -ForegroundColor Gray
        Write-Host "   venv\Scripts\Activate.ps1" -ForegroundColor Gray
        Write-Host "   `$env:QUIZ_SECRET='your-secret-key'" -ForegroundColor Gray
        Write-Host "   python main.py" -ForegroundColor Gray
        Write-Host ""
        Write-Host "2. Terminal 2 - Start Dashboard:" -ForegroundColor White
        Write-Host "   cd dashboard" -ForegroundColor Gray
        Write-Host "   npm run dev" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Then access:" -ForegroundColor Cyan
        Write-Host "  Dashboard: http://localhost:3000" -ForegroundColor White
        Write-Host "  Backend: http://localhost:8000" -ForegroundColor White
        Write-Host ""
        Write-Host "IMPORTANT: Remember to set QUIZ_SECRET in .env!" -ForegroundColor Yellow
    }
    
    "3" {
        Write-Host "Setup cancelled." -ForegroundColor Yellow
        exit 0
    }
    
    default {
        Write-Host "Invalid choice. Setup cancelled." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "For more information, see QUICKSTART.md and README.md" -ForegroundColor Cyan
Write-Host ""
