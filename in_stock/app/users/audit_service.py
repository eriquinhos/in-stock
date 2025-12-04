"""
Serviço de Auditoria - Registra todas as ações do sistema
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from in_stock.app.users.models import AuditLog


class AuditService:
    """Serviço para gerenciar logs de auditoria"""
    
    @staticmethod
    def log_action(user, action, obj=None, old_values=None, new_values=None, request=None, **extra):
        """
        Registra uma ação no log de auditoria.
        
        Args:
            user: Usuário que realizou a ação
            action: Tipo de ação (create, update, delete, etc.)
            obj: Objeto afetado pela ação
            old_values: Valores anteriores (para updates)
            new_values: Novos valores (para creates e updates)
            request: Request HTTP (para capturar IP e user agent)
            **extra: Dados extras a serem armazenados
        
        Returns:
            AuditLog: O registro de log criado
        """
        return AuditLog.log(
            user=user,
            action=action,
            obj=obj,
            old_values=old_values,
            new_values=new_values,
            request=request,
            **extra
        )
    
    @staticmethod
    def log_create(user, obj, request=None, **extra):
        """Registra uma ação de criação"""
        new_values = AuditService._serialize_object(obj)
        return AuditService.log_action(
            user=user,
            action='create',
            obj=obj,
            new_values=new_values,
            request=request,
            **extra
        )
    
    @staticmethod
    def log_update(user, obj, old_values, request=None, **extra):
        """Registra uma ação de atualização"""
        new_values = AuditService._serialize_object(obj)
        changes = AuditService._compute_changes(old_values, new_values)
        
        log = AuditService.log_action(
            user=user,
            action='update',
            obj=obj,
            old_values=old_values,
            new_values=new_values,
            request=request,
            **extra
        )
        log.changes = changes
        log.save()
        return log
    
    @staticmethod
    def log_delete(user, obj, request=None, **extra):
        """Registra uma ação de exclusão"""
        old_values = AuditService._serialize_object(obj)
        return AuditService.log_action(
            user=user,
            action='delete',
            obj=obj,
            old_values=old_values,
            request=request,
            **extra
        )
    
    @staticmethod
    def log_login(user, request=None, **extra):
        """Registra um login"""
        return AuditService.log_action(
            user=user,
            action='login',
            request=request,
            **extra
        )
    
    @staticmethod
    def log_logout(user, request=None, **extra):
        """Registra um logout"""
        return AuditService.log_action(
            user=user,
            action='logout',
            request=request,
            **extra
        )
    
    @staticmethod
    def log_view(user, obj, request=None, **extra):
        """Registra uma visualização (opcional, pode gerar muitos logs)"""
        return AuditService.log_action(
            user=user,
            action='view',
            obj=obj,
            request=request,
            **extra
        )
    
    @staticmethod
    def log_export(user, export_type, request=None, **extra):
        """Registra uma exportação de dados"""
        return AuditService.log_action(
            user=user,
            action='export',
            request=request,
            export_type=export_type,
            **extra
        )
    
    @staticmethod
    def log_approve(user, obj, request=None, **extra):
        """Registra uma aprovação"""
        return AuditService.log_action(
            user=user,
            action='approve',
            obj=obj,
            request=request,
            **extra
        )
    
    @staticmethod
    def log_reject(user, obj, request=None, **extra):
        """Registra uma rejeição"""
        return AuditService.log_action(
            user=user,
            action='reject',
            obj=obj,
            request=request,
            **extra
        )
    
    @staticmethod
    def _serialize_object(obj):
        """Serializa um objeto para armazenamento no log"""
        if obj is None:
            return {}
        
        data = {}
        for field in obj._meta.fields:
            value = getattr(obj, field.name)
            # Converte valores não serializáveis
            if hasattr(value, 'pk'):
                data[field.name] = str(value.pk)
            elif hasattr(value, 'isoformat'):
                data[field.name] = value.isoformat()
            else:
                try:
                    data[field.name] = str(value) if value is not None else None
                except:
                    data[field.name] = '<não serializável>'
        
        return data
    
    @staticmethod
    def _compute_changes(old_values, new_values):
        """Computa as diferenças entre valores antigos e novos"""
        changes = {}
        all_keys = set(old_values.keys()) | set(new_values.keys())
        
        for key in all_keys:
            old_val = old_values.get(key)
            new_val = new_values.get(key)
            
            if old_val != new_val:
                changes[key] = {
                    'old': old_val,
                    'new': new_val
                }
        
        return changes
    
    @staticmethod
    def get_logs_for_object(obj, limit=50):
        """Retorna os logs de um objeto específico"""
        content_type = ContentType.objects.get_for_model(obj)
        return AuditLog.objects.filter(
            content_type=content_type,
            object_id=str(obj.pk)
        )[:limit]
    
    @staticmethod
    def get_logs_for_user(user, limit=50):
        """Retorna os logs de um usuário específico"""
        return AuditLog.objects.filter(user=user)[:limit]
    
    @staticmethod
    def get_logs_for_company(company, limit=100):
        """Retorna os logs de uma empresa específica"""
        return AuditLog.objects.filter(company=company)[:limit]
    
    @staticmethod
    def get_recent_logs(limit=100):
        """Retorna os logs mais recentes"""
        return AuditLog.objects.all()[:limit]


def capture_old_values(instance):
    """
    Helper function para capturar valores antigos antes de uma atualização.
    Use em views antes de salvar um objeto.
    
    Uso:
        old_values = capture_old_values(produto)
        produto.name = 'Novo Nome'
        produto.save()
        AuditService.log_update(request.user, produto, old_values, request)
    """
    if instance.pk:
        try:
            old_instance = instance.__class__.objects.get(pk=instance.pk)
            return AuditService._serialize_object(old_instance)
        except instance.__class__.DoesNotExist:
            pass
    return {}
