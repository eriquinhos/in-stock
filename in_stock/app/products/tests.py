from datetime import date, timedelta

from django.test import TestCase

from in_stock.app.suppliers.models import Supplier
from .models import Category, Product, ProductSupplier


class CategoryModelTests(TestCase):
    """Testa o modelo de categorias"""

    def setUp(self):
        """Prepara dados para cada teste"""
        self.category = Category.objects.create(name='Eletrônicos')

    def test_category_creation(self):
        """Testa criação de uma categoria"""
        self.assertEqual(self.category.name, 'Eletrônicos')
        self.assertIsNotNone(self.category.created_at)
        self.assertIsNotNone(self.category.updated_at)

    def test_category_string_representation(self):
        """Testa a representação em string da categoria"""
        self.assertEqual(str(self.category), 'Eletrônicos')

    def test_category_ordering(self):
        """Testa se as categorias são ordenadas por nome"""
        Category.objects.create(name='Alimentos')
        Category.objects.create(name='Bebidas')
        categories = list(
            Category.objects.all().values_list('name', flat=True))
        self.assertEqual(categories, ['Alimentos', 'Bebidas', 'Eletrônicos'])


class ProductModelTests(TestCase):
    """Testa o modelo de produtos"""

    def setUp(self):
        """Prepara dados para cada teste"""
        self.category = Category.objects.create(name='Eletrônicos')
        self.supplier = Supplier.objects.create(
            name='Tech Supplier',
            cnpj='12345678000190'
        )
        self.product = Product.objects.create(
            name='Notebook',
            category=self.category,
            quantity=10,
            price=2500.00,
            expiration_date=date.today() + timedelta(days=365)
        )

    def test_product_creation(self):
        """Testa criação de um produto"""
        self.assertEqual(self.product.name, 'Notebook')
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(self.product.price, 2500.00)

    def test_product_string_representation(self):
        """Testa a representação em string do produto"""
        self.assertEqual(str(self.product), 'Notebook')

    def test_product_default_quantity(self):
        """Testa se a quantidade padrão é 1"""
        product = Product.objects.create(
            name='Mouse',
            category=self.category,
            price=50.00,
            expiration_date=date.today() + timedelta(days=30)
        )
        self.assertEqual(product.quantity, 1)

    def test_product_unique_name_per_category(self):
        """Testa se um produto com o mesmo nome não pode existir na mesma categoria"""
        with self.assertRaises(Exception):
            Product.objects.create(
                name='Notebook',
                category=self.category,
                quantity=5,
                price=2000.00,
                expiration_date=date.today() + timedelta(days=365)
            )

    def test_product_ordering(self):
        """Testa se os produtos são ordenados por nome"""
        Product.objects.create(
            name='Mouse',
            category=self.category,
            quantity=20,
            price=50.00,
            expiration_date=date.today() + timedelta(days=30)
        )
        products = list(Product.objects.all().values_list('name', flat=True))
        self.assertEqual(products, ['Mouse', 'Notebook'])

    def test_product_supplier_relationship(self):
        """Testa a relação entre produto e fornecedor"""
        self.product.supplier.add(self.supplier)
        self.assertIn(self.supplier, self.product.supplier.all())


class ProductSupplierModelTests(TestCase):
    """Testa o modelo de relacionamento entre produto e fornecedor"""

    def setUp(self):
        """Prepara dados para cada teste"""
        self.category = Category.objects.create(name='Eletrônicos')
        self.supplier = Supplier.objects.create(
            name='Tech Supplier',
            cnpj='12345678000190'
        )
        self.product = Product.objects.create(
            name='Notebook',
            category=self.category,
            quantity=10,
            price=2500.00,
            expiration_date=date.today() + timedelta(days=365)
        )
        self.product_supplier = ProductSupplier.objects.create(
            product=self.product,
            supplier=self.supplier
        )

    def test_product_supplier_creation(self):
        """Testa criação de um relacionamento produto-fornecedor"""
        self.assertEqual(self.product_supplier.product, self.product)
        self.assertEqual(self.product_supplier.supplier, self.supplier)

    def test_product_supplier_string_representation(self):
        """Testa a representação em string do relacionamento"""
        expected = f"{self.product.name}  fornecido por  {self.supplier.name}"
        self.assertEqual(str(self.product_supplier), expected)

    def test_product_supplier_uniqueness(self):
        """Testa se um produto só pode ter uma relação com um fornecedor"""
        with self.assertRaises(Exception):
            ProductSupplier.objects.create(
                product=self.product,
                supplier=self.supplier
            )
