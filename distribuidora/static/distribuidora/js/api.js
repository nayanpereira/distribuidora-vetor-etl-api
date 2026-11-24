const main = document.querySelector('main');

export const endpoints = {
  clientes: main.dataset.clientesUrl,
  vendedores: main.dataset.vendedoresUrl,
  token: main.dataset.tokenUrl,
  perfil: main.dataset.perfilUrl,
  exportar: main.dataset.exportarUrl,
  etlTabela: main.dataset.etlTabelaUrl,
  etlProcessar: main.dataset.etlProcessarUrl,
};

let token = null;
let isStaff = false;

export const hasToken = () => Boolean(token);
export const hasAdmin = () => Boolean(token && isStaff);

export function setToken(value) {
  token = value;
  if (!value) isStaff = false;
}

export function setStaff(value) {
  isStaff = Boolean(value);
}

function buildApiError(status, payload) {
  const messages = {
    400: 'Confira os dados informados.',
    401: 'Entre para continuar.',
    403: 'Sua conta não tem permissão para esta operação.',
    404: 'Registro ou página não encontrada.',
    409: 'O registro possui vínculos que impedem esta operação.',
  };
  const error = new Error(messages[status] ?? 'O servidor não concluiu a operação.');
  error.status = status;
  if (status < 500 && payload && typeof payload === 'object') error.payload = payload;
  return error;
}

export async function request(path, { method = 'GET', data, signal } = {}) {
  const url = new URL(path, location.origin);
  if (url.origin !== location.origin) throw new Error('Endereço da API inválido.');

  const headers = { Accept: 'application/json' };
  const activeToken = url.pathname === endpoints.token ? null : token;
  if (activeToken) headers.Authorization = `Token ${activeToken}`;
  if (data !== undefined) headers['Content-Type'] = 'application/json';

  let response;
  try {
    response = await fetch(url, {
      method, headers, signal, credentials: 'omit', cache: 'no-store',
      body: data === undefined ? undefined : JSON.stringify(data),
    });
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new Error('Falha de conexão. Verifique o servidor e tente novamente.');
  }

  if (response.status === 204) return null;
  const payload = await response.json().catch(() => null);
  if (response.ok && payload !== null) return payload;

  if (response.status === 401 && activeToken && activeToken === token && !signal?.aborted) {
    window.dispatchEvent(new Event('vetor:session-expired'));
  }

  throw buildApiError(response.status, payload);
}

export async function uploadFormData(path, formData, { signal } = {}) {
  const url = new URL(path, location.origin);
  if (url.origin !== location.origin) throw new Error('Endereço da API inválido.');

  const headers = { Accept: 'application/json' };
  const activeToken = token;
  if (activeToken) headers.Authorization = `Token ${activeToken}`;

  let response;
  try {
    response = await fetch(url, {
      method: 'POST', headers, signal, credentials: 'omit', cache: 'no-store', body: formData,
    });
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new Error('Falha de conexão. Verifique o servidor e tente novamente.');
  }

  const payload = await response.json().catch(() => null);
  if (response.ok && payload !== null) return payload;

  if (response.status === 401 && activeToken && activeToken === token && !signal?.aborted) {
    window.dispatchEvent(new Event('vetor:session-expired'));
  }

  throw buildApiError(response.status, payload);
}

export async function downloadFile(path, { method = 'GET', body, defaultFilename = 'exportacao.xlsx', signal } = {}) {
  const url = new URL(path, location.origin);
  if (url.origin !== location.origin) throw new Error('Endereço da API inválido.');

  const headers = {};
  const activeToken = token;
  if (activeToken) headers.Authorization = `Token ${activeToken}`;

  let response;
  try {
    response = await fetch(url, {
      method, headers, body, signal, credentials: 'omit', cache: 'no-store',
    });
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new Error('Falha de conexão. Verifique o servidor e tente novamente.');
  }

  if (!response.ok) {
    if (response.status === 401 && activeToken && activeToken === token && !signal?.aborted) {
      window.dispatchEvent(new Event('vetor:session-expired'));
    }
    const payload = await response.json().catch(() => null);
    throw buildApiError(response.status, payload);
  }

  const blob = await response.blob();
  const disposition = response.headers.get('Content-Disposition') || '';
  const match = disposition.match(/filename="?([^"]+)"?/);
  const filename = match ? match[1] : defaultFilename;

  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(link.href);
}

export const recordPath = (collection, id) => `${collection}${encodeURIComponent(id)}/`;