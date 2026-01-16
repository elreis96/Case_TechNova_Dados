"""
Interface de Consulta - Banco de Dados TechNova
Exemplos de consultas e análises usando o banco de dados SQLite

Autor: Sistema TechNova
Data: 2026-01-16
"""

from criar_banco_dados import TechNovaDatabase
import pandas as pd

def exemplo_consultas():
    """Demonstra diferentes tipos de consultas ao banco de dados"""
    
    # Conectar ao banco
    db = TechNovaDatabase('technova_iot.db')
    db.conectar()
    
    print("=" * 80)
    print("EXEMPLOS DE CONSULTAS - BANCO DE DADOS TECHNOVA")
    print("=" * 80)
    
    # 1. Listar todas as startups ativas
    print("\n1️⃣ TOP 10 STARTUPS ATIVAS (por Performance + Viabilidade)")
    print("-" * 80)
    startups_ativas = db.listar_startups_ativas().head(10)
    print(startups_ativas.to_string(index=False))
    
    # 2. Melhor startup
    print("\n2️⃣ MELHOR STARTUP PARA INVESTIMENTO")
    print("-" * 80)
    melhor = db.obter_melhor_startup()
    if melhor:
        print(f"Nome: {melhor[0]}")
        print(f"Setor: {melhor[1]}")
        print(f"Score Global: {melhor[2]:.2f}")
        print(f"Score Performance + Viabilidade: {melhor[3]:.2f}")
        print(f"\nAvaliações por Dimensão:")
        print(melhor[4])
    
    # 3. Estatísticas por setor
    print("\n3️⃣ ESTATÍSTICAS POR SETOR")
    print("-" * 80)
    stats = db.obter_estatisticas_setor()
    print(stats[['setor', 'total_startups', 'startups_ativas', 'score_medio']].to_string(index=False))
    
    # 4. Startups de um setor específico
    print("\n4️⃣ STARTUPS DO SETOR 'Saúde'")
    print("-" * 80)
    startups_saude = db.listar_startups_por_setor('Saúde')
    if not startups_saude.empty:
        print(startups_saude.to_string(index=False))
    else:
        print("Nenhuma startup encontrada neste setor")
    
    # 5. Query personalizada - Top 5 por dimensão específica
    print("\n5️⃣ TOP 5 STARTUPS EM PERFORMANCE TÉCNICA")
    print("-" * 80)
    query = '''
        SELECT s.nome_startup, s.setor, d.score as performance_tecnica
        FROM startups s
        JOIN avaliacoes_dimensoes d ON s.id = d.startup_id
        WHERE d.dimensao = 'Grupo 1 - Performance Técnica' AND s.status = 'Ativa'
        ORDER BY d.score DESC
        LIMIT 5
    '''
    top_performance = db.executar_query_personalizada(query)
    print(top_performance.to_string(index=False))
    
    # 6. Comparação entre setores
    print("\n6️⃣ COMPARAÇÃO DE SCORES MÉDIOS POR SETOR")
    print("-" * 80)
    query = '''
        SELECT setor, 
               ROUND(AVG(score_global), 2) as score_medio,
               COUNT(*) as total_startups,
               SUM(CASE WHEN status = 'Ativa' THEN 1 ELSE 0 END) as ativas
        FROM startups
        GROUP BY setor
        ORDER BY score_medio DESC
    '''
    comparacao = db.executar_query_personalizada(query)
    print(comparacao.to_string(index=False))
    
    # 7. Startups com melhor equilíbrio (todas dimensões acima de 3.5)
    print("\n7️⃣ STARTUPS COM EQUILÍBRIO (todas dimensões > 3.5)")
    print("-" * 80)
    query = '''
        SELECT s.nome_startup, s.setor, s.score_global,
               COUNT(d.id) as total_dimensoes,
               SUM(CASE WHEN d.score > 3.5 THEN 1 ELSE 0 END) as dimensoes_acima_3_5
        FROM startups s
        JOIN avaliacoes_dimensoes d ON s.id = d.startup_id
        WHERE s.status = 'Ativa'
        GROUP BY s.id
        HAVING dimensoes_acima_3_5 = 8
        ORDER BY s.score_global DESC
    '''
    equilibradas = db.executar_query_personalizada(query)
    if not equilibradas.empty:
        print(equilibradas.to_string(index=False))
    else:
        print("Nenhuma startup atende a este critério")
    
    # 8. Análise de risco por setor (baseado em startups inativas)
    print("\n8️⃣ ANÁLISE DE RISCO POR SETOR (% de Inativas)")
    print("-" * 80)
    query = '''
        SELECT setor,
               COUNT(*) as total,
               SUM(CASE WHEN status = 'Inativa' THEN 1 ELSE 0 END) as inativas,
               ROUND(100.0 * SUM(CASE WHEN status = 'Inativa' THEN 1 ELSE 0 END) / COUNT(*), 2) as percentual_risco
        FROM startups
        GROUP BY setor
        ORDER BY percentual_risco DESC
    '''
    risco = db.executar_query_personalizada(query)
    print(risco.to_string(index=False))
    
    # 9. Detalhamento de uma startup específica
    print("\n9️⃣ DETALHAMENTO COMPLETO DA MELHOR STARTUP")
    print("-" * 80)
    if melhor:
        nome_startup = melhor[0]
        avaliacoes = db.obter_avaliacoes_dimensoes(nome_startup)
        print(f"\nStartup: {nome_startup}")
        print("\nScores por Dimensão:")
        print(avaliacoes.to_string(index=False))
    
    # 10. Exportar resultados para CSV
    print("\n🔟 EXPORTANDO CONSULTAS PARA CSV")
    print("-" * 80)
    
    # Exportar top startups
    startups_ativas.to_csv('consulta_top_startups.csv', index=False, encoding='utf-8-sig')
    print("✓ consulta_top_startups.csv")
    
    # Exportar estatísticas
    stats.to_csv('consulta_estatisticas_setor.csv', index=False, encoding='utf-8-sig')
    print("✓ consulta_estatisticas_setor.csv")
    
    # Exportar comparação
    comparacao.to_csv('consulta_comparacao_setores.csv', index=False, encoding='utf-8-sig')
    print("✓ consulta_comparacao_setores.csv")
    
    print("\n" + "=" * 80)
    print("✓ CONSULTAS CONCLUÍDAS!")
    print("=" * 80)
    
    # Desconectar
    db.desconectar()


def consulta_interativa():
    """Permite ao usuário fazer consultas interativas"""
    db = TechNovaDatabase('technova_iot.db')
    db.conectar()
    
    print("\n" + "=" * 80)
    print("MODO INTERATIVO - CONSULTA SQL")
    print("=" * 80)
    print("Digite suas queries SQL ou 'sair' para encerrar")
    print("Exemplo: SELECT * FROM startups WHERE setor = 'Saúde' LIMIT 5")
    print("-" * 80)
    
    while True:
        query = input("\nSQL> ").strip()
        
        if query.lower() in ['sair', 'exit', 'quit']:
            break
        
        if not query:
            continue
        
        try:
            resultado = db.executar_query_personalizada(query)
            print("\n" + resultado.to_string(index=False))
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    db.desconectar()
    print("\n✓ Sessão encerrada")


if __name__ == "__main__":
    # Executar exemplos de consultas
    exemplo_consultas()
    
    # Descomentar a linha abaixo para modo interativo
    # consulta_interativa()
