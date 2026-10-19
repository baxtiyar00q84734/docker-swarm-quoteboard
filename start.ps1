# Quote Board - start everything (Windows PowerShell)
# Usage:  powershell -ExecutionPolicy Bypass -File .\start.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "1/4 Checking Docker..." -ForegroundColor Cyan
docker version --format "Docker {{.Server.Version}}"
if ($LASTEXITCODE -ne 0) { Write-Host "Docker is not running. Start Docker Desktop and try again." -ForegroundColor Red; exit 1 }

Write-Host "2/4 Enabling Swarm mode (if needed)..." -ForegroundColor Cyan
$state = docker info --format "{{.Swarm.LocalNodeState}}"
if ($state -ne "active") {
    docker swarm init 2>$null
    if ($LASTEXITCODE -ne 0) { docker swarm init --advertise-addr 127.0.0.1 }
}
docker node ls

Write-Host "3/4 Building the web image..." -ForegroundColor Cyan
docker build -t quoteboard-web:1.0 .\web
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "4/4 Deploying the stack..." -ForegroundColor Cyan
docker stack deploy -c docker-compose.yml quotes
Start-Sleep -Seconds 15
docker stack services quotes

Write-Host ""
Write-Host "App:        http://localhost:8000" -ForegroundColor Green
Write-Host "Visualizer: http://localhost:8080" -ForegroundColor Green
