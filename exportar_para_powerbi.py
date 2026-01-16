"""
Exportador de Dados para Power BI - TechNova
Exporta dados do SQLite para formatos compatíveis com Power BI

Autor: Sistema TechNova
Data: 2026-01-16
"""

import pandas as pd
import sqlite3
from pathlib import Path

def exportar_para_powerbi(db_path='technova_iot.db', output_dir='powerbi_export'):
    """
    Exporta todas as tabelas do banco SQLite para CSV otimizado para Power BI
    
    Args:
        db_path: Caminho para o banco de dados SQLite
        output_dir: Diretório de saída para os arquivos CSV
    """
    print("=" * 80)
    print("EXPORTAÇÃO DE DADOS PARA POWER BI")
    print("=" * 80)
    
    # Verificar se banco existe
    if not Path(db_path).exists():
        print(f"✗ Banco de dados não encontrado: {db_path}")
        return False
    
    # Criar diretório de saída
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    print(f"✓ Diretório de saída: {output_path.absolute()}")
    
    # Conectar ao banco
    conn = sqlite3.connect(db_path)
    print(f"✓ Conectado ao banco: {db_path}")
    
    # Lista de tabelas para exportar
    tabelas = {
        'startups': 'Dados principais das startups',
        'avaliacoes_dimensoes': 'Avaliações por dimensão (8 grupos)',
        'avaliacoes_detalhadas': 'Avaliações detalhadas por critério',
        'estatisticas_setor': 'Estatísticas agregadas por setor'
    }
    
    print("\n📊 EXPORTANDO TABELAS...")
    print("-" * 80)
    
    arquivos_gerados = []
    
    for tabela, descricao in tabelas.items():
        try:
            # Ler dados da tabela
            df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)
            
            # Nome do arquivo de saída
            arquivo_csv = output_path / f"powerbi_{tabela}.csv"
            
            # Exportar para CSV
            # UTF-8 com BOM para compatibilidade com Power BI
            df.to_csv(
                arquivo_csv, 
                index=False, 
                encoding='utf-8-sig',
                date_format='%Y-%m-%d %H:%M:%S'
            )
            
            arquivos_gerados.append(arquivo_csv)
            
            print(f"✓ {tabela:25s} → {arquivo_csv.name:30s} ({len(df):4d} registros)")
            
        except Exception as e:
            print(f"✗ Erro ao exportar {tabela}: {e}")
    
    # Criar arquivo de view consolidada para análise rápida
    print("\n📈 CRIANDO VIEWS CONSOLIDADAS...")
    print("-" * 80)
    
    # View 1: Startups com todas as dimensões (formato largo)
    query_wide = """
    SELECT 
        s.id,
        s.nome_startup,
        s.setor,
        s.status,
        s.score_global,
        s.score_performance_viabilidade,
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
    GROUP BY s.id, s.nome_startup, s.setor, s.status, s.score_global, s.score_performance_viabilidade
    """
    
    df_wide = pd.read_sql_query(query_wide, conn)
    arquivo_wide = output_path / "powerbi_startups_completo.csv"
    df_wide.to_csv(arquivo_wide, index=False, encoding='utf-8-sig')
    arquivos_gerados.append(arquivo_wide)
    print(f"✓ View Consolidada (Largo)  → {arquivo_wide.name:30s} ({len(df_wide):4d} registros)")
    
    # View 2: Análise por setor com métricas
    query_setor = """
    SELECT 
        s.setor,
        s.status,
        COUNT(*) as quantidade,
        ROUND(AVG(s.score_global), 2) as score_medio,
        ROUND(MIN(s.score_global), 2) as score_min,
        ROUND(MAX(s.score_global), 2) as score_max,
        ROUND(AVG(s.score_performance_viabilidade), 2) as perf_viab_medio
    FROM startups s
    GROUP BY s.setor, s.status
    """
    
    df_setor = pd.read_sql_query(query_setor, conn)
    arquivo_setor = output_path / "powerbi_analise_setor.csv"
    df_setor.to_csv(arquivo_setor, index=False, encoding='utf-8-sig')
    arquivos_gerados.append(arquivo_setor)
    print(f"✓ Análise por Setor          → {arquivo_setor.name:30s} ({len(df_setor):4d} registros)")
    
    # View 3: Ranking de startups
    query_ranking = """
    SELECT 
        s.nome_startup,
        s.setor,
        s.status,
        s.score_global,
        s.score_performance_viabilidade,
        RANK() OVER (ORDER BY s.score_performance_viabilidade DESC) as ranking_geral,
        RANK() OVER (PARTITION BY s.setor ORDER BY s.score_performance_viabilidade DESC) as ranking_setor
    FROM startups s
    WHERE s.status = 'Ativa'
    ORDER BY s.score_performance_viabilidade DESC
    """
    
    df_ranking = pd.read_sql_query(query_ranking, conn)
    arquivo_ranking = output_path / "powerbi_ranking_startups.csv"
    df_ranking.to_csv(arquivo_ranking, index=False, encoding='utf-8-sig')
    arquivos_gerados.append(arquivo_ranking)
    print(f"✓ Ranking de Startups        → {arquivo_ranking.name:30s} ({len(df_ranking):4d} registros)")
    
    # Fechar conexão
    conn.close()
    
    # Resumo
    print("\n" + "=" * 80)
    print("✓ EXPORTAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    print(f"\n📁 Arquivos gerados ({len(arquivos_gerados)}):")
    for arquivo in arquivos_gerados:
        tamanho_kb = arquivo.stat().st_size / 1024
        print(f"   • {arquivo.name:35s} ({tamanho_kb:6.1f} KB)")
    
    print(f"\n📂 Localização: {output_path.absolute()}")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("   1. Abra o Power BI Desktop")
    print("   2. Clique em 'Obter Dados' → 'Texto/CSV'")
    print(f"   3. Navegue até: {output_path.absolute()}")
    print("   4. Selecione os arquivos CSV desejados")
    print("   5. Configure os relacionamentos entre tabelas")
    print("   6. Comece a criar visualizações!")
    
    print("\n📚 Consulte o GUIA_POWER_BI.md para instruções detalhadas")
    print("=" * 80)
    
    return True


def criar_arquivo_conexao_python():
    """Cria arquivo Python para usar no Power BI"""
    script_content = """# Script Python para Power BI
# Cole este código na opção "Obter Dados" → "Python Script"

import pandas as pd
import sqlite3

# IMPORTANTE: Ajuste o caminho do banco de dados
db_path = r'c:\\Users\\Eduar\\Desktop\\Case_TechNova_Dados\\technova_iot.db'

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
"""
    
    with open('powerbi_export/script_conexao_powerbi.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✓ Arquivo de script Python criado: powerbi_export/script_conexao_powerbi.py")


if __name__ == "__main__":
    # Executar exportação
    sucesso = exportar_para_powerbi()
    
    if sucesso:
        # Criar script de conexão Python
        criar_arquivo_conexao_python()
