# One-Click Run Script for Foodis Platform
# Starts Django Backend and React Frontend in separate windows

$ErrorActionPreference = "Stop"
$scriptDir = $PSScriptRoot

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "      Starting Foodis Platform" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# --- Backend Configuration ---
if (Test-Path "$scriptDir\.venv\Scripts\python.exe") {
    $python = "$scriptDir\.venv\Scripts\python.exe"
    Write-Host "[Backend] Using virtual environment Python" -ForegroundColor Green
}
else {
    $python = "python"
    Write-Host "[Backend] Using system Python" -ForegroundColor Yellow
}

# --- Frontend Configuration ---
$frontendDir = Join-Path $scriptDir "frontend"

# --- Launch Backend ---
Write-Host "Launching Backend Server..." -ForegroundColor Yellow
# We use a slightly different approach to ensure the window stays open and executes the command
$backendArgs = "-NoExit", "-Command", "& '$python' manage.py runserver 0.0.0.0:8000"
Start-Process -FilePath "powershell.exe" -ArgumentList $backendArgs -WorkingDirectory $scriptDir

# --- Launch Frontend ---
if (Test-Path $frontendDir) {
    Write-Host "Launching Frontend Server..." -ForegroundColor Yellow
    if (-not (Test-Path "$frontendDir\node_modules")) {
        Write-Warning "node_modules not found in frontend. You might need to run 'npm install' first."
    }
    
    $frontendArgs = "-NoExit", "-Command", "npm start"
    Start-Process -FilePath "powershell.exe" -ArgumentList $frontendArgs -WorkingDirectory $frontendDir
}
else {
    Write-Error "Frontend directory not found at $frontendDir"
}

Write-Host "------------------------------------------" -ForegroundColor Green
Write-Host "Done! Check the new PowerShell windows." -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Gray
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "------------------------------------------" -ForegroundColor Green

