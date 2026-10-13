"""Cria as duas empresas do grupo com dados provisórios.

Razão social, CNPJ e município devem ser preenchidos no admin (Núcleo > Empresas).
"""

from django.db import migrations

EMPRESAS = [
    {"sigla": "SN", "nome_fantasia": "Empresa Simples Nacional",
     "razao_social": "A preencher (Simples Nacional)", "regime_tributario": "simples"},
    {"sigla": "LP", "nome_fantasia": "Empresa Lucro Presumido",
     "razao_social": "A preencher (Lucro Presumido)", "regime_tributario": "presumido"},
]


def criar(apps, schema_editor):
    Empresa = apps.get_model("core", "Empresa")
    for dados in EMPRESAS:
        Empresa.objects.get_or_create(sigla=dados["sigla"], defaults=dados)


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]
    operations = [migrations.RunPython(criar, migrations.RunPython.noop)]
