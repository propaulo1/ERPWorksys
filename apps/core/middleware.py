from . import empresa_ativa


class EmpresaAtivaMiddleware:
    """Disponibiliza request.empresa (None no consolidado), request.consolidado
    e request.empresas_disponiveis para views e templates."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            empresas, empresa, consolidado = empresa_ativa.resolver(request)
        else:
            empresas, empresa, consolidado = [], None, False
        request.empresas_disponiveis = empresas
        request.empresa = empresa
        request.consolidado = consolidado
        return self.get_response(request)
