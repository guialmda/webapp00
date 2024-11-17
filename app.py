!pip install Flask Flask-SocketIO gspread oauth2client pyngrok

from google.colab import files
uploaded = files.upload()

from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Autenticação com Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("ponto-eletronico-441904-6b27668a826c.json", scope)
client = gspread.authorize(credentials)

# Acessar a planilha
sheet = client.open("Trabalho Ponto eletronico").sheet1

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO
from datetime import datetime

app = Flask(__name__)
app.secret_key = "trabalho_terca_123"  # Troque para uma string mais segura
socketio = SocketIO(app)

usuarios = {"VIni": "1234", "Willian": "1234"}  # Usuários e senhas fictícias

@app.route("/")
def home():
    if "usuario" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    usuario = request.form["usuario"]
    senha = request.form["senha"]
    if usuario in usuarios and usuarios[usuario] == senha:
        session["usuario"] = usuario
        return redirect(url_for("dashboard"))
    return "Login ou senha incorretos. Tente novamente."

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("home"))
    return render_template("dashboard.html", usuario=session["usuario"])

@app.route("/registrar", methods=["POST"])
def registrar():
    if "usuario" not in session:
        return redirect(url_for("home"))

    tipo = request.form["tipo"]  # "entrada" ou "saida"
    now = datetime.now()
    data = now.strftime("%Y-%m-%d")
    hora = now.strftime("%H:%M:%S")
    usuario = session["usuario"]

    # Obter registros atuais da planilha
    registros = sheet.get_all_records()
    registro_atual = next((r for r in registros if r["Data"] == data and r["Funcionário"] == usuario), None)

    if tipo == "entrada" and not registro_atual:
        sheet.append_row([data, usuario, hora, "", ""])
        return f"Entrada registrada para {usuario} às {hora}."
    elif tipo == "saida" and registro_atual:
        linha = registros.index(registro_atual) + 2
        sheet.update_cell(linha, 4, hora)  # Atualiza a saída
        hora_entrada = datetime.strptime(registro_atual["Entrada"], "%H:%M:%S")
        hora_saida = datetime.strptime(hora, "%H:%M:%S")
        horas_trabalhadas = str(hora_saida - hora_entrada)
        sheet.update_cell(linha, 5, horas_trabalhadas)
        return f"Saída registrada para {usuario} às {hora}. Horas trabalhadas: {horas_trabalhadas}."
    else:
        return "Registro inválido ou já existente."
