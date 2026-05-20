# DocuIA - Frontend

Aplicação web em FastAPI que serve como interface para o sistema DocuIA de documentação inteligente de projetos. Consome os microsserviços de Upload, Processamento de IA e Integração com GitHub. O frontend renderiza templates Jinja2 e delega todas as chamadas de dados aos microsserviços por meio do navegador.

## Tecnologias

- Python 3.12+
- FastAPI
- Uvicorn
- Jinja2
- HTML, CSS e JavaScript (sem frameworks)
- httpx (cliente HTTP para integração com microsserviços)
- python-dotenv

## Estrutura de pastas

```
Frontend_Projeto_Microservicos/
├── main.py
├── requirements.txt
├── .env.example
├── README.md
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── projeto_arquivos.js
│   │   ├── projeto_github.js
│   │   └── projeto_upload.js
│   └── assets/
│       └── images/
└── templates/
    └── projeto/
        ├── projeto_arquivos.html
        ├── projeto_github.html
        └── projeto_upload.html
```

## Microsserviços integrados

| Serviço | URL Base | Endpoints utilizados |
|---------|----------|----------------------|
| Upload  | https://docuia-api-upload.azurewebsites.net | `POST /api/upload`, `GET /api/projetos/{id}/artefatos`, `DELETE /api/artefatos/{id}` |
| IA      | https://docuia-api-ia.azurewebsites.net | `POST /api/analisar` |
| GitHub  | https://docuia-api-github.azurewebsites.net | `POST /api/github/conectar` |

As URLs base são lidas das variáveis de ambiente correspondentes e injetadas em todos os templates através do helper `render()` definido em `main.py`. Os arquivos JavaScript consomem essas URLs via o objeto global `window.API` exposto no início de cada template.

## Variáveis de ambiente

Configuradas no arquivo `.env` (use `.env.example` como referência).

| Variável | Descrição |
|----------|-----------|
| `UPLOAD_API_URL` | URL base do microsserviço de Upload e gerenciamento de artefatos. |
| `IA_API_URL` | URL base do microsserviço de análise por Inteligência Artificial. |
| `GITHUB_API_URL` | URL base do microsserviço de integração com repositórios GitHub. |
| `PROJETOS_API_URL` | URL base do microsserviço de Projetos. Quando vazia, o frontend usa uma lista mock definida em `main.py`. |

Quando alguma variável não está definida, o `main.py` adota como padrão a URL pública do serviço hospedado na Azure.

## Instalação

1. Clonar o repositório:
   ```bash
   git clone https://github.com/andretozi/Frontend_Projeto_Microservicos.git
   cd Frontend_Projeto_Microservicos
   ```
2. Criar e ativar um ambiente virtual:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```
3. Instalar as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Copiar o arquivo de exemplo e ajustar os valores se necessário:
   ```bash
   cp .env.example .env
   ```

## Execução local

Execute o servidor a partir da raiz do projeto:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 5000
```

Acesse a aplicação em:

```
http://127.0.0.1:5000
```

O endereço `0.0.0.0` é um bind que aceita conexões em qualquer interface de rede, mas não deve ser digitado diretamente no navegador. Para acesso local utilize `127.0.0.1` ou `localhost`.

## Rotas do frontend

| Método | Rota | Template renderizado |
|--------|------|----------------------|
| GET | `/` | `projeto/projeto_github.html` (página inicial, equivalente à aba GitHub) |
| GET | `/projeto/github` | `projeto/projeto_github.html` |
| GET | `/projeto/upload` | `projeto/projeto_upload.html` |
| GET | `/projeto/arquivos` | `projeto/projeto_arquivos.html` |
| GET | `/healthcheck` | Resposta JSON com status dos microsserviços |

## Healthcheck

A rota `GET /healthcheck` realiza uma requisição HTTP (timeout de 3 segundos) para cada microsserviço configurado e devolve um JSON agregado com o status de conectividade:

```json
{
  "frontend": "ok",
  "upload_api": "ok",
  "ia_api": "ok",
  "github_api": "ok"
}
```

Cada chave assume o valor `"ok"` quando a resposta HTTP tem status inferior a 500, ou `"down"` em caso de falha, timeout ou erro 5xx.

## Endpoints pendentes de confirmação com o backend

Os endpoints abaixo são utilizados pelo frontend, mas seu contrato (path, método e formato de resposta) ainda não foi formalmente confirmado pelo time responsável pelo microsserviço de Upload:

- `GET {UPLOAD_API_URL}/api/projetos/{id}/artefatos` — listagem de artefatos de um projeto. Resposta esperada: `{ "artefatos": [{ "id", "nome_arquivo", "tipo", "tags", "resumo", "data_upload" }, ...] }`.
- `DELETE {UPLOAD_API_URL}/api/artefatos/{id}` — remoção de um artefato pelo identificador. Resposta esperada: HTTP 200 ou 204.

Ambos estão marcados com `// TODO: confirmar com backend` em `static/js/projeto_arquivos.js`.

## Convenções de organização

- Todo CSS deve residir em `static/css/style.css`. Não utilizar blocos `<style>` inline nos templates.
- Todo JavaScript deve residir em arquivos dentro de `static/js/`. Não utilizar blocos `<script>` inline nos templates (exceção: o bloco curto que expõe `window.API` antes do `<script src="...">` de cada página).
- Templates HTML em `templates/` e suas subpastas (atualmente `templates/projeto/`).
- Referências a arquivos estáticos sempre por `url_for('static', path='/...')`, conforme padrão do Starlette/FastAPI.
- URLs de microsserviços nunca devem ser hardcoded no código. Devem vir de variáveis de ambiente no backend Python e de `window.API` no JavaScript.
