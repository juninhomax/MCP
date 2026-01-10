Clear-Host
Write-Host "MCP Brain/Slaves - Chat Interactif" -ForegroundColor Cyan
Write-Host "Tapez 'exit' pour quitter" -ForegroundColor Gray
Write-Host ""

$BrainUrl = "http://localhost:8000"
$SlaveId = "windows-slave-01"

# Generer le token
Write-Host "Generation du token..." -ForegroundColor Yellow
$tokenUri = $BrainUrl + "/api/v1/auth/token?slave_id=" + $SlaveId + "&scopes=*"
$tokenResponse = Invoke-RestMethod -Uri $tokenUri -Method Post
$token = $tokenResponse.token
Write-Host "Token genere!" -ForegroundColor Green
Write-Host ""

while ($true) {
    Write-Host "Vous> " -NoNewline -ForegroundColor Cyan
    $prompt = Read-Host
    
    if ($prompt -eq "exit") { break }
    if ($prompt -eq "") { continue }
    
    Write-Host ""
    Write-Host "Analyse en cours..." -ForegroundColor Yellow
    
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json; charset=utf-8"
    }
    
    $body = @{ request = $prompt; dry_run = $false } | ConvertTo-Json
    
    try {
        $taskResponse = Invoke-RestMethod -Uri "$BrainUrl/api/v1/tasks" -Method Post -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($body))
    } catch {
        Write-Host "[ERREUR] Impossible de creer la tache: $_" -ForegroundColor Red
        Write-Host ""
        continue
    }
    $taskId = $taskResponse.task_id
    
    Write-Host "Tache creee: $taskId" -ForegroundColor Yellow
    Write-Host "Execution..." -ForegroundColor Yellow
    
    Start-Sleep -Seconds 3
    
    $taskStatus = Invoke-RestMethod -Uri "$BrainUrl/api/v1/tasks/$taskId" -Headers $headers
    
    Write-Host ""
    Write-Host "=============================================================" -ForegroundColor DarkGray
    Write-Host "RESULTAT:" -ForegroundColor Green
    Write-Host "Status: $($taskStatus.status)"
    
    if ($taskStatus.result -and $taskStatus.result.steps) {
        foreach ($step in $taskStatus.result.steps) {
            Write-Host ""
            if ($step.success) {
                Write-Host "[OK] Etape $($step.step + 1) - Succes" -ForegroundColor Green
                if ($step.output) {
                    Write-Host $step.output -ForegroundColor White
                } else {
                    Write-Host "(Aucune sortie)" -ForegroundColor Gray
                }
            } else {
                Write-Host "[ERREUR] Etape $($step.step + 1) - Erreur" -ForegroundColor Red
                if ($step.error) {
                    Write-Host $step.error -ForegroundColor Red
                }
            }
        }
    } else {
        Write-Host ""
        Write-Host "(Aucun resultat detaille disponible)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Reponse complete:" -ForegroundColor Yellow
        $taskStatus | ConvertTo-Json -Depth 5
    }
    
    Write-Host ""
    Write-Host "=============================================================" -ForegroundColor DarkGray
    Write-Host ""
}

Write-Host "Au revoir!" -ForegroundColor Yellow
