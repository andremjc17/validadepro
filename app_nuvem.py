st.title("◈ VALIDA PRO - Teste na Nuvem")

st.set_page_config(page_title="Valida Pro", layout="wide")

st.title("◈ VALIDA PRO")
st.write("Se você está vendo isso, a nuvem funcionou!")

usuario = st.text_input("Usuário")
senha = st.text_input("Senha", type="password")

if st.button("Entrar"):
    st.success(f"Bem-vindo {usuario}! Agora vamos conectar com seu sistema real.")

st.divider()
st.info("Esse é só um teste. Depois que rodar, colamos seu código real de login aqui.")
