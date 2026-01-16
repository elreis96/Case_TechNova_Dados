import pandas as pd

# Carregar arquivo Excel
xl = pd.ExcelFile('Case_TechNova_Dados.xlsx')

# Salvar exploração em arquivo
with open('exploracao_dados.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 60 + "\n")
    f.write("ABAS DISPONÍVEIS NO ARQUIVO EXCEL\n")
    f.write("=" * 60 + "\n")
    f.write(str(xl.sheet_names) + "\n\n")
    
    # Explorar cada aba
    for sheet in xl.sheet_names:
        df = pd.read_excel('Case_TechNova_Dados.xlsx', sheet_name=sheet)
        f.write("=" * 60 + "\n")
        f.write(f"ABA: {sheet}\n")
        f.write("=" * 60 + "\n")
        f.write(f"Shape: {df.shape}\n\n")
        f.write(f"Colunas ({len(df.columns)}):\n")
        for i, col in enumerate(df.columns, 1):
            f.write(f"  {i}. {col}\n")
        f.write("\n")
        f.write("Primeiras 5 linhas:\n")
        f.write(df.head().to_string() + "\n\n")

print("Exploração salva em 'exploracao_dados.txt'")
