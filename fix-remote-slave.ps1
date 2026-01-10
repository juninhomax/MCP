# Script pour corriger le start.py sur le serveur distant
# A copier-coller sur le serveur distant

Write-Host "Correction du start.py..." -ForegroundColor Cyan

$startPyContent = @'
import os
import uvicorn
from main import app

if __name__ == "__main__":
    port = int(os.getenv("SLAVE_PORT", "8003"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
'@

$startPyContent | Out-File -FilePath "start.py" -Encoding UTF8

Write-Host "start.py corrige!" -ForegroundColor Green
Write-Host ""
Write-Host "Maintenant, demarrez le Slave:" -ForegroundColor Yellow
Write-Host "  powershell -ExecutionPolicy Bypass -File .\start-slave.ps1" -ForegroundColor White
