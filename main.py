import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Frontend - DocuIA")

# Monta a pasta estática para o CSS e Imagens funcionarem
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configura a pasta onde estão os HTMLs
templates = Jinja2Templates(directory="templates")

# Rotas de renderização de tela (equivalentes ao que estava no Flask)
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Redireciona a raiz para a tela do GitHub
    return templates.TemplateResponse("projeto/projeto_github.html", {"request": request})

@app.get("/projeto/github", response_class=HTMLResponse)
async def projeto_github(request: Request):
    return templates.TemplateResponse("projeto/projeto_github.html", {"request": request})

@app.get("/projeto/upload", response_class=HTMLResponse)
async def projeto_upload(request: Request):
    return templates.TemplateResponse("projeto/projeto_upload.html", {"request": request})

@app.get("/projeto/arquivos", response_class=HTMLResponse)
async def projeto_arquivos(request: Request):
    return templates.TemplateResponse("projeto/projeto_arquivos.html", {"request": request})

if __name__ == "__main__":
    # O Front-end vai rodar na porta 5000 para não conflitar com os outros
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)