import streamlit as st
import banco

# Configuração da página
st.set_page_config(page_title="Gestão Brechó", page_icon="🛍️", layout="wide")

# Garante que as tabelas existem no banco
banco.inicializar_banco()

st.title("🛍️ Painel do Brechó")

menu = st.sidebar.selectbox(
    "Navegação", 
    ["Cadastrar Produto", "Registrar Venda", "Estoque Disponível", "Relatório de Vendas"]
)

# --- OPÇÃO 1: CADASTRAR PRODUTO ---
if menu == "Cadastrar Produto":
    st.subheader("➕ Cadastrar Novo Produto")
    
    with st.form("form_produto", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Produto")
            categoria = st.selectbox("Categoria", ["Camisa", "Calça", "Casaco", "Vestido", "Acessório", "Calçado", "Outros"])
            tamanho = st.text_input("Tamanho (Ex: P, M, 38, Único)")
        
        with col2:
            preco_custo = st.number_input("Preço de Custo (R$)", min_value=0.0, step=1.0)
            preco_venda = st.number_input("Preço de Venda (R$)", min_value=0.0, step=1.0)
            descricao = st.text_area("Descrição / Detalhes")
        
        submetido = st.form_submit_button("Salvar Produto")
        
        if submetido:
            if nome and preco_venda > 0:
                banco.cadastrar_produto(nome, descricao, tamanho, categoria, preco_custo, preco_venda)
                st.success(f"Produto '{nome}' cadastrado com sucesso!")
            else:
                st.error("Preencha o nome e um preço de venda válido.")

# --- OPÇÃO 2: REGISTRAR VENDA ---
elif menu == "Registrar Venda":
    st.subheader("💰 Registrar Venda")
    
    df_disponiveis = banco.listar_produtos_disponiveis()
    
    if df_disponiveis.empty:
        st.info("Nenhum produto disponível no momento.")
    else:
        # Cria um formato fácil para seleção no dropdown
        opcoes_produtos = {
            f"ID {row['id']} - {row['nome']} (R$ {row['preco_venda']:.2f})": row['id']
            for _, row in df_disponiveis.iterrows()
        }
        
        produto_selecionado = st.selectbox("Selecione o Produto", list(opcoes_produtos.keys()))
        produto_id = opcoes_produtos[produto_selecionado]
        
        # Pega o preço padrão para preencher o campo do valor
        preco_padrao = float(df_disponiveis[df_disponiveis['id'] == produto_id]['preco_venda'].values[0])
        
        col1, col2 = st.columns(2)
        with col1:
            valor_final = st.number_input("Valor Final Cobrado (R$)", min_value=0.0, value=preco_padrao, step=1.0)
        with col2:
            forma_pagamento = st.selectbox("Forma de Pagamento", ["pix", "dinheiro", "cartao_credito", "cartao_debito"])
            
        if st.button("Confirmar Venda"):
            banco.registrar_venda(produto_id, valor_final, forma_pagamento)
            st.success("Venda registrada com sucesso!")
            st.rerun()

# --- OPÇÃO 3: ESTOQUE DISPONÍVEL ---
elif menu == "Estoque Disponível":
    st.subheader("📦 Produtos em Estoque")
    df_disponiveis = banco.listar_produtos_disponiveis()
    
    if not df_disponiveis.empty:
        st.dataframe(df_disponiveis, use_container_width=True)
    else:
        st.info("Estoque vazio no momento.")

# --- OPÇÃO 4: RELATÓRIO DE VENDAS ---
elif menu == "Relatório de Vendas":
    st.subheader("📊 Histórico e Lucro")
    df_vendas = banco.relatorio_vendas()
    
    if not df_vendas.empty:
        faturamento_total = df_vendas['valor_vendido'].sum()
        lucro_total = df_vendas['lucro'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Vendas", len(df_vendas))
        col2.metric("Faturamento Total", f"R$ {faturamento_total:.2f}")
        col3.metric("Lucro Líquido", f"R$ {lucro_total:.2f}")
        
        st.markdown("---")
        st.dataframe(df_vendas, use_container_width=True)
    else:
        st.info("Nenhuma venda realizada ainda.")