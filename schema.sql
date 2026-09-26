PRAGMA foreign_keys = ON;


CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    tamanho TEXT, 
    categoria TEXT, 
    preco_custo REAL DEFAULT 0.0, 
    preco_venda REAL NOT NULL,
    status TEXT CHECK(status IN ('disponivel', 'vendido')) DEFAULT 'disponivel',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    valor_final REAL NOT NULL,
    forma_pagamento TEXT CHECK(forma_pagamento IN ('pix', 'dinheiro', 'cartao_credito', 'cartao_debito')),
    data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);