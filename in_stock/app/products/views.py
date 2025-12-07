from django.views.generic import ListView

from .models import Product


class ProductListView(ListView):
    model = Product
    # A LINHA MÁGICA É ESTA AQUI EMBAIXO:
    template_name = (
        "pages/GestaoProdutos.html"  # Use o nome exato do arquivo que você salvou
    )
    context_object_name = "products"
