"""
Modelos de prompts prontos para usar o PostgreSQL Performance Analyzer
"""

MODELS = {
    "1": {
        "name": "📋 Listar Todas as Tabelas",
        "description": "Mostra todas as tabelas do banco com informações básicas",
        "tool": "execute_read_only_query",
        "query": """
            SELECT 
                table_name,
                table_type,
                (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """,
        "example_result": "Lista com nomes das tabelas, tipos e número de colunas"
    },
    
    "2": {
        "name": "👥 Contar Registros de Todas as Tabelas",
        "description": "Conta quantos registros cada tabela possui",
        "tool": "execute_read_only_query", 
        "query": """
            SELECT 
                'owners' as table_name, COUNT(*) as total_records FROM owners
            UNION ALL
            SELECT 'pets' as table_name, COUNT(*) as total_records FROM pets
            UNION ALL  
            SELECT 'vets' as table_name, COUNT(*) as total_records FROM vets
            UNION ALL
            SELECT 'visits' as table_name, COUNT(*) as total_records FROM visits
            UNION ALL
            SELECT 'types' as table_name, COUNT(*) as total_records FROM types
            UNION ALL
            SELECT 'specialties' as table_name, COUNT(*) as total_records FROM specialties
            ORDER BY total_records DESC;
        """,
        "example_result": "Tabela com nome e quantidade de registros"
    },
    
    "3": {
        "name": "🔍 Análise Completa da Estrutura do Banco",
        "description": "Análise detalhada de todas as tabelas, índices e relacionamentos",
        "tool": "analyze_database_structure",
        "query": None,
        "example_result": "Relatório completo com recomendações de otimização"
    },
    
    "4": {
        "name": "📊 Estatísticas dos Proprietários por Cidade",
        "description": "Mostra quantos proprietários existem em cada cidade",
        "tool": "execute_read_only_query",
        "query": """
            SELECT 
                city,
                COUNT(*) as total_owners,
                COUNT(DISTINCT last_name) as unique_surnames
            FROM owners 
            GROUP BY city 
            ORDER BY total_owners DESC;
        """,
        "example_result": "Ranking de cidades com mais proprietários"
    },
    
    "5": {
        "name": "🐕 Pets e Seus Donos",
        "description": "Lista todos os pets com informações dos proprietários",
        "tool": "execute_read_only_query",
        "query": """
            SELECT 
                p.name as pet_name,
                t.name as pet_type,
                p.birth_date,
                o.first_name || ' ' || o.last_name as owner_name,
                o.city,
                o.telephone
            FROM pets p
            JOIN types t ON p.type_id = t.id
            JOIN owners o ON p.owner_id = o.id
            ORDER BY o.last_name, p.name;
        """,
        "example_result": "Lista detalhada de pets com dados dos donos"
    },
    
    "6": {
        "name": "🏥 Veterinários e Especialidades",
        "description": "Mostra veterinários com suas especialidades",
        "tool": "execute_read_only_query",
        "query": """
            SELECT 
                v.first_name || ' ' || v.last_name as vet_name,
                STRING_AGG(s.name, ', ') as specialties
            FROM vets v
            LEFT JOIN vet_specialties vs ON v.id = vs.vet_id
            LEFT JOIN specialties s ON vs.specialty_id = s.id
            GROUP BY v.id, v.first_name, v.last_name
            ORDER BY v.last_name;
        """,
        "example_result": "Lista de veterinários com suas especialidades"
    },
    
    "7": {
        "name": "🔎 Analisar Query Específica",
        "description": "Analisa o plano de execução de uma query personalizada",
        "tool": "analyze_query",
        "query": "SELECT * FROM owners WHERE city = 'Madison'",
        "example_result": "Plano de execução detalhado com recomendações",
        "note": "Você pode modificar a query para analisar"
    },
    
    "8": {
        "name": "💡 Recomendar Índices",
        "description": "Sugere índices para melhorar performance",
        "tool": "recommend_indexes", 
        "query": "SELECT * FROM owners WHERE city = 'Madison' AND last_name = 'Davis'",
        "example_result": "Sugestões de índices para otimização",
        "note": "Personalize a query conforme necessário"
    },
    
    "9": {
        "name": "⚙️ Configurações do PostgreSQL",
        "description": "Mostra configurações importantes do banco",
        "tool": "show_postgresql_settings",
        "pattern": "max_connections|shared_buffers|work_mem",
        "example_result": "Configurações de memória e conexões"
    },
    
    "10": {
        "name": "📈 Visitas por Pet",
        "description": "Estatísticas de visitas veterinárias",
        "tool": "execute_read_only_query",
        "query": """
            SELECT 
                p.name as pet_name,
                t.name as pet_type,
                o.first_name || ' ' || o.last_name as owner_name,
                COUNT(v.id) as total_visits,
                MAX(v.visit_date) as last_visit
            FROM pets p
            JOIN types t ON p.type_id = t.id
            JOIN owners o ON p.owner_id = o.id
            LEFT JOIN visits v ON p.id = v.pet_id
            GROUP BY p.id, p.name, t.name, o.first_name, o.last_name
            ORDER BY total_visits DESC, p.name;
        """,
        "example_result": "Ranking de pets com mais visitas veterinárias"
    }
}

def get_model_list():
    """Retorna lista formatada dos modelos disponíveis"""
    result = "\n🤖 MODELOS DISPONÍVEIS - PostgreSQL Performance Analyzer\n"
    result += "=" * 65 + "\n\n"
    
    for key, model in MODELS.items():
        result += f"{key:2}. {model['name']}\n"
        result += f"    📝 {model['description']}\n"
        if model.get('note'):
            result += f"    💡 {model['note']}\n"
        result += "\n"
    
    result += "💻 Como usar:\n"
    result += "   - Digite o número do modelo desejado\n"
    result += "   - Use 'curl' para executar via terminal\n"
    result += "   - Conecte via cliente MCP\n\n"
    
    return result

def get_model_by_id(model_id):
    """Retorna modelo específico por ID"""
    return MODELS.get(str(model_id))

def get_model_curl_command(model_id, host="localhost", port=5432, dbname="petclinic", username="petclinic", password="petclinic"):
    """Gera comando curl para executar o modelo"""
    model = get_model_by_id(model_id)
    if not model:
        return None
    
    base_params = {
        "host": host,
        "port": port, 
        "dbname": dbname,
        "username": username,
        "password": password
    }
    
    if model["tool"] == "execute_read_only_query":
        params = {**base_params, "query": model["query"].strip()}
    elif model["tool"] == "analyze_database_structure":
        params = base_params
    elif model["tool"] == "analyze_query":
        params = {**base_params, "query": model["query"]}
    elif model["tool"] == "recommend_indexes":
        params = {**base_params, "query": model["query"]}
    elif model["tool"] == "show_postgresql_settings":
        params = {**base_params, "pattern": model.get("pattern", "")}
    else:
        params = base_params
    
    return {
        "tool": model["tool"],
        "params": params,
        "description": model["description"]
    }