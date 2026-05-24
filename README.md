# DocuIA — Front-Cliente

## DocuIA — visão geral

DocuIA é uma plataforma de **documentação inteligente de projetos**: usuários conectam repositórios GitHub e enviam documentos (PDF, DOCX, imagens, diagramas), e uma IA classifica cada artefato em **tipo**, gera **tags** e um **resumo**. Toda a informação extraída fica vinculada ao projeto, ao usuário e à empresa, com persistência em PostgreSQL e arquivos em Azure Blob Storage.

A plataforma é dividida em **microsserviços independentes**: cada front e cada API mora num repositório próprio, faz deploy próprio na Azure App Service, e se comunica via HTTP autenticado com JWT.

## Onde este repo se encaixa

Este repositório é o **front-cliente**: a parte da interface que serve as três telas internas de um projeto:

| Rota | Tela | O que faz |
|---|---|---|
| `GET /projeto/github` | Repositórios GitHub | Conecta um repositório (público ou privado com PAT) ao `ms-api-github`. |
| `GET /projeto/upload` | Upload de Documentos | Envia arquivos pro `ms-ingestao-upload`, que extrai texto, classifica via `ms-api-ia` e persiste. |
| `GET /projeto/arquivos` | Arquivos Processados | Lista, filtra, faz preview e exclui artefatos do projeto. |

Não tem login, dashboard, listagem de empresas/projetos — esse é o papel do **front principal**. O usuário chega aqui vindo do front principal, que monta a URL no formato:

```
https://front-cliente.azurewebsites.net/projeto/upload?id=<projeto_id>&token=<jwt>
```

O `sessao.js` lê `id` e `token`, valida o JWT no client, guarda em `localStorage` e limpa a query string. A partir daí, todas as chamadas aos microsserviços vão direto do browser com `Authorization: Bearer <token>`.

## Arquitetura completa do ecossistema

| Componente | URL default |
|---|---|
| Front principal (login / dashboard / empresas / projetos) | `https://docuia-frontend-hdc8hzfqbqebc6cp.brazilsouth-01.azurewebsites.net` |
| **Front-cliente (este repo)** | `https://front-cliente.azurewebsites.net` |
| `ms-ingestao-upload` | `https://docuia-api-upload.azurewebsites.net` |
| `ms-api-ia` | `https://docuia-api-ia.azurewebsites.net` |
| `ms-api-github` | `https://docuia-api-github.azurewebsites.net` |
| `ms-projetos` | `https://docuia-projetos-hffafgcsgkh0h3au.brazilsouth-01.azurewebsites.net` |
| PostgreSQL + Azure Blob Storage | persistência (gerenciados) |

## Diagrama de fluxo

```mermaid
flowchart LR
    U[Usuário] --> FP[Front Principal]
    FP -->|"?id=projeto_id&token=jwt"| FC[Front-Cliente<br/>este repo]

    FC -->|POST /api/upload| MSU[ms-ingestao-upload]
    FC -->|GET /api/projeto/{id}/artefatos| MSU
    FC -->|DELETE /api/artefatos/{id}| MSU
    FC -->|POST /api/github/conectar| MSG[ms-api-github]

    MSU -->|texto do documento| MSI[ms-api-ia]
    MSI -->|tipo + tags + resumo| MSU
    MSG -->|arquivos do repo| MSI

    MSU --> PG[(PostgreSQL)]
    MSU --> AB[(Azure Blob)]
    MSG --> PG
    FP --> MSP[ms-projetos]
    MSP --> PG
```

## Variáveis de ambiente

| Nome | Descrição | Default |
|---|---|---|
| `UPLOAD_API_URL` | Base do `ms-ingestao-upload` (upload, listagem e exclusão de artefatos). | `https://docuia-api-upload.azurewebsites.net` |
| `IA_API_URL` | Base do `ms-api-ia` (classificação de documentos). | `https://docuia-api-ia.azurewebsites.net` |
| `GITHUB_API_URL` | Base do `ms-api-github` (conexão e análise de repositórios). | `https://docuia-api-github.azurewebsites.net` |
| `FRONT_PRINCIPAL_URL` | URL do front principal (links da sidebar e "Voltar para Projetos"). | `https://docuia-frontend-hdc8hzfqbqebc6cp.brazilsouth-01.azurewebsites.net` |
| `PROJETOS_SERVICE_URL` | Base do `ms-projetos`. | `https://docuia-projetos-hffafgcsgkh0h3au.brazilsouth-01.azurewebsites.net` |
| `LOGIN_URL` | Página de login. Usada como destino quando o JWT está ausente ou expirado. | `${FRONT_PRINCIPAL_URL}/login` |
| `JWT_SECRET_KEY` | Segredo HMAC usado pela rota interna `/api/validar-sessao` pra validar a assinatura do JWT no servidor. | — (obrigatório) |
| `ALGORITHM` | Algoritmo de assinatura do JWT. | `HS256` |

## Como rodar local

```bash
pip install -r requirements.txt
```

Crie um `.env` na raiz com as URLs dos microsserviços e o `JWT_SECRET_KEY`:

```dotenv
UPLOAD_API_URL=https://docuia-api-upload.azurewebsites.net
IA_API_URL=https://docuia-api-ia.azurewebsites.net
GITHUB_API_URL=https://docuia-api-github.azurewebsites.net
FRONT_PRINCIPAL_URL=https://docuia-frontend-hdc8hzfqbqebc6cp.brazilsouth-01.azurewebsites.net
PROJETOS_SERVICE_URL=https://docuia-projetos-hffafgcsgkh0h3au.brazilsouth-01.azurewebsites.net
LOGIN_URL=https://docuia-frontend-hdc8hzfqbqebc6cp.brazilsouth-01.azurewebsites.net/login
JWT_SECRET_KEY=<o-mesmo-segredo-do-front-principal>
ALGORITHM=HS256
```

Suba:

```bash
uvicorn main:app --reload --port 5000
```

Acesse `http://127.0.0.1:5000`. Como as três telas exigem `?id=<projeto_id>&token=<jwt>` na primeira navegação, para testar isoladamente você precisa de um JWT válido emitido pelo front principal.

## Estrutura de pastas

```
Frontend_Projeto_Microservicos/
├── main.py
├── requirements.txt
├── README.md
├── static/
│   ├── assets/
│   │   └── images/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── sessao.js
│       ├── projeto_github.js
│       ├── projeto_upload.js
│       └── projeto_arquivos.js
└── templates/
    ├── interface/
    │   └── sidebar.html
    └── projeto/
        ├── projeto_github.html
        ├── projeto_upload.html
        └── projeto_arquivos.html
```

## Sessão e autenticação

O front principal redireciona o usuário pra este front cliente com `?id=<projeto_id>&token=<jwt>` na URL.

1. `static/js/sessao.js` lê esses parâmetros, guarda em `localStorage` (`projeto_id`, `token`) e remove a query string com `history.replaceState`.
2. Decodifica o payload do JWT no client, checa expiração e popula os dados do usuário na sidebar.
3. Expõe `Sessao.getToken()`, `Sessao.getProjetoId()`, `Sessao.getUsuario()`, `Sessao.pronto` (Promise) e `Sessao.getHeaders(isJson = true)`.
4. Todas as páginas devem chamar `await Sessao.pronto` antes da primeira chamada autenticada.
5. Quando o token está ausente ou expirado, `sessao.js` redireciona pra `LOGIN_URL`.

A **assinatura** do JWT é validada no servidor, não no JS. O servidor Python expõe a rota interna `GET /api/validar-sessao` que decodifica o token com `JWT_SECRET_KEY` (variável de ambiente, nunca exposta ao JS). Use essa rota quando precisar revalidar o token sem confiar só na decodificação client-side.

`Sessao.getHeaders()` devolve `{ Authorization: 'Bearer <token>', 'Content-Type': 'application/json' }`. Para uploads multipart, use `Sessao.getHeaders(false)` — o browser define o `Content-Type` com o `boundary` correto sozinho.

## Exemplos de chamadas de API

Todas as chamadas saem do **browser**, com `Authorization: Bearer <token>`. As URLs base vivem em `window.API` (injetadas pelo template) e nunca são hardcoded no JS.

---

### `GET {UPLOAD_API_URL}/api/projeto/{projeto_id}/artefatos`

Lista todos os artefatos (uploads e arquivos importados de repositórios) de um projeto, já enriquecidos com a classificação da IA.

**Headers**

```
Authorization: Bearer <jwt>
```

**Resposta esperada (200)**

```json
{
  "artefatos": [
    {
      "id": 42,
      "nome_arquivo": "spec-tecnica.pdf",
      "tipo": "Especificação Técnica",
      "tags": ["upload", "Repositório usuario/docuia-api"],
      "resumo": "Documento técnico descrevendo os endpoints do serviço de ingestão...",
      "data_upload": "2026-05-23T14:32:17",
      "url_documento": "https://docuiastorage.blob.core.windows.net/projeto-1/spec-tecnica.pdf"
    }
  ]
}
```

**Snippet (`static/js/projeto_arquivos.js`)**

```js
await Sessao.pronto;
const response = await fetch(
    `${window.API.UPLOAD}/api/projeto/${Sessao.getProjetoId()}/artefatos`,
    { headers: Sessao.getHeaders(false) }
);
const { artefatos } = await response.json();
```

---

### `DELETE {UPLOAD_API_URL}/api/artefatos/{artefato_id}`

Remove um artefato (metadados no Postgres + arquivo no Blob).

**Headers**

```
Authorization: Bearer <jwt>
```

**Body:** nenhum.

**Resposta esperada:** `200 OK` ou `204 No Content`.

**Snippet (`static/js/projeto_arquivos.js`)**

```js
const res = await fetch(`${window.API.UPLOAD}/api/artefatos/${artefatoId}`, {
    method: 'DELETE',
    headers: Sessao.getHeaders(false)
});
```

---

### `POST {UPLOAD_API_URL}/api/upload`

Envia um documento pro `ms-ingestao-upload`. O serviço extrai texto, dispara o `ms-api-ia` pra classificar (tipo + tags + resumo), grava metadados no Postgres e o arquivo no Azure Blob.

**Headers**

```
Authorization: Bearer <jwt>
```

> **Não envie `Content-Type` manualmente.** O browser define `multipart/form-data; boundary=...` automaticamente quando o body é `FormData`. Daí o `Sessao.getHeaders(false)` — ele devolve só o `Authorization`.

**Body (multipart/form-data)**

| Campo | Tipo | Exemplo |
|---|---|---|
| `projeto_id` | int | `42` |
| `documento` | file | `spec-tecnica.pdf` |

**Resposta esperada (200/201)**

```json
{
  "mensagem": "Arquivo processado com sucesso",
  "artefato_id": 137,
  "projeto_id": 42,
  "usuario_id": 7,
  "classificacao": {
    "tipo": "Especificação Técnica",
    "tags": ["upload", "spec", "api"],
    "resumo": "Documento técnico que descreve..."
  },
  "url_documento": "https://docuiastorage.blob.core.windows.net/projeto-42/spec-tecnica.pdf"
}
```

**Snippet (`static/js/projeto_upload.js`)**

```js
await Sessao.pronto;
const formData = new FormData();
formData.append("projeto_id", Sessao.getProjetoId());
formData.append("documento", arquivoReal);

const response = await fetch(`${window.API.UPLOAD}/api/upload`, {
    method: "POST",
    headers: Sessao.getHeaders(false),
    body: formData
});
```

---

### `POST {GITHUB_API_URL}/api/github/conectar`

Conecta um repositório GitHub ao projeto. O `ms-api-github` clona, lista arquivos relevantes, manda cada um pro `ms-api-ia` e persiste como artefatos no Postgres.

**Headers**

```
Authorization: Bearer <jwt>
Content-Type: application/json
```

**Body (JSON)**

```json
{
  "projeto_id": 42,
  "url": "https://github.com/usuario/docuia-api",
  "is_private": true,
  "token": "ghp_xxxxxxxxxxxxxxxxxxxx",
  "sincronizar": false
}
```

| Campo | Tipo | Descrição |
|---|---|---|
| `projeto_id` | int | ID do projeto na DocuIA. |
| `url` | string | URL HTTPS do repositório GitHub. |
| `is_private` | bool | Se `true`, requer `token`. |
| `token` | string \| null | Personal Access Token (PAT) do GitHub. Só é usado pra este clone — não é persistido. |
| `sincronizar` | bool | Se `true` e o repositório já estiver conectado a este projeto, substitui os artefatos antigos. |

**Snippet (`static/js/projeto_github.js`)**

```js
await Sessao.pronto;
const payload = {
    projeto_id: parseInt(Sessao.getProjetoId(), 10),
    url: repoUrl.value.trim(),
    is_private: tipoPrivado.checked,
    token: tipoPrivado.checked ? repoToken.value.trim() : null,
    sincronizar: chkSincronizar.checked
};

const response = await fetch(`${window.API.GITHUB}/api/github/conectar`, {
    method: "POST",
    headers: Sessao.getHeaders(),
    body: JSON.stringify(payload)
});
```

---

### `GET /api/validar-sessao` (rota INTERNA deste front)

Valida a **assinatura** do JWT no servidor Python deste repo, usando `JWT_SECRET_KEY`. Útil quando o cliente quer ter certeza de que o token não foi adulterado, sem ter que expor o segredo no JS.

**Headers**

```
Authorization: Bearer <jwt>
```

**Resposta esperada (200)**

```json
{
  "valido": true,
  "user_id": 7,
  "email": "joao@empresa.com.br",
  "nome": "João"
}
```

**Resposta de erro (401)**

```json
{
  "valido": false,
  "redirect": "https://docuia-frontend-...azurewebsites.net/login",
  "erro": "Sessão expirada. Faça login novamente."
}
```

**Snippet**

```js
await Sessao.pronto;
const res = await fetch('/api/validar-sessao', { headers: Sessao.getHeaders(false) });
if (!res.ok) {
    const { redirect } = await res.json();
    window.location.href = redirect;
}
```
