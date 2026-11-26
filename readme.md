# Distribuidora Vetor — Pipeline ETL, API REST & Painel Web

Solução completa desenvolvida para a **Distribuidora Vetor**, contemplando o pipeline de ETL (Extração, Transformação e Carga) com auditoria linha a linha, persistência em **PostgreSQL**, **API REST** documentada (OpenAPI/Redoc) e **interface web** responsiva com controle de permissões por perfil.

---

## 📌 Funcionalidades Implementadas

* **Pipeline ETL & Higienização (`distribuidora/etl_service.py` e `manage.py etl`):**
  * Normalização com Regex e regras de domínio para **CEP**, **Bairro** (ViaCEP com cache em banco + *fallback* canonizado para regiões do DF), **CNPJ**, **Telefone** (celular/fixo com remoção de `+55`), **E-mail** (minúsculas e remoção de acentos) e **Datas** (`YYYY-MM-DD`).
  * Carga transacional (`transaction.atomic`) e idempotente (`update_or_create`) com histórico na tabela `Auditoria`.
* **API REST (`distribuidora/views.py` e `distribuidora/urls.py`):**
  * CRUD completo de **Clientes** e **Vendedores** (com proteção `409 Conflict` ao tentar excluir vendedor com clientes vinculados).
  * Filtros por bairro (`/api/clientes/bairro/{nome}/`), vendedor (`/api/vendedores/{id}/clientes/`), status de revisão (`?precisa_revisao=true`) e resumo agrupado (`/api/clientes/bairros/`).
  * Autenticação por Token (`/api/auth/token/`) e ocultação automática de dados sensíveis (CNPJ, telefone e e-mail) para visitantes.
  * Documentação interativa: **Swagger** (`/api/docs/`), **Redoc** (`/api/redoc/`) e esquema OpenAPI (`/api/schema/`).
* **Interface Web & Painel Administrativo (`distribuidora/templates/` e `distribuidora/static/`):**
  * **Visitante:** consulta pública de clientes, vendedores e relatórios por bairro.
  * **Usuário Autenticado (Funcionário):** cadastro/edição/exclusão de registros, visualização de dados completos e exportação da base limpa em **CSV** e **Excel (`.xlsx`)**.
  * **Administrador (`is_staff`):** aba exclusiva **Normalização**, exibindo a tabela completa de auditoria (`Original → Final` + critério aplicado) e upload de novas planilhas `.csv` ou `.xlsx` com opção de **incorporar ao histórico do banco** ou **apenas normalizar e baixar sem salvar**.

---

## 🚀 Guia de Execução (Escolha o seu Cenário)

### 🟢 Cenário 1: Primeira vez rodando o projeto do zero

Siga esta sequência se você acabou de clonar o repositório e ainda não possui o banco nem o ambiente Python configurados.

#### 1. Pré-requisitos
* **Python 3.11+** instalado.
* **PostgreSQL** instalado localmente.
* **Git** instalado.
#### 2. Garantir que o PostgreSQL esteja aberto e rodando
* **Windows:** Abra o **pgAdmin 4** pelo Menu Iniciar do Windows e conecte ao seu servidor local (digitando sua senha do PostgreSQL, se solicitado). Isso já garante que o banco esteja ativo e pronto para uso.
* **Linux (Ubuntu/Debian):** Caso não use o pgAdmin, inicie o serviço pelo terminal com:
  ```bash
  sudo service postgresql start
  ```
#### 3. Criar o banco de dados `distribuidora_db`
Escolha **uma** das formas abaixo:
* **Via terminal (`psql`):**
  ```powershell
  psql -U postgres -c "CREATE DATABASE distribuidora_db;"
  ```
* **Via pgAdmin 4:** conecte ao servidor local → clique com o botão direito em **Databases** → **Create > Database...** → digite `distribuidora_db` → **Save**.

#### 4. Clonar o projeto, criar o ambiente virtual e instalar o Django e dependências
```powershell
# 1. Clonar o repositório e entrar na pasta
git clone https://github.com/nayanpereira/distribuidora-vetor-etl-api.git
cd distribuidora-vetor-etl-api

# 2. Criar o ambiente virtual (.venv)
python -m venv .venv

# 3. Ativar o ambiente virtual
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# 4. Instalar o Django, Django REST Framework, Pandas, OpenPyXL e demais pacotes
pip install -r requirements.txt
```
*(Caso o PowerShell bloqueie a ativação da `.venv` no Windows, rode antes: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`).*

#### 5. Configurar as variáveis de ambiente (`.env`)
Crie um arquivo chamado **`.env`** na raiz do projeto (ao lado do `manage.py`) baseado no `.env.example`:
```env
SECRET_KEY=troque-por-uma-chave-segura-do-django
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=distribuidora_db
DB_USER=postgres
DB_PASSWORD=SUA_SENHA_DO_POSTGRES
DB_HOST=127.0.0.1
DB_PORT=5432
```

#### 6. Preparar o banco, rodar o ETL inicial e iniciar o Django
A partir deste ponto, todos os comandos utilizam o **`manage.py`** do Django (com a `.venv` ativa):
```powershell
# 1. Criar as tabelas no PostgreSQL
python manage.py migrate

# 2. Popular o banco rodando o pipeline ETL (CSV + ViaCEP + Auditoria)
python manage.py etl

# 3. Criar um usuário administrador (necessário para acessar a aba Normalização e o /admin/)
python manage.py createsuperuser

# 4. INICIAR O SERVIDOR DJANGO
python manage.py runserver
```

Saída esperada do ETL na primeira execução, com o CSV da Primora:

```text
Iniciando ETL a partir de: dados/clientes_distribuidora_vetor.csv
Arquivo lido com sucesso. Total de linhas: 47
Executando regras de higienização, ViaCEP e carga no PostgreSQL...
ETL Concluído! 47 processados (47 criados, 0 atualizados).
```

Rodar de novo não duplica clientes: o resumo passa a mostrar `0 criados, 47 atualizados`.

---

### 🟡 Cenário 2: Já tenho uma versão antiga e preciso atualizar e rodar novamente

Se você já tinha o projeto configurado anteriormente e puxou novas atualizações do GitHub (como suporte a Excel `.xlsx`, painel de normalização admin e ajustes no `.env`):

```powershell
# 1. Garantir que o PostgreSQL esteja rodando (se necessário)
# Windows (PowerShell como Admin): Start-Service postgresql-x64-17

# 2. Atualizar o código local a partir da main
git checkout main
git pull origin main

# 3. Ativar o ambiente virtual (.venv)
.\.venv\Scripts\Activate.ps1

# 4. Atualizar/instalar novas dependências (ex.: openpyxl)
pip install -r requirements.txt

# 5. Conferir se o arquivo .env existe na raiz com DB_USER=postgres e sua DB_PASSWORD

# 6. Aplicar eventuais novas migrações e reprocessar o ETL atualizado
python manage.py migrate
python manage.py etl

# 7. INICIAR O SERVIDOR DJANGO
python manage.py runserver
```
*(Dica: após abrir o navegador, pressione **`Ctrl + Shift + R`** ou **`Ctrl + F5`** para limpar o cache dos arquivos JavaScript antigos).*

---

### 🔵 Cenário 3: Rotina diária (tudo já instalado e configurado)

Quando o ambiente e o banco já estão prontos e você quer apenas ligar a aplicação para usar ou desenvolver:

```powershell
# 1. Entrar na pasta do projeto e ativar o ambiente virtual
cd distribuidora-vetor-etl-api
.\.venv\Scripts\Activate.ps1

# 2. INICIAR O SERVIDOR DJANGO
python manage.py runserver
```
*(Se aparecer erro de conexão com o banco, certifique-se apenas de que o serviço do PostgreSQL foi iniciado).*

---

## 🌐 Endereços de Acesso (com o Django rodando)

* **Painel Web (Front-end):** `http://127.0.0.1:8000/clientes/`
* **Tela de Login:** `http://127.0.0.1:8000/entrar/`
* **Documentação da API (Swagger):** `http://127.0.0.1:8000/api/docs/`
* **Documentação da API (Redoc):** `http://127.0.0.1:8000/api/redoc/`
* **API REST Base:** `http://127.0.0.1:8000/api/`
* **Django Admin:** `http://127.0.0.1:8000/admin/`

---

## 🧪 Testes Automatizados

Para validar as permissões e os endpoints da API e do painel web (29 testes; ainda não há testes automatizados das regras do ETL), execute (com a `.venv` ativa):

```powershell
python manage.py test
```

---

## 📚 Documentação do Projeto

Os documentos ficam na pasta `docs/`:

* [`docs/API.md`](docs/API.md): rotas, permissões, validações e exemplos da API
* [`docs/REQUISITOS.md`](docs/REQUISITOS.md): requisitos funcionais e não funcionais, com a situação de cada um
* [`docs/CASOS_DE_USO.md`](docs/CASOS_DE_USO.md): atores, diagrama e descrição dos casos de uso
* [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md): arquitetura, camadas e fluxos
* [`docs/DIAGRAMA_DE_CLASSES.md`](docs/DIAGRAMA_DE_CLASSES.md): diagramas de classes (domínio, ETL e API)
* [`docs/MODELO_DE_DADOS.md`](docs/MODELO_DE_DADOS.md): MER, DER e dicionário de dados
* [`docs/REGRAS_DE_NORMALIZACAO.md`](docs/REGRAS_DE_NORMALIZACAO.md): regras de tratamento, critérios da auditoria e limites conhecidos
* [`docs/RELATORIO_TRADEOFFS.md`](docs/RELATORIO_TRADEOFFS.md): decisões do tratamento de dados e seus custos, em linguagem não técnica
* [`docs/REGISTRO_DE_QA.md`](docs/REGISTRO_DE_QA.md): verificações da fase de QA
* [`docs/scrum/DOCUMENTACAO_SCRUM.md`](docs/scrum/DOCUMENTACAO_SCRUM.md): papéis, sprints, backlog e retrospectivas
* `docs/material-base/`: enunciado da Primora e guias de apoio

---

## 🌿 Fluxo de Trabalho no Git (Branches & Pull Requests)

> ⚠️ **REGRA DA EQUIPE:** Evite `git push` direto na `main` durante o desenvolvimento de novas tarefas. Trabalhe em branches dedicadas e abra Pull Requests.

1. Atualize sua `main`: `git checkout main && git pull origin main`
2. Crie sua branch: `git checkout -b feature/nome-da-tarefa` (ou `docs/...`, `fix/...`)
3. Faça seus commits e envie: `git push origin feature/nome-da-tarefa`
4. Abra o **Pull Request** no GitHub para revisão antes do *Merge*.

---

## 📁 Estrutura Atual do Projeto

```text
distribuidora-vetor-etl-api/
│
├── config/                         # Configurações globais do Django (settings, urls, wsgi/asgi)
├── dados/                          # Base bruta CSV (clientes_distribuidora_vetor.csv)
├── distribuidora/                  # App principal (ETL, API REST e Front-end)
│   ├── management/commands/
│   │   └── etl.py                  # Comando CLI (python manage.py etl)
│   ├── static/distribuidora/
│   │   ├── css/style.css           # Estilos da interface web
│   │   └── js/                     # Módulos ES6 (api, app, auth, clientes, normalizacao, relatorios, ui, vendedores)
│   ├── templates/distribuidora/    # Templates HTML (base, clientes, vendedores, relatorios, normalizacao, login, forms)
│   ├── admin.py                    # Configuração do Django Admin
│   ├── etl_service.py              # Motor compartilhado de higienização, ViaCEP e carga/exportação
│   ├── frontend_urls.py            # Rotas das páginas web
│   ├── models.py                   # Modelos (Cliente, Vendedor, Auditoria, CepCache)
│   ├── serializers.py              # Serializers DRF (público, autenticado e resumo)
│   ├── services.py                 # Consultas e regras de negócio da API
│   ├── tests.py                    # Suíte de testes automatizados
│   ├── urls.py                     # Rotas da API REST (/api/...)
│   └── views.py                    # ViewSets e endpoints de exportação/upload ETL
├── docs/                           # Documentação técnica, diagramas e artefatos Scrum
├── notebooks/                      # Jupyter Notebooks de exploração e validação do ETL
├── .env.example                    # Modelo comentado de variáveis de ambiente
├── .gitignore                      # Arquivos ignorados pelo Git (.venv, .env, __pycache__, etc.)
├── manage.py                       # Utilitário principal de linha de comando do Django
└── requirements.txt                # Dependências do projeto (Django, DRF, Pandas, OpenPyXL, etc.)
```

---

## ⚠️ Limitações Conhecidas

Detalhes em [`docs/REGRAS_DE_NORMALIZACAO.md`](docs/REGRAS_DE_NORMALIZACAO.md):

* Quando o ViaCEP responde, o bairro dele **substitui** o bairro digitado, sem registro de conflito e sem enviar o cliente para revisão.
* O bairro devolvido pelo ViaCEP não é padronizado (por exemplo, `Sul (Águas Claras)` convive com `Águas Claras Sul`), e a subdivisão não tem coluna própria.
* O ETL grava o CNPJ com máscara e o telefone como `DD 9XXXX-XXXX`; a API grava os dois só com dígitos.
* Não há testes automatizados das regras do ETL nem das rotas de exportação e de normalização; o `openapi.yml` não inclui essas rotas.
* O painel web guarda o token só na memória da página: ao recarregar, é preciso entrar de novo.

---

## 👥 Equipe

| Integrante | Foco principal |
|------------|----------------|
| Nayan | Dados e ETL |
| Bruno | Banco, API e painel web |
| Davi | Documentação, QA e apresentação |
