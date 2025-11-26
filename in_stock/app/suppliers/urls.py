from django.urls import path

from . import views

urlpatterns = [
    # Lista todos os fornecedores (GET) e cria um novo fornecedor (POST)
    path("", views.SupplierListCreateView.as_view(), name="supplier-list-create"),
    # Recupera um fornecedor específico (GET), atualiza (PUT/PATCH) ou deleta (DELETE)
    path(
        "<int:id_supplier>/", views.SupplierDetailView.as_view(), name="supplier-detail"
    ),
    path(
        "<int:id_supplier>/delete/",
        views.SupplierDeleteView.as_view(),
        name="supplier-delete",
    ),
]
