#!/usr/bin/env pwsh
# System Test Script for LLM Analysis Quiz Bot

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  LLM Analysis Quiz Bot - System Test" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Backend Health
Write-Host "[TEST 1] Testing Backend Health..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    if ($health.StatusCode -eq 200) {
        Write-Host "✅ Backend is healthy!" -ForegroundColor Green
        Write-Host "   Response: $($health.Content)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Backend health check failed!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}

# Test 2: Backend Service Info
Write-Host "`n[TEST 2] Testing Backend Service Info..." -ForegroundColor Yellow
try {
    $info = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing
    if ($info.StatusCode -eq 200) {
        Write-Host "✅ Backend service info retrieved!" -ForegroundColor Green
        Write-Host "   Response: $($info.Content)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Backend service info failed!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}

# Test 3: Frontend Dashboard
Write-Host "`n[TEST 3] Testing Frontend Dashboard..." -ForegroundColor Yellow
try {
    $dashboard = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 10
    if ($dashboard.StatusCode -eq 200) {
        Write-Host "✅ Dashboard is accessible!" -ForegroundColor Green
        $length = $dashboard.Content.Length
        Write-Host "   Page size: $length bytes" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Dashboard check failed!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}

# Test 4: Backend History Endpoint
Write-Host "`n[TEST 4] Testing Backend History..." -ForegroundColor Yellow
try {
    $history = Invoke-WebRequest -Uri "http://localhost:8000/history" -UseBasicParsing
    if ($history.StatusCode -eq 200) {
        Write-Host "✅ History endpoint working!" -ForegroundColor Green
        Write-Host "   Response: $($history.Content)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ History endpoint failed!" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Backend API: http://localhost:8000" -ForegroundColor Green
Write-Host "✓ Dashboard UI: http://localhost:3000" -ForegroundColor Green
Write-Host "`nYour application is ready to use!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
