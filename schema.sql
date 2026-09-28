PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    marca TEXT,
    descricao TEXT,
    tamanho TEXT,
    categoria TEXT,
    quantidade INTEGER DEFAULT 1, -- Nova coluna para quantidade
    preco_custo REAL DEFAULT 0.0,
    preco_venda REAL NOT NULL,
    status TEXT CHECK(status IN ('disponivel', 'esgotado', 'reservado')) DEFAULT 'disponivel',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    quantidade_vendida INTEGER DEFAULT 1, -- Quantidade na venda
    valor_final REAL NOT NULL,
    forma_pagamento TEXT CHECK(forma_pagamento IN ('pix', 'dinheiro', 'cartao_credito', 'cartao_debito')),
    data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

CREATE TABLE IF NOT EXISTS gastos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL,
    valor REAL NOT NULL,
    data_gasto DATETIME DEFAULT CURRENT_TIMESTAMP
);