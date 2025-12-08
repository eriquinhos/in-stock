from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from .forms import CategoryForm, ProductForm
from .services import CategoryService, ProductService

# =========================
# PRODUTOS
# =========================


class ProductListCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    def get_permission_required(self):
        if self.request.method == "POST":
            return ["products.add_product"]
        return ["products.view_product"]

    def get(self, request):
        products = ProductService.get_all()
        return render(
            request,
            "products/list.html",
            {"products": products, "active_page": "products"},
        )

    def post(self, request):
        form = ProductForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            try:
                ProductService.create_product(request)
                messages.success(request, "O produto foi criado com sucesso!")
                return redirect("product-list-create")
            except Exception:
                messages.error(request, "Não foi possível salvar o produto!")
        else:
            messages.error(request, "Verifique se os dados inseridos estão corretos!")

        return render(request, "products/create.html", {"form": form})


class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "products.add_product"

    def get(self, request):
        form = ProductForm()
        return render(
            request,
            "product/create.html",
            {"form": form, "active_page": "products"},
        )

    def post(self, request):
        form = ProductForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            try:
                ProductService.create_product(request)
                messages.success(request, "O produto foi criado com sucesso!")
                return redirect("product-list-create")
            except Exception:
                messages.error(request, "Não foi possível salvar o produto!")
        else:
            messages.error(request, "Verifique se os dados inseridos estão corretos!")

        return render(
            request,
            "product/create.html",
            {"form": form, "active_page": "products"},
        )


class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    def get_permission_required(self):
        method_request = self.request.method
        if method_request in ("PUT", "GET", "POST"):
            return ["products.change_product"]
        return []

    def get(self, request, id_product):
        product = ProductService.get_product_by_id(id_product=id_product)

        if not product:
            return redirect("product-list-create")

        form = ProductForm(instance=product)
        return render(
            request,
            "products/edit.html",
            {"form": form, "product": product, "active_page": "products"},
        )

    def post(self, request, id_product):
        product = ProductService.get_product_by_id(id_product)

        if not product:
            return redirect("product-list-create")

        form = ProductForm(request.POST or None, instance=product)

        if form.is_valid():
            try:
                ProductService.update_product(request, product)
                messages.success(request, "O produto foi modificado com sucesso!")
                return redirect("product-list-create")
            except Exception:
                messages.error(
                    request,
                    "Não foi possível fazer a atualização do produto!",
                )
        else:
            messages.error(request, "Os dados enviados não são válidos.")

        return render(
            request,
            "products/edit.html",
            {"form": form, "product": product, "active_page": "products"},
        )


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

        return redirect("product-list-create")


class CategoryListView(LoginRequiredMixin, PermissionRequiredMixin, View):
    def get_permission_required(self):
        return ["products.view_category"]

    def get(self, request):
        categories = CategoryService.get_all()
        return render(
            request,
            "products/categories/index.html",
            {
                "categories": categories,
                "active_page": "categories",
            },
        )


class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "products.add_category"

    def get(self, request):
        form = CategoryForm()
        return render(
            request,
            "products/categories/create.html",
            {
                "form": form,
                "active_page": "categories",
            },
        )

    def post(self, request):
        form = CategoryForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, "A categoria foi criada com sucesso!")
            return redirect("category-list-create")
        messages.error(request, "Erro ao criar categoria")
        return render(
            request,
            "products/categories/create.html",
            {
                "form": form,
                "active_page": "categories",
            },
        )


class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    def get_permission_required(self):
        return ["products.change_category"]

    def get(self, request, id_category):
        category = CategoryService.get_category_by_id(id_category=id_category)
        if not category:
            return redirect("category-list-create")

        form = CategoryForm(instance=category)
        return render(
            request,
            "products/categories/edit.html",
            {
                "form": form,
                "category": category,
                "active_page": "categories",
            },
        )

    def post(self, request, id_category):
        category = CategoryService.get_category_by_id(id_category)
        if not category:
            return redirect("category-list-create")

        print(f"POST data: {request.POST}")  # ← VER O QUE ESTÁ SENDO ENVIADO

        form = CategoryForm(request.POST or None, instance=category)

        print(f"Form válido? {form.is_valid()}")
        print(
            f"Form cleaned data: {form.cleaned_data if form.is_valid() else form.errors}"
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Categoria atualizada!")
            return redirect("category-list-create")
        else:
            messages.error(request, f"Formulário inválido: {form.errors}")

        return render(
            request,
            "products/categories/edit.html",
            {
                "form": form,
                "category": category,
                "active_page": "categories",
            },
        )


class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "products.delete_category"

    def post(self, request, id_category):
        try:
            deleted = CategoryService.delete_category_by_id(id_category)
            if deleted:
                messages.success(request, "Categoria deletada!")
            else:
                messages.error(request, "Categoria não encontrada.")
        except Exception as e:
            messages.error(request, f"Erro ao deletar categoria: {e}")
        return redirect("category-list-create")
