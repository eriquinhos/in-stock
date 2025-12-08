from django import forms

from in_stock.app.suppliers.models import Supplier

from .models import Category, Product


class ProductForm(forms.ModelForm):
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        required=True,
        empty_label="Selecione um fornecedor",
        error_messages={"required": "Escolha um fornecedor para o produto."},
        widget=forms.Select(
            attrs={"class": "w-full px-4 py-2 border border-gray-300 rounded-lg"}
        ),
    )
    image = forms.ImageField(required=False)

    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "batch",
            "quantity",
            "initial_quantity",
            "price",
            "expiration_date",
            "image",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "w-full px-4 py-2 border border-gray-300 rounded-lg"}
            ),
            "category": forms.Select(
                attrs={"class": "w-full px-4 py-2 border border-gray-300 rounded-lg"}
            ),
            "batch": forms.TextInput(
                attrs={"class": "w-full px-4 py-2 border border-gray-300 rounded-lg"}
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg",
                    "type": "number",
                    "min": "0",
                }
            ),
            "initial_quantity": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg",
                    "type": "number",
                    "min": "1",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg",
                    "type": "number",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "expiration_date": forms.DateInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg",
                    "type": "date",
                }
            ),
            "image": forms.FileInput(
                attrs={"class": "w-full px-4 py-2 border border-gray-300 rounded-lg"}
            ),
        }
        error_messages = {
            "name": {
                "required": "O nome do produto não pode ficar em branco.",
                "max_length": "O nome é muito longo. Máximo de 250 caracteres.",
            },
            "category": {
                "required": "Escolha uma categoria para o produto.",
            },
            "price": {
                "required": "O preço do produto não pode ficar em branco.",
            },
            "expiration_date": {
                "required": "A data de validade do produto não pode ficar em branco.",
            },
            "quantity": {
                "required": "A quantidade não pode ficar em branco.",
            },
            "initial_quantity": {
                "required": "A quantidade inicial do lote não pode ficar em branco.",
            },
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "status"]
        error_messages = {
            "name": {
                "required": "O nome da categoria não pode ficar em branco.",
            }
        }


class ProductEditForm(forms.ModelForm):
    """Form APENAS para editar (quantidade, categoria, nome e preço)"""

    class Meta:
        model = Product
        fields = ["name", "category", "quantity", "price"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "w-full px-4 py-2 border border-gray-300 rounded-lg"}
            ),
            "category": forms.Select(
                attrs={"class": "w-full px-4 py-2 border border-gray-300 rounded-lg"}
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg",
                    "type": "number",
                    "min": "0",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg",
                    "type": "number",
                    "step": "0.01",
                    "min": "0",
                }
            ),
        }
