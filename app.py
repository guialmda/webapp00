from flask import Flask, render_template, request, redirect, url_for, session
from google.oauth2.service_account import Credentials
import gspread
from flask_socketio import SocketIO
from pyngrok import ngrok
from datetime import datetime
import os
from dotenv import load_dotenv

# Configurar variáveis de ambiente
load_dotenv()

# Configuração do Flask
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave_secreta_padrao")  # Melhor armazenar no .env
socketio = SocketIO(app)

# Configuração para o Google Sheets
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credentials = Credentials.from_service_account_file("seu_arquivo_chave.json", scopes=scope)
client = gspread.authorize(credentials)
sheet = client.open("Ponto Eletrônico").sheet1  # Certifique-se que o nome está correto

# Usuários fictícios (melhor usar um banco de dados)
usuarios = {
    "usuario1": "senha1",
    "usuario2": "senha2"
}

# Rota inicial (Login)
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        if usuario in usuarios and usuarios[usuario] == senha:
            session["usuario"] = usuario
            return redirect(url_for("dashboard"))
        else:
            return "Usuário ou senha inválidos", 401
    return render_template("login.html")

# Rota do dashboard
@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", usuario=session["usuario"])

# Rota para registrar ponto de entrada
@app.route("/ponto/entrada", methods=["POST"])
def registrar_entrada():
    if "usuario" in session:
        usuario = session["usuario"]
        horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([usuario, "Entrada", horario])
        return "Ponto de entrada registrado com sucesso!"
    return redirect(url_for("login"))

# Rota para registrar ponto de saída
@app.route("/ponto/saida", methods=["POST"])
def registrar_saida():
    if "usuario" in session:
        usuario = session["usuario"]
        horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([usuario, "Saída", horario])
        return "Ponto de saída registrado com sucesso!"
    return redirect(url_for("login"))

# Rota para logout
@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

# Integrar Flask com Ngrok
if __name__ == "__main__":
    public_url = ngrok.connect(5000)
    print(f"Seu site está online: {public_url}")
    app.run(port=5000)
