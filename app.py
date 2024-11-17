from flask import Flask, render_template, request, redirect, url_for, session
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from flask_socketio import SocketIO
import os

# Configuração do Flask
app = Flask(__name__)
app.secret_key = 'chave_secreta_para_sessao'  # Troque para uma chave segura
socketio = SocketIO(app)

# Configuração para o Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("seu_arquivo_chave.json", scope)
client = gspread.authorize(credentials)
sheet = client.open("Ponto Eletrônico").sheet1  # Certifique-se que o nome está correto

# Usuários fictícios (troque conforme necessário)
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
        sheet.append_row([usuario, "Entrada", "Horário será adicionado automaticamente"])
        return "Ponto de entrada registrado com sucesso!"
    return redirect(url_for("login"))

# Rota para registrar ponto de saída
@app.route("/ponto/saida", methods=["POST"])
def registrar_saida():
    if "usuario" in session:
        usuario = session["usuario"]
        sheet.append_row([usuario, "Saída", "Horário será adicionado automaticamente"])
        return "Ponto de saída registrado com sucesso!"
    return redirect(url_for("login"))

# Rota para logout
@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

# Integrar Flask com Ngrok (para rodar no Colab)
from pyngrok import ngrok
if __name__ == "__main__":
    public_url = ngrok.connect(5000)  # Exponha o servidor Flask
    print(f"Seu site está online: {public_url}")
    socketio.run(app, port=5000)
