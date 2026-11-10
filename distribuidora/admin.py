from django.contrib import admin
from .models import Vendedor, Cliente, Auditoria, CepCache

admin.site.register(Vendedor)
admin.site.register(Cliente)
admin.site.register(CepCache)

# A auditoria deve ser somente leitura conforme as regras[cite: 1, 5]
@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in Auditoria._meta.fields]
    
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False