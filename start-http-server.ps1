# Demarrer un serveur HTTP pour partager les fichiers

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "Serveur HTTP pour deploiement distant" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""

# Obtenir l'adresse IP locale
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -First 1).IPAddress

Write-Host "Adresse IP locale: $ipAddress" -ForegroundColor Green
Write-Host ""
Write-Host "Le serveur HTTP sera accessible sur:" -ForegroundColor Yellow
Write-Host "  http://${ipAddress}:8080" -ForegroundColor White
Write-Host ""
Write-Host "Fichiers disponibles:" -ForegroundColor Yellow
if (Test-Path ".\slave-windows.zip") {
    Write-Host "  - slave-windows.zip" -ForegroundColor Green
} else {
    Write-Host "  [ATTENTION] slave-windows.zip n'existe pas!" -ForegroundColor Red
    Write-Host "  Executez d'abord: .\package-slave.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
Write-Host ""
Write-Host "Commande pour le serveur distant:" -ForegroundColor Cyan
Write-Host "  Invoke-WebRequest -Uri 'http://${ipAddress}:8080/slave-windows.zip' -OutFile 'slave.zip'" -ForegroundColor White
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arreter le serveur" -ForegroundColor Gray
Write-Host ""
Write-Host "Demarrage du serveur HTTP sur le port 8080..." -ForegroundColor Yellow
Write-Host ""

# Demarrer le serveur HTTP Python
python -m http.server 8080
