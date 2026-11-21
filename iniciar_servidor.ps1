# Script para iniciar o servidor Flask no Windows PowerShell
# Execute: powershell -ExecutionPolicy Bypass -File iniciar_servidor.ps1

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Painel Operacional - Loja (Flask + SQLite)        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar se loja.db existe
$dbPath = Join-Path (Get-Location) "loja.db"
if (-not (Test-Path $dbPath)) {
	Write-Host "⚠️  Banco de dados não encontrado!" -ForegroundColor Yellow
	Write-Host "Executando setup_db.py para criar/popular o banco..." -ForegroundColor Yellow
	Write-Host ""
	& '.\env\Scripts\python.exe' 'setup_db.py'
	Write-Host ""
}

# Verificar se dependências estão instaladas
Write-Host "✓ Verificando dependências..." -ForegroundColor Green
& '.\env\Scripts\python.exe' -c "import flask, sqlalchemy, pandas; print('✓ Todas as dependências estão instaladas')" 2>$null
if ($LASTEXITCODE -ne 0) {
	Write-Host "⚠️  Instalando dependências..." -ForegroundColor Yellow
	& '.\env\Scripts\pip.exe' install -r requirements.txt
}

Write-Host ""
Write-Host "✓ Iniciando servidor Flask..." -ForegroundColor Green
Write-Host "  🌐 Acesse em: http://127.0.0.1:5050" -ForegroundColor Cyan
Write-Host "  ⏹️  Pressione CTRL+C para parar o servidor" -ForegroundColor Yellow
Write-Host ""

& '.\env\Scripts\python.exe' app.py
