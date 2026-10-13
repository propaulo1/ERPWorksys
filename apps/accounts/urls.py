from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

app_name = "accounts"

urlpatterns = [
    path("entrar/", auth_views.LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "senha/",
        auth_views.PasswordChangeView.as_view(success_url=reverse_lazy("accounts:senha_alterada")),
        name="senha",
    ),
    path("senha/alterada/", auth_views.PasswordChangeDoneView.as_view(), name="senha_alterada"),
]
