# Quote Board - remove everything from this computer (Windows PowerShell)
# Usage:  powershell -ExecutionPolicy Bypass -File .\stop.ps1
docker stack rm quotes
Start-Sleep -Seconds 10
docker volume rm quotes_redis-data 2>$null
docker image rm quoteboard-web:1.0 2>$null
docker swarm leave --force
Write-Host "Cleaned up. The computer is back to how it was." -ForegroundColor Green
