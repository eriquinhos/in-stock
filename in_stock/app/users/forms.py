from django import forms
from .models import CustomUser

# Precisa terminar este forms


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Confirmar senha', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'phone', 'name', 'type')

        # Repar esse Erro  segundo o CHATGPT: error_messages não deve ser colocado dentro do Meta
        error_messages = {
            'email': {
                'required': 'O email não pode ficar em branco.',
                'unique': '"Este email já está em uso!"',

            },
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem.")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)

        # Criptografa a senha
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user
