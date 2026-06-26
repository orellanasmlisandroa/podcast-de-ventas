# Lanzador rápido de la Fábrica de Podcasts (Windows / PowerShell)
# Uso:  .\run.ps1            -> build + abre dashboard
#       .\run.ps1 watch      -> vigila la carpeta de audio
#       .\run.ps1 status     -> estado en la terminal
param([string]$cmd = "build")

Set-Location $PSScriptRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Host "Python no está en el PATH. Instálalo desde https://python.org" -ForegroundColor Red
  exit 1
}

python -m pip install -q -r requirements.txt

if ($cmd -eq "build") {
  python -m factory build
  python -m factory dashboard
} else {
  python -m factory $cmd
}
