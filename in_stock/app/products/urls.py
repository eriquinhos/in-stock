from django.urls import path

from . import views

urlpatterns = [
    # ==========================
    # PRODUTOS
    # ==========================
    # Lista de Produtos (ProductListCreateView)
    # Nome "product-list-create" é importante pois é usado no success_url das views
    path("", views.ProductListCreateView.as_view(), name="product-list-create"),
    # Edição de Produto (ProductUpdateView)
    # IMPORTANTE: Generic Views esperam <int:pk> por padrão, não <int:id_product>
    path(
        "product/<int:pk>/edit/",
        views.ProductUpdateView.as_view(),
        name="product-update",
    ),
    # Exclusão de Produto (ProductDeleteView)
    path(
        "product/<int:pk>/delete/",
        views.ProductDeleteView.as_view(),
        name="product-delete",
    ),
    # ==========================
    # CATEGORIAS
    # ==========================
    # Lista de Categorias
    path(
        "categories/",
        views.CategoryListCreateView.as_view(),
        name="category-list-create",
    ),
    # Edição de Categoria
    path(
        "categories/<int:pk>/edit/",
        views.CategoryUpdateView.as_view(),
        name="category-update",
    ),
    # Exclusão de Categoria
    path(
        "categories/<int:pk>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category-delete",
    ),
]
