#!/bin/bash

echo "=== Corrigindo e testando MCP Database Analyzer ==="

# Parar serviços se estiverem rodando
echo "Parando serviços..."
sudo systemctl stop mcp-analyzer 2>/dev/null || true
sudo systemctl stop petclinic 2>/dev/null || true

# Ir para o diretório MCP
cd /opt/mcp

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual e instalar dependências
echo "Instalando dependências..."
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install --no-cache-dir -r requirements.txt

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo "Criando arquivo .env..."
    cat > .env <<EOF
LOCAL_DB_HOST=localhost
LOCAL_DB_PORT=5432
LOCAL_DB_NAME=petclinic
LOCAL_DB_USERNAME=petclinic
LOCAL_DB_PASSWORD=petclinic
LOG_LEVEL=INFO
SESSION_TIMEOUT=1800
EOF
fi

# Testar conexão com banco
echo "Testando conexão com banco de dados..."
python3 -c "
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('LOCAL_DB_HOST'),
        port=os.getenv('LOCAL_DB_PORT'),
        database=os.getenv('LOCAL_DB_NAME'),
        user=os.getenv('LOCAL_DB_USERNAME'),
        password=os.getenv('LOCAL_DB_PASSWORD')
    )
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()
    print(f'✅ Conexão com PostgreSQL OK: {version[0]}')
    cursor.close()
    conn.close()
except Exception as e:
    print(f'❌ Erro na conexão: {e}')
    exit(1)
"

# Testar se o MCP pode ser importado
echo "Testando imports do MCP..."
cd /opt/mcp/src
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from config import configure_logging, server_lifespan, session_handler
    from tools.mcp_tools import register_all_tools
    from prompts.prompts import MODELS, get_model_list
    print('✅ Todos os imports funcionaram!')
except Exception as e:
    print(f'❌ Erro nos imports: {e}')
    exit(1)
"

# Reiniciar serviços
echo "Reiniciando serviços..."
sudo systemctl daemon-reload
sudo systemctl start mcp-analyzer
sleep 5

# Verificar status
echo "Verificando status dos serviços..."
sudo systemctl status mcp-analyzer --no-pager

# Testar endpoint de saúde
echo "Testando endpoint de saúde..."
sleep 3
if curl -f http://localhost:8000/health; then
    echo -e "\n✅ MCP Analyzer está funcionando!"
else
    echo -e "\n❌ MCP Analyzer não está respondendo"
    echo "Logs do serviço:"
    sudo journalctl -u mcp-analyzer --no-pager -n 20
fi

echo "=== Correção concluída ==="