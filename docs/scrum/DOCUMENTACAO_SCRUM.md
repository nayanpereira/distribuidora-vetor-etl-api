# Documentação Scrum

Projeto Integrador: Distribuidora Vetor (ETL + API REST)

Este documento reúne os papéis da equipe, a rotina de trabalho, o backlog e o
registro de cada sprint (planning, review e retrospectiva).

**Como ler este documento:** os dados do planejamento (períodos, objetivos,
tarefas e prioridades) vêm do *Roadmap e Backlog* em `docs/scrum/`. Os campos
marcados com **A preencher pela equipe** dependem do que aconteceu de fato nas
reuniões e não foram inventados.

## 1. Equipe e papéis

| Papel | Quem | Responsabilidade |
|-------|------|------------------|
| Product Owner | A preencher pela equipe | Priorizar o backlog e representar as exigências da Primora e do curso. |
| Scrum Master | A preencher pela equipe | Facilitar as reuniões e remover impedimentos. |
| Time de desenvolvimento | Nayan (A), Bruno (B) e Davi (C) | Executar as tarefas das sprints. |

Divisão de foco prevista no roadmap:

| Integrante | Nome | Foco principal | Apoia |
|------------|------|----------------|-------|
| A | Nayan | Dados e ETL (Fases 1 e 2) | Regras de normalização e relatório de trade-offs |
| B | Bruno | Banco e API (Fases 1 e 3) | MER/DER e testes da API |
| C | Davi | Front-end e apresentação (Fases 4 e 7) | Requisitos, UML e Scrum |

A Fase 5 (documentação) é dividida entre os três. Como a avaliação inclui
perguntas da turma, cada integrante deve entender o projeto inteiro e fazer
commits no repositório.

## 2. Rotina e regras de trabalho

| Item | Combinado |
|------|-----------|
| Daily | Reunião de 15 minutos (tarefa G-05). |
| Quadro | Trello ou GitHub Projects, com o backlog importado (tarefa G-04). Ferramenta escolhida: A preencher pela equipe. |
| Repositório | GitHub, com `.gitignore` e regra de branch + Pull Request (tarefa G-03). |
| Fluxo de Git | Sem push direto na `main`. Cada tarefa tem uma branch (`feature/`, `docs/`, `fix/`, `refactor/`) e entra por Pull Request com revisão. |
| Definition of Done | Código revisado, testado e documentado (tarefa G-06). |

## 3. Product Backlog

O backlog completo, com ID, tarefa, área e prioridade, está no PDF
*Roadmap e Backlog* em `docs/scrum/`. Resumo por fase:

Prioridades: P0 = obrigatório, P1 = importante, P2 = extra.

| Fase | Foco | IDs | Tarefas | P0 | P1 | P2 |
|------|------|-----|:-------:|:--:|:--:|:--:|
| 0 | Kickoff | G-01 a G-06 | 6 | 5 | 1 | 0 |
| 1 | Fundações e dados | D-01 a D-03, B-01 a B-06 | 9 | 9 | 0 | 0 |
| 2 | ETL | E-01 a E-12 | 12 | 11 | 0 | 1 |
| 3 | API | A-01 a A-11 | 11 | 10 | 0 | 1 |
| 4 | Front-end | F-01 a F-11 | 11 | 8 | 2 | 1 |
| 5 | Documentação e Scrum | DOC-01 a DOC-10 | 10 | 10 | 0 | 0 |
| 6 | Integração e QA | Q-01 a Q-06 | 6 | 6 | 0 | 0 |
| 7 | Apresentação | P-01 a P-06 | 6 | 4 | 2 | 0 |
| | **Total** | | **71** | **63** | **5** | **3** |

## 4. Sprints

O prazo do projeto é comprimido: o roadmap prevê 12 dias (05/11 a 17/11) para
um escopo pensado para um mês.

### Histórico de commits

Registro do repositório até o commit `85d76d3` (branch `main`):

| Data | Autor | Commit |
|------|-------|--------|
| 06/11 | Nayan Pereira | Estrutura inicial do projeto |
| 10/11 | Nayan Pereira | ETL: lógica de limpeza, integração com o ViaCEP e fallback de bairros |
| 10/11 | Nayan Pereira | Finaliza as Fases 1 e 2, otimiza o `requirements.txt` e atualiza o README |
| 19/11 | brnaum | API REST: conclui a Fase 3 e finaliza os requisitos da Fase 3 (2 commits) |
| 19/11 | brnaum | Painel web da Fase 4 |
| 19/11 | brnaum | Integra as Fases 3 e 4 na `main` |
| 24/11 | Nayan Pereira | Refatora o ETL: regras de normalização e ViaCEP em um serviço reutilizável |
| 24/11 | Nayan Pereira | API: endpoints de exportação, tabela de auditoria e upload de planilha |
| 24/11 | Nayan Pereira | Painel: exportação CSV/Excel e aba de normalização |
| 24/11 | Nayan Pereira | Configuração (`.env.example`), notebook, remoção de rascunho e README |

Os commits de cada integrante aparecem sob os nomes de usuário do Git
(Nayan Pereira e brnaum). A documentação (Fases 5 a 7) ainda não tem commits.

### Sprint 1 (05/11 a 10/11)

**Objetivo:** fechar as decisões e o ambiente, modelar o banco e começar o ETL.

**Fases planejadas:** 0 (Kickoff), 1 (Fundações) e começo da 2 (ETL).

**Marcos de saída previstos:**
- Repositório e quadro Scrum criados e papéis definidos.
- `migrate` roda e as 4 tabelas aparecem no admin.

#### Planning
- Data, participantes e itens escolhidos: A preencher pela equipe.

#### Review
Evidências no repositório que correspondem a itens deste sprint, segundo a
análise do código:

| Item | Evidência |
|------|-----------|
| G-03 | Repositório no GitHub com histórico desde 06/11 e regras de branch e Pull Request no README. |
| B-01 | `requirements.txt` e `requirements-dev.txt` presentes. |
| B-02 | `.env.example` presente na raiz. |
| B-03 | Projeto Django (`config/`, `manage.py`) e app `distribuidora/`. |
| B-04 | `models.py` com `Vendedor`, `Cliente`, `Auditoria` e `CepCache`. |
| B-06 | `admin.py` registra as 4 tabelas; a auditoria não permite criar nem editar. |
| E-01 | O ETL lê o arquivo em texto, com campos vazios como nulos. |
| E-04 | Consulta ao ViaCEP com cache em tabela, timeout e tratamento de CEP inexistente. |
| E-07 | Carga transacional e idempotente (`transaction.atomic()` e `update_or_create`). |

Itens que não puderam ser verificados nos arquivos analisados: G-01, G-02, G-04
a G-06 e D-01 a D-03. O `db/schema.sql` (B-05) não existe no repositório.

- Resultado apresentado e feedback recebido: A preencher pela equipe.

#### Retrospectiva
- O que funcionou bem: A preencher pela equipe.
- O que não funcionou: A preencher pela equipe.
- O que melhorar na próxima sprint: A preencher pela equipe.

### Sprint 2 (11/11 a 14/11)

**Objetivo:** concluir o ETL, construir a API e o front-end e avançar na documentação.

**Fases planejadas:** fim da 2 (ETL), 3 (API), 4 (Front-end) e 5 (Documentação).

**Marcos de saída previstos:**
- `manage.py etl` carrega os 47 clientes e os testes passam.
- Todas as rotas mínimas da API funcionando.
- Fluxo completo no navegador.

**Regra de corte prevista:** se o ETL passar de 11/11, cortar imediatamente as
tarefas extras (P2) e o gráfico do front-end.

#### Planning
- Data, participantes e itens escolhidos: A preencher pela equipe.

#### Review
Evidências no repositório, segundo a análise do código (os commits da API e do
painel são de 19/11; os do ETL refatorado, de 24/11):

| Item | Situação segundo o código |
|------|---------------------------|
| E-02 | Normalizadores de CEP, CNPJ, telefone, e-mail e data, cada um com critério de auditoria (`etl_service.py`). |
| E-03 | Parcial: canoniza Águas Claras, Guará, Taguatinga e Vicente Pires por palavra-chave; o bairro do ViaCEP não é padronizado. |
| E-05 | Parcial: o ViaCEP vence o bairro digitado; `precisa_revisao` só marca cliente sem bairro. |
| E-06 | Seis campos auditados por cliente, em histórico acumulado. |
| E-08 | `manage.py etl` com resumo (`processados, criados e atualizados`). |
| E-09 e E-10 | Não encontrados: não há testes do ETL nem do ViaCEP com mock. |
| E-11 | Pendente: depende de rodar o ETL atual (`REGISTRO_DE_QA.md`). |
| E-12 | Não implementado (dígitos do CNPJ e BrasilAPI). |
| A-01 a A-09 | Serializers, services, CRUD, rotas por bairro e por vendedor, 409 na exclusão do vendedor, token, permissões, Swagger e Redoc. O Redoc está em `/api/redoc/` (o roadmap previa `/api/docs/`). |
| A-10 | 29 testes de API e do painel (`tests.py` e `test_frontend.py`); não foram executados nesta análise. |
| A-11 | Filtro `?precisa_revisao=true` implementado; a normalização do bairro recebido, não. |
| F-02 a F-10 | Painel web em HTML, CSS e JavaScript: login, listagem com paginação, filtros, formulários com erros da API, exclusão com confirmação, vendedores com mensagem do 409, relatório por bairro e modo visitante. |
| F-11 | Lista de clientes que precisam de revisão (tela Relatórios). |
| Extras | Exportação CSV e Excel, aba Normalização para a equipe e envio de planilha (24/11). |

Itens que não puderam ser verificados nos arquivos analisados: F-01 (desenho das telas).

- Itens entregues e demonstração: A preencher pela equipe.

#### Retrospectiva
- O que funcionou bem: A preencher pela equipe.
- O que não funcionou: A preencher pela equipe.
- O que melhorar na próxima sprint: A preencher pela equipe.

### Sprint 3 (15/11 a 17/11)

**Objetivo:** integração, QA e apresentação, **sem nova funcionalidade**.

**Fases planejadas:** 6 (Integração e QA) e 7 (Apresentação).

**Marcos de saída previstos:**
- Tag `v1.0` criada.
- Entrega e apresentação (20 minutos + 5 de perguntas, com demonstração ao vivo).

#### Planning
- Data, participantes e itens escolhidos: A preencher pela equipe.

#### Review
Situação das tarefas de QA e da apresentação (detalhes em `REGISTRO_DE_QA.md`):

| Item | Situação |
|------|----------|
| Q-01 | Parcial: verificado na versão anterior do ETL. |
| Q-02 | A conferir na versão atual. |
| Q-03 | Pendente: 29 testes existentes, sem registro de execução. |
| Q-04 | Parcial: checklist transcrito, com a situação de cada item. |
| Q-05 | Atendido: `.env` fora do repositório e CSV em `dados/`. |
| Q-06 | Pendente: não há tag no repositório. |
| P-01 a P-06 | Não iniciados nos arquivos analisados (slides, roteiro e ensaios não estão no repositório). |

Os commits de 24/11 refatoram o ETL e acrescentam funcionalidades, depois do
período previsto para esta sprint (a regra do roadmap é não criar funcionalidade
nova na Sprint 3).

- Itens entregues e demonstração: A preencher pela equipe.

#### Retrospectiva
- O que funcionou bem: A preencher pela equipe.
- O que não funcionou: A preencher pela equipe.
- O que melhorar: A preencher pela equipe.

## 5. Riscos previstos no roadmap

| Risco | Mitigação prevista |
|-------|--------------------|
| Prazo curto (o guia original prevê 4 semanas) | Se o ETL passar de 11/11, cortar as tarefas P2 e o gráfico do front-end. |
| Sobrecarga de documentação (UML, casos de uso e Scrum fazem parte da avaliação do curso) | Começar esses documentos cedo. |
| Falha na demonstração ao vivo (depende do PostgreSQL e da internet para o ViaCEP) | Cache de CEPs em banco e plano B da demonstração (tarefa P-04). |

## 6. Decisões em aberto registradas no roadmap

| Decisão | O que o código mostra | Decisão do grupo |
|---------|-----------------------|------------------|
| DRF ou FastAPI (o enunciado pede DRF; mudar exige aprovação do professor) | A API usa Django REST Framework e drf-spectacular. | A preencher pela equipe |
| Data de entrega e de apresentação (o roadmap considerou 17/11 para as duas) | Os últimos commits de código são de 24/11. | A preencher pela equipe |
| Nível do bairro | A subdivisão fica no nome do bairro, sem coluna própria. | A preencher pela equipe |
| Quem vence no conflito de bairro | O bairro do ViaCEP vence, sem registro nem revisão. | A preencher pela equipe |
| Data `08-01-2022` | É lida como 8 de janeiro (dia primeiro). | A preencher pela equipe |
| E-mail com acento | O acento é removido e o e-mail é auditado. | A preencher pela equipe |
| CEP inexistente | O CEP do cliente é gravado como nulo e a auditoria registra `Inválido: Reprovado no ViaCEP`. | A preencher pela equipe |
| Guará sem CEP | Mantém o bairro informado (canonizado como `Guará`, `Guará I` ou `Guará II`). | A preencher pela equipe |
