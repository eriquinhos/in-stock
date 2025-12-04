import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "in_stock.config.settings")
os.environ["USE_SQLITE"] = "true"
django.setup()

from in_stock.app.products.models import Product, Category
from in_stock.app.suppliers.models import Supplier
from in_stock.app.sales.models import Sale
from in_stock.app.users.models import CustomUser
from datetime import date, timedelta

print("Criando dados de exemplo...")

# Criar categorias
cat1, _ = Category.objects.get_or_create(name="Alimentos")
cat2, _ = Category.objects.get_or_create(name="Bebidas")
cat3, _ = Category.objects.get_or_create(name="Limpeza")
print(f"Categorias criadas: {Category.objects.count()}")

# Criar fornecedores
sup1, _ = Supplier.objects.get_or_create(
    name="Fornecedor ABC", cnpj="12.345.678/0001-01"
)
sup2, _ = Supplier.objects.get_or_create(
    name="Distribuidora XYZ", cnpj="98.765.432/0001-99"
)
print(f"Fornecedores criados: {Supplier.objects.count()}")

# Criar produtos
p1, _ = Product.objects.get_or_create(
    name="Arroz 5kg",
    category=cat1,
    defaults={
        "quantity": 50,
        "price": 25.90,
        "expiration_date": date.today() + timedelta(days=180),
    },
)
p2, _ = Product.objects.get_or_create(
    name="Feijao 1kg",
    category=cat1,
    defaults={
        "quantity": 5,
        "price": 8.50,
        "expiration_date": date.today() + timedelta(days=120),
    },
)
p3, _ = Product.objects.get_or_create(
    name="Refrigerante 2L",
    category=cat2,
    defaults={
        "quantity": 3,
        "price": 9.99,
        "expiration_date": date.today() + timedelta(days=20),
    },
)
p4, _ = Product.objects.get_or_create(
    name="Suco Natural 1L",
    category=cat2,
    defaults={
        "quantity": 8,
        "price": 12.00,
        "expiration_date": date.today() + timedelta(days=10),
    },
)
p5, _ = Product.objects.get_or_create(
    name="Detergente 500ml",
    category=cat3,
    defaults={
        "quantity": 25,
        "price": 3.50,
        "expiration_date": date.today() + timedelta(days=365),
    },
)
print(f"Produtos criados: {Product.objects.count()}")

# Criar vendas/movimentacoes
user = CustomUser.objects.first()
if user and Sale.objects.count() == 0:
    Sale.objects.create(
        product=p1, user=user, type="entry", quantity=100, description="Compra inicial"
    )
    Sale.objects.create(
        product=p1,
        user=user,
        type="exits",
        quantity=50,
        description="Venda para cliente",
    )
    Sale.objects.create(
        product=p3, user=user, type="entry", quantity=20, description="Reposicao"
    )
    Sale.objects.create(
        product=p4,
        user=user,
        type="exits",
        quantity=12,
        description="Venda promocional",
    )
    print(f"Vendas criadas: {Sale.objects.count()}")
else:
    print(f"Vendas ja existem: {Sale.objects.count()}")

print("\n=== RESUMO ===")
print(f"Total de Categorias: {Category.objects.count()}")
print(f"Total de Produtos: {Product.objects.count()}")
print(f"Total de Fornecedores: {Supplier.objects.count()}")
print(f"Total de Vendas: {Sale.objects.count()}")
print("\nDados de exemplo criados com sucesso!")
