Write-Host "[TEST] Test simple de la plateforme MCP Brain/Slaves" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Générer un token
Write-Host "[1/4] Generation d'un token d'authentification..." -ForegroundColor Yellow
$tokenResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/token?slave_id=windows-slave-01&scopes=*" -Method Post
$token = $tokenResponse.token
Write-Host "   [OK] Token genere: $($token.Substring(0,20))..." -ForegroundColor Green

# 2. Enregistrer le slave
Write-Host ""
Write-Host "[2/4] Enregistrement du Windows Slave..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$slaveInfo = @{
    slave_id = "windows-slave-01"
    slave_type = "windows"
    endpoint = "http://localhost:8002"
    capabilities = @("powershell_exec", "get_service", "get_process", "file_read")
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/slaves/register" -Method Post -Headers $headers -Body $slaveInfo
    Write-Host "   [OK] Slave enregistre" -ForegroundColor Green
} catch {
    Write-Host "   [WARN] Erreur lors de l'enregistrement (peut-etre deja enregistre)" -ForegroundColor Yellow
}

# 3. Créer une tâche simple
Write-Host ""
Write-Host "[3/4] Creation d'une tache de test..." -ForegroundColor Yellow
$taskRequest = @{
    request = "Liste les 5 processus Windows qui consomment le plus de memoire"
    dry_run = $false
} | ConvertTo-Json

$taskResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/tasks" -Method Post -Headers $headers -Body $taskRequest
$taskId = $taskResponse.task_id
Write-Host "   [OK] Tache creee: $taskId" -ForegroundColor Green

# 4. Attendre et récupérer le résultat
Write-Host ""
Write-Host "[4/4] Attente du resultat (10 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

$taskStatus = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/tasks/$taskId" -Headers $headers
Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "Resultat de la tache:" -ForegroundColor Cyan
Write-Host "Status: $($taskStatus.status)" -ForegroundColor $(if ($taskStatus.status -eq "completed") { "Green" } else { "Yellow" })
Write-Host ""
Write-Host "Reponse:" -ForegroundColor White
$taskStatus | ConvertTo-Json -Depth 10
Write-Host ""
