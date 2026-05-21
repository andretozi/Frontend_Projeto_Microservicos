import json
import os

import asyncpg
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
DATABASE_URL = os.getenv("DATABASE_URL", "")


if not JWT_SECRET_KEY:
    print("WARNING: JWT_SECRET_KEY não configurada — todas as requisições autenticadas retornarão 401.")


def verificar_sessao_usuario(token: str) -> dict:
    if not JWT_SECRET_KEY:
        print("[auth] ERRO: JWT_SECRET_KEY vazia. Configure a variável de ambiente.")
        return {"valido": False, "erro": "Servidor sem chave JWT configurada."}
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "valido": True,
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "nome": payload.get("nome"),
        }
    except jwt.ExpiredSignatureError:
        print("[auth] Token expirado.")
        return {"valido": False, "erro": "Sessão expirada. Faça login novamente."}
    except jwt.InvalidTokenError as e:
        print(f"[auth] Token inválido: {e}")
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


@app.get("/api/projeto/{projeto_id}/artefatos")
async def api_projeto_artefatos(projeto_id: int, request: Request):
    """Lista artefatos do projeto consultando o banco diretamente."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return JSONResponse({"artefatos": [], "erro": "Não autorizado"}, status_code=401)
    token = auth.split(" ", 1)[1]
    resultado = verificar_sessao_usuario(token)
    if not resultado["valido"]:
        return JSONResponse({"artefatos": [], "erro": resultado.get("erro")}, status_code=401)

    if not DATABASE_URL:
        print("[db] DATABASE_URL não configurada.")
        return JSONResponse({"artefatos": [], "erro": "Banco não configurado"}, status_code=500)

    try:
        dsn = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        conn = await asyncpg.connect(dsn)
        try:
            rows = await conn.fetch(
                """
                SELECT id, nome_arquivo, tipo_classificado, tags, resumo,
                       data_upload, url_documento
                FROM artefatos_brutos
                WHERE projeto_id = $1
                ORDER BY data_upload DESC
                """,
                projeto_id,
            )
        finally:
            await conn.close()

        artefatos = []
        for row in rows:
            tags = row["tags"]
            if tags is None:
                tags = []
            elif isinstance(tags, str):
                try:
                    tags = json.loads(tags)
                except Exception:
                    tags = [tags]

            artefatos.append({
                "id": row["id"],
                "nome_arquivo": row["nome_arquivo"],
                "tipo": row["tipo_classificado"],
                "tags": tags,
                "resumo": row["resumo"],
                "data_upload": row["data_upload"].isoformat() if row["data_upload"] else None,
                "url_documento": row["url_documento"],
            })

        return JSONResponse({"artefatos": artefatos})

    except Exception as e:
        print(f"[db] Erro ao listar artefatos do projeto {projeto_id}: {e}")
        return JSONResponse({"artefatos": [], "erro": "Erro ao consultar banco"}, status_code=500)


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