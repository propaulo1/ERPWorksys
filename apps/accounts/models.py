from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Perfil(models.TextChoices):
        ADMINISTRADOR = "admin", "Administrador"
        DIRETORIA = "diretoria", "Diretoria"
        FINANCEIRO = "financeiro", "Financeiro"
        COMERCIAL = "comercial", "Comercial / Pré-vendas"
        ENGENHARIA = "engenharia", "Engenharia / Projetos"
        ALMOXARIFADO = "almoxarifado", "Almoxarifado"
        SUPORTE = "suporte", "Suporte técnico"
        TECNICO = "tecnico", "Técnico de campo"

    perfil = models.CharField(max_length=20, choices=Perfil.choices, default=Perfil.TECNICO)
    empresas = models.ManyToManyField(
        "core.Empresa",
        blank=True,
        related_name="usuarios",
        help_text="Empresas cujos dados o usuário pode ver. Administradores e diretoria veem todas.",
    )
    telefone = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "usuário"
        ordering = ["first_name", "last_name", "username"]

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def acessa_todas_empresas(self):
        return self.is_superuser or self.perfil in {self.Perfil.ADMINISTRADOR, self.Perfil.DIRETORIA}
