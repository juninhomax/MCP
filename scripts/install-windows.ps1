Write-Host "[INSTALL] Installation automatique MCP Brain/Slaves - Windows" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier les privilèges administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[WARN] Certaines operations necessitent des privileges administrateur" -ForegroundColor Yellow
    Write-Host "   Relancez PowerShell en tant qu'administrateur si nécessaire" -ForegroundColor Yellow
    Write-Host ""
}

# Fonction pour vérifier si une commande existe
function Test-Command {
    param($Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) { return $true }
    } catch {
        return $false
    }
}

# 1. Vérifier Python
Write-Host "[1/5] Verification de Python..." -ForegroundColor Yellow
if (Test-Command python) {
    $pythonVersion = python --version 2>&1
    Write-Host "   [OK] Python trouve: $pythonVersion" -ForegroundColor Green
    
    # Vérifier la version
    $version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if ([version]$version -lt [version]"3.11") {
        Write-Host "   [WARN] Python $version detecte. Python 3.11+ recommande" -ForegroundColor Yellow
        Write-Host "   Télécharger depuis: https://www.python.org/downloads/" -ForegroundColor Yellow
    }
} else {
    Write-Host "   [ERROR] Python non trouve" -ForegroundColor Red
    Write-Host "   Installation requise:" -ForegroundColor Yellow
    Write-Host "      1. Aller sur https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "      2. Télécharger Python 3.11+" -ForegroundColor White
    Write-Host "      3. IMPORTANT: Cocher 'Add Python to PATH'" -ForegroundColor White
    Write-Host ""
    $continue = Read-Host "Continuer sans Python? (y/N)"
    if ($continue -ne "y") {
        exit 1
    }
}

# 2. Vérifier Ollama
Write-Host ""
Write-Host "[2/5] Verification d'Ollama..." -ForegroundColor Yellow
try {
    $ollamaTest = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "   [OK] Ollama est en cours d'execution" -ForegroundColor Green
    
    # Vérifier si le modèle est téléchargé
    $models = $ollamaTest.Content | ConvertFrom-Json
    $hasQwen = $models.models | Where-Object { $_.name -like "*qwen2.5-coder*" }
    
    if ($hasQwen) {
        Write-Host "   [OK] Modele Qwen detecte: $($hasQwen.name)" -ForegroundColor Green
    } else {
        Write-Host "   [WARN] Modele Qwen non trouve" -ForegroundColor Yellow
        Write-Host "   Telechargement du modele..." -ForegroundColor Yellow
        Write-Host "      Cela peut prendre 10-30 minutes (~8GB)" -ForegroundColor Gray
        $download = Read-Host "Télécharger qwen2.5-coder:14b maintenant? (y/N)"
        if ($download -eq "y") {
            ollama pull qwen2.5-coder:14b
        }
    }
} catch {
    Write-Host "   [ERROR] Ollama n'est pas accessible" -ForegroundColor Red
    Write-Host "   Installation requise:" -ForegroundColor Yellow
    Write-Host "      1. Aller sur https://ollama.com/download" -ForegroundColor White
    Write-Host "      2. Télécharger Ollama pour Windows" -ForegroundColor White
    Write-Host "      3. Installer et lancer l'application" -ForegroundColor White
    Write-Host ""
    $continue = Read-Host "Continuer sans Ollama? (y/N)"
    if ($continue -ne "y") {
        exit 1
    }
}

# 3. Configurer l'environnement virtuel pour Brain
Write-Host ""
Write-Host "[3/5] Configuration de MCP Brain..." -ForegroundColor Yellow
Set-Location brain

if (-not (Test-Path "venv")) {
    Write-Host "   Creation de l'environnement virtuel..." -ForegroundColor Gray
    python -m venv venv
}

Write-Host "   Installation des dependances..." -ForegroundColor Gray
.\venv\Scripts\Activate.ps1
pip install -q --upgrade pip
pip install -q -r requirements.txt

if (-not (Test-Path ".env")) {
    Write-Host "   Creation du fichier de configuration..." -ForegroundColor Gray
    Copy-Item .env.example .env
}

Write-Host "   [OK] MCP Brain configure" -ForegroundColor Green
deactivate
Set-Location ..

# 4. Configurer l'environnement virtuel pour Windows Slave
Write-Host ""
Write-Host "[4/5] Configuration de MCP Slave Windows..." -ForegroundColor Yellow
Set-Location slaves\windows

if (-not (Test-Path "venv")) {
    Write-Host "   Creation de l'environnement virtuel..." -ForegroundColor Gray
    python -m venv venv
}

Write-Host "   Installation des dependances..." -ForegroundColor Gray
.\venv\Scripts\Activate.ps1
pip install -q --upgrade pip
pip install -q -r requirements.txt

if (-not (Test-Path ".env")) {
    Write-Host "   Creation du fichier de configuration..." -ForegroundColor Gray
    Copy-Item .env.example .env
}

Write-Host "   [OK] MCP Slave Windows configure" -ForegroundColor Green
deactivate
Set-Location ..\..

# 5. Vérifier la politique d'exécution
Write-Host ""
Write-Host "[5/5] Verification de la politique d'execution PowerShell..." -ForegroundColor Yellow
$policy = Get-ExecutionPolicy -Scope CurrentUser
if ($policy -eq "Restricted" -or $policy -eq "Undefined") {
    Write-Host "   [WARN] Politique d'execution restrictive detectee: $policy" -ForegroundColor Yellow
    $changePol = Read-Host "Autoriser l'exécution de scripts? (y/N)"
    if ($changePol -eq "y") {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "   [OK] Politique mise a jour" -ForegroundColor Green
    }
} else {
    Write-Host "   [OK] Politique d'execution OK: $policy" -ForegroundColor Green
}

# Résumé
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "[OK] Installation terminee!" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaines etapes:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Démarrer la plateforme:" -ForegroundColor White
Write-Host "   .\scripts\start-all.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Ou démarrer manuellement:" -ForegroundColor White
Write-Host "   Terminal 1: cd brain; .\venv\Scripts\Activate.ps1; python main.py" -ForegroundColor Gray
Write-Host "   Terminal 2: cd slaves\windows; .\venv\Scripts\Activate.ps1; python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Tester la plateforme:" -ForegroundColor White
Write-Host "   .\scripts\test-platform.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "   - INSTALLATION_WINDOWS.md (guide complet)" -ForegroundColor Gray
Write-Host "   - docs/USAGE.md (exemples d'utilisation)" -ForegroundColor Gray
Write-Host "   - docs/API.md (documentation API)" -ForegroundColor Gray
Write-Host ""
