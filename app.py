from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# AUTENTICAÇÃO

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

# DASHBOARD

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard/dashboard.html")

@app.route("/perfil")
def perfil():
    return render_template("dashboard/perfil.html")

@app.route("/empresas")
def empresas():
    return render_template("dashboard/lista_empresas.html")

@app.route("/projetos")
def projetos():
    return render_template("dashboard/lista_projetos.html")


# EMPRESA

@app.route("/empresa")
def empresa():
    return render_template("empresa/empresa.html")

@app.route("/empresa/membros")
def empresa_membros():
    return render_template("empresa/empresa_membros.html")

@app.route("/empresa/solicitacoes")
def empresa_solicitacoes():
    return render_template("empresa/empresa_solicitacoes.html")

@app.route("/empresa/configuracoes")
def empresa_configuracoes():
    return render_template("empresa/empresa_configuracoes.html")


# PROJETO (Pasta: projeto)

@app.route("/projeto")
def projeto():
    return render_template("projeto/projeto.html")

@app.route("/projeto/membros")
def projeto_membros():
    return render_template("projeto/projeto_membros.html")

@app.route("/projeto/solicitacoes")
def projeto_solicitacoes():
    return render_template("projeto/projeto_solicitacoes.html")

@app.route("/projeto/configuracoes")
def projeto_configuracoes():
    return render_template("projeto/projeto_configuracoes.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)