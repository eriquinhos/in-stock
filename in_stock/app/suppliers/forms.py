from django import forms
from .models import Supplier


class SupplierForm(forms.ModelForm):

    class Meta:
        model = Supplier
        fields = ['name', 'cnpj', 'phone', 'email', 'address']

        error_messages = {
            'name': {
                'required': "O nome do fornecedor não pode ficar em branco.",
                'max_length': "A descrição deve ter no máximo 250 caracteres."
            },
            'cnpj': {
                'required': "É necessário preencher o CNPJ.",
            },
            'phone': {
                'required': "Por favor, informe o telefone do fornecedor.",
            },
            'email': {
                'required': "É necessário preencher o email do fornecedor.",
            },
            'address': {
                'required': "Por favor, forneça uma descrição para a venda.",
                'max_length': "A descrição deve ter no máximo 300 caracteres."
            },

        }
