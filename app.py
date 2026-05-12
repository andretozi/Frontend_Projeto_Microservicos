from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("dashboard"))
    return render_template("auth/login.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        return redirect(url_for("login"))
    return render_template("auth/cadastro.html")

@app.route("/esqueceu-senha", methods=["GET", "POST"])
def esqueceu_senha():
    if request.method == "POST":
        return redirect(url_for("confirmacao_senha"))
    return render_template("auth/esqueceu_senha.html")

@app.route("/confirmacao-senha")
def confirmacao_senha():
    return render_template("auth/confirmacao_senha.html")

@app.route("/criar-senha", methods=["GET", "POST"])
def criar_senha():
    if request.method == "POST":
        return redirect(url_for("login"))
    return render_template("auth/criar_senha.html")

# --- DASHBOARD ---
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard/dashboard.html")

@app.route("/perfil")
def perfil():
    return render_template("dashboard/perfil.html")

# --- PROJETO ---
@app.route("/projeto")
def projeto():
    return render_template("projeto/projeto.html")

@app.route("/projeto/membros")
def projeto_membros():
    return render_template("projeto/projeto_membros.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)