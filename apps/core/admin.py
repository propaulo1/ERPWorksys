from django.contrib import admin

from .models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nome_fantasia", "sigla", "cnpj_formatado", "regime_tributario", "municipio", "ativa")
    list_filter = ("regime_tributario", "ativa")
    search_fields = ("razao_social", "nome_fantasia", "cnpj")

    @admin.display(description="CNPJ")
    def cnpj_formatado(self, obj):
        return obj.cnpj_formatado
