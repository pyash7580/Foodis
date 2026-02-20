# Direct PowerShell server startup - no batch files needed
Write-Host "Starting Foodis Development Server..." -ForegroundColor Green
Write-Host ""

# Find Python executable
$pythonCmd = $null
if (Test-Path ".venv\Scripts\python.exe") {
    Write-Host "✓ Found Python in virtual environment" -ForegroundColor Green
    $pythonCmd = ".venv\Scripts\python.exe"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "✓ Using system Python" -ForegroundColor Green
    $pythonCmd = "python"
} else {
    Write-Host "✗ ERROR: Python is not installed or not available" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python version
try {
    $version = & $pythonCmd --version 2>$null
    Write-Host "✓ Python version: $version" -ForegroundColor Cyan
} catch {
    Write-Host "✗ ERROR: Failed to run Python" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run migrations
Write-Host ""
Write-Host "Running migrations..." -ForegroundColor Yellow
try {
    & $pythonCmd manage.py makemigrations --noinput
    & $pythonCmd manage.py migrate --noinput
    Write-Host "✓ Migrations completed successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠ WARNING: Migration failed, continuing anyway..." -ForegroundColor Yellow
}

# Start Django server
Write-Host ""
Write-Host "Starting Django server..." -ForegroundColor Yellow
Write-Host "🌐 Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🛑 Press CTRL+C to stop the server" -ForegroundColor White
Write-Host ""

try {
    & $pythonCmd manage.py runserver 0.0.0.0:8000
} catch {
    Write-Host "✗ ERROR: Failed to start Django server" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
