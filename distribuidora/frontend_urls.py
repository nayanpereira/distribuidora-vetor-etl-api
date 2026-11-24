from django.urls import path
from django.views.generic import RedirectView, TemplateView

app_name = 'frontend'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='frontend:login'), name='inicio'),
    path('clientes/', TemplateView.as_view(template_name='distribuidora/base.html'), name='clientes'),
    path('vendedores/', TemplateView.as_view(template_name='distribuidora/base.html'), name='vendedores'),
    path('relatorios/', TemplateView.as_view(template_name='distribuidora/base.html'), name='relatorios'),
    path('normalizacao/', TemplateView.as_view(template_name='distribuidora/base.html'), name='normalizacao'),
    path('entrar/', TemplateView.as_view(template_name='distribuidora/base.html'), name='login'),
]