# Créer le script d'installation simplifié
$scriptContent = @'
param(
    [string]$BrainIp = "192.168.0.10",
    [string]$SlaveId = "windows-remote-01",
    [string]$SlavePort = "8003"
)

$BrainUrl = "http://${BrainIp}:8000"

Write-Host "Configuration du Slave..." -ForegroundColor Cyan
Write-Host "Brain: $BrainUrl" -ForegroundColor Yellow
Write-Host ""

# Créer l'environnement virtuel
Write-Host "[1/3] Creation de l'environnement virtuel..." -ForegroundColor Yellow
python -m venv venv
Write-Host "OK" -ForegroundColor Green

# Installer les dépendances
Write-Host "[2/3] Installation des dependances..." -ForegroundColor Yellow
.\venv\Scripts\pip.exe install -r requirements.txt --quiet
Write-Host "OK" -ForegroundColor Green

# Créer la configuration
Write-Host "[3/3] Configuration..." -ForegroundColor Yellow
@"
SLAVE_ID=$SlaveId
SLAVE_PORT=$SlavePort
BRAIN_URL=$BrainUrl
"@ | Out-File -FilePath ".env" -Encoding UTF8

# Créer le script de démarrage
@"
`$env:SLAVE_ID = '$SlaveId'
`$env:SLAVE_PORT = '$SlavePort'
`$env:BRAIN_URL = '$BrainUrl'
Write-Host 'Demarrage du Slave: $SlaveId sur port $SlavePort' -ForegroundColor Cyan
.\venv\Scripts\python.exe start.py
"@ | Out-File -FilePath "start-slave.ps1" -Encoding UTF8

Write-Host "OK" -ForegroundColor Green
Write-Host ""
Write-Host "Installation terminee!" -ForegroundColor Green
Write-Host "Pour demarrer: .\start-slave.ps1" -ForegroundColor Yellow
'@

$scriptContent | Out-File -FilePath "quick-install.ps1" -Encoding UTF8

# Lancer l'installation
.\quick-install.ps1 -BrainIp "192.168.0.10"