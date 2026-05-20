import os

import httpx
import jwt
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

load_dotenv()

# URLs dos microsserviços (defaults apontam pra Azure pra funcionar mesmo sem .env)
UPLOAD_API_URL = os.getenv("UPLOAD_API_URL", "https://docuia-api-upload.azurewebsites.net")
IA_API_URL = os.getenv("IA_API_URL", "https://docuia-api-ia.azurewebsites.net")
GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://docuia-api-github.azurewebsites.net")
FRONT_PRINCIPAL_URL = os.getenv("FRONT_PRINCIPAL_URL", "https://docuia-frontend-hdc8hzfqbqebc6cp.brazilsouth-01.azurewebsites.net")
PROJETOS_SERVICE_URL = os.getenv("PROJETOS_SERVICE_URL", "https://docuia-projetos-hffafgcsgkh0h3au.brazilsouth-01.azurewebsites.net")
LOGIN_URL = os.getenv("LOGIN_URL", "https://docuia-frontend-hdc8hzfqbqebc6cp.brazilsouth-01.azurewebsites.net/login")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


def verificar_sessao_usuario(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "valido": True,
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "nome": payload.get("nome"),
        }
    except jwt.ExpiredSignatureError:
        return {"valido": False, "erro": "Sessão expirada. Faça login novamente."}
    except jwt.InvalidTokenError:
        return {"valido": False, "erro": "Token de autenticação inválido."}


app = FastAPI(title="Frontend - DocuIA")

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def render(template: str, request: Request, **extra):
    """Injeta as URLs dos microsserviços em todos os templates."""
    context = {
        "request": request,
        "UPLOAD_API_URL": UPLOAD_API_URL,
        "IA_API_URL": IA_API_URL,
        "GITHUB_API_URL": GITHUB_API_URL,
        "FRONT_PRINCIPAL_URL": FRONT_PRINCIPAL_URL,
        "LOGIN_URL": LOGIN_URL,
        **extra,
    }
    return templates.TemplateResponse(template, context)


# ── Rotas de renderização de tela ──────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return render("projeto/projeto_github.html", request)

@app.get("/projeto/github", response_class=HTMLResponse)
async def projeto_github(request: Request):
    return render("projeto/projeto_github.html", request)

@app.get("/projeto/upload", response_class=HTMLResponse)
async def projeto_upload(request: Request):
    return render("projeto/projeto_upload.html", request)

@app.get("/projeto/arquivos", response_class=HTMLResponse)
async def projeto_arquivos(request: Request):
    return render("projeto/projeto_arquivos.html", request)


# ── Rotas de API internas ──────────────────────────────────────────────────

@app.get("/api/validar-sessao")
async def api_validar_sessao(request: Request):
    """Valida o JWT no servidor (a chave nunca é exposta ao JS)."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return JSONResponse({"valido": False, "redirect": LOGIN_URL}, status_code=401)
    token = auth.split(" ", 1)[1]
    resultado = verificar_sessao_usuario(token)
    if not resultado["valido"]:
        return JSONResponse(
            {"valido": False, "redirect": LOGIN_URL, "erro": resultado.get("erro")},
            status_code=401,
        )
    return JSONResponse(resultado)


@app.get("/api/projeto/{projeto_id}/nome")
async def api_projeto_nome(projeto_id: int, request: Request):
    """Busca o nome do projeto no microsserviço Projetos."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return JSONResponse({"nome": None, "fallback": projeto_id}, status_code=401)
    token = auth.split(" ", 1)[1]
    resultado = verificar_sessao_usuario(token)
    if not resultado["valido"]:
        return JSONResponse({"nome": None, "fallback": projeto_id}, status_code=401)

    if not PROJETOS_SERVICE_URL:
        return JSONResponse({"nome": None, "fallback": projeto_id})

    paths = [
        f"{PROJETOS_SERVICE_URL}/projetos/{projeto_id}",
        f"{PROJETOS_SERVICE_URL}/api/projetos/{projeto_id}",
    ]
    headers = {"Authorization": auth}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for path in paths:
            try:
                r = await client.get(path, headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    nome = data.get("nome") or data.get("name") or data.get("titulo")
                    if nome:
                        print(f"[projetos] Endpoint OK: {path}")
                        return JSONResponse({"nome": nome})
            except Exception as e:
                print(f"[projetos] Erro em {path}: {e}")

    print(f"[projetos] Nenhum endpoint respondeu. Usando fallback id={projeto_id}")
    return JSONResponse({"nome": None, "fallback": projeto_id})


# ── Healthcheck ────────────────────────────────────────────────────────────

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