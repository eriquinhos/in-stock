from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from .models import Supplier
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .service import SupplierService
from django.contrib import messages
from .forms import SupplierForm


class SupplierListCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):

    # Permissão necessária para acessar qualquer método (get ou post)
    def get_permission_required(self):
        if self.request.method == "POST":
            return ["suppliers.add_supplier"]
        return ["suppliers.view_supplier"]

    def get(self, request):

        # Lógica para listar todos os fornecedores
        suppliers = SupplierService.get_all()
        return render(request, "suppliers/index.html", {"suppliers": suppliers})

    def post(self, request):

        # Lógica para criar um novo fornecedor
        # ... processar request.POST ou request.body ...

        form = SupplierForm(request.POST or None)
        if form.is_valid():
            try:
                supplier_created = SupplierService.create_supplier(request)

                messages.success(request, "O fornecedor foi criado com sucesso!")

            except Exception as e:
                messages.error(
                    request, f"Não foi possível criar o fornecedor devido a: {e}"
                )
        else:
            messages.error(request, "Os dados enviados estão incorretos!")

        return render(request, "suppliers/create.html")


class SupplierDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):

    # Permissão necessária para acessar qualquer método (get, put ou delete)
    def get_permission_required(self):
        method_request = self.request.method
        if method_request == "PUT" or method_request == "GET":
            return ["suppliers.change_supplier"]

        return []

    def get(self, request, id_supplier):

        # Lógica para recuperar um fornecedor específico

        supplier = SupplierService.get_supplier_by_id(id_supplier)

        if not supplier:
            return redirect("supplier-list-create")

        return render(request, "suppliers/edit.html", {"supplier": supplier})

    def put(self, request, id_supplier):

        # Lógica para atualizar um fornecedor específico
        # ... processar request.POST ...
        supplier = SupplierService.get_supplier_by_id(id_supplier)

        if not supplier:
            return render(request, "errors/404.html")

        form = SupplierForm(request.POST or None)
        if form.is_valid():

            try:
                update_supplier = SupplierService.update_supplier(request, supplier)
                messages.success(request, "O fornecedor foi atualizado com sucesso!")
            except Exception as e:
                messages.error(
                    request, "Não foi possível fazer a atualização do fornecedor!"
                )

        else:
            messages.error(request, "Os dados enviados estão incorretos!")

        return render(request, "suppliers/edit.html", {"form": form})


class SupplierDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "suppliers.delete_supplier"

    def post(self, request, id_supplier):

        # Lógica para deletar um fornecedor específico
        try:
            deleted = SupplierService.delete_supplier_by_id(id_supplier)
        except Exception as e:
            messages.error(request, f"Erro ao excluir o fornecedor: {e}")
            return redirect("supplier-list-create")

        if not deleted:
            return render(request, "errors/404.html", status=404)

        messages.success(request, "O fornecedor deletado com sucesso!")
        return redirect("supplier-list-create")
