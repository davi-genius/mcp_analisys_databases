#!/usr/bin/env pwsh
# Compass MCP Agent - Setup
# Este script configura o comando 'mcp' no seu PowerShell

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  Compass MCP Agent - Configuracao" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Criar o comando mcp
$mcpCommand = @'

# Compass MCP Agent
function mcp { 
    docker exec -it postgres-analyzer python /app/mcp-prompt.py 
}

'@

# Verificar se o profile existe
if (!(Test-Path $PROFILE)) {
    New-Item -Path $PROFILE -ItemType File -Force | Out-Null
    Write-Host "✅ Profile do PowerShell criado" -ForegroundColor Green
}

# Verificar se o comando já existe
$profileContent = Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue

if ($profileContent -notmatch "function mcp") {
    Add-Content -Path $PROFILE -Value $mcpCommand
    Write-Host "✅ Comando 'mcp' adicionado ao PowerShell!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Para usar agora, execute:" -ForegroundColor Yellow
    Write-Host "  . `$PROFILE" -ForegroundColor White
    Write-Host ""
    Write-Host "Ou feche e abra um novo terminal." -ForegroundColor Yellow
} else {
    Write-Host "✅ Comando 'mcp' já está configurado!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Agora você pode digitar:" -ForegroundColor Cyan
Write-Host "  mcp" -ForegroundColor White
Write-Host ""
Write-Host "Para acessar o Compass MCP Agent!" -ForegroundColor Cyan
Write-Host ""
