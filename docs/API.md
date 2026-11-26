# Documentação da API

Projeto Integrador: Distribuidora Vetor (ETL + API REST)

Este documento descreve a API REST **como ela está no código** (branch `main`,
commit `85d76d3`, de 24/11). Fonte: `distribuidora/views.py`, `serializers.py`,
`services.py`, `etl_service.py`, `urls.py`, `config/urls.py` e `tests.py`.

Os exemplos de resposta mostram o **formato** dos dados, com valores
ilustrativos. A documentação interativa gerada pelo código está em
`/api/docs/` (Swagger) e `/api/redoc/` (Redoc).

## 1. Visão geral

| Item | Valor |
|------|-------|
| Endereço base local | `http://127.0.0.1:8000/api/` |
| Formato | JSON |
| Autenticação | Token (`Authorization: Token <chave>`) |
| Permissões | Visitante: somente leitura (GET). Usuário autenticado: leitura e escrita. Equipe (`is_staff`): também as rotas `admin-etl`. |
| Paginação | Lista de clientes: 20 por página, parâmetro `?page=N` |

## 2. Autenticação

1. Envie `POST /api/auth/token/` (ou `/api/token/`, que faz o mesmo) com `username` e `password`.
2. A API devolve `{"token": "<chave>"}`.
3. Envie o token em toda requisição de escrita, no cabeçalho `Authorization: Token <chave>`.

Sem token, apenas as consultas (GET) funcionam. Escrever sem token responde **401**. Usuário autenticado que não é da equipe, ao chamar uma rota `admin-etl`, recebe **403**.
O usuário precisa existir antes (por exemplo, criado com `python manage.py createsuperuser`).
Credenciais inválidas são recusadas pelo comportamento padrão do Django REST Framework
(resposta 400).

Exemplo no PowerShell:

```powershell
$base = 'http://127.0.0.1:8000/api'
$login = Invoke-RestMethod -Method Post "$base/auth/token/" -Body @{username='admin'; password='SUA_SENHA'}
$headers = @{Authorization = "Token $($login.token)"}
```

## 3. Rotas

| Método | Rota | Quem pode | Descrição |
|--------|------|-----------|-----------|
| POST | `/api/auth/token/` e `/api/token/` | Todos | Obtém o token |
| GET | `/api/clientes/` | Todos | Lista clientes (paginada) |
| POST | `/api/clientes/` | Autenticado | Cria cliente |
| GET | `/api/clientes/{id}/` | Todos | Detalha um cliente |
| PUT, PATCH | `/api/clientes/{id}/` | Autenticado | Altera um cliente |
| DELETE | `/api/clientes/{id}/` | Autenticado | Exclui um cliente |
| GET | `/api/clientes/bairro/{nome}/` | Todos | Clientes de um bairro (paginada) |
| GET | `/api/clientes/bairros/` | Todos | Total de clientes por bairro |
| GET | `/api/clientes/vendedor/{id}/` | Todos | Clientes de um vendedor (paginada) |
| GET | `/api/vendedores/` | Todos | Lista vendedores |
| POST | `/api/vendedores/` | Autenticado | Cria vendedor |
| GET | `/api/vendedores/{id}/` | Todos | Detalha um vendedor |
| PUT, PATCH | `/api/vendedores/{id}/` | Autenticado | Altera um vendedor |
| DELETE | `/api/vendedores/{id}/` | Autenticado | Exclui um vendedor (409 se tiver clientes) |
| GET | `/api/vendedores/{id}/clientes/` | Todos | Clientes de um vendedor (sem paginação) |
| GET | `/api/auth/perfil/` | Autenticado | Nome do usuário e se ele é da equipe |
| GET | `/api/clientes/exportar/` | Autenticado | Baixa a base tratada em CSV ou Excel |
| GET | `/api/admin-etl/tabela/` | Equipe | Tabela de normalização (original, final e critério) |
| POST | `/api/admin-etl/processar/` | Equipe | Envia uma planilha para normalizar |
| GET | `/api/schema/` | Todos | Esquema OpenAPI |
| GET | `/api/docs/` | Todos | Documentação Swagger |
| GET | `/api/redoc/` | Todos | Documentação Redoc |

Nas rotas de cliente e de vendedor, `{id}` é o número do registro no banco (`id`),
e não o código `id_cliente` do CSV.

## 4. Clientes

### 4.1 Campos

| Campo | Visitante vê | Autenticado | Observação |
|-------|:------------:|:-----------:|------------|
| `id` | Sim | Sim | Número do registro |
| `id_cliente` | Sim | Sim | Código do cliente (único) |
| `razao_social` | Sim | Sim | Obrigatório |
| `bairro` | Sim | Sim | Opcional |
| `cep` | Sim | Sim | Opcional; gravado com 8 dígitos |
| `cidade` | Sim | Sim | Obrigatório |
| `uf` | Sim | Sim | Obrigatório; gravado em maiúsculas |
| `data_cadastro` | Sim | Sim | Opcional (`AAAA-MM-DD`) |
| `vendedor_responsavel` | Sim | Sim | Obrigatório; número (`id`) do vendedor |
| `precisa_revisao` | Sim | Sim | Somente leitura: a API ignora tentativas de alterá-lo |
| `cnpj` | Não | Sim | Opcional |
| `telefone` | Não | Sim | Opcional |
| `email` | Não | Sim | Opcional |

O visitante nunca recebe `cnpj`, `telefone` e `email`, em nenhuma rota.

Formato de um cliente para usuário autenticado (valores ilustrativos):

```json
{
  "id": 1,
  "id_cliente": "CLI0001",
  "razao_social": "Empresa Exemplo Ltda",
  "bairro": "Águas Claras",
  "cep": "71926750",
  "cidade": "Brasília",
  "uf": "DF",
  "data_cadastro": null,
  "vendedor_responsavel": 1,
  "precisa_revisao": false,
  "cnpj": "11222333000181",
  "telefone": "61912345678",
  "email": "contato@exemplo.com.br"
}
```

### 4.2 Validações na entrada (POST, PUT e PATCH)

| Campo | Regra | Valor gravado |
|-------|-------|---------------|
| `uf` | Precisa ser uma sigla de estado brasileiro | Maiúsculas (`sp` vira `SP`) |
| `cnpj` | 14 caracteres alfanuméricos, com ou sem máscara (`00.000.000/0000-00`); os dois últimos são números | Sem pontos, barras e hífen |
| `cep` | 8 dígitos, com ou sem hífen (`01310-100` ou `01310100`) | 8 dígitos |
| `telefone` | Telefone brasileiro com DDD, com ou sem DDI `55`, parênteses e hífen | Só dígitos |

Valores vazios ou nulos são aceitos nesses quatro campos, quando eles são opcionais.

O ETL grava o CNPJ com máscara e o telefone como `DD 9XXXX-XXXX`; a API grava os dois só com dígitos. Os dois formatos podem aparecer na mesma coluna.
Dados inválidos respondem **400**, com a mensagem por campo.

### 4.3 Listar clientes

`GET /api/clientes/`

Parâmetros:

| Parâmetro | Descrição |
|-----------|-----------|
| `page` | Número da página (20 clientes por página) |
| `precisa_revisao` | `true` ou `false`. Qualquer outro valor responde 400 |

Resposta (formato paginado):

```json
{
  "count": 47,
  "next": "http://127.0.0.1:8000/api/clientes/?page=2",
  "previous": null,
  "results": [ { "id": 1, "id_cliente": "CLI0001", "...": "..." } ]
}
```

As rotas `/api/clientes/bairro/{nome}/` e `/api/clientes/vendedor/{id}/` usam o mesmo formato
paginado e também aceitam `precisa_revisao`.

### 4.4 Clientes por bairro

`GET /api/clientes/bairro/{nome}/`

A comparação do nome ignora maiúsculas, acentos e pontuação, e trata hífen e sublinhado como espaço.
Por exemplo, `Águas Claras`, `aguas-claras` e `AGUAS CLARAS` encontram os mesmos clientes.

Limite: a comparação é feita com o bairro **como está gravado**. Variantes que diferem por
mais do que isso, como `Águas Claras/DF`, `Vte Pires` ou `Águas Claras Sul`, são tratadas como
outros bairros.

### 4.5 Total de clientes por bairro

`GET /api/clientes/bairros/` (sem paginação)

Agrupa os bairros pela mesma comparação (maiúsculas, acentos e pontuação) e conta os clientes de
cada grupo. Clientes sem bairro formam um grupo com `bairro: null`.

```json
[
  { "bairro": "Águas Claras", "total": 10 },
  { "bairro": null, "total": 1 }
]
```

### 4.6 Clientes por vendedor

`GET /api/clientes/vendedor/{id}/` (paginada) e `GET /api/vendedores/{id}/clientes/` (sem paginação).
Se o vendedor não existe, as duas respondem **404**.

## 5. Vendedores

| Campo | Observação |
|-------|------------|
| `id` | Número do registro |
| `nome` | Nome do vendedor (obrigatório) |

`DELETE /api/vendedores/{id}/` responde **409** quando o vendedor tem clientes vinculados:

```json
{ "detail": "Não é possível excluir um vendedor que possui clientes vinculados." }
```

A lista de vendedores não é paginada.

## 6. Exportação e rotas da equipe

### 6.1 Perfil

`GET /api/auth/perfil/` (autenticado) devolve:

```json
{ "username": "admin", "is_staff": true, "is_superuser": true }
```

O painel usa essa resposta para decidir se mostra a aba Normalização.

### 6.2 Exportar a base tratada

`GET /api/clientes/exportar/?formato=csv` ou `?formato=xlsx` (autenticado). Qualquer valor diferente de `csv` devolve Excel.

O arquivo (`clientes_vetor_normalizados.csv` ou `.xlsx`) tem as colunas `id_cliente`, `razao_social`, `cnpj`, `telefone`, `email`, `bairro`, `cep`, `cidade`, `uf`, `data_cadastro` e `vendedor_responsavel` (nome do vendedor), ordenadas pelo `id_cliente`. O CSV usa `;` como separador.

### 6.3 Tabela de normalização

`GET /api/admin-etl/tabela/` (equipe) devolve uma lista com um item por cliente. Para `cep`, `bairro`, `cnpj`, `telefone`, `email` e `data_cadastro`, traz o valor original, o valor tratado e o critério do registro de auditoria mais recente (ou `Sem registro`):

```json
{
  "id": 1,
  "id_cliente": "CLI0001",
  "razao_social": "Empresa Exemplo Ltda",
  "vendedor": "Nome do vendedor",
  "cidade": "Brasília",
  "uf": "DF",
  "precisa_revisao": false,
  "bairro": { "original": "aguas claras", "tratado": "Águas Claras", "criterio": "Canonizado: De \"aguas claras\" para \"Águas Claras\"" }
}
```

(O exemplo mostra só o campo `bairro`; a resposta traz os seis campos.)

### 6.4 Enviar uma planilha

`POST /api/admin-etl/processar/` (equipe), com `multipart/form-data`:

| Campo | Descrição |
|-------|-----------|
| `arquivo` | Arquivo `.csv` ou `.xlsx`, com as colunas obrigatórias do ETL |
| `modo` | `salvar` grava no banco; qualquer outro valor só normaliza e devolve a planilha |
| `formato_saida` | `xlsx` (padrão) ou `csv`, usado quando o modo não é `salvar` |

- **Modo `salvar`:** responde 200 com `mensagem`, `processados`, `criados` e `atualizados`. A auditoria recebe novas linhas.
- **Outros modos:** devolve o arquivo normalizado (`planilha_normalizada_avulsa`) e não grava clientes nem auditoria.
- **Arquivo ausente, formato inválido ou colunas faltando:** responde 400 com a mensagem no campo `arquivo`.

Essas quatro rotas novas não têm testes automatizados e não constam no `openapi.yml` do repositório.

## 7. Códigos de resposta

| Código | Quando |
|--------|--------|
| 200 | Consulta ou alteração com sucesso |
| 201 | Cliente ou vendedor criado |
| 204 | Cliente ou vendedor excluído |
| 400 | Dados inválidos, ou `precisa_revisao` diferente de `true` e `false` |
| 401 | Escrita sem token, ou exportação sem token |
| 403 | Rota de `admin-etl` chamada por usuário que não é da equipe |
| 404 | Cliente, vendedor ou página inexistente |
| 409 | Exclusão de vendedor que tem clientes |

## 8. Exemplos

```powershell
# Consultas (sem login)
Invoke-RestMethod "$base/clientes/"
Invoke-RestMethod "$base/clientes/bairros/"
Invoke-RestMethod "$base/clientes/bairro/aguas-claras/"
Invoke-RestMethod "$base/clientes/?precisa_revisao=true"
Invoke-RestMethod "$base/vendedores/1/clientes/"

# Escrita (com o token obtido na seção 2)
Invoke-RestMethod -Method Post "$base/vendedores/" -Headers $headers -Body @{nome='Nome do vendedor'}
Invoke-RestMethod -Method Patch "$base/clientes/1/" -Headers $headers -Body @{uf='sp'}
```

Para ver o código de resposta nos erros, use `curl.exe -i`:

```powershell
curl.exe -i -X DELETE "http://127.0.0.1:8000/api/clientes/1/"
```

Sem token, esse comando responde 401.

## 9. Documentação interativa

| Endereço | O que mostra |
|----------|--------------|
| `/api/docs/` | Swagger, com possibilidade de testar as rotas |
| `/api/redoc/` | Redoc |
| `/api/schema/` | Esquema OpenAPI |
| `openapi.yml` (raiz do repositório) | Cópia do esquema salva em arquivo; está desatualizada e não inclui as rotas de exportação, perfil e `admin-etl` |

As páginas de documentação carregam arquivos de uma CDN na internet.

## 10. Painel web

O mesmo servidor entrega um painel simples que consome esta API:

| Endereço | Tela |
|----------|------|
| `/` | Redireciona para o login |
| `/entrar/` | Login (ou seguir como visitante) |
| `/clientes/` | Lista, busca por bairro, filtro por vendedor, criação, edição, exclusão e exportação em CSV ou Excel (autenticado) |
| `/vendedores/` | Lista, criação, edição e exclusão |
| `/relatorios/` | Clientes por bairro e clientes que precisam de revisão |
| `/normalizacao/` | Aba da equipe: tabela de normalização e envio de planilha (aparece só para usuários da equipe) |

O painel guarda o token (e a informação de que o usuário é da equipe) só na memória da página: ao recarregar, ele volta ao modo visitante.
