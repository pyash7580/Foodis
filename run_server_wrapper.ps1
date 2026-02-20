# PowerShell script to run the Foodis server
# This script properly handles batch file execution in PowerShell

Write-Host "Starting Foodis Development Server..." -ForegroundColor Green
Write-Host ""

# Get the directory of this script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$batchPath = Join-Path $scriptDir 'start_server.bat'

# Check if batch file exists
if (-not (Test-Path $batchPath)) {
    Write-Host "ERROR: start_server.bat not found at $batchPath" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the batch file using cmd.exe
try {
    Write-Host "Executing server startup script..." -ForegroundColor Yellow
    $process = Start-Process -FilePath $env:COMSPEC -ArgumentList "/c", "`"$batchPath`"" -WorkingDirectory $scriptDir -PassThru -Wait
    
    if ($process.ExitCode -eq 0) {
        Write-Host "Server startup completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Server startup exited with code: $($process.ExitCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: Failed to execute server startup script" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Cyan
Read-Host
