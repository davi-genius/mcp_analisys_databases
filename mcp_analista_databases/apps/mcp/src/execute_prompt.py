"""
Script auxiliar para executar prompts
"""
import sys
import json
sys.path.append('/app/src')

from tools.mcp_tools import get_database_connector
from prompts.prompts import get_model_by_id

def execute_prompt(prompt_id):
    """Executa um prompt pelo ID"""
    model = get_model_by_id(prompt_id)
    if not model:
        print(f"Prompt {prompt_id} não encontrado")
        return
    
    print(f"\n{'='*70}")
    print(f"📋 {model['name']}")
    print(f"📝 {model['description']}")
    print(f"{'='*70}\n")
    
    # Conectar ao banco
    connector = get_database_connector(
        host='postgres',
        port=5432,
        dbname='petclinic',
        username='petclinic',
        password='petclinic'
    )
    
    if not connector or not connector.connect():
        print("❌ Falha na conexão com o banco")
        return
    
    try:
        if model['tool'] == 'execute_read_only_query':
            query = model['query'].strip()
            result = connector.execute_query(query)
            
            if result:
                print("📊 RESULTADOS:\n")
                for i, row in enumerate(result, 1):
                    print(f"{i}. {row}")
                print(f"\n✅ Total: {len(result)} registros")
            else:
                print("ℹ️  Nenhum resultado encontrado")
        else:
            print(f"🔧 Tool: {model['tool']}")
            print(f"⚠️  Este prompt requer execução via cliente MCP")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        connector.disconnect()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        execute_prompt(sys.argv[1])
    else:
        print("Uso: python execute_prompt.py <prompt_id>")