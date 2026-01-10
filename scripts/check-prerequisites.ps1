Write-Host "[CHECK] Verification des prerequis MCP Brain/Slaves" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

$allOk = $true

# Fonction pour vérifier si une commande existe
function Test-Command {
    param($Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) { return $true }
    } catch {
        return $false
    }
}

# 1. Python
Write-Host "Python 3.11+:" -NoNewline
if (Test-Command python) {
    $version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
    $versionNum = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
    
    if ([version]$versionNum -ge [version]"3.11") {
        Write-Host " [OK] $version" -ForegroundColor Green
    } else {
        Write-Host " [WARN] $version (3.11+ recommande)" -ForegroundColor Yellow
        $allOk = $false
    }
} else {
    Write-Host " [ERROR] Non installe" -ForegroundColor Red
    Write-Host "   -> https://www.python.org/downloads/" -ForegroundColor Gray
    $allOk = $false
}

# 2. pip
Write-Host "pip:          " -NoNewline
if (Test-Command pip) {
    $pipVersion = pip --version 2>$null | Select-String -Pattern "pip (\d+\.\d+\.\d+)" | ForEach-Object { $_.Matches.Groups[1].Value }
    Write-Host " [OK] $pipVersion" -ForegroundColor Green
} else {
    Write-Host " ❌ Non installé" -ForegroundColor Red
    $allOk = $false
}

# 3. Ollama
Write-Host "Ollama:       " -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host " [OK] En cours d'execution" -ForegroundColor Green
    
    # Vérifier les modèles
    $models = ($response.Content | ConvertFrom-Json).models
    Write-Host "  Modèles installés:" -ForegroundColor Gray
    if ($models.Count -eq 0) {
        Write-Host "    [WARN] Aucun modele installe" -ForegroundColor Yellow
        Write-Host "    -> Executer: ollama pull qwen2.5-coder:14b" -ForegroundColor Gray
    } else {
        foreach ($model in $models) {
            $size = [math]::Round($model.size / 1GB, 2)
            Write-Host "    - $($model.name) ($size GB)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host " [ERROR] Non accessible" -ForegroundColor Red
    Write-Host "   -> https://ollama.com/download" -ForegroundColor Gray
    $allOk = $false
}

# 4. Git (optionnel)
Write-Host "Git:          " -NoNewline
if (Test-Command git) {
    $gitVersion = git --version 2>$null
    Write-Host " [OK] $gitVersion" -ForegroundColor Green
} else {
    Write-Host " [WARN] Non installe (optionnel)" -ForegroundColor Yellow
    Write-Host "   -> https://git-scm.com/download/win" -ForegroundColor Gray
}

# 5. Ports disponibles
Write-Host ""
Write-Host "Ports réseau:" -ForegroundColor Cyan

$ports = @(8000, 8001, 8002, 11434)
foreach ($port in $ports) {
    Write-Host "  Port $port" -NoNewline
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host ": [WARN] Utilise par PID $($connection.OwningProcess)" -ForegroundColor Yellow
        if ($port -ne 11434) {
            $allOk = $false
        }
    } else {
        Write-Host ": [OK] Disponible" -ForegroundColor Green
    }
}

# 6. Espace disque
Write-Host ""
Write-Host "Espace disque:" -ForegroundColor Cyan
$drive = Get-PSDrive C
$freeGB = [math]::Round($drive.Free / 1GB, 2)
Write-Host "  Disque C: " -NoNewline
if ($freeGB -gt 20) {
    Write-Host "[OK] $freeGB GB disponibles" -ForegroundColor Green
} else {
    Write-Host "[WARN] $freeGB GB disponibles (20 GB recommandes)" -ForegroundColor Yellow
}

# 7. Environnements virtuels
Write-Host ""
Write-Host "Environnements virtuels:" -ForegroundColor Cyan

Write-Host "  Brain:        " -NoNewline
if (Test-Path "brain\venv") {
    Write-Host "[OK] Configure" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Non configure" -ForegroundColor Red
    Write-Host "    -> Executer: .\scripts\install-windows.ps1" -ForegroundColor Gray
    $allOk = $false
}

Write-Host "  Windows Slave:" -NoNewline
if (Test-Path "slaves\windows\venv") {
    Write-Host "[OK] Configure" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Non configure" -ForegroundColor Red
    Write-Host "    -> Executer: .\scripts\install-windows.ps1" -ForegroundColor Gray
    $allOk = $false
}

# 8. Fichiers de configuration
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan

Write-Host "  brain\.env:   " -NoNewline
if (Test-Path "brain\.env") {
    Write-Host "[OK] Present" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Manquant" -ForegroundColor Red
    $allOk = $false
}

Write-Host "  slaves\windows\.env:" -NoNewline
if (Test-Path "slaves\windows\.env") {
    Write-Host "[OK] Present" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Manquant" -ForegroundColor Red
    $allOk = $false
}

# Résumé
Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
if ($allOk) {
    Write-Host "[OK] Tous les prerequis sont satisfaits!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Vous pouvez démarrer la plateforme:" -ForegroundColor White
    Write-Host "  .\scripts\start-all.ps1" -ForegroundColor Gray
} else {
    Write-Host "[WARN] Certains prerequis manquent" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Pour installer automatiquement:" -ForegroundColor White
    Write-Host "  .\scripts\install-windows.ps1" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Ou consultez le guide:" -ForegroundColor White
    Write-Host "  INSTALLATION_WINDOWS.md" -ForegroundColor Gray
}
Write-Host ""
