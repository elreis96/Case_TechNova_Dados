"""
Visualizador de Banco de Dados - TechNova
Interface simples para explorar o banco de dados SQLite

Autor: Sistema TechNova
Data: 2026-01-16
"""

import sqlite3
import pandas as pd
from pathlib import Path

def exibir_menu():
    """Exibe menu principal"""
    print("\n" + "=" * 80)
    print("VISUALIZADOR DE BANCO DE DADOS - TECHNOVA IoT")
    print("=" * 80)
    print("\n📋 OPÇÕES:")
    print("  1. Ver todas as tabelas")
    print("  2. Ver estrutura de uma tabela")
    print("  3. Listar startups ativas")
    print("  4. Listar startups inativas")
    print("  5. Buscar startup por nome")
    print("  6. Ver estatísticas por setor")
    print("  7. Ver top 10 startups")
    print("  8. Ver detalhes de uma startup")
    print("  9. Executar query personalizada")
    print("  0. Sair")
    print("-" * 80)

def listar_tabelas(conn):
    """Lista todas as tabelas do banco"""
    query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    tabelas = pd.read_sql_query(query, conn)
    print("\n📊 TABELAS NO BANCO DE DADOS:")
    for i, tabela in enumerate(tabelas['name'], 1):
        print(f"  {i}. {tabela}")

def ver_estrutura_tabela(conn, nome_tabela):
    """Mostra a estrutura de uma tabela"""
    query = f"PRAGMA table_info({nome_tabela})"
    estrutura = pd.read_sql_query(query, conn)
    print(f"\n🏗️ ESTRUTURA DA TABELA '{nome_tabela}':")
    print(estrutura[['name', 'type', 'notnull', 'pk']].to_string(index=False))
    
    # Contar registros
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
    total = cursor.fetchone()[0]
    print(f"\n📈 Total de registros: {total}")

def listar_startups_por_status(conn, status):
    """Lista startups por status"""
    query = f"""
        SELECT nome_startup, setor, score_global, score_performance_viabilidade
        FROM startups
        WHERE status = '{status}'
        ORDER BY score_global DESC
    """
    resultado = pd.read_sql_query(query, conn)
    print(f"\n🏢 STARTUPS {status.upper()}S ({len(resultado)}):")
    if not resultado.empty:
        print(resultado.to_string(index=False))
    else:
        print("  Nenhuma startup encontrada")

def buscar_startup(conn, nome):
    """Busca startup por nome (parcial)"""
    query = f"""
        SELECT nome_startup, setor, status, score_global, score_performance_viabilidade
        FROM startups
        WHERE nome_startup LIKE '%{nome}%'
    """
    resultado = pd.read_sql_query(query, conn)
    print(f"\n🔍 RESULTADOS DA BUSCA por '{nome}':")
    if not resultado.empty:
        print(resultado.to_string(index=False))
    else:
        print("  Nenhuma startup encontrada")

def ver_estatisticas_setor(conn):
    """Mostra estatísticas por setor"""
    query = """
        SELECT setor, total_startups, startups_ativas, startups_inativas,
               ROUND(score_medio, 2) as score_medio,
               ROUND(score_min, 2) as score_min,
               ROUND(score_max, 2) as score_max
        FROM estatisticas_setor
        ORDER BY score_medio DESC
    """
    resultado = pd.read_sql_query(query, conn)
    print("\n📊 ESTATÍSTICAS POR SETOR:")
    print(resultado.to_string(index=False))

def ver_top_startups(conn, limite=10):
    """Mostra top N startups"""
    query = f"""
        SELECT nome_startup, setor, 
               ROUND(score_global, 2) as score_global,
               ROUND(score_performance_viabilidade, 2) as perf_viab
        FROM startups
        WHERE status = 'Ativa'
        ORDER BY score_performance_viabilidade DESC
        LIMIT {limite}
    """
    resultado = pd.read_sql_query(query, conn)
    print(f"\n🏆 TOP {limite} STARTUPS:")
    for i, row in enumerate(resultado.itertuples(), 1):
        print(f"  {i:2d}. {row.nome_startup:30s} | {row.setor:15s} | Score: {row.perf_viab:.2f}")

def ver_detalhes_startup(conn, nome):
    """Mostra detalhes completos de uma startup"""
    # Informações básicas
    query_basico = f"""
        SELECT * FROM startups WHERE nome_startup = '{nome}'
    """
    cursor = conn.cursor()
    cursor.execute(query_basico)
    startup = cursor.fetchone()
    
    if not startup:
        print(f"\n✗ Startup '{nome}' não encontrada")
        return
    
    print(f"\n" + "=" * 80)
    print(f"DETALHES DA STARTUP: {nome}")
    print("=" * 80)
    print(f"Setor: {startup[2]}")
    print(f"Status: {startup[3]}")
    print(f"Score Global: {startup[4]:.2f}")
    print(f"Score Performance + Viabilidade: {startup[5]:.2f}")
    
    # Avaliações por dimensão
    query_dimensoes = f"""
        SELECT d.dimensao, ROUND(d.score, 2) as score
        FROM avaliacoes_dimensoes d
        JOIN startups s ON d.startup_id = s.id
        WHERE s.nome_startup = '{nome}'
        ORDER BY d.dimensao
    """
    dimensoes = pd.read_sql_query(query_dimensoes, conn)
    print("\n📊 AVALIAÇÕES POR DIMENSÃO:")
    print(dimensoes.to_string(index=False))
    
    # Top 5 e Bottom 5 critérios
    query_criterios = f"""
        SELECT a.criterio, ROUND(a.score, 2) as score
        FROM avaliacoes_detalhadas a
        JOIN startups s ON a.startup_id = s.id
        WHERE s.nome_startup = '{nome}'
        ORDER BY a.score DESC
    """
    criterios = pd.read_sql_query(query_criterios, conn)
    
    print("\n✅ TOP 5 CRITÉRIOS:")
    print(criterios.head(5).to_string(index=False))
    
    print("\n⚠️ BOTTOM 5 CRITÉRIOS:")
    print(criterios.tail(5).to_string(index=False))

def executar_query_custom(conn):
    """Permite executar query personalizada"""
    print("\n" + "=" * 80)
    print("EXECUTAR QUERY PERSONALIZADA")
    print("=" * 80)
    print("Digite sua query SQL (ou 'voltar' para cancelar):")
    print("Exemplo: SELECT * FROM startups WHERE setor = 'Saúde' LIMIT 5")
    print("-" * 80)
    
    query = input("\nSQL> ").strip()
    
    if query.lower() == 'voltar':
        return
    
    try:
        resultado = pd.read_sql_query(query, conn)
        print("\n📊 RESULTADO:")
        print(resultado.to_string(index=False))
        print(f"\n✓ {len(resultado)} registros retornados")
    except Exception as e:
        print(f"\n✗ Erro ao executar query: {e}")

def main():
    """Função principal"""
    db_path = 'technova_iot.db'
    
    # Verificar se banco existe
    if not Path(db_path).exists():
        print(f"✗ Banco de dados não encontrado: {db_path}")
        print("Execute primeiro: python criar_banco_dados.py")
        return
    
    # Conectar ao banco
    conn = sqlite3.connect(db_path)
    print(f"✓ Conectado ao banco: {db_path}")
    
    while True:
        exibir_menu()
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == '1':
            listar_tabelas(conn)
        
        elif opcao == '2':
            tabela = input("\nNome da tabela: ").strip()
            ver_estrutura_tabela(conn, tabela)
        
        elif opcao == '3':
            listar_startups_por_status(conn, 'Ativa')
        
        elif opcao == '4':
            listar_startups_por_status(conn, 'Inativa')
        
        elif opcao == '5':
            nome = input("\nDigite parte do nome da startup: ").strip()
            buscar_startup(conn, nome)
        
        elif opcao == '6':
            ver_estatisticas_setor(conn)
        
        elif opcao == '7':
            try:
                n = int(input("\nQuantas startups mostrar? (padrão: 10): ").strip() or "10")
                ver_top_startups(conn, n)
            except ValueError:
                ver_top_startups(conn)
        
        elif opcao == '8':
            nome = input("\nNome exato da startup: ").strip()
            ver_detalhes_startup(conn, nome)
        
        elif opcao == '9':
            executar_query_custom(conn)
        
        elif opcao == '0':
            print("\n✓ Encerrando...")
            break
        
        else:
            print("\n✗ Opção inválida!")
        
        input("\nPressione ENTER para continuar...")
    
    conn.close()
    print("✓ Conexão fechada")

if __name__ == "__main__":
    main()
