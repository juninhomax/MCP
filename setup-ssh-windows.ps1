# Script pour installer et configurer OpenSSH Server sur Windows 10/11
# A executer sur le serveur distant Windows avec des droits administrateur

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "Installation et configuration OpenSSH Server - Windows" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""

# Verifier les droits administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERREUR] Ce script necessite des droits administrateur!" -ForegroundColor Red
    Write-Host "Relancez PowerShell en tant qu'administrateur" -ForegroundColor Yellow
    exit 1
}

# 1. Verifier si OpenSSH Server est deja installe
Write-Host "[1/6] Verification d'OpenSSH Server..." -ForegroundColor Yellow
$sshServer = Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'

if ($sshServer.State -eq "Installed") {
    Write-Host "OpenSSH Server est deja installe" -ForegroundColor Green
} else {
    Write-Host "Installation d'OpenSSH Server..." -ForegroundColor Yellow
    Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
    Write-Host "OpenSSH Server installe avec succes" -ForegroundColor Green
}

# 2. Demarrer le service SSH
Write-Host ""
Write-Host "[2/6] Demarrage du service SSH..." -ForegroundColor Yellow
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'
Write-Host "Service SSH demarre et configure en demarrage automatique" -ForegroundColor Green

# 3. Configurer le firewall
Write-Host ""
Write-Host "[3/6] Configuration du firewall..." -ForegroundColor Yellow
$firewallRule = Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue
if ($null -eq $firewallRule) {
    New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
    Write-Host "Regle de firewall creee" -ForegroundColor Green
} else {
    Write-Host "Regle de firewall deja existante" -ForegroundColor Green
}

# 4. Configurer PowerShell comme shell par defaut
Write-Host ""
Write-Host "[4/6] Configuration de PowerShell comme shell par defaut..." -ForegroundColor Yellow
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -PropertyType String -Force | Out-Null
Write-Host "PowerShell configure comme shell par defaut" -ForegroundColor Green

# 5. Afficher les informations de connexion
Write-Host ""
Write-Host "[5/6] Informations de connexion..." -ForegroundColor Yellow
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -First 1).IPAddress
$username = $env:USERNAME
$computerName = $env:COMPUTERNAME

Write-Host ""
Write-Host "Adresse IP: $ipAddress" -ForegroundColor Green
Write-Host "Nom d'utilisateur: $username" -ForegroundColor Green
Write-Host "Nom de l'ordinateur: $computerName" -ForegroundColor Green
Write-Host ""
Write-Host "Commande de connexion SSH:" -ForegroundColor Cyan
Write-Host "  ssh $username@$ipAddress" -ForegroundColor White
Write-Host ""

# 6. Tester le service
Write-Host "[6/6] Test du service SSH..." -ForegroundColor Yellow
$sshStatus = Get-Service sshd
if ($sshStatus.Status -eq "Running") {
    Write-Host "Service SSH fonctionne correctement" -ForegroundColor Green
} else {
    Write-Host "[ATTENTION] Le service SSH n'est pas en cours d'execution" -ForegroundColor Red
}

Write-Host ""
Write-Host "==============================================================" -ForegroundColor Green
Write-Host "Configuration terminee!" -ForegroundColor Green
Write-Host "==============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaines etapes:" -ForegroundColor Cyan
Write-Host "1. Depuis ta machine locale, teste la connexion:" -ForegroundColor White
Write-Host "   ssh $username@$ipAddress" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Pour deployer le Slave via SSH:" -ForegroundColor White
Write-Host "   scp slave-windows.zip ${username}@${ipAddress}:C:/Users/$username/" -ForegroundColor Gray
Write-Host "   ssh $username@$ipAddress" -ForegroundColor Gray
Write-Host "   cd C:/Users/$username" -ForegroundColor Gray
Write-Host "   Expand-Archive -Path slave-windows.zip -DestinationPath C:/MCP-Slave" -ForegroundColor Gray
Write-Host "   cd C:/MCP-Slave" -ForegroundColor Gray
Write-Host "   .\install.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "Note: Vous devrez entrer votre mot de passe Windows lors de la connexion SSH" -ForegroundColor Yellow
Write-Host ""
