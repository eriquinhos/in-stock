from django.contrib import messages

from in_stock.app.products.models import Product

from .models import Sale


class SaleService:

    @staticmethod
    def get_all():
        return Sale.objects.select_related("product", "user").order_by("-created_at")

    @staticmethod
    def get_by_company(company):
        return Sale.objects.filter(company=company).select_related("product", "user").order_by("-created_at")

    @staticmethod
    def create_sale_by_type(request, type_sale: str):
        id_product = request.POST.get("product")
        quantity = int(request.POST.get("quantity", 1))

        try:
            product = Product.objects.get(pk=id_product)
        except Product.DoesNotExist:
            messages.error(
                request, f"O produto com ID {id_product} não foi encontrado.")
            return None

        sale = Sale()
        sale.product = product
        sale.user = request.user
        sale.company = request.user.company_obj
        sale.supplier = request.POST.get("supplier") or None
        sale.type = type_sale
        sale.quantity = quantity
        sale.description = request.POST.get("description") or None

        sale.save()

        SaleService.update_product_quantity(product, type_sale, quantity)

        return sale

    @staticmethod
    def create_sale_entry_standard(request, product: Product):

        sale = Sale(
            product=product,
            user=request.user,
            company=request.user.company_obj,
            supplier=product.supplier.values_list("id", flat=True).first(),
            type="entry",
            quantity=product.quantity,
            description="Registro de ENTRADA padrão.",
        )

        sale.save()
        return sale

    @staticmethod
    def update_product_quantity(product: Product, type_sale: str, quantity: int):
        try:
            if type_sale == "exits":
                product.quantity = max(product.quantity - quantity, 0)
            else:
                product.quantity = product.quantity + quantity

            product.save()

        except Exception as e:
            print(f"Erro ao atualizar quantidade do produto: {str(e)}")

    @staticmethod
    def get_sales_statistics(company=None):
        query = Sale.objects.all()
        if company:
            query = query.filter(company=company)

        total_entries = query.filter(type="entry").count()
        total_exits = query.filter(type="exits").count()

        return {
            "total_entries": total_entries,
            "total_exits": total_exits,
            "total_movements": total_entries + total_exits,
        }

    @staticmethod
    def get_sales_by_date_range(start_date, end_date, company=None):
        query = Sale.objects.filter(date__gte=start_date, date__lte=end_date)
        if company:
            query = query.filter(company=company)
        return query.select_related("product", "user").order_by("-created_at")
