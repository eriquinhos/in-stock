from django.shortcuts import redirect, render
from django.views import View

# Removemos imports de Services, Forms e Mixins pois não serão usados agora


class ProductListCreateView(View):
    def get(self, request):
        # Apenas renderiza a tabela de produtos
        return render(request, "pages/GestaoProdutos.html")

    def post(self, request):
        # Se tentar criar, apenas recarrega a página ou redireciona
        return redirect("product-list-create")


class ProductUpdateView(View):
    def get(self, request, id_product):
        # Recebe o id_product da URL, mas ignora e só abre o HTML de edição
        return render(request, "products/edit.html")

    def post(self, request, id_product):
        # Simula o salvamento e volta para a lista
        return redirect("product-list-create")


class ProductDeleteView(View):
    def get(self, request, id_product):
        # Se acessar via GET, mostra uma confirmação (se tiver) ou volta pra lista
        return render(request, "products/product_confirm_delete.html")

    def post(self, request, id_product):
        # Simula a exclusão e volta para a lista
        return redirect("product-list-create")


# ==========================
# CATEGORIAS (Mesma lógica)
# ==========================


class CategoryListCreateView(View):
    def get(self, request):
        return render(request, "products/categories/index.html")

    def post(self, request):
        return redirect("category-list-create")


class CategoryUpdateView(View):
    def get(self, request, id_category):
        return render(request, "products/categories/edit.html")

    def post(self, request, id_category):
        return redirect("category-list-create")


class CategoryDeleteView(View):
    def post(self, request, id_category):
        return redirect("category-list-create")
