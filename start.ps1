$ErrorActionPreference = "Stop"
$BackendPath  = Join-Path $PSScriptRoot "backend"
$FrontendPath = Join-Path $PSScriptRoot "frontend"
$VenvPython   = Join-Path $BackendPath "venv\Scripts\python.exe"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  checkLit - Uruchamianie serwisow..."  -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# [0/2] Czyszczenie starych procesow
Write-Host "`n[0/2] Czyszcze stare procesy..." -ForegroundColor Magenta

$uvicorn = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*" -or $_.MainWindowTitle -like "*BACKEND*"
}
if ($uvicorn) {
    $uvicorn | Stop-Process -Force
    Write-Host "  Zatrzymano: uvicorn (backend)" -ForegroundColor DarkGray
}

$port8000 = netstat -ano | Select-String ":8000 " | ForEach-Object {
    ($_ -split "\s+")[-1]
} | Select-Object -Unique
foreach ($procId in $port8000) {
    if ($procId -match "^\d+$" -and $procId -ne "0") {
        try {
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            Write-Host "  Zatrzymano PID $procId (port 8000)" -ForegroundColor DarkGray
        } catch {}
    }
}

$port5173 = netstat -ano | Select-String ":5173 " | ForEach-Object {
    ($_ -split "\s+")[-1]
} | Select-Object -Unique
foreach ($procId in $port5173) {
    if ($procId -match "^\d+$" -and $procId -ne "0") {
        try {
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            Write-Host "  Zatrzymano PID $procId (port 5173)" -ForegroundColor DarkGray
        } catch {}
    }
}

Start-Sleep -Seconds 1
Write-Host "  Porty 8000 i 5173 zwolnione." -ForegroundColor DarkGray

# Walidacja venv
if (-not (Test-Path $VenvPython)) {
    Write-Host "`n[ERR] Nie znaleziono venv w backend\venv" -ForegroundColor Red
    Write-Host "Utworz venv i zainstaluj zaleznosci:" -ForegroundColor Yellow
    Write-Host "  cd `"$BackendPath`"" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\python.exe -m pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# [1/2] Backend
Write-Host "`n[1/2] Uruchamiam backend (http://localhost:8000)..." -ForegroundColor Yellow
$BackendCmd = @"
cd `"$BackendPath`";
Write-Host 'BACKEND uruchomiony' -ForegroundColor Green;
& `"$VenvPython`" -m uvicorn app.main:app --reload --port 8000
"@
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $BackendCmd

Start-Sleep -Seconds 2

# [2/2] Frontend
Write-Host "[2/2] Uruchamiam frontend (http://localhost:5173)..." -ForegroundColor Yellow
$FrontendCmd = @"
cd `"$FrontendPath`";
Write-Host 'FRONTEND uruchomiony' -ForegroundColor Green;
npm run dev
"@
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $FrontendCmd

Start-Sleep -Seconds 1

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Gotowe! Otworz przegladarke:"          -ForegroundColor Green
Write-Host "  http://localhost:5173"                 -ForegroundColor Green
Write-Host "  http://localhost:8000/docs (Swagger)"  -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""