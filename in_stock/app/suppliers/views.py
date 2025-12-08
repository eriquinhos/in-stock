from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from .forms import SupplierForm
from .models import Supplier
from .service import SupplierService


class SupplierListCreateView(LoginRequiredMixin, View):

    def get(self, request):
        # Filtra fornecedores pela empresa do usuário (multi-tenant)
        if request.user.is_instock_admin:
            suppliers = SupplierService.get_all()
        elif request.user.company_obj:
            suppliers = SupplierService.get_all().filter(company=request.user.company_obj)
        else:
            suppliers = SupplierService.get_all().none()
            
        return render(request, "suppliers/list.html", {"suppliers": suppliers})


class SupplierCreateView(LoginRequiredMixin, View):

    def get(self, request):
        # Exibe o formulário vazio
        form = SupplierForm()
        return render(request, "suppliers/create.html", {"form": form})

    def post(self, request):
        # Cria o fornecedor
        form = SupplierForm(request.POST)
        if form.is_valid():
            try:
                supplier_created = SupplierService.create_supplier(request)
                messages.success(request, "O fornecedor foi criado com sucesso!")
                return redirect("supplier-list-create")
            except Exception as e:
                messages.error(request, f"Não foi possível criar o fornecedor: {e}")
        else:
            messages.error(request, "Os dados enviados estão incorretos!")

        return render(request, "suppliers/create.html", {"form": form})


class SupplierDetailView(LoginRequiredMixin, View):

    def get(self, request, id_supplier):
        supplier = SupplierService.get_supplier_by_id(id_supplier)
        if not supplier:
            return redirect("supplier-list-create")

        form = SupplierForm(instance=supplier)
        return render(
            request, "suppliers/edit.html", {"supplier": supplier, "form": form}
        )

    def post(self, request, id_supplier):
        supplier = SupplierService.get_supplier_by_id(id_supplier)
        if not supplier:
            return render(request, "errors/404.html")

        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            try:
                update_supplier = SupplierService.update_supplier(request, supplier)
                messages.success(request, "O fornecedor foi atualizado com sucesso!")
                return redirect("supplier-list-create")
            except Exception as e:
                messages.error(
                    request, f"Não foi possível fazer a atualização do fornecedor! {e}"
                )
        else:
            messages.error(request, "Os dados enviados estão incorretos!")

        return render(
            request, "suppliers/edit.html", {"supplier": supplier, "form": form}
        )


class SupplierDeleteView(LoginRequiredMixin, View):

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
