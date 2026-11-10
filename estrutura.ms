primora-api/
├── .env.example
├── .gitignore                         ← incluir .venv/, .env, __pycache__/, .ipynb_checkpoints/
├── .github/workflows/test.yml         ← CI opcional (G-07)
├── README.md
├── manage.py
├── requirements.txt                   ← Django, DRF, drf-spectacular, psycopg, python-dotenv, requests, pandas
├── requirements-dev.txt               ← -r requirements.txt + jupyter, ipykernel, coverage, ruff
├── config/                            (settings.py, urls.py, asgi.py, wsgi.py) configurações gerais do django
├── dados/
│   └── clientes_distribuidora_vetor.csv   ← cópia do arquivo da Primora
├── db/
│   └── schema.sql                     ← gerado na Etapa 3
├── notebooks/                         ← exploração do ETL (D-01 a D-03)
│   └── 01_exploracao.ipynb
├── docs/
│   ├── material-base/                 ← documentos base do PI
│   │   ├── Desafio_1_Backend_ETL.pdf
│   │   ├── LEIA-ME.pdf
│   │   ├── 02_-_Desafio_Primora_Aprimorado.md
│   │   ├── guia_de_construcao.md
│   │   ├── O_que_sera_avaliado_no_Projeto_Integrador.pdf
│   │   └── ROTEIRO_DE_APRESENTACAO_PROJETO_INTEGRADOR.pdf
│   ├── API.md
│   ├── MODELO_DE_DADOS.md             ← MER + DER
│   ├── REGRAS_DE_NORMALIZACAO.md
│   ├── RELATORIO_TRADEOFFS.md
│   ├── openapi.yml                    ← exportado pelo drf-spectacular
│   ├── REQUISITOS.md                  ← exigido pelo curso
│   ├── CASOS_DE_USO.md                ← exigido pelo curso
│   ├── DIAGRAMA_DE_CLASSES.md         ← exigido pelo curso
│   ├── ARQUITETURA.md                 ← exigido pelo curso
│   └── scrum/                         ← exigido pelo curso
│       ├── SCRUM.md                   (papéis, backlog, cerimônias)
│       └── sprint-1.md, sprint-2.md, sprint-3.md   (planning, review, retro)
├── distribuidora/                     (app: dados + API) (aplicativo do django)
│   ├── admin.py  apps.py  models.py
│   ├── serializers.py  services.py  views.py  urls.py
│   ├── etl/
│   │   ├── extracao.py  normalizadores.py  bairros.py
│   │   ├── viacep.py  transformacao.py  carga.py
│   ├── management/commands/etl.py
│   ├── migrations/0001_initial.py     ← gerado pelo Django
│   └── tests/
│       ├── test_api.py  test_bairros.py  test_etl.py
│       ├── test_normalizadores.py  test_viacep.py
└── frontend/                          ← app só do front-end simples  (aplicativo do django)
    ├── apps.py  views.py  urls.py
    ├── templates/frontend/
    │   ├── base.html  login.html  clientes.html  vendedores.html  resumo.html
    └── static/frontend/
        ├── css/estilo.css
        └── js/  api.js  clientes.js  vendedores.js  resumo.js