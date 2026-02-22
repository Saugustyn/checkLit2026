# checkLit – Uruchomienie backendu i frontendu
# Uruchom: .\start.ps1

$BackendPath  = "$PSScriptRoot\backend"
$FrontendPath = "$PSScriptRoot\frontend"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  checkLit - Uruchamianie serwisow..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Backend
Write-Host "`n[1/2] Uruchamiam backend (http://localhost:8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList `
  "-NoExit", `
  "-ExecutionPolicy", "Bypass", `
  "-Command", `
  "cd '$BackendPath'; Write-Host 'BACKEND' -ForegroundColor Green; & .\venv\Scripts\python.exe -m uvicorn app.main:app --reload"

Start-Sleep -Seconds 2

# Frontend
Write-Host "[2/2] Uruchamiam frontend (http://localhost:5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-ExecutionPolicy", "Bypass", `
    "-Command", `
    "cd '$FrontendPath'; Write-Host 'FRONTEND' -ForegroundColor Green; npm run dev"

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Gotowe! Otwierz przegladarke:"        -ForegroundColor Green
Write-Host "  http://localhost:5173"                 -ForegroundColor Green
Write-Host "  http://localhost:8000/docs (Swagger)"  -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""