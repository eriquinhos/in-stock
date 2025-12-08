from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import ProductExportView

urlpatterns = [
    # PRODUTOS
    path(
        "",
        views.ProductListCreateView.as_view(),
        name="product-list-create",
    ),
    path(
        "create/",
        views.ProductCreateView.as_view(),
        name="product-create",
    ),
    path(
        "<int:id_product>/",
        views.ProductUpdateView.as_view(),
        name="product-update",
    ),
    path(
        "<int:id_product>/delete/",
        views.ProductDeleteView.as_view(),
        name="product-delete",
    ),
    # CATEGORIAS
    path(
        "categories/",
        views.CategoryListView.as_view(),
        name="category-list-create",
    ),
    path(
        "categories/create/",
        views.CategoryCreateView.as_view(),
        name="category-create",
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
    path("export/", views.ProductExportView.as_view(), name="product-export"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
