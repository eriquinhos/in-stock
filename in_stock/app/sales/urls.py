from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    # Lista todos os retiradas/entradas (GET) e cria um novo retirada/entrada (POST)
    path("", views.SaleListCreateView.as_view(), name="sale-list-create"),
    # Usa uma Template Genérica para uma página estática
    path(
        "create/",
        TemplateView.as_view(template_name="sales/create.html"),
        name="sale-create",
    ),
]
