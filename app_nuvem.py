import streamlit as st

st.set_page_config(page_title="VALIDA PRO", page_icon="◈", layout="centered")

st.title("◈ VALIDA PRO - Teste na Nuvem")
st.success("Se você está vendo isso em validadepro.streamlit.app, está na nuvem!")

st.subheader("Login")
email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if st.button("Entrar", type="primary"):
    if email and senha:
        st.balloons()
        st.success(f"Bem-vindo! Logado como {email}")
    else:
        st.error("Preencha email e senha")
