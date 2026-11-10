import pandas as pd
import re
import unicodedata
import requests
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from distribuidora.models import Cliente, Vendedor, Auditoria, CepCache

class Command(BaseCommand):
    help = 'Executa o pipeline de ETL a partir do CSV e carrega no banco de dados'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Iniciando processo de ETL..."))

        # 1. Leitura do Arquivo (E-01)
        caminho_csv = 'dados/clientes_distribuidora_vetor.csv'
        try:
            df = pd.read_csv(caminho_csv, sep=";", dtype=str, keep_default_na=False)
            df = df.replace(r'^\s*$', pd.NA, regex=True)
            self.stdout.write(f"Arquivo lido com sucesso. Total de linhas originais: {len(df)}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao ler CSV: {e}"))
            return

        # Funções de normalização (as mesmas do Jupyter)
        def limpar_cep(valor):
            if pd.isna(valor): return pd.NA, 'Já era Nulo'
            numeros = re.sub(r'\D', '', str(valor))
            if len(numeros) == 0 or len(numeros) > 8 or numeros.zfill(8) == '00000000': 
                return pd.NA, 'Inválido'
            return numeros.zfill(8), 'Válido'

        # Limpeza inicial de CEP para a API
        df[['cep_limpo', 'auditoria_cep']] = df['cep'].apply(lambda x: pd.Series(limpar_cep(x)))

        # 2. Integração ViaCEP com Cache no Banco (E-04)
        ceps_unicos = df['cep_limpo'].dropna().unique()
        self.stdout.write(f"Buscando {len(ceps_unicos)} CEPs no ViaCEP...")
        
        for cep in ceps_unicos:
            # Verifica se já está no banco de dados (Cache)
            cache, criado = CepCache.objects.get_or_create(cep=cep)
            if criado or pd.isna(cache.bairro):
                try:
                    resp = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
                    if resp.status_code == 200 and not resp.json().get('erro'):
                        cache.bairro = resp.json().get('bairro', '')
                        cache.valido = True
                    else:
                        cache.valido = False
                    cache.save()
                    time.sleep(0.1) # Respeitar a API
                except requests.RequestException:
                    cache.valido = False
                    cache.save()

        # 3. Carga Transacional e Idempotente no Banco de Dados (E-07)
        # O transaction.atomic() garante que se der erro, nada é salvo pela metade
        with transaction.atomic():
            self.stdout.write("Iniciando carga transacional no PostgreSQL...")
            
            # Limpa auditorias antigas para não duplicar no re-run (idempotência)
            Auditoria.objects.all().delete()
            
            cadastrados = 0
            
            for index, row in df.iterrows():
                # 3.1 Tratamento de Vendedor (Chave Estrangeira)
                nome_vend = str(row['vendedor_responsavel']).strip() if pd.notna(row['vendedor_responsavel']) else 'Vendedor Desconhecido'
                vendedor, _ = Vendedor.objects.get_or_create(nome=nome_vend)

                # 3.2 Define o Bairro Definitivo (ViaCEP ou Fallback)
                bairro_final = str(row['bairro_informado']).strip() if pd.notna(row['bairro_informado']) else None
                cep_final = row['cep_limpo']
                precisa_revisao = False
                
                if pd.notna(cep_final):
                    cache = CepCache.objects.filter(cep=cep_final).first()
                    if cache and cache.valido and cache.bairro:
                        bairro_final = cache.bairro # ViaCEP Vence
                
                if not bairro_final:
                    precisa_revisao = True # Marca para revisão se ficou sem bairro

                # 3.3 Cria ou Atualiza o Cliente (Idempotência pela Chave id_cliente)
                # update_or_create garante que rodar 2x não duplica (E-07)
                cliente, criado = Cliente.objects.update_or_create(
                    id_cliente=str(row['id_cliente']),
                    defaults={
                        'razao_social': str(row['razao_social']),
                        'bairro': bairro_final,
                        'cep': cep_final if pd.notna(cep_final) else None,
                        'cidade': str(row['cidade']),
                        'uf': str(row['uf']),
                        'vendedor_responsavel': vendedor,
                        'precisa_revisao': precisa_revisao
                        # Nota: CNPJ, Telefone, Email e Data omitidos por brevidade, adicione a lógica de gravação conforme a necessidade
                    }
                )
                
                # 3.4 Registra Auditoria (E-06)
                Auditoria.objects.create(
                    cliente=cliente,
                    campo='cep',
                    valor_original=row['cep'],
                    valor_tratado=cep_final,
                    criterio=row['auditoria_cep']
                )
                
                cadastrados += 1
                
        self.stdout.write(self.style.SUCCESS(f"ETL Concluído com sucesso! {cadastrados} clientes processados."))