import json
import secrets
import string
import uuid

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin,
)
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


# ============================================
# MODELO DE EMPRESA (Multi-tenant)
# ============================================
class Company(models.Model):
    """Empresa/Organização - Base do sistema multi-tenant"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, verbose_name="Nome da Empresa")
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
    email = models.EmailField(verbose_name="Email corporativo", blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    address = models.TextField(blank=True, null=True, verbose_name="Endereço")
    logo = models.ImageField(upload_to="companies/logos/", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
    
    def __str__(self):
        return self.name
    
    @property
    def total_users(self):
        return self.users.count()
    
    @property
    def total_products(self):
        return self.products.count()


# ============================================
# MODELO DE PAPEL/PERMISSÃO
# ============================================
class Role(models.Model):
    """Papéis de usuário com permissões granulares"""
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('operator', 'Operador'),
        ('viewer', 'Visualizador'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Papel")
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='roles',
        null=True,
        blank=True,
        verbose_name="Empresa"
    )
    
    # Permissões granulares
    can_create_products = models.BooleanField(default=False, verbose_name="Criar produtos")
    can_edit_products = models.BooleanField(default=False, verbose_name="Editar produtos")
    can_delete_products = models.BooleanField(default=False, verbose_name="Excluir produtos")
    can_view_products = models.BooleanField(default=True, verbose_name="Ver produtos")
    
    can_create_suppliers = models.BooleanField(default=False, verbose_name="Criar fornecedores")
    can_edit_suppliers = models.BooleanField(default=False, verbose_name="Editar fornecedores")
    can_delete_suppliers = models.BooleanField(default=False, verbose_name="Excluir fornecedores")
    can_view_suppliers = models.BooleanField(default=True, verbose_name="Ver fornecedores")
    
    can_create_sales = models.BooleanField(default=False, verbose_name="Criar movimentações")
    can_edit_sales = models.BooleanField(default=False, verbose_name="Editar movimentações")
    can_delete_sales = models.BooleanField(default=False, verbose_name="Excluir movimentações")
    can_view_sales = models.BooleanField(default=True, verbose_name="Ver movimentações")
    
    can_create_reports = models.BooleanField(default=False, verbose_name="Criar relatórios")
    can_view_reports = models.BooleanField(default=True, verbose_name="Ver relatórios")
    
    can_manage_users = models.BooleanField(default=False, verbose_name="Gerenciar usuários")
    can_view_audit_logs = models.BooleanField(default=False, verbose_name="Ver logs de auditoria")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Papel"
        verbose_name_plural = "Papéis"
        unique_together = ['name', 'company']
    
    def __str__(self):
        company_name = self.company.name if self.company else "Sistema"
        return f"{self.get_name_display()} - {company_name}"
    
    @classmethod
    def get_default_permissions(cls, role_name):
        """Retorna as permissões padrão para cada papel"""
        permissions = {
            'admin': {
                'can_create_products': True, 'can_edit_products': True, 'can_delete_products': True, 'can_view_products': True,
                'can_create_suppliers': True, 'can_edit_suppliers': True, 'can_delete_suppliers': True, 'can_view_suppliers': True,
                'can_create_sales': True, 'can_edit_sales': True, 'can_delete_sales': True, 'can_view_sales': True,
                'can_create_reports': True, 'can_view_reports': True,
                'can_manage_users': True, 'can_view_audit_logs': True,
            },
            'manager': {
                'can_create_products': True, 'can_edit_products': True, 'can_delete_products': False, 'can_view_products': True,
                'can_create_suppliers': True, 'can_edit_suppliers': True, 'can_delete_suppliers': False, 'can_view_suppliers': True,
                'can_create_sales': True, 'can_edit_sales': True, 'can_delete_sales': False, 'can_view_sales': True,
                'can_create_reports': True, 'can_view_reports': True,
                'can_manage_users': False, 'can_view_audit_logs': True,
            },
            'operator': {
                'can_create_products': True, 'can_edit_products': True, 'can_delete_products': False, 'can_view_products': True,
                'can_create_suppliers': False, 'can_edit_suppliers': False, 'can_delete_suppliers': False, 'can_view_suppliers': True,
                'can_create_sales': True, 'can_edit_sales': False, 'can_delete_sales': False, 'can_view_sales': True,
                'can_create_reports': False, 'can_view_reports': True,
                'can_manage_users': False, 'can_view_audit_logs': False,
            },
            'viewer': {
                'can_create_products': False, 'can_edit_products': False, 'can_delete_products': False, 'can_view_products': True,
                'can_create_suppliers': False, 'can_edit_suppliers': False, 'can_delete_suppliers': False, 'can_view_suppliers': True,
                'can_create_sales': False, 'can_edit_sales': False, 'can_delete_sales': False, 'can_view_sales': True,
                'can_create_reports': False, 'can_view_reports': True,
                'can_manage_users': False, 'can_view_audit_logs': False,
            },
        }
        return permissions.get(role_name, permissions['viewer'])
    
    @classmethod
    def create_for_company(cls, company, role_name='admin'):
        """Cria um papel com permissões padrão para uma empresa"""
        permissions = cls.get_default_permissions(role_name)
        role, created = cls.objects.get_or_create(
            name=role_name,
            company=company,
            defaults=permissions
        )
        return role


# ============================================
# MODELO DE LOG DE AUDITORIA
# ============================================
class AuditLog(models.Model):
    """Log de auditoria para rastrear todas as ações do sistema"""
    ACTION_CHOICES = [
        ('create', 'Criação'),
        ('update', 'Atualização'),
        ('delete', 'Exclusão'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view', 'Visualização'),
        ('export', 'Exportação'),
        ('import', 'Importação'),
        ('approve', 'Aprovação'),
        ('reject', 'Rejeição'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Quem fez a ação
    user = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name="Usuário"
    )
    user_email = models.EmailField(verbose_name="Email do usuário")  # Backup caso user seja deletado
    
    # Empresa relacionada
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name="Empresa"
    )
    
    # O que foi feito
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Ação")
    
    # Em qual modelo/objeto
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de objeto"
    )
    object_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID do objeto")
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=255, blank=True, verbose_name="Representação do objeto")
    
    # Detalhes da mudança
    changes = models.JSONField(default=dict, blank=True, verbose_name="Mudanças")
    old_values = models.JSONField(default=dict, blank=True, verbose_name="Valores anteriores")
    new_values = models.JSONField(default=dict, blank=True, verbose_name="Novos valores")
    
    # Metadados
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Endereço IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    extra_data = models.JSONField(default=dict, blank=True, verbose_name="Dados extras")
    
    # Quando
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['company', 'created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user_email} - {self.get_action_display()} - {self.object_repr} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"
    
    @classmethod
    def log(cls, user, action, obj=None, old_values=None, new_values=None, request=None, **extra):
        """Método helper para criar logs de auditoria"""
        from django.contrib.contenttypes.models import ContentType
        
        log_entry = cls(
            user=user,
            user_email=user.email if user else 'Sistema',
            company=getattr(user, 'company_obj', None) if user else None,
            action=action,
            old_values=old_values or {},
            new_values=new_values or {},
            extra_data=extra,
        )
        
        if obj:
            log_entry.content_type = ContentType.objects.get_for_model(obj)
            log_entry.object_id = str(obj.pk)
            log_entry.object_repr = str(obj)[:255]
        
        if request:
            log_entry.ip_address = cls.get_client_ip(request)
            log_entry.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        log_entry.save()
        return log_entry
    
    @staticmethod
    def get_client_ip(request):
        """Obtém o IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
    
    def get_changes_display(self):
        """Retorna as mudanças de forma legível"""
        changes = []
        for field, values in self.changes.items():
            if isinstance(values, dict):
                old = values.get('old', '-')
                new = values.get('new', '-')
                changes.append(f"{field}: {old} → {new}")
        return changes


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
        extra_fields.setdefault("role", "instock_admin")
        extra_fields.setdefault("must_change_password", False)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Usuário customizado com sistema de 4 níveis hierárquicos:
    
    1. InStock Admin: Administrador da plataforma InStock
       - Gerencia TODAS as empresas
       - Aprova solicitações de novas empresas
       - Cria admins de empresa
       - Acesso total ao sistema
    
    2. Company Admin (Admin da Empresa): TI/RH/Dono da empresa cliente
       - Gerencia APENAS sua empresa
       - Aprova solicitações de acesso à sua empresa
       - Cria gestores e operadores da sua empresa
       - Não vê dados de outras empresas
    
    3. Gestor (Manager): Responsável pelo estoque
       - Ver, Criar, Editar, Excluir produtos/movimentações
       - Fazer compras e gerenciar estoque
       - Não pode gerenciar usuários
    
    4. Operador (Operator): Funcionário operacional
       - Ver, Criar, Editar produtos/movimentações
       - NÃO pode excluir
       - NÃO pode gerenciar usuários
    """
    
    # Hierarquia de papéis (4 níveis)
    ROLE_CHOICES = [
        ('instock_admin', 'Admin InStock'),
        ('company_admin', 'Admin da Empresa'),
        ('manager', 'Gestor'),
        ('operator', 'Operador'),
    ]
    
    name = models.CharField(max_length=150, default="User")
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=False, verbose_name="Deve trocar senha")
    
    # Papel do usuário (substituindo is_instock_admin e role FK)
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='operator',
        verbose_name="Papel"
    )
    
    # Multi-tenant: Relação com empresa
    company_obj = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Empresa"
    )
    company = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nome da Empresa (legado)")
    
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    # ============================================
    # PROPRIEDADES DE VERIFICAÇÃO DE PAPEL
    # ============================================
    @property
    def is_instock_admin(self):
        """Verifica se é Admin da InStock"""
        return self.role == 'instock_admin' or self.is_superuser
    
    @property
    def is_company_admin(self):
        """Verifica se é Admin de uma Empresa"""
        return self.role == 'company_admin'
    
    @property
    def is_manager(self):
        """Verifica se é Gestor"""
        return self.role == 'manager'
    
    @property
    def is_operator(self):
        """Verifica se é Operador"""
        return self.role == 'operator'
    
    @property
    def is_any_admin(self):
        """Verifica se é qualquer tipo de admin (InStock ou Empresa)"""
        return self.is_instock_admin or self.is_company_admin
    
    @property
    def role_display(self):
        """Retorna o nome do papel de forma legível"""
        return dict(self.ROLE_CHOICES).get(self.role, 'Sem papel definido')
    
    # ============================================
    # MÉTODOS DE VERIFICAÇÃO DE PERMISSÃO
    # ============================================
    def can_view(self):
        """Todos os papéis podem visualizar"""
        return True
    
    def can_create(self):
        """Todos os papéis podem criar"""
        return True
    
    def can_edit(self):
        """Todos os papéis podem editar"""
        return True
    
    def can_delete(self):
        """Apenas Admin InStock, Admin Empresa e Gestor podem excluir"""
        return self.role in ['instock_admin', 'company_admin', 'manager'] or self.is_superuser
    
    def can_manage_users(self):
        """Apenas Admins podem gerenciar usuários"""
        return self.is_any_admin
    
    def can_approve_access_requests(self):
        """Verifica se pode aprovar solicitações de acesso"""
        # InStock Admin aprova solicitações de novas empresas
        # Company Admin aprova solicitações de acesso à sua empresa
        return self.is_any_admin
    
    def can_manage_all_companies(self):
        """Verifica se pode gerenciar todas as empresas"""
        return self.is_instock_admin
    
    def can_view_audit_logs(self):
        """Apenas Admins podem ver logs de auditoria"""
        return self.is_any_admin
    
    def can_create_reports(self):
        """Admins e Gestores podem criar relatórios"""
        return self.role in ['instock_admin', 'company_admin', 'manager'] or self.is_superuser
    
    # Métodos legados para compatibilidade
    def can_create_products(self):
        return self.can_create()
    
    def can_edit_products(self):
        return self.can_edit()
    
    def can_delete_products(self):
        return self.can_delete()
    
    def can_view_products(self):
        return self.can_view()
    
    def can_create_suppliers(self):
        return self.can_create()
    
    def can_edit_suppliers(self):
        return self.can_edit()
    
    def can_delete_suppliers(self):
        return self.can_delete()
    
    def can_view_suppliers(self):
        return self.can_view()
    
    def can_create_sales(self):
        return self.can_create()
    
    def can_edit_sales(self):
        return self.can_edit()
    
    def can_delete_sales(self):
        return self.can_delete()
    
    def can_view_sales(self):
        return self.can_view()
    
    def can_view_reports(self):
        return self.can_view()


class AccessRequest(models.Model):
    """
    Solicitações de acesso ao sistema.
    
    Dois tipos de solicitação:
    1. new_company: Nova empresa querendo usar o sistema
       - Aprovado pelo Admin InStock
       - Cria a empresa e o admin da empresa
    
    2. join_company: Usuário querendo entrar em empresa existente
       - Aprovado pelo Admin da Empresa
       - Cria usuário como Gestor ou Operador
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    ]
    
    TYPE_CHOICES = [
        ('new_company', 'Nova Empresa'),
        ('join_company', 'Entrar em Empresa'),
    ]
    
    REQUESTED_ROLE_CHOICES = [
        ('manager', 'Gestor'),
        ('operator', 'Operador'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Tipo de solicitação
    request_type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='new_company',
        verbose_name="Tipo de solicitação"
    )
    
    # Dados do solicitante
    name = models.CharField(max_length=150, verbose_name="Nome completo")
    personal_email = models.EmailField(verbose_name="Email pessoal")
    phone = models.CharField(max_length=20, verbose_name="Telefone", blank=True, null=True)
    message = models.TextField(verbose_name="Mensagem", blank=True, null=True)
    
    # Para nova empresa (new_company)
    company_name = models.CharField(max_length=150, verbose_name="Nome da empresa", blank=True, null=True)
    cnpj = models.CharField(max_length=18, verbose_name="CNPJ", blank=True, null=True)
    
    # Para entrar em empresa existente (join_company)
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='access_requests',
        verbose_name="Empresa"
    )
    requested_role = models.CharField(
        max_length=20,
        choices=REQUESTED_ROLE_CHOICES,
        default='operator',
        verbose_name="Papel solicitado"
    )
    
    # Status e aprovação
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
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="Motivo da rejeição")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Solicitação de Acesso"
        verbose_name_plural = "Solicitações de Acesso"
    
    def __str__(self):
        if self.request_type == 'new_company':
            return f"{self.name} - {self.company_name} (Nova Empresa - {self.get_status_display()})"
        else:
            company_name = self.company.name if self.company else "?"
            return f"{self.name} - {company_name} ({self.get_requested_role_display()} - {self.get_status_display()})"
    
    @property
    def is_new_company_request(self):
        return self.request_type == 'new_company'
    
    @property
    def is_join_company_request(self):
        return self.request_type == 'join_company'
    
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


class PasswordResetToken(models.Model):
    """Token para redefinição de senha"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Token de Redefinição de Senha"
        verbose_name_plural = "Tokens de Redefinição de Senha"
    
    def __str__(self):
        return f"Token para {self.user.email} - {'Usado' if self.used else 'Válido'}"
    
    @property
    def is_valid(self):
        """Verifica se o token ainda é válido"""
        return not self.used and timezone.now() < self.expires_at
    
    @staticmethod
    def generate_token():
        """Gera um token único e seguro"""
        return secrets.token_urlsafe(32)
    
    @classmethod
    def create_for_user(cls, user, expiration_hours=1):
        """Cria um novo token para o usuário"""
        from datetime import timedelta

        # Invalida tokens anteriores do usuário
        cls.objects.filter(user=user, used=False).update(used=True)
        
        # Cria novo token
        token = cls(
            user=user,
            token=cls.generate_token(),
            expires_at=timezone.now() + timedelta(hours=expiration_hours)
        )
        token.save()
        return token
