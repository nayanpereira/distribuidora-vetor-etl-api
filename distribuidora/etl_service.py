import re
import time
import unicodedata
import pandas as pd
import requests
from django.db import transaction
from .models import Auditoria, CepCache, Cliente, Vendedor


def normalizar_cep_auditoria(valor):
    if pd.isna(valor) or str(valor).strip() == '':
        return None, 'Já era Nulo original'
    apenas_numeros = re.sub(r'\D', '', str(valor))
    if len(apenas_numeros) == 0:
        return None, 'Inválido: Sem caracteres numéricos'
    if len(apenas_numeros) > 8:
        return None, f'Inválido: Excesso de dígitos ({len(apenas_numeros)})'
    cep_formatado = apenas_numeros.zfill(8)
    if cep_formatado == '00000000':
        return None, 'Inválido: Preenchimento genérico (00000000)'
    if len(apenas_numeros) < 8:
        return cep_formatado, 'Válido: Higienizado e zeros à esquerda restaurados'
    return cep_formatado, 'Válido: Higienizado (tamanho original correto)'


def normalizar_bairro_auditoria(valor):
    if pd.isna(valor) or str(valor).strip() == '':
        return None, 'Já era Nulo ou Vazio'
    texto_original = str(valor).strip()
    texto_upper = texto_original.upper()
    bairro_padrao = None

    if 'PIRES' in texto_upper:
        bairro_padrao = 'Vicente Pires'
    elif 'AGUAS' in texto_upper or 'ÁGUAS' in texto_upper:
        if 'NORTE' in texto_upper:
            bairro_padrao = 'Águas Claras Norte'
        elif 'SUL' in texto_upper:
            bairro_padrao = 'Águas Claras Sul'
        else:
            bairro_padrao = 'Águas Claras'
    elif 'GUARA' in texto_upper or 'GUARÁ' in texto_upper:
        if 'II' in texto_upper:
            bairro_padrao = 'Guará II'
        elif 'I' in texto_upper:
            bairro_padrao = 'Guará I'
        else:
            bairro_padrao = 'Guará'
    elif 'TAGUATINGA' in texto_upper:
        if 'SUL' in texto_upper:
            bairro_padrao = 'Taguatinga Sul'
        else:
            bairro_padrao = 'Taguatinga'

    if bairro_padrao is None:
        return texto_original, 'Sem regra: Original mantido'
    if texto_original == bairro_padrao:
        return bairro_padrao, 'Válido: Já no padrão'
    return bairro_padrao, f'Canonizado: De "{texto_original}" para "{bairro_padrao}"'


def normalizar_cnpj_auditoria(valor):
    if pd.isna(valor) or str(valor).strip() == '':
        return None, 'Nulo ou Vazio'
    numeros = re.sub(r'\D', '', str(valor))
    if len(numeros) == 14:
        return (
            f'{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}',
            'Válido: Máscara aplicada',
        )
    return str(valor).strip(), f'Inválido: {len(numeros)} dígitos numéricos'


def normalizar_telefone_auditoria(valor):
    if pd.isna(valor) or str(valor).strip() == '':
        return None, 'Nulo ou Vazio'
    numeros = re.sub(r'\D', '', str(valor))
    extra = ''
    if numeros.startswith('55') and len(numeros) in (12, 13):
        numeros = numeros[2:]
        extra = ' (+55 removido)'
    if len(numeros) == 11:
        return f'{numeros[:2]} {numeros[2:7]}-{numeros[7:]}', f'Celular aplicado{extra}'
    if len(numeros) == 10:
        return f'{numeros[:2]} {numeros[2:6]}-{numeros[6:]}', f'Fixo aplicado{extra}'
    return numeros, f'Inválido: Tamanho {len(numeros)}'


def normalizar_email_auditoria(valor):
    if pd.isna(valor) or str(valor).strip() == '':
        return None, 'Nulo'
    texto_limpo = str(valor).strip().lower()
    texto_sem_acento = (
        unicodedata.normalize('NFKD', texto_limpo)
        .encode('ASCII', 'ignore')
        .decode('utf-8')
    )
    if '@' not in texto_sem_acento or '.' not in texto_sem_acento:
        return texto_sem_acento, 'Inválido: Falta @ ou ponto'
    if str(valor) != texto_sem_acento:
        return texto_sem_acento, 'Válido: Higienizado'
    return texto_sem_acento, 'Válido: Padrão correto'


def normalizar_data_auditoria(valor):
    if pd.isna(valor) or str(valor).strip() == '':
        return None, 'Nulo'
    texto = str(valor).strip()
    try:
        if re.match(r'^\d{4}-', texto):
            data = pd.to_datetime(texto)
        else:
            data = pd.to_datetime(texto, dayfirst=True)
        if pd.isna(data):
            return None, f'Inválido: "{valor}"'
        return data.date(), 'Convertido (YYYY-MM-DD)'
    except Exception:
        return None, f'Inválido: "{valor}"'


COLUNAS_OBRIGATORIAS = {
    'id_cliente',
    'razao_social',
    'cnpj',
    'telefone',
    'email',
    'cep',
    'cidade',
    'uf',
    'data_cadastro',
    'vendedor_responsavel',
}


def ler_arquivo_tabular(arquivo):
    nome = getattr(arquivo, 'name', str(arquivo)).lower()
    if nome.endswith('.xlsx') or nome.endswith('.xls'):
        df = pd.read_excel(arquivo, dtype=str, keep_default_na=False)
    elif nome.endswith('.csv'):
        # Detecta separador ';' ou ',' automaticamente
        inicio = arquivo.read(2048)
        if isinstance(inicio, bytes):
            texto_amostra = inicio.decode('utf-8-sig', errors='ignore')
        else:
            texto_amostra = inicio
        arquivo.seek(0)
        sep = ';' if texto_amostra.count(';') >= texto_amostra.count(',') else ','
        df = pd.read_csv(arquivo, sep=sep, dtype=str, keep_default_na=False)
    else:
        raise ValueError('Formato inválido. Envie um arquivo .csv ou .xlsx.')

    df.columns = [str(c).strip() for c in df.columns]
    # Aceita tanto 'bairro_informado' (CSV bruto) quanto 'bairro'
    if 'bairro_informado' not in df.columns and 'bairro' in df.columns:
        df['bairro_informado'] = df['bairro']

    faltantes = COLUNAS_OBRIGATORIAS - set(df.columns)
    if faltantes or 'bairro_informado' not in df.columns:
        raise ValueError(
            f'Colunas obrigatórias ausentes: {", ".join(sorted(faltantes | {"bairro_informado"}))}'
        )

    return df.replace(r'^\s*$', pd.NA, regex=True)


def _consultar_viacep(ceps_unicos, salvar_cache=True):
    mapa_ceps = {}
    for cep in ceps_unicos:
        existente = CepCache.objects.filter(cep=cep).first()
        if existente and (not existente.valido or existente.bairro):
            mapa_ceps[cep] = {'bairro': existente.bairro, 'valido': existente.valido}
            continue

        try:
            resp = requests.get(f'https://viacep.com.br/ws/{cep}/json/', timeout=5)
            if resp.status_code == 200:
                dados = resp.json()
                if dados.get('erro'):
                    info = {'bairro': None, 'valido': False}
                else:
                    info = {'bairro': dados.get('bairro', '').strip() or None, 'valido': True}
                mapa_ceps[cep] = info
                if salvar_cache:
                    CepCache.objects.update_or_create(cep=cep, defaults=info)
            time.sleep(0.1)
        except requests.RequestException:
            pass
    return mapa_ceps


def executar_pipeline_etl(df, persistir=True):
    df = df.copy()
    df[['cep_limpo', 'auditoria_cep']] = df['cep'].apply(
        lambda x: pd.Series(normalizar_cep_auditoria(x))
    )

    ceps_unicos = df['cep_limpo'].dropna().unique()
    mapa_ceps = _consultar_viacep(ceps_unicos, salvar_cache=persistir)

    linhas_limpas = []
    registros_processamento = []

    for _, row in df.iterrows():
        nome_vend = (
            str(row['vendedor_responsavel']).strip()
            if pd.notna(row['vendedor_responsavel'])
            else 'Vendedor Desconhecido'
        )
        cep_final = row['cep_limpo'] if pd.notna(row['cep_limpo']) else None
        auditoria_cep = row['auditoria_cep']
        bairro_viacep = None

        if cep_final and cep_final in mapa_ceps:
            info_cep = mapa_ceps[cep_final]
            if not info_cep['valido']:
                cep_final = None
                auditoria_cep = 'Inválido: Reprovado no ViaCEP'
            elif info_cep['bairro']:
                bairro_viacep = info_cep['bairro']

        if bairro_viacep:
            bairro_final = bairro_viacep
            auditoria_bairro = 'Válido: Trazido do ViaCEP'
        else:
            bairro_final, auditoria_bairro = normalizar_bairro_auditoria(row['bairro_informado'])

        cnpj_final, auditoria_cnpj = normalizar_cnpj_auditoria(row['cnpj'])
        telefone_final, auditoria_telefone = normalizar_telefone_auditoria(row['telefone'])
        email_final, auditoria_email = normalizar_email_auditoria(row['email'])
        data_final, auditoria_data = normalizar_data_auditoria(row['data_cadastro'])

        dados_finais = {
            'id_cliente': str(row['id_cliente']).strip(),
            'razao_social': str(row['razao_social']).strip(),
            'cnpj': cnpj_final,
            'telefone': telefone_final,
            'email': email_final,
            'bairro': bairro_final,
            'cep': cep_final,
            'cidade': str(row['cidade']).strip(),
            'uf': str(row['uf']).strip().upper(),
            'data_cadastro': str(data_final) if data_final else None,
            'vendedor_responsavel': nome_vend,
        }
        linhas_limpas.append(dados_finais)

        auditorias = [
            ('cep', row['cep'], cep_final, auditoria_cep),
            ('bairro', row['bairro_informado'], bairro_final, auditoria_bairro),
            ('cnpj', row['cnpj'], cnpj_final, auditoria_cnpj),
            ('telefone', row['telefone'], telefone_final, auditoria_telefone),
            ('email', row['email'], email_final, auditoria_email),
            (
                'data_cadastro',
                row['data_cadastro'],
                str(data_final) if data_final else None,
                auditoria_data,
            ),
        ]
        registros_processamento.append((dados_finais, data_final, auditorias))

    resumo = {'processados': len(linhas_limpas), 'criados': 0, 'atualizados': 0}

    if persistir:
        with transaction.atomic():
            for dados_finais, data_obj, auditorias in registros_processamento:
                vendedor, _ = Vendedor.objects.get_or_create(
                    nome=dados_finais['vendedor_responsavel']
                )
                cliente, criado = Cliente.objects.update_or_create(
                    id_cliente=dados_finais['id_cliente'],
                    defaults={
                        'razao_social': dados_finais['razao_social'],
                        'cnpj': dados_finais['cnpj'],
                        'telefone': dados_finais['telefone'],
                        'email': dados_finais['email'],
                        'bairro': dados_finais['bairro'],
                        'cep': dados_finais['cep'],
                        'cidade': dados_finais['cidade'],
                        'uf': dados_finais['uf'],
                        'data_cadastro': data_obj,
                        'vendedor_responsavel': vendedor,
                        'precisa_revisao': dados_finais['bairro'] is None,
                    },
                )
                if criado:
                    resumo['criados'] += 1
                else:
                    resumo['atualizados'] += 1

                # Adiciona ao histórico de auditoria sem apagar registros anteriores
                for campo, orig, trat, crit in auditorias:
                    Auditoria.objects.create(
                        cliente=cliente,
                        campo=campo,
                        valor_original=str(orig) if pd.notna(orig) else None,
                        valor_tratado=str(trat) if trat is not None else None,
                        criterio=crit,
                    )

    df_resultado = pd.DataFrame(linhas_limpas)
    return df_resultado, resumo