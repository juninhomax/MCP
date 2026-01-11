# Test pour voir ce que retourne le dry run
$brainUrl = "http://localhost:8000"
$token = (Invoke-RestMethod -Uri "$brainUrl/api/v1/auth/token?slave_id=test&scopes=*" -Method Post).token

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$body = @{ request = "que contient le dossier C:\MCP-Slave"; dry_run = $true } | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$brainUrl/api/v1/tasks" -Method Post -Headers $headers -Body $body
$taskId = $response.task_id

Start-Sleep -Seconds 3

$task = Invoke-RestMethod -Uri "$brainUrl/api/v1/tasks/$taskId" -Headers $headers

Write-Host "=== TASK COMPLETE ===" -ForegroundColor Cyan
$task | ConvertTo-Json -Depth 10
