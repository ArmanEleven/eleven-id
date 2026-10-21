$ErrorActionPreference = "Stop"

Write-Host "Eleven ID Online Setup" -ForegroundColor Cyan
Write-Host "This downloads the source archive from the official GitHub repository." -ForegroundColor Gray
Write-Host "Review the repository and its installer before continuing." -ForegroundColor Gray

$Target = Join-Path (Get-Location) "Eleven-ID"
if (Test-Path -LiteralPath $Target) {
    throw "The folder '$Target' already exists. Rename or move it, then run this script again."
}

$Temp = Join-Path ([IO.Path]::GetTempPath()) ("eleven-id-" + [guid]::NewGuid().ToString("N"))
$Zip = Join-Path $Temp "source.zip"
$Extract = Join-Path $Temp "extract"

try {
    New-Item -ItemType Directory -Path $Temp -Force | Out-Null
    Invoke-WebRequest -Uri "https://github.com/ArmanEleven/eleven-id/archive/refs/heads/main.zip" -OutFile $Zip
    Expand-Archive -LiteralPath $Zip -DestinationPath $Extract
    $Source = Get-ChildItem -LiteralPath $Extract -Directory | Select-Object -First 1
    if (-not $Source -or -not (Test-Path (Join-Path $Source.FullName "install.ps1"))) {
        throw "The downloaded archive did not contain the expected installer."
    }
    Move-Item -LiteralPath $Source.FullName -Destination $Target
    Write-Host "Downloaded to $Target" -ForegroundColor Green
    Write-Host "Opening the installer. It will ask for API_ID, API_HASH and PHONE." -ForegroundColor Cyan
    Write-Host "Read install.ps1 before proceeding if you have not reviewed the project source." -ForegroundColor Yellow
    $Confirm = Read-Host "Continue to the installer? (y/N)"
    if ($Confirm -notin @("y","Y","yes","YES")) {
        Write-Host "Source downloaded. Start the installer later from $Target\install.ps1."
        exit 0
    }
    Push-Location $Target
    try {
        & powershell.exe -NoProfile -File ".\install.ps1"
        if ($LASTEXITCODE -ne 0) { throw "The installer exited with code $LASTEXITCODE." }
    } finally {
        Pop-Location
    }
} finally {
    if (Test-Path -LiteralPath $Temp) {
        Remove-Item -LiteralPath $Temp -Recurse -Force -ErrorAction SilentlyContinue
    }
}
