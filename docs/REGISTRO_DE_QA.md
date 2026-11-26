# Registro de QA (Fase 6)

Projeto Integrador: Distribuidora Vetor (ETL + API REST)

Este documento registra o que já foi verificado na fase de integração e QA, a
evidência de cada verificação e o que ainda falta. Ele deve ser atualizado a
cada nova verificação. Estado do código avaliado: branch `main`, commit
`85d76d3` (24/11).

## 1. Situação das tarefas

| ID | Verificação | Situação | Evidência e o que falta |
|----|-------------|----------|-------------------------|
| Q-01 | Alguém que não escreveu o código clona o repositório e roda tudo só pelo README | Parcial | `migrate` e `etl` já rodaram em um clone novo, mas na versão anterior à refatoração do ETL (24/11). Falta repetir na versão atual, seguindo um dos cenários do README até o painel web e a API. |
| Q-02 | ETL do zero em banco vazio, duas vezes, sem duplicar | A conferir | O código usa `update_or_create` pelo `id_cliente`. Falta rodar a versão atual duas vezes (seção 3). |
| Q-03 | `python manage.py test` completo | Pendente | Existem 29 testes (API e painel web). Falta rodar e anotar o resultado. |
| Q-04 | Checklist final do guia (seção 19) | Parcial | Checklist na seção 5, com a situação de cada item. |
| Q-05 | `.env` fora do repositório e CSV dentro | Atendido | O `.gitignore` ignora o `.env` e a `main` só tem o `.env.example`. O CSV está em `dados/` (e há uma cópia em `docs/material-base/`). |
| Q-06 | Congelar o código e criar a tag `v1.0` | Pendente | O repositório ainda não tem nenhuma tag. Depende de o grupo fechar o checklist e a decisão sobre o conflito de bairro. |

## 2. Execução anterior (ETL antes de 24/11)

Registro histórico da primeira verificação, feita antes da refatoração do ETL.
Esses números **não valem mais** para a versão atual, porque o ETL passou a
tratar mais campos e a auditoria passou a ser acumulada.

| Indicador | Valor naquela execução |
|-----------|------------------------|
| Clientes / vendedores / CEPs no cache | 47 / 5 / 14 |
| CEPs não reconhecidos pelo ViaCEP | 2 |
| Clientes marcados para revisão | 1 |
| Grafias distintas de bairro gravadas | 17, mais 1 cliente sem bairro |
| Bairro do ViaCEP no lugar do informado | CLI0002 (`Taguatinga Norte`) e CLI0010, CLI0012 e CLI0032 (`Areal`) |

## 3. Como verificar a versão atual

### 3.1 Primeira execução

```bash
git pull origin main
python manage.py migrate
python manage.py etl
```

Saída esperada:

```
Iniciando ETL a partir de: dados/clientes_distribuidora_vetor.csv
Arquivo lido com sucesso. Total de linhas: 47
Executando regras de higienização, ViaCEP e carga no PostgreSQL...
ETL Concluído! 47 processados (47 criados, 0 atualizados).
```

Se o banco já tinha os clientes da execução anterior, o resumo mostra `0 criados, 47 atualizados`.

### 3.2 Conferência no banco

```bash
python manage.py shell
```

Cole uma linha de cada vez:

```python
from distribuidora.models import Cliente, Vendedor, Auditoria, CepCache
from django.db.models import Count
print(Cliente.objects.count(), Vendedor.objects.count(), Auditoria.objects.count(), CepCache.objects.count())
print(Cliente.objects.filter(precisa_revisao=True).count())
print(Cliente.objects.filter(cep__isnull=True).count())
print(CepCache.objects.filter(valido=False).count())
print(Cliente.objects.values('bairro').distinct().count())
print(list(Cliente.objects.values_list('bairro', flat=True).distinct().order_by('bairro')))
print(list(Auditoria.objects.values('campo').annotate(n=Count('id'))))
print(list(Cliente.objects.filter(id_cliente__in=['CLI0002','CLI0010','CLI0012','CLI0032']).values_list('id_cliente','bairro')))
```

Resultado esperado em um **banco vazio** (os valores marcados com * dependem da resposta do ViaCEP e foram estimados por simulação com as respostas registradas no guia do curso):

| Linha | Esperado |
|-------|----------|
| 1 | `47 5 282 14` (a auditoria tem 47 × 6 linhas) |
| 2 | `1` * (CLI0047, sem bairro e sem CEP) |
| 3 | `19` * (13 vazios, 3 genéricos e 3 reprovados no ViaCEP) |
| 4 | `2` * |
| 5 | `13` * (12 bairros mais o valor nulo) |
| 7 | 47 linhas para cada um de `cep`, `bairro`, `cnpj`, `telefone`, `email` e `data_cadastro` |
| 8 | CLI0002 em `Taguatinga Norte`; CLI0010, CLI0012 e CLI0032 em `Areal` * |

Resultado obtido: A preencher pela equipe.

### 3.3 Q-02: segunda execução

Rode `python manage.py etl` de novo e repita a primeira linha de contagem. O resumo deve mostrar `0 criados, 47 atualizados`, e o resultado deve ser `47 5 564 14`: clientes, vendedores e cache não mudam, e a auditoria **cresce 282 linhas**, porque ela é um histórico acumulado e não um duplicado de clientes.

Resultado obtido: A preencher pela equipe.

### 3.4 Q-03: testes

```bash
python manage.py test
```

Resultado esperado: 29 testes. Anote quantos passaram.

Resultado obtido: A preencher pela equipe.

### 3.5 Q-06: tag (quando o código estiver congelado)

```bash
git checkout main
git pull
git tag -a v1.0 -m "Versão 1.0 do Projeto Integrador"
git push origin v1.0
```

## 4. Itens fora do checklist que merecem teste manual

Estas funcionalidades não têm testes automatizados:

- Exportar CSV e Excel na tela de clientes (usuário logado).
- Aba Normalização com usuário da equipe: tabela de tratamento e envio de planilha, nos dois modos (salvar e apenas exportar).
- Envio de um arquivo `.xls`, que depende de uma biblioteca que não está no `requirements.txt`.

Quem fizer o teste anota aqui o resultado: A preencher pela equipe.

## 5. Checklist final do guia (Q-04)

Itens da seção 19 do guia de construção (`docs/material-base/guia_de_construção.md`), com a situação segundo a leitura do código e o histórico do repositório.

Legenda: **Atendido**, **Parcial**, **Não atendido** e **A conferir** (falta rodar uma verificação).

### Parte 1: ETL

| Item do guia | Situação | Evidência e o que falta |
|--------------|----------|-------------------------|
| `python manage.py etl` roda do zero num banco vazio | A conferir | Rodou na versão anterior; falta a versão atual (seção 3.1). |
| Rodar duas vezes mantém 47 clientes e 5 vendedores | A conferir | Seção 3.3. |
| CNPJs, telefones e CEPs gravados no mesmo formato | Atendido | O ETL grava CNPJ com máscara, telefone como `DD 9XXXX-XXXX` e CEP com 8 dígitos. Ressalva: a API grava CNPJ e telefone só com dígitos. |
| Todas as datas convertidas para `date` | Atendido | Conversão para `AAAA-MM-DD`, com dia primeiro nos formatos ambíguos. |
| Bairros agrupados (poucos bairros, não dezenas) | Parcial | De 25 grafias para cerca de 12 (estimativa); o guia espera 4. Os nomes do ViaCEP não são padronizados. |
| Conflitos entre bairro e CEP marcados com `precisa_revisao` | Não atendido | O conflito não é detectado; só o cliente sem bairro é marcado. |
| Toda decisão na auditoria, com valor original, tratado, critério e fonte | Parcial | Seis campos auditados com original, tratado e critério. Não há coluna de fonte, e razão social, cidade, UF e vendedor não são auditados. |
| ViaCEP com cache: a segunda execução não consulta a API de novo | Atendido | CEPs reconhecidos e não reconhecidos ficam no cache; falha de rede não é guardada. |
| Testes de normalização passam sem internet | Não atendido | Não há testes das regras do ETL. |
| Regras, limites e trade-offs documentados | Atendido | `REGRAS_DE_NORMALIZACAO.md` e `RELATORIO_TRADEOFFS.md` (após entrarem no repositório). |

### Parte 2: API

| Item do guia | Situação | Evidência e o que falta |
|--------------|----------|-------------------------|
| CRUD de clientes e de vendedores funcionando | Atendido | Implementado e coberto pelos testes existentes (não executados aqui). |
| `/api/clientes/bairro/{nome}/` aceita grafias diferentes | Parcial | Ignora maiúsculas, acentos e pontuação; não unifica variantes como `Águas Claras/DF`. |
| Rotas por vendedor funcionando | Atendido | `/api/clientes/vendedor/{id}/` e `/api/vendedores/{id}/clientes/`. |
| `/api/auth/token/` devolve token | Atendido | |
| Sem token: GET responde 200; escrita responde 401 | Atendido | |
| Com token: CRUD completo | Atendido | |
| As quatro tabelas aparecem no admin; a auditoria não aparece na API | Atendido, com ressalva | O guia também bloqueia a exclusão da auditoria no admin; o `admin.py` bloqueia só criar e editar. |
| `/api/docs/` abre a documentação Redoc | Parcial | `/api/docs/` abre o Swagger; o Redoc está em `/api/redoc/`. O `openapi.yml` do repositório está desatualizado. |
| `python manage.py test` passa | A conferir | Seção 3.4. |

### Pronto para entregar

| Item do guia | Situação | Evidência e o que falta |
|--------------|----------|-------------------------|
| Outra pessoa do grupo clonou o repositório e rodou tudo só pelo README | Parcial | Verificação feita na versão anterior; falta repetir na atual. |
| `.env` fora do GitHub e `.env.example` dentro | Atendido | Ver Q-05. |
| Todos do grupo têm commits | Não atendido | Até o commit `85d76d3`, os autores são só Nayan Pereira e brnaum. Quando o Pull Request da documentação for aceito, o terceiro integrante passa a ter commits. |

### Critérios de avaliação da Primora

| Critério | Situação atual |
|----------|----------------|
| Cobertura do tratamento | Boa: CEP, bairro, CNPJ, telefone, e-mail e data são tratados. O bairro tem limites (conflitos e nomes do ViaCEP). |
| Qualidade da decisão | A regra do conflito de bairro ainda está em aberto (`REGRAS_DE_NORMALIZACAO.md`, seção 14). |
| Documentação e rastreabilidade | Documentação pronta; a auditoria cobre seis campos, em histórico acumulado. |
| Testes | Há testes da API e do painel; faltam os do ETL. |
| Comunicação | Relatório de trade-offs pronto. Os números que dependem do ViaCEP são estimados até a execução real. |
