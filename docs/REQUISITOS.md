# Requisitos do Sistema

Projeto Integrador: Distribuidora Vetor (ETL + API REST)

Este documento lista os requisitos funcionais e não funcionais do sistema,
conforme o enunciado da Primora e o backlog do projeto, e indica a **situação
de cada um no código atual**.

## Legenda da situação

A situação foi avaliada por **leitura do código** da branch `main` (commit
`85d76d3`, de 24/11), incluindo `models.py`, `admin.py`, `etl_service.py`,
`etl.py`, `normalizadores.py`, `serializers.py`, `services.py`, `views.py`, as
rotas, os arquivos do painel web, os testes e os `requirements`. O sistema
**não foi executado** para esta avaliação. O ETL anterior à refatoração foi
rodado, mas a versão atual ainda precisa ser executada (`REGISTRO_DE_QA.md`).

| Situação | Significado |
|----------|-------------|
| Implementado | O código analisado cumpre o requisito. |
| Parcial | O código cumpre uma parte do requisito. A observação diz o que falta. |
| Não implementado | O requisito faz parte do escopo, mas não existe no código analisado. |
| Não verificado | Não é possível confirmar apenas com a leitura do código. |

## Resumo

| Grupo | Implementado | Parcial | Não implementado | Não verificado | Total |
|-------|:-----------:|:-------:|:----------------:|:--------------:|:-----:|
| Requisitos funcionais | 23 | 7 | 1 | 0 | 31 |
| Requisitos não funcionais | 6 | 3 | 0 | 1 | 10 |

## 1. Requisitos funcionais

Prioridades: P0 = obrigatório, P1 = importante, P2 = extra.

### 1.1 ETL (tratamento da base de clientes)

| ID | Requisito | Prior. | Situação | Observação |
|----|-----------|--------|----------|------------|
| RF-01 | O sistema deve ler o CSV de clientes preservando zeros à esquerda e campos vazios. | P0 | Implementado | Leitura com `dtype=str` e `keep_default_na=False`. |
| RF-02 | O sistema deve normalizar CNPJ, telefone, e-mail (com acento), data e CEP. | P0 | Implementado | Normaliza CEP, bairro, CNPJ, telefone, e-mail e data. A carga grava o CNPJ com máscara e o telefone como `DD 9XXXX-XXXX`; a API grava os dois só com dígitos. |
| RF-03 | O sistema deve unificar as variantes de grafia dos bairros e separar a subdivisão. | P0 | Parcial | Canoniza Águas Claras, Guará, Taguatinga e Vicente Pires por palavra-chave. A subdivisão fica no nome (não em coluna própria) e o bairro devolvido pelo ViaCEP não é padronizado. |
| RF-04 | O sistema deve consultar o ViaCEP para obter o bairro de cada CEP, guardando o resultado em cache no banco e tratando o retorno de erro. | P0 | Implementado | Cache na tabela `CepCache`, timeout de 5 s; CEPs não reconhecidos também ficam no cache. Falha de rede segue sem o bairro do ViaCEP. |
| RF-05 | O sistema deve decidir entre o bairro digitado e o bairro do CEP em caso de conflito, marcando `precisa_revisao` quando necessário. | P0 | Parcial | O bairro do ViaCEP substitui o digitado. Não há detecção de conflito; `precisa_revisao` só é marcado quando o cliente fica sem bairro. |
| RF-06 | O sistema deve registrar na auditoria, para cada campo tratado, o valor original, o valor tratado e o critério aplicado. | P0 | Implementado | Audita `cep`, `bairro`, `cnpj`, `telefone`, `email` e `data_cadastro` (6 linhas por cliente), em histórico acumulado. Campos só aparados (razão social, cidade, UF e vendedor) não são auditados. |
| RF-07 | O sistema deve gravar os dados em PostgreSQL de forma transacional e idempotente. | P0 | Implementado | `transaction.atomic()` e `update_or_create` por `id_cliente`. O cache de CEPs é gravado antes da transação. |
| RF-08 | O sistema deve oferecer o comando `python manage.py etl`, com um resumo no terminal. | P0 | Implementado | O comando aceita `--arquivo` (CSV ou Excel) e exibe `N processados (X criados, Y atualizados)`. O resumo não lista bairros nem casos de revisão. |
| RF-09 | O sistema deve validar os dígitos do CNPJ (marcando para revisão, sem descartar) e usar a BrasilAPI como alternativa ao ViaCEP. | P2 | Não implementado | |

### 1.2 API REST e administração

| ID | Requisito | Prior. | Situação | Observação |
|----|-----------|--------|----------|------------|
| RF-10 | A API deve permitir criar, listar, consultar, alterar e excluir clientes. | P0 | Implementado | `/api/clientes/`, com paginação de 20 por página. |
| RF-11 | A API deve permitir o CRUD de vendedores e responder 409 ao excluir um vendedor que possui clientes. | P0 | Implementado | `/api/vendedores/`; o 409 vem de `RestrictedError` do modelo. |
| RF-12 | A API deve listar clientes de um bairro aceitando qualquer grafia do nome. | P0 | Parcial | Ignora maiúsculas, acentos e pontuação. Não unifica variantes como `Águas Claras/DF`, `Vte Pires` ou `Águas Claras Sul`. |
| RF-13 | A API deve exibir os clientes agrupados por bairro. | P0 | Parcial | `/api/clientes/bairros/` agrupa por maiúsculas, acentos e pontuação. Com o ETL atual, a estimativa é de cerca de 12 bairros distintos, mais os clientes sem bairro, porque o bairro do ViaCEP não é padronizado (a confirmar na execução real). |
| RF-14 | A API deve listar os clientes de um vendedor. | P0 | Implementado | `/api/clientes/vendedor/{id}/` e `/api/vendedores/{id}/clientes/`; 404 para vendedor inexistente. |
| RF-15 | A API deve autenticar o usuário por token. | P0 | Implementado | `/api/auth/token/` e `/api/token/`. |
| RF-16 | Usuário autenticado faz CRUD completo; usuário não autenticado só consulta (GET). | P0 | Implementado | `IsAuthenticatedOrReadOnly`. Visitante não recebe CNPJ, telefone e e-mail. |
| RF-17 | A API deve ter documentação OpenAPI/Redoc, com o `openapi.yml` exportado. | P0 | Parcial | Swagger em `/api/docs/` e Redoc em `/api/redoc/` (o roadmap previa o Redoc em `/api/docs/`). O `openapi.yml` não inclui as rotas novas (exportação, perfil e `admin-etl`). |
| RF-18 | O Django Admin deve exibir as 4 tabelas (Cliente, Vendedor, Auditoria, CepCache), com a auditoria somente leitura e acessível apenas no admin. | P0 | Parcial | As 4 tabelas estão registradas e a auditoria não aparece na API. Na auditoria, criar e editar estão bloqueados; excluir não. |
| RF-19 | A API deve permitir filtrar clientes por `precisa_revisao` e normalizar o bairro recebido. | P2 | Parcial | O filtro `?precisa_revisao=true` existe. O bairro recebido pela API não é normalizado. |

### 1.3 Front-end

| ID | Requisito | Prior. | Situação | Observação |
|----|-----------|--------|----------|------------|
| RF-20 | O front deve ter tela de login (guardando o token) e logout. | P0 | Implementado | `/entrar/` e botão Sair. O token fica só na memória da página: ao recarregar, volta ao modo visitante. |
| RF-21 | O front deve listar clientes com paginação. | P0 | Implementado | Botões Anterior e Próxima, 20 por página. |
| RF-22 | O front deve filtrar clientes por bairro e por vendedor. | P0 | Implementado | Campo de busca por bairro e seletor de vendedor. A busca por bairro no front não aceita pontos nem barras. |
| RF-23 | O front deve ter formulário de criar e editar cliente, exibindo os erros de validação da API. | P0 | Implementado | O código exibe as mensagens por campo devolvidas pela API. |
| RF-24 | O front deve permitir excluir cliente com confirmação. | P0 | Implementado | Janela de confirmação antes de excluir. |
| RF-25 | O front deve ter CRUD de vendedores, exibindo a mensagem do 409. | P0 | Implementado | Mensagem própria para o 409 ao excluir vendedor com clientes. |
| RF-26 | O front deve ter um painel de clientes por bairro (tabela ou gráfico simples). | P1 | Implementado | Tela Relatórios, seção Clientes por bairro. |
| RF-27 | No modo visitante, o front deve ocultar os botões de escrita. | P1 | Implementado | Ficam ocultos Novo cliente, Novo vendedor, Editar e Excluir. |
| RF-28 | O front deve listar os clientes que "precisam de revisão". | P2 | Implementado | Tela Relatórios, seção Clientes que precisam de revisão. |

### 1.4 Funcionalidades adicionais (além do enunciado)

| ID | Requisito | Prior. | Situação | Observação |
|----|-----------|--------|----------|------------|
| RF-29 | Usuário autenticado pode exportar a base tratada em CSV ou Excel. | Extra | Implementado | Botões Exportar CSV e Exportar Excel em `/clientes/`; rota `GET /api/clientes/exportar/`. Não há testes automatizados. |
| RF-30 | Usuário da equipe (`is_staff`) vê, na aba Normalização, a tabela com valor original, valor final e critério de cada campo. | Extra | Implementado | Rota `GET /api/admin-etl/tabela/`; a aba fica oculta para os demais usuários. |
| RF-31 | Usuário da equipe pode enviar uma planilha CSV ou Excel e escolher entre salvar no banco ou apenas normalizar e baixar. | Extra | Implementado | Rota `POST /api/admin-etl/processar/`. Aceita `.xls`, mas o `requirements.txt` só traz o `openpyxl`. |

## 2. Requisitos não funcionais

| ID | Categoria | Requisito | Situação | Observação |
|----|-----------|-----------|----------|------------|
| RNF-01 | Tecnologia | Python 3.11+, Django REST Framework e PostgreSQL. | Implementado | Django 5.2, DRF, drf-spectacular e PostgreSQL em uso. |
| RNF-02 | Confiabilidade | O ETL deve ser idempotente e transacional: em caso de erro, nada é gravado pela metade. | Implementado | O cache de CEPs é gravado antes da transação e permanece em caso de erro. |
| RNF-03 | Resiliência | O ETL deve usar timeout nas chamadas ao ViaCEP e cache em tabela, para funcionar com a API externa lenta ou indisponível. | Implementado | Timeout e cache existem (inclusive para CEPs não reconhecidos). Com o ViaCEP fora do ar, o ETL continua com o bairro informado. |
| RNF-04 | Testabilidade | Os testes não podem depender de internet (ViaCEP simulado com mocks) e devem rodar com `python manage.py test`. | Parcial | Existem 29 testes de API e do painel web, que não usam o ViaCEP. Não há testes do ETL nem dos normalizadores, e nem mocks do ViaCEP. |
| RNF-05 | Rastreabilidade | Toda alteração feita pelo ETL deve poder ser auditada (valor original, valor tratado e critério). | Implementado | Seis campos auditados, com histórico acumulado. Campos só aparados não são auditados. |
| RNF-06 | Segurança | Escrita protegida por token; `.env` com senhas e `SECRET_KEY` fora do repositório. | Implementado | Escrita exige token. `.env` está no `.gitignore` e a `main` só tem `.env.example`. Sem `SECRET_KEY` no `.env`, o `settings.py` usa uma chave local de desenvolvimento. |
| RNF-07 | Documentação | API documentada em Redoc; modelo de dados, arquitetura e regras documentados em `docs/`. | Parcial | A API tem Swagger e Redoc, mas o `openapi.yml` está desatualizado e o README cita o Redoc no endereço errado. Os documentos de `docs/` dependem do Pull Request. |
| RNF-08 | Reprodutibilidade | Um terceiro deve conseguir instalar e rodar tudo seguindo só o README, em máquina limpa. | Não verificado | A verificação é a tarefa Q-01 da Fase 6. |
| RNF-09 | Manutenibilidade | Normalizadores reutilizáveis entre ETL e API; fluxo de branches com Pull Request. | Parcial | As regras do ETL ficam em `etl_service.py`, usado pelo comando e pelo envio de planilha no painel. A API usa `normalizadores.py` (CEP) e validações próprias de CNPJ e telefone, com formatos diferentes dos do ETL. |
| RNF-10 | Usabilidade | Front simples (HTML, CSS e JavaScript puro), servido pelo próprio Django. | Implementado | Templates e arquivos estáticos do app `distribuidora`. |

## 3. Observações

- "Não implementado" significa que o requisito não existe nos arquivos analisados. Se houver código em outra branch ou ainda não enviado ao repositório, a situação deve ser atualizada.
- Os 29 testes existem no código, mas não foram executados para esta avaliação (Q-03). Eles cobrem a API e o painel web; não há testes das regras do ETL nem das rotas de exportação e de `admin-etl`.
- Este documento deve ser revisado quando a regra de conflito de bairro for definida.
