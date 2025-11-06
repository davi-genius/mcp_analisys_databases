#!/usr/bin/env python3
"""
MCP Interactive Prompt - PostgreSQL Performance Analyzer
Compass UOL Edition
"""
import sys
import os
import requests
from datetime import datetime

# Configurações
MCP_URL = "http://localhost:8000"
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "petclinic",
    "username": "petclinic",
    "password": "petclinic"
}

# Logo ASCII da Compass
COMPASS_LOGO = """
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║     ██████╗ ██████╗ ███╗   ███╗██████╗  █████╗ ███████╗███████╗
    ║    ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔══██╗██╔════╝██╔════╝
    ║    ██║     ██║   ██║██╔████╔██║██████╔╝███████║███████╗███████╗
    ║    ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██╔══██║╚════██║╚════██║
    ║    ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ██║  ██║███████║███████║
    ║     ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝
    ║                                                                ║
    ║         PostgreSQL Performance Analyzer Agent                 ║
    ║                    Compass UOL                                ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
"""

def print_logo():
    """Exibe logo da Compass"""
    # Borda amarela
    logo_lines = COMPASS_LOGO.split('\n')
    for i, line in enumerate(logo_lines):
        if i in [1, 2, 13, 14]:  # Bordas e linha vazia
            print(f"\033[93m{line}\033[0m")
        elif i >= 3 and i <= 9:  # Logo COMPASS
            print(f"\033[93m{line[:8]}\033[38;5;214m{line[8:-1]}\033[93m{line[-1:]}\033[0m")
        elif i == 11:  # PostgreSQL Performance...
            print(f"\033[93m{line[:13]}\033[97m{line[13:-18]}\033[93m{line[-18:]}\033[0m")
        elif i == 12:  # Compass UOL
            print(f"\033[93m{line[:24]}\033[96m{line[24:-20]}\033[93m{line[-20:]}\033[0m")
        else:
            print(line)
    
    print(f"\033[90m    Versao: 1.0.0 | Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\033[0m")
    print()

def print_header(title):
    """Exibe cabeçalho formatado"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def check_mcp_status():
    """Verifica status do MCP"""
    try:
        response = requests.get(f"{MCP_URL}/health", timeout=2)
        if response.status_code == 200:
            return True, "Healthy"
        return False, "Unhealthy"
    except:
        return False, "Offline"

def list_databases():
    """Lista todos os bancos de dados disponíveis"""
    print_header("BANCOS DE DADOS DISPONIVEIS")
    
    try:
        # Conectar no postgres padrão para listar databases
        import subprocess
        result = subprocess.run(
            ['docker', 'exec', 'postgres-analyzer', 'python', '-c',
             """
import sys
sys.path.append('/app/src')
from tools.mcp_tools import get_database_connector
conn = get_database_connector(host='postgres', port=5432, dbname='postgres', username='petclinic', password='petclinic')
if conn and conn.connect():
    result = conn.execute_query('SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname')
    for i, row in enumerate(result, 1):
        print(f"{i}. {row['datname']}")
    conn.disconnect()
"""],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("Erro ao listar bancos de dados")
            
    except Exception as e:
        print(f"Erro: {e}")

def list_tables(dbname=None):
    """Lista todas as tabelas de um banco"""
    if not dbname:
        dbname = DB_CONFIG['dbname']
    
    print_header(f"TABELAS DO BANCO: {dbname}")
    
    try:
        import subprocess
        result = subprocess.run(
            ['docker', 'exec', 'postgres-analyzer', 'python', '-c',
             f"""
import sys
sys.path.append('/app/src')
from tools.mcp_tools import get_database_connector
conn = get_database_connector(host='postgres', port=5432, dbname='{dbname}', username='petclinic', password='petclinic')
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
        print(f"{{i}}. {{row['table_name']}} ({{row['column_count']}} colunas)")
    conn.disconnect()
"""],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("Erro ao listar tabelas")
            
    except Exception as e:
        print(f"Erro: {e}")

def show_table_details(table_name, dbname=None):
    """Mostra detalhes de uma tabela específica"""
    if not dbname:
        dbname = DB_CONFIG['dbname']
    
    print_header(f"DETALHES DA TABELA: {table_name}")
    
    try:
        import subprocess
        result = subprocess.run(
            ['docker', 'exec', 'postgres-analyzer', 'python', '-c',
             f"""
import sys
sys.path.append('/app/src')
from tools.mcp_tools import get_database_connector
conn = get_database_connector(host='postgres', port=5432, dbname='{dbname}', username='petclinic', password='petclinic')
if conn and conn.connect():
    # Colunas
    query = '''
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
    '''
    result = conn.execute_query(query)
    print("\\nCOLUNAS:")
    print("-" * 70)
    for row in result:
        nullable = "NULL" if row['is_nullable'] == 'YES' else "NOT NULL"
        type_info = row['data_type']
        if row['character_maximum_length']:
            type_info += f"({{row['character_maximum_length']}})"
        default = f" DEFAULT {{row['column_default']}}" if row['column_default'] else ""
        print(f"  - {{row['column_name']}}: {{type_info}} {{nullable}}{{default}}")
    
    # Contagem de registros
    count_query = f"SELECT COUNT(*) as total FROM {{table_name}}"
    count_result = conn.execute_query(count_query)
    print(f"\\nTOTAL DE REGISTROS: {{count_result[0]['total']}}")
    
    conn.disconnect()
"""],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("Erro ao buscar detalhes da tabela")
            
    except Exception as e:
        print(f"Erro: {e}")

def show_db_actions():
    """Mostra menu de ações do banco de dados"""
    print_header("ACOES DE BANCO DE DADOS")
    
    print("Escolha uma opcao:")
    print()
    print("  1 - Listar todos os bancos de dados")
    print("  2 - Listar tabelas de um banco especifico")
    print("  3 - Ver detalhes de uma tabela")
    print("  4 - Executar prompts prontos")
    print("  0 - Voltar")
    print()
    
    choice = input("Digite o numero da opcao: ").strip()
    
    if choice == '1':
        list_databases()
    elif choice == '2':
        list_tables()
        print()
        table_choice = input("Digite o numero da tabela para ver detalhes (0 para voltar): ").strip()
        # Implementar seleção por número
    elif choice == '3':
        table_name = input("Digite o nome da tabela: ").strip()
        if table_name:
            show_table_details(table_name)
    elif choice == '4':
        show_prompts_menu()

def show_prompts_menu():
    """Mostra menu de prompts prontos"""
    try:
        response = requests.get(f"{MCP_URL}/prompts")
        print()
        print(response.text)
        print()
        
        prompt_id = input("Digite o numero do prompt para executar (0 para voltar): ").strip()
        if prompt_id and prompt_id != '0':
            execute_prompt(prompt_id)
    except:
        print("Erro ao carregar prompts")

def execute_prompt(prompt_id):
    """Executa um prompt"""
    try:
        import subprocess
        result = subprocess.run(
            ['docker', 'exec', 'postgres-analyzer', 'python', 
             'src/execute_prompt.py', prompt_id],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except Exception as e:
        print(f"Erro ao executar prompt: {e}")

def show_mcp_app():
    """Mostra informações da aplicação e conexão"""
    print_header("INFORMACOES DA APLICACAO")
    
    print(f"Aplicacao: PostgreSQL Performance Analyzer")
    print(f"Versao: 1.0.0")
    print(f"Compass UOL Edition")
    print()
    print("CONFIGURACAO DE BANCO:")
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  Porta: {DB_CONFIG['port']}")
    print(f"  Database: {DB_CONFIG['dbname']}")
    print(f"  Usuario: {DB_CONFIG['username']}")
    print()

def show_help():
    """Mostra comandos disponíveis"""
    print_header("COMANDOS DISPONIVEIS")
    
    print("COMANDOS MCP:")
    print("  mcp help       - Mostra esta ajuda")
    print("  mcp status     - Verifica status do servidor MCP")
    print("  mcp list       - Lista todos os bancos de dados")
    print("  mcp tables     - Lista tabelas do banco atual")
    print("  mcp actions    - Menu interativo de acoes")
    print("  mcp app        - Informacoes da aplicacao")
    print("  mcp prompts    - Lista e executa prompts prontos")
    print("  mcp clear      - Limpa a tela")
    print("  mcp quit       - Sai do prompt")
    print()

def clear_screen():
    """Limpa a tela"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main_loop():
    """Loop principal do prompt interativo"""
    clear_screen()
    print_logo()
    
    # Verificar status inicial
    is_healthy, status = check_mcp_status()
    if is_healthy:
        print(f"    Status MCP: \033[32m{status}\033[0m")
    else:
        print(f"    Status MCP: \033[31m{status}\033[0m")
        print("\n    ATENCAO: MCP nao esta acessivel. Inicie com 'docker compose up -d'")
    
    print()
    print("    \033[93mCOMANDOS DISPONIVEIS:\033[0m")
    print("    \033[36mmcp status\033[0m   - Status do servidor  |  \033[36mmcp list\033[0m    - Listar bancos")
    print("    \033[36mmcp tables\033[0m   - Listar tabelas      |  \033[36mmcp actions\033[0m - Menu de acoes")
    print("    \033[36mmcp prompts\033[0m  - Prompts prontos     |  \033[36mmcp app\033[0m     - Info da app")
    print("    \033[36mmcp help\033[0m     - Ajuda completa      |  \033[36mmcp quit\033[0m    - Sair")
    print()
    
    while True:
        try:
            command = input("\033[33mcompass>\033[0m ").strip().lower()
            
            if not command:
                continue
            
            # Comandos de saída
            if command in ['quit', 'exit', 'q', 'mcp quit']:
                print("\nEncerrando MCP Agent. Ate logo!")
                break
            
            # Comandos MCP
            elif command in ['mcp help', 'help']:
                show_help()
            
            elif command in ['mcp clear', 'clear']:
                clear_screen()
                print_logo()
            
            elif command == 'mcp status':
                is_healthy, status = check_mcp_status()
                print(f"\nStatus MCP: {status}")
                if is_healthy:
                    print("Endpoint: " + MCP_URL)
                    print("Estado: Operacional\n")
                else:
                    print("Estado: Indisponivel\n")
            
            elif command == 'mcp list':
                list_databases()
            
            elif command == 'mcp tables':
                list_tables()
            
            elif command == 'mcp actions':
                show_db_actions()
            
            elif command == 'mcp app':
                show_mcp_app()
            
            elif command == 'mcp prompts':
                show_prompts_menu()
            
            else:
                print(f"Comando desconhecido: '{command}'")
                print("Digite 'mcp help' para ver comandos disponiveis\n")
                
        except KeyboardInterrupt:
            print("\n\nUse 'quit' para sair\n")
        except EOFError:
            print("\n\nEncerrando...")
            break
        except Exception as e:
            print(f"Erro: {e}\n")

if __name__ == "__main__":
    main_loop()