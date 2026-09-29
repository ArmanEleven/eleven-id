$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host "Python launcher (py) was not found. Install Python 3.11+ and try again." -ForegroundColor Red
    exit 1
}

py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Created .env from .env.example. Fill in API_ID, API_HASH and PHONE, then run .\run.bat" -ForegroundColor Yellow
} else {
    Write-Host "Dependencies installed. Starting Eleven ID..." -ForegroundColor Green
    .\.venv\Scripts\python.exe main.py
}
