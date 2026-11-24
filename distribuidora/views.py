import io
import pandas as pd
from django.db.models.deletion import RestrictedError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import serializers, viewsets
from rest_framework.decorators import action, api_view, parser_classes, permission_classes
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
    inline_serializer,
)

from .etl_service import executar_pipeline_etl, ler_arquivo_tabular
from .models import Cliente, Vendedor
from .serializers import (
    ClientePublicoSerializer,
    ClienteSerializer,
    ResumoBairroSerializer,
    VendedorSerializer,
)
from .services import clientes_por_bairro, clientes_por_vendedor, resumo_por_bairro


class VendedorComClientesError(APIException):
    status_code = 409
    default_detail = (
        'Não é possível excluir um vendedor '
        'que possui clientes vinculados.'
    )
    default_code = 'vendedor_com_clientes'


class ClientePagination(PageNumberPagination):
    page_size = 20


filtro_revisao = OpenApiParameter(
    name='precisa_revisao',
    type=bool,
    description='Filtra clientes marcados (true) ou não marcados (false) para revisão.',
)


@extend_schema_view(list=extend_schema(parameters=[filtro_revisao]))
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.order_by('pk')
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = ClientePagination

    def filtrar_revisao(self, clientes):
        valor = self.request.query_params.get('precisa_revisao')
        if valor is None:
            return clientes
        valor = valor.casefold()
        if valor not in ('true', 'false'):
            raise ValidationError({'precisa_revisao': 'Use true ou false.'})
        return clientes.filter(precisa_revisao=valor == 'true')

    def list(self, request, *args, **kwargs):
        return self.resposta_clientes(self.get_queryset())

    def resposta_clientes(self, clientes):
        clientes = self.filtrar_revisao(self.filter_queryset(clientes))
        page = self.paginate_queryset(clientes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(clientes, many=True).data)

    @extend_schema(
        parameters=[
            filtro_revisao,
            OpenApiParameter(
                name='nome',
                type=str,
                location=OpenApiParameter.PATH,
                description='Nome do bairro para filtrar os clientes.'
            )
        ],
        responses=ClienteSerializer(many=True),
    )
    @action(
        detail=False,
        methods=['get'],
        url_path=r'bairro/(?P<nome>[^/]+)'
    )
    def buscar_por_bairro(self, request, nome):
        return self.resposta_clientes(clientes_por_bairro(self.get_queryset(), nome))

    @extend_schema(
        parameters=[OpenApiParameter('id', int, OpenApiParameter.PATH), filtro_revisao],
        responses=ClienteSerializer(many=True),
    )
    @action(detail=False, methods=['get'], url_path=r'vendedor/(?P<id>[0-9]+)')
    def buscar_por_vendedor(self, request, id):
        vendedor = get_object_or_404(Vendedor, pk=id)
        return self.resposta_clientes(clientes_por_vendedor(vendedor))

    @extend_schema(responses=ResumoBairroSerializer(many=True))
    @action(detail=False, methods=['get'], url_path='bairros', pagination_class=None)
    def listar_bairros(self, request):
        resumo = resumo_por_bairro(self.get_queryset())
        return Response(self.get_serializer(resumo, many=True).data)

    def get_serializer_class(self):
        if self.action == 'listar_bairros':
            return ResumoBairroSerializer
        if getattr(self, 'swagger_fake_view', False) or self.request.user.is_authenticated:
            return ClienteSerializer
        return ClientePublicoSerializer


class VendedorViewSet(viewsets.ModelViewSet):
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(responses={
        204: None,
        409: OpenApiResponse(
            response=inline_serializer(
                name='VendedorComClientes',
                fields={'detail': serializers.CharField()},
            ),
            description='O vendedor possui clientes vinculados.',
        ),
    })
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except RestrictedError:
            raise VendedorComClientesError()

    @extend_schema(
        responses=ClienteSerializer(many=True),
        description='Lista de clientes do vendedor. CNPJ, telefone e e-mail exigem autenticação.',
    )
    @action(
        detail=True,
        methods=['get'],
        url_path='clientes'
    )
    def listar_clientes(self, request, pk=None):
        vendedor = self.get_object()

        clientes = clientes_por_vendedor(vendedor)

        serializer_class = (
            ClienteSerializer if request.user.is_authenticated else ClientePublicoSerializer
        )
        serializer = serializer_class(clientes, many=True, context=self.get_serializer_context())

        return Response(serializer.data)


def _gerar_resposta_arquivo(df, formato='xlsx', prefixo='clientes_normalizados'):
    if formato == 'csv':
        buffer = io.StringIO()
        df.to_csv(buffer, sep=';', index=False, encoding='utf-8-sig')
        response = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{prefixo}.csv"'
        return response

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados Normalizados')
    buffer.seek(0)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{prefixo}.xlsx"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil_usuario(request):
    return Response({
        'username': request.user.username,
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exportar_clientes_limpos(request):
    """Exporta somente os dados finais normalizados do banco em CSV ou Excel."""
    formato = request.query_params.get('formato', 'xlsx').lower()
    clientes = Cliente.objects.select_related('vendedor_responsavel').order_by('id_cliente')
    dados = [
        {
            'id_cliente': c.id_cliente,
            'razao_social': c.razao_social,
            'cnpj': c.cnpj or '',
            'telefone': c.telefone or '',
            'email': c.email or '',
            'bairro': c.bairro or '',
            'cep': c.cep or '',
            'cidade': c.cidade,
            'uf': c.uf,
            'data_cadastro': c.data_cadastro.isoformat() if c.data_cadastro else '',
            'vendedor_responsavel': c.vendedor_responsavel.nome,
        }
        for c in clientes
    ]
    df = pd.DataFrame(dados)
    return _gerar_resposta_arquivo(df, formato=formato, prefixo='clientes_vetor_normalizados')


@api_view(['GET'])
@permission_classes([IsAdminUser])
def tabela_normalizacao_admin(request):
    """Retorna a tabela completa de normalização (original vs tratado + critérios) apenas para admins."""
    clientes = (
        Cliente.objects.select_related('vendedor_responsavel')
        .prefetch_related('auditorias')
        .order_by('id_cliente')
    )
    resultado = []
    for c in clientes:
        ultimas = {}
        for aud in c.auditorias.all():
            if aud.campo not in ultimas or aud.id > ultimas[aud.campo].id:
                ultimas[aud.campo] = aud

        def detalhe(campo, valor_atual):
            reg = ultimas.get(campo)
            return {
                'original': reg.valor_original if reg else None,
                'tratado': valor_atual,
                'criterio': reg.criterio if reg else 'Sem registro',
            }

        resultado.append({
            'id': c.id,
            'id_cliente': c.id_cliente,
            'razao_social': c.razao_social,
            'vendedor': c.vendedor_responsavel.nome,
            'cidade': c.cidade,
            'uf': c.uf,
            'precisa_revisao': c.precisa_revisao,
            'cep': detalhe('cep', c.cep),
            'bairro': detalhe('bairro', c.bairro),
            'cnpj': detalhe('cnpj', c.cnpj),
            'telefone': detalhe('telefone', c.telefone),
            'email': detalhe('email', c.email),
            'data_cadastro': detalhe(
                'data_cadastro', c.data_cadastro.isoformat() if c.data_cadastro else None
            ),
        })

    return Response(resultado)


@api_view(['POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def processar_planilha_etl(request):
    """Recebe CSV/Excel, normaliza e salva no histórico ou apenas exporta sem gravar no banco."""
    arquivo = request.FILES.get('arquivo')
    if not arquivo:
        raise ValidationError({'arquivo': 'Envie um arquivo .csv ou .xlsx.'})

    modo = request.data.get('modo', 'salvar')
    formato_saida = request.data.get('formato_saida', 'xlsx').lower()

    try:
        df_bruto = ler_arquivo_tabular(arquivo)
    except ValueError as exc:
        raise ValidationError({'arquivo': str(exc)})

    persistir = modo == 'salvar'
    df_limpo, resumo = executar_pipeline_etl(df_bruto, persistir=persistir)

    if not persistir:
        return _gerar_resposta_arquivo(
            df_limpo, formato=formato_saida, prefixo='planilha_normalizada_avulsa'
        )

    return Response({
        'mensagem': 'Planilha normalizada e adicionada ao banco de dados com sucesso.',
        **resumo,
    })