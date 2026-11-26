# Relatório de Trade-offs

Projeto Integrador: Distribuidora Vetor

Este relatório explica, em linguagem simples, as escolhas feitas no tratamento
da base de clientes, o que cada uma traz de bom e o que custa. Ele descreve o
sistema **como está hoje**.

## 1. O que o sistema faz hoje

O sistema lê o arquivo de clientes, padroniza os dados (CEP, bairro, CNPJ,
telefone, e-mail e data de cadastro), pergunta o bairro correspondente a um
serviço público de consulta de CEP (o ViaCEP) e guarda tudo em um banco de
dados. Para cada campo tratado, ele registra o valor original, o valor final
e o motivo da decisão.

Os dados tratados podem ser consultados por uma API e por um painel web:
qualquer pessoa consulta, quem tem login altera os dados e baixa a base em
CSV ou Excel, e a equipe administrativa vê a tabela completa de tratamento e
pode enviar novas planilhas.

## 2. Resultado em números

Com o arquivo de clientes atual:

- **47 clientes** carregados, ligados a **5 vendedores**.
- **Bairros:** o arquivo trazia **25 formas diferentes** de escrever os
  bairros. Depois do tratamento, ficam cerca de **12** (estimativa; veja a nota
  abaixo) e 1 cliente sem bairro, que é marcado para revisão manual.
- **CEP:** 13 clientes não tinham CEP e 3 tinham um CEP genérico (zerado).
  Cerca de 3 clientes têm CEP que o ViaCEP não reconhece. No total, perto de
  **19 dos 47** ficam sem CEP gravado, e **28** têm o CEP confirmado.
- **CNPJ:** os 47 ficam no mesmo formato (9 precisaram de ajuste).
- **Telefone:** os 47 ficam no mesmo formato, 33 celulares e 14 fixos (12 tinham
  o código do país `+55`, que foi retirado).
- **E-mail:** 10 e-mails foram corrigidos (letras maiúsculas ou acentos).
- **Data de cadastro:** as 47 viraram o formato único `ano-mês-dia`; 24 estavam
  em outros formatos.
- **4 clientes** (CLI0002, CLI0010, CLI0012 e CLI0032) ficaram com o bairro
  indicado pelo CEP, "Areal" em três casos e "Taguatinga Norte" em um. Nenhum
  foi marcado para revisão.

> Nota: os números que dependem da resposta do ViaCEP (bairros finais, CEPs
> reprovados e os 4 clientes acima) foram estimados por simulação, com as
> respostas do serviço registradas no guia do curso. Devem ser confirmados na
> execução real (`REGISTRO_DE_QA.md`). Os demais números vêm só do arquivo.

## 3. Decisões e o que cada uma custa

| Decisão | O que ganhamos | O que perdemos ou o risco |
|---------|----------------|---------------------------|
| **Usar o bairro do CEP no lugar do digitado**, quando o ViaCEP responde | O bairro vem de uma fonte oficial. | Se o bairro digitado estava correto, ou era mais específico, ele é substituído, e o sistema não registra que houve diferença. É o caso de 4 clientes. |
| **Padronizar o bairro digitado por palavras-chave** (Águas Claras, Guará, Taguatinga e Vicente Pires) | Grafias como "AGUAS CLARAS" e "Vte Pires" viram um nome só, sem depender de internet. | Só cobre as quatro regiões; outros bairros ficam como foram digitados. |
| **Manter o bairro digitado quando o CEP não ajuda** (sem CEP, CEP inválido ou serviço fora do ar) | Nenhuma informação é descartada. | Erros de digitação nesses casos continuam na base. |
| **Guardar as respostas do ViaCEP no banco** | A execução é mais rápida e depende menos da internet; CEPs não reconhecidos também ficam guardados. | CEPs novos exigem internet na primeira consulta. |
| **Carga "tudo ou nada"** | Se algo der errado no meio, nada fica gravado pela metade, e repetir o processo não duplica clientes. | Um erro cancela a carga inteira. |
| **Guardar o histórico de tratamento a cada execução** | Dá para ver o que foi feito em cada campo, inclusive em execuções anteriores. | A tabela de histórico cresce a cada execução, mesmo sem mudanças nos dados. |
| **Pouca revisão manual**: só vai para revisão o cliente sem bairro | O trabalho humano é pequeno (1 cliente em 47). | Casos duvidosos, como bairro digitado diferente do bairro do CEP, passam sem revisão. |
| **Visitantes só consultam e não veem contatos** (CNPJ, telefone e e-mail) | Protege os dados de contato. | Quem precisa desses dados precisa de login. |

## 4. O que ainda não foi tratado

- **Padronização completa dos bairros.** Os nomes vindos do ViaCEP não são
  padronizados, então a mesma região pode aparecer de formas diferentes
  (por exemplo, "Sul (Águas Claras)" e "Águas Claras Sul"). Uma contagem de
  clientes por bairro ainda fica dividida.
- **Subdivisões (Norte, Sul, I, II)** ficam dentro do nome do bairro, e não em
  uma coluna separada.
- **Formato de CNPJ e telefone.** A carga automática grava o CNPJ com pontos e
  barras e o telefone com espaço; quem cadastra pela API grava só números. Os
  dois formatos podem coexistir.
- **CNPJ:** só se confere o tamanho, não os dígitos verificadores.
- **CEPs com poucos dígitos** recebem zeros à esquerda; só se confirmam quando o
  ViaCEP reconhece o CEP.

## 5. Dependência de internet

A consulta ao ViaCEP exige internet na primeira vez que cada CEP aparece. Se o
serviço estiver fora do ar, o sistema continua: o cliente fica sem o bairro do
CEP e usa o bairro digitado.

## 6. Próximos passos sugeridos

1. Decidir, como equipe, **qual bairro vence** quando o digitado e o do CEP são
   diferentes, e registrar essa divergência para consulta.
2. **Padronizar também os bairros devolvidos pelo ViaCEP**.
3. Enviar para revisão manual os casos em que o bairro digitado e o do CEP
   divergem.
4. Usar o mesmo formato de CNPJ e telefone na carga e na API.
5. Criar testes automatizados das regras de tratamento.

## 7. Decisões da equipe

| Tema | Decisão |
|------|---------|
| Qual bairro vence em caso de divergência | A preencher pela equipe |
| Nível do bairro (com ou sem subdivisão) | A preencher pela equipe |
