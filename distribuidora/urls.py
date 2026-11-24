from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ClienteViewSet,
    VendedorViewSet,
    exportar_clientes_limpos,
    perfil_usuario,
    processar_planilha_etl,
    tabela_normalizacao_admin,
)


router = DefaultRouter()

router.register(
    r'clientes',
    ClienteViewSet,
    basename='cliente'
)

router.register(
    r'vendedores',
    VendedorViewSet,
    basename='vendedor'
)

urlpatterns = [
    path('auth/perfil/', perfil_usuario, name='auth-perfil'),
    path('clientes/exportar/', exportar_clientes_limpos, name='clientes-exportar'),
    path('admin-etl/tabela/', tabela_normalizacao_admin, name='admin-etl-tabela'),
    path('admin-etl/processar/', processar_planilha_etl, name='admin-etl-processar'),
    *router.urls,
]