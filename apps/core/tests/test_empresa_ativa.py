from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.core.empresa_ativa import CONSOLIDADO, SESSION_KEY
from apps.core.models import Empresa

Usuario = get_user_model()


class EmpresaAtivaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # As duas empresas vêm da migração de dados inicial.
        cls.sn = Empresa.objects.get(sigla="SN")
        cls.lp = Empresa.objects.get(sigla="LP")
        cls.tecnico = Usuario.objects.create_user("tecnico", password="senha-forte-123", perfil="tecnico")
        cls.tecnico.empresas.add(cls.lp)
        cls.diretor = Usuario.objects.create_user("diretor", password="senha-forte-123", perfil="diretoria")

    def selecionar(self, valor):
        return self.client.post(reverse("core:selecionar_empresa"), {"empresa": valor, "next": "/"})

    def test_empresas_iniciais_criadas(self):
        self.assertEqual(self.sn.regime_tributario, Empresa.Regime.SIMPLES)
        self.assertEqual(self.lp.regime_tributario, Empresa.Regime.PRESUMIDO)

    def test_usuario_ve_so_suas_empresas(self):
        self.client.force_login(self.tecnico)
        resposta = self.client.get(reverse("core:painel"))
        self.assertEqual(resposta.context["empresas_disponiveis"], [self.lp])
        self.assertEqual(resposta.context["empresa_ativa"], self.lp)
        self.assertNotContains(resposta, "Consolidado")

    def test_usuario_nao_seleciona_empresa_sem_acesso(self):
        self.client.force_login(self.tecnico)
        self.selecionar(self.sn.pk)
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.selecionar(CONSOLIDADO)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_diretoria_ve_todas_e_consolidado(self):
        self.client.force_login(self.diretor)
        self.selecionar(self.sn.pk)
        resposta = self.client.get(reverse("core:painel"))
        self.assertEqual(resposta.context["empresa_ativa"], self.sn)
        self.assertContains(resposta, "Consolidado")

        self.selecionar(CONSOLIDADO)
        resposta = self.client.get(reverse("core:painel"))
        self.assertIsNone(resposta.context["empresa_ativa"])
        self.assertTrue(resposta.context["consolidado"])

    def test_redirecionamento_externo_bloqueado(self):
        self.client.force_login(self.diretor)
        resposta = self.client.post(
            reverse("core:selecionar_empresa"), {"empresa": self.sn.pk, "next": "https://exemplo.com/"}
        )
        self.assertRedirects(resposta, reverse("core:painel"), fetch_redirect_response=False)

    def test_cnpj_unico_quando_preenchido(self):
        self.sn.cnpj = "11.222.333/0001-81"
        self.sn.full_clean()
        self.sn.save()
        self.assertEqual(self.sn.cnpj, "11222333000181")
        self.lp.cnpj = "11222333000181"
        with self.assertRaises(Exception):
            self.lp.full_clean()
