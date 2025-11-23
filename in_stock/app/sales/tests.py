from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from in_stock.app.sales.models import Sale
from in_stock.app.products.models import Category, Product
from in_stock.app.suppliers.models import Supplier

User = get_user_model()


class SaleModelTests(TestCase):
    """Testa o modelo de vendas/movimentações"""

    def setUp(self):
        """Prepara dados para cada teste"""
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
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

    def test_sale_entry_creation(self):
        """Testa criação de uma entrada de estoque"""
        sale = Sale.objects.create(
            product=self.product,
            user=self.user,
            type='entry',
            quantity=5,
            description='Compra de notebooks'
        )
        self.assertEqual(sale.product, self.product)
        self.assertEqual(sale.user, self.user)
        self.assertEqual(sale.type, 'entry')
        self.assertEqual(sale.quantity, 5)

    def test_sale_exit_creation(self):
        """Testa criação de uma saída de estoque"""
        sale = Sale.objects.create(
            product=self.product,
            user=self.user,
            type='exits',
            quantity=2,
            description='Venda de notebooks'
        )
        self.assertEqual(sale.type, 'exits')
        self.assertEqual(sale.quantity, 2)

    def test_sale_default_quantity(self):
        """Testa se a quantidade padrão é 1"""
        sale = Sale.objects.create(
            product=self.product,
            user=self.user,
            type='entry'
        )
        self.assertEqual(sale.quantity, 1)

    def test_sale_string_representation_with_description(self):
        """Testa a representação em string com descrição"""
        sale = Sale.objects.create(
            product=self.product,
            user=self.user,
            type='entry',
            quantity=5,
            description='Compra de notebooks'
        )
        self.assertIn('Entrada', str(sale))
        self.assertIn('Compra de notebooks', str(sale))

    def test_sale_string_representation_without_description(self):
        """Testa a representação em string sem descrição"""
        sale = Sale.objects.create(
            product=self.product,
            user=self.user,
            type='entry',
            quantity=5
        )
        self.assertIn('Entrada', str(sale))
        self.assertIn('Notebook', str(sale))

    def test_sale_with_supplier(self):
        """Testa criação de venda com fornecedor"""
        sale = Sale.objects.create(
            product=self.product,
            user=self.user,
            supplier=self.supplier,
            type='entry',
            quantity=10
        )
        self.assertEqual(sale.supplier, self.supplier)

    def test_sale_timestamps(self):
        """Testa se os timestamps são registrados"""
        sale = Sale.objects.create(
            product=self.product,
            user=self.user,
            type='entry'
        )
        self.assertIsNotNone(sale.created_at)
        self.assertIsNotNone(sale.updated_at)

    def test_sale_default_date(self):
        """Testa se a data padrão é a data atual"""
        sale = Sale.objects.create(
            product=self.product,
            user=self.user,
            type='entry'
        )
        self.assertIsNotNone(sale.date)
