from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.shortcuts import redirect, render
from django.views import View

from .forms import CategoryForm, ProductForm
from .services import CategoryService, ProductService


class ProductListCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):

    # Permissão necessária para acessar qualquer método (get ou post)
    def get_permission_required(self):
        if self.request.method == "POST":
            return ["products.add_product"]
        return ["products.view_product"]

    def get(self, request):

        # Lógica para listar todos os produtos
        products = ProductService.get_all()

        return render(request, "pages/GestaoProdutos.html", {"products": products})

    def post(self, request):

        # Lógica para criar um novo produto
        # ... processar request.POST ou request.body ...
        form = ProductForm(request.POST or None, request.FILES or None)
        if form.is_valid():

            # Terminar e testar a lógica de salvar imagem
            try:

                product_create = ProductService.create_product(request)

                messages.success("O produto foi criado com sucesso!")

            except Exception:
                messages.error("Não foi possível salvar o produto!")

        else:
            messages.error("Verifique se os dados inseridos estão corretos!")

        return render(request, "products/create.html", {"form": form})


class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):

    # Permissão necessária para acessar qualquer método (get, put ou delete)
    def get_permission_required(self):
        method_request = self.request.method
        if method_request == "PUT" or method_request == "GET":
            return ["products.change_product"]
        return []

    def get(self, request, id_product):

        # Lógica para recuperar um produto específico

        product = ProductService.get_product_by_id(id_product=id_product)
        if not product:
            return redirect("product-list-create")

        return render(request, "products/edit.html", {"product": product})

    def put(self, request, id_product):
        # Lógica para atualizar um produto específico
        # ... processar request.POST ...

        # Conferir a lógica

        product = ProductService.get_product_by_id(id_product)

        if not product:
            return render(request, "error/404.html")

        form = ProductForm(request.POST or None, instance=product)

        if form.is_valid():
            try:
                update_product = ProductService.update_product(request, product)
                messages.success("O produto foi modificado com sucesso!")

            except Exception as e:
                messages.error("Não foi possível fazer a atualização do produto!")

        else:
            messages.error("Os dados enviados não são válidos.")

        return render(request, "products/edit.html", {"form": form})


class ProductDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "products.delete_product"

    def post(self, request, id_product):

        # Lógica para deletar um produto específico
        try:
            deleted = ProductService.delete_product_by_id(id_product)
        except Exception as e:
            messages.error(request, f"Erro ao excluir o produto: {e}")
            return redirect("product-list-create")

        if not deleted:
            return render(request, "errors/404.html", status=404)

        messages.success(request, "Produto deletado com sucesso!")
        return redirect("product-list-create")


class CategoryListCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):

    # Permissão necessária para acessar qualquer método (get ou post)
    def get_permission_required(self):
        if self.request.method == "POST":
            return ["products.add_category"]
        return ["products.view_category"]

    def get(self, request):
        # Lógica para listar todos os categorias

        categories = CategoryService.get_all()

        return render(
            request, "products/categories/index.html", {"categories": categories}
        )

    def post(self, request):
        # Lógica para criar um nova categoria
        # ... processar request.POST ou request.body ...
        form = CategoryForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success("A categoria foi criada com sucesso!")
        else:
            messages.error("Verifique se os dados inseridos estão corretos!")
        return render(request, "products/categories/create.html", {"form": form})


class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):

    # Permissão necessária para acessar qualquer método (get, put ou delete)
    def get_permission_required(self):
        method_request = self.request.method
        if method_request == "PUT" or method_request == "GET":
            return ["products.change_category"]
        return []

    def get(self, request, id_category):

        # Lógica para recuperar uma categoria específica

        category = CategoryService.get_category_by_id(id_category=id_category)

        if not category:
            return redirect("category-list-create")

        return render(request, "products/categories/edit.html", {"category": category})

    def put(self, request, id_category):

        # Lógica para atualizar uma categoria específica
        # ... processar request.body ...

        category = CategoryService.get_category_by_id(id_category)

        if not category:
            return render(request, "errors/404.html")

        form = CategoryForm(request.POST or None, instance=category)

        if form.is_valid():
            form.save()
            messages.success("A categoria foi atualizada com sucesso!")

        return render(request, "products/categories/edit.html", {"form": form})


class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "products.delete_category"

    def post(self, request, id_category):

        # Lógica para deletar uma categoria específica
        category = CategoryService.delete_category_by_id(request, id_category)
        if not category:

            # Renderiza um template de erro 404 customizado com status 404
            return render(request, "errors/404.html")

        return redirect("category-list-create")
