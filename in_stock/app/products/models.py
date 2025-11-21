from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Boa prática: ordenar por nome
        ordering = ['name']

    def __str__(self):
        """Devolve uma representação em string do Modelo"""
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=250, null=False)
    category = models.ForeignKey(
        'Category', on_delete=models.CASCADE, related_name='products_category', null=False)
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    expiration_date = models.DateField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Definir o ManyToManyField aqui.
    # O argumento `through` aponta para a tabela intermediária ProductSupplier.
    supplier = models.ManyToManyField(
        'suppliers.Supplier',
        through='ProductSupplier',
        related_name='products_suppliers'
    )

    # Apaga a imagem antiga se for substituída
    def save(self, *args, **kwargs):
        try:
            old = Product.objects.get(pk=self.pk)
            if old.image and old.image != self.image:
                old.image.delete(save=False)
        except Product.DoesNotExist:
            pass
        super().save(*args, **kwargs)

    class Meta:
        # Garante que o mesmo produto não seja criado na mesma categoria
        unique_together = ('name', 'category')
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductSupplier(models.Model):
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE, related_name='productsupplier_product', null=False)
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.CASCADE,
                                 related_name='productsupplier_supplier', null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Garante que um produto só pode ter uma relação com um fornecedor
        unique_together = ('product', 'supplier')

    def __str__(self):
        return f"{self.product.name}  fornecido por  {self.supplier.name}"
