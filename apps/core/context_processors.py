from .empresa_ativa import CONSOLIDADO
from .modulos import MODULOS


def empresa(request):
    if not hasattr(request, "empresas_disponiveis"):
        return {}
    return {
        "empresas_disponiveis": request.empresas_disponiveis,
        "empresa_ativa": request.empresa,
        "consolidado": request.consolidado,
        "CONSOLIDADO": CONSOLIDADO,
        "menu_modulos": MODULOS,
    }
