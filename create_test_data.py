"""
Script para criar dados de teste no banco de dados
Execute com: python create_test_data.py
"""
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'in_stock.config.settings')
os.environ['USE_SQLITE'] = 'true'

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from in_stock.app.users.models import CustomUser
from in_stock.app.products.models import Product, Category
from in_stock.app.suppliers.models import Supplier
from in_stock.app.sales.models import Sale
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

def create_test_data():
    print("Criando dados de teste...")
    
    # Criar superusuário se não existir
    if not CustomUser.objects.filter(email='admin@admin.com').exists():
        CustomUser.objects.create_superuser(
            email='admin@admin.com',
            password='admin123',
            name='Administrador'
        )
        print("✓ Superusuário criado: admin@admin.com / admin123")
    else:
        print("✓ Superusuário já existe")
    
    # Criar categorias
    categorias = ['Eletrônicos', 'Alimentos', 'Bebidas', 'Limpeza', 'Higiene']
    for nome in categorias:
        Category.objects.get_or_create(name=nome)
    print(f"✓ {len(categorias)} categorias criadas")
    
    # Criar fornecedores
    fornecedores_data = [
        {'name': 'Tech Solutions', 'cnpj': '11.111.111/0001-11', 'email': 'contato@techsolutions.com', 'phone': '11999999999'},
        {'name': 'Alimentos Brasil', 'cnpj': '22.222.222/0001-22', 'email': 'vendas@alimentosbr.com', 'phone': '11988888888'},
        {'name': 'Distribuidora Central', 'cnpj': '33.333.333/0001-33', 'email': 'central@dist.com', 'phone': '11977777777'},
    ]
    for data in fornecedores_data:
        Supplier.objects.get_or_create(cnpj=data['cnpj'], defaults=data)
    print(f"✓ {len(fornecedores_data)} fornecedores criados")
    
    # Criar produtos
    cat_eletronicos = Category.objects.get(name='Eletrônicos')
    cat_alimentos = Category.objects.get(name='Alimentos')
    cat_bebidas = Category.objects.get(name='Bebidas')
    
    # Data futura para produtos sem vencimento real
    data_futura = timezone.now().date() + timedelta(days=365*5)  # 5 anos
    
    produtos_data = [
        {'name': 'Smartphone Samsung', 'category': cat_eletronicos, 'quantity': 50, 'price': Decimal('1999.99'), 'expiration_date': data_futura},
        {'name': 'Notebook Dell', 'category': cat_eletronicos, 'quantity': 20, 'price': Decimal('4500.00'), 'expiration_date': data_futura},
        {'name': 'Fone Bluetooth', 'category': cat_eletronicos, 'quantity': 3, 'price': Decimal('299.99'), 'expiration_date': data_futura},  # estoque baixo
        {'name': 'Arroz 5kg', 'category': cat_alimentos, 'quantity': 100, 'price': Decimal('25.90'), 'expiration_date': timezone.now().date() + timedelta(days=180)},
        {'name': 'Feijão 1kg', 'category': cat_alimentos, 'quantity': 80, 'price': Decimal('8.50'), 'expiration_date': timezone.now().date() + timedelta(days=5)},  # próximo ao vencimento
        {'name': 'Leite Integral', 'category': cat_bebidas, 'quantity': 2, 'price': Decimal('5.99'), 'expiration_date': timezone.now().date() + timedelta(days=3)},  # estoque baixo e vencendo
        {'name': 'Refrigerante 2L', 'category': cat_bebidas, 'quantity': 60, 'price': Decimal('8.99'), 'expiration_date': timezone.now().date() + timedelta(days=90)},
        {'name': 'Suco Natural', 'category': cat_bebidas, 'quantity': 40, 'price': Decimal('12.50'), 'expiration_date': timezone.now().date() + timedelta(days=7)},  # próximo ao vencimento
    ]
    
    for data in produtos_data:
        Product.objects.get_or_create(name=data['name'], defaults=data)
    print(f"✓ {len(produtos_data)} produtos criados")
    
    # Criar algumas vendas
    admin_user = CustomUser.objects.get(email='admin@admin.com')
    produtos = Product.objects.all()[:3]
    for i, produto in enumerate(produtos):
        Sale.objects.get_or_create(
            product=produto,
            quantity=5 + i,
            defaults={
                'type': 'out',
                'date': timezone.now() - timedelta(days=i),
                'user': admin_user
            }
        )
    print("✓ Vendas de exemplo criadas")
    
    print("\n" + "="*50)
    print("DADOS DE TESTE CRIADOS COM SUCESSO!")
    print("="*50)
    print("\nAcesse: http://127.0.0.1:8000/login/")
    print("Email: admin@admin.com")
    print("Senha: admin123")
    print("\nDepois do login, acesse: http://127.0.0.1:8000/dashboard/")

if __name__ == '__main__':
    create_test_data()
