import sqlite3
import pandas as pd

DB_NAME = "brecho.db"

def conectar():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def inicializar_banco():
    """Cria as tabelas caso não existam a partir do arquivo schema.sql."""
    with conectar() as conn:
        with open("schema.sql", "r", encoding="utf-8") as f:
            conn.executescript(f.read())
            
        # Garante a coluna 'marca' em bancos criados anteriormente
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(produtos);")
        colunas = [col[1] for col in cursor.fetchall()]
        if 'marca' not in colunas:
            cursor.execute("ALTER TABLE produtos ADD COLUMN marca TEXT;")
            conn.commit()

# --- PRODUTOS ---

def cadastrar_produto(nome, marca, descricao, tamanho, categoria, preco_custo, preco_venda):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO produtos (nome, marca, descricao, tamanho, categoria, preco_custo, preco_venda)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nome, marca, descricao, tamanho, categoria, preco_custo, preco_venda))
        conn.commit()

def atualizar_produto(produto_id, nome, marca, descricao, tamanho, categoria, preco_custo, preco_venda, status):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE produtos
            SET nome = ?, marca = ?, descricao = ?, tamanho = ?, categoria = ?, preco_custo = ?, preco_venda = ?, status = ?
            WHERE id = ?
        ''', (nome, marca, descricao, tamanho, categoria, preco_custo, preco_venda, status, produto_id))
        conn.commit()

def excluir_produto(produto_id):
    with conectar() as conn:
        cursor = conn.cursor()
        # Remove primeiro vendas associadas se houver, depois o produto
        cursor.execute('DELETE FROM vendas WHERE produto_id = ?', (produto_id,))
        cursor.execute('DELETE FROM produtos WHERE id = ?', (produto_id,))
        conn.commit()

def listar_todos_produtos():
    with conectar() as conn:
        query = "SELECT * FROM produtos ORDER BY id DESC"
        return pd.read_sql_query(query, conn)

def listar_produtos_disponiveis():
    with conectar() as conn:
        query = "SELECT id, nome, marca, tamanho, categoria, preco_venda FROM produtos WHERE status = 'disponivel'"
        return pd.read_sql_query(query, conn)

# --- VENDAS ---

def registrar_venda(produto_id, valor_final, forma_pagamento):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vendas (produto_id, valor_final, forma_pagamento)
            VALUES (?, ?, ?)
        ''', (produto_id, valor_final, forma_pagamento))
        
        cursor.execute('''
            UPDATE produtos SET status = 'vendido' WHERE id = ?
        ''', (produto_id,))
        conn.commit()

def relatorio_vendas():
    with conectar() as conn:
        query = '''
            SELECT 
                v.id AS venda_id,
                p.nome AS produto,
                p.marca,
                p.preco_custo,
                v.valor_final AS valor_vendido,
                (v.valor_final - p.preco_custo) AS lucro_bruto,
                v.forma_pagamento,
                v.data_venda
            FROM vendas v
            JOIN produtos p ON v.produto_id = p.id
            ORDER BY v.data_venda DESC
        '''
        return pd.read_sql_query(query, conn)

# --- GASTOS DA EMPRESA ---

def cadastrar_gasto(descricao, categoria, valor):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO gastos (descricao, categoria, valor)
            VALUES (?, ?, ?)
        ''', (descricao, categoria, valor))
        conn.commit()

def listar_gastos():
    with conectar() as conn:
        query = "SELECT id, descricao, categoria, valor, data_gasto FROM gastos ORDER BY data_gasto DESC"
        return pd.read_sql_query(query, conn)

def excluir_gasto(gasto_id):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM gastos WHERE id = ?', (gasto_id,))
        conn.commit()