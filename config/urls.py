from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "ERP Worksys — Administração"
admin.site.site_title = "ERP Worksys"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("conta/", include("apps.accounts.urls")),
    path("", include("apps.core.urls")),
]
