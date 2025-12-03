from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
import uuid
import secrets
import string


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O campo email é obrigatório")
        email = self.normalize_email(email).lower()

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_instock_admin", True)
        extra_fields.setdefault("must_change_password", False)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=150, default="User")
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_instock_admin = models.BooleanField(default=False, verbose_name="Admin InStock")
    must_change_password = models.BooleanField(default=False, verbose_name="Deve trocar senha")
    company = models.CharField(max_length=150, blank=True, null=True, verbose_name="Empresa")
    TYPE_CHOICES = [
        ("admin", "Administrador"),
        ("standard", "Padrão"),
    ]
    type = models.CharField(max_length=8, choices=TYPE_CHOICES, default="standard")
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class AccessRequest(models.Model):
    """Solicitações de acesso de admins de empresas"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, verbose_name="Nome completo")
    personal_email = models.EmailField(verbose_name="Email pessoal")
    company_name = models.CharField(max_length=150, verbose_name="Nome da empresa")
    cnpj = models.CharField(max_length=18, verbose_name="CNPJ")
    phone = models.CharField(max_length=20, verbose_name="Telefone", blank=True, null=True)
    message = models.TextField(verbose_name="Mensagem", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    generated_email = models.EmailField(blank=True, null=True, verbose_name="Email gerado")
    generated_password = models.CharField(max_length=100, blank=True, null=True)
    approved_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_requests'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Solicitação de Acesso"
        verbose_name_plural = "Solicitações de Acesso"
    
    def __str__(self):
        return f"{self.name} - {self.company_name} ({self.status})"
    
    @staticmethod
    def generate_password(length=10):
        """Gera uma senha aleatória segura"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_company_email(name, company_name):
        """Gera um email corporativo para o admin"""
        import re
        # Pega o primeiro nome e limpa
        first_name = name.split()[0].lower()
        first_name = re.sub(r'[^a-z]', '', first_name)
        # Limpa o nome da empresa
        company_slug = company_name.lower()
        company_slug = re.sub(r'[^a-z0-9]', '', company_slug)[:15]
        return f"{first_name}@{company_slug}.instock.app.br"
