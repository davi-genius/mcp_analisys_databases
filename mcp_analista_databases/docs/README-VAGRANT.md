# MCP Database Analyzer - Vagrant Edition

## 🚀 Visão Geral

Este projeto configura um ambiente completo para análise de performance de bancos PostgreSQL usando **Vagrant** para máxima compatibilidade e performance nativa. O ambiente inclui:

- **PostgreSQL Server** (192.168.56.10:5432) - Banco de dados principal
- **PetClinic Application** (192.168.56.11:8080) - Aplicação de exemplo
- **MCP Analyzer** (192.168.56.12:8000) - **Prompt MCP com auto-start via SSH**

## ✨ Principais Funcionalidades

- 🎯 **Prompt MCP inicia automaticamente** quando você faz SSH na VM analyzer
- 🐧 Ubuntu 22.04 LTS com Python 3.10, Java 17, Node.js 18
- 🔧 Scripts de gerenciamento simples (`manage.sh`)
- 🎨 Interface colorida e intuitiva
- 📊 Monitoramento e análise de performance em tempo real

## 📋 Pré-requisitos

- [Vagrant](https://www.vagrantup.com/downloads) instalado
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads) instalado
- Pelo menos 6GB de RAM disponível
- 20GB de espaço em disco

## ⚡ Início Rápido

### 1. Inicialização Completa

Para subir todo o ambiente:

```bash
# Usar script de gerenciamento (recomendado)
./manage.sh up

# Ou comando vagrant direto
vagrant up
```

### 2. Acesso Direto ao MCP (Auto-start)

```bash
# O prompt MCP inicia automaticamente!
./manage.sh ssh-analyzer
# ou
vagrant ssh analyzer
```

### 2. Inicialização Individual

Para subir VMs específicas:

```bash
# Apenas PostgreSQL
vagrant up postgres

# Apenas PetClinic (requer postgres)
vagrant up postgres petclinic

# Apenas MCP Analyzer (requer postgres)
vagrant up postgres analyzer
```

### 3. Verificação do Status

```bash
# Status de todas as VMs
vagrant status

# Status global
vagrant global-status
```

## Acesso aos Serviços

### PostgreSQL Database
- **Host:** localhost:5432 (externo) / 192.168.56.10:5432 (interno)
- **Database:** petclinic
- **Usuário:** petclinic
- **Senha:** petclinic

### PetClinic Application
- **URL:** http://localhost:8080
- **URL Interna:** http://192.168.56.11:8080

### MCP Analyzer
- **API:** http://localhost:8000
- **Health Check:** http://localhost:8000/health
- **Prompts:** http://localhost:8000/prompts

## 🎯 Auto-Start do Prompt MCP

**PRINCIPAL FUNCIONALIDADE:** O prompt interativo do MCP inicia **automaticamente** quando você faz SSH na VM analyzer!

```bash
# Conecte-se à VM do MCP
vagrant ssh analyzer

# O prompt aparece automaticamente:
# ╔══════════════════════════════════════════════════════════════════╗
# ║  🚀 BEM-VINDO AO MCP DATABASE ANALYZER - VAGRANT EDITION        ║
# ║     ✨ Iniciado automaticamente via SSH                         ║
# ║     🐘 PostgreSQL pronto para análise                           ║
# ║     🔍 Ferramentas de performance disponíveis                   ║
# ╚══════════════════════════════════════════════════════════════════╝

# Use comandos como:
compass> mcp status     # Verificar status
compass> mcp actions    # Menu de ações
compass> mcp prompts    # Análises prontas
compass> quit           # Sair
```

### Como Cancelar o Auto-Start

Se você quiser acessar o shell normal da VM, você tem 3 segundos para pressionar qualquer tecla quando a mensagem aparecer.

## Comandos Úteis

### Gerenciamento das VMs

```bash
# Parar todas as VMs
vagrant halt

# Reiniciar VMs
vagrant reload

# Reprovisionar (aplicar mudanças nos scripts)
vagrant provision

# Destruir ambiente (cuidado!)
vagrant destroy
```

### Acesso SSH

```bash
# Acessar PostgreSQL VM
vagrant ssh postgres

# Acessar PetClinic VM
vagrant ssh petclinic

# Acessar MCP Analyzer VM
vagrant ssh analyzer
```

### Logs e Monitoramento

```bash
# Logs do PostgreSQL
vagrant ssh postgres -c "sudo journalctl -u postgresql -f"

# Logs do PetClinic
vagrant ssh petclinic -c "sudo journalctl -u petclinic -f"

# Logs do MCP Analyzer
vagrant ssh analyzer -c "sudo journalctl -u mcp-analyzer -f"
```

### Prompt Interativo do MCP

```bash
# Acessar prompt interativo
vagrant ssh analyzer -c "mcp-prompt"

# Ou conectar e executar manualmente
vagrant ssh analyzer
cd /home/vagrant
python3 mcp-prompt.py
```

## Estrutura das VMs

### VM PostgreSQL (mcp-postgres-db)
- **IP:** 192.168.56.10
- **RAM:** 1GB
- **CPUs:** 1
- **Portas:** 5432

### VM PetClinic (mcp-petclinic-app)
- **IP:** 192.168.56.11
- **RAM:** 3GB
- **CPUs:** 2
- **Portas:** 8080

### VM MCP Analyzer (mcp-analyzer)
- **IP:** 192.168.56.12
- **RAM:** 1.5GB
- **CPUs:** 2
- **Portas:** 8000

## Troubleshooting

### Problema: VMs não sobem
```bash
# Verificar VirtualBox
VBoxManage list runningvms

# Limpar cache do Vagrant
vagrant global-status --prune
```

### Problema: Serviços não respondem
```bash
# Verificar status dos serviços
vagrant ssh <vm_name> -c "sudo systemctl status <service_name>"

# Reiniciar serviços
vagrant ssh <vm_name> -c "sudo systemctl restart <service_name>"
```

### Problema: Conectividade entre VMs
```bash
# Testar conectividade
vagrant ssh analyzer -c "nc -z 192.168.56.10 5432"
vagrant ssh petclinic -c "nc -z 192.168.56.10 5432"
```

### Problema: Performance baixa
- Aumentar RAM das VMs no Vagrantfile
- Verificar recursos disponíveis no host
- Usar SSD se possível

## Desenvolvimento

### Sincronização de Código

O código é sincronizado via rsync para melhor performance:

- **PetClinic:** `./lab_agent/pet-clinic-hilla` → `/opt/petclinic`
- **MCP:** `./lab_agent/mcp` → `/opt/mcp`

Para aplicar mudanças:

```bash
# Reprovisionar apenas uma VM
vagrant provision analyzer

# Ou fazer rsync manual
vagrant rsync analyzer
```

### Personalização

Edite os scripts em `vagrant/` para personalizar a configuração:

- `provision-postgres.sh` - Setup do PostgreSQL
- `provision-petclinic.sh` - Setup do PetClinic
- `provision-analyzer.sh` - Setup do MCP

## Comandos Rápidos

```bash
# Setup completo
vagrant up

# Testar tudo funcionando
curl http://localhost:8000/health
curl http://localhost:8080
psql -h localhost -U petclinic -d petclinic -c "SELECT version();"

# Acessar prompt MCP
vagrant ssh analyzer -c "mcp-prompt"

# Ver status
vagrant status

# Parar tudo
vagrant halt
```

## Sistema Operacional

- **Base:** Ubuntu 22.04 LTS (Jammy Jellyfish)
- **Arquitetura:** x64
- **Python:** 3.10
- **Java:** OpenJDK 17
- **Node.js:** 18 LTS