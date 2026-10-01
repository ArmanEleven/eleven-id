$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host "Python launcher (py) was not found. Install Python 3.11+ and try again." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Eleven ID Installer ===" -ForegroundColor Cyan
Write-Host ""

py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host ""
Write-Host "=== Telegram API Setup ===" -ForegroundColor Cyan
Write-Host "Get your API credentials from:" -ForegroundColor White
Write-Host "https://my.telegram.org/apps" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Sign in with your Telegram number." -ForegroundColor Gray
Write-Host "2. Open 'API development tools'." -ForegroundColor Gray
Write-Host "3. Create an application if you do not already have one." -ForegroundColor Gray
Write-Host "4. Copy the 'api_id' and 'api_hash' values." -ForegroundColor Gray
Write-Host ""

$ApiId = Read-Host "Enter API_ID"
$ApiHash = Read-Host "Enter API_HASH"
$Phone = Read-Host "Enter Telegram phone number (example: +989xxxxxxxxxx)"

if ([string]::IsNullOrWhiteSpace($ApiId) -or
    [string]::IsNullOrWhiteSpace($ApiHash) -or
    [string]::IsNullOrWhiteSpace($Phone)) {
    Write-Host ""
    Write-Host "API_ID, API_HASH and PHONE are required." -ForegroundColor Red
    exit 1
}

@"
API_ID=$ApiId
API_HASH=$ApiHash
PHONE=$Phone
"@ | Set-Content -Path .env -Encoding UTF8

Write-Host ""
Write-Host ".env created successfully." -ForegroundColor Green
Write-Host "Starting Eleven ID..." -ForegroundColor Green
Write-Host ""

.\.venv\Scripts\python.exe main.py
