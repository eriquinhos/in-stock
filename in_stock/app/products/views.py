from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.shortcuts import redirect, render
from django.views import View

# from .forms import CategoryForm, ProductForm
from .services import CategoryService, ProductService


class ProductListCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    # Permissão necessária
    def get_permission_required(self):
        if self.request.method == "POST":
            return ["products.add_product"]
        return ["products.view_product"]

    def get(self, request):
        # Lógica para listar todos os produtos
        products = ProductService.get_all()
        # Aponta para a sua tela principal (Tabela de Produtos)
        return render(
            request,
            "pages/GestaoProdutos.html",
            {"products": products, "active_page": "products"},
        )

    def post(self, request):
        # Lógica para criar novo produto
        form = ProductForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            try:
                ProductService.create_product(request)
                messages.success(request, "O produto foi criado com sucesso!")
                # Após criar, volta para a lista (Gestão)
                return redirect("product-list-create")
            except Exception:
                messages.error(request, "Não foi possível salvar o produto!")
        else:
            messages.error(request, "Verifique se os dados inseridos estão corretos!")

        return render(request, "products/create.html", {"form": form})


class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    # Permissões
    def get_permission_required(self):
        method_request = self.request.method
        if (
            method_request == "PUT"
            or method_request == "GET"
            or method_request == "POST"
        ):
            return ["products.change_product"]
        return []

    def get(self, request, id_product):
        # Recupera o produto para edição
        product = ProductService.get_product_by_id(id_product=id_product)

        if not product:
            # CORREÇÃO: Se não achar, volta para a lista principal
            return redirect("product-list-create")

        # CORREÇÃO: Ao clicar em editar, deve abrir o formulário de edição (edit.html),
        # e não a lista (GestaoProdutos.html), senão você não consegue alterar os dados.
        form = ProductForm(instance=product)
        return render(request, "products/edit.html", {"form": form, "product": product})

    # Mudei para POST pois HTML forms padrão não enviam PUT nativamente sem JS
    def post(self, request, id_product):
        product = ProductService.get_product_by_id(id_product)

        if not product:
            return redirect("product-list-create")

        form = ProductForm(request.POST or None, instance=product)

        if form.is_valid():
            try:
                ProductService.update_product(request, product)
                messages.success(request, "O produto foi modificado com sucesso!")
                # CORREÇÃO: Após salvar, volta para a lista principal
                return redirect("product-list-create")

            except Exception as e:
                messages.error(
                    request, "Não foi possível fazer a atualização do produto!"
                )
        else:
            messages.error(request, "Os dados enviados não são válidos.")

        return render(request, "products/edit.html", {"form": form, "product": product})


class ProductDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "products.delete_product"

    def post(self, request, id_product):
        try:
            deleted = ProductService.delete_product_by_id(id_product)
        except Exception as e:
            messages.error(request, f"Erro ao excluir o produto: {e}")
            return redirect("product-list-create")

        if not deleted:
            messages.error(request, "Produto não encontrado.")
        else:
            messages.success(request, "Produto deletado com sucesso!")

        # CORREÇÃO: Volta sempre para a lista principal
        return redirect("product-list-create")


# ... As classes de Category permanecem iguais, apenas certifique-se
# de que os redirects delas também apontem para "category-list-create" se necessário.
class CategoryListCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    def get_permission_required(self):
        if self.request.method == "POST":
            return ["products.add_category"]
        return ["products.view_category"]

    def get(self, request):
        categories = CategoryService.get_all()
        return render(
            request, "products/categories/index.html", {"categories": categories}
        )

    def post(self, request):
        form = CategoryForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, "A categoria foi criada com sucesso!")
            return redirect("category-list-create")
        else:
            messages.error(request, "Erro ao criar categoria")
        return render(request, "products/categories/create.html", {"form": form})


# ... (CategoryUpdateView e CategoryDeleteView mantidos, lógica similar)
class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    def get_permission_required(self):
        return ["products.change_category"]

    def get(self, request, id_category):
        category = CategoryService.get_category_by_id(id_category=id_category)
        if not category:
            return redirect("category-list-create")
        return render(request, "products/categories/edit.html", {"category": category})

    def post(self, request, id_category):  # Alterado put para post por compatibilidade
        category = CategoryService.get_category_by_id(id_category)
        if not category:
            return redirect("category-list-create")

        form = CategoryForm(request.POST or None, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoria atualizada!")
            return redirect("category-list-create")
        return render(request, "products/categories/edit.html", {"form": form})


class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "products.delete_category"

    def post(self, request, id_category):
        CategoryService.delete_category_by_id(request, id_category)
        return redirect("category-list-create")
