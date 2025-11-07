# 🚀 MCP Analista Databases - Comandos Vagrant

## ⚡ Comandos Vagrant Diretos

### 📦 Gerenciamento Básico
```bash
# Iniciar todas as VMs
vagrant up

# Iniciar apenas VM específica
vagrant up analyzer    # MCP + PostgreSQL
vagrant up petclinic   # PetClinic App

# Parar VMs
vagrant halt           # Todas
vagrant halt analyzer  # Apenas analyzer
vagrant halt petclinic # Apenas petclinic

# Status das VMs
vagrant status
vagrant global-status
```

### 🔧 Manutenção e Debugging
```bash
# Reprovisionar (aplicar mudanças nos scripts)
vagrant provision           # Todas
vagrant provision analyzer  # Apenas analyzer
vagrant provision petclinic # Apenas petclinic

# Reiniciar VMs
vagrant reload              # Todas
vagrant reload analyzer     # Apenas analyzer
vagrant reload petclinic    # Apenas petclinic

# Destruir VMs (cuidado!)
vagrant destroy             # Todas
vagrant destroy analyzer    # Apenas analyzer
vagrant destroy petclinic   # Apenas petclinic
```

### 🖥️ Acesso SSH
```bash
# SSH para MCP (prompt auto-start!)
vagrant ssh analyzer

# SSH para PetClinic
vagrant ssh petclinic

# SSH com comando específico
vagrant ssh analyzer -c "mcp-status"
vagrant ssh analyzer -c "mcp-logs"
vagrant ssh analyzer -c "sudo systemctl status postgresql"
```

## 🔧 Script de Gerenciamento (manage.sh)

### 📦 Comandos Básicos
```bash
# Iniciar ambiente
./manage.sh up              # Todas as VMs
./manage.sh up analyzer     # Apenas analyzer
./manage.sh up petclinic    # Apenas petclinic

# Parar ambiente
./manage.sh down            # Todas as VMs
./manage.sh down analyzer   # Apenas analyzer
./manage.sh down petclinic  # Apenas petclinic

# Status e testes
./manage.sh status          # Status das VMs
./manage.sh test            # Teste de conectividade
```

### 🔧 Manutenção
```bash
# Reprovisionar
./manage.sh provision           # Todas as VMs
./manage.sh provision analyzer  # Apenas analyzer
./manage.sh provision petclinic # Apenas petclinic

# Reiniciar
./manage.sh reload              # Todas as VMs
./manage.sh reload analyzer     # Apenas analyzer
./manage.sh reload petclinic    # Apenas petclinic

# Limpeza completa
./manage.sh clean               # Destruir e recriar
```

### 🖥️ Acesso e Logs
```bash
# SSH direto
./manage.sh ssh-analyzer    # MCP (auto-start prompt)
./manage.sh ssh-postgres    # PostgreSQL (mesma VM)
./manage.sh ssh-petclinic   # PetClinic

# Logs em tempo real
./manage.sh logs-mcp        # Logs do MCP
./manage.sh logs-pg         # Logs PostgreSQL
./manage.sh logs-app        # Logs PetClinic
```

## 🎯 Comandos Mais Usados

### Início Rápido
```bash
# Setup inicial
vagrant up
./manage.sh test

# Acessar MCP (auto-start!)
vagrant ssh analyzer
```

### Desenvolvimento
```bash
# Reprovisionar apenas MCP após mudanças
./manage.sh provision analyzer

# Ver logs do MCP
./manage.sh logs-mcp

# Reiniciar apenas analyzer
./manage.sh reload analyzer
```

### Troubleshooting
```bash
# Status completo
./manage.sh status

# Testar conectividade
./manage.sh test

# Ver logs de erro
vagrant ssh analyzer -c "journalctl -u mcp-analyzer -n 50"
vagrant ssh petclinic -c "journalctl -u petclinic -n 50"
```

## 🌐 URLs de Acesso

- **🌸 PetClinic**: http://localhost:8080
- **🔍 MCP API**: http://localhost:8000
- **❤️ Health Check**: http://localhost:8000/health
- **📊 Prompts**: http://localhost:8000/prompts
- **🐘 PostgreSQL**: localhost:5432 (user: petclinic, pass: petclinic)

## 📋 Aliases na VM Analyzer

Quando você fizer SSH na VM analyzer, estão disponíveis:

```bash
mcp-prompt    # Iniciar prompt MCP manualmente
mcp-status    # Status do serviço MCP
mcp-logs      # Logs do MCP
pg-status     # Status PostgreSQL
pg-logs       # Logs PostgreSQL
```

## 🚨 Comandos de Emergência

```bash
# Se algo der errado, reset completo:
vagrant destroy -f
vagrant up

# Ou usar o script:
./manage.sh clean
./manage.sh up
```

---

**💡 Dica**: Use sempre `vagrant ssh analyzer` para acesso direto ao prompt MCP! 🚀