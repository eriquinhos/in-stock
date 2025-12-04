from django import forms

from .models import Company, CustomUser

# Formulário para criação de usuário


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Senha", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar senha", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ("email", "phone", "name", "role", "company_obj")
        widgets = {
            "role": forms.Select(attrs={"class": "form-select"}),
            "company_obj": forms.Select(attrs={"class": "form-select"}),
        }

        error_messages = {
            "email": {
                "required": "O email não pode ficar em branco.",
                "unique": '"Este email já está em uso!"',
            },
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Se não for admin InStock, limita as opções de papel
        if self.user and not self.user.is_instock_admin:
            # Admin de empresa só pode criar gestores e operadores
            self.fields["role"].choices = [
                ("manager", "Gestor"),
                ("operator", "Operador"),
            ]
            # E só pode criar na sua empresa
            if self.user.company_obj:
                self.fields["company_obj"].queryset = Company.objects.filter(
                    id=self.user.company_obj.id
                )
                self.fields["company_obj"].initial = self.user.company_obj
                self.fields["company_obj"].widget = forms.HiddenInput()

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem.")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)

        # Criptografa a senha
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
        return user
