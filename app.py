import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime
import json
import os

# Configuração do Google Sheets
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Credenciais via variável de ambiente (ou arquivo JSON local)
if "GOOGLE_CREDENTIALS" in os.environ:
    credenciais_json = os.getenv("GOOGLE_CREDENTIALS")
    credentials = Credentials.from_service_account_info(json.loads(credenciais_json), scopes=scope)
else:
    credentials = Credentials.from_service_account_file("seu_arquivo_chave.json", scopes=scope)

client = gspread.authorize(credentials)
sheet = client.open("Ponto Eletrônico").sheet1  # Certifique-se de que o nome está correto

# Usuários fictícios
usuarios = {
    "usuario1": "senha1",
    "usuario2": "senha2"
}

# Função para registrar entrada ou saída
def registrar_ponto(tipo):
    usuario = st.session_state["usuario"]
    horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([usuario, tipo, horario])
    st.success(f"Ponto de {tipo.lower()} registrado com sucesso!")

# Interface do Streamlit
st.title("Ponto Eletrônico")
st.sidebar.title("Menu de Navegação")

# Verificar se o usuário está logado
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# Página de Login
if st.session_state["usuario"] is None:
    st.sidebar.write("Por favor, faça login para continuar.")
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if usuario in usuarios and usuarios[usuario] == senha:
                st.session_state["usuario"] = usuario
                st.success(f"Bem-vindo, {usuario}!")
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha inválidos.")
else:
    # Dashboard após login
    st.sidebar.write(f"Usuário logado: {st.session_state['usuario']}")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"usuario": None}))

    st.header(f"Bem-vindo, {st.session_state['usuario']}!")

    # Botões para registrar entrada e saída
    if st.button("Registrar Entrada"):
        registrar_ponto("Entrada")

    if st.button("Registrar Saída"):
        registrar_ponto("Saída")

    # Visualizar registros da planilha
    st.subheader("Registros")
    registros = sheet.get_all_values()
    st.table(registros)
