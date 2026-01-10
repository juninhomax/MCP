Write-Host "🛑 Stopping MCP Brain/Slaves Platform" -ForegroundColor Red
Write-Host "======================================" -ForegroundColor Red

if (Test-Path ".jobs") {
    $jobs = Get-Content ".jobs"
    foreach ($jobId in $jobs) {
        try {
            Stop-Job -Id $jobId -ErrorAction SilentlyContinue
            Remove-Job -Id $jobId -ErrorAction SilentlyContinue
            Write-Host "Stopped job $jobId" -ForegroundColor Yellow
        } catch {
            Write-Host "Could not stop job $jobId" -ForegroundColor Gray
        }
    }
    Remove-Item ".jobs"
    Write-Host "✅ All services stopped" -ForegroundColor Green
} else {
    Write-Host "⚠️  No .jobs file found. Stopping all Python processes..." -ForegroundColor Yellow
    Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*mcp-brain-slaves*" } | Stop-Process -Force
    Write-Host "✅ Stopped all matching processes" -ForegroundColor Green
}
