# Build script for Windows
# Requires: Python 3.8+, Node.js 18+

param(
    [switch]$SkipFrontend,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BUAA Evaluation - Windows Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Clean previous builds
if ($Clean) {
    Write-Host "[1/4] Cleaning previous builds..." -ForegroundColor Yellow
    Remove-Item -Path "$ProjectRoot\dist" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$ProjectRoot\build" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$ProjectRoot\backend\web" -Recurse -Force -ErrorAction SilentlyContinue
}

# Install Python dependencies
Write-Host "[2/4] Installing Python dependencies..." -ForegroundColor Yellow
Push-Location $ProjectRoot
pip install -q pywebview pyinstaller requests beautifulsoup4
Pop-Location

# Build frontend
if (-not $SkipFrontend) {
    Write-Host "[3/4] Building frontend..." -ForegroundColor Yellow
    Push-Location "$ProjectRoot\frontend"

    if (-not (Test-Path "node_modules")) {
        npm install
    }
    npm run build

    Pop-Location
}

# Build executable
Write-Host "[4/4] Building executable..." -ForegroundColor Yellow
Push-Location $ProjectRoot

pyinstaller `
    --name "BUAA-Evaluation" `
    --onefile `
    --windowed `
    --add-data "backend\web;web" `
    --add-data "backend\evaluator.py;." `
    --hidden-import webview `
    --hidden-import webview.platforms.edgechromium `
    --hidden-import webview.platforms.winforms `
    --hidden-import clr `
    --hidden-import pythonnet `
    --icon "assets\icons\icon.ico" `
    --clean `
    --noconfirm `
    backend\main.py

Pop-Location

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Build complete!" -ForegroundColor Green
Write-Host "  Output: dist\BUAA-Evaluation.exe" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
