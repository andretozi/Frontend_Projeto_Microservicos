# 📄 DocuIA - Documentação Inteligente com IA

![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-blue)
![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey?logo=flask)

A **Plataforma de Documentação Inteligente de Projetos de Engenharia de Software** (DocuIA) é uma solução criada para resolver o problema da documentação de software, que frequentemente fica obsoleta em entregas ágeis. 

A nossa missão é integrar o código-fonte com a documentação, utilizando IA para reduzir o esforço manual, centralizando repositórios (GitHub), diagramas e arquivos diversos para gerar artefatos de forma automática. Este projeto é desenvolvido em grupos, onde cada equipe é responsável por um microsserviço que será integrado a um sistema único da turma.

---

## Estratégia Top-Down e o Módulo de Ingestão de Dados

Neste repositório, estamos adotando a abordagem de desenvolvimento **Top-Down** (Front-end ➔ Back-end ➔ Banco de Dados). Antes de construirmos as complexas integrações de IA e os pipelines de dados, estruturamos toda a interface visual e a navegação da plataforma (usando Flask, HTML e CSS).

Nosso grupo é especificamente responsável pelo módulo de **Upload, Cadastro e Gerenciamento de Dados (Ingestão)**. A construção deste "Módulo 2" focado em interface agrega valor direto ao nosso microsserviço de Ingestão porque:

* **Mapeamento de Entradas:** Define exatamente as telas e formulários por onde o usuário fará a integração com o GitHub (repositórios, branches) e o upload de arquivos soltos (PDFs de requisitos, atas, diagramas).
* **Estruturação Visual:** Ajuda a validar como as informações e documentos enviados serão organizados por projetos e estrutura de pastas antes de modelarmos o banco de dados.
* **Preparação para IA:** Ao ter o Front-end pronto, sabemos exatamente como o sistema receberá os dados que, futuramente, nossa IA classificará automaticamente, extraindo metadados fundamentais.

---

## ✨ Funcionalidades Atuais do Front-end 

Através do roteamento com o framework Flask, já temos o esqueleto navegável da plataforma:

- **🔐 Autenticação:** Telas e fluxos simulados de Login, Cadastro e Recuperação de senha.
- **📊 Dashboard:** Visão geral para os perfis de usuários (Tech Lead, PM, Desenvolvedor).
- **🏢 Gestão de Empresas:** Telas de visualização, membros e painel de solicitações.
- **📂 Gestão e Ingestão de Projetos:** Telas preparadas para a nossa funcionalidade principal de upload de dados, visão de permissões e controle de arquivos do projeto.

---

## 🛠️ Tecnologias Utilizadas

* **Front-end:** HTML5, CSS3.
* **Back-end de Roteamento:** Python, Flask (Web Framework).
* **Gerenciamento de Dependências:** `pip` e `requirements.txt`.

---

## ⚙️ Como executar o projeto na sua máquina

Para rodar a interface estática roteada pelo Flask localmente, você precisará ter o [Python](https://www.python.org/downloads/) instalado. Siga os passos:

### 1. Clone o repositório
```bash
git clone https://github.com/andretozi/Frontend_Projeto_Microservicos.git
cd Frontend_Projeto_Microservicos
```

### 2. Crie e ative um Ambiente Virtual (Recomendado)
O ambiente virtual previne que as bibliotecas deste projeto entrem em conflito com outras instaladas no seu PC.
```bash
# Criando o ambiente virtual
python -m venv venv

# Ativando no Windows:
venv\Scripts\activate

# Ativando no Mac/Linux:
source venv/bin/activate
```

### 3. Instale as dependências com `requirements.txt` 📦
O arquivo `requirements.txt` funciona como uma "lista de compras" que diz ao Python exatamente quais bibliotecas externas (e em quais versões) o projeto precisa para rodar (neste caso, o Flask). 

Com o seu ambiente virtual ativado, rode o comando abaixo:
```bash
pip install -r requirements.txt
```
> **Como isso funciona?** O `pip` (gerenciador de pacotes do Python) lê o arquivo de requisitos linha por linha, baixa todos os pacotes necessários diretamente da internet e os instala no seu ambiente virtual de forma automática, garantindo que o projeto rode perfeitamente na sua máquina.

### 4. Execute a aplicação
Com tudo instalado, inicie o servidor local do Flask:
```bash
python main.py
```

### 5. Acesse no Navegador
O terminal indicará que o servidor está online. Abra o seu navegador e acesse:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)** ou **http://localhost:5000**

---
*Projeto desenvolvido pela equipe de Ingestão de Dados para a disciplina de Engenharia de Software com Microsserviços.*
