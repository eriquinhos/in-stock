from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from .forms import SaleForm
from .models import Sale
from .services import SaleService


class SaleListView(LoginRequiredMixin, PermissionRequiredMixin, View):

    def get_permission_required(self):
        return ["sales.view_sale"]

    def get(self, request):
        if request.user.company_obj:
            sales = SaleService.get_by_company(request.user.company_obj)
            stats = SaleService.get_sales_statistics(request.user.company_obj)
        else:
            sales = SaleService.get_all()
            stats = SaleService.get_sales_statistics()

        type_filter = request.GET.get("type", "")
        product_filter = request.GET.get("product", "")

        if type_filter:
            sales = sales.filter(type=type_filter)
        if product_filter:
            sales = sales.filter(product__name__icontains=product_filter)

        context = {
            "sales": sales,
            "type_filter": type_filter,
            "product_filter": product_filter,
            "stats": stats,
        }

        return render(request, "sales/index.html", context)


class SaleCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):

    def get_permission_required(self):
        if self.request.method == "POST":
            return ["sales.add_sale"]
        return ["sales.view_sale"]

    def get(self, request):
        form = SaleForm()
        return render(request, "sales/create.html", {"form": form})

    def post(self, request):
        form = SaleForm(request.POST or None)

        if form.is_valid():
            type_sale = request.POST.get("type")

            try:
                create_sale = SaleService.create_sale_by_type(
                    request, type_sale)
            except Exception as e:
                messages.error(
                    request, f"Ocorreu um erro ao salvar a movimentação: {str(e)}")
                return render(request, "sales/create.html", {"form": form})

            if not create_sale:
                messages.error(
                    request, "Não foi possível salvar a movimentação!")
            else:
                messages.success(
                    request, "A movimentação foi registrada com sucesso!")
                return redirect("sale-list")

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        return render(request, "sales/create.html", {"form": form})
