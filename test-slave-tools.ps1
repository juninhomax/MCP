Write-Host "[TEST] Test manuel des outils Windows Slave" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

$slaveUrl = "http://localhost:8002"

# Test 1: powershell_exec - Lister les processus
Write-Host "[1/5] Test powershell_exec - Top 5 processus memoire" -ForegroundColor Yellow
$request1 = @{
    jsonrpc = "2.0"
    id = 1
    method = "execute_tool"
    params = @{
        tool_name = "powershell_exec"
        parameters = @{
            command = "Get-Process | Sort-Object -Property WS -Descending | Select-Object -First 5 Name, @{Name='Memory(MB)';Expression={[math]::Round(`$_.WS/1MB,2)}} | Format-Table -AutoSize"
        }
    }
} | ConvertTo-Json -Depth 10

$response1 = Invoke-RestMethod -Uri "$slaveUrl/jsonrpc" -Method Post -Body $request1 -ContentType "application/json"
Write-Host "Resultat:" -ForegroundColor White
if ($response1.result.success) {
    Write-Host $response1.result.output -ForegroundColor Green
} else {
    Write-Host "Erreur: $($response1.result.error)" -ForegroundColor Red
}

# Test 2: get_process - Informations sur un processus specifique
Write-Host ""
Write-Host "[2/5] Test get_process - Processus 'explorer'" -ForegroundColor Yellow
$request2 = @{
    jsonrpc = "2.0"
    id = 2
    method = "execute_tool"
    params = @{
        tool_name = "get_process"
        parameters = @{
            process_name = "explorer"
        }
    }
} | ConvertTo-Json -Depth 10

$response2 = Invoke-RestMethod -Uri "$slaveUrl/jsonrpc" -Method Post -Body $request2 -ContentType "application/json"
Write-Host "Resultat:" -ForegroundColor White
if ($response2.result.success) {
    Write-Host $response2.result.output -ForegroundColor Green
} else {
    Write-Host "Erreur: $($response2.result.error)" -ForegroundColor Red
}

# Test 3: get_service - Statut d'un service Windows
Write-Host ""
Write-Host "[3/5] Test get_service - Service 'wuauserv' (Windows Update)" -ForegroundColor Yellow
$request3 = @{
    jsonrpc = "2.0"
    id = 3
    method = "execute_tool"
    params = @{
        tool_name = "get_service"
        parameters = @{
            service_name = "wuauserv"
        }
    }
} | ConvertTo-Json -Depth 10

$response3 = Invoke-RestMethod -Uri "$slaveUrl/jsonrpc" -Method Post -Body $request3 -ContentType "application/json"
Write-Host "Resultat:" -ForegroundColor White
if ($response3.result.success) {
    Write-Host $response3.result.output -ForegroundColor Green
} else {
    Write-Host "Erreur: $($response3.result.error)" -ForegroundColor Red
}

# Test 4: file_read - Lire le fichier hosts
Write-Host ""
Write-Host "[4/5] Test file_read - Fichier hosts (10 premieres lignes)" -ForegroundColor Yellow
$request4 = @{
    jsonrpc = "2.0"
    id = 4
    method = "execute_tool"
    params = @{
        tool_name = "file_read"
        parameters = @{
            path = "C:\Windows\System32\drivers\etc\hosts"
            max_lines = 10
        }
    }
} | ConvertTo-Json -Depth 10

$response4 = Invoke-RestMethod -Uri "$slaveUrl/jsonrpc" -Method Post -Body $request4 -ContentType "application/json"
Write-Host "Resultat:" -ForegroundColor White
if ($response4.result.success) {
    Write-Host $response4.result.output -ForegroundColor Green
} else {
    Write-Host "Erreur: $($response4.result.error)" -ForegroundColor Red
}

# Test 5: test_path - Verifier l'existence d'un chemin
Write-Host ""
Write-Host "[5/5] Test test_path - Verification C:\Windows" -ForegroundColor Yellow
$request5 = @{
    jsonrpc = "2.0"
    id = 5
    method = "execute_tool"
    params = @{
        tool_name = "test_path"
        parameters = @{
            path = "C:\Windows"
        }
    }
} | ConvertTo-Json -Depth 10

$response5 = Invoke-RestMethod -Uri "$slaveUrl/jsonrpc" -Method Post -Body $request5 -ContentType "application/json"
Write-Host "Resultat:" -ForegroundColor White
if ($response5.result.success) {
    Write-Host $response5.result.output -ForegroundColor Green
} else {
    Write-Host "Erreur: $($response5.result.error)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "[OK] Tests termines!" -ForegroundColor Green
Write-Host ""
