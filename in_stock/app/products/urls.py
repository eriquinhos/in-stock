from django.urls import path

from . import views

urlpatterns = [
    # O 'name' aqui deve ser igual ao que está no {% url %}
    path("produtos/", views.minha_view_de_produtos, name="GestaoProdutos"),
]
