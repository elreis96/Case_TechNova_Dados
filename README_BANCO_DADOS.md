# 🗄️ Sistema de Banco de Dados TechNova IoT

Sistema completo para gerenciamento de dados de startups IoT usando SQLite.

## 📋 Visão Geral

Este sistema converte os dados do arquivo Excel `Case_TechNova_Dados.xlsx` em um banco de dados SQLite relacional, permitindo consultas eficientes e análises avançadas.

## 🏗️ Estrutura do Banco de Dados

O banco de dados `technova_iot.db` contém 4 tabelas principais:

### 1. **startups**
Tabela principal com informações das startups.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária (auto-incremento) |
| nome_startup | TEXT | Nome da startup (único) |
| setor | TEXT | Setor de atuação |
| status | TEXT | 'Ativa' ou 'Inativa' |
| score_global | REAL | Média de todas as avaliações |
| score_performance_viabilidade | REAL | Média de Performance + Viabilidade |
| data_cadastro | TIMESTAMP | Data de inserção no banco |

### 2. **avaliacoes_dimensoes**
Avaliações agregadas por dimensão (8 grupos).

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária |
| startup_id | INTEGER | Referência à startup |
| dimensao | TEXT | Nome da dimensão (ex: "Grupo 1 - Performance Técnica") |
| score | REAL | Score da dimensão |

**Dimensões disponíveis:**
- Grupo 1 - Performance Técnica
- Grupo 2 - Viabilidade Econômica
- Grupo 3 - Confiabilidade
- Grupo 4 - Usabilidade
- Grupo 5 - Eficiência Energética
- Grupo 6 - Robustez Física
- Grupo 7 - Conectividade
- Grupo 8 - Sustentabilidade

### 3. **avaliacoes_detalhadas**
Todas as avaliações individuais (critérios 1.1 a 8.5).

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária |
| startup_id | INTEGER | Referência à startup |
| criterio | TEXT | Código do critério (ex: "1.1", "2.3") |
| score | REAL | Nota do critério |

### 4. **estatisticas_setor**
Estatísticas agregadas por setor.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | Chave primária |
| setor | TEXT | Nome do setor (único) |
| total_startups | INTEGER | Total de startups no setor |
| startups_ativas | INTEGER | Quantidade de startups ativas |
| startups_inativas | INTEGER | Quantidade de startups inativas |
| score_medio | REAL | Score médio do setor |
| score_mediano | REAL | Score mediano do setor |
| score_min | REAL | Menor score do setor |
| score_max | REAL | Maior score do setor |
| ultima_atualizacao | TIMESTAMP | Data da última atualização |

## 🚀 Como Usar

### 1. Criar o Banco de Dados

Execute o script principal para criar e popular o banco:

```bash
python criar_banco_dados.py
```

Este script irá:
- ✅ Criar o arquivo `technova_iot.db`
- ✅ Criar todas as tabelas
- ✅ Importar dados do Excel
- ✅ Calcular scores e estatísticas
- ✅ Exibir resumo dos dados importados

### 2. Executar Consultas de Exemplo

Execute o script de consultas para ver exemplos práticos:

```bash
python consultar_banco.py
```

Este script demonstra:
- 📊 Top 10 startups ativas
- 🏆 Melhor startup para investimento
- 📈 Estatísticas por setor
- 🔍 Consultas personalizadas
- 💾 Exportação para CSV

### 3. Usar a Classe TechNovaDatabase

Você pode usar a classe em seus próprios scripts:

```python
from criar_banco_dados import TechNovaDatabase

# Conectar ao banco
db = TechNovaDatabase('technova_iot.db')
db.conectar()

# Listar startups ativas
startups = db.listar_startups_ativas()
print(startups)

# Obter melhor startup
melhor = db.obter_melhor_startup()
print(f"Melhor: {melhor[0]}")

# Consulta personalizada
query = "SELECT * FROM startups WHERE setor = 'Saúde'"
resultado = db.executar_query_personalizada(query)
print(resultado)

# Desconectar
db.desconectar()
```

## 📊 Métodos Disponíveis

### Métodos de Consulta

| Método | Descrição | Retorno |
|--------|-----------|---------|
| `listar_startups_ativas()` | Lista todas as startups ativas ordenadas por score | DataFrame |
| `listar_startups_por_setor(setor)` | Lista startups de um setor específico | DataFrame |
| `obter_melhor_startup()` | Retorna a startup com melhor score | Tupla |
| `obter_estatisticas_setor(setor=None)` | Estatísticas de um ou todos os setores | DataFrame |
| `obter_avaliacoes_dimensoes(nome_startup)` | Avaliações por dimensão de uma startup | DataFrame |
| `executar_query_personalizada(query, params)` | Executa query SQL customizada | DataFrame |

### Métodos de Gerenciamento

| Método | Descrição |
|--------|-----------|
| `conectar()` | Estabelece conexão com o banco |
| `desconectar()` | Fecha conexão com o banco |
| `criar_tabelas()` | Cria estrutura do banco |
| `importar_dados_excel(excel_path)` | Importa dados do Excel |

## 💡 Exemplos de Queries SQL

### Top 5 startups por Performance Técnica

```sql
SELECT s.nome_startup, s.setor, d.score
FROM startups s
JOIN avaliacoes_dimensoes d ON s.id = d.startup_id
WHERE d.dimensao = 'Grupo 1 - Performance Técnica' 
  AND s.status = 'Ativa'
ORDER BY d.score DESC
LIMIT 5;
```

### Startups equilibradas (todas dimensões > 3.5)

```sql
SELECT s.nome_startup, s.setor, s.score_global
FROM startups s
JOIN avaliacoes_dimensoes d ON s.id = d.startup_id
WHERE s.status = 'Ativa'
GROUP BY s.id
HAVING MIN(d.score) > 3.5
ORDER BY s.score_global DESC;
```

### Análise de risco por setor

```sql
SELECT setor,
       COUNT(*) as total,
       SUM(CASE WHEN status = 'Inativa' THEN 1 ELSE 0 END) as inativas,
       ROUND(100.0 * SUM(CASE WHEN status = 'Inativa' THEN 1 ELSE 0 END) / COUNT(*), 2) as percentual_risco
FROM startups
GROUP BY setor
ORDER BY percentual_risco DESC;
```

### Comparação entre setores

```sql
SELECT setor, 
       ROUND(AVG(score_global), 2) as score_medio,
       COUNT(*) as total_startups,
       SUM(CASE WHEN status = 'Ativa' THEN 1 ELSE 0 END) as ativas
FROM startups
GROUP BY setor
ORDER BY score_medio DESC;
```

## 🔧 Ferramentas Recomendadas

Para visualizar e editar o banco de dados graficamente:

1. **DB Browser for SQLite** (gratuito)
   - Download: https://sqlitebrowser.org/
   - Interface gráfica completa
   - Suporta queries, edição e visualização

2. **DBeaver** (gratuito)
   - Download: https://dbeaver.io/
   - Suporta múltiplos bancos de dados
   - Recursos avançados de análise

3. **SQLite Online** (web)
   - URL: https://sqliteonline.com/
   - Não requer instalação
   - Bom para testes rápidos

## 📁 Arquivos do Sistema

```
Case_TechNova_Dados/
├── Case_TechNova_Dados.xlsx          # Arquivo Excel original
├── criar_banco_dados.py              # Script de criação do banco
├── consultar_banco.py                # Script de consultas de exemplo
├── technova_iot.db                   # Banco de dados SQLite
├── README_BANCO_DADOS.md             # Esta documentação
└── requirements.txt                  # Dependências Python
```

## 📦 Dependências

```
pandas
openpyxl
```

Instalar com:
```bash
pip install -r requirements.txt
```

## 🎯 Casos de Uso

### 1. Análise de Investimento
```python
db = TechNovaDatabase()
db.conectar()

# Encontrar melhores oportunidades
melhor = db.obter_melhor_startup()
top_10 = db.listar_startups_ativas().head(10)

# Analisar setor específico
setor_saude = db.listar_startups_por_setor('Saúde')
```

### 2. Relatórios Executivos
```python
# Gerar relatório completo
stats = db.obter_estatisticas_setor()
stats.to_excel('relatorio_setores.xlsx')

# Exportar top performers
top = db.listar_startups_ativas().head(20)
top.to_csv('top_20_startups.csv')
```

### 3. Análise de Risco
```python
query = """
    SELECT setor, 
           100.0 * SUM(CASE WHEN status = 'Inativa' THEN 1 ELSE 0 END) / COUNT(*) as taxa_falha
    FROM startups
    GROUP BY setor
    ORDER BY taxa_falha DESC
"""
risco = db.executar_query_personalizada(query)
```

## 🔄 Atualização dos Dados

Para atualizar o banco com novos dados do Excel:

```python
db = TechNovaDatabase()
db.conectar()

# Recriar tabelas (apaga dados antigos)
db.criar_tabelas()

# Importar novos dados
db.importar_dados_excel('Case_TechNova_Dados.xlsx')

db.desconectar()
```

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique se o arquivo Excel está no mesmo diretório
2. Certifique-se de que as dependências estão instaladas
3. Verifique se o arquivo `technova_iot.db` tem permissões de escrita

## 📝 Notas

- O banco de dados é criado no mesmo diretório dos scripts
- Todas as queries retornam DataFrames do pandas para fácil manipulação
- O sistema preserva a integridade referencial entre tabelas
- Scores são armazenados como REAL (float) com precisão decimal

---

**Desenvolvido para TechNova - Sistema de Análise de Maturidade IoT**
