import { endpoints, request, setStaff, setToken } from './api.js';
import { byId, disableButton, errorText, formData, message } from './ui.js';

export function setupAuth(onLogin, onLogout) {
  const form = byId('login-form');
  const feedback = byId('login-error');
  const submit = form.querySelector('button[type=submit]');
  let pending;
  let username = '';

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (submit.disabled) return;
    const credentials = formData(form);
    credentials.password = form.elements.password.value;
    const controller = new AbortController();
    pending = controller;
    message(feedback, '');
    const restore = disableButton(submit, 'Entrando…');
    try {
      const result = await request(endpoints.token, {
        method: 'POST', data: credentials, signal: controller.signal,
      });
      if (controller.signal.aborted) return;
      if (typeof result.token !== 'string' || !result.token) throw new Error('Resposta de login inválida.');
      setToken(result.token);
      const perfil = await request(endpoints.perfil, { signal: controller.signal });
      if (controller.signal.aborted) return;
      setStaff(perfil.is_staff || perfil.is_superuser);
      username = perfil.username || credentials.username;
      onLogin();
    } catch (error) {
      setToken(null);
      if (!controller.signal.aborted) {
        message(feedback, [400, 401].includes(error.status)
          ? 'Usuário ou senha inválidos.'
          : errorText(error));
      }
    } finally {
      form.elements.password.value = '';
      if (pending === controller) pending = undefined;
      restore();
    }
  });

  function logout(expired) {
    setToken(null);
    username = '';
    onLogout(expired);
  }

  byId('logout').addEventListener('click', () => logout(false));
  window.addEventListener('vetor:session-expired', () => logout(true));

  return {
    username: () => username,
    clearLogin() {
      pending?.abort();
      form.reset();
      message(feedback, '');
    },
  };
}