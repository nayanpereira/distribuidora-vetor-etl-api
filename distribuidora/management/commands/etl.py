from django.core.management.base import BaseCommand
from distribuidora.etl_service import executar_pipeline_etl, ler_arquivo_tabular


class Command(BaseCommand):
    help = 'Executa o pipeline completo de ETL a partir do CSV e carrega no PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--arquivo',
            type=str,
            default='dados/clientes_distribuidora_vetor.csv',
            help='Caminho do arquivo CSV ou Excel a ser processado.',
        )

    def handle(self, *args, **options):
        caminho = options['arquivo']
        self.stdout.write(self.style.WARNING(f'Iniciando ETL a partir de: {caminho}'))

        try:
            with open(caminho, 'rb') as arquivo:
                df = ler_arquivo_tabular(arquivo)
            self.stdout.write(f'Arquivo lido com sucesso. Total de linhas: {len(df)}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao ler arquivo: {e}'))
            return

        self.stdout.write('Executando regras de higienização, ViaCEP e carga no PostgreSQL...')
        _, resumo = executar_pipeline_etl(df, persistir=True)

        self.stdout.write(
            self.style.SUCCESS(
                f"ETL Concluído! {resumo['processados']} processados "
                f"({resumo['criados']} criados, {resumo['atualizados']} atualizados)."
            )
        )