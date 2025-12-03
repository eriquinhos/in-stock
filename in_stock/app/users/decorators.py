"""
Decorators para verificação de permissões
"""
from functools import wraps
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpResponseForbidden


def permission_required(permission_name, redirect_url='dashboard'):
    """
    Decorator que verifica se o usuário tem uma permissão específica.
    
    Uso:
        @permission_required('can_create_products')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Super admins têm todas as permissões
            if request.user.is_superuser or request.user.is_instock_admin:
                return view_func(request, *args, **kwargs)
            
            # Verifica a permissão
            if request.user.has_permission(permission_name):
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'Você não tem permissão para realizar esta ação.')
            return redirect(redirect_url)
        
        return wrapper
    return decorator


def role_required(allowed_roles, redirect_url='dashboard'):
    """
    Decorator que verifica se o usuário tem um dos papéis permitidos.
    
    Uso:
        @role_required(['admin', 'manager'])
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Super admins têm todas as permissões
            if request.user.is_superuser or request.user.is_instock_admin:
                return view_func(request, *args, **kwargs)
            
            # Verifica o papel
            if request.user.role and request.user.role.name in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'Você não tem permissão para acessar esta página.')
            return redirect(redirect_url)
        
        return wrapper
    return decorator


def company_required(redirect_url='dashboard'):
    """
    Decorator que verifica se o usuário pertence a uma empresa.
    
    Uso:
        @company_required()
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # InStock admins podem acessar tudo
            if request.user.is_instock_admin:
                return view_func(request, *args, **kwargs)
            
            # Verifica se tem empresa
            if request.user.company_obj:
                return view_func(request, *args, **kwargs)
            
            messages.warning(request, 'Você precisa estar vinculado a uma empresa para acessar esta funcionalidade.')
            return redirect(redirect_url)
        
        return wrapper
    return decorator


def admin_or_manager_required(redirect_url='dashboard'):
    """
    Decorator que permite apenas admins e gerentes.
    """
    return role_required(['admin', 'manager'], redirect_url)


def admin_only(redirect_url='dashboard'):
    """
    Decorator que permite apenas admins.
    """
    return role_required(['admin'], redirect_url)


class PermissionRequiredMixin:
    """
    Mixin para Class-Based Views que requer uma permissão específica.
    
    Uso:
        class MyView(PermissionRequiredMixin, View):
            permission_required = 'can_create_products'
    """
    permission_required = None
    permission_denied_redirect = 'dashboard'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if request.user.is_superuser or request.user.is_instock_admin:
            return super().dispatch(request, *args, **kwargs)
        
        if self.permission_required and request.user.has_permission(self.permission_required):
            return super().dispatch(request, *args, **kwargs)
        
        messages.error(request, 'Você não tem permissão para realizar esta ação.')
        return redirect(self.permission_denied_redirect)


class CompanyFilterMixin:
    """
    Mixin que filtra querysets pela empresa do usuário.
    
    Uso:
        class MyListView(CompanyFilterMixin, ListView):
            model = Product
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # InStock admins veem tudo
        if self.request.user.is_instock_admin:
            return queryset
        
        # Filtra pela empresa do usuário
        if hasattr(queryset.model, 'company') and self.request.user.company_obj:
            return queryset.filter(company=self.request.user.company_obj)
        
        return queryset
