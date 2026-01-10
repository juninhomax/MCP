Write-Host "🧪 Testing MCP Brain/Slaves Platform" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if services are running
Write-Host ""
Write-Host "1️⃣ Checking services health..." -ForegroundColor Yellow

try {
    $brainHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -ErrorAction Stop
    Write-Host "   ✅ Brain is healthy: $($brainHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Brain is not responding" -ForegroundColor Red
    exit 1
}

try {
    $windowsHealth = Invoke-RestMethod -Uri "http://localhost:8002/health" -ErrorAction Stop
    Write-Host "   ✅ Windows Slave is healthy: $($windowsHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Windows Slave is not responding" -ForegroundColor Yellow
}

# Generate test token
Write-Host ""
Write-Host "2️⃣ Generating test token..." -ForegroundColor Yellow
try {
    $tokenResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/token?slave_id=test-client&scopes=*" -Method Post
    $token = $tokenResponse.token
    Write-Host "   ✅ Token generated" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to generate token" -ForegroundColor Red
    exit 1
}

# Test 1: Dry run task
Write-Host ""
Write-Host "3️⃣ Test 1: Dry run task..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    $body = @{
        request = "List all running processes"
        dry_run = $true
    } | ConvertTo-Json

    $taskResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/tasks" -Method Post -Headers $headers -Body $body
    Write-Host "   ✅ Dry run task created: $($taskResponse.task_id)" -ForegroundColor Green
    
    Start-Sleep -Seconds 2
    $taskDetails = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/tasks/$($taskResponse.task_id)" -Headers $headers
    Write-Host "   ✅ Task status: $($taskDetails.status)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Dry run test failed: $_" -ForegroundColor Red
}

# Test 2: Windows service check
Write-Host ""
Write-Host "4️⃣ Test 2: Check Windows service..." -ForegroundColor Yellow
try {
    $body = @{
        request = "Get status of Windows Time service"
        dry_run = $false
    } | ConvertTo-Json

    $taskResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/tasks" -Method Post -Headers $headers -Body $body
    Write-Host "   ✅ Task created: $($taskResponse.task_id)" -ForegroundColor Green
    
    Start-Sleep -Seconds 3
    $taskDetails = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/tasks/$($taskResponse.task_id)" -Headers $headers
    Write-Host "   ✅ Task completed: $($taskDetails.status)" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Service check test failed: $_" -ForegroundColor Yellow
}

# Test 3: File read
Write-Host ""
Write-Host "5️⃣ Test 3: Read file..." -ForegroundColor Yellow
try {
    $body = @{
        request = "Read first 5 lines of C:\Windows\System32\drivers\etc\hosts"
        dry_run = $false
    } | ConvertTo-Json

    $taskResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/tasks" -Method Post -Headers $headers -Body $body
    Write-Host "   ✅ Task created: $($taskResponse.task_id)" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  File read test failed: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Platform testing completed!" -ForegroundColor Green
Write-Host ""
