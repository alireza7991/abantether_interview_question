from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/wlt/", include("wallet.urls")),
    path("api/v1/exc/", include("exchange.urls")),
]
