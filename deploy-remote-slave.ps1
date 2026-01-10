# Script d'installation du Slave Windows distant
# A executer sur le serveur distant Windows 10

param(
    [string]$BrainUrl = "http://VOTRE_IP_BRAIN:8000",
    [string]$SlaveId = "windows-remote-01",
    [string]$SlavePort = "8003"
)

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "Installation MCP Slave Windows - Serveur distant" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verifier Python
Write-Host "[1/6] Verification de Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERREUR] Python n'est pas installe!" -ForegroundColor Red
    Write-Host "Telechargez Python depuis: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "Python trouve: $pythonVersion" -ForegroundColor Green

# 2. Creer le dossier de travail
Write-Host ""
Write-Host "[2/6] Creation du dossier de travail..." -ForegroundColor Yellow
$workDir = "C:\MCP-Slave"
if (-not (Test-Path $workDir)) {
    New-Item -ItemType Directory -Path $workDir | Out-Null
}
Set-Location $workDir
Write-Host "Dossier de travail: $workDir" -ForegroundColor Green

# 3. Telecharger les fichiers depuis le serveur HTTP
Write-Host ""
Write-Host "[3/6] Telechargement des fichiers..." -ForegroundColor Yellow
Write-Host "Entrez l'URL du serveur HTTP (ex: http://192.168.1.100:8080):" -ForegroundColor Yellow
$httpServer = Read-Host

try {
    Invoke-WebRequest -Uri "$httpServer/slave-windows.zip" -OutFile "slave-windows.zip"
    Expand-Archive -Path "slave-windows.zip" -DestinationPath "." -Force
    Remove-Item "slave-windows.zip"
    Write-Host "Fichiers telecharges avec succes" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Impossible de telecharger les fichiers: $_" -ForegroundColor Red
    exit 1
}

# 4. Creer l'environnement virtuel
Write-Host ""
Write-Host "[4/6] Creation de l'environnement virtuel..." -ForegroundColor Yellow
python -m venv venv
Write-Host "Environnement virtuel cree" -ForegroundColor Green

# 5. Installer les dependances
Write-Host ""
Write-Host "[5/6] Installation des dependances..." -ForegroundColor Yellow
.\venv\Scripts\pip.exe install -r requirements.txt
Write-Host "Dependances installees" -ForegroundColor Green

# 6. Creer le fichier de configuration
Write-Host ""
Write-Host "[6/6] Configuration du Slave..." -ForegroundColor Yellow

$configContent = @"
# Configuration du Slave Windows distant
SLAVE_ID=$SlaveId
SLAVE_PORT=$SlavePort
BRAIN_URL=$BrainUrl
"@

$configContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "Configuration creee" -ForegroundColor Green

# Creer le script de demarrage
$startScript = @"
# Demarrage du Slave Windows
`$env:SLAVE_ID = "$SlaveId"
`$env:SLAVE_PORT = "$SlavePort"
`$env:BRAIN_URL = "$BrainUrl"

Write-Host "Demarrage du Slave Windows: $SlaveId" -ForegroundColor Cyan
Write-Host "Port: $SlavePort" -ForegroundColor Yellow
Write-Host "Brain: $BrainUrl" -ForegroundColor Yellow
Write-Host ""

.\venv\Scripts\python.exe start.py
"@

$startScript | Out-File -FilePath "start-slave.ps1" -Encoding UTF8

Write-Host ""
Write-Host "==============================================================" -ForegroundColor Green
Write-Host "Installation terminee!" -ForegroundColor Green
Write-Host "==============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pour demarrer le Slave:" -ForegroundColor Yellow
Write-Host "  cd $workDir" -ForegroundColor White
Write-Host "  .\start-slave.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Le Slave sera accessible sur: http://localhost:$SlavePort" -ForegroundColor Yellow
Write-Host ""
