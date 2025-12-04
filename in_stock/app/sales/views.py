from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin,
)
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from .forms import SaleForm
from .models import Sale
from .services import SaleService


class SaleListCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):

    # Permissão necessária para acessar qualquer método (get ou post)
    def get_permission_required(self):
        if self.request.method == "POST":
            return ["sales.add_sale"]
        return ["sales.view_sale"]

    def get(self, request):

        # Lógica para listar todos os movimentações
        sales = SaleService.get_all()
        return render(request, "sales/index.html", {"sales": sales})

    def post(self, request):

        # Lógica para criar um nova movimentação
        # ... processar request.POST ou request.body ...
        form = SaleForm(request.POST or None)
        if form.is_valid():
            type_sale = request.POST.get("type")

            try:
                create_sale = SaleService.create_sale_by_type(request, type_sale)
            except Exception as e:
                messages.error(request, "Ocorreu um erro ao salvar a movimentação.")
                return render(request, "sales/create.html")

            if not create_sale:
                messages.error(request, "Não foi possível salvar a movimentação!")
            else:
                messages.success(request, "A movimentação foi registrada com sucesso!")

        else:
            messages.error(request, "Os dados enviados não são válidos.")

        return render(request, "sales/create.html")
