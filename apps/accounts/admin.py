from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "perfil", "is_active")
    list_filter = ("perfil", "is_active", "empresas")
    filter_horizontal = ("empresas", "groups", "user_permissions")
    fieldsets = UserAdmin.fieldsets + (
        ("ERP Worksys", {"fields": ("perfil", "empresas", "telefone")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("ERP Worksys", {"fields": ("first_name", "last_name", "email", "perfil", "empresas")}),
    )
