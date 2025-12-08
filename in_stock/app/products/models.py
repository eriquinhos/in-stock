from datetime import timedelta

from django.db import models
from django.utils import timezone


class Category(models.Model):
    STATUS_CHOICES = (
        ("ativa", "Ativa"),
        ("inativa", "Inativa"),
    )

    name = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ativa")
    company = models.ForeignKey(
        "users.Company",
        on_delete=models.CASCADE,
        related_name="categories",
        null=True,
        blank=True,
        verbose_name="Empresa",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    PRODUCT_STATUS = (
        ("ok", "OK"),
        ("baixo", "Abaixo do Estoque"),
        ("proximo_vencimento", "Próximo do Vencimento"),
    )

    name = models.CharField(max_length=250, null=False)
    quantity = models.IntegerField(default=1)
    batch = models.CharField(max_length=100, null=True, blank=True, verbose_name="Lote")
    initial_quantity = models.IntegerField(
        default=1, verbose_name="Quantidade Inicial do Lote"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    expiration_date = models.DateField(null=False)
    status = models.CharField(
        max_length=20,
        choices=PRODUCT_STATUS,
        default="ok",
        verbose_name="Status do Estoque",
    )
    image = models.ImageField(upload_to="uploads", blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products_category", null=False
    )
    company = models.ForeignKey(
        "users.Company",
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
        verbose_name="Empresa",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    supplier = models.ManyToManyField(
        "suppliers.Supplier",
        related_name="products_suppliers",
        through="ProductSupplier",
    )

    class Meta:
        unique_together = ("name", "category")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_status(self):
        """Calcula o status baseado na quantidade e vencimento"""
        hoje = timezone.now().date()
        dias_para_vencer = (self.expiration_date - hoje).days

        # Verifica se está próximo do vencimento (menos de 7 dias)
        if dias_para_vencer < 7 and dias_para_vencer >= 0:
            return "proximo_vencimento"

        # Verifica se está abaixo da metade da quantidade inicial
        if self.quantity < (self.initial_quantity / 2):
            return "baixo"

        return "ok"

    def save(self, *args, **kwargs):
        """Atualiza status automaticamente ao salvar"""
        self.status = self.get_status()
        super().save(*args, **kwargs)


class ProductSupplier(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="productsupplier_product",
        null=False,
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        related_name="productsupplier_supplier",
        null=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} fornecido por {self.supplier.name}"
