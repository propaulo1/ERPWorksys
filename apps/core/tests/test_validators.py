from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from apps.core.validators import cnpj_valido, formatar_cnpj, validar_cnpj


class CnpjTests(SimpleTestCase):
    def test_cnpj_valido_com_e_sem_mascara(self):
        self.assertTrue(cnpj_valido("11.222.333/0001-81"))
        self.assertTrue(cnpj_valido("11222333000181"))

    def test_cnpj_invalido(self):
        self.assertFalse(cnpj_valido("11.222.333/0001-80"))
        self.assertFalse(cnpj_valido("00000000000000"))
        self.assertFalse(cnpj_valido("123"))

    def test_validador_aceita_vazio(self):
        validar_cnpj("")
        with self.assertRaises(ValidationError):
            validar_cnpj("11222333000180")

    def test_formatar(self):
        self.assertEqual(formatar_cnpj("11222333000181"), "11.222.333/0001-81")
