from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Lista todos os produtos (GET) e cria um novo produto (POST)
    path("", views.ProductListCreateView.as_view(), name="product-list-create"),
    # Usa uma Template Genérica para uma página estática
    path(
        "create/",
        TemplateView.as_view(template_name="product/create.html"),
        name="product-create",
    ),
    # Recupera um produto específico (GET), atualiza (PUT/PATCH)
    path("<int:id_product>/", views.ProductUpdateView.as_view(), name="product-update"),
    path(
        "<int:id_product>/delete/",
        views.ProductDeleteView.as_view(),
        name="product-delete",
    ),
    # Lista todos os categorias (GET) e cria um novo categoria (POST)
    path(
        "categories/",
        views.CategoryListCreateView.as_view(),
        name="category-list-create",
    ),
    # Usa uma Template Genérica para uma página estática
    path(
        "create/",
        TemplateView.as_view(template_name="products/create.html"),
        name="product-create",
    ),
    path(
        "categories/<int:id_category>/delete",
        views.CategoryDeleteView.as_view(),
        name="category-delete",
    ),
    # Recupera um categoria específico (GET), atualiza (PUT/PATCH)
    path(
        "categories/<int:id_category>/",
        views.CategoryUpdateView.as_view(),
        name="category-update",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
