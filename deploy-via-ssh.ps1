# Script pour deployer le Slave Windows via SSH
# A executer sur ta machine locale

param(
    [Parameter(Mandatory=$true)]
    [string]$RemoteHost,
    
    [Parameter(Mandatory=$true)]
    [string]$RemoteUser,
    
    [string]$BrainUrl = "",
    [string]$SlaveId = "windows-remote-01",
    [string]$SlavePort = "8003"
)

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "Deploiement du Slave Windows via SSH" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""

# Obtenir l'IP locale pour le Brain
if ([string]::IsNullOrEmpty($BrainUrl)) {
    $localIp = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -First 1).IPAddress
    $BrainUrl = "http://${localIp}:8000"
}

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Serveur distant: $RemoteUser@$RemoteHost" -ForegroundColor White
Write-Host "  Brain URL: $BrainUrl" -ForegroundColor White
Write-Host "  Slave ID: $SlaveId" -ForegroundColor White
Write-Host "  Slave Port: $SlavePort" -ForegroundColor White
Write-Host ""

# Verifier que le package existe
if (-not (Test-Path ".\slave-windows.zip")) {
    Write-Host "[ERREUR] Le fichier slave-windows.zip n'existe pas!" -ForegroundColor Red
    Write-Host "Executez d'abord: .\package-slave.ps1" -ForegroundColor Yellow
    exit 1
}

# 1. Copier le package sur le serveur distant
Write-Host "[1/5] Copie du package sur le serveur distant..." -ForegroundColor Yellow
scp .\slave-windows.zip "${RemoteUser}@${RemoteHost}:C:/Users/$RemoteUser/slave-windows.zip"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERREUR] Impossible de copier le fichier" -ForegroundColor Red
    exit 1
}
Write-Host "Package copie avec succes" -ForegroundColor Green

# 2. Extraire l'archive sur le serveur distant
Write-Host ""
Write-Host "[2/5] Extraction de l'archive..." -ForegroundColor Yellow
ssh "${RemoteUser}@${RemoteHost}" "powershell -Command `"Expand-Archive -Path C:/Users/$RemoteUser/slave-windows.zip -DestinationPath C:/MCP-Slave -Force`""
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERREUR] Impossible d'extraire l'archive" -ForegroundColor Red
    exit 1
}
Write-Host "Archive extraite" -ForegroundColor Green

# 3. Creer le fichier de configuration
Write-Host ""
Write-Host "[3/5] Creation de la configuration..." -ForegroundColor Yellow
$configContent = @"
SLAVE_ID=$SlaveId
SLAVE_PORT=$SlavePort
BRAIN_URL=$BrainUrl
"@

# Ecrire la config dans un fichier temporaire
$configContent | Out-File -FilePath ".\temp-config.env" -Encoding UTF8

# Copier la config sur le serveur distant
scp .\temp-config.env "${RemoteUser}@${RemoteHost}:C:/MCP-Slave/.env"
Remove-Item ".\temp-config.env"
Write-Host "Configuration creee" -ForegroundColor Green

# 4. Installer les dependances
Write-Host ""
Write-Host "[4/5] Installation des dependances (cela peut prendre quelques minutes)..." -ForegroundColor Yellow
ssh "${RemoteUser}@${RemoteHost}" "cd C:/MCP-Slave; python -m venv venv; .\venv\Scripts\pip.exe install -r requirements.txt"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ATTENTION] Probleme lors de l'installation des dependances" -ForegroundColor Yellow
    Write-Host "Vous devrez peut-etre installer manuellement" -ForegroundColor Yellow
} else {
    Write-Host "Dependances installees" -ForegroundColor Green
}

# 5. Creer le script de demarrage
Write-Host ""
Write-Host "[5/5] Creation du script de demarrage..." -ForegroundColor Yellow
$startScript = @"
`$env:SLAVE_ID = '$SlaveId'
`$env:SLAVE_PORT = '$SlavePort'
`$env:BRAIN_URL = '$BrainUrl'

Write-Host 'Demarrage du Slave Windows: $SlaveId' -ForegroundColor Cyan
Write-Host 'Port: $SlavePort' -ForegroundColor Yellow
Write-Host 'Brain: $BrainUrl' -ForegroundColor Yellow
Write-Host ''

.\venv\Scripts\python.exe start.py
"@

$startScript | Out-File -FilePath ".\temp-start.ps1" -Encoding UTF8
scp .\temp-start.ps1 "${RemoteUser}@${RemoteHost}:C:/MCP-Slave/start-slave.ps1"
Remove-Item ".\temp-start.ps1"
Write-Host "Script de demarrage cree" -ForegroundColor Green

Write-Host ""
Write-Host "==============================================================" -ForegroundColor Green
Write-Host "Deploiement termine!" -ForegroundColor Green
Write-Host "==============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pour demarrer le Slave sur le serveur distant:" -ForegroundColor Cyan
Write-Host "  ssh $RemoteUser@$RemoteHost" -ForegroundColor White
Write-Host "  cd C:/MCP-Slave" -ForegroundColor White
Write-Host "  .\start-slave.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Ou en une seule commande:" -ForegroundColor Cyan
Write-Host "  ssh $RemoteUser@$RemoteHost 'cd C:/MCP-Slave; .\start-slave.ps1'" -ForegroundColor White
Write-Host ""
Write-Host "Le Slave sera accessible sur: http://${RemoteHost}:${SlavePort}" -ForegroundColor Yellow
Write-Host ""
