from django.contrib import messages
from .models import Product, Category
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from in_stock.app.suppliers.models import Supplier


class ProductService:
    # Erro: Precisa tirar o messages dos services e colocar na view
    @staticmethod
    def get_all():
        return Product.objects.all()

    def create_product(self, request):
        image_path = self.save_image(request)

        name = request.POST.get("name")
        category = request.POST.get("category")
        quantity = request.POST.get("quantity")
        expiration_date = request.POST.get("expiration_date")

        product = Product(
            name=name,
            category=category,
            image=image_path,
            quantity=quantity,
            expiration_date=expiration_date,
        )
        product.save()

        # Criar relação com algum fornecedor já registrado
        supplier_input = request.POST.get("supplier")

        # Relacionamento N-N (product-supplier)
        suppliers = Supplier.objects.filter(id__in=supplier_input)
        for supplier in suppliers:
            product.supplier.add(supplier)

        # Lógica para criar uma movimentação ENTRADA

        return product

    @staticmethod
    def get_product_by_id(id_product: int):
        try:
            return Product.objects.get(pk=id_product)
        except Product.DoesNotExist:
            return None

    def save_image(self, request):
        """
        Salva a imagem enviada e retorna o caminho relativo (para gravar no model)
        ou None se ocorrer erro.
        """
        try:
            image = request.FILES["image"]
        except Exception:
            return None

        if not hasattr(image, "chunks"):
            messages.error(request, "Arquivo inválido.")
            return None

        fs = FileSystemStorage()  # Usa MEDIA_ROOT por padrão
        try:
            filename = fs.save(image.name, image)
            # retorna a URL (ex: /media/uploads/img.jpg)
            return fs.url(filename)
        except Exception as e:
            messages.error(request, f"Erro ao salvar imagem: {e}")
            return None

    def update_product(self, request, product: Product):

        product.name = request.POST.get("name")
        product.category = request.POST.get("category")
        # product.quantity = request.POST.get('quantity')
        product.expiration_date = request.POST.get("expiration_date")

        if "image" in request.FILES:
            product.image = self.save_image(request)

        product.save()
        return product

    @staticmethod
    def delete_product_by_id(request, id_product: int):
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
        return Category.objects.all()

    def create_category(self, request):
        name = request.POST.get("name")

        category = Category(
            name=name,
        )
        category.save()

        return category

    def get_category_by_id(self, request, id_category: int):
        try:
            return Category.objects.get(pk=id_category)
        except Category.DoesNotExist:
            return None

    def delete_category_by_id(self, request, id_category: int):
        try:
            category = Category.objects.get(pk=id_category)

            category.delete()
            messages.success("A categoria foi excluida com sucesso!")

            return True
        except Category.DoesNotExist:

            return False
