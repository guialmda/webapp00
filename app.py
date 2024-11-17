import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Definir usuários e senhas (em um ambiente real, isso seria mais seguro)
USUARIOS = {
    "usuario1": "senha1",
    "usuario2": "senha2"
}

# Função para autenticar no Google Sheets
def autenticar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("caminho/para/sua/chave.json", scope)
    client = gspread.authorize(creds)
    return client

# Função para registrar o ponto na planilha
def registrar_ponto(nome):
    # Acessa a planilha
    client = autenticar_google_sheets()
    sheet = client.open("Nome_da_sua_planilha").sheet1

    # Pega a data e hora atual
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
    hora_atual = datetime.datetime.now().strftime("%H:%M:%S")

    # Adiciona os dados na planilha
    sheet.append_row([nome, data_atual, hora_atual])

# Função de login
def fazer_login():
    st.title("Login - Batedor de Ponto Eletrônico")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario in USUARIOS and USUARIOS[usuario] == senha:
            st.session_state.usuario = usuario
            st.success(f"Bem-vindo, {usuario}!")
        else:
            st.error("Usuário ou senha inválidos!")

# Função principal
def app():
    if "usuario" not in st.session_state:
        fazer_login()
    else:
        st.title(f"Batedor de Ponto Eletrônico - {st.session_state.usuario}")
        
        # Opção para registrar o ponto
        if st.button("Registrar Ponto"):
            registrar_ponto(st.session_state.usuario)
            st.success(f"Ponto registrado com sucesso para {st.session_state.usuario}!")

# Executar o app
if __name__ == "__main__":
    app()

