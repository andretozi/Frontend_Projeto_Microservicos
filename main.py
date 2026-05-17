import os

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

load_dotenv()

# URLs dos microsserviços na Azure (defaults apontam pra Azure pra funcionar mesmo sem .env)
UPLOAD_API_URL = os.getenv("UPLOAD_API_URL", "https://docuia-api-upload.azurewebsites.net")
IA_API_URL = os.getenv("IA_API_URL", "https://docuia-api-ia.azurewebsites.net")
GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://docuia-api-github.azurewebsites.net")
FRONT_PRINCIPAL_URL = os.getenv("FRONT_PRINCIPAL_URL", "https://docuia-frontend-hdc8hzfqbqebc6cp.brazilsouth-01.azurewebsites.net")

# TODO: trocar por chamada à API do ms3_projetos quando estiver pronta
PROJETOS_API_URL = os.getenv("PROJETOS_API_URL", "")

PROJETOS_MOCK = [
    {"id": 1, "nome": "Sistema E-commerce"},
    {"id": 2, "nome": "App Mobile Delivery"},
    {"id": 3, "nome": "Dashboard Analytics"},
    {"id": 4, "nome": "Portal Interno RH"},
]

async def get_projetos():
    if not PROJETOS_API_URL:
        return PROJETOS_MOCK
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{PROJETOS_API_URL}/projetos", timeout=5.0)
        r.raise_for_status()
        return r.json()

app = FastAPI(title="Frontend - DocuIA")

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# Monta a pasta estática para o CSS e Imagens funcionarem
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configura a pasta onde estão os HTMLs
templates = Jinja2Templates(directory="templates")


def render(template: str, request: Request, **extra):
    """Injeta as URLs dos microsserviços em todos os templates."""
    context = {
        "request": request,
        "UPLOAD_API_URL": UPLOAD_API_URL,
        "IA_API_URL": IA_API_URL,
        "GITHUB_API_URL": GITHUB_API_URL,
        "FRONT_PRINCIPAL_URL": FRONT_PRINCIPAL_URL,
        **extra,
    }
    return templates.TemplateResponse(template, context)


# Rotas de renderização de tela
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Redireciona a raiz para a tela do GitHub
    return render("projeto/projeto_github.html", request)

@app.get("/projeto/github", response_class=HTMLResponse)
async def projeto_github(request: Request):
    return render("projeto/projeto_github.html", request)

@app.get("/projeto/upload", response_class=HTMLResponse)
async def projeto_upload(request: Request):
    projetos = await get_projetos()
    return render("projeto/projeto_upload.html", request, projetos=projetos)

@app.get("/projeto/arquivos", response_class=HTMLResponse)
async def projeto_arquivos(request: Request):
    return render("projeto/projeto_arquivos.html", request)


@app.get("/healthcheck")
async def healthcheck():
    """Pinga cada microsserviço (timeout 3s) e devolve status agregado."""
    alvos = {
        "upload_api": UPLOAD_API_URL,
        "ia_api": IA_API_URL,
        "github_api": GITHUB_API_URL,
    }
    resultado = {"frontend": "ok"}
    async with httpx.AsyncClient(timeout=3.0) as client:
        for chave, url in alvos.items():
            if not url:
                resultado[chave] = "down"
                continue
            try:
                r = await client.get(url)
                resultado[chave] = "ok" if r.status_code < 500 else "down"
            except Exception:
                resultado[chave] = "down"
    return JSONResponse(resultado)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=5000,
        reload=True,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )