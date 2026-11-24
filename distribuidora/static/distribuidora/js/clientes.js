import { downloadFile, endpoints, hasToken, recordPath, request } from './api.js';
import { byId, button, confirmDelete, editor, element, errorText, notice, openDialog, row } from './ui.js';

const search = byId('bairro-search');
const sellerFilter = byId('seller-filter');
const pageSize = 20;
const status = byId('clients-status');
const rows = byId('client-rows');
const retry = byId('clients-retry');
const previous = byId('previous-page');
const next = byId('next-page');
const pageLabel = byId('page-label');

export function showClient(clientId, sellerName) {
  openDialog('Detalhes do cliente', async (signal) => {
    const client = await request(recordPath(endpoints.clientes, clientId), { signal });
    const fields = [
      ['Identificador', client.id_cliente], ['Razão social', client.razao_social],
      ['Bairro', client.bairro], ['Cidade', client.cidade], ['UF', client.uf],
      ['CEP', client.cep], ['Vendedor', sellerName(client.vendedor_responsavel)],
      ['Data de cadastro', client.data_cadastro?.split('-').reverse().join('/')],
      ['Precisa de revisão', client.precisa_revisao ? 'Sim' : 'Não'],
    ];
    if (hasToken()) fields.push(['CNPJ', client.cnpj], ['Telefone', client.telefone], ['E-mail', client.email]);
    const details = element('dl', undefined, 'details');
    for (const [label, value] of fields) {
      details.append(element('dt', label), element('dd', value || '—'));
    }
    return details;
  });
}

export function setupClients(refresh) {
  let bairro = '';
  let sellerId = '';
  let page = 1;
  let sellerNames = new Map();
  const sellerName = (id) => sellerNames.get(id) ?? `Vendedor #${id}`;

  function finish(text) {
    notice(text);
    refresh('clientes');
  }

  function edit(client) {
    if (!hasToken()) return;
    const path = client ? recordPath(endpoints.clientes, client.id) : endpoints.clientes;
    openDialog(client ? 'Editar cliente' : 'Novo cliente', async (signal) => {
      const [sellers, original] = await Promise.all([
        request(endpoints.vendedores, { signal }),
        client ? request(path, { signal }) : null,
      ]);
      if (!sellers.length) throw new Error('Cadastre um vendedor na seção Vendedores antes de criar um cliente.');
      return editor('client-form-template', path, original, signal, () => {
        finish(client ? 'Cliente atualizado.' : 'Cliente cadastrado.');
      }, (form) => {
        const select = form.elements.namedItem('vendedor_responsavel');
        select.append(new Option('Selecione um vendedor', ''));
        for (const seller of sellers) select.append(new Option(seller.nome, seller.id));
      });
    });
  }

  byId('export-csv').addEventListener('click', () => {
    if (!hasToken()) return;
    downloadFile(`${endpoints.exportar}?formato=csv`, { defaultFilename: 'clientes_vetor_normalizados.csv' })
      .catch((error) => notice(errorText(error), true));
  });
  byId('export-xlsx').addEventListener('click', () => {
    if (!hasToken()) return;
    downloadFile(`${endpoints.exportar}?formato=xlsx`, { defaultFilename: 'clientes_vetor_normalizados.xlsx' })
      .catch((error) => notice(errorText(error), true));
  });
  byId('new-client').addEventListener('click', () => edit(null));
  byId('bairro-form').addEventListener('submit', (event) => {
    event.preventDefault();
    bairro = search.value.trim();
    sellerId = sellerFilter.value;
    page = 1;
    refresh('clientes');
  });
  byId('clear-bairro').addEventListener('click', () => {
    search.value = '';
    sellerFilter.value = '';
    bairro = '';
    sellerId = '';
    page = 1;
    refresh('clientes');
  });
  previous.addEventListener('click', () => {
    page -= 1;
    refresh('clientes');
  });
  next.addEventListener('click', () => {
    page += 1;
    refresh('clientes');
  });
  retry.addEventListener('click', () => refresh('clientes'));

  async function load(signal) {
    rows.replaceChildren();
    previous.disabled = next.disabled = true;
    retry.hidden = true;
    pageLabel.textContent = `Página ${page}`;
    status.textContent = 'Carregando clientes…';
    if (!sellerId && /[./]/.test(bairro)) {
      status.textContent = 'A busca por bairro não aceita pontos ou barras.';
      return;
    }

    const collection = bairro
      ? `${endpoints.clientes}bairro/${encodeURIComponent(bairro)}/`
      : endpoints.clientes;
    const path = sellerId
      ? `${recordPath(endpoints.vendedores, sellerId)}clientes/`
      : `${collection}?page=${page}`;

    try {
      const [sellers, data] = await Promise.all([
        request(endpoints.vendedores, { signal }),
        request(path, { signal }),
      ]);
      if (signal.aborted) return;
      sellerNames = new Map(sellers.map(({ id, nome }) => [id, nome]));
      const selected = sellerFilter.value || sellerId;
      sellerFilter.replaceChildren(
        new Option('Todos os vendedores', ''),
        ...sellers.map(({ id, nome }) => new Option(nome, id)),
      );
      sellerFilter.value = sellers.some(({ id }) => String(id) === selected) ? selected : '';
      sellerFilter.disabled = false;

      let result = data;
      if (sellerId) {
        const normalized = bairro.toLocaleLowerCase('pt-BR');
        const matches = bairro
          ? data.filter((client) => client.bairro?.toLocaleLowerCase('pt-BR') === normalized)
          : data;
        page = Math.min(page, Math.max(1, Math.ceil(matches.length / pageSize)));
        const start = (page - 1) * pageSize;
        result = {
          count: matches.length,
          previous: page > 1,
          next: start + pageSize < matches.length,
          results: matches.slice(start, start + pageSize),
        };
        pageLabel.textContent = `Página ${page}`;
      }
      status.textContent = result.count === 0
        ? 'Nenhum cliente encontrado.'
        : `${result.count} ${result.count === 1 ? 'cliente encontrado' : 'clientes encontrados'}`;
      previous.disabled = !result.previous;
      next.disabled = !result.next;

      for (const client of result.results) {
        const actions = [button('Visualizar', () => showClient(client.id, sellerName))];
        if (hasToken()) {
          actions.push(
            button('Editar', () => edit(client)),
            button('Excluir', () => confirmDelete(
              'Excluir cliente',
              `${client.razao_social} · ${client.id_cliente}`,
              recordPath(endpoints.clientes, client.id),
              () => finish('Cliente excluído.'),
            ), 'danger'),
          );
        }
        rows.append(row([
          client.id_cliente, client.razao_social, client.bairro || '—',
          client.cidade, client.uf, sellerName(client.vendedor_responsavel),
        ], actions));
      }
    } catch (error) {
      if (signal.aborted) return;
      if (error.status === 404 && sellerId) {
        sellerId = '';
        sellerFilter.value = '';
        page = 1;
        return load(signal);
      }
      if (error.status === 404 && page > 1) {
        page = 1;
        return load(signal);
      }
      status.textContent = errorText(error);
      retry.hidden = false;
    }
  }

  return load;
}