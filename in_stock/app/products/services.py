from django.core.files.storage import default_storage

from in_stock.app.suppliers.models import Supplier

from .forms import ProductForm
from .models import Category, Product, ProductSupplier


class ProductService:
    @staticmethod
    def get_all():
        """Retorna todos os produtos com categoria relacionada"""
        return Product.objects.select_related("category").all()

    @staticmethod
    def get_product_by_id(id_product):
        """Retorna um produto pelo ID"""
        try:
            return Product.objects.select_related("category").get(id=id_product)
        except Product.DoesNotExist:
            return None

    @staticmethod
    def create_product(request):
        """Cria um novo produto"""
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()

            # Associar fornecedor se fornecido no form
            supplier = form.cleaned_data.get("supplier")
            if supplier:
                ProductSupplier.objects.create(product=product, supplier=supplier)

            return product
        return None

    @staticmethod
    def update_product(request, product):
        """Atualiza um produto existente"""
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)

            # Atualizar fornecedor se fornecido
            supplier_id = request.POST.get("supplier")
            if supplier_id:
                try:
                    supplier = Supplier.objects.get(id=supplier_id)
                    # Remove associação anterior e cria nova
                    ProductSupplier.objects.filter(product=product).delete()
                    ProductSupplier.objects.create(product=product, supplier=supplier)
                except Supplier.DoesNotExist:
                    pass

            product.save()
            return product
        return None

    @staticmethod
    def delete_product_by_id(id_product):
        """Deleta um produto pelo ID e remove sua imagem"""
        try:
            product = Product.objects.get(pk=id_product)

            # Deleta imagem, se existir
            if product.image and default_storage.exists(product.image.name):
                default_storage.delete(product.image.name)

            product.delete()
            return True

        except Product.DoesNotExist:
            return False

        except Exception:
            # Deixa view decidir o que fazer
            raise


class CategoryService:
    @staticmethod
    def get_all():
        """Retorna todas as categorias"""
        return Category.objects.all()

    @staticmethod
    def get_category_by_id(id_category):
        """Retorna uma categoria pelo ID"""
        try:
            return Category.objects.get(id=id_category)
        except Category.DoesNotExist:
            return None

    @staticmethod
    def delete_category_by_id(id_category):
        """Deleta uma categoria pelo ID"""
        try:
            category = Category.objects.get(id=id_category)
            category.delete()
            return True
        except Category.DoesNotExist:
            return False
