from django.urls import path

from . import views

urlpatterns = [
    # Lista todos os fornecedores (GET)
    path("", views.SupplierListCreateView.as_view(), name="supplier-list-create"),
    # Formulário de criação (GET) e criar fornecedor (POST)
    path("create/", views.SupplierCreateView.as_view(), name="supplier-create"),
    # Editar fornecedor (GET/POST)
    path(
        "<int:id_supplier>/", views.SupplierDetailView.as_view(), name="supplier-detail"
    ),
    # Deletar fornecedor (POST)
    path(
        "<int:id_supplier>/delete/",
        views.SupplierDeleteView.as_view(),
        name="supplier-delete",
    ),
]
