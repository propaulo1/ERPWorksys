from django.db import models
from django.db.models import Q

from .validators import formatar_cnpj, somente_digitos, validar_cnpj


class Empresa(models.Model):
    """Empresa do grupo. Todo documento financeiro/operacional pertence a uma empresa."""

    class Regime(models.TextChoices):
        SIMPLES = "simples", "Simples Nacional"
        PRESUMIDO = "presumido", "Lucro Presumido"
        REAL = "real", "Lucro Real"

    razao_social = models.CharField("razão social", max_length=150)
    nome_fantasia = models.CharField("nome fantasia", max_length=80)
    sigla = models.CharField(
        max_length=12, help_text="Abreviação exibida no seletor de empresa e nos relatórios."
    )
    cnpj = models.CharField("CNPJ", max_length=18, blank=True, validators=[validar_cnpj])
    inscricao_municipal = models.CharField("inscrição municipal", max_length=30, blank=True)
    regime_tributario = models.CharField(
        "regime tributário", max_length=12, choices=Regime.choices
    )
    municipio = models.CharField("município", max_length=80, blank=True)
    uf = models.CharField("UF", max_length=2, blank=True)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "empresa"
        ordering = ["nome_fantasia"]
        constraints = [
            models.UniqueConstraint(
                fields=["cnpj"], condition=~Q(cnpj=""), name="empresa_cnpj_unico"
            ),
            models.UniqueConstraint(fields=["sigla"], name="empresa_sigla_unica"),
        ]

    def __str__(self):
        return self.nome_fantasia

    def _normalizar(self):
        self.cnpj = somente_digitos(self.cnpj)
        self.uf = (self.uf or "").upper()

    def clean(self):
        # Antes das verificações de unicidade, para comparar CNPJs sem máscara.
        self._normalizar()

    def save(self, *args, **kwargs):
        self._normalizar()
        super().save(*args, **kwargs)

    @property
    def cnpj_formatado(self):
        return formatar_cnpj(self.cnpj)
