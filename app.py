import streamlit as st
import banco

st.set_page_config(page_title="Gestão Brechó", page_icon="🛍️", layout="wide")

banco.inicializar_banco()

st.title("🛍️ Painel do Brechó")

menu = st.sidebar.selectbox(
    "Navegação", 
    ["Cadastrar Produto", "Gerenciar / Editar Produtos", "Registrar Venda", "Registrar Gastos", "Relatório Financeiro"]
)

# --- OPÇÃO 1: CADASTRAR PRODUTO ---
if menu == "Cadastrar Produto":
    st.subheader("➕ Cadastrar Novo Produto")
    
    with st.form("form_produto", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Produto")
            marca = st.text_input("Marca (Ex: Zara, Farm, Nike, Sem Marca)")
            categoria = st.selectbox("Categoria", ["Camisa", "Calça", "Casaco", "Vestido", "Acessório", "Calçado", "Outros"])
            tamanho = st.text_input("Tamanho (Ex: P, M, 38, Único)")
        
        with col2:
            preco_custo = st.number_input("Preço de Custo (R$)", min_value=0.0, step=1.0)
            preco_venda = st.number_input("Preço de Venda (R$)", min_value=0.0, step=1.0)
            descricao = st.text_area("Descrição / Detalhes")
        
        submetido = st.form_submit_button("Salvar Produto")
        
        if submetido:
            if nome and preco_venda > 0:
                banco.cadastrar_produto(nome, marca, descricao, tamanho, categoria, preco_custo, preco_venda)
                st.success(f"Produto '{nome}' cadastrado com sucesso!")
            else:
                st.error("Preencha o nome e um preço de venda válido.")

# --- OPÇÃO 2: GERENCIAR / EDITAR PRODUTOS ---
elif menu == "Gerenciar / Editar Produtos":
    st.subheader("⚙️ Editar ou Excluir Produtos")
    
    df_todos = banco.listar_todos_produtos()
    
    if df_todos.empty:
        st.info("Nenhum produto cadastrado no banco.")
    else:
        opcoes_produtos = {
            f"ID {row['id']} - {row['nome']} [{row['marca'] if row['marca'] else 'Sem Marca'}] ({row['status']})": row['id']
            for _, row in df_todos.iterrows()
        }
        
        produto_sel = st.selectbox("Selecione um produto para editar/excluir", list(opcoes_produtos.keys()))
        prod_id = opcoes_produtos[produto_sel]
        
        dados_prod = df_todos[df_todos['id'] == prod_id].iloc[0]
        
        col_edit, col_del = st.columns([3, 1])
        
        with col_edit:
            st.markdown("### Editar Dados")
            with st.form("form_edicao"):
                col1, col2 = st.columns(2)
                with col1:
                    novo_nome = st.text_input("Nome", value=dados_prod['nome'])
                    nova_marca = st.text_input("Marca", value=dados_prod['marca'] if dados_prod['marca'] else "")
                    
                    cats = ["Camisa", "Calça", "Casaco", "Vestido", "Acessório", "Calçado", "Outros"]
                    cat_idx = cats.index(dados_prod['categoria']) if dados_prod['categoria'] in cats else 0
                    nova_cat = st.selectbox("Categoria", cats, index=cat_idx)
                    
                    novo_tam = st.text_input("Tamanho", value=dados_prod['tamanho'] if dados_prod['tamanho'] else "")
                
                with col2:
                    novo_custo = st.number_input("Custo (R$)", min_value=0.0, value=float(dados_prod['preco_custo']), step=1.0)
                    novo_venda = st.number_input("Venda (R$)", min_value=0.0, value=float(dados_prod['preco_venda']), step=1.0)
                    
                    statuses = ["disponivel", "vendido", "reservado"]
                    status_idx = statuses.index(dados_prod['status']) if dados_prod['status'] in statuses else 0
                    novo_status = st.selectbox("Status", statuses, index=status_idx)
                    
                    nova_desc = st.text_area("Descrição", value=dados_prod['descricao'] if dados_prod['descricao'] else "")
                
                if st.form_submit_button("Atualizar Produto"):
                    banco.atualizar_produto(prod_id, novo_nome, nova_marca, nova_desc, novo_tam, nova_cat, novo_custo, novo_venda, novo_status)
                    st.success("Produto atualizado com sucesso!")
                    st.rerun()

        with col_del:
            st.markdown("### Excluir")
            st.warning("⚠️ Cuidado: A exclusão removerá o produto e o histórico de venda dele.")
            if st.button("🔴 Excluir Produto", key="btn_excluir"):
                banco.excluir_produto(prod_id)
                st.success("Produto excluído com sucesso!")
                st.rerun()
                
        st.markdown("---")
        st.markdown("### Tabela Completa de Estoque")
        st.dataframe(df_todos, use_container_width=True)

# --- OPÇÃO 3: REGISTRAR VENDA ---
elif menu == "Registrar Venda":
    st.subheader("💰 Registrar Venda")
    
    df_disponiveis = banco.listar_produtos_disponiveis()
    
    if df_disponiveis.empty:
        st.info("Nenhum produto disponível no momento.")
    else:
        opcoes_produtos = {
            f"ID {row['id']} - {row['nome']} [{row['marca'] if row['marca'] else 'Sem marca'}] (R$ {row['preco_venda']:.2f})": row['id']
            for _, row in df_disponiveis.iterrows()
        }
        
        produto_selecionado = st.selectbox("Selecione o Produto", list(opcoes_produtos.keys()))
        produto_id = opcoes_produtos[produto_selecionado]
        
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

# --- OPÇÃO 4: REGISTRAR GASTOS ---
elif menu == "Registrar Gastos":
    st.subheader("💸 Gastos e Despesas da Empresa")
    
    col_form, col_lista = st.columns([1, 1.5])
    
    with col_form:
        st.markdown("### Lançar Novo Gasto")
        with st.form("form_gasto", clear_on_submit=True):
            desc_gasto = st.text_input("Descrição (Ex: Sacolas, Uber para Garimpo)")
            cat_gasto = st.selectbox("Categoria do Gasto", ["Embalagens", "Transporte / Frete", "Marketing / Fotos", "Aluguel / Feiras", "Taxas", "Outros"])
            valor_gasto = st.number_input("Valor do Gasto (R$)", min_value=0.0, step=1.0)
            
            if st.form_submit_button("Salvar Gasto"):
                if desc_gasto and valor_gasto > 0:
                    banco.cadastrar_gasto(desc_gasto, cat_gasto, valor_gasto)
                    st.success("Gasto registrado com sucesso!")
                    st.rerun()
                else:
                    st.error("Informe a descrição e um valor maior que zero.")

    with col_lista:
        st.markdown("### Histórico de Despesas")
        df_gastos = banco.listar_gastos()
        if not df_gastos.empty:
            st.dataframe(df_gastos, use_container_width=True)
            
            gasto_excluir = st.selectbox("Selecione um gasto para remover", df_gastos['id'].tolist(), format_func=lambda x: f"ID {x} - {df_gastos[df_gastos['id']==x]['descricao'].values[0]}")
            if st.button("Remover Gasto Selecionado"):
                banco.excluir_gasto(gasto_excluir)
                st.success("Gasto removido!")
                st.rerun()
        else:
            st.info("Nenhum gasto cadastrado.")

# --- OPÇÃO 5: RELATÓRIO FINANCEIRO ---
elif menu == "Relatório Financeiro":
    st.subheader("📊 Balanço Financeiro Geral")
    
    df_vendas = banco.relatorio_vendas()
    df_gastos = banco.listar_gastos()
    
    faturamento_total = df_vendas['valor_vendido'].sum() if not df_vendas.empty else 0.0
    lucro_bruto_vendas = df_vendas['lucro_bruto'].sum() if not df_vendas.empty else 0.0
    total_gastos = df_gastos['valor'].sum() if not df_gastos.empty else 0.0
    
    lucro_liquido_real = lucro_bruto_vendas - total_gastos
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento (Vendas)", f"R$ {faturamento_total:.2f}")
    c2.metric("Lucro Bruto (Peças)", f"R$ {lucro_bruto_vendas:.2f}")
    c3.metric("Gastos Operacionais", f"R$ {total_gastos:.2f}")
    c4.metric("Lucro Líquido Real", f"R$ {lucro_liquido_real:.2f}", delta=f"{lucro_liquido_real:.2f}")
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🛒 Histórico de Vendas", "📉 Histórico de Gastos"])
    with tab1:
        if not df_vendas.empty:
            st.dataframe(df_vendas, use_container_width=True)
        else:
            st.info("Nenhuma venda realizada ainda.")
    
    with tab2:
        if not df_gastos.empty:
            st.dataframe(df_gastos, use_container_width=True)
        else:
            st.info("Nenhum gasto registrado.")