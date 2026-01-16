# Script Python para Power BI
# Cole este código na opção "Obter Dados" → "Python Script"

import pandas as pd
import sqlite3

# IMPORTANTE: Ajuste o caminho do banco de dados
db_path = r'c:\Users\Eduar\Desktop\Case_TechNova_Dados\technova_iot.db'

# Conectar ao banco
conn = sqlite3.connect(db_path)

# Carregar tabelas
startups = pd.read_sql_query("SELECT * FROM startups", conn)
avaliacoes_dimensoes = pd.read_sql_query("SELECT * FROM avaliacoes_dimensoes", conn)
avaliacoes_detalhadas = pd.read_sql_query("SELECT * FROM avaliacoes_detalhadas", conn)
estatisticas_setor = pd.read_sql_query("SELECT * FROM estatisticas_setor", conn)

# View consolidada
startups_completo = pd.read_sql_query('''
    SELECT 
        s.*,
        MAX(CASE WHEN d.dimensao = 'Grupo 1 - Performance Técnica' THEN d.score END) as performance_tecnica,
        MAX(CASE WHEN d.dimensao = 'Grupo 2 - Viabilidade Econômica' THEN d.score END) as viabilidade_economica,
        MAX(CASE WHEN d.dimensao = 'Grupo 3 - Confiabilidade' THEN d.score END) as confiabilidade,
        MAX(CASE WHEN d.dimensao = 'Grupo 4 - Usabilidade' THEN d.score END) as usabilidade,
        MAX(CASE WHEN d.dimensao = 'Grupo 5 - Eficiência Energética' THEN d.score END) as eficiencia_energetica,
        MAX(CASE WHEN d.dimensao = 'Grupo 6 - Robustez Física' THEN d.score END) as robustez_fisica,
        MAX(CASE WHEN d.dimensao = 'Grupo 7 - Conectividade' THEN d.score END) as conectividade,
        MAX(CASE WHEN d.dimensao = 'Grupo 8 - Sustentabilidade' THEN d.score END) as sustentabilidade
    FROM startups s
    LEFT JOIN avaliacoes_dimensoes d ON s.id = d.startup_id
    GROUP BY s.id
''', conn)

conn.close()

# As tabelas estarão disponíveis para seleção no Power BI
