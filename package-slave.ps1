# Script pour packager le Slave Windows pour deploiement distant
# A executer sur ta machine locale

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "Packaging du Slave Windows pour deploiement distant" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""

$packageDir = ".\slave-package"
$slaveDir = ".\slaves\windows"

# 1. Creer le dossier de package
Write-Host "[1/4] Creation du dossier de package..." -ForegroundColor Yellow
if (Test-Path $packageDir) {
    Remove-Item -Recurse -Force $packageDir
}
New-Item -ItemType Directory -Path $packageDir | Out-Null
Write-Host "Dossier cree: $packageDir" -ForegroundColor Green

# 2. Copier les fichiers necessaires
Write-Host ""
Write-Host "[2/4] Copie des fichiers du Slave..." -ForegroundColor Yellow

# Creer la structure slaves/windows
New-Item -ItemType Directory -Path "$packageDir\slaves\windows\tools" -Force | Out-Null

# Copier tout le contenu du Slave Windows
Copy-Item -Path "$slaveDir\*.py" -Destination "$packageDir\slaves\windows\" -Recurse
Copy-Item -Path "$slaveDir\tools\*.py" -Destination "$packageDir\slaves\windows\tools\" -Recurse
Copy-Item -Path "$slaveDir\requirements.txt" -Destination $packageDir

# Creer les fichiers __init__.py
"" | Out-File -FilePath "$packageDir\slaves\__init__.py" -Encoding UTF8
"" | Out-File -FilePath "$packageDir\slaves\windows\__init__.py" -Encoding UTF8
"" | Out-File -FilePath "$packageDir\slaves\windows\tools\__init__.py" -Encoding UTF8

# Creer un start.py adapte pour le deploiement distant
$startPyContent = @'
import sys
from pathlib import Path
import os

# Ajouter le dossier courant au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from slaves.windows.main import app
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("SLAVE_PORT", "8003"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
'@

$startPyContent | Out-File -FilePath "$packageDir\start.py" -Encoding UTF8

# Copier les modules shared
if (Test-Path ".\shared") {
    New-Item -ItemType Directory -Path "$packageDir\shared" -Force | Out-Null
    Copy-Item -Path ".\shared\*" -Destination "$packageDir\shared\" -Recurse -Force
}

Write-Host "Fichiers copies avec structure complete" -ForegroundColor Green

# 3. Copier le script d'installation
Write-Host ""
Write-Host "[3/4] Ajout du script d'installation..." -ForegroundColor Yellow
Copy-Item -Path ".\deploy-remote-slave.ps1" -Destination "$packageDir\install.ps1"
Write-Host "Script d'installation ajoute" -ForegroundColor Green

# 4. Creer l'archive ZIP
Write-Host ""
Write-Host "[4/4] Creation de l'archive..." -ForegroundColor Yellow
$zipPath = ".\slave-windows.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath
}
Compress-Archive -Path "$packageDir\*" -DestinationPath $zipPath
Write-Host "Archive creee: $zipPath" -ForegroundColor Green

# Nettoyer
Remove-Item -Recurse -Force $packageDir

Write-Host ""
Write-Host "==============================================================" -ForegroundColor Green
Write-Host "Package pret!" -ForegroundColor Green
Write-Host "==============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Fichier cree: slave-windows.zip" -ForegroundColor Yellow
Write-Host ""
Write-Host "Prochaines etapes:" -ForegroundColor Cyan
Write-Host "1. Demarrer le serveur HTTP:" -ForegroundColor White
Write-Host "   python -m http.server 8080" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Sur le serveur distant, telecharger et executer:" -ForegroundColor White
Write-Host "   Invoke-WebRequest -Uri 'http://VOTRE_IP:8080/slave-windows.zip' -OutFile 'slave.zip'" -ForegroundColor Gray
Write-Host "   Expand-Archive -Path 'slave.zip' -DestinationPath 'C:\MCP-Slave'" -ForegroundColor Gray
Write-Host "   cd C:\MCP-Slave" -ForegroundColor Gray
Write-Host "   .\install.ps1" -ForegroundColor Gray
Write-Host ""
