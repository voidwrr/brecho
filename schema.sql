-- Habilita o suporte a chaves estrangeiras no SQLite
PRAGMA foreign_keys = ON;

-- Tabela para cadastrar os produtos do brechó
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    marca TEXT, -- Ex: Zara, Farm, Nike, Sem Marca
    descricao TEXT,
    tamanho TEXT, -- Ex: P, M, G, 38, 40
    categoria TEXT, -- Ex: Camisa, Calça, Acessório
    preco_custo REAL DEFAULT 0.0, -- Quanto vocês pagaram pela peça
    preco_venda REAL NOT NULL, -- Preço na etiqueta
    status TEXT CHECK(status IN ('disponivel', 'vendido', 'reservado')) DEFAULT 'disponivel',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para registrar o histórico de vendas
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    valor_final REAL NOT NULL, -- Valor real cobrado (pode ter tido desconto)
    forma_pagamento TEXT CHECK(forma_pagamento IN ('pix', 'dinheiro', 'cartao_credito', 'cartao_debito')),
    data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);

-- Tabela para registrar os gastos/despesas da empresa
CREATE TABLE IF NOT EXISTS gastos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL, -- Ex: Embalagens, Transporte, Marketing, Aluguel, Outros
    valor REAL NOT NULL,
    data_gasto DATETIME DEFAULT CURRENT_TIMESTAMP
);