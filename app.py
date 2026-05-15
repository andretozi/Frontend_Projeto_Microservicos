from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return redirect(url_for("projeto_github"))

@app.route("/projeto/github")
def projeto_github():
    return render_template("projeto/projeto_github.html")

@app.route("/projeto/upload")
def projeto_upload():
    return render_template("projeto/projeto_upload.html")

@app.route("/projeto/arquivos")
def projeto_arquivos():
    return render_template("projeto/projeto_arquivos.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)