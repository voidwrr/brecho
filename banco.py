import sqlite3
import pandas as pd

DB_NAME = "brecho.db"

def conectar():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def inicializar_banco():
    with conectar() as conn:
        with open("schema.sql", "r", encoding="utf-8") as f:
            conn.executescript(f.read())
            
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(produtos);")
        colunas_prod = [col[1] for col in cursor.fetchall()]
        if 'marca' not in colunas_prod:
            cursor.execute("ALTER TABLE produtos ADD COLUMN marca TEXT;")
        if 'quantidade' not in colunas_prod:
            cursor.execute("ALTER TABLE produtos ADD COLUMN quantidade INTEGER DEFAULT 1;")
            
        cursor.execute("PRAGMA table_info(vendas);")
        colunas_vendas = [col[1] for col in cursor.fetchall()]
        if 'quantidade_vendida' not in colunas_vendas:
            cursor.execute("ALTER TABLE vendas ADD COLUMN quantidade_vendida INTEGER DEFAULT 1;")
            
        conn.commit()

# --- PRODUTOS ---

def cadastrar_produto(nome, marca, descricao, tamanho, categoria, quantidade, preco_custo, preco_venda):
    status = 'disponivel' if quantidade > 0 else 'esgotado'
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO produtos (nome, marca, descricao, tamanho, categoria, quantidade, preco_custo, preco_venda, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, marca, descricao, tamanho, categoria, quantidade, preco_custo, preco_venda, status))
        conn.commit()

def atualizar_produto(produto_id, nome, marca, descricao, tamanho, categoria, quantidade, preco_custo, preco_venda, status):
    # Se a quantidade for ajustada para 0 ou menos, atualiza status para esgotado
    if quantidade <= 0:
        status = 'esgotado'
    elif status == 'esgotado' and quantidade > 0:
        status = 'disponivel'

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE produtos
            SET nome = ?, marca = ?, descricao = ?, tamanho = ?, categoria = ?, quantidade = ?, preco_custo = ?, preco_venda = ?, status = ?
            WHERE id = ?
        ''', (nome, marca, descricao, tamanho, categoria, quantidade, preco_custo, preco_venda, status, produto_id))
        conn.commit()

def excluir_produto(produto_id):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM vendas WHERE produto_id = ?', (produto_id,))
        cursor.execute('DELETE FROM produtos WHERE id = ?', (produto_id,))
        conn.commit()

def listar_todos_produtos():
    with conectar() as conn:
        query = "SELECT * FROM produtos ORDER BY id DESC"
        return pd.read_sql_query(query, conn)

def listar_produtos_disponiveis():
    with conectar() as conn:
        query = "SELECT id, nome, marca, tamanho, categoria, quantidade, preco_venda FROM produtos WHERE quantidade > 0 AND status != 'esgotado'"
        return pd.read_sql_query(query, conn)

# --- VENDAS ---

def registrar_venda(produto_id, qtd_vendida, valor_final_unitario, forma_pagamento):
    valor_total_venda = valor_final_unitario * qtd_vendida
    with conectar() as conn:
        cursor = conn.cursor()
        
        # Registrar a venda
        cursor.execute('''
            INSERT INTO vendas (produto_id, quantidade_vendida, valor_final, forma_pagamento)
            VALUES (?, ?, ?, ?)
        ''', (produto_id, qtd_vendida, valor_total_venda, forma_pagamento))
        
        # Abater do estoque do produto
        cursor.execute('SELECT quantidade FROM produtos WHERE id = ?', (produto_id,))
        qtd_atual = cursor.fetchone()[0]
        nova_qtd = max(0, qtd_atual - qtd_vendida)
        novo_status = 'esgotado' if nova_qtd == 0 else 'disponivel'
        
        cursor.execute('''
            UPDATE produtos SET quantidade = ?, status = ? WHERE id = ?
        ''', (nova_qtd, novo_status, produto_id))
        
        conn.commit()

def relatorio_vendas():
    with conectar() as conn:
        query = '''
            SELECT 
                v.id AS venda_id,
                p.nome AS produto,
                p.marca,
                v.quantidade_vendida,
                p.preco_custo AS custo_unitario,
                (p.preco_custo * v.quantidade_vendida) AS custo_total,
                v.valor_final AS valor_total_vendido,
                (v.valor_final - (p.preco_custo * v.quantidade_vendida)) AS lucro_bruto,
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