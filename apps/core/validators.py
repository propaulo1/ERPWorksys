import re

from django.core.exceptions import ValidationError


def somente_digitos(valor):
    return re.sub(r"\D", "", valor or "")


def cnpj_valido(valor):
    """Confere os dígitos verificadores de um CNPJ numérico (14 dígitos)."""
    cnpj = somente_digitos(valor)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    def digito(base, pesos):
        resto = sum(int(d) * p for d, p in zip(base, pesos)) % 11
        return "0" if resto < 2 else str(11 - resto)

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1
    d1 = digito(cnpj[:12], pesos1)
    d2 = digito(cnpj[:12] + d1, pesos2)
    return cnpj[12:] == d1 + d2


def validar_cnpj(valor):
    if valor and not cnpj_valido(valor):
        raise ValidationError("CNPJ inválido.")


def formatar_cnpj(valor):
    cnpj = somente_digitos(valor)
    if len(cnpj) != 14:
        return valor or ""
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
