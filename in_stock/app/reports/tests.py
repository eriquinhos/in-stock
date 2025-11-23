from django.test import TestCase
from django.contrib.auth import get_user_model
from in_stock.app.reports.models import Report

User = get_user_model()


class ReportModelTests(TestCase):
    """Testa o modelo de relatórios"""

    def setUp(self):
        """Prepara dados para cada teste"""
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )

    def test_expenses_report_creation(self):
        """Testa criação de um relatório de despesas"""
        report = Report.objects.create(
            user=self.user,
            type='expenses'
        )
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.type, 'expenses')

    def test_revenue_report_creation(self):
        """Testa criação de um relatório de receitas"""
        report = Report.objects.create(
            user=self.user,
            type='revenue'
        )
        self.assertEqual(report.type, 'revenue')

    def test_full_report_creation(self):
        """Testa criação de um relatório completo"""
        report = Report.objects.create(
            user=self.user,
            type='full'
        )
        self.assertEqual(report.type, 'full')

    def test_default_report_type(self):
        """Testa se o tipo padrão é 'full'"""
        report = Report.objects.create(user=self.user)
        self.assertEqual(report.type, 'full')

    def test_report_date_is_set(self):
        """Testa se a data do relatório é registrada"""
        report = Report.objects.create(user=self.user)
        self.assertIsNotNone(report.date)

    def test_multiple_reports_per_user(self):
        """Testa se um usuário pode ter múltiplos relatórios"""
        report1 = Report.objects.create(user=self.user, type='expenses')
        report2 = Report.objects.create(user=self.user, type='revenue')

        user_reports = Report.objects.filter(user=self.user)
        self.assertEqual(user_reports.count(), 2)
