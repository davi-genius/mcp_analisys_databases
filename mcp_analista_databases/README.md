# 🚀 MCP Database Analyzer - Vagrant Edition

## ✅ STATUS: FUNCIONANDO CORRETAMENTE

**Última atualização**: 2025-11-07  
**Problemas corrigidos**: Dependências, imports, caminhos, configuração systemd

## ⚡ Visão Geral

Sistema integrado de análise de performance PostgreSQL com **prompt MCP que inicia automaticamente** via SSH!

### 🎯 Principais Funcionalidades

- **🎪 Auto-Start**: Prompt MCP inicia automaticamente quando você faz SSH
- **🏗️ Arquitetura Simplificada**: Apenas 2 VMs otimizadas
- **🐘 PostgreSQL Integrado**: Banco de dados na mesma VM do MCP
- **🌍 Acesso Externo**: PetClinic e MCP acessíveis do host
- **🎨 Interface Rica**: Prompt colorido com comandos intuitivos

## 🏗️ Arquitetura (2 VMs)

```
┌─────────────────────┐    ┌─────────────────────┐
│   MCP Analyzer      │    │    PetClinic        │
│  (192.168.56.12)   │    │  (192.168.56.11)   │
│                     │    │                     │
│  🔍 MCP API :8000   │◄──►│  🌸 Spring App      │
│  🐘 PostgreSQL :5432│    │     :8080           │
│  🎯 Auto Prompt     │    │                     │
│                     │    │                     │
│  2GB RAM / 2 CPU    │    │  3GB RAM / 2 CPU    │
└─────────────────────┘    └─────────────────────┘
           ▲                          ▲
           │                          │
    localhost:8000             localhost:8080
    localhost:5432         
```

## ⚡ Início Rápido

### 1. Iniciar Ambiente

```bash
# Via script de gerenciamento
./manage.sh up

# Ou comando direto
vagrant up
```

### 2. Acessar MCP (Auto-Start!)

```bash
# O prompt MCP inicia automaticamente!
vagrant ssh analyzer

# Você verá imediatamente:
# ╔══════════════════════════════════════════════════════════════════╗
# ║  🚀 BEM-VINDO AO MCP DATABASE ANALYZER - VAGRANT EDITION        ║
# ║     ✨ Iniciado automaticamente via SSH                         ║
# ║     🐘 PostgreSQL pronto para análise                           ║
# ╚══════════════════════════════════════════════════════════════════╝
#
# compass> _
```

### 3. URLs de Acesso Externo

- **🌸 PetClinic**: http://localhost:8080
- **🔍 MCP API**: http://localhost:8000
- **❤️ Health Check**: http://localhost:8000/health
- **🐘 PostgreSQL**: localhost:5432 (petclinic/petclinic)

## 🎮 Comandos do MCP

Quando estiver no prompt MCP:

```bash
compass> mcp status     # Status dos serviços
compass> mcp actions    # Menu de ações interativo  
compass> mcp prompts    # Análises prontas
compass> mcp list       # Listar bancos
compass> mcp tables     # Listar tabelas
compass> mcp help       # Ajuda completa
compass> quit           # Sair
```

## 🔧 Gerenciamento

### Script Bash (Recomendado)

```bash
./manage.sh up          # Iniciar ambiente
./manage.sh status      # Status das VMs
./manage.sh ssh-analyzer # SSH para MCP (auto-start)
./manage.sh test        # Testar conectividade
./manage.sh down        # Parar ambiente
```

### Comandos Vagrant Diretos

```bash
# Gerenciamento básico
vagrant up               # Iniciar todas as VMs
vagrant up analyzer      # Iniciar apenas MCP + PostgreSQL
vagrant up petclinic     # Iniciar apenas PetClinic
vagrant ssh analyzer     # SSH para MCP (prompt auto-start)
vagrant halt             # Parar tudo
vagrant provision        # Reprovisionar
vagrant reload           # Reiniciar VMs
```

**📚 Para lista completa de comandos**: Ver arquivo `COMANDOS.md`

### Logs e Monitoramento

```bash
# Via script
./manage.sh logs-mcp    # Logs do MCP
./manage.sh logs-pg     # Logs PostgreSQL
./manage.sh logs-app    # Logs PetClinic

# Via SSH direto
vagrant ssh analyzer -c "mcp-logs"
vagrant ssh analyzer -c "pg-logs"
```

## 📁 Estrutura Organizada

```
mcp_analista_databases/
├── Vagrantfile                 # Configuração principal
├── manage.sh                   # Script de gerenciamento
├── vagrant/
│   ├── provision-analyzer.sh   # Setup MCP + PostgreSQL
│   └── provision-petclinic.sh  # Setup PetClinic
├── apps/
│   ├── mcp/                    # Código MCP Analyzer
│   │   ├── mcp-prompt.py       # Prompt interativo
│   │   ├── requirements.txt
│   │   └── src/                # API e ferramentas
│   └── pet-clinic-hilla/       # Aplicação Spring Boot
├── config/
│   └── .vagrant.env            # Configurações
└── docs/
    ├── README-VAGRANT.md       # Documentação detalhada
    └── RESUMO-MUDANCAS.md     # Histórico de mudanças
```

## 🎯 Casos de Uso

### Análise Rápida
```bash
vagrant ssh analyzer    # Auto-start do MCP
compass> mcp status     # Verificar status
compass> mcp actions    # Menu de análises
```

### Desenvolvimento
```bash
# Acessar aplicação web
curl http://localhost:8080

# Conectar no banco
psql -h localhost -U petclinic -d petclinic

# API do MCP
curl http://localhost:8000/health
```

### Troubleshooting
```bash
./manage.sh status      # Status geral
./manage.sh test        # Teste de conectividade
./manage.sh logs-mcp    # Ver logs do MCP
```

## ⚙️ Requisitos

- **Vagrant** + **VirtualBox**
- **5GB RAM** disponível (2GB + 3GB)
- **15GB** espaço em disco
- **Portas**: 5432, 8000, 8080

## 🎊 Resultado Final

**Uma vez configurado**, basta digitar:
```bash
vagrant ssh analyzer
```

E você estará **imediatamente** no prompt MCP, pronto para analisar o PostgreSQL! 🚀

---

**🎯 Zero configuração adicional necessária!** O ambiente está completamente otimizado para análise imediata de bancos de dados PostgreSQL.