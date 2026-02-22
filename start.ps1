# checkLit – Uruchomienie backendu i frontendu
# Uruchom: .\start.ps1

$ErrorActionPreference = "Stop"

$BackendPath  = Join-Path $PSScriptRoot "backend"
$FrontendPath = Join-Path $PSScriptRoot "frontend"

$VenvPython = Join-Path $BackendPath "venv\Scripts\python.exe"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  checkLit - Uruchamianie serwisow..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Szybka walidacja venv
if (-not (Test-Path $VenvPython)) {
  Write-Host "`n[ERR] Nie znaleziono venv w backend\venv" -ForegroundColor Red
  Write-Host "Utworz venv i zainstaluj zaleznosci:" -ForegroundColor Yellow
  Write-Host "  cd `"$BackendPath`"" -ForegroundColor Yellow
  Write-Host "  python -m venv venv" -ForegroundColor Yellow
  Write-Host "  .\venv\Scripts\python.exe -m pip install -r requirements.txt" -ForegroundColor Yellow
  exit 1
}

# Backend
Write-Host "`n[1/2] Uruchamiam backend (http://localhost:8000)..." -ForegroundColor Yellow

$BackendCmd = @"
cd `"$BackendPath`";
Write-Host 'BACKEND' -ForegroundColor Green;
& `"$VenvPython`" -m uvicorn app.main:app --reload
"@

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $BackendCmd

Start-Sleep -Seconds 2

# Frontend
Write-Host "[2/2] Uruchamiam frontend (http://localhost:5173)..." -ForegroundColor Yellow

$FrontendCmd = @"
cd `"$FrontendPath`";
Write-Host 'FRONTEND' -ForegroundColor Green;
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $FrontendCmd

Start-Sleep -Seconds 1

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Gotowe! Otworz przegladarke:"         -ForegroundColor Green
Write-Host "  http://localhost:5173"               -ForegroundColor Green
Write-Host "  http://localhost:8000/docs (Swagger)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""