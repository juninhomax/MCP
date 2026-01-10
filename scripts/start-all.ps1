Write-Host "🚀 Starting MCP Brain/Slaves Platform" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Check if Ollama is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -ErrorAction Stop
} catch {
    Write-Host "⚠️  Warning: Ollama is not running. Please start Ollama first." -ForegroundColor Yellow
    Write-Host "   Run: ollama serve" -ForegroundColor Yellow
    exit 1
}

# Start MCP Brain
Write-Host ""
Write-Host "📡 Starting MCP Brain..." -ForegroundColor Green
Set-Location brain
if (-not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt
$brainJob = Start-Job -ScriptBlock { 
    Set-Location $using:PWD
    .\venv\Scripts\Activate.ps1
    python main.py 
}
Write-Host "   Brain started (Job ID: $($brainJob.Id))" -ForegroundColor Green
Set-Location ..

# Wait for brain to be ready
Write-Host "   Waiting for Brain to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Generate tokens
Write-Host ""
Write-Host "🔑 Generating authentication tokens..." -ForegroundColor Green
try {
    $linuxResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/token?slave_id=linux-slave-01&scopes=*" -Method Post
    $linuxToken = $linuxResponse.token
    Write-Host "   Linux token generated" -ForegroundColor Green
    Add-Content -Path "slaves\linux\.env" -Value "AUTH_TOKEN=$linuxToken"
} catch {
    Write-Host "   ⚠️  Failed to generate Linux token" -ForegroundColor Yellow
}

try {
    $windowsResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/token?slave_id=windows-slave-01&scopes=*" -Method Post
    $windowsToken = $windowsResponse.token
    Write-Host "   Windows token generated" -ForegroundColor Green
    Add-Content -Path "slaves\windows\.env" -Value "AUTH_TOKEN=$windowsToken"
} catch {
    Write-Host "   ⚠️  Failed to generate Windows token" -ForegroundColor Yellow
}

# Start Windows Slave
Write-Host ""
Write-Host "🪟 Starting Windows Slave..." -ForegroundColor Green
Set-Location slaves\windows
if (-not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt
$windowsJob = Start-Job -ScriptBlock { 
    Set-Location $using:PWD
    .\venv\Scripts\Activate.ps1
    python main.py 
}
Write-Host "   Windows Slave started (Job ID: $($windowsJob.Id))" -ForegroundColor Green
Set-Location ..\..

Write-Host ""
Write-Host "✅ Platform started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  - MCP Brain:      http://localhost:8000" -ForegroundColor White
Write-Host "  - Windows Slave:  http://localhost:8002" -ForegroundColor White
Write-Host ""
Write-Host "To stop all services, run: .\scripts\stop-all.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Job IDs saved to .jobs file" -ForegroundColor Gray
"$($brainJob.Id)" | Out-File -FilePath ".jobs"
"$($windowsJob.Id)" | Out-File -FilePath ".jobs" -Append
