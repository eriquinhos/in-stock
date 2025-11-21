from .models import Report
from in_stock.app.sales.models import Sale
from in_stock.app.products.models import Product
from django.contrib import messages
from datetime import datetime, date, timezone
from django.db.models import Prefetch
from django.template.loader import render_to_string
import tempfile
import os
import pdfkit


class ReportService():

    def get_all(self):
        return Report.objects.all()

    def create_report_by_user(self, request):
        user = request.user.id

        report = Report()

        report.user = user
        report.type = request.POST.get("type")
        report.save()
        return report

    def create_report_pdf(self, request):
        try:
            default_start = '2025-10-15'
            default_end = '2025-11-15'

            # Poderia ser feito seguindo um periodo estipulado pelo usuário
            # Fazer uma busca dos produtos junto com todas as movimentações AGRUPADOS pelos tipos (entrada e saída)

            # Crie o QuerySet filtrado de (Sales)
            sales_qs = Sale.objects.filter(
                date__gte=default_start, date__lte=default_end).get()

            # Use Prefetch no modelo Produto
            #    - 'sales' é o related_name original na ForeignKey
            #    - 'queryset=sales_qs' aplica o filtro
            #    - 'to_attr="vendas_tipo"' armazena o resultado em um novo atributo
            products = Product.objects.prefetch_related(
                Prefetch(
                    'sales',
                    queryset=sales_qs,
                    to_attr=f"movimentacoes"
                )
            ).all()

            # Criar a funcionalidade de PDF

            # Fazer pdf para diferentes tipos de relatório com o status do estoque completo
            # com mais informações de receitas e despesas

            # Gera o PDF
            pdf_path = self.convert_html_to_pdf(
                products, "products_pdf.html", "relatorio_produtos")

            if not os.path.exists(pdf_path):
                messages.error(request, "Arquivo não encontrado.")
                return False

            return pdf_path

        except Exception as e:
            messages.error(
                request, f"Não foi possível gerar pdf, devido ao erro: {e}")
            return False

    def convert_html_to_pdf(self, products: Product, save_name: str):

        # Montar HTML com o Django
        html_content = render_to_string('pages/pdf.html', {
            "products": products,
            "empresa": self.empresa,
            "data_emissao": timezone.now(),
        })

        # Cria um arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_html:
            tmp_html.write(html_content.encode("utf-8"))
            tmp_html.flush()

            output_path = f"media/pdfs/{save_name}.pdf"

            # Converte arquivos HTML locais em documentos PDF
            pdfkit.from_file(tmp_html.name, output_path)

        return output_path
