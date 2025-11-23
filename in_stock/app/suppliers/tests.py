from django.test import TestCase
from in_stock.app.suppliers.models import Supplier


class SupplierModelTests(TestCase):
    """Testa o modelo de fornecedores"""

    def setUp(self):
        """Prepara dados para cada teste"""
        self.supplier = Supplier.objects.create(
            name='Tech Supplier',
            cnpj='12345678000190',
            phone='1133334444',
            email='contact@techsupplier.com',
            address='Rua Principal, 123 - São Paulo, SP'
        )

    def test_supplier_creation(self):
        """Testa criação de um fornecedor"""
        self.assertEqual(self.supplier.name, 'Tech Supplier')
        self.assertEqual(self.supplier.cnpj, '12345678000190')
        self.assertEqual(self.supplier.phone, '1133334444')
        self.assertEqual(self.supplier.email, 'contact@techsupplier.com')
        self.assertEqual(self.supplier.address,
                         'Rua Principal, 123 - São Paulo, SP')

    def test_supplier_string_representation(self):
        """Testa a representação em string do fornecedor"""
        self.assertEqual(str(self.supplier), 'Tech Supplier')

    def test_supplier_cnpj_uniqueness(self):
        """Testa se o CNPJ deve ser único"""
        with self.assertRaises(Exception):
            Supplier.objects.create(
                name='Another Supplier',
                cnpj='12345678000190'
            )

    def test_supplier_ordering(self):
        """Testa se os fornecedores são ordenados por nome"""
        Supplier.objects.create(
            name='ABC Supplier',
            cnpj='98765432000190'
        )
        Supplier.objects.create(
            name='XYZ Supplier',
            cnpj='11111111000190'
        )
        suppliers = list(Supplier.objects.all().values_list('name', flat=True))
        self.assertEqual(
            suppliers, ['ABC Supplier', 'Tech Supplier', 'XYZ Supplier'])

    def test_supplier_optional_fields(self):
        """Testa se campos opcionais podem ser deixados em branco"""
        supplier = Supplier.objects.create(
            name='Minimal Supplier',
            cnpj='55555555000190'
        )
        self.assertIsNone(supplier.phone)
        self.assertIsNone(supplier.email)
        self.assertIsNone(supplier.address)

    def test_supplier_timestamps(self):
        """Testa se os timestamps são registrados"""
        self.assertIsNotNone(self.supplier.created_at)
        self.assertIsNotNone(self.supplier.updated_at)
