from .models import Supplier


class SupplierService:
    def get_all(self):
        return Supplier.objects.all()

    def create_supplier(self, request):

        name = request.POST.get("name")
        cnpj = request.POST.get("cnpj")
        phone = request.POST.get("phone") or None
        email = request.POST.get("email") or None
        address = request.POST.get("address") or None

        supplier = Supplier(
            name=name, cnpj=cnpj, phone=phone, email=email, address=address
        )

        supplier.save()
        return supplier

    def get_supplier_by_id(self, id_supplier: int):
        try:
            supplier = Supplier.objects.get(pk=id_supplier)
            return supplier
        except Supplier.DoesNotExist:
            return None

    def update_supplier(request, supplier: Supplier):
        supplier.name = request.POST.get("name")
        supplier.cnpj = request.POST.get("cnpj")
        supplier.phone = request.POST.get("phone") or None
        supplier.email = request.POST.get("email") or None
        supplier.address = request.POST.get("address") or None

        supplier.save()
        return supplier

    def delete_supplier_by_id(self, id_supplier: int):
        try:
            supplier = Supplier.objects.get(pk=id_supplier)
            supplier.delete()
            return True
        except Supplier.DoesNotExist:
            return False

        except Exception:
            raise
