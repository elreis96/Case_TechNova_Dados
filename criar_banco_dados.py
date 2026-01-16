"""
Sistema de Banco de Dados - TechNova IoT
Converte dados do Excel para SQLite e fornece interface de consulta

Autor: Sistema TechNova
Data: 2026-01-16
"""

import pandas as pd
import sqlite3
from pathlib import Path
import sys

class TechNovaDatabase:
    """Classe para gerenciar o banco de dados TechNova"""
    
    def __init__(self, db_path='technova_iot.db'):
        """
        Inicializa conexão com o banco de dados
        
        Args:
            db_path: Caminho para o arquivo do banco de dados SQLite
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def conectar(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"✓ Conectado ao banco de dados: {self.db_path}")
            return True
        except Exception as e:
            print(f"✗ Erro ao conectar ao banco: {e}")
            return False
    
    def desconectar(self):
        """Fecha conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
            print("✓ Conexão fechada")
    
    def criar_tabelas(self):
        """Cria as tabelas do banco de dados"""
        print("\n" + "=" * 80)
        print("CRIANDO ESTRUTURA DO BANCO DE DADOS")
        print("=" * 80)
        
        # Tabela de Startups
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS startups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_startup TEXT NOT NULL UNIQUE,
                setor TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Ativa', 'Inativa')),
                score_global REAL,
                score_performance_viabilidade REAL,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Tabela 'startups' criada")
        
        # Tabela de Avaliações por Dimensão
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS avaliacoes_dimensoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                startup_id INTEGER NOT NULL,
                dimensao TEXT NOT NULL,
                score REAL NOT NULL,
                FOREIGN KEY (startup_id) REFERENCES startups(id),
                UNIQUE(startup_id, dimensao)
            )
        ''')
        print("✓ Tabela 'avaliacoes_dimensoes' criada")
        
        # Tabela de Avaliações Detalhadas (todas as colunas de notas)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS avaliacoes_detalhadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                startup_id INTEGER NOT NULL,
                criterio TEXT NOT NULL,
                score REAL NOT NULL,
                FOREIGN KEY (startup_id) REFERENCES startups(id),
                UNIQUE(startup_id, criterio)
            )
        ''')
        print("✓ Tabela 'avaliacoes_detalhadas' criada")
        
        # Tabela de Estatísticas por Setor
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS estatisticas_setor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setor TEXT NOT NULL UNIQUE,
                total_startups INTEGER,
                startups_ativas INTEGER,
                startups_inativas INTEGER,
                score_medio REAL,
                score_mediano REAL,
                score_min REAL,
                score_max REAL,
                ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Tabela 'estatisticas_setor' criada")
        
        self.conn.commit()
        print("\n✓ Estrutura do banco de dados criada com sucesso!")
    
    def importar_dados_excel(self, excel_path='Case_TechNova_Dados.xlsx'):
        """
        Importa dados do arquivo Excel para o banco de dados
        
        Args:
            excel_path: Caminho para o arquivo Excel
        """
        print("\n" + "=" * 80)
        print("IMPORTANDO DADOS DO EXCEL")
        print("=" * 80)
        
        # Verificar se arquivo existe
        if not Path(excel_path).exists():
            print(f"✗ Arquivo não encontrado: {excel_path}")
            return False
        
        # Carregar dados
        df = pd.read_excel(excel_path, sheet_name='Avaliacoes_Startups')
        print(f"✓ Dados carregados: {len(df)} startups")
        
        # Identificar colunas de notas
        colunas_notas = [col for col in df.columns if col[0].isdigit() and '.' in col]
        print(f"✓ Colunas de avaliação: {len(colunas_notas)}")
        
        # Calcular Score Global
        df['Score_Global'] = df[colunas_notas].mean(axis=1)
        
        # Definir dimensões
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
        
        # Calcular scores por dimensão
        for nome_dim, colunas_dim in dimensoes.items():
            df[nome_dim] = df[colunas_dim].mean(axis=1)
        
        # Calcular Score Performance + Viabilidade
        df['Score_Performance_Viabilidade'] = (
            df['Grupo 1 - Performance Técnica'] + 
            df['Grupo 2 - Viabilidade Econômica']
        ) / 2
        
        print("\n📊 Inserindo dados nas tabelas...")
        
        # Inserir startups
        startups_inseridas = 0
        for _, row in df.iterrows():
            try:
                self.cursor.execute('''
                    INSERT INTO startups (nome_startup, setor, status, score_global, score_performance_viabilidade)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    row['nome_startup'],
                    row['setor'],
                    row['status'],
                    float(row['Score_Global']),
                    float(row['Score_Performance_Viabilidade'])
                ))
                startup_id = self.cursor.lastrowid
                
                # Inserir avaliações por dimensão
                for dimensao in dimensoes.keys():
                    self.cursor.execute('''
                        INSERT INTO avaliacoes_dimensoes (startup_id, dimensao, score)
                        VALUES (?, ?, ?)
                    ''', (startup_id, dimensao, float(row[dimensao])))
                
                # Inserir avaliações detalhadas
                for criterio in colunas_notas:
                    self.cursor.execute('''
                        INSERT INTO avaliacoes_detalhadas (startup_id, criterio, score)
                        VALUES (?, ?, ?)
                    ''', (startup_id, criterio, float(row[criterio])))
                
                startups_inseridas += 1
                
            except Exception as e:
                print(f"✗ Erro ao inserir {row['nome_startup']}: {e}")
        
        print(f"✓ {startups_inseridas} startups inseridas")
        
        # Calcular e inserir estatísticas por setor
        print("\n📈 Calculando estatísticas por setor...")
        setores = df['setor'].unique()
        
        for setor in setores:
            df_setor = df[df['setor'] == setor]
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO estatisticas_setor 
                (setor, total_startups, startups_ativas, startups_inativas, 
                 score_medio, score_mediano, score_min, score_max)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                setor,
                len(df_setor),
                len(df_setor[df_setor['status'] == 'Ativa']),
                len(df_setor[df_setor['status'] == 'Inativa']),
                float(df_setor['Score_Global'].mean()),
                float(df_setor['Score_Global'].median()),
                float(df_setor['Score_Global'].min()),
                float(df_setor['Score_Global'].max())
            ))
        
        print(f"✓ Estatísticas calculadas para {len(setores)} setores")
        
        self.conn.commit()
        print("\n✓ Importação concluída com sucesso!")
        return True
    
    def consultar_startup(self, nome_startup):
        """Consulta informações completas de uma startup"""
        self.cursor.execute('''
            SELECT * FROM startups WHERE nome_startup = ?
        ''', (nome_startup,))
        return self.cursor.fetchone()
    
    def listar_startups_ativas(self):
        """Lista todas as startups ativas ordenadas por score"""
        query = '''
            SELECT nome_startup, setor, score_global, score_performance_viabilidade
            FROM startups
            WHERE status = 'Ativa'
            ORDER BY score_performance_viabilidade DESC
        '''
        return pd.read_sql_query(query, self.conn)
    
    def listar_startups_por_setor(self, setor):
        """Lista startups de um setor específico"""
        query = '''
            SELECT nome_startup, status, score_global, score_performance_viabilidade
            FROM startups
            WHERE setor = ?
            ORDER BY score_global DESC
        '''
        return pd.read_sql_query(query, self.conn, params=(setor,))
    
    def obter_melhor_startup(self):
        """Retorna a startup com melhor score de performance + viabilidade"""
        query = '''
            SELECT s.nome_startup, s.setor, s.score_global, s.score_performance_viabilidade,
                   GROUP_CONCAT(d.dimensao || ': ' || ROUND(d.score, 2), '\n') as dimensoes
            FROM startups s
            LEFT JOIN avaliacoes_dimensoes d ON s.id = d.startup_id
            WHERE s.status = 'Ativa'
            GROUP BY s.id
            ORDER BY s.score_performance_viabilidade DESC
            LIMIT 1
        '''
        self.cursor.execute(query)
        return self.cursor.fetchone()
    
    def obter_estatisticas_setor(self, setor=None):
        """Retorna estatísticas de um setor ou de todos os setores"""
        if setor:
            query = 'SELECT * FROM estatisticas_setor WHERE setor = ?'
            return pd.read_sql_query(query, self.conn, params=(setor,))
        else:
            query = 'SELECT * FROM estatisticas_setor ORDER BY score_medio DESC'
            return pd.read_sql_query(query, self.conn)
    
    def obter_avaliacoes_dimensoes(self, nome_startup):
        """Retorna as avaliações por dimensão de uma startup"""
        query = '''
            SELECT d.dimensao, d.score
            FROM avaliacoes_dimensoes d
            JOIN startups s ON d.startup_id = s.id
            WHERE s.nome_startup = ?
            ORDER BY d.dimensao
        '''
        return pd.read_sql_query(query, self.conn, params=(nome_startup,))
    
    def executar_query_personalizada(self, query, params=None):
        """Executa uma query SQL personalizada"""
        if params:
            return pd.read_sql_query(query, self.conn, params=params)
        else:
            return pd.read_sql_query(query, self.conn)


def main():
    """Função principal para criar e popular o banco de dados"""
    print("=" * 80)
    print("SISTEMA DE BANCO DE DADOS - TECHNOVA IoT")
    print("=" * 80)
    
    # Criar instância do banco
    db = TechNovaDatabase('technova_iot.db')
    
    # Conectar
    if not db.conectar():
        sys.exit(1)
    
    # Criar tabelas
    db.criar_tabelas()
    
    # Importar dados
    if db.importar_dados_excel():
        print("\n" + "=" * 80)
        print("VERIFICAÇÃO DOS DADOS IMPORTADOS")
        print("=" * 80)
        
        # Mostrar melhor startup
        melhor = db.obter_melhor_startup()
        if melhor:
            print(f"\n🏆 MELHOR STARTUP:")
            print(f"   Nome: {melhor[0]}")
            print(f"   Setor: {melhor[1]}")
            print(f"   Score Global: {melhor[2]:.2f}")
            print(f"   Score Performance + Viabilidade: {melhor[3]:.2f}")
        
        # Mostrar estatísticas gerais
        print("\n📊 ESTATÍSTICAS POR SETOR:")
        stats = db.obter_estatisticas_setor()
        print(stats.to_string(index=False))
        
        # Contar registros
        db.cursor.execute('SELECT COUNT(*) FROM startups')
        total_startups = db.cursor.fetchone()[0]
        
        db.cursor.execute('SELECT COUNT(*) FROM avaliacoes_dimensoes')
        total_avaliacoes_dim = db.cursor.fetchone()[0]
        
        db.cursor.execute('SELECT COUNT(*) FROM avaliacoes_detalhadas')
        total_avaliacoes_det = db.cursor.fetchone()[0]
        
        print(f"\n📈 RESUMO DO BANCO DE DADOS:")
        print(f"   Total de Startups: {total_startups}")
        print(f"   Total de Avaliações por Dimensão: {total_avaliacoes_dim}")
        print(f"   Total de Avaliações Detalhadas: {total_avaliacoes_det}")
        
        print("\n" + "=" * 80)
        print("✓ BANCO DE DADOS CRIADO E POPULADO COM SUCESSO!")
        print(f"✓ Arquivo: technova_iot.db")
        print("=" * 80)
    
    # Desconectar
    db.desconectar()


if __name__ == "__main__":
    main()
