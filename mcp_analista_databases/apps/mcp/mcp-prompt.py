#!/usr/bin/env python3
"""
MCP Interactive Prompt - PostgreSQL Performance Analyzer
Compass UOL Edition
"""
import sys
import os
import psycopg2
import json
import re
from typing import Dict, List, Optional
import requests
from datetime import datetime

# Cores do UOL Compass e Amazon Q
class AmazonColors:
    ORANGE = '\033[38;5;214m'     # Laranja Amazon Q
    UOL_ORANGE = '\033[38;5;202m' # Laranja UOL vibrante (círculo externo)
    UOL_RED = '\033[38;5;196m'    # Vermelho UOL (círculo interno)
    UOL_YELLOW = '\033[38;5;220m' # Amarelo UOL (círculo meio)
    BLUE = '\033[38;5;33m'        # Azul Amazon Q
    DARK_BLUE = '\033[38;5;17m'   # Azul escuro para texto
    WHITE = '\033[97m'            # Branco
    GRAY = '\033[90m'             # Cinza
    BLACK = '\033[30m'            # Preto para "compass.uol"
    RESET = '\033[0m'             # Reset

# Configurações
MCP_URL = "http://localhost:8000"
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "petclinic",
    "username": "petclinic",
    "password": "petclinic"
}

def print_welcome_auto_start():
    """Exibe mensagem de boas-vindas para auto-start"""
    print(f"{AmazonColors.ORANGE}")
    print("    Conectando ao MCP Database Analyzer...  ✨")
    print("    Sistema inicializado com sucesso!       🚀")
    print(f"{AmazonColors.RESET}")
    print()

def is_auto_started():
    """Verifica se foi iniciado automaticamente"""
    return os.getenv('MCP_PROMPT_STARTED') == '1'

# Logo ASCII da Compass UOL (baseado na imagem real)
COMPASS_LOGO = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                                                                              ║
║                                                                              ║
║                                                                              ║
║                                                                              ║
║          ██████╗ ██████╗ ███╗   ███╗██████╗  █████╗ ███████╗███████╗        ║
║         ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔══██╗██╔════╝██╔════╝        ║
║         ██║     ██║   ██║██╔████╔██║██████╔╝███████║███████╗███████╗        ║
║         ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██╔══██║╚════██║╚════██║        ║
║         ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ██║  ██║███████║███████║        ║
║          ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝        ║
║                                                                              ║
║                                                                              ║
║                                                                              ║
║                               ██╗   ██╗ ██████╗ ██╗                        ║
║                               ██║   ██║██╔═══██╗██║                        ║
║                               ██║   ██║██║   ██║██║                        ║
║                               ██║   ██║██║   ██║██║                        ║
║                               ╚██████╔╝╚██████╔╝███████╗                   ║
║                                ╚═════╝  ╚═════╝ ╚══════╝                   ║
║                                                                              ║
║                      PostgreSQL Performance Analyzer                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

def print_logo():
    """Exibe logo da Compass UOL limpo - COMPASS em preto, UOL em laranja"""
    logo_lines = COMPASS_LOGO.split('\n')
    for i, line in enumerate(logo_lines):
        if i in [1, 29]:  # Bordas superior e inferior
            print(f"{AmazonColors.BLUE}{line}{AmazonColors.RESET}")
        elif "██╗   ██╗ ██████╗ ██╗" in line or "██║   ██║██╔═══██╗██║" in line or "██║   ██║██║   ██║██║" in line or "╚██████╔╝╚██████╔╝███████╗" in line or "╚═════╝  ╚═════╝ ╚══════╝" in line:
            # "UOL" em laranja
            print(f"{AmazonColors.UOL_ORANGE}{line}{AmazonColors.RESET}")
        elif "██" in line and any(word in line for word in ["██████╗", "██╔", "██║", "╚██████╗", "╚═════╝"]):
            # "COMPASS" (incluindo SS na mesma linha) em preto
            print(f"{AmazonColors.BLACK}{line}{AmazonColors.RESET}")
        elif "PostgreSQL Performance Analyzer" in line:
            # Subtítulo em azul
            print(f"{AmazonColors.BLUE}{line}{AmazonColors.RESET}")
        elif line.strip().startswith("║") or line.strip().startswith("╚") or line.strip().startswith("╔"):
            # Bordas em azul
            print(f"{AmazonColors.BLUE}{line}{AmazonColors.RESET}")
        else:
            print(line)
    
    print(f"{AmazonColors.GRAY}        Versão: 1.0.0 | Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} | compass.uol{AmazonColors.RESET}")
    print()

def print_welcome():
    """Exibe o logo da Compass e menu principal"""
    print_logo()
    print(f"{AmazonColors.BLUE}💡 Digite 'mcp help' para ver os comandos disponíveis{AmazonColors.RESET}")
    print()

def print_header(title):
    """Exibe cabeçalho formatado"""
    print(f"\n{AmazonColors.BLUE}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{AmazonColors.RESET}\n")

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
        import psycopg2
        # Conectar no postgres padrão para listar databases
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database='postgres',  # Conectar no postgres padrão
            user=DB_CONFIG['username'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname")
        databases = cursor.fetchall()
        
        for i, (dbname,) in enumerate(databases, 1):
            print(f"{i}. {dbname}")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erro ao conectar com PostgreSQL: {e}")
        print("Verifique se o PostgreSQL está rodando e as credenciais estão corretas.")

def list_tables(dbname=None):
    """Lista todas as tabelas de um banco"""
    if not dbname:
        dbname = DB_CONFIG['dbname']
    
    print_header(f"TABELAS DO BANCO: {dbname}")
    
    try:
        import psycopg2
        # Conectar no banco especificado
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=dbname,
            user=DB_CONFIG['username'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Query para listar tabelas com contagem de colunas
        cursor.execute("""
            SELECT 
                table_name,
                (SELECT COUNT(*) 
                 FROM information_schema.columns 
                 WHERE table_name = t.table_name 
                   AND table_schema = 'public') as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        
        if tables:
            for i, (table_name, column_count) in enumerate(tables, 1):
                print(f"{i}. {table_name} ({column_count} colunas)")
        else:
            print("Nenhuma tabela encontrada no schema public.")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erro ao conectar com PostgreSQL: {e}")
        print("Verifique se o PostgreSQL está rodando e as base de dados existe.")

def show_table_details(table_name, dbname=None):
    """Mostra detalhes de uma tabela específica"""
    if not dbname:
        dbname = DB_CONFIG['dbname']
    
    print_header(f"DETALHES DA TABELA: {table_name}")
    
    try:
        import psycopg2
        # Conectar no banco especificado
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=dbname,
            user=DB_CONFIG['username'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Buscar informações das colunas
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = cursor.fetchall()
        
        if columns:
            print("\nCOLUNAS:")
            print("-" * 70)
            for column_name, data_type, max_length, is_nullable, default in columns:
                nullable = "NULL" if is_nullable == 'YES' else "NOT NULL"
                type_info = data_type
                if max_length:
                    type_info += f"({max_length})"
                default_info = f" DEFAULT {default}" if default else ""
                print(f"  - {column_name}: {type_info} {nullable}{default_info}")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\nTOTAL DE REGISTROS: {count}")
        else:
            print(f"Tabela '{table_name}' não encontrada.")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erro ao conectar com PostgreSQL: {e}")

def show_db_actions():
    """Mostra menu de ações do banco de dados"""
    print_header("MENU DE ACOES")
    
    print("Escolha uma opcao:")
    print()
    print("  1 - Listar bancos de dados")
    print("  2 - Listar tabelas do banco atual")
    print("  3 - Executar prompts prontos")
    print("  4 - Informações da aplicação")
    print("  0 - Voltar")
    print()
    
    choice = input("Digite o numero da opcao: ").strip()
    
    if choice == '1':
        list_databases()
    elif choice == '2':
        list_tables()
    elif choice == '3':
        show_prompts_menu()
    elif choice == '4':
        show_mcp_app()
    elif choice == '0':
        return
    else:
        print("Opção inválida!")
        
    print()
    input("Pressione ENTER para continuar...")
    show_db_actions()  # Retorna ao menu

def show_prompts_menu():
    """Mostra menu de prompts prontos"""
    try:
        print_header("PROMPTS DE ANALISE")
        print("PostgreSQL Performance Analyzer")
        print("=" * 50)
        print()
        
        # Lista simplificada e otimizada
        prompts = [
            "1. Estrutura Completa do Banco",
            "2. Contagem de Registros por Tabela", 
            "3. Análise de Performance",
            "4. Proprietários e Pets", 
            "5. Estatísticas de Visitas",
            "6. Configurações do PostgreSQL"
        ]
        
        for prompt in prompts:
            print(prompt)
        
        print()
        print("💡 Dica: Os prompts executam análises via API MCP")
        print()
        
        prompt_id = input("Digite o numero do prompt (0 para voltar): ").strip()
        if prompt_id and prompt_id != '0':
            execute_prompt(prompt_id)
            
    except Exception as e:
        print(f"Erro ao carregar prompts: {e}")
        print("Verifique se o serviço MCP está rodando.")

def execute_prompt(prompt_id):
    """Executa um prompt via API MCP"""
    try:
        # Fazer chamada para a API MCP
        response = requests.post(f"{MCP_URL}/execute_prompt", 
                               json={"prompt_id": int(prompt_id)}, 
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'result' in result:
                print(result['result'])
            else:
                print("Prompt executado com sucesso!")
        else:
            print(f"Erro ao executar prompt: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Erro ao executar prompt: {e}")
        print("Verifique se o serviço MCP está rodando.")

def show_mcp_app():
    """Mostra informações da aplicação"""
    print_header("INFORMACOES DO SISTEMA")
    
    print(f"📊 Aplicação: PostgreSQL Performance Analyzer")
    print(f"🏷️  Versão: 1.0.0")
    print(f"🏢 Compass UOL - Vagrant Edition")
    print(f"🖥️  Ambiente: Ubuntu 22.04 LTS")
    print()
    print("🔗 CONEXÕES:")
    print(f"  🔍 MCP API: {MCP_URL}")
    print(f"  🐘 PostgreSQL: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"  📊 Database: {DB_CONFIG['dbname']}")
    print()
    print("🌐 ACESSO EXTERNO:")
    print(f"  🔍 MCP API: http://localhost:8000")
    print(f"  🐘 PostgreSQL: localhost:5432")
    print()

def clear_screen():
    """Limpa a tela"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main_loop():
    """Loop principal do prompt interativo"""
    clear_screen()
    
    # Se foi iniciado automaticamente, mostra boas-vindas especial
    if is_auto_started():
        print_welcome_auto_start()
    
    print_logo()
    
    # Verificar status inicial
    is_healthy, status = check_mcp_status()
    if is_healthy:
        print(f"    Status MCP: \033[32m{status}\033[0m")
    else:
        print(f"    Status MCP: \033[31m{status}\033[0m")
        print("\n    ATENCAO: MCP nao esta acessivel. Verifique se as VMs estao rodando")
    
    print()
    print("    \033[93mCOMANDOS PRINCIPAIS:\033[0m")
    print("    \033[36mmcp status\033[0m   - Status do sistema   |  \033[36mmcp actions\033[0m - Menu principal")
    print("    \033[36mmcp list\033[0m     - Listar bancos      |  \033[36mmcp tables\033[0m  - Listar tabelas")
    print("    \033[36mmcp prompts\033[0m  - Análises prontas   |  \033[36mmcp quit\033[0m    - Sair")
    print()
    
    # Se foi auto-iniciado, mostrar dica de acesso rápido
    if is_auto_started():
        print("    \033[95m💡 DICA: Digite 'mcp actions' para acessar o menu completo\033[0m")
        print("    \033[95m💡 DICA: Digite 'mcp status' para verificar o sistema\033[0m")
        print()
    
    while True:
        try:
            command = input(f"{AmazonColors.ORANGE}compass❯ {AmazonColors.RESET}").strip().lower()
            
            if not command:
                continue
            
            # Comandos de saída
            if command in ['quit', 'exit', 'q', 'mcp quit']:
                print("\n✅ Encerrando MCP Agent. Até logo!")
                break
            
            # Comandos MCP essenciais
            elif command in ['mcp clear', 'clear']:
                clear_screen()
                print_logo()
            
            elif command in ['mcp status', 'status']:
                is_healthy, status = check_mcp_status()
                print(f"\n📊 Status MCP: {status}")
                if is_healthy:
                    print(f"🌐 Endpoint: {MCP_URL}")
                    print("✅ Estado: Operacional\n")
                else:
                    print("❌ Estado: Indisponível\n")
            
            elif command in ['mcp list', 'list']:
                list_databases()
            
            elif command in ['mcp tables', 'tables']:
                list_tables()
            
            elif command in ['mcp actions', 'actions']:
                show_db_actions()
            
            elif command in ['mcp prompts', 'prompts']:
                show_prompts_menu()
            
            elif command in ['mcp app', 'app']:
                show_mcp_app()
            
            else:
                print(f"❌ Comando desconhecido: '{command}'")
                print("💡 Digite 'mcp actions' para ver opções disponíveis\n")
                
        except KeyboardInterrupt:
            print("\n\nUse 'quit' para sair\n")
        except EOFError:
            print("\n\nEncerrando...")
            break
        except Exception as e:
            print(f"Erro: {e}\n")

if __name__ == "__main__":
    main_loop()