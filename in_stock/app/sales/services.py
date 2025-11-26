from django.contrib import messages

from in_stock.app.products.models import Product

from .models import Sale


class SaleService:

    def get_all(self):
        return Sale.objects.select_related("product", "user").order_by("-created_at")

    # Referente a movimentação ENTRADA ou SAÍDA feita na CRUD
    def create_sale_by_type(self, request, type_sale: str):
        id_product = request.POST.get("product")
        quantity = request.POST.get("quantity")

        sale = Sale()
        sale.product = id_product
        sale.user = request.user.id
        sale.supplier = request.POST.get("supplier")
        sale.type = type_sale
        sale.quantity = quantity
        sale.description = request.POST.get("description") or None

        sale.save()

        # Decrementar ou Incrementar a quantidade do produto
        self.update_product_quantity(request, id_product, type_sale, quantity)

        return sale

    # Referente a movimentação ENTRADA feita na criação de um Produto

    @staticmethod
    def create_sale_entry_standard(request, product: Product):

        sale = Sale(
            product=product.id,
            user=request.user.id,
            supplier=product.supplier.values_list("id", flat=True).first(),
            type="entry",
            quantity=product.quantity,
            description="Registro de ENTRADA padrão.",
        )

        sale.save()
        return sale

    def update_product_quantity(
        self, request, id_product: int, type_sale: str, quantity: int
    ):

        try:
            product = Product.objects.get(pk=id_product)

            if type_sale == "exist":
                product.quantity = max(product.quantity - quantity, 0)
            else:
                product.quantity = product.quantity + quantity

            product.save()

        except Product.DoesNotExist:
            messages.error(
                request, f"O produto com ID {id_product} não foi encontrado."
            )
