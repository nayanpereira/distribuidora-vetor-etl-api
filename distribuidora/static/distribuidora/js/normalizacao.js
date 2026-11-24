import { downloadFile, endpoints, hasAdmin, request, uploadFormData } from './api.js';
import { byId, button, closeDialog, element, errorText, notice, openDialog } from './ui.js';

function formatarCelula(campoObj) {
  if (!campoObj) return '—';
  const orig = campoObj.original ?? 'Nulo';
  const trat = campoObj.tratado ?? 'Nulo';
  const crit = campoObj.criterio ?? '';
  return `${orig} → ${trat} (${crit})`;
}

export function setupNormalization(refresh) {
  const tableStatus = byId('etl-table-status');
  const uploadStatus = byId('etl-upload-status');
  const rows = byId('etl-rows');
  const form = byId('etl-upload-form');
  const fileInput = byId('etl-file');
  const formatSelect = byId('etl-export-format');

  byId('refresh-etl').addEventListener('click', () => refresh('normalizacao'));
  byId('admin-export-csv').addEventListener('click', () => {
    if (!hasAdmin()) return;
    downloadFile(`${endpoints.exportar}?formato=csv`, { defaultFilename: 'clientes_vetor_normalizados.csv' })
      .catch((error) => notice(errorText(error), true));
  });
  byId('admin-export-xlsx').addEventListener('click', () => {
    if (!hasAdmin()) return;
    downloadFile(`${endpoints.exportar}?formato=xlsx`, { defaultFilename: 'clientes_vetor_normalizados.xlsx' })
      .catch((error) => notice(errorText(error), true));
  });

  async function executarUpload(arquivo, modo, formatoSaida) {
    closeDialog();
    uploadStatus.textContent = 'Processando regras de normalização e ViaCEP…';

    const formData = new FormData();
    formData.append('arquivo', arquivo);
    formData.append('modo', modo);
    formData.append('formato_saida', formatoSaida);

    try {
      if (modo === 'exportar') {
        await downloadFile(endpoints.etlProcessar, {
          method: 'POST',
          body: formData,
          defaultFilename: `planilha_normalizada_avulsa.${formatoSaida}`,
        });
        uploadStatus.textContent = 'Planilha normalizada e exportada sem alterar o banco de dados.';
        notice('Download da planilha normalizada iniciado.');
      } else {
        const payload = await uploadFormData(endpoints.etlProcessar, formData);
        uploadStatus.textContent =
          `Concluído: ${payload.processados} processados (${payload.criados} novos, ${payload.atualizados} atualizados no histórico).`;
        notice('Banco de dados e histórico atualizados com sucesso!');
        refresh('normalizacao');
      }
      form.reset();
    } catch (error) {
      uploadStatus.textContent = errorText(error);
      notice(errorText(error), true);
    }
  }

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!hasAdmin()) return;
    const arquivo = fileInput.files?.[0];
    if (!arquivo) return;
    const formatoSaida = formatSelect.value;

    openDialog('Como deseja processar esta planilha?', () => {
      const box = element('div');
      box.append(
        element(
          'p',
          `Arquivo selecionado: "${arquivo.name}". Escolha se deseja incorporar os registros ao banco de dados ou apenas gerar o arquivo limpo:`,
        ),
      );
      const actions = element('div', undefined, 'actions');
      actions.append(
        button(
          'Adicionar ao histórico e atualizar site',
          () => executarUpload(arquivo, 'salvar', formatoSaida),
          'primary',
        ),
        button(
          `Apenas normalizar e baixar (${formatoSaida.toUpperCase()})`,
          () => executarUpload(arquivo, 'exportar', formatoSaida),
        ),
      );
      box.append(actions);
      return box;
    });
  });

  return async (signal) => {
    if (!hasAdmin()) return;
    rows.replaceChildren();
    tableStatus.textContent = 'Carregando tabela completa de normalização…';
    try {
      const data = await request(endpoints.etlTabela, { signal });
      if (signal.aborted) return;
      tableStatus.textContent = `${data.length} registros auditados no banco de dados.`;
      for (const item of data) {
        const tr = element('tr');
        for (const val of [
          item.id_cliente,
          item.razao_social,
          formatarCelula(item.bairro),
          formatarCelula(item.cep),
          formatarCelula(item.cnpj),
          formatarCelula(item.telefone),
          formatarCelula(item.email),
          formatarCelula(item.data_cadastro),
        ]) {
          tr.append(element('td', val));
        }
        rows.append(tr);
      }
    } catch (error) {
      if (!signal.aborted) tableStatus.textContent = errorText(error);
    }
  };
}