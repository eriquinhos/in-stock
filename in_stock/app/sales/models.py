from django.db import models
from django.utils import timezone


class Sale(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="sale_product",
        null=False,
    )
    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        related_name="sale_user",
        null=False,
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        related_name="sale_supplier",
        blank=True,
        null=True,
    )
    date = models.DateTimeField(default=timezone.now)
    TIPO = [("entry", "Entrada"), ("exits", "Saída")]
    type = models.CharField(max_length=5, choices=TIPO)
    quantity = models.IntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.description:
            return f"{self.get_type_display()} - {self.description} ({self.created_at.strftime('%d/%m/%Y')})"
        return f"{self.get_type_display()} - {self.product.name} ({self.created_at.strftime('%d/%m/%Y')})"
