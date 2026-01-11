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
    Write-Host "=============================================================" -ForegroundColor DarkGray
    Write-Host "ANALYSE DE LA DEMANDE" -ForegroundColor Cyan
    Write-Host "=============================================================" -ForegroundColor DarkGray
    
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json; charset=utf-8"
    }
    
    # Etape 1: Dry run pour voir le plan
    Write-Host ""
    Write-Host "[1/2] Analyse et planification..." -ForegroundColor Yellow
    $dryRunBody = @{ request = $prompt; dry_run = $true } | ConvertTo-Json
    
    try {
        $dryRunResponse = Invoke-RestMethod -Uri "$BrainUrl/api/v1/tasks" -Method Post -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($dryRunBody))
    } catch {
        Write-Host "[ERREUR] Impossible d'analyser la demande: $_" -ForegroundColor Red
        Write-Host ""
        continue
    }
    
    $dryRunTaskId = $dryRunResponse.task_id
    Start-Sleep -Seconds 2
    
    $dryRunStatus = Invoke-RestMethod -Uri "$BrainUrl/api/v1/tasks/$dryRunTaskId" -Headers $headers
    
    # Afficher les metriques LLM de l'analyse
    if ($dryRunStatus.metadata.llm_metrics_analysis) {
        $metrics = $dryRunStatus.metadata.llm_metrics_analysis
        Write-Host ""
        Write-Host "Performance LLM (Analyse):" -ForegroundColor DarkCyan
        if ($metrics.tokens_per_second) {
            Write-Host "  Vitesse: $([math]::Round($metrics.tokens_per_second, 2)) tokens/sec" -ForegroundColor Cyan
        }
        if ($metrics.tokens_generated) {
            Write-Host "  Tokens generes: $($metrics.tokens_generated)" -ForegroundColor DarkGray
        }
        if ($metrics.generation_time) {
            Write-Host "  Temps: $([math]::Round($metrics.generation_time, 2))s" -ForegroundColor DarkGray
        }
    }
    
    # Afficher le raisonnement du LLM
    if ($dryRunStatus.reasoning_steps -and $dryRunStatus.reasoning_steps.Count -gt 0) {
        Write-Host ""
        Write-Host "Raisonnement du LLM:" -ForegroundColor Magenta
        foreach ($reasoningStep in $dryRunStatus.reasoning_steps) {
            if ($reasoningStep.thought) {
                Write-Host "  - $($reasoningStep.thought)" -ForegroundColor White
            }
            if ($reasoningStep.action) {
                Write-Host "    Action: $($reasoningStep.action)" -ForegroundColor Gray
            }
        }
    }
    
    # Afficher le plan d'execution
    if ($dryRunStatus.execution_plan -and $dryRunStatus.execution_plan.steps) {
        Write-Host ""
        Write-Host "Plan d'execution:" -ForegroundColor Cyan
        $stepNum = 1
        foreach ($step in $dryRunStatus.execution_plan.steps) {
            $slaveType = if ($step.slave_type) { " (Slave: $($step.slave_type))" } else { "" }
            $toolName = if ($step.tool) { $step.tool } elseif ($step.tool_name) { $step.tool_name } else { "Unknown" }
            Write-Host "  [$stepNum] $toolName$slaveType" -ForegroundColor Yellow
            if ($step.justification) {
                Write-Host "      -> $($step.justification)" -ForegroundColor Gray
            }
            if ($step.parameters) {
                Write-Host "      Parametres:" -ForegroundColor DarkGray
                # Afficher les parametres de maniere lisible
                $stepArgs = $step.parameters
                if ($stepArgs -is [string]) {
                    try {
                        $stepArgs = $stepArgs | ConvertFrom-Json
                    } catch {
                        # Si ce n'est pas du JSON, afficher tel quel
                    }
                }
                if ($stepArgs -is [PSCustomObject] -or $stepArgs -is [hashtable]) {
                    foreach ($key in $stepArgs.PSObject.Properties.Name) {
                        $value = $stepArgs.$key
                        if ($key -eq "command" -or $key -eq "script") {
                            Write-Host "        Commande PowerShell:" -ForegroundColor Cyan
                            Write-Host "          $value" -ForegroundColor White
                        } else {
                            Write-Host "        $key = $value" -ForegroundColor DarkGray
                        }
                    }
                } else {
                    Write-Host "        $($stepArgs | ConvertTo-Json -Compress)" -ForegroundColor DarkGray
                }
            }
            $stepNum++
        }
    } else {
        Write-Host ""
        Write-Host "Plan d'execution: (generation en cours...)" -ForegroundColor Gray
    }
    
    # Afficher les metriques LLM de la planification
    if ($dryRunStatus.metadata.llm_metrics_planning) {
        $metrics = $dryRunStatus.metadata.llm_metrics_planning
        Write-Host ""
        Write-Host "Performance LLM (Planification):" -ForegroundColor DarkCyan
        if ($metrics.tokens_per_second) {
            Write-Host "  Vitesse: $([math]::Round($metrics.tokens_per_second, 2)) tokens/sec" -ForegroundColor Cyan
        }
        if ($metrics.tokens_generated) {
            Write-Host "  Tokens generes: $($metrics.tokens_generated)" -ForegroundColor DarkGray
        }
        if ($metrics.generation_time) {
            Write-Host "  Temps: $([math]::Round($metrics.generation_time, 2))s" -ForegroundColor DarkGray
        }
    }
    
    Write-Host ""
    Write-Host "=============================================================" -ForegroundColor DarkGray
    Write-Host ""
    
    # Etape 2: Execution reelle
    Write-Host "[2/2] Execution du plan..." -ForegroundColor Yellow
    $execBody = @{ request = $prompt; dry_run = $false } | ConvertTo-Json
    
    try {
        $taskResponse = Invoke-RestMethod -Uri "$BrainUrl/api/v1/tasks" -Method Post -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($execBody))
    } catch {
        Write-Host "[ERREUR] Impossible de creer la tache: $_" -ForegroundColor Red
        Write-Host ""
        continue
    }
    $taskId = $taskResponse.task_id
    
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
