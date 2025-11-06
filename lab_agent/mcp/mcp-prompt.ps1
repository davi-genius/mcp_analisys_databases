# MCP Interactive Prompt - PowerShell Version
# PostgreSQL Performance Analyzer - Compass UOL Edition

$MCP_URL = "http://localhost:8000"
$DB_CONFIG = @{
    host = "localhost"
    port = 5432
    dbname = "petclinic"
    username = "petclinic"
    password = "petclinic"
}

function Show-Logo {
    Write-Host ""
    Write-Host "    ╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "    ║                                                                ║" -ForegroundColor Yellow
    Write-Host "    ║   " -NoNewline -ForegroundColor Yellow
    Write-Host "  ██████╗ ██████╗ ███╗   ███╗██████╗  █████╗ ███████╗███████╗" -NoNewline -ForegroundColor DarkYellow
    Write-Host "  ║" -ForegroundColor Yellow
    Write-Host "    ║   " -NoNewline -ForegroundColor Yellow
    Write-Host " ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔══██╗██╔════╝██╔════╝" -NoNewline -ForegroundColor DarkYellow
    Write-Host "  ║" -ForegroundColor Yellow
    Write-Host "    ║   " -NoNewline -ForegroundColor Yellow
    Write-Host " ██║     ██║   ██║██╔████╔██║██████╔╝███████║███████╗███████╗" -NoNewline -ForegroundColor DarkYellow
    Write-Host "  ║" -ForegroundColor Yellow
    Write-Host "    ║   " -NoNewline -ForegroundColor Yellow
    Write-Host " ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██╔══██║╚════██║╚════██║" -NoNewline -ForegroundColor DarkYellow
    Write-Host "  ║" -ForegroundColor Yellow
    Write-Host "    ║   " -NoNewline -ForegroundColor Yellow
    Write-Host " ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ██║  ██║███████║███████║" -NoNewline -ForegroundColor DarkYellow
    Write-Host "  ║" -ForegroundColor Yellow
    Write-Host "    ║   " -NoNewline -ForegroundColor Yellow
    Write-Host "  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝" -NoNewline -ForegroundColor DarkYellow
    Write-Host "  ║" -ForegroundColor Yellow
    Write-Host "    ║                                                                ║" -ForegroundColor Yellow
    Write-Host "    ║           " -NoNewline -ForegroundColor Yellow
    Write-Host "PostgreSQL Performance Analyzer Agent" -NoNewline -ForegroundColor White
    Write-Host "              ║" -ForegroundColor Yellow
    Write-Host "    ║                      " -NoNewline -ForegroundColor Yellow
    Write-Host "Compass UOL" -NoNewline -ForegroundColor Cyan
    Write-Host "                            ║" -ForegroundColor Yellow
    Write-Host "    ║                                                                ║" -ForegroundColor Yellow
    Write-Host "    ╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    Versao: 1.0.0 | Data: " -NoNewline -ForegroundColor Gray
    Write-Host (Get-Date -Format "dd/MM/yyyy HH:mm") -ForegroundColor Gray
    Write-Host ""
}

function Show-Header {
    param($Title)
    Write-Host ""
    Write-Host ("="*70)
    Write-Host "  $Title"
    Write-Host ("="*70)
    Write-Host ""
}

function Test-McpStatus {
    try {
        $response = Invoke-RestMethod -Uri "$MCP_URL/health" -TimeoutSec 2 -ErrorAction Stop
        return @{Healthy=$true; Status="Healthy"}
    }
    catch {
        return @{Healthy=$false; Status="Offline"}
    }
}

function Show-Databases {
    Show-Header "BANCOS DE DADOS DISPONIVEIS"
    
    try {
        $result = docker exec postgres-analyzer python -c @"
import sys
sys.path.append('/app/src')
from tools.mcp_tools import get_database_connector
conn = get_database_connector(host='postgres', port=5432, dbname='postgres', username='petclinic', password='petclinic')
if conn and conn.connect():
    result = conn.execute_query('SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname')
    for i, row in enumerate(result, 1):
        print(f'{i}. {row[\"datname\"]}')
    conn.disconnect()
"@
        Write-Host $result
    }
    catch {
        Write-Host "Erro ao listar bancos de dados"
    }
}

function Show-Tables {
    param($DbName = $DB_CONFIG.dbname)
    
    Show-Header "TABELAS DO BANCO: $DbName"
    
    try {
        $result = docker exec postgres-analyzer python -c @"
import sys
sys.path.append('/app/src')
from tools.mcp_tools import get_database_connector
conn = get_database_connector(host='postgres', port=5432, dbname='$DbName', username='petclinic', password='petclinic')
if conn and conn.connect():
    query = '''
        SELECT 
            table_name,
            (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
        FROM information_schema.tables t
        WHERE table_schema = 'public'
        ORDER BY table_name
    '''
    result = conn.execute_query(query)
    for i, row in enumerate(result, 1):
        print(f'{i}. {row[\"table_name\"]} ({row[\"column_count\"]} colunas)')
    conn.disconnect()
"@
        Write-Host $result
    }
    catch {
        Write-Host "Erro ao listar tabelas"
    }
}

function Show-TableDetails {
    param($TableName, $DbName = $DB_CONFIG.dbname)
    
    Show-Header "DETALHES DA TABELA: $TableName"
    
    try {
        $result = docker exec postgres-analyzer python -c @"
import sys
sys.path.append('/app/src')
from tools.mcp_tools import get_database_connector
conn = get_database_connector(host='postgres', port=5432, dbname='$DbName', username='petclinic', password='petclinic')
if conn and conn.connect():
    query = '''
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = '$TableName'
        ORDER BY ordinal_position
    '''
    result = conn.execute_query(query)
    print('\nCOLUNAS:')
    print('-' * 70)
    for row in result:
        nullable = 'NULL' if row['is_nullable'] == 'YES' else 'NOT NULL'
        type_info = row['data_type']
        if row['character_maximum_length']:
            type_info += f'({row[\"character_maximum_length\"]})'
        default = f' DEFAULT {row[\"column_default\"]}' if row['column_default'] else ''
        print(f'  - {row[\"column_name\"]}: {type_info} {nullable}{default}')
    
    count_query = f'SELECT COUNT(*) as total FROM $TableName'
    count_result = conn.execute_query(count_query)
    print(f'\nTOTAL DE REGISTROS: {count_result[0][\"total\"]}')
    
    conn.disconnect()
"@
        Write-Host $result
    }
    catch {
        Write-Host "Erro ao buscar detalhes da tabela"
    }
}

function Show-DbActions {
    Show-Header "ACOES DE BANCO DE DADOS"
    
    Write-Host "Escolha uma opcao:"
    Write-Host ""
    Write-Host "  1 - Listar todos os bancos de dados"
    Write-Host "  2 - Listar tabelas do banco atual"
    Write-Host "  3 - Ver detalhes de uma tabela"
    Write-Host "  4 - Executar prompts prontos"
    Write-Host "  0 - Voltar"
    Write-Host ""
    
    $choice = Read-Host "Digite o numero da opcao"
    
    switch ($choice) {
        '1' { Show-Databases }
        '2' { Show-Tables }
        '3' {
            $tableName = Read-Host "Digite o nome da tabela"
            if ($tableName) {
                Show-TableDetails $tableName
            }
        }
        '4' { Show-PromptsMenu }
    }
}

function Show-PromptsMenu {
    try {
        $response = Invoke-RestMethod -Uri "$MCP_URL/prompts"
        Write-Host ""
        Write-Host $response
        Write-Host ""
        
        $promptId = Read-Host "Digite o numero do prompt para executar (0 para voltar)"
        if ($promptId -and $promptId -ne '0') {
            Invoke-Prompt $promptId
        }
    }
    catch {
        Write-Host "Erro ao carregar prompts"
    }
}

function Invoke-Prompt {
    param($PromptId)
    
    try {
        $result = docker exec postgres-analyzer python src/execute_prompt.py $PromptId
        Write-Host $result
    }
    catch {
        Write-Host "Erro ao executar prompt: $_"
    }
}

function Show-McpApp {
    Show-Header "INFORMACOES DA APLICACAO"
    
    Write-Host "Aplicacao: PostgreSQL Performance Analyzer"
    Write-Host "Versao: 1.0.0"
    Write-Host "Compass UOL Edition"
    Write-Host ""
    Write-Host "CONFIGURACAO DE BANCO:"
    Write-Host "  Host: $($DB_CONFIG.host)"
    Write-Host "  Porta: $($DB_CONFIG.port)"
    Write-Host "  Database: $($DB_CONFIG.dbname)"
    Write-Host "  Usuario: $($DB_CONFIG.username)"
    Write-Host ""
}

function Show-Help {
    Show-Header "COMANDOS DISPONIVEIS"
    
    Write-Host "COMANDOS MCP:"
    Write-Host "  mcp status     - Verifica status do servidor MCP"
    Write-Host "  mcp list       - Lista todos os bancos de dados"
    Write-Host "  mcp tables     - Lista tabelas do banco atual"
    Write-Host "  mcp actions    - Menu interativo de acoes"
    Write-Host "  mcp app        - Informacoes da aplicacao"
    Write-Host "  mcp prompts    - Lista e executa prompts prontos"
    Write-Host "  mcp quit       - Sai do prompt"
    Write-Host ""
    Write-Host "OUTROS COMANDOS:"
    Write-Host "  help / h       - Mostra esta ajuda"
    Write-Host "  clear / cls    - Limpa a tela"
    Write-Host ""
}

function Start-McpPrompt {
    Clear-Host
    Show-Logo
    
    # Verificar status inicial
    $status = Test-McpStatus
    if ($status.Healthy) {
        Write-Host "    Status MCP: " -NoNewline
        Write-Host $status.Status -ForegroundColor Green
    }
    else {
        Write-Host "    Status MCP: " -NoNewline
        Write-Host $status.Status -ForegroundColor Red
        Write-Host ""
        Write-Host "    ATENCAO: MCP nao esta acessivel. Inicie com 'docker compose up -d'"
    }
    
    Write-Host ""
    Write-Host "    Digite 'help' para ver comandos disponiveis"
    Write-Host ""
    
    while ($true) {
        Write-Host "compass> " -NoNewline -ForegroundColor Yellow
        $command = Read-Host
        $command = $command.Trim().ToLower()
        
        if (-not $command) { continue }
        
        switch ($command) {
            {$_ -in 'quit','exit','q','mcp quit'} {
                Write-Host "`nEncerrando MCP Agent. Ate logo!"
                return
            }
            
            {$_ -in 'help','h','?'} {
                Show-Help
            }
            
            {$_ -in 'clear','cls'} {
                Clear-Host
                Show-Logo
            }
            
            'mcp status' {
                $status = Test-McpStatus
                Write-Host "`nStatus MCP: $($status.Status)"
                if ($status.Healthy) {
                    Write-Host "Endpoint: $MCP_URL"
                    Write-Host "Estado: Operacional`n"
                }
                else {
                    Write-Host "Estado: Indisponivel`n"
                }
            }
            
            'mcp list' {
                Show-Databases
            }
            
            'mcp tables' {
                Show-Tables
            }
            
            'mcp actions' {
                Show-DbActions
            }
            
            'mcp app' {
                Show-McpApp
            }
            
            'mcp prompts' {
                Show-PromptsMenu
            }
            
            default {
                Write-Host "Comando desconhecido: '$command'"
                Write-Host "Digite 'help' para ver comandos disponiveis`n"
            }
        }
    }
}

# Iniciar prompt
Start-McpPrompt