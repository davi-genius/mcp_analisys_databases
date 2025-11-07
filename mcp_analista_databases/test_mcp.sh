#!/bin/bash

echo "=== TESTE COMPLETO DO MCP DATABASE ANALYZER ==="

# Verificar se estamos na VM
if [ ! -f "/opt/mcp/src/main.py" ]; then
    echo "❌ Este script deve ser executado dentro da VM Vagrant"
    echo "Execute: vagrant ssh mcp-petclinic-app"
    exit 1
fi

echo "1. Verificando status dos serviços..."
echo "   PostgreSQL: $(systemctl is-active postgresql)"
echo "   MCP Analyzer: $(systemctl is-active mcp-analyzer)"

echo ""
echo "2. Testando conectividade..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ Health endpoint: OK"
else
    echo "   ❌ Health endpoint: FALHOU"
fi

echo ""
echo "3. Testando banco de dados..."
if psql -h localhost -U petclinic -d petclinic -c "SELECT 1;" > /dev/null 2>&1; then
    echo "   ✅ Conexão PostgreSQL: OK"
else
    echo "   ❌ Conexão PostgreSQL: FALHOU"
fi

echo ""
echo "4. Testando endpoints MCP..."
PROMPTS_COUNT=$(curl -s http://localhost:8000/api/prompts | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data['prompts']))" 2>/dev/null)
if [ "$PROMPTS_COUNT" -gt "0" ]; then
    echo "   ✅ API Prompts: $PROMPTS_COUNT prompts disponíveis"
else
    echo "   ❌ API Prompts: FALHOU"
fi

echo ""
echo "5. Testando imports Python..."
cd /opt/mcp/src
if python3 -c "
import sys
sys.path.insert(0, '.')
from config import configure_logging
from tools.mcp_tools import register_all_tools
from prompts.prompts import MODELS
print('✅ Todos os imports OK')
" 2>/dev/null; then
    echo "   ✅ Imports Python: OK"
else
    echo "   ❌ Imports Python: FALHOU"
fi

echo ""
echo "6. Informações do sistema:"
echo "   Versão Python: $(python3 --version)"
echo "   Versão PostgreSQL: $(psql --version | head -1)"
echo "   Diretório MCP: $(ls -la /opt/mcp/ | wc -l) arquivos"
echo "   Ambiente virtual: $(ls -la /opt/mcp/venv/bin/ | wc -l) executáveis"

echo ""
echo "7. URLs disponíveis:"
echo "   Health Check: http://localhost:8000/health"
echo "   Prompts: http://localhost:8000/prompts"
echo "   API Prompts: http://localhost:8000/api/prompts"
echo "   Sessions: http://localhost:8000/sessions"

echo ""
echo "8. Comandos úteis:"
echo "   Ver logs MCP: journalctl -u mcp-analyzer -f"
echo "   Restart MCP: sudo systemctl restart mcp-analyzer"
echo "   Prompt interativo: python3 /home/vagrant/mcp-prompt.py"
echo "   Conectar ao banco: psql -h localhost -U petclinic -d petclinic"

echo ""
echo "=== TESTE CONCLUÍDO ==="