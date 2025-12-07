from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

# Importe seus modelos aqui. 
# Se os nomes forem diferentes no seu models.py, ajuste aqui.
from .models import Product, Category
from .forms import ProductForm, CategoryForm # Assumindo que você tem forms criados

# ==========================
# VIEWS DE PRODUTOS
# ==========================

class ProductListCreateView(ListView):
    """
    Exibe a lista de produtos.
    Aqui é onde definimos que o template será 'pages/GestaoProdutos.html'
    """
    model = Product
    template_name = "pages/GestaoProdutos.html"  # <--- O PULO DO GATO AQUI
    context_object_name = "products"  # Como você vai chamar a lista no HTML (ex: {% for p in products %})
    paginate_by = 10 # Opcional: paginação

    def get_queryset(self):
        # Aqui você pode ordenar ou filtrar se necessário
        return Product.objects.all().order_by('-id')


class ProductDeleteView(DeleteView):
    model = Product
    template_name = "products/product_confirm_delete.html" # Django pede confirmação padrão
    success_url = reverse_lazy('product-list-create')

# ==========================
# VIEWS DE CATEGORIAS
# ==========================

class CategoryListCreateView(ListView):
    model = Category
    template_name = "products/categories_list.html" # Ajuste para o seu template de categorias
    context_object_name = "categories"

class CategoryUpdateView(UpdateView):
    model = Category
    template_name = "products/category_form.html"
    fields = ['name', 'description']
    success_url = reverse_lazy('category-list-create')

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = "products/category_confirm_delete.html"
    success_url = reverse_lazy('category-list-create')