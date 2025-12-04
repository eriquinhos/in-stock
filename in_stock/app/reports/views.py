import os
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.http import FileResponse
from django.shortcuts import redirect, render
from django.views import View

from .services import ReportService


class ReportListCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):

    # Permissão necessária para acessar qualquer método (get ou post)
    def get_permission_required(self):
        if self.request.method == "POST":
            return ["reports.add_report"]
        return ["reports.view_report"]

    def get(self, request):

        # Lógica para listar todos os relatorios gerados
        reports = ReportService.get_all()

        return render(request, "reports/index.html", {"reports": reports})

    def post(self, request):

        # Lógica para criar um novo relatório
        # ... processar request.POST ou request.body ...
        try:

            report = ReportService.create_report_by_user(request)
        except Exception as e:
            messages.error(request, "Não foi possível realizar o relatório!")
            return redirect("report-list-create")

        pdf_path_created = ReportService.create_report_pdf(request)

        if not pdf_path_created or not os.path.exists(pdf_path_created):
            messages.error(request, "O arquivo PDF não foi gerado.")
            return redirect("report-list-create")

        # Retorna como download
        filename = f"relatorio_produtos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return FileResponse(
            open(pdf_path_created, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )
