from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class CustomUserManagerTests(TestCase):
    """Testa o gerenciador de usuários customizado"""

    def test_create_user(self):
        """Testa a criação de um usuário comum"""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password("testpass123"))

    def test_create_user_without_email(self):
        """Testa se o sistema não permite criar usuário sem email"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="testpass123")

    def test_create_superuser(self):
        """Testa a criação de um superusuário"""
        admin = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_normalize_email(self):
        """Testa se o email é normalizado (lowercase)"""
        user = User.objects.create_user(
            email="TEST@EXAMPLE.COM", password="testpass123"
        )
        self.assertEqual(user.email, "test@example.com")


class CustomUserModelTests(TestCase):
    """Testa o modelo de usuário customizado"""

    def setUp(self):
        """Prepara dados para cada teste"""
        self.user = User.objects.create_user(
            email="user@example.com",
            password="testpass123",
            name="Test User",
            phone="11999999999",
        )

    def test_user_creation_with_all_fields(self):
        """Testa criação de usuário com todos os campos"""
        self.assertEqual(self.user.name, "Test User")
        self.assertEqual(self.user.email, "user@example.com")
        self.assertEqual(self.user.phone, "11999999999")
        # Correção: type -> role, standard -> operator
        self.assertEqual(self.user.role, "operator")

    def test_user_string_representation(self):
        """Testa a representação em string do usuário"""
        self.assertEqual(str(self.user), "user@example.com")

    def test_default_user_type(self):
        """Testa se o tipo padrão de usuário é 'operator'"""
        # Correção: type -> role, standard -> operator
        self.assertEqual(self.user.role, "operator")

    def test_user_can_be_admin_type(self):
        """Testa se um usuário pode ser do tipo 'company_admin'"""
        # Correção: type -> role, admin -> company_admin
        admin = User.objects.create_user(
            email="admin@example.com", password="adminpass123", role="company_admin"
        )
        self.assertEqual(admin.role, "company_admin")

    def test_email_uniqueness(self):
        """Testa se o email deve ser único"""
        with self.assertRaises(Exception):
            User.objects.create_user(
                email="user@example.com", password="anotherpass123"
            )

    def test_date_joined_is_set(self):
        """Testa se a data de criação é registrada"""
        self.assertIsNotNone(self.user.date_joined)