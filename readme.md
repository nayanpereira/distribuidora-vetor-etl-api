# Distribuidora Vetor - Pipeline ETL & API REST (Projeto Integrador)

Este repositório contém a solução desenvolvida para a **Distribuidora Vetor**, abrangendo desde o pipeline de ETL (Extração, Transformação e Carga) de dados brutos de clientes até a disponibilização de uma API REST integrada a um banco de dados relacional PostgreSQL.

## 📌 Status Atual do Projeto

As etapas de **Fundações** e **ETL** já foram desenvolvidas e consolidadas:

* **Fase 0 (Kickoff):** Repositório criado, estrutura de diretórios padronizada e ambiente virtual configurado.

* **Fase 1 (Fundações & Banco de Dados):**
  * Modelagem relacional concluída (`Cliente`, `Vendedor`, `Auditoria`, `CepCache`).
  * Integração total com o **PostgreSQL**.
  * Tabelas registradas e configuradas no **Django Admin** (com auditoria em modo *read-only*).

* **Fase 2 (ETL & Higienização de Dados):**
  * Script de ETL migrado de Jupyter Notebook para um comando nativo Django (`python manage.py etl`).
  * Higienização e normalização com Regex (CNPJ, Telefone, E-mail com acentos, Datas).
  * Integração com a API do **ViaCEP** com mecanismo de *cache* em banco.
  * Regra de decisão para nomes de bairros e *fallback* inteligente.
  * Processamento **transacional** (`transaction.atomic`) e **idempotente** (`update_or_create`).
  * Registro de histórico linha a linha na tabela de `Auditoria`.

---

## 🌿 Fluxo de Trabalho no Git (Branches & Pull Requests)

> ⚠️ **REGRA OBRIGATÓRIA DA EQUIPE:** É estritamente proibido fazer `git push` diretamente na branch `main`. Todo o desenvolvimento deve ocorrer em branches de funcionalidade e passar por Pull Request (PR).

Siga o passo a passo abaixo para desenvolver qualquer tarefa:

1. **Garanta que sua `main` local esteja atualizada:**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Crie uma nova branch para a sua tarefa:**
   Use nomes claros e descritivos com os prefixos `feature/`, `docs/`, `fix/` ou `refactor/`:
   ```bash
   # Exemplos:
   git checkout -b feature/api-serializers
   git checkout -b feature/frontend-login
   git checkout -b docs/modelo-der
   ```

3. **Desenvolva a tarefa e faça os commits:**
   ```bash
   git add .
   git commit -m "feat(api): cria serializers de cliente e vendedor"
   ```

4. **Envie a sua branch para o GitHub:**
   ```bash
   git push origin feature/nome-da-sua-branch
   ```

5. **Abra um Pull Request (PR):**
   * Vá até o repositório no GitHub.
   * Clique em **"Compare & pull request"**.
   * Descreva o que foi implementado na tarefa.
   * Peça a revisão de pelo menos um integrante da equipe antes de realizar o *Merge* para a `main`.

---

## 👥 Divisão de Tarefas & Próximos Passos (Backlog da Equipe)

Para garantir a entrega e apresentação do projeto, as tarefas pendentes estão divididas entre os dois demais integrantes da equipe:

### 🎯 1. Alinhamentos Iniciais Conjuntos (Pendências da Fase 0)

*Ambos os integrantes devem realizar as seguintes tarefas da Fase 0:*

* **G-01:** Ler todos os documentos do projeto juntos e listar eventuais dúvidas para o professor.
* **G-02:** Confirmar/validar a escolha da stack (**Django REST Framework** vs FastAPI) e conferir as datas de entrega e apresentação. *(Nota: A infraestrutura base em DRF já está implementada).*
* **G-06:** Escrever formalmente a **Definition of Done (DoD)** (critérios para considerar uma tarefa pronta: código revisado, testado e documentado).

### 💻 2. Integrante B: Desenvolvimento Web (Fases 3 e 4)

Foco na criação da camada de serviço/API e interface com o usuário.

* **Fase 3 — API REST (Backend):**
  * **A-01:** Serializers (`ClienteSerializer`, `VendedorSerializer`, `AuditoriaSerializer`).
  * **A-03 / A-04:** Endpoints e CRUD de clientes e vendedores (incluindo o tratamento de erro `409 Conflict` ao tentar deletar vendedores com clientes vinculados).
  * **A-05 / A-06:** Rotas de busca por bairro (`/api/clientes/bairro/{nome}/`) e filtro por vendedor (`/api/vendedores/{id}/clientes/`).
  * **A-07 / A-08:** Autenticação por Token e permissões (Usuário autenticado: CRUD completo; Visitante: Apenas GET).
  * **A-09 / A-10:** Documentação OpenAPI/Redoc (`drf-spectacular`) e testes automatizados de API.

* **Fase 4 — Front-end Simples:**
  * **F-01 a F-08:** Telas simples em HTML/CSS/JS (consumindo a API via `fetch`): Tela de login (armazenamento do Token), listagem paginada de clientes, formulários de criação/edição e exclusão com confirmação.
  * **F-10:** Modo visitante (ocultar botões de escrita para usuários não autenticados).

### 📑 3. Integrante C: Documentação, QA & Apresentação (Fases 5, 6 e 7)

Foco nos artefatos acadêmicos, qualidade de software e materiais de apresentação.

* **Fase 5 — Documentação Geral & Artefatos Scrum:**
  * **DOC-02 / DOC-03:** Criar `docs/API.md` e os modelos **MER / DER** (usando Mermaid) em `docs/MODELO_DE_DADOS.md`.
  * **DOC-04 / DOC-05:** Redigir `REGRAS_DE_NORMALIZACAO.md` e o relatório de *trade-offs* `RELATORIO_TRADEOFFS.md` (1 a 2 páginas, em linguagem não técnica).
  * **DOC-06 a DOC-09:** Mapear Requisitos (RF/RNF), Casos de Uso, Diagrama de Classes e Arquitetura Abstrata ($CSV \rightarrow ETL \rightarrow PostgreSQL \rightarrow API \rightarrow Frontend$).
  * **DOC-10:** Documentação Scrum (Papéis, Sprints, Planning, Review e Retrospectivas).

* **Fase 6 — Integração e QA:**
  * **Q-01 a Q-06:** Testar instalação em máquina limpa seguindo o README, rodar suíte de testes (`python manage.py test`), verificar variáveis de ambiente e criar a tag `v1.0` de congelamento de código.

* **Fase 7 — Apresentação:**
  * **P-01 a P-06:** Elaborar slides da apresentação, definir roteiro da demonstração ao vivo, preparar Plano B (gravação/prints da demo) e ensaiar a fala com a equipe (20 min + 5 min de perguntas).

---

## 🛠️ Guia de Instalação e Execução Local

Siga as instruções abaixo para rodar o projeto no seu ambiente local.

### 1. Pré-requisitos

* **Python 3.11+** instalado.
* **PostgreSQL** instalado e em execução localmente.
* **Git** instalado.

### 2. Clonar o Repositório e Configurar o Ambiente Virtual

```bash
# 1. Clonar o repositório
git clone https://github.com/nayanpereira/distribuidora-vetor-etl-api.git
cd distribuidora-vetor-etl-api

# 2. Criar o ambiente virtual (.venv)
python -m venv .venv

# 3. Ativar o ambiente virtual
# No Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# No Linux/macOS:
source .venv/bin/activate

# 4. Instalar as dependências
pip install -r requirements.txt
```

### 3. Configurar o Banco de Dados (PostgreSQL)

1. Abra o seu gerenciador do PostgreSQL (pgAdmin, DBeaver ou via terminal `psql`) e crie o banco de dados:
   ```sql
   CREATE DATABASE distribuidora_db;
   ```

2. Na raiz do projeto, crie um arquivo chamado **`.env`** (utilize o `.env.example` como referência):
   ```ini
   DB_NAME=distribuidora_db
   DB_USER=postgres
   DB_PASSWORD=SUA_SENHA_DO_POSTGRES
   DB_HOST=127.0.0.1
   DB_PORT=5432
   SECRET_KEY=sua-chave-secreta-django
   DEBUG=True
   ```

### 4. Executar Migrações e Iniciar o ETL

Com a `.venv` ativa e o banco configurado no `.env`, execute:

```bash
# 1. Aplicar a estrutura de tabelas no PostgreSQL
python manage.py migrate

# 2. Executar o pipeline de ETL (Lê o CSV, faz ViaCEP e popula o PostgreSQL)
python manage.py etl

# 3. Criar o superusuário para acessar o Django Admin
python manage.py createsuperuser
```

### 5. Iniciar o Servidor de Desenvolvimento

```bash
python manage.py runserver
```

Acesse no navegador:
* **Django Admin:** `http://127.0.0.1:8000/admin/` (para visualizar Clientes, Vendedores, Caches de CEP e a Tabela de Auditoria).
* **API Base:** `http://127.0.0.1:8000/api/`

---

## 📁 Estrutura do Projeto

```text
distribuidora-vetor-etl-api/
│
├── config/                 # Configurações globais do Django (settings, urls, etc.)
├── dados/                  # Arquivo CSV original (clientes_distribuidora_vetor.csv)
├── distribuidora/          # App principal (models, views, serializers, admin)
│   └── management/
│       └── commands/
│           └── etl.py      # Comando de ETL executável (manage.py etl)
├── docs/                   # Documentações acadêmicas e diagramas do projeto
├── notebooks/              # Jupyter Notebooks utilizados na fase de exploração
├── .env.example            # Modelo de variáveis de ambiente
├── .gitignore              # Arquivos ignorados pelo Git
├── manage.py               # Utilitário de linha de comando do Django
└── requirements.txt        # Dependências do projeto
```