#!/bin/bash

set -e

echo "=== Configurando MCP Database Analyzer com PostgreSQL Integrado ==="

# Update system
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get upgrade -y

# Install PostgreSQL first
echo "Instalando PostgreSQL..."
apt-get install -y postgresql-14 postgresql-contrib-14 postgresql-client-14

# Install Python 3.10 and related packages
echo "Instalando Python 3.10 e dependências..."
apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip

# Install system dependencies for PostgreSQL and other requirements
apt-get install -y libpq-dev gcc curl build-essential netcat

# Configure PostgreSQL
echo "Configurando PostgreSQL..."
sudo -u postgres psql <<EOF
CREATE DATABASE petclinic;
CREATE USER petclinic WITH ENCRYPTED PASSWORD 'petclinic';
GRANT ALL PRIVILEGES ON DATABASE petclinic TO petclinic;
ALTER USER petclinic CREATEDB;
ALTER DATABASE petclinic OWNER TO petclinic;
\q
EOF

# Configure PostgreSQL para aceitar conexões externas
POSTGRES_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP '\d+\.\d+' | head -1)
PG_VERSION=$(echo $POSTGRES_VERSION | cut -d. -f1)

echo "Configurando PostgreSQL versão $PG_VERSION para acesso externo..."

# Editar postgresql.conf
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/$PG_VERSION/main/postgresql.conf

# Editar pg_hba.conf para permitir conexões
echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/$PG_VERSION/main/pg_hba.conf
echo "host all all 192.168.56.0/24 md5" >> /etc/postgresql/$PG_VERSION/main/pg_hba.conf

# Reiniciar PostgreSQL
systemctl restart postgresql
systemctl enable postgresql

# Aguardar PostgreSQL estar pronto
echo "Aguardando PostgreSQL estar operacional..."
until sudo -u postgres psql -c "SELECT 1" > /dev/null 2>&1; do
  sleep 2
done

# Create symlinks for easier use
ln -sf /usr/bin/python3.10 /usr/bin/python3
ln -sf /usr/bin/python3.10 /usr/bin/python

# Verify Python installation
echo "Versão do Python: $(python3 --version)"

# Change to MCP directory and set ownership
cd /opt/mcp
chown -R vagrant:vagrant /opt/mcp

# Create Python virtual environment as vagrant user
echo "Criando ambiente virtual Python..."
sudo -u vagrant python3 -m venv /opt/mcp/venv

# Activate virtual environment and install dependencies
echo "Instalando dependências Python..."
sudo -u vagrant bash -c "
  cd /opt/mcp
  source venv/bin/activate
  pip install --upgrade pip setuptools wheel
  pip install --no-cache-dir -r requirements.txt
  echo 'Dependências instaladas com sucesso!'
"

# Verify installations
echo "Verificando instalações..."
sudo -u vagrant bash -c "
  cd /opt/mcp
  source venv/bin/activate
  pip list
"

# Create environment configuration (usando localhost já que está na mesma VM)
echo "Criando configuração de ambiente..."
sudo -u vagrant cat > /opt/mcp/.env <<EOF
LOCAL_DB_HOST=localhost
LOCAL_DB_PORT=5432
LOCAL_DB_NAME=petclinic
LOCAL_DB_USERNAME=petclinic
LOCAL_DB_PASSWORD=petclinic
LOG_LEVEL=INFO
SESSION_TIMEOUT=1800
EOF

# Test database connection
echo "Testando conexão com banco de dados..."
sudo -u vagrant bash -c "
  cd /opt/mcp
  source venv/bin/activate
  python3 -c '
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv(\"LOCAL_DB_HOST\"),
        port=os.getenv(\"LOCAL_DB_PORT\"),
        database=os.getenv(\"LOCAL_DB_NAME\"),
        user=os.getenv(\"LOCAL_DB_USERNAME\"),
        password=os.getenv(\"LOCAL_DB_PASSWORD\")
    )
    cursor = conn.cursor()
    cursor.execute(\"SELECT version();\")
    version = cursor.fetchone()
    print(f\"Conexão com PostgreSQL OK: {version[0]}\")
    cursor.close()
    conn.close()
except Exception as e:
    print(f\"Erro na conexão: {e}\")
    exit(1)
'
"

# Create systemd service for MCP Analyzer
echo "Criando serviço systemd..."
cat > /etc/systemd/system/mcp-analyzer.service <<EOF
[Unit]
Description=MCP Database Analyzer
After=network.target postgresql.service
Wants=network-online.target
Requires=postgresql.service

[Service]
Type=simple
User=vagrant
Group=vagrant
WorkingDirectory=/opt/mcp
Environment=PATH=/opt/mcp/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
EnvironmentFile=/opt/mcp/.env
ExecStart=/opt/mcp/venv/bin/python /opt/mcp/src/main.py --host 0.0.0.0 --port 8000
Restart=always
RestartSec=15
StandardOutput=journal
StandardError=journal
SyslogIdentifier=mcp-analyzer

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
systemctl daemon-reload
systemctl enable mcp-analyzer

# Start service
echo "Iniciando serviço MCP Analyzer..."
systemctl start mcp-analyzer

# Wait a bit and check status
sleep 10
echo "Status do serviço:"
systemctl status mcp-analyzer --no-pager

# Test health endpoint
echo "Testando endpoint de saúde..."
sleep 5
if curl -f http://localhost:8000/health; then
    echo -e "\n✅ MCP Analyzer está respondendo!"
else
    echo -e "\n❌ MCP Analyzer não está respondendo"
    echo "Verificando logs:"
    journalctl -u mcp-analyzer --no-pager -n 20
fi

# Copy and configure the interactive prompt
echo "Copiando script de prompt interativo..."
sudo -u vagrant cp /opt/mcp/mcp-prompt.py /home/vagrant/mcp-prompt.py
sudo -u vagrant chmod +x /home/vagrant/mcp-prompt.py

# Update the interactive prompt for integrated environment
sudo -u vagrant sed -i 's/MCP_URL = "http:\/\/localhost:8000"/MCP_URL = "http:\/\/localhost:8000"/' /home/vagrant/mcp-prompt.py
sudo -u vagrant sed -i 's/"host": "localhost"/"host": "localhost"/' /home/vagrant/mcp-prompt.py

# Create convenient aliases and functions
echo "Criando aliases úteis..."
sudo -u vagrant cat >> /home/vagrant/.bashrc << 'EOFBASH'

# MCP Analyzer Aliases
alias mcp-prompt='cd /home/vagrant && python3 mcp-prompt.py'
alias mcp-start='cd /home/vagrant && python3 mcp-prompt.py'
alias mcp-status='systemctl status mcp-analyzer --no-pager'
alias mcp-logs='journalctl -u mcp-analyzer -f'
alias mcp-restart='sudo systemctl restart mcp-analyzer'

# PostgreSQL Aliases
alias pg-status='systemctl status postgresql --no-pager'
alias pg-logs='journalctl -u postgresql -f'
alias pg-restart='sudo systemctl restart postgresql'
alias pg-connect='psql -h localhost -U petclinic -d petclinic'

# Quick commands
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Auto-start MCP prompt on interactive SSH login
if [[ $- == *i* ]] && [[ -n "$SSH_CONNECTION" ]] && [[ -z "$MCP_PROMPT_STARTED" ]]; then
    export MCP_PROMPT_STARTED=1
    echo ""
    echo "🚀 Iniciando MCP Database Analyzer automaticamente..."
    echo "   Para pular, pressione Ctrl+C nos próximos 3 segundos"
    echo "   Ou digite 'mcp-start' a qualquer momento para iniciar manualmente"
    echo ""
    
    # Wait 3 seconds, allow user to cancel
    if timeout 3 bash -c 'read -n 1 -s'; then
        echo "Inicialização cancelada pelo usuário."
        echo "💡 Use 'mcp-start' para iniciar o prompt quando quiser!"
    else
        cd /home/vagrant
        python3 mcp-prompt.py
    fi
fi
EOFBASH

echo "=== MCP Analyzer configurado com sucesso! ==="
echo "Serviços disponíveis:"
echo "  - API: http://192.168.56.12:8000 (interno) / http://localhost:8000 (externo)"
echo "  - Health: http://192.168.56.12:8000/health"
echo "  - Prompts: http://192.168.56.12:8000/prompts"
echo ""
echo "Comandos úteis:"
echo "  - mcp-start      : Iniciar prompt MCP interativo"
echo "  - mcp-status     : Ver status do serviço MCP"
echo "  - mcp-logs       : Ver logs do MCP em tempo real"
echo "  - pg-status      : Ver status do PostgreSQL"
echo "  - pg-logs        : Ver logs do PostgreSQL"
echo ""
echo "Acesso rápido:"
echo "  - SSH: vagrant ssh analyzer"
echo "  - Prompt automático inicia em 3 segundos"
echo "  - Cancele com Ctrl+C e use 'mcp-start' depois"