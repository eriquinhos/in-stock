from django import forms
from .models import Sale


class SaleForm(forms.ModelForm):

    class Meta:
        model = Sale
        fields = ['product', 'supplier', 'date',
                  'type', 'quantity', 'description']

        error_messages = {
            'product': {
                'required': "É necessário informar o produto."
            },
            'supplier': {
                'required': "É necessário informar o fornecedor."
            },
            'date': {
                'required': "É necessário informar a data."
            },
            'type': {
                'required': "Por favor, informe se é Entrada ou Saída."
            },
            'quantity': {
                'required': "É necessário informar a quantidade."
            },
            'description': {
                'required': "Por favor, forneça uma descrição para a venda.",
                'max_length': "A descrição deve ter no máximo 500 caracteres."
            },
        }

    # O método de validação deve estar no nível da classe SaleForm

    def clean_description(self):
        description = self.cleaned_data.get('description')

        # A validação só é aplicada se o campo foi preenchido
        if description:
            # Exemplo de validação: garantir que a descrição não seja muito curta
            if len(description) < 10:
                raise forms.ValidationError(
                    "A descrição deve ter pelo menos 10 caracteres.")

            return description
