from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

Usuario = get_user_model()


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(
            "ana", password="senha-forte-123", first_name="Ana", perfil="financeiro"
        )

    def test_painel_exige_login(self):
        resposta = self.client.get(reverse("core:painel"))
        self.assertRedirects(resposta, f"{reverse('accounts:login')}?next=/")

    def test_login_e_painel(self):
        resposta = self.client.post(
            reverse("accounts:login"), {"username": "ana", "password": "senha-forte-123"}, follow=True
        )
        self.assertContains(resposta, "Olá, Ana")
        self.assertContains(resposta, "Financeiro")

    def test_login_invalido(self):
        resposta = self.client.post(reverse("accounts:login"), {"username": "ana", "password": "errada"})
        self.assertContains(resposta, "Usuário ou senha incorretos")

    def test_logout(self):
        self.client.force_login(self.usuario)
        self.client.post(reverse("accounts:logout"))
        resposta = self.client.get(reverse("core:painel"))
        self.assertEqual(resposta.status_code, 302)

    def test_sem_empresa_mostra_aviso(self):
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse("core:painel"))
        self.assertContains(resposta, "ainda não tem acesso a nenhuma empresa")
