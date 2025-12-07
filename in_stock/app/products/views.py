from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView  # Adicionei DeleteView

from .models import Category, Product  # Adicionei Category


# Sua View de Listagem (Essa mostra o HTML bonito)
class ProductListView(ListView):
    model = Product
    template_name = "pages/GestaoProdutos.html"
    context_object_name = "products"


# --- A PEÇA QUE FALTAVA ---
# Sem essa classe abaixo, o servidor dá erro e não atualiza seu HTML
class CategoryDeleteView(DeleteView):
    model = Category
    # O Django vai procurar um template simples para confirmar a exclusão
    template_name = "products/category_confirm_delete.html"
    # Para onde vai depois de deletar? Para a lista de categorias
    success_url = reverse_lazy("category-list-create")
