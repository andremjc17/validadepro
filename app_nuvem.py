import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# TEM QUE SER A PRIMEIRA LINHA DE COMANDO
st.set_page_config(page_title="VALIDA PRO", page_icon="◈", layout="wide")

# --- BANCO DE DADOS SIMPLES (CSV) ---
DB_CLIENTES = "clientes.csv"
DB_VALIDADES = "validades.csv"

def init_db():
    if not os.path.exists(DB_CLIENTES):
        pd.DataFrame(columns=["ID", "Nome", "CNPJ", "Contato", "Data_Cadastro"]).to_csv(DB_CLIENTES, index=False)
    if not os.path.exists(DB_VALIDADES):
        pd.DataFrame(columns=["ID", "Cliente", "Produto", "Lote", "Validade", "Status"]).to_csv(DB_VALIDADES, index=False)

init_db()

# --- LOGIN ---
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("◈ VALIDA PRO")
    st.subheader("Acesso Restrito")
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("Email", value="andre.djs")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar", type="primary", use_container_width=True):
            if email and senha:
                st.session_state.logado = True
                st.session_state.usuario = email
                st.rerun()
            else:
                st.error("Preencha os campos")
    st.stop()

# --- APP LOGADO ---
st.sidebar.title(f"◈ VALIDA PRO")
st.sidebar.success(f"Logado: {st.session_state.usuario}")
if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

menu = st.sidebar.radio("Menu", ["Dashboard", "Clientes", "Controle de Validades", "Etiquetas"])

if menu == "Dashboard":
    st.title("Dashboard")
    df_val = pd.read_csv(DB_VALIDADES)
    df_cli = pd.read_csv(DB_CLIENTES)

    c1, c2, c3 = st.columns(3)
    c1.metric("Clientes", len(df_cli))
    c2.metric("Produtos Cadastrados", len(df_val))

    if not df_val.empty:
        df_val["Validade"] = pd.to_datetime(df_val["Validade"])
        vencidos = df_val[df_val["Validade"] < datetime.now()]
        c3.metric("Vencidos", len(vencidos), delta_color="inverse")
        st.subheader("Próximos a vencer (7 dias)")
        proximos = df_val[(df_val["Validade"] >= datetime.now()) & (df_val["Validade"] <= datetime.now() + timedelta(days=7))]
        st.dataframe(proximos, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado ainda.")

elif menu == "Clientes":
    st.title("Cadastro de Clientes")
    with st.form("form_cliente"):
        nome = st.text_input("Nome da Empresa / Cliente")
        cnpj = st.text_input("CNPJ / CPF")
        contato = st.text_input("WhatsApp / Contato")
        enviar = st.form_submit_button("Salvar Cliente", type="primary")
        if enviar and nome:
            df = pd.read_csv(DB_CLIENTES)
            novo_id = len(df) + 1
            novo = pd.DataFrame([[novo_id, nome, cnpj, contato, datetime.now().strftime("%d/%m/%Y")]], columns=df.columns)
            df = pd.concat([df, novo], ignore_index=True)
            df.to_csv(DB_CLIENTES, index=False)
            st.success(f"Cliente {nome} salvo!")
            st.rerun()

    st.divider()
    st.subheader("Clientes Cadastrados")
    st.dataframe(pd.read_csv(DB_CLIENTES), use_container_width=True)

elif menu == "Controle de Validades":
    st.title("Controle de Validades")
    df_cli = pd.read_csv(DB_CLIENTES)
    clientes_lista = df_cli["Nome"].tolist() if not df_cli.empty else ["Cliente Avulso"]

    with st.form("form_validade"):
        cliente = st.selectbox("Cliente", clientes_lista)
        produto = st.text_input("Nome do Produto")
        lote = st.text_input("Lote")
        validade = st.date_input("Data de Validade", min_value=datetime.now().date())
        enviar = st.form_submit_button("Cadastrar Produto", type="primary")
        if enviar and produto:
            df = pd.read_csv(DB_VALIDADES)
            novo_id = len(df) + 1
            status = "OK"
            novo = pd.DataFrame([[novo_id, cliente, produto, lote, validade.strftime("%Y-%m-%d"), status]], columns=df.columns)
            df = pd.concat([df, novo], ignore_index=True)
            df.to_csv(DB_VALIDADES, index=False)
            st.success("Produto cadastrado!")
            st.rerun()

    st.divider()
    df_val = pd.read_csv(DB_VALIDADES)
    if not df_val.empty:
        df_val["Validade"] = pd.to_datetime(df_val["Validade"])
        df_val["Dias_Restantes"] = (df_val["Validade"] - datetime.now()).dt.days
        def cor_status(dias):
            if dias < 0: return "🔴 VENCIDO"
            if dias <= 7: return "🟡 VENCE EM BREVE"
            return "🟢 OK"
        df_val["Alerta"] = df_val["Dias_Restantes"].apply(cor_status)
        st.dataframe(df_val.sort_values("Validade"), use_container_width=True)

        csv = df_val.to_csv(index=False).encode('utf-8')
        st.download_button("Baixar Relatório Excel/CSV", csv, "validades.csv", "text/csv")

elif menu == "Etiquetas":
    st.title("Gerador de Etiquetas")
    st.info("Digite o produto para gerar a etiqueta com validade.")
    produto = st.text_input("Produto")
    lote = st.text_input("Lote", key="lote_et")
    validade = st.date_input("Validade", key="val_et")
    if st.button("Gerar Etiqueta"):
        st.markdown(f"""
        <div style="border:2px dashed black; padding:20px; width:350px; text-align:center">
            <h2>{produto}</h2>
            <p><b>Lote:</b> {lote}</p>
            <p><b>Validade:</b> {validade.strftime('%d/%m/%Y')}</p>
            <p>◈ VALIDA PRO</p>
        </div>
        """, unsafe_allow_html=True)
