"""Empresa em que o usuário está trabalhando, guardada na sessão.

O valor pode ser o id de uma empresa ou CONSOLIDADO (visão das empresas
a que o usuário tem acesso juntas), permitido só para quem acessa mais de uma.
"""

from .models import Empresa

SESSION_KEY = "empresa_ativa"
CONSOLIDADO = "consolidado"


def empresas_do_usuario(user):
    if not user.is_authenticated:
        return Empresa.objects.none()
    qs = Empresa.objects.filter(ativa=True)
    if user.acessa_todas_empresas:
        return qs
    return qs.filter(usuarios=user)


def resolver(request):
    """Retorna (empresas_disponiveis, empresa_ativa, consolidado)."""
    empresas = list(empresas_do_usuario(request.user))
    escolha = request.session.get(SESSION_KEY)
    if escolha == CONSOLIDADO and len(empresas) > 1:
        return empresas, None, True
    for empresa in empresas:
        if str(empresa.pk) == str(escolha):
            return empresas, empresa, False
    return empresas, (empresas[0] if empresas else None), False


def definir(request, valor):
    """Grava a escolha na sessão. Retorna False se o usuário não puder usá-la."""
    empresas = list(empresas_do_usuario(request.user))
    if valor == CONSOLIDADO:
        if len(empresas) < 2:
            return False
    elif str(valor) not in {str(e.pk) for e in empresas}:
        return False
    request.session[SESSION_KEY] = valor
    return True
