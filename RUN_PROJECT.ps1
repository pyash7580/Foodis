# PowerShell helper to run RUN_PROJECT.bat or run equivalent commands directly when cmd.exe isn't available
# Behavior:
# - If cmd.exe is available via $env:COMSPEC, launch the batch in a new cmd window.
# - If not, fall back to launching backend/frontend directly from PowerShell using available executables.

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$batchPath = Join-Path $scriptDir 'RUN_PROJECT.bat'
if (-Not (Test-Path $batchPath)) {
    Write-Error "RUN_PROJECT.bat not found at $batchPath"
    exit 1
}

if ($env:COMSPEC -and (Test-Path $env:COMSPEC)) {
    Write-Output "Launching RUN_PROJECT.bat via COMSPEC ($env:COMSPEC)..."
    Start-Process -FilePath $env:COMSPEC -ArgumentList "/k `"$batchPath`"" -WindowStyle Normal
    exit 0
}

# Fallback: run the commands from PowerShell (for environments without cmd.exe)
Write-Output "COMSPEC not found; running servers from PowerShell instead (no new windows will be spawned)."

# detect Python exe (prefer .venv)
$pyCandidates = @(
    (Join-Path $scriptDir '.venv\Scripts\python.exe');
    (Join-Path $scriptDir 'venv\Scripts\python.exe');
    'python'
)
$pythonExe = $null
foreach ($p in $pyCandidates) {
    if ($p -eq 'python') {
        $cmd = Get-Command python -ErrorAction SilentlyContinue
        if ($cmd) { $pythonExe = $cmd.Source; break }
    } else {
        if (Test-Path $p) { $pythonExe = $p; break }
    }
}
if (-not $pythonExe) {
    Write-Error "No Python interpreter found. Please install Python or create a virtual environment at .venv"
    exit 1
}
Write-Output "Using Python: $pythonExe"

# Start backend as a job
Write-Output "Starting Django backend (manage.py runserver)..."
$backendArgs = 'manage.py','runserver','0.0.0.0:8000'
$backendJob = Start-Process -FilePath $pythonExe -ArgumentList $backendArgs -WorkingDirectory $scriptDir -PassThru
Start-Sleep -Seconds 1

# Wait for backend to respond
$backendOk = $false
for ($i=0; $i -lt 20; $i++) {
    try {
        $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:8000' -TimeoutSec 2
        $backendOk = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
if ($backendOk) { Write-Output 'Backend is responding at http://localhost:8000' } else { Write-Warning 'Backend did not respond within timeout; it may still be starting.' }

# Frontend handling
$frontendDir = Join-Path $scriptDir 'frontend'
if (Test-Path $frontendDir) {
    $node = Get-Command node -ErrorAction SilentlyContinue
    $npm = Get-Command npm -ErrorAction SilentlyContinue
    $npx = Get-Command npx -ErrorAction SilentlyContinue
    if ($npm) {
        Write-Output 'Starting frontend dev server: npm start (opens a new PowerShell window)...'
        Start-Process -FilePath 'powershell' -ArgumentList "-NoExit -Command cd `"$frontendDir`"; npm start" -WindowStyle Normal
    } elseif ((Test-Path (Join-Path $frontendDir 'build')) -and $npx) {
        Write-Output 'npm not found; serving built frontend with npx serve -s build -l 3000 (opens a new PowerShell window)...'
        Start-Process -FilePath 'powershell' -ArgumentList "-NoExit -Command cd `"$frontendDir`"; npx serve -s build -l 3000" -WindowStyle Normal
    } else {
        Write-Warning 'Cannot start frontend: npm not found and no build available. Install Node.js or create a build with "cd frontend && npm run build".'
    }
} else {
    Write-Warning "Frontend directory not found at: $frontendDir"
}

Write-Output 'Servers launched (PowerShell fallback). Use your shell to monitor logs.'

