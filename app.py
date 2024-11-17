from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import gspread
from pyngrok import ngrok

# Configuração do Flask
app = Flask(__name__)
app.secret_key = "chave_secreta_segura"  # Alterar para algo seguro
socketio = SocketIO(app)

# Configuração do Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("seu_arquivo_chave.json", scope)
client = gspread.authorize(credentials)
sheet = client.open("Ponto Eletrônico").sheet1

# Simulação de usuários (login)
usuarios = {"joao": "1234", "maria": "5678"}  # Usuários fictícios

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

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("home"))

# Iniciar servidor com ngrok
if __name__ == "__main__":
    public_url = ngrok.connect(5000)
    print(f"Seu site está online: {public_url}")
    socketio.run(app, port=5000)

