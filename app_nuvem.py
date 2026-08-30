import streamlit as st
st.set_page_config(page_title="VALIDA PRO", page_icon="◈", layout="wide")

import hashlib, json, random, secrets, string, os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "data" / "auth" / "usuarios.json"
SESSION_FILE = BASE_DIR / "data" / "auth" / "session.json"
REGISTRATION_CODE_DIR = BASE_DIR / "data" / "codigo_de_cadastro"
REGISTRATION_CODE_FILE = REGISTRATION_CODE_DIR / "codigo_de_cadastro.txt"
USER_CODE_DIR = BASE_DIR / "data" / "codigos_usuarios"
CODE_LOG_FILE = REGISTRATION_CODE_DIR / "codigos_gerados.json"
DEFAULT_REGISTRATION_CODE = "CADASTRO-LOJA-2026"
SUPER_ADMIN_USERNAME = "andre.adm"
SUPER_ADMIN_PASSWORD_HASH = "f1880808edbd37087ad11bc1d14146d76e5735b15b6db29dcce8029249cc1f27"
ACCOUNT_MANAGEMENT_PASSWORD_HASH = "abd3f2ed90f684b305ed7632ee24e58ed439de9158399ce9a5952281ef804b43"
DB_CLIENTES = BASE_DIR / "clientes.csv"
DB_VALIDADES = BASE_DIR / "validades.csv"

def hash_password(senha): return hashlib.sha256(senha.encode("utf-8")).hexdigest()
def carregar_usuarios():
    if not USERS_FILE.exists(): return []
    try:
        with USERS_FILE.open("r", encoding="utf-8") as f: dados=json.load(f)
        return dados if isinstance(dados,list) else []
    except: return []
def salvar_usuarios(usuarios):
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with USERS_FILE.open("w", encoding="utf-8") as f: json.dump(usuarios,f,ensure_ascii=False,indent=2)
def usuario_existe(username): return any(u.get("username")==username for u in carregar_usuarios())
def usuario_por_username(username):
    for u in carregar_usuarios():
        if u.get("username")==username: return u
    return None
def gerar_ip_acesso(usuarios=None):
    usuarios = usuarios if usuarios is not None else carregar_usuarios()
    usados={u.get("ip_acesso") for u in usuarios if u.get("ip_acesso")}
    while True:
        codigo="".join(secrets.SystemRandom().sample("0123456789",9))
        if codigo not in usados: return codigo
def garantir_ips_acesso():
    usuarios=carregar_usuarios(); alterado=False; usados=set()
    for usuario in usuarios:
        ip=usuario.get("ip_acesso")
        if not ip or len(str(ip))!=9 or len(set(str(ip)))!=9 or str(ip) in usados:
            usuario["ip_acesso"]=gerar_ip_acesso(usuarios); alterado=True
        usados.add(usuario["ip_acesso"])
    if alterado: salvar_usuarios(usuarios)
    return usuarios
def senha_super_admin_valida(senha): return hash_password(senha)==SUPER_ADMIN_PASSWORD_HASH
def senha_gestao_contas_valida(senha): return hash_password(senha)==ACCOUNT_MANAGEMENT_PASSWORD_HASH
def carregar_codigo_cadastro():
    REGISTRATION_CODE_DIR.mkdir(parents=True, exist_ok=True)
    if not REGISTRATION_CODE_FILE.exists():
        with REGISTRATION_CODE_FILE.open("w",encoding="utf-8") as f: f.write(DEFAULT_REGISTRATION_CODE)
        return DEFAULT_REGISTRATION_CODE
    try:
        with REGISTRATION_CODE_FILE.open("r",encoding="utf-8") as f: codigo=f.read().strip()
        return codigo or DEFAULT_REGISTRATION_CODE
    except: return DEFAULT_REGISTRATION_CODE
def salvar_codigo_cadastro(codigo):
    REGISTRATION_CODE_DIR.mkdir(parents=True, exist_ok=True)
    codigo_limpo=(codigo or DEFAULT_REGISTRATION_CODE).strip()
    with REGISTRATION_CODE_FILE.open("w",encoding="utf-8") as f: f.write(codigo_limpo)
    return codigo_limpo
def validar_codigo_cadastro(codigo): return (codigo or "").strip().upper()==carregar_codigo_cadastro().upper()
def _carregar_codigos_gerados():
    REGISTRATION_CODE_DIR.mkdir(parents=True, exist_ok=True)
    if not CODE_LOG_FILE.exists(): return []
    try:
        with CODE_LOG_FILE.open("r",encoding="utf-8") as h: dados=json.load(h)
        return dados if isinstance(dados,list) else []
    except: return []
def _salvar_codigos_gerados(codigos):
    REGISTRATION_CODE_DIR.mkdir(parents=True, exist_ok=True)
    with CODE_LOG_FILE.open("w",encoding="utf-8") as h: json.dump(codigos,h,ensure_ascii=False,indent=2)
def gerar_codigo_cadastro(tamanho=8):
    letras=string.ascii_uppercase+string.digits
    codigos=_carregar_codigos_gerados(); usados={i.get("codigo") for i in codigos if i.get("codigo")}
    while True:
        codigo="".join(random.choice(letras) for _ in range(tamanho))
        if codigo not in usados:
            codigos.append({"codigo":codigo,"login":"pendente","status":"pendente"})
            _salvar_codigos_gerados(codigos)
            return salvar_codigo_cadastro(codigo)

# INIT
garantir_ips_acesso()
if not DB_CLIENTES.exists(): pd.DataFrame(columns=["ID","Nome","CNPJ","Contato","Data_Cadastro"]).to_csv(DB_CLIENTES,index=False)
if not DB_VALIDADES.exists(): pd.DataFrame(columns=["ID","Cliente","Produto","Lote","Validade","Status"]).to_csv(DB_VALIDADES,index=False)

if "logado" not in st.session_state: st.session_state.logado=False
if "usuario" not in st.session_state: st.session_state.usuario=None
if "tela" not in st.session_state: st.session_state.tela="menu"

# LOGIN NAO FEITO
if not st.session_state.logado:
    st.title("◈ VALIDA PRO - Acesso ao Sistema")
    if st.session_state.tela=="menu":
        st.subheader("Escolha uma opção")
        c1,c2=st.columns(2)
        if c1.button("Acessar conta",type="primary",use_container_width=True): st.session_state.tela="login"; st.rerun()
        if c2.button("Criar conta",use_container_width=True): st.session_state.tela="cadastro"; st.rerun()
        st.info(f"Código atual: {carregar_codigo_cadastro()} | Super Admin: {SUPER_ADMIN_USERNAME}")

    elif st.session_state.tela=="login":
        st.subheader("Acessar conta")
        user=st.text_input("Usuário")
        senha=st.text_input("Senha",type="password")
        if st.button("Entrar",type="primary"):
            u=usuario_por_username(user)
            if u and (u.get("password")==senha or u.get("password")==hash_password(senha)):
                if u.get("bloqueado"): st.error("Usuário bloqueado")
                else:
                    st.session_state.logado=True; st.session_state.usuario=user; st.session_state.role=u.get("role","user"); st.rerun()
            else: st.error("Usuário ou senha inválidos")
        if st.button("Voltar"): st.session_state.tela="menu"; st.rerun()

    elif st.session_state.tela=="cadastro":
        st.subheader("Criar conta - Precisa do código de cadastro")
        username=st.text_input("Novo usuário")
        codigo=st.text_input("Código de cadastro")
        senha=st.text_input("Senha",type="password")
        senha2=st.text_input("Confirmar senha",type="password")
        senha_auth=st.text_input("Senha de autorização do ADM",type="password")
        if st.button("Criar conta ADMIN",type="primary"):
            if not senha_super_admin_valida(senha_auth): st.error("Senha de autorização inválida")
            elif not validar_codigo_cadastro(codigo): st.error("Código de cadastro inválido")
            elif senha!=senha2: st.error("Senhas não conferem")
            elif usuario_existe(username): st.error("Usuário já existe")
            else:
                us=carregar_usuarios()
                us.append({"username":username,"password":hash_password(senha),"role":"admin","ip_acesso":gerar_ip_acesso(us)})
                salvar_usuarios(us)
                st.success("Conta criada!"); st.session_state.tela="login"; st.rerun()
        if st.button("Voltar"): st.session_state.tela="menu"; st.rerun()
    st.stop()

# LOGADO - APP PRINCIPAL
st.sidebar.title(f"◈ VALIDA PRO")
st.sidebar.success(f"Logado: {st.session_state.usuario} ({st.session_state.role})")
if st.sidebar.button("Sair"): st.session_state.logado=False; st.session_state.tela="menu"; st.rerun()

if st.session_state.role=="admin" or st.session_state.usuario==SUPER_ADMIN_USERNAME:
    st.sidebar.divider()
    st.sidebar.subheader("Admin")
    if st.sidebar.button("Gerar novo código de cadastro"):
        novo=gerar_codigo_cadastro()
        st.sidebar.success(f"Novo código: {novo}")
    st.sidebar.code(f"Atual: {carregar_codigo_cadastro()}")

menu=st.sidebar.radio("Menu",["Dashboard","Clientes","Controle de Validades","Etiquetas","Usuários (ADM)"])

if menu=="Dashboard":
    st.title("Dashboard"); df_val=pd.read_csv(DB_VALIDADES); df_cli=pd.read_csv(DB_CLIENTES)
    c1,c2,c3=st.columns(3); c1.metric("Clientes",len(df_cli)); c2.metric("Produtos",len(df_val))
    if not df_val.empty:
        df_val["Validade"]=pd.to_datetime(df_val["Validade"])
        vencidos=df_val[df_val["Validade"]<datetime.now()]
        c3.metric("Vencidos",len(vencidos))
        st.dataframe(df_val.sort_values("Validade"),use_container_width=True)

elif menu=="Clientes":
    st.title("Clientes"); 
    with st.form("form_cli"):
        nome=st.text_input("Nome"); cnpj=st.text_input("CNPJ"); contato=st.text_input("Contato")
        if st.form_submit_button("Salvar",type="primary") and nome:
            df=pd.read_csv(DB_CLIENTES); novo=pd.DataFrame([[len(df)+1,nome,cnpj,contato,datetime.now().strftime("%d/%m/%Y")]],columns=df.columns)
            pd.concat([df,novo]).to_csv(DB_CLIENTES,index=False); st.success("Salvo"); st.rerun()
    st.dataframe(pd.read_csv(DB_CLIENTES),use_container_width=True)

elif menu=="Controle de Validades":
    st.title("Controle de Validades")
    df_cli=pd.read_csv(DB_CLIENTES); lista=df_cli["Nome"].tolist() if not df_cli.empty else ["Avulso"]
    with st.form("form_val"):
        cliente=st.selectbox("Cliente",lista); produto=st.text_input("Produto"); lote=st.text_input("Lote")
        validade=st.date_input("Validade")
        if st.form_submit_button("Cadastrar",type="primary") and produto:
            df=pd.read_csv(DB_VALIDADES)
            novo=pd.DataFrame([[len(df)+1,cliente,produto,lote,validade.strftime("%Y-%m-%d"),"OK"]],columns=df.columns)
            pd.concat([df,novo]).to_csv(DB_VALIDADES,index=False); st.success("Cadastrado"); st.rerun()
    st.dataframe(pd.read_csv(DB_VALIDADES),use_container_width=True)

elif menu=="Usuários (ADM)":
    st.title("Gestão de Contas - Super Admin")
    st.json(carregar_usuarios())
