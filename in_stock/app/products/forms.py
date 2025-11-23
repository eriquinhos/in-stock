from django import forms

from .models import Category, Product


class ProductForm(forms.ModelForm):
    supplier = forms.IntegerField(
        required=True,
        error_messages={"required": "Escolha pelo menos um fornecedor para o produto."},
    )
    image = forms.ImageField(required=False)

    class Meta:
        model = Product
        fields = ["name", "category", "price", "expiration_date"]
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
                "required": "O data de validade do produto não pode ficar em branco.",
            },
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        error_messages = {
            "name": {
                "required": "O nome da categoria não pode ficar em branco.",
            }
        }
