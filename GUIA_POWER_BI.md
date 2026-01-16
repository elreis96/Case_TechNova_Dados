# 📊 Guia de Integração com Power BI

## 🎯 Visão Geral

O banco de dados SQLite `technova_iot.db` pode ser facilmente integrado ao **Power BI Desktop** para criar dashboards interativos e análises visuais avançadas.

## 🔌 Métodos de Conexão

### Método 1: Conexão Direta ao SQLite (Recomendado)

#### Passo 1: Instalar Driver ODBC (se necessário)

1. Baixe o driver SQLite ODBC:
   - **Windows 64-bit**: http://www.ch-werner.de/sqliteodbc/
   - Baixe `sqliteodbc_w64.exe`

2. Execute o instalador
3. Confirme a instalação

#### Passo 2: Conectar no Power BI

1. Abra o **Power BI Desktop**
2. Clique em **Obter Dados** (Get Data)
3. Procure por **"ODBC"** ou **"Database" → "SQLite"**
4. Selecione **ODBC** ou **SQLite Database**
5. Clique em **Conectar**

**Para ODBC:**
- DSN: Criar novo DSN apontando para `technova_iot.db`
- Ou usar string de conexão direta

**Para SQLite direto:**
- Navegue até: `c:\Users\Eduar\Desktop\Case_TechNova_Dados\technova_iot.db`
- Clique em **OK**

6. Selecione as tabelas desejadas:
   - ✅ `startups`
   - ✅ `avaliacoes_dimensoes`
   - ✅ `avaliacoes_detalhadas`
   - ✅ `estatisticas_setor`

7. Clique em **Carregar** ou **Transformar Dados**

### Método 2: Importar via CSV (Alternativa Simples)

Se tiver problemas com a conexão direta, use os CSVs:

1. Execute o script de exportação:
```bash
python exportar_para_powerbi.py
```

2. No Power BI:
   - **Obter Dados** → **Texto/CSV**
   - Selecione os arquivos CSV gerados
   - Clique em **Carregar**

### Método 3: Usar Python no Power BI

1. No Power BI, vá em **Obter Dados** → **Mais** → **Python Script**

2. Cole o script:
```python
import pandas as pd
import sqlite3

# Conectar ao banco
conn = sqlite3.connect(r'c:\Users\Eduar\Desktop\Case_TechNova_Dados\technova_iot.db')

# Carregar tabelas
startups = pd.read_sql_query("SELECT * FROM startups", conn)
avaliacoes_dimensoes = pd.read_sql_query("SELECT * FROM avaliacoes_dimensoes", conn)
estatisticas_setor = pd.read_sql_query("SELECT * FROM estatisticas_setor", conn)

conn.close()
```

3. Clique em **OK**
4. Selecione as tabelas que aparecerão
5. Clique em **Carregar**

## 📊 Estrutura de Dados no Power BI

### Tabelas Principais

#### 1. **startups** (Fato Principal)
```
id (INT) - Chave Primária
nome_startup (TEXT)
setor (TEXT)
status (TEXT)
score_global (DECIMAL)
score_performance_viabilidade (DECIMAL)
data_cadastro (DATETIME)
```

#### 2. **avaliacoes_dimensoes** (Fato Detalhado)
```
id (INT) - Chave Primária
startup_id (INT) - Chave Estrangeira → startups.id
dimensao (TEXT)
score (DECIMAL)
```

#### 3. **avaliacoes_detalhadas** (Granular)
```
id (INT) - Chave Primária
startup_id (INT) - Chave Estrangeira → startups.id
criterio (TEXT)
score (DECIMAL)
```

#### 4. **estatisticas_setor** (Agregado)
```
id (INT) - Chave Primária
setor (TEXT)
total_startups (INT)
startups_ativas (INT)
startups_inativas (INT)
score_medio (DECIMAL)
score_mediano (DECIMAL)
score_min (DECIMAL)
score_max (DECIMAL)
ultima_atualizacao (DATETIME)
```

## 🔗 Relacionamentos no Power BI

Configure os relacionamentos entre tabelas:

```
startups (1) ←→ (N) avaliacoes_dimensoes
  Chave: id ←→ startup_id
  Cardinalidade: Um para Muitos
  Direção do Filtro: Ambas

startups (1) ←→ (N) avaliacoes_detalhadas
  Chave: id ←→ startup_id
  Cardinalidade: Um para Muitos
  Direção do Filtro: Ambas

startups (N) ←→ (1) estatisticas_setor
  Chave: setor ←→ setor
  Cardinalidade: Muitos para Um
  Direção do Filtro: Ambas
```

## 📈 Medidas DAX Sugeridas

### Medidas Básicas

```dax
// Total de Startups
Total Startups = COUNTROWS(startups)

// Startups Ativas
Startups Ativas = 
CALCULATE(
    COUNTROWS(startups),
    startups[status] = "Ativa"
)

// Startups Inativas
Startups Inativas = 
CALCULATE(
    COUNTROWS(startups),
    startups[status] = "Inativa"
)

// Taxa de Sucesso
Taxa de Sucesso = 
DIVIDE(
    [Startups Ativas],
    [Total Startups],
    0
)

// Score Médio Global
Score Médio = AVERAGE(startups[score_global])

// Score Médio Performance + Viabilidade
Score Perf+Viab = AVERAGE(startups[score_performance_viabilidade])
```

### Medidas Avançadas

```dax
// Top Startup (Nome)
Top Startup = 
CALCULATE(
    FIRSTNONBLANK(startups[nome_startup], 1),
    TOPN(
        1,
        FILTER(startups, startups[status] = "Ativa"),
        startups[score_performance_viabilidade],
        DESC
    )
)

// Score da Melhor Startup
Score Top Startup = 
CALCULATE(
    MAX(startups[score_performance_viabilidade]),
    startups[status] = "Ativa"
)

// Ranking de Startups
Ranking Startup = 
RANKX(
    FILTER(startups, startups[status] = "Ativa"),
    startups[score_performance_viabilidade],
    ,
    DESC,
    DENSE
)

// Score por Dimensão (Média)
Score Dimensão = AVERAGE(avaliacoes_dimensoes[score])

// Percentual do Setor
% do Setor = 
DIVIDE(
    COUNTROWS(startups),
    CALCULATE(COUNTROWS(startups), ALL(startups[setor])),
    0
)

// Variação vs Média do Setor
Variação vs Setor = 
VAR ScoreStartup = AVERAGE(startups[score_global])
VAR MediaSetor = 
    CALCULATE(
        AVERAGE(startups[score_global]),
        ALLEXCEPT(startups, startups[setor])
    )
RETURN
    ScoreStartup - MediaSetor
```

## 🎨 Visualizações Recomendadas

### Dashboard Principal

#### 1. **KPIs (Cartões)**
- Total de Startups
- Startups Ativas
- Taxa de Sucesso
- Score Médio Global
- Melhor Startup (nome + score)

#### 2. **Gráfico de Barras**
- **Eixo X**: Setor
- **Eixo Y**: Total de Startups
- **Legenda**: Status (Ativa/Inativa)
- **Cores**: Verde (Ativa), Vermelho (Inativa)

#### 3. **Gráfico de Pizza/Donut**
- **Valores**: Total de Startups
- **Legenda**: Setor
- **Título**: "Distribuição por Setor"

#### 4. **Gráfico de Dispersão**
- **Eixo X**: Grupo 1 - Performance Técnica
- **Eixo Y**: Grupo 2 - Viabilidade Econômica
- **Legenda**: Setor
- **Tamanho**: Score Global
- **Filtro**: Status = "Ativa"

#### 5. **Gráfico de Radar** (Visual Customizado)
- Instale o visual "Radar Chart" da galeria
- **Categoria**: Dimensão
- **Valores**: Score
- **Filtro**: Selecionar startup específica

#### 6. **Tabela Detalhada**
- Nome da Startup
- Setor
- Status
- Score Global
- Score Performance + Viabilidade
- Ranking

#### 7. **Mapa de Calor (Matrix)**
- **Linhas**: Nome da Startup
- **Colunas**: Dimensão
- **Valores**: Score
- **Formatação Condicional**: Escala de cores

#### 8. **Gráfico de Funil**
- **Valores**: Score por Dimensão
- **Categoria**: Nome da Dimensão
- **Filtro**: Top 5 Startups

### Dashboard de Análise Setorial

#### 1. **Tabela de Estatísticas**
- Setor
- Total de Startups
- Startups Ativas
- Score Médio
- Score Mínimo
- Score Máximo

#### 2. **Boxplot por Setor**
- Instale visual "Box and Whisker" da galeria
- **Categoria**: Setor
- **Valores**: Score Global

#### 3. **Gráfico de Linhas**
- **Eixo X**: Setor
- **Eixo Y**: Score Médio, Score Mínimo, Score Máximo
- **Linhas**: 3 séries diferentes

## 🔄 Atualização de Dados

### Atualização Manual

1. Execute o script Python para atualizar o banco:
```bash
python criar_banco_dados.py
```

2. No Power BI, clique em **Atualizar** na faixa de opções

### Atualização Automática (Power BI Service)

1. Publique o relatório no Power BI Service
2. Configure o **Gateway de Dados Local**
3. Configure a atualização agendada:
   - Frequência: Diária/Semanal
   - Horário: Definir conforme necessidade

## 📝 Script de Exportação para Power BI

Criei um script para facilitar a exportação:

```python
# Ver arquivo: exportar_para_powerbi.py
```

Execute:
```bash
python exportar_para_powerbi.py
```

Isso gerará:
- ✅ `powerbi_startups.csv`
- ✅ `powerbi_avaliacoes_dimensoes.csv`
- ✅ `powerbi_avaliacoes_detalhadas.csv`
- ✅ `powerbi_estatisticas_setor.csv`

## 🎯 Exemplo de Dashboard

### Layout Sugerido

```
┌─────────────────────────────────────────────────────────┐
│  ANÁLISE DE MATURIDADE IoT - TECHNOVA                   │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│ Total    │ Ativas   │ Inativas │ Taxa     │ Score Médio │
│ 50       │ 35       │ 15       │ 70%      │ 3.45        │
├──────────┴──────────┴──────────┴──────────┴─────────────┤
│                                                          │
│  📊 Distribuição por Setor    📈 Performance vs Viab.   │
│  [Gráfico de Barras]           [Scatter Plot]           │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  🎯 Radar - Melhor Startup     📋 Top 10 Startups       │
│  [Gráfico de Radar]            [Tabela]                 │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  Filtros: Setor | Status | Dimensão                     │
└──────────────────────────────────────────────────────────┘
```

## 🛠️ Troubleshooting

### Problema: Não consigo conectar ao SQLite

**Solução 1**: Use o método CSV
```bash
python exportar_para_powerbi.py
```

**Solução 2**: Instale o driver ODBC correto
- Verifique se instalou a versão 64-bit
- Reinicie o Power BI Desktop

**Solução 3**: Use Python Script no Power BI
- Certifique-se de ter Python configurado
- Instale pandas: `pip install pandas`

### Problema: Relacionamentos não funcionam

**Solução**: Verifique os tipos de dados
- `startup_id` deve ser INT em ambas as tabelas
- `setor` deve ser TEXT em ambas as tabelas
- Use "Gerenciar Relacionamentos" para criar manualmente

### Problema: Medidas DAX com erro

**Solução**: Verifique os nomes das colunas
- Use `startups[score_global]` e não `startups.score_global`
- Nomes de tabelas e colunas são case-sensitive

## 📚 Recursos Adicionais

### Visuais Customizados Recomendados

1. **Radar Chart** - Para análise multidimensional
2. **Box and Whisker** - Para boxplots
3. **Chiclet Slicer** - Para filtros visuais
4. **Advanced Card** - Para KPIs estilizados
5. **Table Heatmap** - Para mapas de calor

### Templates de Dashboard

Você pode criar templates reutilizáveis:
1. Configure o dashboard uma vez
2. Salve como `.pbit` (Power BI Template)
3. Reutilize com novos dados

## 🎓 Próximos Passos

1. ✅ Conectar ao banco de dados
2. ✅ Configurar relacionamentos
3. ✅ Criar medidas DAX
4. ✅ Desenvolver visualizações
5. ✅ Publicar no Power BI Service
6. ✅ Configurar atualização automática

---

**Desenvolvido para TechNova - Integração Power BI**

*Para dúvidas, consulte a documentação do Power BI: https://docs.microsoft.com/power-bi/*
