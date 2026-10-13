from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.painel, name="painel"),
    path("empresa/selecionar/", views.selecionar_empresa, name="selecionar_empresa"),
]
