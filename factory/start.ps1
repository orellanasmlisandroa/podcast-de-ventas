# Lanzador rápido de la App Web de la Fábrica de Podcasts (Windows / PowerShell)
# Uso:  .\start.ps1

Set-Location $PSScriptRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Host "Python no está en el PATH. Instálalo desde https://python.org" -ForegroundColor Red
  exit 1
}

Write-Host "Instalando y verificando dependencias en Python..." -ForegroundColor Cyan
python -m pip install -q -r requirements.txt

Write-Host "`n=======================================================" -ForegroundColor Cyan
Write-Host " Arrancando la aplicación web de CORTEXIA 777" -ForegroundColor Green
Write-Host " Accede en tu navegador a:" -ForegroundColor Cyan
Write-Host "    👉 http://localhost:8000" -ForegroundColor Yellow
Write-Host "=======================================================`n" -ForegroundColor Cyan

python -m uvicorn app:app --host 127.0.0.1 --port 8000
