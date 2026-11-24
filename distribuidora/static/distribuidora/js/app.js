import { hasAdmin, hasToken } from './api.js';
import { setupAuth } from './auth.js';
import { setupClients } from './clientes.js';
import { setupNormalization } from './normalizacao.js';
import { setupReports } from './relatorios.js';
import { setupSellers } from './vendedores.js';
import { byId, closeDialog, notice } from './ui.js';

let activeSection;
let activeRead;
let loginReturn = 'clientes';
const links = [...document.querySelectorAll('a[data-nav]')];
const pages = new Map(links.map((link) => [link.dataset.nav, link.pathname]));

function refresh(section) {
  if (section !== activeSection) return;
  activeRead?.abort();
  activeRead = new AbortController();
  loaders[section]?.(activeRead.signal);
}

const loaders = {
  clientes: setupClients(refresh),
  vendedores: setupSellers(refresh),
  relatorios: setupReports(refresh),
  normalizacao: setupNormalization(refresh),
};
const auth = setupAuth(
  () => {
    navigate(loginReturn, { replace: true });
    notice('Acesso autenticado.');
  },
  (expired) => {
    closeDialog();
    navigate(activeSection, { replace: true });
    notice(expired ? 'Sessão inválida. Entre novamente para editar registros.' : 'Você saiu. Modo visitante.', expired);
  },
);

function navigate(section, { replace = false, pop = false, focus = true } = {}) {
  if (section === 'login' && hasToken()) {
    navigate('clientes', { replace: true, focus });
    return;
  }
  if (section === 'normalizacao' && !hasAdmin()) {
    navigate('clientes', { replace: true, focus });
    return;
  }
  if (section === 'login' && loaders[activeSection]) loginReturn = activeSection;
  if (activeSection === 'login' && section !== 'login') auth.clearLogin();

  closeDialog();
  notice('');
  activeSection = section;
  const path = pages.get(section);
  if (!pop && location.pathname !== path) {
    history[replace ? 'replaceState' : 'pushState'](null, '', path);
  }

  for (const page of pages.keys()) byId(page).hidden = page !== section;
  for (const link of links) {
    if (link.dataset.nav === section) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  }

  const isLogin = section === 'login';
  byId('sidebar').hidden = isLogin;
  document.querySelector('.layout').classList.toggle('login-layout', isLogin);

  const authenticated = hasToken();
  const admin = hasAdmin();
  byId('session-status').textContent = authenticated ? auth.username() : 'Visitante';
  byId('login-link').hidden = authenticated || section === 'login';
  byId('logout').hidden = !authenticated;
  byId('nav-normalizacao').hidden = !admin;
  byId('export-csv').hidden = !authenticated;
  byId('export-xlsx').hidden = !authenticated;
  byId('new-client').hidden = !authenticated;
  byId('new-seller').hidden = !authenticated;
  document.title = `${byId(`${section}-title`).textContent} · Distribuidora Vetor`;
  refresh(section);
  if (focus) byId(`${section}-title`).focus();
}

function sectionFromLocation() {
  return [...pages].find(([, path]) => path === location.pathname)?.[0] ?? 'clientes';
}

for (const link of links) {
  link.addEventListener('click', (event) => {
    if (event.button || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    navigate(link.dataset.nav);
  });
}
window.addEventListener('popstate', () => {
  if (sectionFromLocation() !== activeSection) navigate(sectionFromLocation(), { pop: true });
});

navigate(sectionFromLocation(), { pop: true, focus: false });