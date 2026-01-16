"""
Análise de Maturidade de Produtos IoT - TechNova
Especialista em Data Analytics

Autor: Sistema de Análise TechNova
Data: 2026-01-16
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Configurações de visualização
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print("=" * 80)
print("ANÁLISE DE MATURIDADE DE PRODUTOS IoT - TECHNOVA")
print("=" * 80)
print()

# ============================================================================
# 1. TRATAMENTO DE DADOS
# ============================================================================
print("1. TRATAMENTO DE DADOS")
print("-" * 80)

# Carregar dados
df = pd.read_excel('Case_TechNova_Dados.xlsx', sheet_name='Avaliacoes_Startups')
print(f"✓ Dados carregados: {df.shape[0]} startups, {df.shape[1]} colunas")

# Separar por status
df_falhas = df[df['status'] == 'Inativa'].copy()
df_investimento = df[df['status'] == 'Ativa'].copy()

print(f"✓ Startups Ativas: {len(df_investimento)}")
print(f"✓ Startups Inativas: {len(df_falhas)}")
print()

# ============================================================================
# 2. ENGENHARIA DE ATRIBUTOS
# ============================================================================
print("2. ENGENHARIA DE ATRIBUTOS")
print("-" * 80)

# Identificar colunas de notas (1.1 a 8.5)
colunas_notas = [col for col in df.columns if col[0].isdigit() and '.' in col]
print(f"✓ Colunas de avaliação identificadas: {len(colunas_notas)}")

# Criar Score_Global para todas as startups
df['Score_Global'] = df[colunas_notas].mean(axis=1)
df_investimento['Score_Global'] = df_investimento[colunas_notas].mean(axis=1)
df_falhas['Score_Global'] = df_falhas[colunas_notas].mean(axis=1)

print(f"✓ Score_Global criado")
print(f"  - Média geral: {df['Score_Global'].mean():.2f}")
print(f"  - Média Ativas: {df_investimento['Score_Global'].mean():.2f}")
print(f"  - Média Inativas: {df_falhas['Score_Global'].mean():.2f}")
print()

# ============================================================================
# 3. VISÃO MACRO - AGREGAÇÃO POR DIMENSÃO
# ============================================================================
print("3. VISÃO MACRO - AGREGAÇÃO POR DIMENSÕES")
print("-" * 80)

# Definir grupos/dimensões
dimensoes = {
    'Grupo 1 - Performance Técnica': [col for col in colunas_notas if col.startswith('1.')],
    'Grupo 2 - Viabilidade Econômica': [col for col in colunas_notas if col.startswith('2.')],
    'Grupo 3 - Confiabilidade': [col for col in colunas_notas if col.startswith('3.')],
    'Grupo 4 - Usabilidade': [col for col in colunas_notas if col.startswith('4.')],
    'Grupo 5 - Eficiência Energética': [col for col in colunas_notas if col.startswith('5.')],
    'Grupo 6 - Robustez Física': [col for col in colunas_notas if col.startswith('6.')],
    'Grupo 7 - Conectividade': [col for col in colunas_notas if col.startswith('7.')],
    'Grupo 8 - Sustentabilidade': [col for col in colunas_notas if col.startswith('8.')]
}

# Calcular médias por dimensão para startups ativas
for nome_dim, colunas_dim in dimensoes.items():
    df_investimento[nome_dim] = df_investimento[colunas_dim].mean(axis=1)
    media = df_investimento[nome_dim].mean()
    print(f"✓ {nome_dim}: {media:.2f}")

print()

# ============================================================================
# 4. IDENTIFICAÇÃO DA MELHOR STARTUP
# ============================================================================
print("4. IDENTIFICAÇÃO DA MELHOR STARTUP")
print("-" * 80)

# Calcular média combinada de Performance (Grupo 1) e Viabilidade (Grupo 2)
df_investimento['Score_Performance_Viabilidade'] = (
    df_investimento['Grupo 1 - Performance Técnica'] + 
    df_investimento['Grupo 2 - Viabilidade Econômica']
) / 2

# Identificar a melhor startup
melhor_startup_idx = df_investimento['Score_Performance_Viabilidade'].idxmax()
melhor_startup = df_investimento.loc[melhor_startup_idx]

print(f"🏆 MELHOR STARTUP PARA INVESTIMENTO:")
print(f"   Nome: {melhor_startup['nome_startup']}")
print(f"   Setor: {melhor_startup['setor']}")
print(f"   Score Global: {melhor_startup['Score_Global']:.2f}")
print(f"   Performance Técnica (Grupo 1): {melhor_startup['Grupo 1 - Performance Técnica']:.2f}")
print(f"   Viabilidade Econômica (Grupo 2): {melhor_startup['Grupo 2 - Viabilidade Econômica']:.2f}")
print(f"   Score Performance + Viabilidade: {melhor_startup['Score_Performance_Viabilidade']:.2f}")
print()

# Top 5 startups
print("📊 TOP 5 STARTUPS (Performance + Viabilidade):")
top5 = df_investimento.nlargest(5, 'Score_Performance_Viabilidade')[
    ['nome_startup', 'setor', 'Score_Global', 'Score_Performance_Viabilidade']
]
for idx, (i, row) in enumerate(top5.iterrows(), 1):
    print(f"   {idx}. {row['nome_startup']} ({row['setor']}) - Score: {row['Score_Performance_Viabilidade']:.2f}")
print()

# ============================================================================
# 5. VISUALIZAÇÕES
# ============================================================================
print("5. GERANDO VISUALIZAÇÕES")
print("-" * 80)

# 5.1 GRÁFICO DE RADAR - Melhor Startup (Plotly)
print("✓ Gerando Gráfico de Radar (Plotly)...")

# Preparar dados para o radar
categorias = list(dimensoes.keys())
valores_melhor = [melhor_startup[cat] for cat in categorias]

# Criar gráfico de radar
fig_radar = go.Figure()

fig_radar.add_trace(go.Scatterpolar(
    r=valores_melhor,
    theta=categorias,
    fill='toself',
    name=melhor_startup['nome_startup'],
    line=dict(color='#1f77b4', width=2),
    fillcolor='rgba(31, 119, 180, 0.3)'
))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 5],
            tickmode='linear',
            tick0=0,
            dtick=1
        )
    ),
    title=dict(
        text=f"Análise Multidimensional - {melhor_startup['nome_startup']}<br>" +
             f"<sub>Setor: {melhor_startup['setor']} | Score Global: {melhor_startup['Score_Global']:.2f}</sub>",
        x=0.5,
        xanchor='center',
        font=dict(size=18)
    ),
    showlegend=True,
    height=600,
    width=800
)

# Salvar gráfico de radar
fig_radar.write_html('radar_melhor_startup.html')
fig_radar.write_image('radar_melhor_startup.png', width=800, height=600, scale=2)
print("  → Salvo: radar_melhor_startup.html e radar_melhor_startup.png")

# 5.2 BOXPLOT - Score Global por Setor (Matplotlib/Seaborn)
print("✓ Gerando Boxplot - Score Global por Setor...")

plt.figure(figsize=(12, 6))
sns.boxplot(data=df_investimento, x='setor', y='Score_Global', palette='Set2')
plt.title('Distribuição do Score Global por Setor\n(Startups Ativas)', 
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Setor', fontsize=12, fontweight='bold')
plt.ylabel('Score Global', fontsize=12, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig('boxplot_score_por_setor.png', dpi=300, bbox_inches='tight')
print("  → Salvo: boxplot_score_por_setor.png")
plt.close()

# 5.3 GRÁFICO ADICIONAL - Comparação Performance vs Viabilidade
print("✓ Gerando Scatter Plot - Performance vs Viabilidade...")

plt.figure(figsize=(12, 8))
setores_unicos = df_investimento['setor'].unique()
cores = plt.cm.Set3(np.linspace(0, 1, len(setores_unicos)))

for setor, cor in zip(setores_unicos, cores):
    dados_setor = df_investimento[df_investimento['setor'] == setor]
    plt.scatter(
        dados_setor['Grupo 1 - Performance Técnica'],
        dados_setor['Grupo 2 - Viabilidade Econômica'],
        label=setor,
        s=100,
        alpha=0.6,
        c=[cor],
        edgecolors='black',
        linewidth=1
    )

# Destacar a melhor startup
plt.scatter(
    melhor_startup['Grupo 1 - Performance Técnica'],
    melhor_startup['Grupo 2 - Viabilidade Econômica'],
    s=500,
    c='gold',
    marker='*',
    edgecolors='red',
    linewidth=2,
    label=f'🏆 {melhor_startup["nome_startup"]}',
    zorder=10
)

plt.title('Performance Técnica vs Viabilidade Econômica\n(Startups Ativas)', 
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Grupo 1 - Performance Técnica', fontsize=12, fontweight='bold')
plt.ylabel('Grupo 2 - Viabilidade Econômica', fontsize=12, fontweight='bold')
plt.legend(loc='best', framealpha=0.9)
plt.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig('scatter_performance_viabilidade.png', dpi=300, bbox_inches='tight')
print("  → Salvo: scatter_performance_viabilidade.png")
plt.close()

print()

# ============================================================================
# 6. RELATÓRIO FINAL
# ============================================================================
print("6. RELATÓRIO EXECUTIVO")
print("=" * 80)

print(f"""
RECOMENDAÇÃO DE INVESTIMENTO - TECHNOVA
{'=' * 80}

STARTUP RECOMENDADA: {melhor_startup['nome_startup']}
Setor: {melhor_startup['setor']}

JUSTIFICATIVA:
- Melhor equilíbrio entre Performance Técnica e Viabilidade Econômica
- Score Combinado (Performance + Viabilidade): {melhor_startup['Score_Performance_Viabilidade']:.2f}/5.00
- Score Global: {melhor_startup['Score_Global']:.2f}/5.00

DESTAQUES POR DIMENSÃO:
""")

for cat in categorias:
    valor = melhor_startup[cat]
    print(f"  • {cat}: {valor:.2f}/5.00")

print(f"""
ANÁLISE SETORIAL:
- Total de startups ativas no setor {melhor_startup['setor']}: {len(df_investimento[df_investimento['setor'] == melhor_startup['setor']])}
- Média do setor: {df_investimento[df_investimento['setor'] == melhor_startup['setor']]['Score_Global'].mean():.2f}
- Posição da startup no setor: #{(df_investimento[df_investimento['setor'] == melhor_startup['setor']]['Score_Global'] > melhor_startup['Score_Global']).sum() + 1}

ARQUIVOS GERADOS:
✓ radar_melhor_startup.html (interativo)
✓ radar_melhor_startup.png
✓ boxplot_score_por_setor.png
✓ scatter_performance_viabilidade.png

{'=' * 80}
""")

# Salvar DataFrames processados
df_investimento.to_csv('startups_ativas_processadas.csv', index=False, encoding='utf-8-sig')
df_falhas.to_csv('startups_inativas_processadas.csv', index=False, encoding='utf-8-sig')
print("✓ DataFrames salvos: startups_ativas_processadas.csv e startups_inativas_processadas.csv")
print()
print("=" * 80)
print("ANÁLISE CONCLUÍDA COM SUCESSO!")
print("=" * 80)
