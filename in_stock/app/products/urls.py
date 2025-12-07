from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    # ==========================
    # PRODUTOS
    # ==========================
    # URL: /products/ -> Chama a lista (GestaoProdutos.html)
    path("", views.ProductListCreateView.as_view(), name="product-list-create"),
    # URL: /products/create/ -> Chama o form de criação
    path(
        "create/",
        TemplateView.as_view(template_name="products/create.html"),
        name="product-create",
    ),
    # URL: /products/1/ -> Edição
    path("<int:id_product>/", views.ProductUpdateView.as_view(), name="product-update"),
    # URL: /products/1/delete/ -> Exclusão
    path(
        "<int:id_product>/delete/",
        views.ProductDeleteView.as_view(),
        name="product-delete",
    ),
    # ==========================
    # CATEGORIAS
    # ==========================
    path(
        "categories/",
        views.CategoryListCreateView.as_view(),
        name="category-list-create",
    ),
    path(
        "categories/<int:id_category>/",
        views.CategoryUpdateView.as_view(),
        name="category-update",
    ),
    path(
        "categories/<int:id_category>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category-delete",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
