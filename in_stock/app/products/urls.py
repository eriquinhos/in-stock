from django.urls import path

from . import views

urlpatterns = [
    # O 'name' aqui deve ser igual ao que está no {% url %}
    path("pages/GestaoProdutos.html", views.ProductListView.as_view(), name="GestaoProdutos"),
]
