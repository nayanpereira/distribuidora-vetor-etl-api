# Regras de Normalização

Projeto Integrador: Distribuidora Vetor (ETL + API REST)

Este documento descreve as regras de tratamento de dados **que o ETL aplica**,
os critérios registrados na auditoria e os limites conhecidos. Fonte:
`distribuidora/etl_service.py` (motor do ETL), `distribuidora/management/commands/etl.py`
e `distribuidora/models.py`, na branch `main` (commit `85d76d3`, de 24/11).

O mesmo motor é usado pelo comando `python manage.py etl` e pelo envio de
planilhas na aba **Normalização** do painel web (seção 9).

## 1. Visão geral do tratamento

Em cada execução, o ETL faz:

1. **Leitura** do arquivo (CSV ou Excel).
2. **Limpeza do CEP** de todas as linhas.
3. **Consulta do bairro** de cada CEP válido no ViaCEP, com cache.
4. **Tratamento** de bairro, CNPJ, telefone, e-mail e data de cada linha.
5. **Carga**, dentro de uma transação: vendedor, cliente e auditoria.

## 2. Leitura do arquivo

| Regra | Efeito |
|-------|--------|
| Aceita `.csv`, `.xlsx` e `.xls` | Outro formato gera o erro "Formato inválido. Envie um arquivo .csv ou .xlsx." O `.xls` pode falhar, porque o `requirements.txt` só traz o `openpyxl` (para `.xlsx`). |
| Em CSV, o separador (`;` ou `,`) é detectado pelo conteúdo | Funciona com o CSV da Primora (`;`) e com CSVs comuns (`,`). |
| Todas as colunas são lidas como texto e valores como "NA" não viram nulo | Zeros à esquerda não se perdem. |
| Campos vazios ou só com espaços viram nulo | Vale para todas as colunas. |
| Colunas obrigatórias: `id_cliente`, `razao_social`, `cnpj`, `telefone`, `email`, `cep`, `cidade`, `uf`, `data_cadastro`, `vendedor_responsavel` e `bairro_informado` (ou `bairro`) | Se faltar alguma, o ETL informa quais e não grava nada. |

Se o arquivo não puder ser lido, o ETL exibe `Erro ao ler arquivo` com o motivo e encerra.

## 3. Situação do tratamento por campo

| Campo do arquivo | Tratamento | Gravado no banco | Auditado |
|------------------|------------|------------------|----------|
| `id_cliente` | Remoção de espaços nas pontas | Sim | Não |
| `razao_social` | Remoção de espaços nas pontas | Sim | Não |
| `cep` | Limpeza, validação e consulta ao ViaCEP (seção 4) | Sim, quando válido | Sim |
| `bairro_informado` | Bairro do ViaCEP ou canonização por palavra-chave (seção 5) | Sim (bairro final) | Sim |
| `cnpj` | Máscara `00.000.000/0000-00` (seção 6) | Sim | Sim |
| `telefone` | Formato `DD 9XXXX-XXXX` ou `DD XXXX-XXXX` (seção 7) | Sim | Sim |
| `email` | Minúsculas e sem acentos (seção 8) | Sim | Sim |
| `data_cadastro` | Conversão para `AAAA-MM-DD` (seção 9) | Sim | Sim |
| `cidade` | Remoção de espaços nas pontas | Sim | Não |
| `uf` | Remoção de espaços e maiúsculas | Sim | Não |
| `vendedor_responsavel` | Remoção de espaços; vazio vira `Vendedor Desconhecido` | Sim | Não |

## 4. CEP

### 4.1 Regra de limpeza

1. Se o CEP é nulo: resultado nulo, critério `Já era Nulo original`.
2. Mantém só os dígitos (remove pontos, hífens, espaços e letras).
3. Sem nenhum dígito: nulo, `Inválido: Sem caracteres numéricos`.
4. Mais de 8 dígitos: nulo, `Inválido: Excesso de dígitos (N)`.
5. Completa com zeros à esquerda até 8 dígitos. Se o resultado é `00000000`: nulo, `Inválido: Preenchimento genérico (00000000)`.
6. Se o CEP tinha menos de 8 dígitos: `Válido: Higienizado e zeros à esquerda restaurados`. Se tinha 8: `Válido: Higienizado (tamanho original correto)`.

### 4.2 Exemplos

Exemplos construídos a partir da regra, não são linhas reais do CSV.

| Valor original | Valor tratado | Critério |
|----------------|---------------|----------|
| `71215-000` | `71215000` | Válido: Higienizado (tamanho original correto) |
| `7121500` (7 dígitos) | `07121500` | Válido: Higienizado e zeros à esquerda restaurados |
| (vazio) | (nulo) | Já era Nulo original |
| `00000-000` | (nulo) | Inválido: Preenchimento genérico (00000000) |
| `123456789` (9 dígitos) | (nulo) | Inválido: Excesso de dígitos (9) |
| `sem cep` | (nulo) | Inválido: Sem caracteres numéricos |

### 4.3 Consulta ao ViaCEP e cache

- Cada CEP válido e distinto é consultado uma vez por execução, com timeout de 5 segundos e pausa de 0,1 segundo entre consultas.
- O resultado fica na tabela `CepCache` (bairro e indicador `valido`). CEPs não reconhecidos também ficam guardados, como `valido = falso`.
- Um CEP só é consultado de novo se não está no cache, ou se está como válido mas sem bairro.
- **CEP que o ViaCEP não reconhece:** o CEP do cliente é gravado como nulo e a auditoria recebe `Inválido: Reprovado no ViaCEP`.
- **Falha de rede ou resposta diferente de 200:** nada é guardado no cache, o CEP continua válido e o cliente segue sem o bairro do ViaCEP (usa a canonização da seção 5).

`Válido` indica que o **formato** é aceitável e, depois da consulta, que o ViaCEP reconhece o CEP.

## 5. Bairro

### 5.1 Escolha do bairro final

1. Se o CEP é válido e o ViaCEP devolve um bairro, **o bairro do ViaCEP é usado** (`Válido: Trazido do ViaCEP`), no formato em que ele vem.
2. Senão, aplica-se a canonização por palavra-chave ao bairro informado (seção 5.2).
3. Se o bairro informado é vazio, o bairro final é nulo (`Já era Nulo ou Vazio`) e o cliente recebe `precisa_revisao = verdadeiro`.

| Situação | Bairro gravado | `precisa_revisao` |
|----------|----------------|-------------------|
| CEP válido e ViaCEP devolve bairro | Bairro do ViaCEP | Não |
| CEP não reconhecido, sem CEP ou falha na consulta, bairro informado reconhecido pelas regras | Bairro canonizado | Não |
| Idem, mas o bairro informado não bate com nenhuma regra | Bairro informado, sem alteração (`Sem regra: Original mantido`) | Não |
| Sem bairro do ViaCEP e sem bairro informado | Nenhum | Sim |

### 5.2 Canonização por palavra-chave

O texto informado é comparado em maiúsculas, nesta ordem:

| Se o texto contém | Resultado |
|-------------------|-----------|
| `PIRES` | Vicente Pires |
| `AGUAS` ou `ÁGUAS` | Águas Claras Norte (com `NORTE`), Águas Claras Sul (com `SUL`) ou Águas Claras |
| `GUARA` ou `GUARÁ` | Guará II (com `II`), Guará I (com `I`) ou Guará |
| `TAGUATINGA` | Taguatinga Sul (com `SUL`) ou Taguatinga |
| nada disso | O texto original é mantido |

Critérios de auditoria: `Válido: Já no padrão` (já estava igual ao resultado), `Canonizado: De "x" para "y"` e `Sem regra: Original mantido`.

Exemplos: `Vte Pires` e `V. Pires` viram `Vicente Pires`; `taguatinga sul` vira `Taguatinga Sul`; `guara - df` vira `Guará`.

### 5.3 O que o código não faz com o bairro

- **Não detecta conflito** entre o bairro informado e o do ViaCEP: quando o ViaCEP responde, ele vence, sem aviso e sem marcar revisão.
- **Não padroniza o bairro devolvido pelo ViaCEP.** Nomes como `Sul (Águas Claras)`, `Norte (Águas Claras)`, `Setor Habitacional Vicente Pires`, `Taguatinga Norte` e `Areal` são gravados como chegam, e convivem com `Águas Claras Sul` ou `Vicente Pires`, vindos da canonização.
- **Não separa a subdivisão** em uma coluna própria: ela fica no nome (`Águas Claras Norte`, `Guará II`).
- **`Taguatinga Norte` informado** (sem ViaCEP) vira `Taguatinga`, porque só `SUL` é tratado para Taguatinga.
- A regra de Guará procura a letra `I` em qualquer parte do texto, então textos com `I` fora do sufixo podem virar `Guará I`.

## 6. CNPJ

| Situação | Valor tratado | Critério |
|----------|---------------|----------|
| 14 dígitos (com ou sem máscara) | `00.000.000/0000-00` | Válido: Máscara aplicada |
| Outra quantidade de dígitos | O texto original, sem espaços nas pontas | Inválido: N dígitos numéricos |
| Vazio | Nulo | Nulo ou Vazio |

Só o tamanho é conferido; os dígitos verificadores não são validados.

## 7. Telefone

1. Mantém só os dígitos.
2. Se começa com `55` e tem 12 ou 13 dígitos, remove o `55`.
3. Com 11 dígitos: `DD 9XXXX-XXXX`, critério `Celular aplicado`.
4. Com 10 dígitos: `DD XXXX-XXXX`, critério `Fixo aplicado`.
5. O critério ganha ` (+55 removido)` quando o DDI foi retirado.
6. Outro tamanho: os dígitos, sem formato, com `Inválido: Tamanho N`. Vazio: nulo, `Nulo ou Vazio`.

O formato gravado não usa parênteses (por exemplo, `61 99999-9999`).

## 8. E-mail

1. Converte para minúsculas e remove os acentos.
2. Se não tem `@` ou não tem `.`: mantém o texto limpo e registra `Inválido: Falta @ ou ponto`.
3. Se o resultado é diferente do original: `Válido: Higienizado`. Se é igual: `Válido: Padrão correto`.
4. Vazio: nulo, critério `Nulo`.

## 9. Data de cadastro

- Datas que começam com `AAAA-` são lidas como ano-mês-dia.
- As demais são lidas com **dia primeiro** (por exemplo, `08-01-2022` vira 8 de janeiro de 2022).
- O resultado é gravado como `AAAA-MM-DD`, critério `Convertido (YYYY-MM-DD)`.
- Texto que não vira data: nulo, `Inválido: "valor"`. Vazio: nulo, `Nulo`.

## 10. Vendedor

- O nome é lido sem espaços nas pontas.
- Nome vazio: o cliente fica ligado a um vendedor chamado `Vendedor Desconhecido`.
- A busca do vendedor é pelo nome **exato**: grafias diferentes do mesmo nome criam vendedores diferentes.

## 11. Auditoria

| Item | Regra atual |
|------|-------------|
| Campos auditados | `cep`, `bairro`, `cnpj`, `telefone`, `email` e `data_cadastro` |
| Quantidade | 6 linhas por cliente em cada execução |
| Conteúdo | Valor original, valor tratado e critério |
| Ciclo de vida | **Histórico acumulado**: o ETL não apaga as linhas anteriores |
| Consulta | A tela Normalização do painel mostra o registro mais recente de cada campo; o Django Admin lista todos |
| Acesso | Django Admin (não permite criar nem editar; a exclusão não está bloqueada) e aba Normalização, só para usuários da equipe |

A auditoria não registra o motivo da escolha entre o bairro digitado e o do ViaCEP quando há divergência.

## 12. Idempotência e execução

- O cliente é identificado pelo `id_cliente`: se já existe, é atualizado; se não, é criado. Rodar o ETL de novo não duplica clientes.
- O terminal informa `ETL Concluído! N processados (X criados, Y atualizados).`
- A carga roda numa transação: em caso de erro, clientes, vendedores e auditoria da carga não ficam gravados pela metade. O cache de CEPs é gravado antes e permanece.
- Como a auditoria é acumulada, cada execução acrescenta 6 linhas por cliente, mesmo que os dados não mudem.

## 13. Envio de planilha pelo painel

Na aba **Normalização** (só para usuários da equipe), é possível enviar um `.csv` ou `.xlsx`:

- **Salvar:** as mesmas regras são aplicadas e os dados entram no banco, com auditoria.
- **Apenas exportar:** as regras são aplicadas e a planilha tratada é devolvida em CSV ou Excel, **sem gravar** clientes nem auditoria. Os resultados do ViaCEP não são guardados no cache nesse modo.

## 14. Limites conhecidos

1. **Conflito de bairro não é detectado:** o ViaCEP vence sem registro e sem revisão (seção 5.3).
2. **Bairros do ViaCEP não são padronizados**, o que mantém formas diferentes para a mesma região.
3. **Canonização por palavra-chave:** cobre só Águas Claras, Guará, Taguatinga e Vicente Pires; `Taguatinga Norte` informado vira `Taguatinga`.
4. **Formatos diferentes entre ETL e API:** o ETL grava o CNPJ com máscara e o telefone como `DD 9XXXX-XXXX`; a API grava os dois só com dígitos. A mesma coluna pode ter os dois formatos.
5. **CEP com menos de 8 dígitos** recebe zeros à esquerda; só se confirma se o ViaCEP reconhecer o CEP.
6. **Falha de rede:** o cliente fica sem o bairro do ViaCEP, e o CEP segue como válido.
7. **CNPJ:** só o tamanho é conferido.
8. **Sem testes automatizados** das regras do ETL: os 29 testes existentes cobrem a API e o painel web.
9. **Auditoria acumulada** cresce a cada execução.

## 15. Resultado esperado com o CSV atual

Números que dependem só do arquivo (calculados a partir das regras):

| Indicador | Valor |
|-----------|-------|
| Linhas lidas e vendedores distintos | 47 e 5 |
| Grafias distintas de bairro no arquivo | 25, mais 1 linha sem bairro |
| CEPs distintos válidos (consultados no ViaCEP) | 14 |
| CEP vazio / preenchimento genérico | 13 / 3 |
| CNPJ com máscara aplicada | 9 (os outros 38 já estavam com máscara) |
| Telefones: celular / fixo | 33 / 14 (12 com `+55` removido) |
| E-mails higienizados | 10 (os outros 37 já estavam corretos) |
| Datas em outros formatos (convertidas) | 24 de 47 |
| Linhas de auditoria por execução | 282 (47 × 6) |

Números que dependem da resposta do ViaCEP, **estimados por simulação** com as respostas registradas no guia do curso e a confirmar na execução real (`REGISTRO_DE_QA.md`):

| Indicador | Valor estimado |
|-----------|----------------|
| CEPs reprovados no ViaCEP | 2 CEPs, 3 clientes |
| CEPs válidos confirmados | 28 clientes |
| Clientes sem CEP gravado | 19 (13 vazios, 3 genéricos e 3 reprovados) |
| Bairros finais distintos | 12, mais 1 cliente sem bairro |
| Clientes para revisão | 1 (CLI0047, sem bairro e sem CEP) |
| Bairro do CEP no lugar do informado, em conflito | CLI0010, CLI0012 e CLI0032 em `Areal`; CLI0002 em `Taguatinga Norte` |

Esses quatro clientes já foram conferidos no banco com a versão anterior do ETL, que usava a mesma regra de prioridade do ViaCEP.
