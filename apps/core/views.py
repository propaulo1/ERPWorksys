from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from . import empresa_ativa
from .modulos import MODULOS


@login_required
def painel(request):
    return render(request, "core/painel.html", {"modulos": MODULOS})


@require_POST
@login_required
def selecionar_empresa(request):
    if not empresa_ativa.definir(request, request.POST.get("empresa", "")):
        messages.error(request, "Você não tem acesso a essa empresa.")
    destino = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(
        destino, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        destino = "core:painel"
    return redirect(destino)
